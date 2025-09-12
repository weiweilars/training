#!/usr/bin/env python3
"""
SK-Powered A2A Agent Server - Training Example with A2A Agent-to-Agent Communication
A2A server with Microsoft Semantic Kernel integration and dynamic A2A agent calling
"""

import asyncio
import json
import logging
import argparse
import os
from datetime import datetime
from typing import Dict, Any, Optional, List
import aiohttp
import uuid
import yaml
from collections import defaultdict

try:
    from fastapi import FastAPI
    from fastapi.responses import JSONResponse
    from pydantic import BaseModel
    import uvicorn
except ImportError:
    print("❌ ERROR: Required dependencies not found!")
    print("📦 Install required dependencies:")
    print("   pip install starlette uvicorn aiohttp")
    exit(1)

# Semantic Kernel imports
try:
    from semantic_kernel import Kernel
    from semantic_kernel.agents import ChatCompletionAgent
    from semantic_kernel.connectors.ai.open_ai import OpenAIChatCompletion, AzureChatCompletion
    from semantic_kernel.connectors.ai import FunctionChoiceBehavior
    from semantic_kernel.functions import kernel_function
    from semantic_kernel.functions import KernelArguments
    from semantic_kernel.contents.chat_history import ChatHistory
    from semantic_kernel.contents.chat_message_content import ChatMessageContent
    from semantic_kernel.contents.utils.author_role import AuthorRole
except ImportError:
    print("❌ ERROR: Semantic Kernel not found!")
    print("📦 Install Semantic Kernel:")
    print("   pip install semantic-kernel")
    exit(1)

# Custom A2A Agent Client (replacing MCP client)
from custom_a2a_client import CustomA2AAgentset

from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Default Configuration
DEFAULT_AGENT_ID = "sk-a2a-training-agent"
DEFAULT_AGENT_NAME = "SK A2A Training Agent"
DEFAULT_AGENT_PORT = 5002
DEFAULT_A2A_AGENT_URL = "http://localhost:5010"  # Default A2A agent URL

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

async def parse_a2a_response(response) -> dict:
    """Parse HTTP response from A2A agent"""
    if response.status != 200:
        logger.error(f"A2A agent returned status {response.status}")
        return None
    
    try:
        # A2A agents return JSON responses
        return await response.json()
    except Exception as e:
        logger.error(f"Failed to parse A2A response: {e}")
        return None

# Configuration Management
class AgentConfig:
    """Agent configuration loaded from YAML files"""
    
    def __init__(self, config_data: Dict[str, Any]):
        self.agent = config_data.get("agent", {})
        self.id = self.agent.get("id", DEFAULT_AGENT_ID)
        self.name = self.agent.get("name", DEFAULT_AGENT_NAME)
        self.version = self.agent.get("version", "1.0.0")
        self.description = self.agent.get("description", "SK-powered A2A agent with agent-to-agent communication")
        
        # Agent card properties
        self.card = self.agent.get("card", {})
        self.greeting = self.card.get("greeting", f"Hello! I'm {self.name}.")
        self.instructions = self.card.get("instructions", "I'm here to help you with various tasks using other AI agents.")
        
        # Agent personality
        self.personality = self.agent.get("personality", {})
        self.style = self.personality.get("style", "helpful and friendly")
        self.tone = self.personality.get("tone", "professional")
        self.expertise = self.personality.get("expertise", "general assistance with agent coordination")
        
        # A2A Agents configuration (replacing tools configuration)
        self.agents = self.agent.get("agents", {})
        self.default_agent_urls = self.agents.get("default_urls", [DEFAULT_A2A_AGENT_URL])
        
        # Server configuration
        self.server = self.agent.get("server", {})
        self.default_port = self.server.get("default_port", DEFAULT_AGENT_PORT)
        self.host = self.server.get("host", "0.0.0.0")
        
        # LLM configuration
        self.llm = self.agent.get("llm", {})
        self.model = self.llm.get("model", "gpt-3.5-turbo")
        self.system_prompt = self.llm.get("system_prompt", "You are a helpful AI assistant that can coordinate with other AI agents to complete tasks.")

def load_agent_config(config_path: str) -> AgentConfig:
    """Load agent configuration from YAML file"""
    try:
        with open(config_path, 'r') as file:
            config_data = yaml.safe_load(file)
            return AgentConfig(config_data)
    except FileNotFoundError:
        logger.error(f"❌ Configuration file not found: {config_path}")
        exit(1)
    except yaml.YAMLError as e:
        logger.error(f"❌ Invalid YAML in configuration file: {e}")
        exit(1)
    except Exception as e:
        logger.error(f"❌ Error loading configuration: {e}")
        exit(1)


