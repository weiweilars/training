#!/usr/bin/env python3
"""
ADK-Powered A2A Agent Server - Training Example
A2A server with Google ADK LLM integration and dynamic MCP tool calling
"""

import asyncio
import json
import logging
import argparse
import os
from datetime import datetime
from typing import Dict, Any, Optional
import aiohttp
import uuid
import yaml
from contextlib import AsyncExitStack

try:
    from starlette.applications import Starlette
    from starlette.responses import JSONResponse
    import uvicorn
except ImportError:
    print("❌ ERROR: Required dependencies not found!")
    print("📦 Install required dependencies:")
    print("   pip install starlette uvicorn aiohttp")
    exit(1)

# ADK imports
from google.adk.agents.llm_agent import LlmAgent
from google.adk.sessions import InMemorySessionService
from google.adk.memory.in_memory_memory_service import InMemoryMemoryService
from google.adk.artifacts import InMemoryArtifactService
from google.adk.tools.mcp_tool.mcp_toolset import MCPToolset, StreamableHTTPConnectionParams
from google.adk.runners import Runner
from google.genai import types
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Default Configuration
DEFAULT_AGENT_ID = "adk-a2a-training-agent"
DEFAULT_AGENT_NAME = "ADK A2A Training Agent"
DEFAULT_AGENT_PORT = 5002
DEFAULT_MCP_TOOL_URL = "http://localhost:8002/mcp"  # Default weather MCP tool URL

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

async def parse_mcp_response(response) -> dict:
    """Parse HTTP response from MCP server (handles both JSON and SSE)"""
    if response.status != 200:
        response_text = await response.text()
        logger.error(f"MCP server returned status {response.status}: {response_text}")
        return None
    
    try:
        # Check content type
        content_type = response.headers.get('content-type', '').lower()
        
        if 'application/json' in content_type:
            # Direct JSON response
            return await response.json()
        elif 'text/event-stream' in content_type:
            # SSE format - parse as text and look for data lines
            response_text = await response.text()
            logger.debug(f"SSE Response: {response_text[:200]}...")
            
            # Parse SSE format - look for the last data line
            data_lines = []
            for line in response_text.strip().split('\n'):
                if line.startswith('data: '):
                    data_content = line[6:]  # Remove 'data: ' prefix
                    if data_content and data_content != '[DONE]':
                        try:
                            data_lines.append(json.loads(data_content))
                        except json.JSONDecodeError:
                            logger.warning(f"Failed to parse SSE data line: {data_content}")
            
            # Return the last valid data line (usually the complete response)
            if data_lines:
                return data_lines[-1]
            else:
                logger.warning("No valid data lines found in SSE response")
                return None
        else:
            # Try parsing as JSON anyway
            try:
                return await response.json()
            except:
                # Fallback to text parsing for SSE
                response_text = await response.text()
                for line in response_text.split('\n'):
                    if line.startswith('data: '):
                        try:
                            return json.loads(line[6:])
                        except:
                            continue
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
        self.description = self.agent.get("description", "ADK-powered A2A agent")
        
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
        self.model = self.llm.get("model", "gemini-2.5-flash")
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

