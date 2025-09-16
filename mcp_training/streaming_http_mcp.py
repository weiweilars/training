#!/usr/bin/env python3
"""
MCP-Compliant Streaming HTTP Server using Starlette

Implements Model Context Protocol (MCP) with SSE streaming capabilities
following JSON-RPC 2.0 specification.
"""

import json
import asyncio
import logging
import uuid
from typing import AsyncIterator, Dict, Any, Optional, List
from datetime import datetime
from collections import defaultdict

from starlette.applications import Starlette
from starlette.responses import StreamingResponse, JSONResponse, Response
from starlette.routing import Route
from starlette.middleware import Middleware
from starlette.middleware.cors import CORSMiddleware
from starlette.requests import Request
import uvicorn

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class MCPStreamingServer:
    """MCP-compliant server with SSE streaming support"""

    def __init__(self):
        self.sessions: Dict[str, Dict[str, Any]] = {}
        self.active_streams: Dict[str, asyncio.Queue] = {}
        self.tools = self._initialize_tools()

    def _initialize_tools(self) -> List[Dict[str, Any]]:
        """Initialize available MCP tools"""
        return [
            {
                "name": "start_stream",
                "description": "Start a new SSE stream with real-time data",
                "inputSchema": {
                    "type": "object",
                    "properties": {
                        "topic": {"type": "string", "description": "Data topic to stream"},
                        "interval": {"type": "number", "default": 1.0, "description": "Update interval in seconds"},
                        "limit": {"type": "integer", "description": "Maximum number of events to stream"}
                    },
                    "required": ["topic"]
                }
            },
            {
                "name": "send_event",
                "description": "Send a custom event to an active stream",
                "inputSchema": {
                    "type": "object",
                    "properties": {
                        "stream_id": {"type": "string", "description": "ID of the stream"},
                        "data": {"type": "object", "description": "Event data to send"}
                    },
                    "required": ["stream_id", "data"]
                }
            },
            {
                "name": "list_streams",
                "description": "List all active streams",
                "inputSchema": {
                    "type": "object",
                    "properties": {}
                }
            },
            {
                "name": "get_metrics",
                "description": "Get streaming metrics and statistics",
                "inputSchema": {
                    "type": "object",
                    "properties": {
                        "stream_id": {"type": "string", "description": "Optional stream ID for specific metrics"}
                    }
                }
            }
        ]

    def get_or_create_session(self, session_id: Optional[str] = None) -> str:
        """Get existing session or create new one"""
        if not session_id or session_id not in self.sessions:
            session_id = str(uuid.uuid4())
            self.sessions[session_id] = {
                "created": datetime.now().isoformat(),
                "requests": 0,
                "streams": []
            }
        return session_id

    async def handle_jsonrpc(self, request: Dict[str, Any], session_id: str) -> Dict[str, Any]:
        """Handle JSON-RPC 2.0 request"""
        # Validate JSON-RPC request
        if request.get("jsonrpc") != "2.0":
            return self._error_response(
                request.get("id"),
                -32600,
                "Invalid Request: Must be JSON-RPC 2.0"
            )

        method = request.get("method")
        params = request.get("params", {})
        request_id = request.get("id")

        # Update session stats
        if session_id in self.sessions:
            self.sessions[session_id]["requests"] += 1

        # Route method calls
        if method == "initialize":
            return await self._handle_initialize(request_id, params, session_id)
        elif method == "tools/list":
            return await self._handle_tools_list(request_id)
        elif method == "tools/call":
            return await self._handle_tool_call(request_id, params, session_id)
        elif method == "ping":
            return self._success_response(request_id, {"pong": True})
        else:
            return self._error_response(
                request_id,
                -32601,
                f"Method not found: {method}"
            )

    async def _handle_initialize(self, request_id: Any, params: Dict, session_id: str) -> Dict[str, Any]:
        """Handle initialize request"""
        return self._success_response(request_id, {
            "protocolVersion": "2024-11-05",
            "capabilities": {
                "tools": {},
                "streaming": {
                    "sse": True,
                    "websocket": False
                }
            },
            "serverInfo": {
                "name": "streaming-mcp-server",
                "version": "1.0.0"
            },
            "sessionId": session_id
        })

    async def _handle_tools_list(self, request_id: Any) -> Dict[str, Any]:
        """Handle tools/list request"""
        return self._success_response(request_id, {
            "tools": self.tools
        })

    async def _handle_tool_call(self, request_id: Any, params: Dict, session_id: str) -> Dict[str, Any]:
        """Handle tools/call request"""
        tool_name = params.get("name")
        arguments = params.get("arguments", {})

        if tool_name == "start_stream":
            # Create stream and return stream info
            stream_id = f"stream_{uuid.uuid4().hex[:8]}"
            topic = arguments.get("topic", "default")
            interval = arguments.get("interval", 1.0)
            limit = arguments.get("limit")

            # Register stream
            self.active_streams[stream_id] = asyncio.Queue()
            if session_id in self.sessions:
                self.sessions[session_id]["streams"].append(stream_id)

            return self._success_response(request_id, {
                "content": [
                    {
                        "type": "text",
                        "text": f"Stream created: {stream_id}"
                    }
                ],
                "stream": {
                    "id": stream_id,
                    "endpoint": f"/stream/{stream_id}",
                    "topic": topic,
                    "interval": interval,
                    "limit": limit
                }
            })

        elif tool_name == "send_event":
            stream_id = arguments.get("stream_id")
            data = arguments.get("data")

            if stream_id in self.active_streams:
                await self.active_streams[stream_id].put(data)
                return self._success_response(request_id, {
                    "content": [
                        {
                            "type": "text",
                            "text": f"Event sent to stream {stream_id}"
                        }
                    ]
                })
            else:
                return self._error_response(
                    request_id,
                    -32602,
                    f"Stream not found: {stream_id}"
                )

        elif tool_name == "list_streams":
            streams_info = []
            for stream_id in self.active_streams:
                streams_info.append({
                    "id": stream_id,
                    "active": True,
                    "queue_size": self.active_streams[stream_id].qsize()
                })

            return self._success_response(request_id, {
                "content": [
                    {
                        "type": "text",
                        "text": f"Active streams: {len(streams_info)}"
                    }
                ],
                "streams": streams_info
            })

        elif tool_name == "get_metrics":
            stream_id = arguments.get("stream_id")
            metrics = {
                "total_sessions": len(self.sessions),
                "active_streams": len(self.active_streams)
            }

            if stream_id and stream_id in self.active_streams:
                metrics["stream"] = {
                    "id": stream_id,
                    "queue_size": self.active_streams[stream_id].qsize()
                }

            return self._success_response(request_id, {
                "content": [
                    {
                        "type": "text",
                        "text": json.dumps(metrics, indent=2)
                    }
                ]
            })

        else:
            return self._error_response(
                request_id,
                -32601,
                f"Unknown tool: {tool_name}"
            )

    async def generate_sse_stream(self, stream_id: str, interval: float = 1.0, limit: Optional[int] = None) -> AsyncIterator[str]:
        """Generate SSE stream data"""
        if stream_id not in self.active_streams:
            yield f"data: {json.dumps({'error': 'Stream not found'})}\n\n"
            return

        queue = self.active_streams[stream_id]
        count = 0

        try:
            while True:
                # Check for limit
                if limit and count >= limit:
                    yield f"data: {json.dumps({'type': 'complete', 'count': count})}\n\n"
                    break

                # Check for queued events
                try:
                    data = await asyncio.wait_for(queue.get(), timeout=interval)
                    event = {
                        "id": f"evt_{count}",
                        "type": "custom",
                        "timestamp": datetime.now().isoformat(),
                        "data": data
                    }
                except asyncio.TimeoutError:
                    # Generate automatic event
                    event = {
                        "id": f"evt_{count}",
                        "type": "auto",
                        "timestamp": datetime.now().isoformat(),
                        "count": count,
                        "message": f"Auto-generated event #{count}"
                    }

                yield f"data: {json.dumps(event)}\n\n"
                count += 1

        except asyncio.CancelledError:
            yield f"data: {json.dumps({'type': 'cancelled'})}\n\n"
        finally:
            # Cleanup
            if stream_id in self.active_streams:
                del self.active_streams[stream_id]

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


