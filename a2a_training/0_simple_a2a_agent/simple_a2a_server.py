#!/usr/bin/env python3
"""
Simple A2A Agent Server - Training Example
A2A server with hardcoded HTTP MCP tool calling
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

# Default Configuration
DEFAULT_AGENT_ID = "simple-a2a-training-agent"
DEFAULT_AGENT_NAME = "Simple A2A Training Agent"
DEFAULT_AGENT_PORT = 5001
DEFAULT_MCP_TOOL_URL = "http://localhost:8001/mcp"  # Default weather MCP tool URL

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class SimpleA2AAgent:
    """Simple A2A Agent with HTTP MCP tool calling"""
    
    def __init__(self, agent_id: str, agent_name: str, mcp_tool_url: str, port: int = 5001):
        self.agent_id = agent_id
        self.name = agent_name
        self.mcp_tool_url = mcp_tool_url
        self.port = port
        self.status = "active"
        self.tasks = {}  # Store tasks by ID
        self.available_tools = {}  # Cache discovered tools
        
    async def call_mcp_tool(self, tool_name: str, arguments: Dict[str, Any]) -> Dict[str, Any]:
        """Call hardcoded HTTP MCP tool"""
        try:
            payload = {
                "jsonrpc": "2.0",
                "id": str(uuid.uuid4()),
                "method": f"tools/call",
                "params": {
                    "name": tool_name,
                    "arguments": arguments
                }
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
                        # Handle Server-Sent Events response
                        response_text = await response.text()
                        
                        # Parse SSE format - look for data: line with JSON
                        result = None
                        for line in response_text.split('\n'):
                            if line.startswith('data: '):
                                try:
                                    result = json.loads(line[6:])  # Remove 'data: ' prefix
                                    break
                                except json.JSONDecodeError:
                                    continue
                        
                        if result is None:
                            result = {"error": "Could not parse SSE response", "raw": response_text}
                        
                        return {"success": True, "result": result}
                    else:
                        error_msg = f"HTTP {response.status}: {await response.text()}"
                        return {"success": False, "error": error_msg}
                        
        except Exception as e:
            error_msg = str(e)
            return {"success": False, "error": error_msg}
    
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
                        # Handle Server-Sent Events response
                        response_text = await response.text()
                        
                        # Parse SSE format - look for data: line with JSON
                        result = None
                        for line in response_text.split('\n'):
                            if line.startswith('data: '):
                                try:
                                    result = json.loads(line[6:])  # Remove 'data: ' prefix
                                    break
                                except json.JSONDecodeError:
                                    continue
                        
                        if result and result.get("result", {}).get("tools"):
                            tools_list = result["result"]["tools"]
                            # Convert to dict for easy lookup
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
        """Process a task and potentially call MCP tools"""
        
        # Ensure tools are discovered
        if not self.available_tools:
            await self.discover_mcp_tools()
        
        task_lower = task_message.lower()
        
        # Try to match task with available MCP tools
        for tool_name, tool_info in self.available_tools.items():
            tool_description = tool_info.get("description", "").lower()
            tool_name_lower = tool_name.lower()
            
            # Simple matching logic based on keywords
            if tool_name_lower in task_lower or any(keyword in task_lower for keyword in tool_description.split()[:3]):
                # Try to extract arguments based on the tool
                arguments = self._extract_tool_arguments(tool_name, tool_info, task_message)
                
                tool_result = await self.call_mcp_tool(tool_name, arguments)
                
                if tool_result["success"]:
                    result_data = tool_result.get("result", {})
                    if isinstance(result_data, dict) and "result" in result_data:
                        result_content = result_data["result"]
                        if isinstance(result_content, str):
                            return f"Using {tool_name}: {result_content}"
                        else:
                            return f"Using {tool_name}: {json.dumps(result_content, indent=2)}"
                    else:
                        return f"Using {tool_name}: {json.dumps(result_data, indent=2)}"
                else:
                    return f"Failed to use {tool_name}: {tool_result['error']}"
        
        # If no tool matches, return a general response
        return f"I received your message: '{task_message}'. I have access to these MCP tools: {list(self.available_tools.keys())}. Try asking about weather, time, or calculations!"
    
    def _extract_tool_arguments(self, tool_name: str, tool_info: Dict[str, Any], message: str) -> Dict[str, Any]:
        """Extract arguments for a tool based on the message content"""
        arguments = {}
        message_lower = message.lower()
        
        # Get expected parameters from tool schema
        properties = tool_info.get("inputSchema", {}).get("properties", {})
        
        # Simple argument extraction based on common patterns
        if tool_name == "get_current_weather":
            # Extract city from message
            city = "London"  # Default
            if "in " in message_lower:
                parts = message_lower.split("in ")
                if len(parts) > 1:
                    city = parts[-1].strip().title()
            elif "for " in message_lower:
                parts = message_lower.split("for ")
                if len(parts) > 1:
                    city = parts[-1].strip().title()
            arguments["city"] = city
            
        elif tool_name == "get_weather_forecast":
            # Extract city and days
            city = "London"  # Default
            days = 3  # Default
            if "in " in message_lower:
                parts = message_lower.split("in ")
                if len(parts) > 1:
                    city = parts[-1].strip().title()
            
            # Look for number of days
            import re
            day_match = re.search(r'(\d+)\s*day', message_lower)
            if day_match:
                days = int(day_match.group(1))
            
            arguments["city"] = city
            arguments["days"] = days
            
        elif tool_name == "convert_temperature":
            # Extract temperature value and units
            import re
            temp_match = re.search(r'(\d+(?:\.\d+)?)', message)
            if temp_match:
                arguments["temperature"] = float(temp_match.group(1))
            
            # Extract units
            if "celsius" in message_lower or "°c" in message_lower:
                arguments["from_unit"] = "celsius"
            elif "fahrenheit" in message_lower or "°f" in message_lower:
                arguments["from_unit"] = "fahrenheit"
            elif "kelvin" in message_lower:
                arguments["from_unit"] = "kelvin"
            else:
                arguments["from_unit"] = "celsius"
            
            if "to fahrenheit" in message_lower:
                arguments["to_unit"] = "fahrenheit"
            elif "to celsius" in message_lower:
                arguments["to_unit"] = "celsius"
            elif "to kelvin" in message_lower:
                arguments["to_unit"] = "kelvin"
            else:
                arguments["to_unit"] = "fahrenheit" if arguments.get("from_unit") == "celsius" else "celsius"
        
        # For other tools, try to match parameter names with message content
        else:
            for param_name, param_info in properties.items():
                if param_name in message_lower:
                    # Simple extraction - could be improved
                    arguments[param_name] = message
        
        return arguments
    
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
            "result": None
        }
        self.tasks[task_id] = task
        return task
    
    def get_task(self, task_id: str) -> Dict[str, Any]:
        """Get task by ID"""
        return self.tasks.get(task_id)
    
    def update_task_status(self, task_id: str, status: str, result: str = None):
        """Update task status and result"""
        if task_id in self.tasks:
            self.tasks[task_id]["status"] = status
            self.tasks[task_id]["updated_at"] = datetime.now().isoformat()
            if result:
                self.tasks[task_id]["result"] = result
                self.tasks[task_id]["messages"].append({
                    "role": "agent",
                    "content": result,
                    "timestamp": datetime.now().isoformat()
                })
    
    def cancel_task(self, task_id: str) -> bool:
        """Cancel a task"""
        if task_id in self.tasks and self.tasks[task_id]["status"] in ["submitted", "working"]:
            self.tasks[task_id]["status"] = "cancelled"
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
            # Process the message
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
                    "message": str(e)
                }
            }

def parse_args():
    """Parse command line arguments"""
    parser = argparse.ArgumentParser(description="Simple A2A Agent Server")
    parser.add_argument("--mcp-url", type=str, 
                       default=os.getenv("MCP_TOOL_URL", DEFAULT_MCP_TOOL_URL),
                       help="MCP tool URL (default: %(default)s)")
    parser.add_argument("--agent-id", type=str,
                       default=os.getenv("AGENT_ID", DEFAULT_AGENT_ID),
                       help="Agent ID (default: %(default)s)")
    parser.add_argument("--agent-name", type=str,
                       default=os.getenv("AGENT_NAME", DEFAULT_AGENT_NAME),
                       help="Agent name (default: %(default)s)")
    parser.add_argument("--port", type=int,
                       default=int(os.getenv("AGENT_PORT", DEFAULT_AGENT_PORT)),
                       help="Server port (default: %(default)s)")
    return parser.parse_args()

# Global agent instance (will be initialized in main)
agent = None

# Create Starlette app
app = Starlette()

@app.route("/.well-known/agent-card.json", methods=["GET"])
async def get_agent_card(request):
    """A2A Agent Card discovery endpoint (A2A spec compliant)"""
    
    # Ensure tools are discovered
    if not agent.available_tools:
        await agent.discover_mcp_tools()
    
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
        "name": "general_response",
        "description": "General conversational responses and text processing"
    })
    
    agent_card = {
        "name": agent.name,
        "description": "Simple A2A training agent with dynamic HTTP MCP tool calling",
        "version": "1.0.0",
        "url": f"http://localhost:{agent.port if hasattr(agent, 'port') else 5001}",
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
            "status": agent.status
        }
    }
    return JSONResponse(agent_card)



async def handle_jsonrpc_method(method: str, params: Dict[str, Any], request_id: str) -> Dict[str, Any]:
    """Handle JSON-RPC method calls for A2A protocol"""
    try:
        if method == "message/send":
            result = await agent.handle_message_send(params)
            return {
                "jsonrpc": "2.0",
                "id": request_id,
                "result": result
            }
        
        elif method == "tasks/get":
            task_id = params.get("taskId")
            if not task_id:
                return {
                    "jsonrpc": "2.0",
                    "id": request_id,
                    "error": {
                        "code": -32602,
                        "message": "taskId parameter required"
                    }
                }
            
            task = agent.get_task(task_id)
            if not task:
                return {
                    "jsonrpc": "2.0",
                    "id": request_id,
                    "error": {
                        "code": -32604,
                        "message": "Task not found"
                    }
                }
            
            return {
                "jsonrpc": "2.0",
                "id": request_id,
                "result": task
            }
        
        elif method == "tasks/cancel":
            task_id = params.get("taskId")
            if not task_id:
                return {
                    "jsonrpc": "2.0",
                    "id": request_id,
                    "error": {
                        "code": -32602,
                        "message": "taskId parameter required"
                    }
                }
            
            success = agent.cancel_task(task_id)
            return {
                "jsonrpc": "2.0",
                "id": request_id,
                "result": {
                    "taskId": task_id,
                    "cancelled": success
                }
            }
        
        # Legacy support for old send-task method
        elif method == "send-task":
            # Convert old format to new message/send format
            message_params = {
                "message": params.get("message", {}),
                "taskId": params.get("id"),
                "sessionId": params.get("sessionId")
            }
            result = await agent.handle_message_send(message_params)
            
            # Convert response to legacy format
            return {
                "jsonrpc": "2.0",
                "id": request_id,
                "result": {
                    "id": result.get("taskId"),
                    "status": {"state": result.get("status", "").upper()},
                    "history": [
                        {
                            "role": "user",
                            "parts": [{"text": message_params["message"].get("parts", [{}])[0].get("text", "")}]
                        },
                        {
                            "role": "agent",
                            "parts": [{"text": result.get("result", {}).get("message", {}).get("content", "")}]
                        }
                    ]
                }
            }
        
        else:
            return {
                "jsonrpc": "2.0",
                "id": request_id,
                "error": {
                    "code": -32601,
                    "message": f"Method '{method}' not found. Supported methods: message/send, tasks/get, tasks/cancel"
                }
            }
    
    except Exception as e:
        logger.error(f"Error handling method {method}: {e}")
        return {
            "jsonrpc": "2.0",
            "id": request_id,
            "error": {
                "code": -32603,
                "message": f"Internal error: {str(e)}"
            }
        }

@app.route("/", methods=["POST"])
async def handle_jsonrpc_request(request):
    """Handle JSON-RPC requests for A2A protocol"""
    try:
        body = await request.json()
        logger.info(f"Received JSON-RPC request: {json.dumps(body, indent=2)}")
        
        # Validate JSON-RPC format
        if not isinstance(body, dict) or body.get("jsonrpc") != "2.0":
            return JSONResponse({
                "jsonrpc": "2.0",
                "id": body.get("id"),
                "error": {
                    "code": -32600,
                    "message": "Invalid JSON-RPC request"
                }
            }, status_code=400)
        
        method = body.get("method")
        params = body.get("params", {})
        request_id = body.get("id")
        
        if not method:
            return JSONResponse({
                "jsonrpc": "2.0",
                "id": request_id,
                "error": {
                    "code": -32600,
                    "message": "Method field required"
                }
            }, status_code=400)
        
        # Handle the method
        response = await handle_jsonrpc_method(method, params, request_id)
        
        # Return appropriate status code based on response
        status_code = 200
        if "error" in response:
            status_code = 400 if response["error"]["code"] in [-32600, -32602, -32604] else 500
        
        return JSONResponse(response, status_code=status_code)
        
    except json.JSONDecodeError:
        return JSONResponse({
            "jsonrpc": "2.0",
            "id": None,
            "error": {
                "code": -32700,
                "message": "Parse error: Invalid JSON"
            }
        }, status_code=400)
        
    except Exception as e:
        logger.error(f"Error processing JSON-RPC request: {e}")
        return JSONResponse({
            "jsonrpc": "2.0", 
            "id": None,
            "error": {
                "code": -32603,
                "message": f"Internal error: {str(e)}"
            }
        }, status_code=500)


async def start_server(agent_instance, port):
    """Start the A2A server"""
    global agent
    agent = agent_instance
    
    logger.info(f"🤖 Starting {agent.name}")
    logger.info(f"🆔 Agent ID: {agent.agent_id}")
    logger.info(f"🔧 MCP Tool URL: {agent.mcp_tool_url}")
    logger.info(f"🌐 Server starting on http://0.0.0.0:{port}")
    
    config = uvicorn.Config(
        app,
        host="0.0.0.0",
        port=port,
        log_level="info"
    )
    server = uvicorn.Server(config)
    await server.serve()

def main():
    """Main function"""
    args = parse_args()
    
    print("🚀 Simple A2A Agent Server - Training Example")
    print("=" * 50)
    print(f"Agent ID: {args.agent_id}")
    print(f"Agent Name: {args.agent_name}")
    print(f"MCP Tool URL: {args.mcp_url}")
    print(f"Port: {args.port}")
    print()
    
    # Create agent instance with parsed arguments
    agent_instance = SimpleA2AAgent(args.agent_id, args.agent_name, args.mcp_url, args.port)
    
    # Start server
    asyncio.run(start_server(agent_instance, args.port))

if __name__ == "__main__":
    main()