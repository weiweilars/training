"""
Extended MCP Server Registry - Supports both local and external HTTP MCP servers
"""

import json
import yaml
import aiohttp
import asyncio
from pathlib import Path
from typing import Dict, List, Optional, Any, Union
from dataclasses import dataclass, field, asdict
from datetime import datetime
from enum import Enum


class ServerType(Enum):
    LOCAL = "local"
    HTTP = "http"
    STDIO = "stdio"


@dataclass
class ToolInvocation:
    """Information about how to invoke a tool"""
    input_schema: Dict[str, Any] = field(default_factory=dict)  # Complete input schema
    output_schema: Dict[str, Any] = field(default_factory=dict)  # Expected output schema
    required_params: List[str] = field(default_factory=list)  # Required parameters
    optional_params: List[str] = field(default_factory=list)  # Optional parameters
    examples: List[Dict[str, Any]] = field(default_factory=list)  # Usage examples
    error_codes: List[Dict[str, str]] = field(default_factory=list)  # Possible error responses


@dataclass
class ToolRouting:
    """Routing information for tool calls"""
    source_server_id: str  # Original server ID
    source_endpoint: str   # Original server endpoint
    tool_path: str        # Path to tool on original server
    auth_required: bool = False  # Whether authentication is needed
    headers: Dict[str, str] = field(default_factory=dict)  # Required headers
    timeout: int = 30     # Timeout for tool calls


@dataclass
class ToolDefinition:
    """Represents a single tool in an MCP server with complete invocation info"""
    name: str
    description: str
    parameters: Dict[str, Any] = field(default_factory=dict)  # Legacy - use invocation.input_schema
    categories: List[str] = field(default_factory=list)
    keywords: List[str] = field(default_factory=list)
    tool_id: Optional[str] = None  # Tool identifier from MCP server
    unique_id: Optional[str] = None  # Generated unique identifier
    server_id: Optional[str] = None  # Which server this tool belongs to

    # Enhanced invocation information
    invocation: Optional[ToolInvocation] = None  # How to call this tool
    routing: Optional[ToolRouting] = None  # How to route calls to original server

    def __post_init__(self):
        """Generate unique identifier and setup invocation info if not provided"""
        import hashlib

        # Use tool_id if provided by MCP server, otherwise generate one
        if not self.unique_id:
            if self.tool_id:
                self.unique_id = self.tool_id
            else:
                # Generate unique ID from server_id + tool_name + description hash
                content = f"{self.server_id or 'unknown'}:{self.name}:{self.description[:100]}"
                hash_obj = hashlib.md5(content.encode())
                self.unique_id = f"tool_{hash_obj.hexdigest()[:12]}"

        # Initialize invocation if not provided
        if not self.invocation:
            self.invocation = ToolInvocation(
                input_schema=self.parameters,  # Use legacy parameters as fallback
                required_params=self._extract_required_params(),
                optional_params=self._extract_optional_params()
            )

    def _extract_required_params(self) -> List[str]:
        """Extract required parameters from schema"""
        if isinstance(self.parameters, dict):
            return self.parameters.get('required', [])
        return []

    def _extract_optional_params(self) -> List[str]:
        """Extract optional parameters from schema"""
        if isinstance(self.parameters, dict) and 'properties' in self.parameters:
            all_params = list(self.parameters['properties'].keys())
            required = self.parameters.get('required', [])
            return [p for p in all_params if p not in required]
        return []

    def get_full_identifier(self) -> str:
        """Get fully qualified tool identifier"""
        if self.server_id:
            return f"{self.server_id}.{self.name}"
        return self.name

    def can_be_called_remotely(self) -> bool:
        """Check if this tool can be called on the original server"""
        return self.routing is not None and self.routing.source_endpoint

    def get_call_signature(self) -> Dict[str, Any]:
        """Get the complete call signature for this tool"""
        return {
            "name": self.name,
            "description": self.description,
            "input_schema": self.invocation.input_schema if self.invocation else self.parameters,
            "required_params": self.invocation.required_params if self.invocation else [],
            "optional_params": self.invocation.optional_params if self.invocation else [],
            "routing": {
                "endpoint": self.routing.source_endpoint if self.routing else None,
                "server_id": self.server_id,
                "tool_path": self.routing.tool_path if self.routing else self.name
            }
        }


