#!/usr/bin/env python3
"""
Simple MCP Server Registration - Register by address only
All information is discovered directly from the MCP server
"""

import sys
import json
from pathlib import Path

sys.path.append(str(Path(__file__).parent.parent))

from registry.mcp_registry_extended import ExtendedMCPRegistry


def main():
    """Demonstrate simple MCP server registration by address"""
    print("MCP Server Registration - Address Only")
    print("="*50)

    # Create registry
    registry = ExtendedMCPRegistry()

    # Example: Register MCP servers by address only
    # All information will be auto-discovered from the server

    servers_to_register = [
        ("hr_tools", "http://localhost:8080"),
        ("analytics_api", "http://localhost:8100"),
        ("communication_service", "http://localhost:8200"),
    ]

    print("\nRegistering MCP servers...")
    print("-" * 30)

    for server_id, address in servers_to_register:
        print(f"\nRegistering: {server_id} at {address}")

        # This single call will:
        # 1. Connect to the MCP server
        # 2. Call initialize() to get server info (name, version, description)
        # 3. Call tools/list to get all available tools
        # 4. Auto-extract categories and keywords from tool definitions
        # 5. Store everything in the registry

        success = registry.register_http_server(
            server_id=server_id,
            address=address,
            auto_discover=True  # This is the default
        )

        if success:
            server = registry.servers[server_id]
            print(f"✓ Successfully registered {server.name}")
            print(f"  Version: {server.version}")
            print(f"  Tools: {len(server.tools)}")
        else:
            print(f"✗ Failed to register {server_id}")

    # Show final registry state
    print("\n" + "="*50)
    print("FINAL REGISTRY STATE")
    print("="*50)

    for server_id, server in registry.servers.items():
        print(f"\n{server_id}:")
        print(f"  Name: {server.name}")
        print(f"  Address: {server.address}")
        print(f"  Description: {server.description}")
        print(f"  Version: {server.version}")
        print(f"  Tools ({len(server.tools)}):")

        for tool in server.tools[:3]:  # Show first 3 tools
            print(f"    - {tool.name}: {tool.description}")

        if len(server.tools) > 3:
            print(f"    ... and {len(server.tools) - 3} more")

    # Show how to get connection info
    print("\n" + "="*50)
    print("CONNECTION INFORMATION")
    print("="*50)

    print("All server endpoints:")
    for server_id, endpoint in registry.list_all_endpoints().items():
        print(f"  {server_id}: {endpoint}")

    print("\nHTTP servers only:")
    for server_id, endpoint in registry.list_http_servers().items():
        print(f"  {server_id}: {endpoint}")

    # Export example configuration
    print("\n" + "="*50)
    print("EXAMPLE EXPORTED CONFIG")
    print("="*50)

    if registry.servers:
        first_server_id = list(registry.servers.keys())[0]
        config = registry.export_server_config(first_server_id)
        if config:
            print(json.dumps(config, indent=2))


if __name__ == "__main__":
    main()