# Initialize server
mcp_server = MCPStreamingServer()


# Route handlers
async def root_handler(request: Request):
    """Root endpoint with service info"""
    return JSONResponse({
        "service": "MCP Streaming HTTP Server",
        "version": "1.0.0",
        "protocol": "MCP 2024-11-05",
        "transport": "HTTP with SSE",
        "endpoints": {
            "/": "Service information",
            "/mcp": "Main MCP endpoint (JSON-RPC)",
            "/stream/{stream_id}": "SSE stream endpoint",
            "/health": "Health check"
        }
    })


async def mcp_endpoint(request: Request):
    """Main MCP endpoint - handles JSON-RPC requests"""
    # Get or create session
    session_id = request.headers.get("Mcp-Session-Id")
    session_id = mcp_server.get_or_create_session(session_id)

    try:
        # Parse JSON-RPC request
        body = await request.json()

        # Handle single request or batch
        if isinstance(body, list):
            # Batch request
            responses = []
            for req in body:
                response = await mcp_server.handle_jsonrpc(req, session_id)
                if response:  # Don't include responses for notifications
                    responses.append(response)

            return JSONResponse(
                responses,
                headers={"Mcp-Session-Id": session_id}
            )
        else:
            # Single request
            response = await mcp_server.handle_jsonrpc(body, session_id)

            # Check if streaming is requested
            if "stream" in response.get("result", {}):
                # Return stream info, client will connect to stream endpoint
                return JSONResponse(
                    response,
                    headers={"Mcp-Session-Id": session_id}
                )

            return JSONResponse(
                response,
                headers={"Mcp-Session-Id": session_id}
            )

    except json.JSONDecodeError:
        return JSONResponse(
            mcp_server._error_response(None, -32700, "Parse error"),
            status_code=400
        )
    except Exception as e:
        logger.error(f"Error handling request: {e}")
        return JSONResponse(
            mcp_server._error_response(None, -32603, f"Internal error: {str(e)}"),
            status_code=500
        )