@dataclass
class MCPServer:
    """Represents an MCP server with its tools and metadata"""
    name: str
    description: str
    version: str
    tools: List[ToolDefinition]
    server_type: ServerType = ServerType.LOCAL
    address: Optional[str] = None  # For HTTP servers: "http://localhost:8080"
    endpoint: Optional[str] = None  # Server endpoint URL for connections
    host: str = "localhost"  # For local servers
    port: Optional[int] = None  # For local servers
    protocol: str = "http"
    metadata: Dict[str, Any] = field(default_factory=dict)
    created_at: str = field(default_factory=lambda: datetime.now().isoformat())
    last_discovered: Optional[str] = None  # When tools were last fetched

    def __post_init__(self):
        """Set endpoint based on server type and address"""
        if self.server_type == ServerType.HTTP and self.address:
            self.endpoint = self.address
        elif self.server_type == ServerType.LOCAL and self.port:
            self.endpoint = f"{self.protocol}://{self.host}:{self.port}"

    def to_dict(self) -> Dict:
        """Convert to dictionary for serialization"""
        data = asdict(self)
        data['server_type'] = self.server_type.value
        data['tools'] = [asdict(tool) for tool in self.tools]
        return data

    @classmethod
    def from_dict(cls, data: Dict) -> 'MCPServer':
        """Create from dictionary"""
        tools = [ToolDefinition(**tool_data) for tool_data in data.pop('tools', [])]
        server_type = ServerType(data.pop('server_type', 'local'))
        return cls(tools=tools, server_type=server_type, **data)

    def get_connection_url(self) -> Optional[str]:
        """Get the URL for connecting to this server"""
        return self.endpoint


@dataclass
class MCPServerInfo:
    """Complete server information discovered from MCP server"""
    name: str
    description: str
    version: str
    tools: List[ToolDefinition]
    capabilities: List[str] = field(default_factory=list)
    metadata: Dict[str, Any] = field(default_factory=dict)


