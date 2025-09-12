#!/usr/bin/env python3
"""
SK-Powered A2A Agent Server - Training Example with Configuration Support
A2A server with Microsoft Semantic Kernel integration and dynamic MCP tool calling
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
# from contextlib import AsyncExitStack  # Not needed for simple working pattern
from collections import defaultdict
import requests

try:
    from starlette.applications import Starlette
    from starlette.responses import JSONResponse
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
    from semantic_kernel.connectors.mcp import MCPSsePlugin
    from semantic_kernel.functions import kernel_function
    from semantic_kernel.contents.chat_history import ChatHistory
    from semantic_kernel.contents.chat_message_content import ChatMessageContent
    from semantic_kernel.contents.utils.author_role import AuthorRole
except ImportError:
    print("❌ ERROR: Semantic Kernel not found!")
    print("📦 Install Semantic Kernel:")
    print("   pip install semantic-kernel")
    exit(1)

from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Default Configuration
DEFAULT_AGENT_ID = "sk-a2a-training-agent"
DEFAULT_AGENT_NAME = "SK A2A Training Agent"
DEFAULT_AGENT_PORT = 5002
DEFAULT_MCP_TOOL_URL = "http://localhost:8002/mcp"  # Default weather MCP tool URL

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

async def parse_mcp_response(response) -> dict:
    """Parse HTTP response from MCP server (handles both JSON and SSE)"""
    if response.status != 200:
        logger.error(f"MCP server returned status {response.status}")
        return None
    
    try:
        # Check content type
        content_type = response.headers.get('content-type', '').lower()
        
        if 'application/json' in content_type:
            # Direct JSON response
            return await response.json()
        else:
            # SSE format or other - parse as text
            response_text = await response.text()
            # Look for SSE data line
            for line in response_text.split('\n'):
                if line.startswith('data: '):
                    return json.loads(line[6:])  # Remove 'data: ' prefix
            return None
            
    except Exception as e:
        logger.error(f"Failed to parse MCP response: {e}")
        return None

# Configuration Management
class AgentConfig:
    """Agent configuration loaded from YAML files"""
    
    def __init__(self, config_data: Dict[str, Any]):
        self.agent = config_data.get("agent", {})
        self.id = self.agent.get("id", DEFAULT_AGENT_ID)
        self.name = self.agent.get("name", DEFAULT_AGENT_NAME)
        self.version = self.agent.get("version", "1.0.0")
        self.description = self.agent.get("description", "SK-powered A2A agent")
        
        # Agent card properties
        self.card = self.agent.get("card", {})
        self.greeting = self.card.get("greeting", f"Hello! I'm {self.name}.")
        self.instructions = self.card.get("instructions", "I'm here to help you with various tasks.")
        
        # Agent personality
        self.personality = self.agent.get("personality", {})
        self.style = self.personality.get("style", "helpful and friendly")
        self.tone = self.personality.get("tone", "professional")
        self.expertise = self.personality.get("expertise", "general assistance")
        
        # Tools configuration
        self.tools = self.agent.get("tools", {})
        self.default_tool_urls = self.tools.get("default_urls", [DEFAULT_MCP_TOOL_URL])
        
        # Server configuration
        self.server = self.agent.get("server", {})
        self.default_port = self.server.get("default_port", DEFAULT_AGENT_PORT)
        self.host = self.server.get("host", "0.0.0.0")
        
        # LLM configuration
        self.llm = self.agent.get("llm", {})
        self.model = self.llm.get("model", "gpt-3.5-turbo")
        self.system_prompt = self.llm.get("system_prompt", "You are a helpful AI assistant.")

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


class StatefulMCPClient:
    """Stateful MCP client that maintains persistent sessions"""
    
    def __init__(self, base_url: str):
        self.base_url = base_url
        self.session = requests.Session()
        self.session_id = None
        self.initialized = False
        self.tools_cache = {}
    
    async def initialize(self):
        """Initialize MCP session"""
        payload = {
            "jsonrpc": "2.0",
            "id": 1,
            "method": "initialize",
            "params": {
                "protocolVersion": "2024-11-05",
                "capabilities": {
                    "roots": {"listChanged": True},
                    "sampling": {}
                },
                "clientInfo": {
                    "name": "sk-a2a-agent",
                    "version": "1.0.0"
                }
            }
        }
        
        headers = {
            "Content-Type": "application/json",
            "Accept": "application/json, text/event-stream"
        }
        
        try:
            response = self.session.post(f"{self.base_url}/mcp", json=payload, headers=headers, timeout=10)
            
            if response.status_code == 200:
                # Extract session ID from headers
                self.session_id = response.headers.get('mcp-session-id')
                if self.session_id:
                    logger.info(f"✅ MCP Session initialized: {self.session_id} for {self.base_url}")
                    self.initialized = True
                    
                    # Send notifications required by MCP protocol
                    await self.send_notifications()
                    return True
                else:
                    logger.warning(f"❌ No session ID in response from {self.base_url}")
                    return False
            else:
                logger.error(f"❌ MCP Initialization failed for {self.base_url}: {response.text}")
                return False
                
        except Exception as e:
            logger.error(f"❌ MCP Initialization error for {self.base_url}: {e}")
            return False
    
    async def send_notifications(self):
        """Send required notifications after initialization"""
        notifications = [
            {
                "jsonrpc": "2.0",
                "method": "notifications/initialized"
            }
        ]
        
        headers = {
            "Content-Type": "application/json",
            "Accept": "application/json, text/event-stream",
            "Mcp-Session-Id": self.session_id
        }
        
        for notification in notifications:
            try:
                response = self.session.post(f"{self.base_url}/mcp", json=notification, headers=headers, timeout=5)
                logger.debug(f"Notification sent: {notification['method']} -> {response.status_code}")
            except Exception as e:
                logger.error(f"Notification failed: {e}")
    
    async def list_tools(self):
        """Get list of available tools from MCP server"""
        if not self.initialized:
            logger.error("❌ MCP Session not initialized")
            return []
        
        payload = {
            "jsonrpc": "2.0",
            "id": 1,
            "method": "tools/list"
        }
        
        headers = {
            "Content-Type": "application/json",
            "Accept": "application/json, text/event-stream",
            "Mcp-Session-Id": self.session_id
        }
        
        try:
            response = self.session.post(f"{self.base_url}/mcp", json=payload, headers=headers, timeout=10)
            
            if response.status_code == 200:
                if response.headers.get('content-type', '').startswith('text/event-stream'):
                    lines = response.text.strip().split('\n')
                    for line in lines:
                        if line.startswith('data: '):
                            data = line[6:]
                            try:
                                result = json.loads(data)
                                if 'result' in result and 'tools' in result['result']:
                                    self.tools_cache = {tool['name']: tool for tool in result['result']['tools']}
                                    return result['result']['tools']
                            except json.JSONDecodeError:
                                logger.error(f"Failed to parse tools response: {data}")
                                return []
                else:
                    result = response.json()
                    if 'result' in result and 'tools' in result['result']:
                        self.tools_cache = {tool['name']: tool for tool in result['result']['tools']}
                        return result['result']['tools']
            else:
                logger.error(f"❌ Failed to list tools from {self.base_url} ({response.status_code}): {response.text}")
                return []
                
        except Exception as e:
            logger.error(f"❌ Error listing tools from {self.base_url}: {e}")
            return []
    
    async def call_tool(self, tool_name: str, arguments: dict = None):
        """Call a tool with proper session handling"""
        if not self.initialized:
            logger.error("❌ MCP Session not initialized")
            return None
        
        payload = {
            "jsonrpc": "2.0",
            "id": 2,
            "method": "tools/call",
            "params": {
                "name": tool_name,
                "arguments": arguments or {}
            }
        }
        
        headers = {
            "Content-Type": "application/json",
            "Accept": "application/json, text/event-stream",
            "Mcp-Session-Id": self.session_id
        }
        
        try:
            response = self.session.post(f"{self.base_url}/mcp", json=payload, headers=headers, timeout=15)
            
            if response.status_code == 200:
                if response.headers.get('content-type', '').startswith('text/event-stream'):
                    lines = response.text.strip().split('\n')
                    for line in lines:
                        if line.startswith('data: '):
                            data = line[6:]
                            try:
                                result = json.loads(data)
                                return result
                            except json.JSONDecodeError:
                                logger.error(f"Failed to parse tool response: {data}")
                                return None
                else:
                    return response.json()
            else:
                logger.error(f"❌ Tool call failed for {tool_name}: {response.text}")
                return None
                
        except Exception as e:
            logger.error(f"❌ Tool call error for {tool_name}: {e}")
            return None


class A2AAgent:
    """Semantic Kernel-powered agent"""
    
    def __init__(self, model="gpt-3.5-turbo", agent_name="SK Agent", 
                 agent_description="SK-powered agent", agent_instruction="You are a helpful assistant."):
        self._model = model
        self._name = agent_name
        self._description = agent_description
        self._instruction = agent_instruction
        self._kernel = None
        self._agent = None
        self._chat_service = None
        self._tool_plugins = {}
        self._tool_urls = []
        self._tool_history = []
        # self._tool_exit_stack = AsyncExitStack()  # Not needed for simple working pattern
        
        # Session management - maintain chat history per session
        self._sessions = defaultdict(lambda: {
            "chat_history": ChatHistory(),
            "created_at": datetime.now().isoformat()
        })

    async def create(self, mcp_urls: list = None, preserve_sessions: bool = False):
        """Initialize the SK agent with MCP tools"""
        if mcp_urls is None:
            mcp_urls = []
        
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
                # You would implement a mock service here for testing
                
            if self._chat_service:
                self._kernel.add_service(self._chat_service)
            
            # Clear existing plugins if not preserving sessions
            if not preserve_sessions:
                self._tool_plugins = {}
                self._sessions.clear()
            
            # Add MCP plugins to kernel using proven working pattern
            for url in mcp_urls:
                await self._add_mcp_plugin_to_kernel(url)
            
            # Store tool URLs
            self._tool_urls = mcp_urls.copy()
            
            # Create the agent using proven working pattern (no plugins=[], no FunctionChoiceBehavior)
            self._agent = ChatCompletionAgent(
                kernel=self._kernel,
                name=self._name,
                description=self._description,
                id=self._name.replace(" ", "_"),
                instructions=self._instruction
            )
            
            logger.info(f"SK agent '{self._name}' {'recreated' if preserve_sessions else 'created'} successfully with {len(self._tool_plugins)} MCP tool plugins")
            if preserve_sessions:
                logger.info("Sessions preserved across agent recreation")
            
            return self
            
        except Exception as e:
            logger.error(f"Failed to create SK agent: {e}")
            raise

    async def _add_mcp_plugin_to_kernel(self, url: str):
        """Add MCP plugin to kernel using MCPSsePlugin (same as working A2A_agent_with_MCP)"""
        try:
            # Create MCPSsePlugin using same pattern as working reference
            plugin = MCPSsePlugin(
                name=f"mcp_plugin_{url.replace('://', '_').replace('/', '_').replace(':', '_')}",
                description=f"MCP tools from {url}",
                url=url
            )
            
            # Use the exact working pattern from A2A_agent_with_MCP: connect then add directly
            await plugin.connect()
            self._kernel.add_plugin(plugin)
            
            # Store plugin for reference
            self._tool_plugins[url] = plugin
            
            logger.info(f"Connected and added MCP plugin from {url} to kernel")
                
        except Exception as e:
            logger.error(f"Failed to add MCP plugin from {url}: {e}")
            # Don't raise, continue with other plugins

    async def invoke(self, query: str, session_id: str, user_id: str = "agent_user") -> str:
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
            
            
            # Get response with full conversation context and tool calling enabled
            response = await self._agent.get_response(
                messages=chat_history,
                user_id=user_id,
                session_id=session_id
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

    async def add_tool(self, tool_url: str) -> bool:
        """Add a single tool to the agent with session preservation"""
        try:
            if tool_url not in self._tool_urls:
                # Add the new tool URL
                new_tools = self._tool_urls + [tool_url]
                
                # Recreate the agent with preserved sessions
                await self.create(new_tools, preserve_sessions=True)
                
                # Record the change
                self._tool_history.append({
                    "action": "add",
                    "url": tool_url,
                    "timestamp": datetime.now().isoformat(),
                    "session_preserved": True
                })
                
                logger.info(f"Tool added with session preservation: {tool_url}")
                return True
            else:
                logger.info(f"Tool already exists: {tool_url}")
                return False
                
        except Exception as e:
            logger.error(f"Failed to add tool {tool_url}: {e}")
            return False

    async def remove_tool(self, tool_url: str) -> bool:
        """Remove a single tool from the agent with session preservation"""
        try:
            if tool_url in self._tool_urls:
                # Remove the tool URL
                new_tools = [url for url in self._tool_urls if url != tool_url]
                
                # Recreate the agent with preserved sessions
                await self.create(new_tools, preserve_sessions=True)
                
                # Record the change
                self._tool_history.append({
                    "action": "remove",
                    "url": tool_url,
                    "timestamp": datetime.now().isoformat(),
                    "session_preserved": True
                })
                
                logger.info(f"Tool removed with session preservation: {tool_url}")
                return True
            else:
                logger.info(f"Tool not found: {tool_url}")
                return False
                
        except Exception as e:
            logger.error(f"Failed to remove tool {tool_url}: {e}")
            return False

    def get_tool_list(self) -> list:
        """Get current list of tool URLs"""
        return self._tool_urls.copy()

    def get_tool_history(self) -> list:
        """Get history of tool changes"""
        return self._tool_history.copy()
    
    def get_available_tools(self) -> dict:
        """Get all available tools from all plugins"""
        tools = {}
        # Note: MCPSsePlugin doesn't expose available_tools directly
        # Tools are registered in the kernel, so we return the URLs for now
        for url in self._tool_urls:
            tools[url] = {"description": f"MCP tools from {url}"}
        return tools

    async def close(self):
        """Clean up MCP plugin connections when agent is destroyed"""
        try:
            await self._tool_exit_stack.aclose()
            logger.info("AsyncExitStack closed")
        except Exception as e:
            logger.warning(f"Failed to close AsyncExitStack: {e}")
        
        self._tool_plugins.clear()
        logger.info("SKAgent cleanup completed")

class A2AAgentServer:
    """SK-powered A2A Agent with dynamic MCP tool discovery"""
    
    def __init__(self, config: Optional[AgentConfig] = None, agent_id: str = None, 
                 agent_name: str = None, mcp_tool_url: str = None, port: int = None):
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
            # Use config tool URLs if no mcp_tool_url specified
            self.mcp_tool_urls = [mcp_tool_url] if mcp_tool_url else config.default_tool_urls
        else:
            # Legacy mode - use individual parameters
            self.config = None
            self.agent_id = agent_id or DEFAULT_AGENT_ID
            self.name = agent_name or DEFAULT_AGENT_NAME
            self.description = "SK-powered A2A agent"
            self.greeting = f"Hello! I'm {self.name}."
            self.instructions = "I'm here to help you with various tasks."
            self.system_prompt = "You are a helpful AI assistant."
            self.model = "gpt-3.5-turbo"
            self.port = port or DEFAULT_AGENT_PORT
            self.host = "0.0.0.0"
            self.mcp_tool_urls = [mcp_tool_url or DEFAULT_MCP_TOOL_URL]
            
        self.status = "active"
        self.tasks = {}  # Store tasks by ID
        self.available_tools = {}  # Cache discovered tools
        self.sk_agent = None
        
        # For backward compatibility, expose mcp_tool_url as single URL
        self.mcp_tool_url = self.mcp_tool_urls[0] if self.mcp_tool_urls else DEFAULT_MCP_TOOL_URL
        
    async def initialize_agent(self):
        """Initialize the SK agent with MCP tools (skip startup discovery, use direct plugin connection)"""
        try:
            # Create SK agent with MCP tools (skip startup discovery - use working A2A pattern)
            valid_agent_name = self.name.replace(" ", "_").replace("-", "_")
            self.sk_agent = A2AAgent(
                model=self.model,
                agent_name=valid_agent_name,
                agent_description=self.description,
                agent_instruction=self.system_prompt
            )
            
            # Pass MCP URLs directly to SK agent for direct plugin connection (working A2A pattern)
            mcp_urls = self.mcp_tool_urls
            await self.sk_agent.create(mcp_urls)
            
            # For compatibility, populate available_tools from connected plugins
            self.available_tools = {}
            for i, url in enumerate(mcp_urls):
                # Add placeholder entries for each MCP URL
                self.available_tools[f"mcp_tools_{i}"] = {
                    "description": f"MCP tools from {url}",
                    "url": url
                }
            
            logger.info(f"SK agent initialized with {len(mcp_urls)} MCP tool plugins (using direct connection)")
            
        except Exception as e:
            logger.error(f"Failed to initialize SK agent: {e}")
            # Fallback: create agent without MCP tools
            valid_agent_name = self.name.replace(" ", "_").replace("-", "_")
            self.sk_agent = A2AAgent(
                model=self.model,
                agent_name=valid_agent_name,
                agent_description=self.description,
                agent_instruction=self.system_prompt
            )
            await self.sk_agent.create([])
        
    async def discover_mcp_tools(self) -> Dict[str, Any]:
        """Discover available tools from all configured MCP servers"""
        total_tools_discovered = 0
        discovery_results = []
        
        # Clear the existing tools cache to ensure fresh discovery
        self.available_tools = {}
        
        try:
            payload = {
                "jsonrpc": "2.0",
                "id": str(uuid.uuid4()),
                "method": "tools/list"
            }
            
            async with aiohttp.ClientSession() as session:
                # Use current SK agent tool URLs if available, otherwise use static config
                mcp_urls_to_discover = self.sk_agent.get_tool_list() if self.sk_agent else self.mcp_tool_urls
                
                # Iterate through all current MCP tool URLs
                for mcp_url in mcp_urls_to_discover:
                    try:
                        logger.info(f"Discovering tools from MCP server: {mcp_url}")
                        
                        async with session.post(
                            mcp_url,
                            json=payload,
                            headers={
                                "Content-Type": "application/json",
                                "Accept": "application/json, text/event-stream"
                            }
                        ) as response:
                            result = await parse_mcp_response(response)
                            
                            if result and result.get("result", {}).get("tools"):
                                tools_list = result["result"]["tools"]
                                server_tools_count = 0
                                for tool in tools_list:
                                    # Avoid duplicate tool names by prefixing with server info if needed
                                    tool_name = tool["name"]
                                    if tool_name in self.available_tools:
                                        # Add server info to distinguish duplicate tool names
                                        server_port = mcp_url.split(':')[-2].split('/')[-1] if ':' in mcp_url else 'unknown'
                                        tool_name = f"{tool['name']}_port{server_port}"
                                        
                                    self.available_tools[tool_name] = tool
                                    server_tools_count += 1
                                
                                total_tools_discovered += server_tools_count
                                discovery_results.append({
                                    "url": mcp_url,
                                    "success": True,
                                    "tools_count": server_tools_count,
                                    "tools": [t["name"] for t in tools_list]
                                })
                                logger.info(f"Discovered {server_tools_count} tools from {mcp_url}: {[t['name'] for t in tools_list]}")
                            else:
                                discovery_results.append({
                                    "url": mcp_url,
                                    "success": False,
                                    "error": "No tools found in response"
                                })
                                logger.warning(f"No tools found from {mcp_url}")
                                
                    except Exception as e:
                        error_msg = str(e)
                        discovery_results.append({
                            "url": mcp_url,
                            "success": False,
                            "error": error_msg
                        })
                        logger.error(f"Exception discovering tools from {mcp_url}: {error_msg}")
                
                # Summary
                successful_servers = len([r for r in discovery_results if r["success"]])
                mcp_urls_to_discover = self.sk_agent.get_tool_list() if self.sk_agent else self.mcp_tool_urls
                total_servers = len(mcp_urls_to_discover)
                
                logger.info(f"Tool discovery complete: {total_tools_discovered} tools from {successful_servers}/{total_servers} servers")
                logger.info(f"Available tools: {list(self.available_tools.keys())}")
                
                return {
                    "success": total_tools_discovered > 0,
                    "tools": self.available_tools,
                    "total_tools": total_tools_discovered,
                    "servers_contacted": total_servers,
                    "successful_servers": successful_servers,
                    "discovery_results": discovery_results
                }
                        
        except Exception as e:
            error_msg = str(e)
            logger.error(f"Failed to discover MCP tools: {error_msg}")
            return {"success": False, "error": error_msg}
    
    async def process_task(self, task_message: str, session_id: str) -> str:
        """Process a task using SK agent"""
        
        # Ensure agent is initialized
        if not self.sk_agent:
            await self.initialize_agent()
        
        try:
            # Use SK agent to process the message
            response = await self.sk_agent.invoke(task_message, session_id)
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
        message = params.get("message", {})
        task_id = params.get("taskId", str(uuid.uuid4()))
        session_id = params.get("sessionId")
        
        # Extract message text
        message_text = ""
        if isinstance(message, dict):
            if "content" in message:
                message_text = message["content"]
            elif "text" in message:
                message_text = message["text"]
        elif isinstance(message, str):
            message_text = message
        
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

# Create Starlette app
app = Starlette()

@app.route("/.well-known/agent-card.json", methods=["GET"])
async def get_agent_card(request):
    """A2A Agent Card discovery endpoint (A2A spec compliant)"""
    
    # Ensure agent is initialized
    if not agent.sk_agent:
        await agent.initialize_sk_agent()
    
    # Build skills dynamically from discovered tools
    skills = []
    for tool_name, tool_info in agent.available_tools.items():
        skills.append({
            "name": tool_name,
            "description": tool_info.get("description", f"MCP tool: {tool_name}"),
            "parameters": tool_info.get("inputSchema", {}).get("properties", {})
        })
    
    # Add general response capability
    skills.append({
        "name": "general_conversation",
        "description": "General conversational AI powered by Semantic Kernel with tool access"
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
            "mcp_tool_urls": agent.mcp_tool_urls,
            "agent_id": agent.agent_id,
            "status": agent.status,
            "llm_model": agent.model,
            "a2a_powered": True,
            "personality": {
                "style": getattr(agent.config, 'style', 'helpful and friendly') if agent.config else "helpful and friendly",
                "tone": getattr(agent.config, 'tone', 'professional') if agent.config else "professional",
                "expertise": getattr(agent.config, 'expertise', 'general assistance') if agent.config else "general assistance"
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
            
        elif method == "tools/add":
            tool_url = params.get("url")
            if not tool_url:
                return JSONResponse({
                    "jsonrpc": "2.0",
                    "id": request_id,
                    "error": {
                        "code": -32602,
                        "message": "Invalid params - url required"
                    }
                })
            
            # Ensure SK agent is initialized
            if not agent.sk_agent:
                await agent.initialize_sk_agent()
                
            success = await agent.sk_agent.add_tool(tool_url)
            
            # Update the agent's available_tools cache to refresh agent card
            if success:
                await agent.discover_mcp_tools()
                logger.info(f"Agent card updated after adding tool: {tool_url}")
            
            return JSONResponse({
                "jsonrpc": "2.0",
                "id": request_id,
                "result": {
                    "success": success,
                    "message": f"Tool {'added' if success else 'already exists or failed to add'}: {tool_url}",
                    "current_tools": list(agent.available_tools.keys()) if success else None
                }
            })
            
        elif method == "tools/remove":
            tool_url = params.get("url")
            if not tool_url:
                return JSONResponse({
                    "jsonrpc": "2.0",
                    "id": request_id,
                    "error": {
                        "code": -32602,
                        "message": "Invalid params - url required"
                    }
                })
            
            # Ensure SK agent is initialized
            if not agent.sk_agent:
                await agent.initialize_sk_agent()
                
            success = await agent.sk_agent.remove_tool(tool_url)
            
            # Update the agent's available_tools cache to refresh agent card
            if success:
                await agent.discover_mcp_tools()
                logger.info(f"Agent card updated after removing tool: {tool_url}")
            
            return JSONResponse({
                "jsonrpc": "2.0",
                "id": request_id,
                "result": {
                    "success": success,
                    "message": f"Tool {'removed' if success else 'not found or failed to remove'}: {tool_url}",
                    "current_tools": list(agent.available_tools.keys()) if success else None
                }
            })
            
        elif method == "tools/list":
            # Ensure SK agent is initialized
            if not agent.sk_agent:
                await agent.initialize_sk_agent()
                
            tool_list = agent.sk_agent.get_tool_list()
            return JSONResponse({
                "jsonrpc": "2.0",
                "id": request_id,
                "result": {
                    "tools": tool_list,
                    "count": len(tool_list)
                }
            })
            
        elif method == "tools/history":
            # Ensure SK agent is initialized
            if not agent.sk_agent:
                await agent.initialize_sk_agent()
                
            history = agent.sk_agent.get_tool_history()
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
    parser = argparse.ArgumentParser(description="SK-Powered A2A Agent Server with Configuration Support")
    
    # Configuration file option (new)
    parser.add_argument("--config", type=str, 
                      help="Path to YAML configuration file (e.g., agentA.yaml)")
    
    # Legacy individual options (maintained for backward compatibility)
    parser.add_argument("--mcp-url", default=os.getenv("MCP_TOOL_URL", DEFAULT_MCP_TOOL_URL),
                      help="MCP tool server URL (overrides config file)")
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
            config=config,
            mcp_tool_url=args.mcp_url if args.mcp_url != DEFAULT_MCP_TOOL_URL else None,
            port=args.port if args.port != DEFAULT_AGENT_PORT else None
        )
    else:
        agent = A2AAgentServer(
            agent_id=args.agent_id,
            agent_name=args.agent_name,
            mcp_tool_url=args.mcp_url,
            port=args.port
        )
    
    # Display startup information
    print("🤖 SK-Powered A2A Agent Server - Configuration Example")
    print("=" * 60)
    print(f"Configuration: {'YAML Config' if config else 'Command Line'}")
    print(f"Agent ID: {agent.agent_id}")
    print(f"Agent Name: {agent.name}")
    print(f"Description: {agent.description}")
    print(f"MCP Tool URLs: {agent.mcp_tool_urls}")
    print(f"Port: {agent.port}")
    print(f"LLM Model: {agent.model}")
    if config:
        print(f"Personality: {agent.config.style}, {agent.config.tone}")
        print(f"Expertise: {agent.config.expertise}")
    print()
    
    logger.info("🤖 Starting SK-Powered A2A Training Agent")
    logger.info(f"🆔 Agent ID: {agent.agent_id}")
    logger.info(f"🔧 MCP Tool URLs: {agent.mcp_tool_urls}")
    logger.info(f"🧠 LLM Model: {agent.model}")
    logger.info(f"🌐 Server starting on http://{agent.host}:{agent.port}")
    
    # Initialize the SK agent
    import asyncio
    asyncio.run(agent.initialize_agent())
    logger.info("🚀 Agent initialized successfully")
    
    # Run the server
    uvicorn.run(app, host="0.0.0.0", port=agent.port)