class A2ATeamAgent:
    """Semantic Kernel-powered agent that can call other A2A agents in a team"""
    
    def __init__(self, model="gpt-3.5-turbo", agent_name="SK Agent", 
                 agent_description="SK-powered agent", agent_instruction="You are a helpful assistant."):
        self._model = model
        self._name = agent_name
        self._description = agent_description
        self._instruction = agent_instruction
        self._kernel = None
        self._agent = None
        self._chat_service = None
        self._agent_plugins = {}
        self._agent_urls = []
        self._agent_history = []
        
        # Session management - maintain chat history per session
        self._sessions = defaultdict(lambda: {
            "chat_history": ChatHistory(),
            "created_at": datetime.now().isoformat()
        })

    async def create(self, agent_urls: list = None, preserve_sessions: bool = False):
        """Initialize the SK agent with A2A agents"""
        if agent_urls is None:
            agent_urls = []
        
        try:
            # Initialize kernel
            self._kernel = Kernel()
            
            # Configure chat service based on available environment variables
            if os.getenv("OPENAI_API_KEY"):
                self._chat_service = OpenAIChatCompletion(
                    ai_model_id=self._model,
                    api_key=os.getenv("OPENAI_API_KEY")
                )
            elif os.getenv("AZURE_OPENAI_API_KEY"):
                self._chat_service = AzureChatCompletion(
                    deployment_name=os.getenv("AZURE_OPENAI_DEPLOYMENT_NAME", self._model),
                    api_key=os.getenv("AZURE_OPENAI_API_KEY"),
                    endpoint=os.getenv("AZURE_OPENAI_ENDPOINT")
                )
            elif os.getenv("AZURE_AI_INFERENCE_API_KEY"):
                # Handle Azure AI Inference credentials
                endpoint = os.getenv("AZURE_AI_INFERENCE_ENDPOINT")
                api_key = os.getenv("AZURE_AI_INFERENCE_API_KEY")
                # Extract base endpoint and deployment from the full endpoint URL
                if "/openai/deployments/" in endpoint:
                    parts = endpoint.split("/openai/deployments/")
                    base_endpoint = parts[0]
                    deployment = parts[1].split("/")[0]
                else:
                    base_endpoint = endpoint
                    deployment = "gpt-4o"  # Default deployment
                
                self._chat_service = AzureChatCompletion(
                    deployment_name=deployment,
                    api_key=api_key,
                    endpoint=base_endpoint
                )
                logger.info(f"Using Azure AI Inference with deployment: {deployment}")
            else:
                # Fallback to a mock service for testing
                logger.warning("No OpenAI/Azure credentials found. Using mock service.")
                
            if self._chat_service:
                self._kernel.add_service(self._chat_service)
            
            # Clear existing plugins if not preserving sessions
            if not preserve_sessions:
                self._agent_plugins = {}
                self._sessions.clear()
            
            # Add A2A agent plugins to kernel
            for url in agent_urls:
                await self._add_a2a_plugin_to_kernel(url)
            
            # Store agent URLs
            self._agent_urls = agent_urls.copy()
            
            # Create the agent with kernel that has plugins loaded
            kernel_plugins = list(self._kernel.plugins.values()) if hasattr(self._kernel, 'plugins') else []
            
            self._agent = ChatCompletionAgent(
                kernel=self._kernel,
                name=self._name,
                description=self._description,
                id=self._name.replace(" ", "_"),
                instructions=self._instruction,
                plugins=kernel_plugins
            )
            
            logger.info(f"SK agent '{self._name}' {'recreated' if preserve_sessions else 'created'} successfully with {len(self._agent_plugins)} A2A agent plugins")
            if preserve_sessions:
                logger.info("Sessions preserved across agent recreation")
            
            return self
            
        except Exception as e:
            logger.error(f"Failed to create SK agent: {e}")
            raise

    def _get_parameter_dicts_from_capability(self, capability_data: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Creates parameter dictionaries from A2A agent capability data"""
        parameters = capability_data.get("parameters", {})
        
        if not parameters:
            return []
            
        params = []
        for prop_name, prop_details in parameters.items():
            # Handle string-encoded JSON
            if isinstance(prop_details, str):
                try:
                    prop_details = json.loads(prop_details)
                except json.JSONDecodeError:
                    prop_details = {"type": "string"}
            
            params.append({
                "name": prop_name,
                "is_required": prop_details.get("required", False),
                "type": prop_details.get("type", "string"),
                "default_value": prop_details.get("default", None),
                "schema_data": prop_details,
                "description": prop_details.get("description", f"Parameter {prop_name}")
            })
        return params

    async def _add_a2a_plugin_to_kernel(self, url: str):
        """Add A2A agent capabilities to kernel as functions"""
        try:
            # Import plugin type if available
            from semantic_kernel.functions import KernelPlugin
            
            # Create custom A2A agentset
            custom_agentset = CustomA2AAgentset(url)
            
            # Get the agent capabilities
            capability_list = await custom_agentset.discover_capabilities()
            
            logger.info(f"Discovered {len(capability_list)} capabilities from {url}")
            
            # Create a plugin name
            plugin_name = f"a2a_plugin_{url.replace('://', '_').replace('/', '_').replace(':', '_')}"
            
            # Create a dictionary to hold plugin functions
            plugin_functions = {}
            
            # Add each capability as a kernel function
            for capability_name in capability_list:
                capability_data = custom_agentset.capabilities.get(capability_name, {})
                capability_description = capability_data.get("description", f"A2A agent capability: {capability_name}")
                
                logger.info(f"Registering capability: {capability_name}")
                
                # Create kernel function for this capability
                def create_kernel_func(name, desc, agentset, capability_info):
                    @kernel_function(
                        name=name,
                        description=desc
                    )
                    async def kernel_func(**kwargs):
                        try:
                            # Format message for the A2A agent
                            if kwargs:
                                message = f"Please help with {name}. Parameters: {json.dumps(kwargs, indent=2)}"
                            else:
                                message = f"Please help with {name}"
                            
                            result = await agentset.client.send_message(message)
                            
                            # Extract content from A2A result
                            if isinstance(result, dict):
                                if "result" in result and "message" in result["result"]:
                                    message_content = result["result"]["message"]
                                    if isinstance(message_content, dict) and "content" in message_content:
                                        return message_content["content"]
                                    elif isinstance(message_content, str):
                                        return message_content
                                elif "message" in result and "content" in result["message"]:
                                    return result["message"]["content"]
                            
                            # Fallback to JSON representation
                            return json.dumps(result, indent=2)
                        except Exception as e:
                            return f"Error calling A2A agent {name}: {str(e)}"
                    
                    # Add parameter metadata to enable function calling
                    kernel_func.__kernel_function_parameters__ = self._get_parameter_dicts_from_capability(capability_info)
                    return kernel_func
                
                kernel_func = create_kernel_func(capability_name, capability_description, custom_agentset, capability_data)
                plugin_functions[capability_name] = kernel_func
                
                logger.info(f"Registered {capability_name} with {len(kernel_func.__kernel_function_parameters__)} parameters")
            
            # Create a plugin from all the functions
            plugin = KernelPlugin(
                name=plugin_name,
                description=f"A2A agent capabilities from {url}",
                functions=plugin_functions
            )
            
            # Add the plugin to the kernel
            self._kernel.add_plugin(plugin)
            
            # Store agentset for reference
            self._agent_plugins[url] = custom_agentset
            
            logger.info(f"Successfully added plugin '{plugin_name}' with {len(capability_list)} A2A agent capabilities from {url} to kernel")
                
        except Exception as e:
            logger.error(f"Failed to add A2A agent capabilities from {url}: {e}")
            # Don't raise, continue with other plugins

    async def invoke(self, query: str, session_id: str) -> str:
        """Process a query using the SK agent with proper session context"""
        if not self._agent:
            raise RuntimeError("Agent not initialized. Call create() first.")
        
        try:
            logger.info(f"Processing query: '{query}' for session: {session_id}")
            
            # Get or create session chat history
            session_data = self._sessions[session_id]
            chat_history = session_data["chat_history"]
            
            # Add user message to chat history
            user_message = ChatMessageContent(
                role=AuthorRole.USER,
                content=query
            )
            chat_history.add_message(user_message)
            
            # Get response with full conversation context and function calling enabled
            from semantic_kernel.connectors.ai.open_ai import AzureChatPromptExecutionSettings
            
            execution_settings = AzureChatPromptExecutionSettings()
            execution_settings.function_choice_behavior = FunctionChoiceBehavior.Auto(auto_invoke=True)
            execution_settings.parallel_tool_calls = True
            
            kernel_arguments = KernelArguments(settings=execution_settings)
            
            response = await self._agent.get_response(
                messages=chat_history,
                arguments=kernel_arguments
            )
            
            # Extract response text and add to history
            response_text = str(response) if response else "I apologize, but I couldn't generate a response."
            
            # Add assistant response to chat history
            assistant_message = ChatMessageContent(
                role=AuthorRole.ASSISTANT,
                content=response_text
            )
            chat_history.add_message(assistant_message)
            
            logger.info(f"SK agent response generated successfully (session has {len(chat_history)} messages)")
            return response_text
                
        except Exception as e:
            logger.error(f"Error processing query: {e}")
            return f"Error processing your request: {str(e)}"

    async def add_agent(self, agent_url: str) -> bool:
        """Add a single A2A agent to the agent with session preservation"""
        try:
            if agent_url not in self._agent_urls:
                # Add the new agent URL
                new_agents = self._agent_urls + [agent_url]
                
                # Recreate the agent with preserved sessions
                await self.create(new_agents, preserve_sessions=True)
                
                # Record the change
                self._agent_history.append({
                    "action": "add",
                    "url": agent_url,
                    "timestamp": datetime.now().isoformat(),
                    "session_preserved": True
                })
                
                logger.info(f"A2A Agent added with session preservation: {agent_url}")
                return True
            else:
                logger.info(f"A2A Agent already exists: {agent_url}")
                return False
                
        except Exception as e:
            logger.error(f"Failed to add A2A agent {agent_url}: {e}")
            return False

    async def remove_agent(self, agent_url: str) -> bool:
        """Remove a single A2A agent from the agent with session preservation"""
        try:
            if agent_url in self._agent_urls:
                # Remove the agent URL
                new_agents = [url for url in self._agent_urls if url != agent_url]
                
                # Recreate the agent with preserved sessions
                await self.create(new_agents, preserve_sessions=True)
                
                # Record the change
                self._agent_history.append({
                    "action": "remove",
                    "url": agent_url,
                    "timestamp": datetime.now().isoformat(),
                    "session_preserved": True
                })
                
                logger.info(f"A2A Agent removed with session preservation: {agent_url}")
                return True
            else:
                logger.info(f"A2A Agent not found: {agent_url}")
                return False
                
        except Exception as e:
            logger.error(f"Failed to remove A2A agent {agent_url}: {e}")
            return False

    def get_agent_list(self) -> list:
        """Get current list of A2A agent URLs"""
        return self._agent_urls.copy()

    def get_agent_history(self) -> list:
        """Get history of agent changes"""
        return self._agent_history.copy()
    
    def get_available_agents(self) -> dict:
        """Get all available A2A agents"""
        agents = {}
        for url in self._agent_urls:
            agents[url] = {"description": f"A2A agent from {url}"}
        return agents

    async def close(self):
        """Clean up A2A agent connections when agent is destroyed"""
        self._agent_plugins.clear()
        logger.info("SKAgent cleanup completed")

class A2AAgentServer:
    """Framework-agnostic A2A Agent Server with injectable agent class"""
    
    def __init__(self, agent_class=None, config: Optional[AgentConfig] = None, agent_id: str = None, 
                 agent_name: str = None, a2a_agent_url: str = None, port: int = None):
        # Store injectable agent class (defaults to A2ATeamAgent for backward compatibility)
        self.agent_class = agent_class or A2ATeamAgent
        
        # Use config if provided, otherwise use individual parameters or defaults
        if config:
            self.config = config
            self.agent_id = config.id
            self.name = config.name
            self.description = config.description
            self.greeting = config.greeting
            self.instructions = config.instructions
            self.system_prompt = config.system_prompt
            self.model = config.model
            self.port = port or config.default_port
            self.host = config.host
            # Use config agent URLs if no a2a_agent_url specified
            self.a2a_agent_urls = [a2a_agent_url] if a2a_agent_url else config.default_agent_urls
        else:
            # Legacy mode - use individual parameters
            self.config = None
            self.agent_id = agent_id or DEFAULT_AGENT_ID
            self.name = agent_name or DEFAULT_AGENT_NAME
            self.description = "SK-powered A2A agent with agent-to-agent communication"
            self.greeting = f"Hello! I'm {self.name}."
            self.instructions = "I'm here to help you with various tasks by coordinating with other AI agents."
            self.system_prompt = "You are a helpful AI assistant that can coordinate with other AI agents to complete tasks."
            self.model = "gpt-3.5-turbo"
            self.port = port or DEFAULT_AGENT_PORT
            self.host = "0.0.0.0"
            self.a2a_agent_urls = [a2a_agent_url or DEFAULT_A2A_AGENT_URL]
            
        self.status = "active"
        self.tasks = {}  # Store tasks by ID
        self.available_agents = {}  # Cache discovered agents
        self.agent = None
        
        # For backward compatibility, expose a2a_agent_url as single URL
        self.a2a_agent_url = self.a2a_agent_urls[0] if self.a2a_agent_urls else DEFAULT_A2A_AGENT_URL
        
    async def initialize_agent(self):
        """Initialize the SK agent with A2A agents"""
        try:
            # Create agent with A2A agents using injected agent class
            valid_agent_name = self.name.replace(" ", "_").replace("-", "_")
            self.agent = self.agent_class(
                model=self.model,
                agent_name=valid_agent_name,
                agent_description=self.description,
                agent_instruction=self.system_prompt
            )
            
            # Pass A2A URLs directly to SK agent for direct plugin connection
            a2a_urls = self.a2a_agent_urls
            await self.agent.create(a2a_urls)
            
            # For compatibility, populate available_agents from connected plugins
            self.available_agents = {}
            for i, url in enumerate(a2a_urls):
                # Add placeholder entries for each A2A URL
                self.available_agents[f"a2a_agent_{i}"] = {
                    "description": f"A2A agent from {url}",
                    "url": url
                }
            
            logger.info(f"SK agent initialized with {len(a2a_urls)} A2A agent plugins")
            
        except Exception as e:
            logger.error(f"Failed to initialize SK agent: {e}")
            # Fallback: create agent without A2A agents
            valid_agent_name = self.name.replace(" ", "_").replace("-", "_")
            self.agent = self.agent_class(
                model=self.model,
                agent_name=valid_agent_name,
                agent_description=self.description,
                agent_instruction=self.system_prompt
            )
            await self.agent.create([])
        
    async def discover_a2a_agents(self) -> Dict[str, Any]:
        """Discover available capabilities from all configured A2A agents"""
        total_capabilities_discovered = 0
        discovery_results = []
        
        # Clear the existing agents cache to ensure fresh discovery
        self.available_agents = {}
        
        try:
            async with aiohttp.ClientSession() as session:
                # Use current SK agent URLs if available, otherwise use static config
                a2a_urls_to_discover = self.agent.get_agent_list() if self.agent else self.a2a_agent_urls
                
                # Iterate through all current A2A agent URLs
                for a2a_url in a2a_urls_to_discover:
                    try:
                        logger.info(f"Discovering capabilities from A2A agent: {a2a_url}")
                        
                        # Fetch agent card
                        async with session.get(f"{a2a_url}/.well-known/agent-card.json") as response:
                            if response.status == 200:
                                agent_card = await response.json()
                                capabilities = agent_card.get("skills", [])
                                agent_capabilities_count = len(capabilities)
                                
                                for capability in capabilities:
                                    capability_name = capability.get("name", "unknown_capability")
                                    # Avoid duplicate capability names by prefixing with agent info if needed
                                    if capability_name in self.available_agents:
                                        # Add agent info to distinguish duplicate capability names
                                        agent_port = a2a_url.split(':')[-1] if ':' in a2a_url else 'unknown'
                                        capability_name = f"{capability['name']}_agent{agent_port}"
                                        
                                    self.available_agents[capability_name] = capability
                                
                                total_capabilities_discovered += agent_capabilities_count
                                discovery_results.append({
                                    "url": a2a_url,
                                    "success": True,
                                    "capabilities_count": agent_capabilities_count,
                                    "capabilities": [c["name"] for c in capabilities]
                                })
                                logger.info(f"Discovered {agent_capabilities_count} capabilities from {a2a_url}: {[c['name'] for c in capabilities]}")
                            else:
                                discovery_results.append({
                                    "url": a2a_url,
                                    "success": False,
                                    "error": f"Failed to fetch agent card (status {response.status})"
                                })
                                logger.warning(f"Failed to get agent card from {a2a_url}")
                                
                    except Exception as e:
                        error_msg = str(e)
                        discovery_results.append({
                            "url": a2a_url,
                            "success": False,
                            "error": error_msg
                        })
                        logger.error(f"Exception discovering capabilities from {a2a_url}: {error_msg}")
                
                # Summary
                successful_agents = len([r for r in discovery_results if r["success"]])
                a2a_urls_to_discover = self.agent.get_agent_list() if self.agent else self.a2a_agent_urls
                total_agents = len(a2a_urls_to_discover)
                
                logger.info(f"Agent discovery complete: {total_capabilities_discovered} capabilities from {successful_agents}/{total_agents} agents")
                logger.info(f"Available capabilities: {list(self.available_agents.keys())}")
                
                return {
                    "success": total_capabilities_discovered > 0,
                    "agents": self.available_agents,
                    "total_capabilities": total_capabilities_discovered,
                    "agents_contacted": total_agents,
                    "successful_agents": successful_agents,
                    "discovery_results": discovery_results
                }
                        
        except Exception as e:
            error_msg = str(e)
            logger.error(f"Failed to discover A2A agents: {error_msg}")
            return {"success": False, "error": error_msg}
    
    async def process_task(self, task_message: str, session_id: str) -> str:
        """Process a task using SK agent"""
        
        # Ensure SK agent is initialized
        if not self.agent:
            await self.initialize_agent()
        
        try:
            # Use SK agent to process the message
            response = await self.agent.invoke(task_message, session_id)
            return response
            
        except Exception as e:
            logger.error(f"Error processing task with SK agent: {e}")
            return f"I apologize, but I encountered an error processing your request: {str(e)}"
    
    def create_task(self, task_id: str, message: str, session_id: str = None) -> Dict[str, Any]:
        """Create a new task"""
        task = {
            "id": task_id,
            "status": "submitted",
            "created_at": datetime.now().isoformat(),
            "session_id": session_id,
            "messages": [
                {
                    "role": "user",
                    "content": message,
                    "timestamp": datetime.now().isoformat()
                }
            ],
            "result": None,
            "updated_at": datetime.now().isoformat()
        }
        self.tasks[task_id] = task
        return task

    def get_task(self, task_id: str) -> Dict[str, Any]:
        """Get a task by ID"""
        return self.tasks.get(task_id)

    def update_task_status(self, task_id: str, status: str, result: str = None) -> bool:
        """Update task status and result"""
        if task_id in self.tasks:
            self.tasks[task_id]["status"] = status
            if result:
                self.tasks[task_id]["result"] = result
                self.tasks[task_id]["messages"].append({
                    "role": "agent",
                    "content": result,
                    "timestamp": datetime.now().isoformat()
                })
            self.tasks[task_id]["updated_at"] = datetime.now().isoformat()
            return True
        return False
    
    async def handle_message_send(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Handle A2A message/send method"""
        # First check if content is directly in params (JSON-RPC style)
        if "content" in params:
            message_text = params["content"]
        else:
            # Otherwise look for message object
            message = params.get("message", {})
            # Extract message text
            message_text = ""
            if isinstance(message, dict):
                if "content" in message:
                    message_text = message["content"]
                elif "text" in message:
                    message_text = message["text"]
            elif isinstance(message, str):
                message_text = message
        
        task_id = params.get("taskId", str(uuid.uuid4()))
        session_id = params.get("sessionId")
        
        # Create task
        task = self.create_task(task_id, message_text, session_id)
        
        # Update task status to working
        self.update_task_status(task_id, "working")
        
        try:
            # Process the message with SK agent
            response = await self.process_task(message_text, session_id or "default")
            
            # Update task with result
            self.update_task_status(task_id, "completed", response)
            
            return {
                "taskId": task_id,
                "status": "completed",
                "result": {
                    "message": {
                        "role": "agent",
                        "content": response
                    }
                }
            }
        except Exception as e:
            self.update_task_status(task_id, "failed", str(e))
            return {
                "taskId": task_id,
                "status": "failed",
                "error": {
                    "code": -32603,
                    "message": "Internal error",
                    "data": str(e)
                }
            }

# Create global agent instance
agent = None

# Pydantic models
class ChatRequest(BaseModel):
    user_message: str
    session_id: str = "default"

class ChatResponse(BaseModel):
    response: str
    session_id: str

# Create FastAPI app
app = FastAPI(title="SK A2A Agent with A2A Agent-to-Agent Communication")

@app.get("/.well-known/agent-card.json")
async def get_agent_card():
    """A2A Agent Card discovery endpoint (A2A spec compliant)"""
    
    # Ensure agent is initialized
    if not agent.agent:
        await agent.initialize_agent()
    
    # Build skills dynamically from discovered agents
    skills = []
    for capability_name, capability_info in agent.available_agents.items():
        skills.append({
            "name": capability_name,
            "description": capability_info.get("description", f"A2A agent capability: {capability_name}"),
            "parameters": capability_info.get("parameters", {})
        })
    
    # Add general response capability
    skills.append({
        "name": "general_conversation",
        "description": "General conversational AI powered by Semantic Kernel with A2A agent access"
    })
    
    agent_card = {
        "name": agent.name,
        "description": agent.description,
        "version": getattr(agent.config, 'version', '1.0.0') if agent.config else "1.0.0",
        "url": f"http://{agent.host}:{agent.port}",
        "preferredTransport": "http",
        "authentication": {
            "type": "none"
        },
        "capabilities": {
            "messageTypes": ["text"],
            "streaming": False,
            "taskManagement": True
        },
        "skills": skills,
        "greeting": agent.greeting,
        "instructions": agent.instructions,
        "metadata": {
            "a2a_agent_urls": agent.a2a_agent_urls,
            "agent_id": agent.agent_id,
            "status": agent.status,
            "llm_model": agent.model,
            "sk_powered": True,
            "agent_to_agent": True,
            "personality": {
                "style": getattr(agent.config, 'style', 'helpful and friendly') if agent.config else "helpful and friendly",
                "tone": getattr(agent.config, 'tone', 'professional') if agent.config else "professional",
                "expertise": getattr(agent.config, 'expertise', 'general assistance with agent coordination') if agent.config else "general assistance with agent coordination"
            } if agent.config else {}
        }
    }
    
    return JSONResponse(agent_card)


@app.route("/", methods=["POST"])
async def handle_jsonrpc(request):
    """Handle JSON-RPC requests"""
    try:
        body = await request.json()
        logger.info(f"Received JSON-RPC request: {json.dumps(body, indent=2)}")
        
        jsonrpc_version = body.get("jsonrpc")
        method = body.get("method")
        params = body.get("params", {})
        request_id = body.get("id")
        
        if jsonrpc_version != "2.0":
            return JSONResponse({
                "jsonrpc": "2.0",
                "id": request_id,
                "error": {
                    "code": -32600,
                    "message": "Invalid Request - JSON-RPC 2.0 required"
                }
            })
        
        # Handle different methods
        if method == "message/send":
            result = await agent.handle_message_send(params)
            return JSONResponse({
                "jsonrpc": "2.0",
                "id": request_id,
                "result": result
            })
            
        elif method == "tasks/get":
            task_id = params.get("taskId")
            if not task_id:
                return JSONResponse({
                    "jsonrpc": "2.0",
                    "id": request_id,
                    "error": {
                        "code": -32602,
                        "message": "Invalid params - taskId required"
                    }
                })
            
            task = agent.get_task(task_id)
            if not task:
                return JSONResponse({
                    "jsonrpc": "2.0",
                    "id": request_id,
                    "error": {
                        "code": -32603,
                        "message": "Task not found"
                    }
                })
            
            return JSONResponse({
                "jsonrpc": "2.0",
                "id": request_id,
                "result": task
            })
            
        elif method == "tasks/cancel":
            task_id = params.get("taskId")
            if task_id and task_id in agent.tasks:
                agent.update_task_status(task_id, "cancelled")
                return JSONResponse({
                    "jsonrpc": "2.0",
                    "id": request_id,
                    "result": {"success": True, "taskId": task_id}
                })
            
            return JSONResponse({
                "jsonrpc": "2.0",
                "id": request_id,
                "error": {
                    "code": -32603,
                    "message": "Task not found or cannot be cancelled"
                }
            })
            
        elif method == "agents/add":
            agent_url = params.get("url")
            if not agent_url:
                return JSONResponse({
                    "jsonrpc": "2.0",
                    "id": request_id,
                    "error": {
                        "code": -32602,
                        "message": "Invalid params - url required"
                    }
                })
            
            # Ensure SK agent is initialized
            if not agent.agent:
                await agent.initialize_agent()
                
            success = await agent.agent.add_agent(agent_url)
            
            # Update the agent's available_agents cache to refresh agent card
            if success:
                await agent.discover_a2a_agents()
                logger.info(f"Agent card updated after adding agent: {agent_url}")
            
            return JSONResponse({
                "jsonrpc": "2.0",
                "id": request_id,
                "result": {
                    "success": success,
                    "message": f"Agent {'added' if success else 'already exists or failed to add'}: {agent_url}",
                    "current_agents": list(agent.available_agents.keys()) if success else None
                }
            })
            
        elif method == "agents/remove":
            agent_url = params.get("url")
            if not agent_url:
                return JSONResponse({
                    "jsonrpc": "2.0",
                    "id": request_id,
                    "error": {
                        "code": -32602,
                        "message": "Invalid params - url required"
                    }
                })
            
            # Ensure SK agent is initialized
            if not agent.agent:
                await agent.initialize_agent()
                
            success = await agent.agent.remove_agent(agent_url)
            
            # Update the agent's available_agents cache to refresh agent card
            if success:
                await agent.discover_a2a_agents()
                logger.info(f"Agent card updated after removing agent: {agent_url}")
            
            return JSONResponse({
                "jsonrpc": "2.0",
                "id": request_id,
                "result": {
                    "success": success,
                    "message": f"Agent {'removed' if success else 'not found or failed to remove'}: {agent_url}",
                    "current_agents": list(agent.available_agents.keys()) if success else None
                }
            })
            
        elif method == "agents/list":
            # Ensure SK agent is initialized
            if not agent.agent:
                await agent.initialize_agent()
                
            agent_list = agent.agent.get_agent_list()
            return JSONResponse({
                "jsonrpc": "2.0",
                "id": request_id,
                "result": {
                    "agents": agent_list,
                    "count": len(agent_list)
                }
            })
            
        elif method == "agents/history":
            # Ensure SK agent is initialized
            if not agent.agent:
                await agent.initialize_agent()
                
            history = agent.agent.get_agent_history()
            return JSONResponse({
                "jsonrpc": "2.0",
                "id": request_id,
                "result": {
                    "history": history,
                    "count": len(history)
                }
            })
            
        else:
            return JSONResponse({
                "jsonrpc": "2.0",
                "id": request_id,
                "error": {
                    "code": -32601,
                    "message": f"Method not found: {method}"
                }
            })
            
    except Exception as e:
        logger.error(f"Error handling JSON-RPC request: {e}")
        return JSONResponse({
            "jsonrpc": "2.0",
            "id": body.get("id") if "body" in locals() else None,
            "error": {
                "code": -32603,
                "message": "Internal error",
                "data": str(e)
            }
        })

def parse_args():
    parser = argparse.ArgumentParser(description="SK-Powered A2A Agent Server with A2A Agent-to-Agent Communication")
    
    # Configuration file option (new)
    parser.add_argument("--config", type=str, 
                      help="Path to YAML configuration file (e.g., agentA.yaml)")
    
    # Legacy individual options (maintained for backward compatibility)
    parser.add_argument("--a2a-url", default=os.getenv("A2A_AGENT_URL", DEFAULT_A2A_AGENT_URL),
                      help="A2A agent server URL (overrides config file)")
    parser.add_argument("--agent-id", default=os.getenv("AGENT_ID", DEFAULT_AGENT_ID),
                      help="Agent ID (overrides config file)")
    parser.add_argument("--agent-name", default=os.getenv("AGENT_NAME", DEFAULT_AGENT_NAME),
                      help="Agent name (overrides config file)")
    parser.add_argument("--port", type=int, default=int(os.getenv("AGENT_PORT", DEFAULT_AGENT_PORT)),
                      help="Server port (overrides config file)")
    return parser.parse_args()

if __name__ == "__main__":
    args = parse_args()
    
    # Load configuration if provided
    config = None
    if args.config:
        config = load_agent_config(args.config)
        print("🔧 Configuration loaded from:", args.config)
    
    # Create global agent instance (config takes precedence, args override)
    if config:
        agent = A2AAgentServer(
            agent_class=A2ATeamAgent,  # Explicitly inject A2A Team agent
            config=config,
            a2a_agent_url=args.a2a_url if args.a2a_url != DEFAULT_A2A_AGENT_URL else None,
            port=args.port if args.port != DEFAULT_AGENT_PORT else None
        )
    else:
        agent = A2AAgentServer(
            agent_class=A2ATeamAgent,  # Explicitly inject A2A Team agent
            agent_id=args.agent_id,
            agent_name=args.agent_name,
            a2a_agent_url=args.a2a_url,
            port=args.port
        )
    
    # Display startup information
    print("🤖 SK-Powered A2A Agent Server - Agent-to-Agent Communication")
    print("=" * 70)
    print(f"Configuration: {'YAML Config' if config else 'Command Line'}")
    print(f"Agent ID: {agent.agent_id}")
    print(f"Agent Name: {agent.name}")
    print(f"Description: {agent.description}")
    print(f"A2A Agent URLs: {agent.a2a_agent_urls}")
    print(f"Port: {agent.port}")
    print(f"LLM Model: {agent.model}")
    if config:
        print(f"Personality: {agent.config.style}, {agent.config.tone}")
        print(f"Expertise: {agent.config.expertise}")
    print()
    
    logger.info("🤖 Starting SK-Powered A2A Agent with Agent-to-Agent Communication")
    logger.info(f"🆔 Agent ID: {agent.agent_id}")
    logger.info(f"🔧 A2A Agent URLs: {agent.a2a_agent_urls}")
    logger.info(f"🧠 LLM Model: {agent.model}")
    logger.info(f"🌐 Server starting on http://{agent.host}:{agent.port}")
    
    # Initialize the SK agent
    import asyncio
    asyncio.run(agent.initialize_agent())
    logger.info("🚀 SK agent initialized successfully")
    
    # Run the server
    uvicorn.run(app, host="0.0.0.0", port=agent.port)