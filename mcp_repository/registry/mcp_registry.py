"""
MCP Server Registry - Central repository for all available MCP servers and their tools
"""

import json
import yaml
from pathlib import Path
from typing import Dict, List, Optional, Any
from dataclasses import dataclass, field, asdict
from datetime import datetime


@dataclass
class ToolDefinition:
    """Represents a single tool in an MCP server"""
    name: str
    description: str
    parameters: Dict[str, Any] = field(default_factory=dict)
    categories: List[str] = field(default_factory=list)  # e.g., ["hr", "recruitment", "communication"]
    keywords: List[str] = field(default_factory=list)  # for better matching


@dataclass
class MCPServer:
    """Represents an MCP server with its tools and metadata"""
    name: str
    description: str
    version: str
    tools: List[ToolDefinition]
    host: str = "localhost"
    port: Optional[int] = None
    protocol: str = "http"  # http, stdio, pipe
    metadata: Dict[str, Any] = field(default_factory=dict)
    created_at: str = field(default_factory=lambda: datetime.now().isoformat())

    def to_dict(self) -> Dict:
        """Convert to dictionary for serialization"""
        data = asdict(self)
        data['tools'] = [asdict(tool) for tool in self.tools]
        return data

    @classmethod
    def from_dict(cls, data: Dict) -> 'MCPServer':
        """Create from dictionary"""
        tools = [ToolDefinition(**tool_data) for tool_data in data.pop('tools', [])]
        return cls(tools=tools, **data)


class MCPRegistry:
    """Central registry for managing MCP servers"""

    def __init__(self, registry_path: str = "exploration/mcp_repository/registry/servers.json"):
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

    def register_server(self, server_id: str, server: MCPServer) -> bool:
        """Register a new MCP server"""
        if server_id in self.servers:
            print(f"Server {server_id} already exists. Use update_server to modify.")
            return False

        self.servers[server_id] = server
        self.save_registry()
        return True

    def update_server(self, server_id: str, server: MCPServer) -> bool:
        """Update an existing MCP server"""
        if server_id not in self.servers:
            print(f"Server {server_id} not found")
            return False

        self.servers[server_id] = server
        self.save_registry()
        return True

    def get_server(self, server_id: str) -> Optional[MCPServer]:
        """Get a specific server by ID"""
        return self.servers.get(server_id)

    def list_servers(self) -> List[str]:
        """List all registered server IDs"""
        return list(self.servers.keys())

    def search_servers_by_tool(self, tool_name: str) -> List[str]:
        """Find servers that have a specific tool"""
        matching_servers = []
        for server_id, server in self.servers.items():
            for tool in server.tools:
                if tool_name.lower() in tool.name.lower():
                    matching_servers.append(server_id)
                    break
        return matching_servers

    def search_servers_by_category(self, category: str) -> List[str]:
        """Find servers with tools in a specific category"""
        matching_servers = []
        for server_id, server in self.servers.items():
            for tool in server.tools:
                if category.lower() in [c.lower() for c in tool.categories]:
                    matching_servers.append(server_id)
                    break
        return matching_servers

    def get_all_tools(self) -> Dict[str, List[ToolDefinition]]:
        """Get all tools grouped by server"""
        return {
            server_id: server.tools
            for server_id, server in self.servers.items()
        }

    def import_from_yaml(self, yaml_path: str) -> bool:
        """Import server definition from YAML file"""
        try:
            with open(yaml_path, 'r') as f:
                data = yaml.safe_load(f)

            # Extract server info
            server_id = data.get('id', Path(yaml_path).stem)
            tools = []

            for tool_data in data.get('tools', []):
                tool = ToolDefinition(
                    name=tool_data['name'],
                    description=tool_data.get('description', ''),
                    parameters=tool_data.get('parameters', {}),
                    categories=tool_data.get('categories', []),
                    keywords=tool_data.get('keywords', [])
                )
                tools.append(tool)

            server = MCPServer(
                name=data.get('name', server_id),
                description=data.get('description', ''),
                version=data.get('version', '1.0.0'),
                tools=tools,
                host=data.get('host', 'localhost'),
                port=data.get('port'),
                protocol=data.get('protocol', 'http'),
                metadata=data.get('metadata', {})
            )

            return self.register_server(server_id, server)

        except Exception as e:
            print(f"Error importing from YAML: {e}")
            return False


def create_example_servers():
    """Create example MCP servers for testing"""
    registry = MCPRegistry()

    # HR Tools Server
    hr_tools = [
        ToolDefinition(
            name="create_job_requisition",
            description="Create a new job requisition",
            categories=["hr", "recruitment", "requisition"],
            keywords=["job", "position", "hiring", "requisition"]
        ),
        ToolDefinition(
            name="screen_resume",
            description="Screen and evaluate resumes",
            categories=["hr", "recruitment", "screening"],
            keywords=["resume", "cv", "screening", "evaluation"]
        ),
        ToolDefinition(
            name="schedule_interview",
            description="Schedule interviews with candidates",
            categories=["hr", "recruitment", "scheduling"],
            keywords=["interview", "schedule", "calendar", "meeting"]
        ),
        ToolDefinition(
            name="send_notification",
            description="Send notifications to candidates or team",
            categories=["hr", "communication"],
            keywords=["email", "notification", "message", "communication"]
        )
    ]

    hr_server = MCPServer(
        name="HR Recruitment Tools",
        description="MCP server for HR recruitment operations",
        version="1.0.0",
        tools=hr_tools,
        port=8100
    )

    registry.register_server("hr_recruitment", hr_server)

    # Analytics Server
    analytics_tools = [
        ToolDefinition(
            name="generate_report",
            description="Generate analytics reports",
            categories=["analytics", "reporting"],
            keywords=["report", "analytics", "data", "metrics"]
        ),
        ToolDefinition(
            name="analyze_metrics",
            description="Analyze recruitment metrics",
            categories=["analytics", "hr"],
            keywords=["metrics", "kpi", "analysis", "performance"]
        )
    ]

    analytics_server = MCPServer(
        name="Analytics Tools",
        description="MCP server for analytics and reporting",
        version="1.0.0",
        tools=analytics_tools,
        port=8101
    )

    registry.register_server("analytics", analytics_server)

    # Communication Server
    comm_tools = [
        ToolDefinition(
            name="send_email",
            description="Send email messages",
            categories=["communication", "email"],
            keywords=["email", "send", "message"]
        ),
        ToolDefinition(
            name="send_sms",
            description="Send SMS messages",
            categories=["communication", "sms"],
            keywords=["sms", "text", "message", "mobile"]
        ),
        ToolDefinition(
            name="create_calendar_event",
            description="Create calendar events",
            categories=["communication", "scheduling"],
            keywords=["calendar", "event", "meeting", "schedule"]
        )
    ]

    comm_server = MCPServer(
        name="Communication Tools",
        description="MCP server for communication operations",
        version="1.0.0",
        tools=comm_tools,
        port=8102
    )

    registry.register_server("communication", comm_server)

    print(f"Created {len(registry.servers)} example servers")
    return registry


if __name__ == "__main__":
    # Create example servers for testing
    registry = create_example_servers()

    # Test search functionality
    print("\nServers with 'schedule' tools:")
    print(registry.search_servers_by_tool("schedule"))

    print("\nServers in 'hr' category:")
    print(registry.search_servers_by_category("hr"))

    print("\nAll registered servers:")
    print(registry.list_servers())