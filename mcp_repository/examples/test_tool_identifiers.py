#!/usr/bin/env python3
"""
Test Tool Identifier Functionality
"""

import sys
import json
from pathlib import Path

sys.path.append(str(Path(__file__).parent.parent))

from registry.mcp_registry_extended import ExtendedMCPRegistry, ToolDefinition, MCPServer, ServerType


def create_test_servers():
    """Create test servers with tools to demonstrate identifiers"""
    registry = ExtendedMCPRegistry()

    # Create test tools with different identifier scenarios
    hr_tools = [
        ToolDefinition(
            name="create_job_posting",
            description="Create a new job posting",
            tool_id="hr_001",  # Server provides tool ID
            server_id="hr_server",
            categories=["hr", "recruitment"]
        ),
        ToolDefinition(
            name="screen_candidate",
            description="Screen candidate applications",
            # No tool_id - will generate unique_id
            server_id="hr_server",
            categories=["hr", "screening"]
        ),
        ToolDefinition(
            name="schedule_interview",
            description="Schedule interviews with candidates",
            tool_id="hr_003",
            server_id="hr_server",
            categories=["hr", "scheduling"]
        )
    ]

    # Create test server
    hr_server = MCPServer(
        name="HR Management Server",
        description="HR tools for recruitment and management",
        version="2.1.0",
        tools=hr_tools,
        server_type=ServerType.HTTP,
        address="http://hr-tools.company.com:8080",
        endpoint="http://hr-tools.company.com:8080"
    )

    # Register the server
    registry.servers["hr_server"] = hr_server

    # Create another test server
    analytics_tools = [
        ToolDefinition(
            name="generate_report",
            description="Generate analytics reports",
            tool_id="analytics_report_v2",  # Different ID format
            server_id="analytics_api",
            categories=["analytics", "reporting"]
        ),
        ToolDefinition(
            name="analyze_metrics",
            description="Analyze recruitment metrics",
            server_id="analytics_api",
            categories=["analytics", "metrics"]
        )
    ]

    analytics_server = MCPServer(
        name="Analytics API",
        description="Analytics and reporting services",
        version="1.5.2",
        tools=analytics_tools,
        server_type=ServerType.HTTP,
        address="http://analytics.internal:8100",
        endpoint="http://analytics.internal:8100"
    )

    registry.servers["analytics_api"] = analytics_server
    registry.save_registry()

    return registry