async def mcp_delete(request: Request):
    """Handle session cleanup via DELETE"""
    session_id = request.headers.get("Mcp-Session-Id")

    if session_id and session_id in mcp_server.sessions:
        # Clean up session and associated streams
        session = mcp_server.sessions[session_id]
        for stream_id in session.get("streams", []):
            if stream_id in mcp_server.active_streams:
                del mcp_server.active_streams[stream_id]

        del mcp_server.sessions[session_id]

        return Response(status_code=204)  # No Content

    return JSONResponse(
        {"error": "Session not found"},
        status_code=404
    )


async def stream_endpoint(request: Request):
    """SSE stream endpoint"""
    stream_id = request.path_params.get("stream_id")

    if not stream_id or stream_id not in mcp_server.active_streams:
        return JSONResponse(
            {"error": "Stream not found"},
            status_code=404
        )

    # Get stream parameters from query
    interval = float(request.query_params.get("interval", "1.0"))
    limit = request.query_params.get("limit")
    if limit:
        limit = int(limit)

    # Return SSE stream
    return StreamingResponse(
        mcp_server.generate_sse_stream(stream_id, interval, limit),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
            "X-Accel-Buffering": "no"
        }
    )


async def health_check(request: Request):
    """Health check endpoint"""
    return JSONResponse({
        "status": "healthy",
        "timestamp": datetime.now().isoformat(),
        "sessions": len(mcp_server.sessions),
        "active_streams": len(mcp_server.active_streams)
    })


# Create Starlette application
app = Starlette(
    routes=[
        Route("/", root_handler),
        Route("/mcp", mcp_endpoint, methods=["POST"]),
        Route("/mcp", mcp_delete, methods=["DELETE"]),
        Route("/stream/{stream_id}", stream_endpoint),
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
    ],
    on_startup=[lambda: logger.info("MCP Streaming Server started")],
    on_shutdown=[lambda: logger.info("MCP Streaming Server shutting down")]
)


if __name__ == "__main__":
    # Run the server
    uvicorn.run(
        app,
        host="0.0.0.0",
        port=8001,
        log_level="info",
        access_log=True
    )