class MCPClient:
    """Client for discovering complete server information from HTTP MCP servers"""

    @staticmethod
    async def discover_server_info(address: str, timeout: int = 10) -> Optional[MCPServerInfo]:
        """
        Discover complete server information from an HTTP MCP server

        Args:
            address: HTTP address of the MCP server (e.g., "http://localhost:8080")
            timeout: Request timeout in seconds

        Returns:
            Complete server information or None if discovery failed
        """
        try:
            async with aiohttp.ClientSession(timeout=aiohttp.ClientTimeout(total=timeout)) as session:
                # Step 1: Initialize connection to get server info
                init_request = {
                    "jsonrpc": "2.0",
                    "method": "initialize",
                    "params": {
                        "protocolVersion": "2024-11-05",
                        "capabilities": {
                            "tools": {}
                        },
                        "clientInfo": {
                            "name": "MCP Registry Client",
                            "version": "1.0.0"
                        }
                    },
                    "id": 1
                }

                server_info = {}

                # Try initialization first
                async with session.post(address, json=init_request) as response:
                    if response.status == 200:
                        data = await response.json()
                        if "result" in data:
                            result = data["result"]
                            server_info = {
                                "name": result.get("serverInfo", {}).get("name", "Unknown Server"),
                                "version": result.get("serverInfo", {}).get("version", "1.0.0"),
                                "description": result.get("serverInfo", {}).get("description", ""),
                                "capabilities": list(result.get("capabilities", {}).keys()),
                                "metadata": result.get("serverInfo", {})
                            }

                # Step 2: List tools
                tools_request = {
                    "jsonrpc": "2.0",
                    "method": "tools/list",
                    "id": 2
                }

                tools = []
                async with session.post(address, json=tools_request) as response:
                    if response.status == 200:
                        data = await response.json()
                        if "result" in data and "tools" in data["result"]:
                            for tool_data in data["result"]["tools"]:
                                # Extract complete schema information from MCP tool definition
                                input_schema = tool_data.get("inputSchema", {})

                                # Create invocation information
                                invocation = ToolInvocation(
                                    input_schema=input_schema,
                                    required_params=input_schema.get("required", []),
                                    optional_params=MCPClient._extract_optional_params_from_schema(input_schema),
                                    examples=tool_data.get("examples", []),
                                    error_codes=tool_data.get("errorCodes", [])
                                )

                                # Create routing information (will be set during registration)
                                routing = ToolRouting(
                                    source_server_id="",  # Will be set during registration
                                    source_endpoint=address,
                                    tool_path=tool_data.get("name", ""),
                                    auth_required=tool_data.get("authRequired", False),
                                    headers=tool_data.get("headers", {}),
                                    timeout=tool_data.get("timeout", 30)
                                )

                                tool = ToolDefinition(
                                    name=tool_data.get("name", ""),
                                    description=tool_data.get("description", ""),
                                    parameters=input_schema.get("properties", {}),  # Legacy support
                                    categories=tool_data.get("categories", []),
                                    keywords=tool_data.get("keywords", []),
                                    tool_id=tool_data.get("id") or tool_data.get("tool_id"),
                                    server_id=None,  # Will be set when registering
                                    invocation=invocation,
                                    routing=routing
                                )
                                tools.append(tool)

                # If no server info from initialization, create minimal info
                if not server_info.get("name") or server_info["name"] == "Unknown Server":
                    server_info = MCPClient._create_minimal_server_info(address, tools)

                return MCPServerInfo(
                    name=server_info.get("name", f"Server at {address}"),
                    description=server_info.get("description", f"MCP server at {address}"),
                    version=server_info.get("version", "1.0.0"),
                    tools=tools,
                    capabilities=server_info.get("capabilities", []),
                    metadata=server_info.get("metadata", {})
                )

        except asyncio.TimeoutError:
            print(f"Timeout connecting to {address}")
        except aiohttp.ClientError as e:
            print(f"Error connecting to {address}: {e}")
        except Exception as e:
            print(f"Unexpected error discovering server info from {address}: {e}")

        return None

    @staticmethod
    def _extract_keywords(text: str) -> List[str]:
        """Extract keywords from text"""
        import re

        # Common stop words to filter out
        stop_words = {
            'the', 'a', 'an', 'and', 'or', 'but', 'in', 'on', 'at', 'to', 'for',
            'of', 'with', 'by', 'from', 'as', 'is', 'was', 'are', 'were', 'been',
            'have', 'has', 'had', 'do', 'does', 'did', 'will', 'would', 'could',
            'should', 'may', 'might', 'must', 'can', 'this', 'that', 'these',
            'those', 'i', 'you', 'he', 'she', 'it', 'we', 'they'
        }

        # Extract words (alphanumeric only)
        words = re.findall(r'\b[a-zA-Z][a-zA-Z0-9_]*\b', text.lower())

        # Filter out stop words and short words
        keywords = [word for word in words if word not in stop_words and len(word) > 2]

        return keywords[:10]  # Limit to 10 keywords

    @staticmethod
    def _extract_optional_params_from_schema(schema: Dict[str, Any]) -> List[str]:
        """Extract optional parameters from JSON schema"""
        if not isinstance(schema, dict) or 'properties' not in schema:
            return []

        all_params = list(schema['properties'].keys())
        required_params = schema.get('required', [])
        return [param for param in all_params if param not in required_params]

    @staticmethod
    def _create_minimal_server_info(address: str, tools: List[ToolDefinition]) -> Dict[str, Any]:
        """Create minimal server info when MCP server doesn't provide server details"""
        # Use only basic information without inferring categories or purposes
        parsed_address = address.split('://')[-1]  # Remove protocol

        return {
            "name": f"MCP Server ({parsed_address})",
            "description": f"MCP server at {address} with {len(tools)} tools",
            "version": "1.0.0",
            "capabilities": ["tools"],
            "metadata": {
                "auto_discovered": True,
                "tool_count": len(tools),
                "address": address
            }
        }

    @staticmethod
    async def discover_tools(address: str, timeout: int = 10) -> List[ToolDefinition]:
        """
        Discover available tools from an HTTP MCP server (legacy method)

        Args:
            address: HTTP address of the MCP server
            timeout: Request timeout in seconds

        Returns:
            List of discovered tools
        """
        server_info = await MCPClient.discover_server_info(address, timeout)
        return server_info.tools if server_info else []

    @staticmethod
    def discover_server_info_sync(address: str, timeout: int = 10) -> Optional[MCPServerInfo]:
        """Synchronous wrapper for discover_server_info"""
        return asyncio.run(MCPClient.discover_server_info(address, timeout))

    @staticmethod
    def discover_tools_sync(address: str, timeout: int = 10) -> List[ToolDefinition]:
        """Synchronous wrapper for discover_tools"""
        return asyncio.run(MCPClient.discover_tools(address, timeout))