def test_tool_identifiers():
    """Test tool identifier functionality"""
    print("TOOL IDENTIFIER FUNCTIONALITY TEST")
    print("="*50)

    # Create test registry
    registry = create_test_servers()

    # Test 1: List all tools with their identifiers
    print("\n1. ALL TOOLS WITH IDENTIFIERS:")
    print("-" * 30)

    all_tools = registry.list_all_tools_with_ids()
    for unique_id, tool_info in all_tools.items():
        print(f"\nUnique ID: {unique_id}")
        print(f"  Name: {tool_info['name']}")
        print(f"  Server: {tool_info['server_name']} ({tool_info['server_id']})")
        print(f"  Tool ID: {tool_info['tool_id'] or 'Generated'}")
        print(f"  Full ID: {tool_info['full_identifier']}")
        print(f"  Endpoint: {tool_info['endpoint']}")

    # Test 2: Find tools by unique ID
    print("\n\n2. FIND TOOLS BY UNIQUE ID:")
    print("-" * 30)

    # Get first tool's unique ID for testing
    first_unique_id = list(all_tools.keys())[0]
    print(f"\nSearching for unique ID: {first_unique_id}")

    tool = registry.get_tool_by_unique_id(first_unique_id)
    if tool:
        print(f"  Found: {tool.name}")
        print(f"  Description: {tool.description}")
        print(f"  Server: {tool.server_id}")
    else:
        print("  Tool not found")

    # Test 3: Find tools by full identifier
    print("\n\n3. FIND TOOLS BY FULL IDENTIFIER:")
    print("-" * 30)

    full_ids_to_test = ["hr_server.create_job_posting", "analytics_api.generate_report"]

    for full_id in full_ids_to_test:
        print(f"\nSearching for full ID: {full_id}")
        tool = registry.get_tool_by_full_identifier(full_id)
        if tool:
            print(f"  Found: {tool.name}")
            print(f"  Unique ID: {tool.unique_id}")
            print(f"  Tool ID: {tool.tool_id or 'Generated'}")
        else:
            print("  Tool not found")

    # Test 4: Search tools by pattern
    print("\n\n4. SEARCH TOOLS BY PATTERN:")
    print("-" * 30)

    patterns = ["job", "hr_", "analytics", "screen"]

    for pattern in patterns:
        print(f"\nSearching for pattern: '{pattern}'")
        matching_tools = registry.search_tools_by_identifier(pattern)
        if matching_tools:
            for tool in matching_tools:
                print(f"  - {tool.name} ({tool.unique_id})")
        else:
            print("  No matching tools found")

    # Test 5: Export configuration with identifiers
    print("\n\n5. EXPORTED CONFIGURATION WITH IDENTIFIERS:")
    print("-" * 50)

    config = registry.export_server_config("hr_server")
    if config:
        print(f"\nServer: {config['name']}")
        print(f"Endpoint: {config['endpoint']}")
        print(f"\nTools with identifiers:")
        for tool in config['tools']:
            print(f"  - {tool['name']}:")
            print(f"    Tool ID: {tool['tool_id'] or 'Generated'}")
            print(f"    Unique ID: {tool['unique_id']}")
            print(f"    Full ID: {tool['full_identifier']}")

    return registry


def demonstrate_identifier_types():
    """Demonstrate different types of identifiers"""
    print("\n\n" + "="*50)
    print("IDENTIFIER TYPES DEMONSTRATION")
    print("="*50)

    # Example tool definitions showing different identifier scenarios
    examples = [
        {
            "scenario": "MCP Server provides tool_id",
            "tool_id": "custom_tool_123",
            "expected_unique_id": "custom_tool_123"
        },
        {
            "scenario": "No tool_id provided - generate unique_id",
            "tool_id": None,
            "expected_unique_id": "Generated from content hash"
        }
    ]

    for i, example in enumerate(examples, 1):
        print(f"\n{i}. {example['scenario']}:")
        print(f"   Input tool_id: {example['tool_id']}")
        print(f"   Result unique_id: {example['expected_unique_id']}")

    print(f"\nIdentifier Hierarchy:")
    print(f"  1. tool_id (from MCP server) -> unique_id")
    print(f"  2. Generated hash -> unique_id")
    print(f"  3. Full identifier: server_id.tool_name")
    print(f"  4. Search supports all identifier types")


def main():
    """Run all identifier tests"""
    registry = test_tool_identifiers()
    demonstrate_identifier_types()

    print("\n\n" + "="*50)
    print("SUMMARY")
    print("="*50)
    print(f"✓ Registered {len(registry.servers)} servers")

    total_tools = sum(len(server.tools) for server in registry.servers.values())
    print(f"✓ Total tools: {total_tools}")

    tools_with_server_ids = sum(
        1 for server in registry.servers.values()
        for tool in server.tools
        if tool.tool_id
    )
    print(f"✓ Tools with server-provided IDs: {tools_with_server_ids}")
    print(f"✓ Tools with generated IDs: {total_tools - tools_with_server_ids}")

    print(f"\nIdentifier Features:")
    print(f"  • tool_id: Original ID from MCP server")
    print(f"  • unique_id: Guaranteed unique identifier")
    print(f"  • full_identifier: server_id.tool_name")
    print(f"  • Search by any identifier type")
    print(f"  • Export includes all identifier types")


if __name__ == "__main__":
    main()