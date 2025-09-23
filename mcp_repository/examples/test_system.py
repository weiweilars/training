#!/usr/bin/env python3
"""
Test the complete MCP repository system
"""

import sys
import json
from pathlib import Path
import asyncio
import time

# Add parent directory to path
sys.path.append(str(Path(__file__).parent.parent))

from registry.mcp_registry import MCPRegistry, MCPServer, ToolDefinition, create_example_servers
from filters.tool_filter import ToolFilter, AgentCard, create_example_agent_cards
from generators.temp_mcp_generator import TempMCPGenerator


def test_registry():
    """Test the MCP registry functionality"""
    print("="*80)
    print("TESTING MCP REGISTRY")
    print("="*80)

    # Create registry with example servers
    registry = create_example_servers()

    # List all servers
    print("\nRegistered servers:")
    for server_id in registry.list_servers():
        server = registry.get_server(server_id)
        print(f"  - {server_id}: {server.name} ({len(server.tools)} tools)")

    # Search by tool
    print("\nServers with 'schedule' tools:")
    results = registry.search_servers_by_tool("schedule")
    for server_id in results:
        print(f"  - {server_id}")

    # Search by category
    print("\nServers in 'hr' category:")
    results = registry.search_servers_by_category("hr")
    for server_id in results:
        print(f"  - {server_id}")

    return registry


def test_filtering(registry):
    """Test the tool filtering system"""
    print("\n" + "="*80)
    print("TESTING TOOL FILTERING")
    print("="*80)

    # Create filter
    filter_system = ToolFilter(registry)

    # Create test agents
    agents = create_example_agent_cards()

    for agent in agents:
        print(f"\n{'-'*60}")
        print(f"Agent: {agent.name}")
        print(f"Description: {agent.description}")

        # Get filtered tools
        matched_tools = filter_system.filter_tools_for_agent(agent, min_score=0.3)
        print(f"\nMatched tools ({len(matched_tools)}):")

        for server_id, tool, score in matched_tools[:5]:  # Show top 5
            print(f"  - {tool.name} (from {server_id}): {score:.2f}")

        # Get required servers
        required_servers = filter_system.get_required_servers(agent)
        print(f"\nRequired servers: {', '.join(required_servers)}")

    return filter_system


def test_temp_server_generation(registry):
    """Test temporary server generation"""
    print("\n" + "="*80)
    print("TESTING TEMP SERVER GENERATION")
    print("="*80)

    # Create generator
    generator = TempMCPGenerator(registry)

    # Create test agents
    agents = create_example_agent_cards()

    # Generate temp servers
    configs = []
    for agent in agents[:2]:  # Test with first 2 agents
        print(f"\n{'-'*60}")
        print(f"Creating temp server for: {agent.name}")

        try:
            config = generator.create_temp_server(agent, min_score=0.3)
            configs.append(config)

            print(f"  Server name: {config.server_name}")
            print(f"  Port: {config.port}")
            print(f"  Tools: {len(config.tools)}")
            print(f"  Directory: {config.temp_dir}")

            # List tools
            print("  Available tools:")
            for tool in config.tools[:5]:  # Show first 5 tools
                print(f"    - {tool.name}: {tool.description}")

            # Check generated files
            temp_dir = Path(config.temp_dir)
            if temp_dir.exists():
                files = list(temp_dir.iterdir())
                print(f"  Generated files ({len(files)}):")
                for f in files:
                    print(f"    - {f.name}")

        except Exception as e:
            print(f"  Error: {e}")

    return generator, configs


def test_integrated_workflow():
    """Test the complete integrated workflow"""
    print("\n" + "="*80)
    print("INTEGRATED WORKFLOW TEST")
    print("="*80)

    # Step 1: Create registry
    print("\n1. Creating MCP registry...")
    registry = create_example_servers()
    print(f"   Registered {len(registry.servers)} servers")

    # Step 2: Create an agent card
    print("\n2. Creating agent card...")
    agent = AgentCard(
        name="Comprehensive HR Agent",
        description="Handles end-to-end recruitment process including requisitions, screening, and scheduling",
        capabilities=[
            "Create job postings",
            "Screen resumes",
            "Schedule interviews",
            "Send notifications",
            "Generate reports"
        ],
        required_tools=["create_job_requisition", "screen_resume", "schedule_interview"],
        tool_categories=["hr", "recruitment", "communication", "analytics"],
        keywords=["job", "resume", "interview", "candidate", "report", "notification"]
    )
    print(f"   Agent: {agent.name}")

    # Step 3: Filter tools
    print("\n3. Filtering tools for agent...")
    filter_system = ToolFilter(registry)
    matched_tools = filter_system.filter_tools_for_agent(agent)
    print(f"   Found {len(matched_tools)} matching tools")

    # Step 4: Generate temp server
    print("\n4. Generating temporary MCP server...")
    generator = TempMCPGenerator(registry)
    config = generator.create_temp_server(agent)
    print(f"   Server created: {config.server_name}")
    print(f"   Port: {config.port}")
    print(f"   Tools: {len(config.tools)}")

    # Step 5: Show configuration
    print("\n5. Server configuration:")
    config_file = Path(config.temp_dir) / "config.json"
    if config_file.exists():
        with open(config_file, 'r') as f:
            config_data = json.load(f)
        print(json.dumps(config_data, indent=2))

    # Cleanup
    print("\n6. Cleaning up...")
    generator.cleanup_temp_server(agent.name.lower().replace(" ", "_"))
    print("   Temp server cleaned up")

    print("\n" + "="*80)
    print("WORKFLOW COMPLETE")


def main():
    """Run all tests"""
    print("\nMCP REPOSITORY SYSTEM TEST SUITE")
    print("="*80)

    # Test individual components
    registry = test_registry()
    filter_system = test_filtering(registry)
    generator, configs = test_temp_server_generation(registry)

    # Test integrated workflow
    test_integrated_workflow()

    # Cleanup
    print("\n" + "="*80)
    print("CLEANUP")
    print("="*80)
    generator.cleanup_all()
    print("All temp servers cleaned up")

    print("\n" + "="*80)
    print("ALL TESTS COMPLETE")
    print("="*80)


if __name__ == "__main__":
    main()