class ExtendedMCPRegistry:
    """Extended registry for managing both local and external MCP servers"""

    def __init__(self, registry_path: str = "exploration/mcp_repository/registry/servers_extended.json"):
        self.registry_path = Path(registry_path)
        self.servers: Dict[str, MCPServer] = {}
        self._load_registry()

    def _load_registry(self):
        """Load existing registry from file"""
        if self.registry_path.exists():
            try:
                with open(self.registry_path, 'r') as f:
                    data = json.load(f)
                    for server_id, server_data in data.items():
                        self.servers[server_id] = MCPServer.from_dict(server_data)
            except Exception as e:
                print(f"Error loading registry: {e}")
                self.servers = {}

    def save_registry(self):
        """Save registry to file"""
        self.registry_path.parent.mkdir(parents=True, exist_ok=True)
        data = {
            server_id: server.to_dict()
            for server_id, server in self.servers.items()
        }
        with open(self.registry_path, 'w') as f:
            json.dump(data, f, indent=2)

    def register_http_server(self,
                           server_id: str,
                           address: str,
                           auto_discover: bool = True) -> bool:
        """
        Register an external HTTP MCP server by its address
        All server information is automatically discovered from the MCP server

        Args:
            server_id: Unique identifier for the server
            address: HTTP address (e.g., "http://localhost:8080")
            auto_discover: Whether to automatically discover all server info

        Returns:
            True if registration successful
        """
        if server_id in self.servers:
            print(f"Server {server_id} already exists. Use update_server to modify.")
            return False

        if auto_discover:
            print(f"Auto-discovering server information from {address}...")
            server_info = MCPClient.discover_server_info_sync(address)

            if not server_info:
                print(f"Failed to discover server information from {address}")
                return False

            print(f"Discovered server: {server_info.name}")
            print(f"  Description: {server_info.description}")
            print(f"  Version: {server_info.version}")
            print(f"  Tools: {len(server_info.tools)}")
            print(f"  Capabilities: {', '.join(server_info.capabilities)}")

            # Set server_id on all tools and update routing information
            for tool in server_info.tools:
                tool.server_id = server_id
                # Update routing information
                if tool.routing:
                    tool.routing.source_server_id = server_id
                # This will trigger __post_init__ to generate unique_id
                tool.__post_init__()

            # Create server entry from discovered information
            server = MCPServer(
                name=server_info.name,
                description=server_info.description,
                version=server_info.version,
                tools=server_info.tools,
                server_type=ServerType.HTTP,
                address=address,
                endpoint=address,  # Set endpoint explicitly
                last_discovered=datetime.now().isoformat(),
                metadata=server_info.metadata
            )
        else:
            # Fallback: create minimal server entry without discovery
            server = MCPServer(
                name=f"HTTP Server at {address}",
                description=f"External MCP server at {address}",
                version="unknown",
                tools=[],
                server_type=ServerType.HTTP,
                address=address,
                endpoint=address  # Set endpoint explicitly
            )

        self.servers[server_id] = server
        self.save_registry()
        print(f"Registered HTTP server '{server_id}' at {address}")
        return True

    def register_server(self, server_id: str, server: MCPServer) -> bool:
        """Register a new MCP server (local or external)"""
        if server_id in self.servers:
            print(f"Server {server_id} already exists. Use update_server to modify.")
            return False

        self.servers[server_id] = server
        self.save_registry()
        return True

    def refresh_http_server_tools(self, server_id: str) -> bool:
        """
        Refresh tool list for an HTTP server by re-discovering

        Args:
            server_id: Server to refresh

        Returns:
            True if refresh successful
        """
        if server_id not in self.servers:
            print(f"Server {server_id} not found")
            return False

        server = self.servers[server_id]
        if server.server_type != ServerType.HTTP or not server.address:
            print(f"Server {server_id} is not an HTTP server")
            return False

        print(f"Refreshing tools for {server_id} from {server.address}...")
        tools = MCPClient.discover_tools_sync(server.address)

        if tools:
            server.tools = tools
            server.last_discovered = datetime.now().isoformat()
            self.save_registry()
            print(f"Updated {len(tools)} tools for {server_id}")
            return True
        else:
            print(f"No tools discovered from {server.address}")
            return False

    def get_server_address(self, server_id: str) -> Optional[str]:
        """Get the address for connecting to a server"""
        server = self.servers.get(server_id)
        if not server:
            return None

        return server.get_connection_url()

    def get_server_endpoint(self, server_id: str) -> Optional[str]:
        """Get the endpoint URL for connecting to a server"""
        return self.get_server_address(server_id)

    def list_http_servers(self) -> Dict[str, str]:
        """List all registered HTTP servers with their endpoints"""
        return {
            server_id: server.endpoint
            for server_id, server in self.servers.items()
            if server.server_type == ServerType.HTTP and server.endpoint
        }

    def list_all_endpoints(self) -> Dict[str, str]:
        """List all registered servers with their endpoints"""
        return {
            server_id: server.get_connection_url()
            for server_id, server in self.servers.items()
            if server.get_connection_url()
        }

    def get_tool_by_unique_id(self, unique_id: str) -> Optional[ToolDefinition]:
        """Find a tool by its unique identifier"""
        for server in self.servers.values():
            for tool in server.tools:
                if tool.unique_id == unique_id:
                    return tool
        return None

    def get_tool_by_full_identifier(self, full_id: str) -> Optional[ToolDefinition]:
        """Find a tool by its full identifier (server_id.tool_name)"""
        for server in self.servers.values():
            for tool in server.tools:
                if tool.get_full_identifier() == full_id:
                    return tool
        return None

    def list_all_tools_with_ids(self) -> Dict[str, Dict[str, Any]]:
        """List all tools with their identifiers"""
        tools = {}
        for server_id, server in self.servers.items():
            for tool in server.tools:
                tools[tool.unique_id] = {
                    "name": tool.name,
                    "description": tool.description,
                    "server_id": server_id,
                    "server_name": server.name,
                    "tool_id": tool.tool_id,
                    "unique_id": tool.unique_id,
                    "full_identifier": tool.get_full_identifier(),
                    "endpoint": server.endpoint,
                    "categories": tool.categories,
                    "keywords": tool.keywords
                }
        return tools

    def search_tools_by_identifier(self, pattern: str) -> List[ToolDefinition]:
        """Search tools by any identifier pattern"""
        matching_tools = []
        pattern_lower = pattern.lower()

        for server in self.servers.values():
            for tool in server.tools:
                # Check various identifier fields
                if (pattern_lower in tool.name.lower() or
                    (tool.tool_id and pattern_lower in tool.tool_id.lower()) or
                    (tool.unique_id and pattern_lower in tool.unique_id.lower()) or
                    pattern_lower in tool.get_full_identifier().lower()):
                    matching_tools.append(tool)

        return matching_tools

    def bulk_register_http_servers(self, servers: Dict[str, str], discover_tools: bool = True):
        """
        Register multiple HTTP servers at once

        Args:
            servers: Dict mapping server_id to address
            discover_tools: Whether to discover tools for each server
        """
        for server_id, address in servers.items():
            self.register_http_server(server_id, address, discover_tools=discover_tools)

    def export_server_config(self, server_id: str) -> Optional[Dict]:
        """Export server configuration for use by agents"""
        server = self.servers.get(server_id)
        if not server:
            return None

        config = {
            "id": server_id,
            "name": server.name,
            "type": server.server_type.value,
            "address": server.address,  # Original address
            "endpoint": server.endpoint,  # Connection endpoint
            "version": server.version,
            "description": server.description,
            "tools": [
                {
                    "name": tool.name,
                    "description": tool.description,
                    "categories": tool.categories,
                    "keywords": tool.keywords,
                    "tool_id": tool.tool_id,
                    "unique_id": tool.unique_id,
                    "full_identifier": tool.get_full_identifier()
                }
                for tool in server.tools
            ],
            "metadata": server.metadata
        }
        return config