class ADKAgent:
    """ADK-powered agent using Google's Agent Development Kit"""
    
    def __init__(self, model="gemini-2.5-flash", agent_name="ADK Agent", 
                 agent_description="ADK-powered agent", agent_instruction="You are a helpful assistant."):
        self._model = model
        self._name = agent_name
        self._description = agent_description
        self._instruction = agent_instruction
        self._tool_exit_stack = AsyncExitStack()
        self._tools = []
        self._agent = None
        self._runner = None
        self._tool_history = []  # Track tool changes with timestamps

    async def create(self, mcp_urls: list = None, preserve_services: bool = False):
        """Initialize the ADK agent with MCP tools"""
        if mcp_urls is None:
            mcp_urls = []
        
        # Store existing services if preserving state
        existing_session_service = None
        existing_memory_service = None
        existing_artifact_service = None
        
        if preserve_services and self._runner:
            existing_session_service = self._runner.session_service
            existing_memory_service = self._runner.memory_service
            existing_artifact_service = self._runner.artifact_service
        
        try:
            # Get MCP tools if URLs provided
            mcp_tools = []
            if mcp_urls:
                mcp_tools = await self._get_tools(mcp_urls)
            
            # Create the LLM agent
            self._agent = LlmAgent(
                model=self._model,
                name=self._name,
                description=self._description,
                instruction=self._instruction,
                tools=mcp_tools,
            )
            
            # Create the runner with preserved or new services
            self._runner = Runner(
                app_name=self._agent.name,
                agent=self._agent,
                artifact_service=existing_artifact_service or InMemoryArtifactService(),
                session_service=existing_session_service or InMemorySessionService(),
                memory_service=existing_memory_service or InMemoryMemoryService(),
            )
            
            # Update tools list
            self._tools = mcp_urls
            
            logger.info(f"ADK agent '{self._name}' {'recreated' if preserve_services else 'created'} successfully with {len(mcp_tools)} MCP tools")
            if preserve_services and existing_session_service:
                logger.info("Session state preserved across agent recreation")
            
            return self
            
        except Exception as e:
            logger.error(f"Failed to create ADK agent: {e}")
            raise

    async def _get_tools(self, urls) -> list:
        """Get MCP tools from URLs"""
        logger.info(f"Connecting to MCP servers: {urls}")
        combine_tools = []
        
        try:
            for tool_url in urls:
                logger.info(f"Connecting to MCP server: {tool_url}")
                tools = MCPToolset(
                    connection_params=StreamableHTTPConnectionParams(url=tool_url)
                )
                combine_tools.append(tools)
            
            logger.info(f"Successfully connected to {len(combine_tools)} MCP servers")
            return combine_tools
            
        except Exception as e:
            logger.error(f"Error connecting to MCP servers: {e}")
            raise

    async def invoke(self, query: str, session_id: str, user_id: str = "agent_user") -> str:
        """Process a query using the ADK agent"""
        if not self._runner:
            raise RuntimeError("Agent not initialized. Call create() first.")
        
        try:
            # Get or create session
            session = await self._runner.session_service.get_session(
                app_name=self._agent.name,
                user_id=user_id,
                session_id=session_id
            )

            if session is None:
                session = await self._runner.session_service.create_session(
                    app_name=self._agent.name,
                    user_id=user_id,
                    session_id=session_id,
                    state={}
                )

            # Format the message
            content = types.Content(
                role="user",
                parts=[types.Part.from_text(text=query)]
            )

            logger.info(f"Processing query: '{query}' for session: {session_id}")
            
            # Run the agent
            events = []
            for event in self._runner.run(
                user_id=user_id,
                session_id=session.id,
                new_message=content
            ):
                logger.debug(f"ADK event: {event}")
                events.append(event)

            # Extract response - improved debugging and extraction logic
            logger.info(f"Processing {len(events)} events from ADK agent")
            
            if not events:
                logger.warning("No events received from ADK agent")
                return "I apologize, but I couldn't generate a response - no events received."
            
            # Debug the last event structure
            last_event = events[-1]
            logger.info(f"Last event type: {type(last_event)}")
            logger.info(f"Last event has content: {hasattr(last_event, 'content')}")
            
            # Try different approaches to extract response
            response_parts = []
            
            # Method 1: Check last event content and parts
            if hasattr(last_event, 'content') and last_event.content:
                if hasattr(last_event.content, 'parts') and last_event.content.parts:
                    for part in last_event.content.parts:
                        if hasattr(part, 'text') and part.text:
                            response_parts.append(part.text)
                            logger.info(f"Found text part: {part.text[:100]}...")
            
            # Method 2: Check if events have direct text attribute
            if not response_parts:
                for event in reversed(events):  # Check from last to first
                    if hasattr(event, 'text') and event.text:
                        response_parts.append(event.text)
                        logger.info(f"Found direct text: {event.text[:100]}...")
                        break
            
            # Method 3: Check if events have message content
            if not response_parts:
                for event in reversed(events):
                    if hasattr(event, 'message') and event.message:
                        if hasattr(event.message, 'content'):
                            response_parts.append(str(event.message.content))
                            logger.info(f"Found message content: {str(event.message.content)[:100]}...")
                            break
            
            # Method 4: Try to convert event to string as fallback
            if not response_parts:
                for event in reversed(events):
                    event_str = str(event)
                    if event_str and event_str != "None" and len(event_str.strip()) > 0:
                        response_parts.append(event_str)
                        logger.info(f"Using string representation: {event_str[:100]}...")
                        break
            
            if response_parts:
                response = "\n".join(response_parts)
                logger.info(f"ADK agent response generated successfully: {len(response)} characters")
                return response
            else:
                logger.warning("No response generated by ADK agent - all extraction methods failed")
                logger.warning(f"Event attributes: {[dir(e) for e in events[-3:]]}")  # Debug last few events
                return "I apologize, but I couldn't generate a response - no content found in events."
                
        except Exception as e:
            logger.error(f"Error processing query: {e}")
            return f"Error processing your request: {str(e)}"

    async def add_tool(self, tool_url: str) -> bool:
        """Add a single tool to the agent with session preservation"""
        try:
            if tool_url not in self._tools:
                # Get tool descriptions before adding
                tool_descriptions = await self._get_tool_descriptions(tool_url)
                
                # Add the new tool URL to the list
                new_tools = self._tools + [tool_url]
                
                # Recreate the agent with preserved session state
                preserve_services = self._runner is not None
                await self.create(new_tools, preserve_services=preserve_services)
                
                # Record the change with tool descriptions
                self._tool_history.append({
                    "action": "add",
                    "url": tool_url,
                    "timestamp": datetime.now().isoformat(),
                    "session_preserved": preserve_services,
                    "tool_descriptions": tool_descriptions
                })
                
                logger.info(f"Tool added with {'session preservation' if preserve_services else 'new session'}: {tool_url}")
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
            if tool_url in self._tools:
                # Get tool descriptions before removing
                tool_descriptions = await self._get_tool_descriptions(tool_url)
                
                # Remove the tool URL from the list
                new_tools = [url for url in self._tools if url != tool_url]
                
                # Recreate the agent with preserved session state
                preserve_services = self._runner is not None
                await self.create(new_tools, preserve_services=preserve_services)
                
                # Record the change with tool descriptions
                self._tool_history.append({
                    "action": "remove",
                    "url": tool_url,
                    "timestamp": datetime.now().isoformat(),
                    "session_preserved": preserve_services,
                    "tool_descriptions": tool_descriptions
                })
                
                logger.info(f"Tool removed with {'session preservation' if preserve_services else 'new session'}: {tool_url}")
                return True
            else:
                logger.info(f"Tool not found: {tool_url}")
                return False
                
        except Exception as e:
            logger.error(f"Failed to remove tool {tool_url}: {e}")
            return False

    def get_tool_list(self) -> list:
        """Get current list of tool URLs"""
        return self._tools.copy()

    def get_tool_history(self) -> list:
        """Get history of tool changes"""
        return self._tool_history.copy()

    async def _get_tool_descriptions(self, tool_url: str) -> list:
        """Get tool descriptions from MCP server"""
        try:
            payload = {
                "jsonrpc": "2.0",
                "id": str(uuid.uuid4()),
                "method": "tools/list"
            }
            
            async with aiohttp.ClientSession() as session:
                async with session.post(
                    tool_url,
                    json=payload,
                    headers={
                        "Content-Type": "application/json",
                        "Accept": "application/json, text/event-stream"
                    }
                ) as response:
                    result = await parse_mcp_response(response)
                    
                    if result and result.get("result", {}).get("tools"):
                        tools_list = result["result"]["tools"]
                        descriptions = []
                        for tool in tools_list:
                            descriptions.append({
                                "name": tool["name"],
                                "description": tool.get("description", "No description available")
                            })
                        return descriptions
                    else:
                        return []
                        
        except Exception as e:
            logger.error(f"Failed to get tool descriptions for {tool_url}: {e}")
            return []

    async def close(self):
        """Clean up resources"""
        if self._tool_exit_stack:
            await self._tool_exit_stack.aclose()

