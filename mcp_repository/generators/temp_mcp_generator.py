"""
Temporary MCP Server Generator - Creates dynamic MCP servers with filtered tools
"""

import json
import asyncio
import subprocess
import tempfile
import shutil
from pathlib import Path
from typing import List, Dict, Optional, Any
from dataclasses import dataclass
import sys
import os
sys.path.append(str(Path(__file__).parent.parent))

from mcp import server
from mcp.types import Tool, TextContent
from mcp.server import Server

from registry.mcp_registry import MCPRegistry, MCPServer, ToolDefinition
from filters.tool_filter import ToolFilter, AgentCard


@dataclass
class TempMCPConfig:
    """Configuration for a temporary MCP server"""
    agent_id: str
    server_name: str
    tools: List[ToolDefinition]
    port: int
    temp_dir: Optional[str] = None
    metadata: Dict = None


class TempMCPGenerator:
    """Generates temporary MCP servers with filtered tools for specific agents"""

    def __init__(self, registry: MCPRegistry):
        self.registry = registry
        self.filter = ToolFilter(registry)
        self.active_servers = {}  # Track active temporary servers
        self.next_port = 9000  # Starting port for temp servers

    def _get_next_port(self) -> int:
        """Get the next available port for a temp server"""
        port = self.next_port
        self.next_port += 1
        return port

    def generate_server_code(self, config: TempMCPConfig) -> str:
        """Generate Python code for a temporary MCP server with routing"""

        # Create tool handler functions that route to original servers
        tool_handlers = []
        for tool in config.tools:
            if tool.can_be_called_remotely():
                # Create a handler that routes to the original server
                handler = f'''
async def handle_{tool.name}(**kwargs):
    """Handler for {tool.name} - routes to original server"""
    import aiohttp
    import json

    # Routing information
    endpoint = "{tool.routing.source_endpoint}"
    tool_path = "{tool.routing.tool_path}"
    timeout = {tool.routing.timeout}

    try:
        async with aiohttp.ClientSession(timeout=aiohttp.ClientTimeout(total=timeout)) as session:
            # Prepare MCP tool call request
            request_data = {{
                "jsonrpc": "2.0",
                "method": "tools/call",
                "params": {{
                    "name": "{tool.name}",
                    "arguments": kwargs
                }},
                "id": 1
            }}

            # Add custom headers if specified
            headers = {{"Content-Type": "application/json"}}
            {f'headers.update({dict(tool.routing.headers)})' if tool.routing.headers else ''}

            async with session.post(endpoint, json=request_data, headers=headers) as response:
                if response.status == 200:
                    result = await response.json()
                    if "result" in result:
                        return result["result"]
                    else:
                        return {{
                            "error": "MCP error",
                            "details": result.get("error", "Unknown error")
                        }}
                else:
                    return {{
                        "error": f"HTTP {{response.status}}",
                        "message": "Failed to call original server"
                    }}
    except Exception as e:
        return {{
            "error": "Connection failed",
            "message": str(e),
            "tool": "{tool.name}",
            "endpoint": endpoint
        }}
'''
            else:
                # Create a mock handler for tools without routing info
                handler = f'''
async def handle_{tool.name}(**kwargs):
    """Handler for {tool.name} - mock implementation"""
    return {{
        "status": "success",
        "message": "Mock execution of {tool.name}",
        "params": kwargs,
        "agent": "{config.agent_id}",
        "note": "This is a mock response - original server not available"
    }}
'''
            tool_handlers.append(handler)

        # Create tool registrations with complete schema
        tool_registrations = []
        for tool in config.tools:
            # Use the complete input schema from invocation info
            if tool.invocation and tool.invocation.input_schema:
                input_schema = json.dumps(tool.invocation.input_schema, indent=8)
            else:
                # Fallback to legacy parameters
                input_schema = json.dumps({
                    "type": "object",
                    "properties": tool.parameters,
                    "required": tool._extract_required_params() if hasattr(tool, '_extract_required_params') else []
                }, indent=8)

            registration = f'''
    server.add_tool(Tool(
        name="{tool.name}",
        description="{tool.description}",
        inputSchema={input_schema}
    ))
'''
            tool_registrations.append(registration)

        # Generate the complete server code
        code = f'''#!/usr/bin/env python3
"""
Temporary MCP Server for Agent: {config.agent_id}
Auto-generated server with filtered tools
"""

import asyncio
import json
from typing import Any
from mcp import server
from mcp.server import Server
from mcp.types import Tool, TextContent

# Initialize server
app = Server("{config.server_name}")

# Tool handlers
{"".join(tool_handlers)}

@app.list_tools()
async def list_tools():
    """List available tools"""
    tools = []
{"".join(tool_registrations)}
    return tools

@app.call_tool()
async def call_tool(name: str, arguments: dict) -> list:
    """Execute a tool"""

    # Map tool names to handlers
    handlers = {{
{chr(10).join(f'        "{tool.name}": handle_{tool.name},' for tool in config.tools)}
    }}

    if name not in handlers:
        return [TextContent(
            type="text",
            text=f"Unknown tool: {{name}}"
        )]

    try:
        result = await handlers[name](**arguments)
        return [TextContent(
            type="text",
            text=json.dumps(result, indent=2)
        )]
    except Exception as e:
        return [TextContent(
            type="text",
            text=f"Error executing {{name}}: {{str(e)}}"
        )]

async def main():
    """Run the server"""
    from mcp.server.stdio import stdio_server

    async with stdio_server() as (read_stream, write_stream):
        await app.run(
            read_stream,
            write_stream,
            app.create_initialization_options()
        )

if __name__ == "__main__":
    asyncio.run(main())
'''
        return code

    def generate_http_wrapper(self, config: TempMCPConfig, server_script: str) -> str:
        """Generate HTTP wrapper for the MCP server"""

        code = f'''#!/usr/bin/env python3
"""
HTTP Wrapper for Temporary MCP Server
Agent: {config.agent_id}
Port: {config.port}
"""

import asyncio
import json
import subprocess
import sys
from pathlib import Path
from aiohttp import web

class MCPHTTPWrapper:
    def __init__(self, mcp_script_path: str, port: int):
        self.mcp_script_path = mcp_script_path
        self.port = port
        self.process = None

    async def handle_list_tools(self, request):
        """Handle list tools request"""
        tools = {json.dumps([tool.name for tool in config.tools], indent=2)}

        return web.json_response({{
            "jsonrpc": "2.0",
            "id": 1,
            "result": {{
                "tools": json.loads(tools)
            }}
        }})

    async def handle_call_tool(self, request):
        """Handle tool call request"""
        data = await request.json()
        tool_name = data.get("params", {{}}).get("name")
        arguments = data.get("params", {{}}).get("arguments", {{}})

        # For this temp server, return mock responses
        result = {{
            "status": "success",
            "tool": tool_name,
            "arguments": arguments,
            "agent": "{config.agent_id}",
            "server": "{config.server_name}"
        }}

        return web.json_response({{
            "jsonrpc": "2.0",
            "id": data.get("id", 1),
            "result": {{
                "content": [{{
                    "type": "text",
                    "text": json.dumps(result, indent=2)
                }}]
            }}
        }})

    async def handle_request(self, request):
        """Main request handler"""
        if request.path == "/":
            data = await request.json()
            method = data.get("method", "")

            if method == "tools/list":
                return await self.handle_list_tools(request)
            elif method == "tools/call":
                return await self.handle_call_tool(request)
            else:
                return web.json_response({{
                    "jsonrpc": "2.0",
                    "id": data.get("id", 1),
                    "error": {{
                        "code": -32601,
                        "message": f"Method not found: {{method}}"
                    }}
                }})

        return web.Response(text="Temp MCP Server", status=404)

    async def start(self):
        """Start the HTTP server"""
        app = web.Application()
        app.router.add_post("/", self.handle_request)

        runner = web.AppRunner(app)
        await runner.setup()
        site = web.TCPSite(runner, "localhost", self.port)
        await site.start()

        print(f"Temp MCP Server running on http://localhost:{{self.port}}")
        print(f"Agent: {config.agent_id}")
        print(f"Tools: {[tool.name for tool in config.tools]}")

        # Keep running
        await asyncio.Event().wait()

async def main():
    server = MCPHTTPWrapper("{server_script}", {config.port})
    await server.start()

if __name__ == "__main__":
    asyncio.run(main())
'''
        return code

    def create_temp_server(self, agent: AgentCard,
                         min_score: float = 0.3,
                         use_http: bool = True) -> TempMCPConfig:
        """Create a temporary MCP server for an agent"""

        # Get filtered tools for the agent
        matched_tools = self.filter.filter_tools_for_agent(agent, min_score)

        if not matched_tools:
            raise ValueError(f"No matching tools found for agent {agent.name}")

        # Extract unique tools
        tools = []
        tool_names = set()
        for server_id, tool, score in matched_tools:
            if tool.name not in tool_names:
                tools.append(tool)
                tool_names.add(tool.name)

        # Create config
        config = TempMCPConfig(
            agent_id=agent.name.lower().replace(" ", "_"),
            server_name=f"temp_mcp_{agent.name.lower().replace(' ', '_')}",
            tools=tools,
            port=self._get_next_port(),
            metadata={
                "agent_description": agent.description,
                "created_for": agent.name,
                "tool_count": len(tools)
            }
        )

        # Create temporary directory
        temp_dir = Path(tempfile.mkdtemp(prefix=f"mcp_{config.agent_id}_"))
        config.temp_dir = str(temp_dir)

        # Generate server code
        server_code = self.generate_server_code(config)
        server_script = temp_dir / "server.py"
        server_script.write_text(server_code)
        server_script.chmod(0o755)

        if use_http:
            # Generate HTTP wrapper
            http_code = self.generate_http_wrapper(config, str(server_script))
            http_script = temp_dir / "http_server.py"
            http_script.write_text(http_code)
            http_script.chmod(0o755)

        # Save configuration
        config_file = temp_dir / "config.json"
        with open(config_file, 'w') as f:
            json.dump({
                "agent_id": config.agent_id,
                "server_name": config.server_name,
                "port": config.port,
                "tools": [{"name": t.name, "description": t.description} for t in tools],
                "temp_dir": str(temp_dir),
                "metadata": config.metadata
            }, f, indent=2)

        # Track the server
        self.active_servers[config.agent_id] = config

        print(f"Created temp server for {agent.name}:")
        print(f"  - Directory: {temp_dir}")
        print(f"  - Port: {config.port}")
        print(f"  - Tools: {len(tools)}")

        return config

    def start_temp_server(self, config: TempMCPConfig) -> subprocess.Popen:
        """Start a temporary server process"""
        temp_dir = Path(config.temp_dir)
        http_script = temp_dir / "http_server.py"

        if http_script.exists():
            process = subprocess.Popen(
                [sys.executable, str(http_script)],
                cwd=str(temp_dir),
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE
            )
            print(f"Started temp server {config.server_name} on port {config.port}")
            return process
        else:
            raise FileNotFoundError(f"HTTP server script not found: {http_script}")

    def cleanup_temp_server(self, agent_id: str):
        """Clean up a temporary server"""
        if agent_id in self.active_servers:
            config = self.active_servers[agent_id]
            if config.temp_dir and Path(config.temp_dir).exists():
                shutil.rmtree(config.temp_dir)
                print(f"Cleaned up temp server for {agent_id}")
            del self.active_servers[agent_id]

    def cleanup_all(self):
        """Clean up all temporary servers"""
        for agent_id in list(self.active_servers.keys()):
            self.cleanup_temp_server(agent_id)


def test_temp_server_generation():
    """Test the temporary server generation"""
    from registry.mcp_registry import create_example_servers
    from filters.tool_filter import create_example_agent_cards

    # Create registry and agents
    registry = create_example_servers()
    agents = create_example_agent_cards()

    # Create generator
    generator = TempMCPGenerator(registry)

    # Generate temp servers for all agents
    configs = []
    for agent in agents:
        print(f"\n{'='*60}")
        print(f"Generating temp server for: {agent.name}")
        config = generator.create_temp_server(agent)
        configs.append(config)

        # Show the generated files
        temp_dir = Path(config.temp_dir)
        print(f"\nGenerated files in {temp_dir}:")
        for file in temp_dir.iterdir():
            print(f"  - {file.name}")

    return generator, configs


if __name__ == "__main__":
    generator, configs = test_temp_server_generation()

    print(f"\n{'='*60}")
    print("Summary of generated temp servers:")
    for config in configs:
        print(f"\n{config.agent_id}:")
        print(f"  Port: {config.port}")
        print(f"  Tools: {[t.name for t in config.tools]}")

    # Cleanup
    print(f"\n{'='*60}")
    print("Cleaning up temp servers...")
    generator.cleanup_all()
    print("Done!")