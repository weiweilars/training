#!/usr/bin/env python3
"""
Production-ready MCP Deployment with Starlette
Supports streaming HTTP responses, middleware for auth/monitoring
"""

import json
import asyncio
from typing import Dict, Any, Optional, AsyncGenerator
from pathlib import Path
import importlib.util

from starlette.applications import Starlette
from starlette.responses import StreamingResponse, JSONResponse
from starlette.routing import Route
from starlette.requests import Request
from starlette.middleware import Middleware

from middleware.auth import AuthMiddleware
from middleware.monitoring import MonitoringMiddleware
from middleware.cors import CustomCORSMiddleware
from config.settings import Settings
from utils.logger import setup_logger

logger = setup_logger(__name__)


class MCPDeploymentWrapper:
    """Production wrapper for MCP tools with enhanced capabilities"""

    def __init__(self, mcp_tool_module, settings: Settings):
        self.mcp = mcp_tool_module.mcp
        self.settings = settings
        self.module_name = getattr(mcp_tool_module, '__name__', 'unknown')

    async def handle_jsonrpc_stream(self, request_data: Dict[str, Any]) -> AsyncGenerator:
        """Handle JSON-RPC requests with streaming support"""
        try:
            if request_data.get("jsonrpc") != "2.0":
                yield json.dumps(self._error_response(
                    request_data.get("id"),
                    -32600,
                    "Invalid Request: Must be JSON-RPC 2.0"
                )) + "\n"
                return

            method = request_data.get("method")
            params = request_data.get("params", {})
            request_id = request_data.get("id")

            if method == "tools/list":
                result = await self._handle_tools_list(request_id)
                yield json.dumps(result) + "\n"
            elif method == "tools/call":
                async for chunk in self._handle_tool_call_stream(request_id, params):
                    yield chunk
            elif method == "initialize":
                result = await self._handle_initialize(request_id, params)
                yield json.dumps(result) + "\n"
            elif method == "ping":
                yield json.dumps(self._success_response(request_id, {"pong": True})) + "\n"
            else:
                yield json.dumps(self._error_response(
                    request_id,
                    -32601,
                    f"Method not found: {method}"
                )) + "\n"
        except Exception as e:
            logger.error(f"Error in handle_jsonrpc_stream: {e}")
            yield json.dumps(self._error_response(
                request_data.get("id"),
                -32603,
                f"Internal error: {str(e)}"
            )) + "\n"

    async def _handle_tool_call_stream(self, request_id: Any, params: Dict) -> AsyncGenerator:
        """Execute tool calls with streaming support"""
        tool_name = params.get("name")
        arguments = params.get("arguments", {})

        if not tool_name:
            yield json.dumps(self._error_response(
                request_id,
                -32602,
                "Missing tool name"
            )) + "\n"
            return

        try:
            tools_dict = await self.mcp.get_tools()

            if tool_name not in tools_dict:
                yield json.dumps(self._error_response(
                    request_id,
                    -32601,
                    f"Tool not found: {tool_name}"
                )) + "\n"
                return

            tool_obj = tools_dict[tool_name]
            tool_func = tool_obj.fn

            # Check if the tool supports streaming
            if hasattr(tool_func, '__stream__') and tool_func.__stream__:
                # Stream chunks as they come
                async for chunk in tool_func(**arguments):
                    yield json.dumps({
                        "jsonrpc": "2.0",
                        "id": request_id,
                        "result": {
                            "content": [{"type": "text", "text": str(chunk)}],
                            "isPartial": True
                        }
                    }) + "\n"

                # Send final completion marker
                yield json.dumps({
                    "jsonrpc": "2.0",
                    "id": request_id,
                    "result": {
                        "content": [],
                        "isPartial": False,
                        "done": True
                    }
                }) + "\n"
            else:
                # Regular non-streaming execution
                if asyncio.iscoroutinefunction(tool_func):
                    result = await tool_func(**arguments)
                else:
                    result = await asyncio.to_thread(tool_func, **arguments)

                yield json.dumps(self._success_response(request_id, {
                    "content": [{"type": "text", "text": str(result)}]
                })) + "\n"

        except Exception as e:
            logger.error(f"Tool execution failed: {e}")
            yield json.dumps(self._error_response(
                request_id,
                -32603,
                f"Tool execution failed: {str(e)}"
            )) + "\n"

    async def _handle_initialize(self, request_id: Any, params: Dict) -> Dict[str, Any]:
        """Handle initialize request"""
        return self._success_response(request_id, {
            "protocolVersion": "2024-11-05",
            "capabilities": {
                "tools": {},
                "streaming": True  # Indicate streaming support
            },
            "serverInfo": {
                "name": self.mcp.name,
                "version": self.settings.VERSION,
                "environment": self.settings.ENVIRONMENT
            }
        })

    async def _handle_tools_list(self, request_id: Any) -> Dict[str, Any]:
        """List available tools from the MCP instance"""
        try:
            tools_dict = await self.mcp.get_tools()

            tools = []
            for tool_name, tool_obj in tools_dict.items():
                tool_schema = {
                    "name": tool_obj.name,
                    "description": tool_obj.description or "",
                    "inputSchema": tool_obj.parameters,
                    "supportsStreaming": getattr(tool_obj.fn, '__stream__', False)
                }
                tools.append(tool_schema)

            return self._success_response(request_id, {"tools": tools})
        except Exception as e:
            logger.error(f"Failed to get tools: {e}")
            return self._error_response(
                request_id,
                -32603,
                f"Failed to get tools: {str(e)}"
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


# MCP tool loading is now handled by the scanner module


def create_app(mcp_wrapper: MCPDeploymentWrapper, settings: Settings) -> Starlette:
    """Create production Starlette application"""

    async def root_handler(request: Request):
        """Root endpoint with service info"""
        return JSONResponse({
            "service": f"MCP Deployment Server - {mcp_wrapper.mcp.name}",
            "version": settings.VERSION,
            "environment": settings.ENVIRONMENT,
            "protocol": "MCP 2024-11-05",
            "transport": "HTTP with Streaming",
            "endpoints": {
                "/": "Service information",
                "/mcp": "Main MCP endpoint (JSON-RPC with streaming)",
                "/mcp/stream": "Streaming MCP endpoint",
                "/health": "Health check",
                "/metrics": "Prometheus metrics (if enabled)"
            }
        })

    async def mcp_endpoint(request: Request):
        """Main MCP endpoint - handles JSON-RPC requests"""
        try:
            body = await request.json()

            # Check if client wants streaming
            if request.headers.get("X-Stream-Response") == "true":
                async def generate():
                    if isinstance(body, list):
                        for req in body:
                            async for chunk in mcp_wrapper.handle_jsonrpc_stream(req):
                                yield chunk
                    else:
                        async for chunk in mcp_wrapper.handle_jsonrpc_stream(body):
                            yield chunk

                return StreamingResponse(
                    generate(),
                    media_type="application/x-ndjson"
                )
            else:
                # Non-streaming response
                if isinstance(body, list):
                    responses = []
                    for req in body:
                        # Collect all chunks from stream
                        chunks = []
                        async for chunk in mcp_wrapper.handle_jsonrpc_stream(req):
                            chunks.append(json.loads(chunk.strip()))
                        # Return the last non-partial response
                        for chunk in reversed(chunks):
                            if not chunk.get("result", {}).get("isPartial", False):
                                responses.append(chunk)
                                break
                    return JSONResponse(responses)
                else:
                    chunks = []
                    async for chunk in mcp_wrapper.handle_jsonrpc_stream(body):
                        chunks.append(json.loads(chunk.strip()))
                    # Return the last non-partial response
                    for chunk in reversed(chunks):
                        if not chunk.get("result", {}).get("isPartial", False):
                            return JSONResponse(chunk)
                    return JSONResponse(chunks[-1] if chunks else {})

        except json.JSONDecodeError:
            return JSONResponse(
                mcp_wrapper._error_response(None, -32700, "Parse error"),
                status_code=400
            )
        except Exception as e:
            logger.error(f"Error in mcp_endpoint: {e}")
            return JSONResponse(
                mcp_wrapper._error_response(None, -32603, f"Internal error: {str(e)}"),
                status_code=500
            )

    async def stream_endpoint(request: Request):
        """Dedicated streaming endpoint"""
        try:
            body = await request.json()

            async def generate():
                if isinstance(body, list):
                    for req in body:
                        async for chunk in mcp_wrapper.handle_jsonrpc_stream(req):
                            yield chunk
                else:
                    async for chunk in mcp_wrapper.handle_jsonrpc_stream(body):
                        yield chunk

            return StreamingResponse(
                generate(),
                media_type="application/x-ndjson"
            )
        except Exception as e:
            logger.error(f"Error in stream_endpoint: {e}")
            return JSONResponse(
                {"error": str(e)},
                status_code=500
            )

    async def health_check(request: Request):
        """Health check endpoint"""
        return JSONResponse({
            "status": "healthy",
            "tool": mcp_wrapper.mcp.name,
            "version": settings.VERSION,
            "environment": settings.ENVIRONMENT
        })

    async def metrics_endpoint(request: Request):
        """Prometheus metrics endpoint (placeholder)"""
        # This will be implemented by the monitoring middleware
        return JSONResponse({
            "message": "Metrics endpoint - implementation pending"
        })

    # Configure middleware
    middleware = [
        Middleware(CustomCORSMiddleware, settings=settings),
        Middleware(MonitoringMiddleware, settings=settings),
    ]

    # Add auth middleware if enabled
    if settings.AUTH_ENABLED:
        middleware.insert(0, Middleware(AuthMiddleware, settings=settings))

    # Create Starlette application
    app = Starlette(
        routes=[
            Route("/", root_handler),
            Route("/mcp", mcp_endpoint, methods=["POST"]),
            Route("/mcp/stream", stream_endpoint, methods=["POST"]),
            Route("/health", health_check),
            Route("/metrics", metrics_endpoint),
        ],
        middleware=middleware,
        debug=settings.DEBUG
    )

    return app


async def startup():
    """Application startup tasks"""
    logger.info("Starting MCP Deployment Server...")


async def shutdown():
    """Application shutdown tasks"""
    logger.info("Shutting down MCP Deployment Server...")