def example_usage():
    """Example of registering and using HTTP MCP servers"""

    # Create registry
    registry = ExtendedMCPRegistry()

    # Register individual HTTP servers
    registry.register_http_server(
        server_id="hr_tools_prod",
        address="http://hr-tools.company.com:8080",
        name="Production HR Tools",
        description="Production HR recruitment tools server",
        discover_tools=False  # Set to True if server is running
    )

    # Register multiple servers at once
    external_servers = {
        "analytics_server": "http://analytics.local:8100",
        "communication_api": "http://comm-api.local:8200",
        "screening_service": "http://screening.ai:9000"
    }

    registry.bulk_register_http_servers(external_servers, discover_tools=False)

    # List all HTTP servers
    print("\nRegistered HTTP Servers:")
    for server_id, address in registry.list_http_servers().items():
        print(f"  - {server_id}: {address}")

    # Get server configuration for an agent
    config = registry.export_server_config("hr_tools_prod")
    if config:
        print(f"\nServer config for hr_tools_prod:")
        print(json.dumps(config, indent=2))

    return registry


if __name__ == "__main__":
    # Example with mock HTTP servers
    registry = example_usage()

    # If you have actual HTTP MCP servers running, you can test discovery:
    # registry.register_http_server(
    #     "test_server",
    #     "http://localhost:8080",
    #     discover_tools=True
    # )