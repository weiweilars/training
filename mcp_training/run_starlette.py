#!/usr/bin/env python3
"""
Universal Starlette Runner for MCP Tools
Deploys any MCP tool as a Starlette HTTP server with streaming capabilities
"""

import sys
import os
import argparse
import importlib.util
import json
import asyncio
from pathlib import Path
from typing import Dict, Any, Optional

from starlette.applications import Starlette
from starlette.responses import StreamingResponse, JSONResponse, Response
from starlette.routing import Route
from starlette.middleware import Middleware
from starlette.middleware.cors import CORSMiddleware
from starlette.requests import Request
import uvicorn

class MCPStarletteWrapper:
    """Wrapper to run any FastMCP tool via Starlette"""

    def __init__(self, mcp_tool_module):
        self.mcp = mcp_tool_module.mcp
        self.module_name = getattr(mcp_tool_module, '__name__', 'unknown')

    async def handle_jsonrpc(self, request_data: Dict[str, Any]) -> Dict[str, Any]:
        """Handle JSON-RPC 2.0 requests"""
        if request_data.get("jsonrpc") != "2.0":
            return self._error_response(
                request_data.get("id"),
                -32600,
                "Invalid Request: Must be JSON-RPC 2.0"
            )

        method = request_data.get("method")
        params = request_data.get("params", {})
        request_id = request_data.get("id")

        if method == "tools/list":
            return await self._handle_tools_list(request_id)
        elif method == "tools/call":
            return await self._handle_tool_call(request_id, params)
        elif method == "initialize":
            return await self._handle_initialize(request_id, params)
        elif method == "ping":
            return self._success_response(request_id, {"pong": True})
        else:
            return self._error_response(
                request_id,
                -32601,
                f"Method not found: {method}"
            )

    async def _handle_initialize(self, request_id: Any, params: Dict) -> Dict[str, Any]:
        """Handle initialize request"""
        return self._success_response(request_id, {
            "protocolVersion": "2024-11-05",
            "capabilities": {
                "tools": {}
            },
            "serverInfo": {
                "name": self.mcp.name,
                "version": "1.0.0"
            }
        })

    async def _handle_tools_list(self, request_id: Any) -> Dict[str, Any]:
        """List available tools from the MCP instance"""
        try:
            # Use FastMCP's get_tools method
            tools_dict = await self.mcp.get_tools()

            # Convert FunctionTool objects to MCP tool schema
            tools = []
            for tool_name, tool_obj in tools_dict.items():
                tool_schema = {
                    "name": tool_obj.name,
                    "description": tool_obj.description or "",
                    "inputSchema": tool_obj.parameters  # Use the parameters directly
                }
                tools.append(tool_schema)

            return self._success_response(request_id, {"tools": tools})
        except Exception as e:
            return self._error_response(
                request_id,
                -32603,
                f"Failed to get tools: {str(e)}"
            )

    async def _handle_tool_call(self, request_id: Any, params: Dict) -> Dict[str, Any]:
        """Execute a tool call"""
        tool_name = params.get("name")
        arguments = params.get("arguments", {})

        if not tool_name:
            return self._error_response(
                request_id,
                -32602,
                "Missing tool name"
            )

        try:
            # Get tools dict and find the specific tool
            tools_dict = await self.mcp.get_tools()

            if tool_name not in tools_dict:
                return self._error_response(
                    request_id,
                    -32601,
                    f"Tool not found: {tool_name}"
                )

            tool_obj = tools_dict[tool_name]
            tool_func = tool_obj.fn

            # Call the tool function
            if asyncio.iscoroutinefunction(tool_func):
                result = await tool_func(**arguments)
            else:
                result = tool_func(**arguments)

            return self._success_response(request_id, {
                "content": [
                    {
                        "type": "text",
                        "text": str(result)
                    }
                ]
            })

        except Exception as e:
            return self._error_response(
                request_id,
                -32603,
                f"Tool execution failed: {str(e)}"
            )

    def _success_response(self, request_id: Any, result: Any) -> Dict[str, Any]:
        """Create JSON-RPC success response"""
        return {
            "jsonrpc": "2.0",
            "id": request_id,
            "result": result
        }

    def _error_response(self, request_id: Any, code: int, message: str, data: Any = None) -> Dict[str, Any]:
        """Create JSON-RPC error response"""
        error = {
            "code": code,
            "message": message
        }
        if data is not None:
            error["data"] = data

        return {
            "jsonrpc": "2.0",
            "id": request_id,
            "error": error
        }

