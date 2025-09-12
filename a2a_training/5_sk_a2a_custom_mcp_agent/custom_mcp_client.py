#!/usr/bin/env python3
"""
Custom MCP Client for Google ADK
Bypasses Python MCP SDK issues by implementing direct HTTP calls
"""

import asyncio
import httpx
import json
import uuid
from typing import Dict, Any, List, Optional


class CustomMCPClient:
    """Custom MCP client that works with Google ADK without SDK issues"""
    
    def __init__(self, server_url: str):
        self.server_url = server_url
        self.session_id = str(uuid.uuid4())
        self.initialized = False
        
    async def _parse_response(self, response) -> Optional[Dict[str, Any]]:
        """Parse HTTP response from MCP server (handles both JSON and SSE)"""
        if response.status_code != 200:
            print(f"MCP server returned status {response.status_code}")
            return None
        
        try:
            # Check content type
            content_type = response.headers.get('content-type', '').lower()
            
            if 'application/json' in content_type:
                # Direct JSON response
                return response.json()
            else:
                # SSE format - parse as text
                response_text = response.text
                # Look for SSE data line
                for line in response_text.split('\n'):
                    if line.startswith('data: '):
                        return json.loads(line[6:])  # Remove 'data: ' prefix
                return None
                
        except Exception as e:
            print(f"Failed to parse MCP response: {e}")
            return None
        
    async def initialize(self) -> Dict[str, Any]:
        """Initialize MCP session"""
        payload = {
            "jsonrpc": "2.0",
            "method": "initialize",
            "params": {
                "protocolVersion": "2025-06-18",
                "capabilities": {"tools": {}}
            },
            "id": str(uuid.uuid4())
        }
        
        headers = {
            "Content-Type": "application/json",
            "Accept": "application/json, text/event-stream"
        }
        
        async with httpx.AsyncClient() as client:
            response = await client.post(self.server_url, json=payload, headers=headers)
            result = await self._parse_response(response)
            self.initialized = True
            return result
    
    async def list_tools(self) -> List[Dict[str, Any]]:
        """Get available tools from MCP server"""
        if not self.initialized:
            await self.initialize()
            
        payload = {
            "jsonrpc": "2.0",
            "method": "tools/list",
            "params": {},
            "id": str(uuid.uuid4())
        }
        
        headers = {
            "Content-Type": "application/json",
            "Accept": "application/json, text/event-stream"
        }
        
        async with httpx.AsyncClient() as client:
            response = await client.post(self.server_url, json=payload, headers=headers)
            result = await self._parse_response(response)
            
            if result and "result" in result and "tools" in result["result"]:
                return result["result"]["tools"]
            return []
    
    async def call_tool(self, tool_name: str, arguments: Dict[str, Any] = None) -> Dict[str, Any]:
        """Call a specific MCP tool"""
        if arguments is None:
            arguments = {}
            
        payload = {
            "jsonrpc": "2.0",
            "method": "tools/call",
            "params": {
                "name": tool_name,
                "arguments": arguments
            },
            "id": str(uuid.uuid4())
        }
        
        headers = {
            "Content-Type": "application/json",
            "Accept": "application/json, text/event-stream"
        }
        
        async with httpx.AsyncClient() as client:
            response = await client.post(self.server_url, json=payload, headers=headers)
            result = await self._parse_response(response)
            
            if result and "result" in result:
                return result["result"]
            elif result and "error" in result:
                raise Exception(f"MCP Tool Error: {result['error']}")
            else:
                raise Exception(f"Unexpected response: {result}")


def create_custom_tool_function(mcp_client: CustomMCPClient, tool_info: Dict[str, Any]):
    """Create a callable function from MCP tool info that ADK can use"""
    tool_name = tool_info.get("name", "unknown_tool")
    
    async def tool_function(**kwargs) -> str:
        """Callable tool function for Google ADK"""
        try:
            result = await mcp_client.call_tool(tool_name, kwargs)
            
            # Extract content from MCP result
            if "content" in result and len(result["content"]) > 0:
                content = result["content"][0]
                if content["type"] == "text":
                    return content["text"]
            
            # Fallback to JSON representation
            return json.dumps(result, indent=2)
            
        except Exception as e:
            return f"Error calling {tool_name}: {str(e)}"
    
    # Add metadata to the function for ADK
    tool_function.__name__ = tool_name
    tool_function.__doc__ = tool_info.get("description", "")
    
    return tool_function


class CustomMCPToolset:
    """Custom toolset that replaces MCPToolset for Google ADK"""
    
    def __init__(self, server_url: str):
        self.server_url = server_url
        self.client = CustomMCPClient(server_url)
        self.tools = {}
        self._discovered_tools = []
    
    async def discover_tools(self) -> List[str]:
        """Discover available tools from the MCP server"""
        try:
            tools = await self.client.list_tools()
            self._discovered_tools = tools
            
            tool_names = []
            for tool in tools:
                tool_name = tool.get("name", "unknown")
                tool_names.append(tool_name)
                
                # Store tool info for later function creation
                self.tools[tool_name] = tool
            
            return tool_names
            
        except Exception as e:
            print(f"Error discovering tools from {self.server_url}: {e}")
            return []
    
    async def get_tools(self) -> List:
        """Get all available tool functions for ADK"""
        if not self._discovered_tools:
            await self.discover_tools()
        
        # Return list of callable functions
        tool_functions = []
        for tool_info in self._discovered_tools:
            tool_function = create_custom_tool_function(self.client, tool_info)
            tool_functions.append(tool_function)
        
        return tool_functions
    
    def get_tool(self, tool_name: str) -> Optional:
        """Get specific tool function by name"""
        tool_info = self.tools.get(tool_name)
        if tool_info:
            return create_custom_tool_function(self.client, tool_info)
        return None