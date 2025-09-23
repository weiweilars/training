# MCP Repository System

A dynamic MCP (Model Context Protocol) server management system that creates temporary MCP servers with filtered tools based on agent descriptions and requirements.

## Features

- **MCP Server Registry**: Centralized repository for all available MCP servers and their tools
- **Tool Filtering**: Intelligent matching of tools to agent requirements based on descriptions, categories, and keywords
- **Temporary Server Generation**: Dynamic creation of MCP servers with only the relevant tools for specific agents
- **Agent Cards**: YAML-based agent definitions with capabilities and tool requirements

## Architecture

```
mcp_repository/
├── registry/           # MCP server registry
│   └── mcp_registry.py
├── filters/           # Tool filtering system
│   └── tool_filter.py
├── generators/        # Temporary server generator
│   └── temp_mcp_generator.py
├── temp_servers/      # Generated temporary servers
├── examples/          # Example agent cards and tests
│   ├── test_system.py
│   └── sample_agent_cards.yaml
└── README.md
```

## Key Components

### 1. MCP Registry (`registry/mcp_registry.py`)

Manages a centralized repository of MCP servers and their tools:

- `MCPServer`: Represents an MCP server with tools and metadata
- `ToolDefinition`: Defines individual tools with categories and keywords
- `MCPRegistry`: Central registry for managing servers

### 2. Tool Filter (`filters/tool_filter.py`)

Intelligently matches tools to agent requirements:

- Relevance scoring based on:
  - Direct tool name matches
  - Category alignment
  - Keyword matching
  - Description analysis
- Generates filtered tool configurations for agents

### 3. Temp MCP Generator (`generators/temp_mcp_generator.py`)

Creates temporary MCP servers with filtered tools:

- Generates Python MCP server code
- Creates HTTP wrappers for easy access
- Manages temporary server lifecycle
- Automatic port allocation

## Usage

### 1. Create MCP Registry

```python
from registry.mcp_registry import MCPRegistry, MCPServer, ToolDefinition

registry = MCPRegistry()

# Register a server
hr_tools = [
    ToolDefinition(
        name="create_job_requisition",
        description="Create a new job requisition",
        categories=["hr", "recruitment"],
        keywords=["job", "position", "hiring"]
    )
]

hr_server = MCPServer(
    name="HR Recruitment Tools",
    description="MCP server for HR operations",
    version="1.0.0",
    tools=hr_tools,
    port=8100
)

registry.register_server("hr_recruitment", hr_server)
```

### 2. Define Agent Card

```python
from filters.tool_filter import AgentCard

agent = AgentCard(
    name="Job Requisition Agent",
    description="Manages job requisitions and postings",
    capabilities=["Create job requisitions", "Publish postings"],
    required_tools=["create_job_requisition"],
    tool_categories=["hr", "recruitment"],
    keywords=["job", "requisition", "posting"]
)
```

### 3. Generate Temporary Server

```python
from generators.temp_mcp_generator import TempMCPGenerator

generator = TempMCPGenerator(registry)
config = generator.create_temp_server(agent)

print(f"Server created on port {config.port}")
print(f"Available tools: {[t.name for t in config.tools]}")
```

## Testing

Run the complete test suite:

```bash
cd exploration/mcp_repository
python examples/test_system.py
```

## Agent Card Format

Agent cards can be defined in YAML:

```yaml
name: Interview Scheduling Agent
description: Coordinates and schedules interviews
capabilities:
  - Schedule interviews
  - Send invitations
required_tools:
  - schedule_interview
  - send_notification
tool_categories:
  - hr
  - scheduling
  - communication
keywords:
  - interview
  - schedule
  - calendar
metadata:
  team: recruitment
```

## Benefits

1. **Resource Efficiency**: Agents only get access to relevant tools
2. **Security**: Limited tool exposure based on agent requirements
3. **Scalability**: Dynamic server creation as needed
4. **Flexibility**: Easy to add new servers and tools to the registry
5. **Intelligence**: Smart matching based on descriptions and keywords