def load_mcp_tool(tool_path: Path):
    """Load MCP tool module from file path"""
    spec = importlib.util.spec_from_file_location("mcp_tool", tool_path)
    if spec is None or spec.loader is None:
        raise ImportError(f"Could not load module from {tool_path}")

    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)

    if not hasattr(module, 'mcp'):
        raise AttributeError(f"Module {tool_path} does not have 'mcp' attribute")

    return module

def create_app(mcp_wrapper: MCPStarletteWrapper) -> Starlette:
    """Create Starlette application with MCP wrapper"""

    async def root_handler(request: Request):
        """Root endpoint with service info"""
        return JSONResponse({
            "service": f"Starlette MCP Server - {mcp_wrapper.mcp.name}",
            "version": "1.0.0",
            "protocol": "MCP 2024-11-05",
            "transport": "HTTP",
            "endpoints": {
                "/": "Service information",
                "/mcp": "Main MCP endpoint (JSON-RPC)",
                "/health": "Health check"
            }
        })

    async def mcp_endpoint(request: Request):
        """Main MCP endpoint - handles JSON-RPC requests"""
        try:
            body = await request.json()

            # Handle single request or batch
            if isinstance(body, list):
                # Batch request
                responses = []
                for req in body:
                    response = await mcp_wrapper.handle_jsonrpc(req)
                    if response:  # Don't include responses for notifications
                        responses.append(response)
                return JSONResponse(responses)
            else:
                # Single request
                response = await mcp_wrapper.handle_jsonrpc(body)
                return JSONResponse(response)

        except json.JSONDecodeError:
            return JSONResponse(
                mcp_wrapper._error_response(None, -32700, "Parse error"),
                status_code=400
            )
        except Exception as e:
            return JSONResponse(
                mcp_wrapper._error_response(None, -32603, f"Internal error: {str(e)}"),
                status_code=500
            )

    async def health_check(request: Request):
        """Health check endpoint"""
        return JSONResponse({
            "status": "healthy",
            "tool": mcp_wrapper.mcp.name,
            "timestamp": "2024-01-01T00:00:00Z"
        })

    # Create Starlette application
    app = Starlette(
        routes=[
            Route("/", root_handler),
            Route("/mcp", mcp_endpoint, methods=["POST"]),
            Route("/health", health_check),
        ],
        middleware=[
            Middleware(
                CORSMiddleware,
                allow_origins=["*"],
                allow_credentials=True,
                allow_methods=["*"],
                allow_headers=["*"],
            )
        ]
    )

    return app

def main():
    """Main entry point"""
    parser = argparse.ArgumentParser(
        description="Run MCP tools via Starlette HTTP server",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python run_starlette.py simple_weather_tool.py
  python run_starlette.py simple_calculator_tool.py --port 8002
  python run_starlette.py custom_tool.py --host 0.0.0.0 --port 9000
        """
    )

    parser.add_argument(
        "tool_file",
        help="Path to the MCP tool Python file"
    )

    parser.add_argument(
        "--port", "-p",
        type=int,
        default=8000,
        help="Port to run the HTTP server on (default: 8000)"
    )

    parser.add_argument(
        "--host",
        default="localhost",
        help="Host to bind the server to (default: localhost)"
    )

    parser.add_argument(
        "--log-level",
        default="info",
        choices=["debug", "info", "warning", "error"],
        help="Logging level (default: info)"
    )

    args = parser.parse_args()

    # Resolve tool file path
    tool_path = Path(args.tool_file)
    if not tool_path.exists():
        # Try relative to script directory
        script_dir = Path(__file__).parent
        tool_path = script_dir / args.tool_file

        if not tool_path.exists():
            print(f"Error: Tool file not found: {args.tool_file}")
            return 1

    try:
        # Load the MCP tool
        print(f"Loading MCP tool: {tool_path}")
        mcp_module = load_mcp_tool(tool_path)

        # Create wrapper
        mcp_wrapper = MCPStarletteWrapper(mcp_module)

        # Create Starlette app
        app = create_app(mcp_wrapper)

        print(f"Starting Starlette server for: {mcp_wrapper.mcp.name}")
        print(f"Server URL: http://{args.host}:{args.port}")
        print("Press Ctrl+C to stop the server")
        print("-" * 50)

        # Run the server
        uvicorn.run(
            app,
            host=args.host,
            port=args.port,
            log_level=args.log_level,
            access_log=True
        )

    except ImportError as e:
        print(f"Error importing tool module: {e}")
        print("Make sure the tool file has a valid 'mcp' attribute")
        return 1
    except Exception as e:
        print(f"Error running server: {e}")
        return 1

    return 0

if __name__ == "__main__":
    exit_code = main()
    if exit_code:
        sys.exit(exit_code)