class ADKA2AAgent:
    """ADK-powered A2A Agent with dynamic MCP tool discovery"""
    
    def __init__(self, config: Optional[AgentConfig] = None, agent_id: str = None, agent_name: str = None, mcp_tool_url: str = None, port: int = None):
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
            self.description = "ADK-powered A2A agent"
            self.greeting = f"Hello! I'm {self.name}."
            self.instructions = "I'm here to help you with various tasks."
            self.system_prompt = "You are a helpful AI assistant."
            self.model = "gemini-2.5-flash"
            self.port = port or DEFAULT_AGENT_PORT
            self.host = "0.0.0.0"
            self.mcp_tool_urls = [mcp_tool_url or DEFAULT_MCP_TOOL_URL]
            
        self.status = "active"
        self.tasks = {}  # Store tasks by ID
        self.available_tools = {}  # Cache discovered tools
        self.adk_agent = None
        
        # For backward compatibility, expose mcp_tool_url as single URL
        self.mcp_tool_url = self.mcp_tool_urls[0] if self.mcp_tool_urls else DEFAULT_MCP_TOOL_URL
        
    async def initialize_adk_agent(self):
        """Initialize the ADK agent with discovered MCP tools"""
        try:
            # Discover tools first
            await self.discover_mcp_tools()
            
            # Create ADK agent with MCP tools
            # Convert agent name to valid identifier (replace spaces with underscores)
            valid_agent_name = self.name.replace(" ", "_").replace("-", "_")
            self.adk_agent = ADKAgent(
                agent_name=valid_agent_name,
                agent_description="ADK-powered A2A training agent with MCP tool integration",
                agent_instruction="You are a helpful assistant with access to various tools. Use the appropriate tools to answer user questions. When using tools, provide clear and helpful responses based on the tool results."
            )
            
            # Initialize with all MCP URLs if tools were discovered
            mcp_urls = self.mcp_tool_urls if self.available_tools else []
            await self.adk_agent.create(mcp_urls)
            
            logger.info(f"ADK agent initialized with {len(self.available_tools)} discovered tools")
            
        except Exception as e:
            logger.error(f"Failed to initialize ADK agent: {e}")
            # Fallback: create agent without MCP tools
            valid_agent_name = self.name.replace(" ", "_").replace("-", "_")
            self.adk_agent = ADKAgent(
                agent_name=valid_agent_name,
                agent_description="ADK-powered A2A training agent",
                agent_instruction="You are a helpful assistant."
            )
            await self.adk_agent.create([])
        
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
                # Use current ADK agent tool URLs if available, otherwise use static config
                mcp_urls_to_discover = self.adk_agent.get_tool_list() if self.adk_agent else self.mcp_tool_urls
                
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
                mcp_urls_to_discover = self.adk_agent.get_tool_list() if self.adk_agent else self.mcp_tool_urls
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
        """Process a task using ADK agent"""
        
        # Ensure ADK agent is initialized
        if not self.adk_agent:
            await self.initialize_adk_agent()
        
        try:
            # Use ADK agent to process the message
            response = await self.adk_agent.invoke(task_message, session_id)
            return response
            
        except Exception as e:
            logger.error(f"Error processing task with ADK agent: {e}")
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
            # Process the message with ADK agent
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

    async def handle_send_task(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Handle legacy send-task method"""
        task_id = params.get("id", str(uuid.uuid4()))
        session_id = params.get("sessionId")
        message = params.get("message", {})
        
        # Extract text from parts
        text_parts = []
        if "parts" in message:
            for part in message["parts"]:
                if "text" in part:
                    text_parts.append(part["text"])
        
        message_text = " ".join(text_parts)
        
        # Process with ADK agent
        try:
            response = await self.process_task(message_text, session_id or "default")
            
            return {
                "id": task_id,
                "status": {"state": "COMPLETED"},
                "history": [
                    message,
                    {
                        "role": "agent",
                        "parts": [{"text": response}]
                    }
                ]
            }
        except Exception as e:
            return {
                "id": task_id,
                "status": {"state": "FAILED"},
                "error": str(e)
            }

# Create global agent instance
agent = None

# Create Starlette app
app = Starlette()

@app.route("/.well-known/agent-card.json", methods=["GET"])
async def get_agent_card(request):
    """A2A Agent Card discovery endpoint (A2A spec compliant)"""
    
    # Ensure agent is initialized
    if not agent.adk_agent:
        await agent.initialize_adk_agent()
    
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
        "description": "General conversational AI powered by Google Gemini with tool access"
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
            "adk_powered": True,
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
            
        elif method == "send-task":
            # Legacy format
            result = await agent.handle_send_task(params)
            return JSONResponse({
                "jsonrpc": "2.0",
                "id": request_id,
                "result": result
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
            
            # Ensure ADK agent is initialized
            if not agent.adk_agent:
                await agent.initialize_adk_agent()
                
            success = await agent.adk_agent.add_tool(tool_url)
            
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
            
            # Ensure ADK agent is initialized
            if not agent.adk_agent:
                await agent.initialize_adk_agent()
                
            success = await agent.adk_agent.remove_tool(tool_url)
            
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
            # Ensure ADK agent is initialized
            if not agent.adk_agent:
                await agent.initialize_adk_agent()
                
            tool_list = agent.adk_agent.get_tool_list()
            return JSONResponse({
                "jsonrpc": "2.0",
                "id": request_id,
                "result": {
                    "tools": tool_list,
                    "count": len(tool_list)
                }
            })
            
        elif method == "tools/history":
            # Ensure ADK agent is initialized
            if not agent.adk_agent:
                await agent.initialize_adk_agent()
                
            history = agent.adk_agent.get_tool_history()
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
    parser = argparse.ArgumentParser(description="ADK-Powered A2A Agent Server with Configuration Support")
    
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
        agent = ADKA2AAgent(
            config=config,
            mcp_tool_url=args.mcp_url if args.mcp_url != DEFAULT_MCP_TOOL_URL else None,
            port=args.port if args.port != DEFAULT_AGENT_PORT else None
        )
    else:
        agent = ADKA2AAgent(
            agent_id=args.agent_id,
            agent_name=args.agent_name,
            mcp_tool_url=args.mcp_url,
            port=args.port
        )
    
    # Display startup information
    print("🤖 ADK-Powered A2A Agent Server - Configuration Example")
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
    
    logger.info("🤖 Starting ADK-Powered A2A Training Agent")
    logger.info(f"🆔 Agent ID: {agent.agent_id}")
    logger.info(f"🔧 MCP Tool URLs: {agent.mcp_tool_urls}")
    logger.info(f"🧠 LLM Model: {agent.model}")
    logger.info(f"🌐 Server starting on http://{agent.host}:{agent.port}")
    
    # Initialize the ADK agent
    import asyncio
    asyncio.run(agent.initialize_adk_agent())
    logger.info("🚀 ADK agent initialized successfully")
    
    # Run the server
    uvicorn.run(app, host="0.0.0.0", port=agent.port)