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
from typing import Dict, Any
import aiohttp
import uuid
from contextlib import AsyncExitStack

try:
    from starlette.applications import Starlette
    from starlette.responses import JSONResponse
    from starlette.requests import Request
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
DEFAULT_MCP_TOOL_URL = "http://localhost:8001/mcp"  # Default weather MCP tool URL

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class ADKAgent:
    """ADK-powered agent using Google's Agent Development Kit"""
    
    def __init__(self, model="gemini-1.5-flash-latest", agent_name="ADK Agent", 
                 agent_description="ADK-powered agent", agent_instruction="You are a helpful assistant."):
        self._model = model
        self._name = agent_name
        self._description = agent_description
        self._instruction = agent_instruction
        self._tool_exit_stack = AsyncExitStack()
        self._tools = []
        self._agent = None
        self._runner = None

    async def create(self, mcp_urls: list = None):
        """Initialize the ADK agent with MCP tools"""
        if mcp_urls is None:
            mcp_urls = []
        
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
            
            # Create the runner
            self._runner = Runner(
                app_name=self._agent.name,
                agent=self._agent,
                artifact_service=InMemoryArtifactService(),
                session_service=InMemorySessionService(),
                memory_service=InMemoryMemoryService(),
            )
            
            logger.info(f"ADK agent '{self._name}' created successfully with {len(mcp_tools)} MCP tools")
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
                events.append(event)

            # Extract response
            if events and events[-1].content and events[-1].content.parts:
                response = "\n".join([p.text for p in events[-1].content.parts if p.text])
                logger.info(f"ADK agent response generated successfully")
                return response
            else:
                logger.warning("No response generated by ADK agent")
                return "I apologize, but I couldn't generate a response."
                
        except Exception as e:
            logger.error(f"Error processing query: {e}")
            return f"Error processing your request: {str(e)}"

    async def close(self):
        """Clean up resources"""
        if self._tool_exit_stack:
            await self._tool_exit_stack.aclose()

class ADKA2AAgent:
    """ADK-powered A2A Agent with dynamic MCP tool discovery"""
    
    def __init__(self, agent_id: str, agent_name: str, mcp_tool_url: str, port: int = 5002):
        self.agent_id = agent_id
        self.name = agent_name
        self.mcp_tool_url = mcp_tool_url
        self.port = port
        self.status = "active"
        self.tasks = {}  # Store tasks by ID
        self.available_tools = {}  # Cache discovered tools
        self.adk_agent = None
        
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
            
            # Initialize with MCP URL if tools were discovered
            mcp_urls = [self.mcp_tool_url] if self.available_tools else []
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
        """Discover available tools from MCP server"""
        try:
            payload = {
                "jsonrpc": "2.0",
                "id": str(uuid.uuid4()),
                "method": "tools/list"
            }
            
            async with aiohttp.ClientSession() as session:
                async with session.post(
                    self.mcp_tool_url,
                    json=payload,
                    headers={
                        "Content-Type": "application/json",
                        "Accept": "application/json, text/event-stream"
                    }
                ) as response:
                    if response.status == 200:
                        response_text = await response.text()
                        
                        # Parse SSE format
                        result = None
                        for line in response_text.split('\n'):
                            if line.startswith('data: '):
                                try:
                                    result = json.loads(line[6:])
                                    break
                                except json.JSONDecodeError:
                                    continue
                        
                        if result and result.get("result", {}).get("tools"):
                            tools_list = result["result"]["tools"]
                            for tool in tools_list:
                                self.available_tools[tool["name"]] = tool
                            logger.info(f"Discovered {len(self.available_tools)} MCP tools: {list(self.available_tools.keys())}")
                            return {"success": True, "tools": self.available_tools}
                        else:
                            return {"success": False, "error": "No tools found in response"}
                    else:
                        error_msg = f"HTTP {response.status}: {await response.text()}"
                        return {"success": False, "error": error_msg}
                        
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
        "description": "ADK-powered A2A training agent with Google Gemini LLM and dynamic MCP tool calling",
        "version": "1.0.0",
        "url": f"http://localhost:{agent.port}",
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
        "metadata": {
            "mcp_tool_url": agent.mcp_tool_url,
            "agent_id": agent.agent_id,
            "status": agent.status,
            "llm_model": "gemini-1.5-flash-latest",
            "adk_powered": True
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
    parser = argparse.ArgumentParser(description="ADK-Powered A2A Agent Server")
    parser.add_argument("--mcp-url", default=os.getenv("MCP_TOOL_URL", DEFAULT_MCP_TOOL_URL),
                      help="MCP tool server URL")
    parser.add_argument("--agent-id", default=os.getenv("AGENT_ID", DEFAULT_AGENT_ID),
                      help="Agent ID")
    parser.add_argument("--agent-name", default=os.getenv("AGENT_NAME", DEFAULT_AGENT_NAME),
                      help="Agent name")
    parser.add_argument("--port", type=int, default=int(os.getenv("AGENT_PORT", DEFAULT_AGENT_PORT)),
                      help="Server port")
    return parser.parse_args()

if __name__ == "__main__":
    args = parse_args()
    
    # Create global agent instance
    agent = ADKA2AAgent(
        agent_id=args.agent_id,
        agent_name=args.agent_name,
        mcp_tool_url=args.mcp_url,
        port=args.port
    )
    
    # Display startup information
    print("🤖 ADK-Powered A2A Agent Server - Training Example")
    print("=" * 60)
    print(f"Agent ID: {agent.agent_id}")
    print(f"Agent Name: {agent.name}")
    print(f"MCP Tool URL: {agent.mcp_tool_url}")
    print(f"Port: {agent.port}")
    print(f"LLM Model: gemini-1.5-flash-latest")
    print()
    
    logger.info("🤖 Starting ADK-Powered A2A Training Agent")
    logger.info(f"🆔 Agent ID: {agent.agent_id}")
    logger.info(f"🔧 MCP Tool URL: {agent.mcp_tool_url}")
    logger.info(f"🧠 LLM Model: gemini-1.5-flash-latest")
    logger.info(f"🌐 Server starting on http://0.0.0.0:{agent.port}")
    
    # Initialize the ADK agent
    import asyncio
    asyncio.run(agent.initialize_adk_agent())
    logger.info("🚀 ADK agent initialized successfully")
    
    # Run the server
    uvicorn.run(app, host="0.0.0.0", port=agent.port)