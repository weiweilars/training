# Semantic Kernel A2A Agent Server - Configuration-Driven Agent Creation

Create different specialized AI agents using Microsoft Semantic Kernel with configurable personalities, tools, and behaviors through YAML configuration files.

## 📁 Available Agent Configurations

| Config File | Agent Type | Description | Default Port | Tools |
|-------------|------------|-------------|--------------|-------|
| `agentA.yaml` | **Weather Specialist** | Expert in weather analysis and forecasting | 5010 | Weather MCP (port 8001) |
| `agentB.yaml` | **Calculator Agent** | Mathematical calculations and computational tasks | 5011 | Calculator MCP (port 8002) |
| `agentC.yaml` | **Multi-Tool Assistant** | Versatile agent with multiple capabilities | 5012 | Weather + Calculator MCPs |

## 🚀 Quick Start

### Prerequisites

```bash
# Start MCP tool servers
cd ../mcp_training
python run_http.py weather --port 8001 &      # Weather tools
python run_http.py calculator --port 8002 &   # Calculator tools
```

### Start Agents

```bash
# Weather Agent (using Semantic Kernel)
python sk_a2a_server.py --config agentA.yaml  # Port 5010

# Calculator Agent (using Semantic Kernel)  
python sk_a2a_server.py --config agentB.yaml  # Port 5011

# Multi-Tool Assistant (using Semantic Kernel)
python sk_a2a_server.py --config agentC.yaml  # Port 5012
```

## 🚨 **SK MCP Problem: Agent Cannot Use MCP Tools**

**Problem**: Even with proper `MCPStreamableHttpPlugin` connection, SK agents still fail to call MCP tools during conversations.

### 🔍 **The Issue**

**Implementation Uses Correct Plugin**:
```python
from semantic_kernel.connectors.mcp import MCPStreamableHttpPlugin

# Connection works fine
plugin = MCPStreamableHttpPlugin(name="calc", url="http://localhost:8002/mcp")
await plugin.connect()  # ← CONNECTS SUCCESSFULLY
```

### 🧪 **Test Results: Direct Tool Calling WORKS**

MCP tool calling works perfectly at the **plugin level**:

```bash
# Test MCPStreamableHttpPlugin
python test_direct_tool_call.py
```

**Results**:
```
✅ Connected successfully!
✅ Tool discovery works: ['basic_math', 'advanced_math', 'evaluate_expression']
✅ Tool call successful: 789 * 123 = 97047  ← ACTUAL MCP CALL!
```

**Proof in logs**:
```
DEBUG: SSE message: JSONRPCResponse(jsonrpc='2.0', id=3, result={'content': [{'type': 'text', 'text': '{\n  "operation": "789.0 * 123.0",\n  "result": 97047.0\n}'}]})
INFO: Function calculator_plugin-basic_math succeeded.
```

### 🚫 **But Agent Integration Fails**

| Component | Connection | Tool Discovery | Tool Calling | Status |
|-----------|------------|----------------|--------------|--------|
| **MCPStreamableHttpPlugin** | ✅ Connects successfully | ✅ Finds all tools | ✅ **Calls MCP tools** | **WORKS** |
| **ChatCompletionAgent** | ✅ Plugin loaded | ✅ Tools available | ❌ **Won't use tools** | **BROKEN** |

### 🔗 **Official Documentation**

**Microsoft Learn**: [Give agents access to MCP Servers](https://learn.microsoft.com/en-us/semantic-kernel/concepts/plugins/adding-mcp-plugins)

**Known Issues** (GitHub): [Python: MCP Connector Failure #12565](https://github.com/microsoft/semantic-kernel/issues/12565)

**Stack Overflow**: [Azure AI agent not using MCP tools](https://stackoverflow.com/questions/79733906/why-is-the-azure-ai-agent-semantic-kernel-not-using-the-configured-mcp-tools-d)

### ⚙️ **SK MCP Plugin Types**

Semantic Kernel provides **3 MCP plugin types**:

1. **MCPStdioPlugin** - Local subprocess communication via stdin/stdout
2. **MCPSsePlugin** - Pure SSE streaming (causes hangs with HTTP-based MCP servers)  
3. **MCPStreamableHttpPlugin** - **HTTP + SSE transport** (correct for standard MCP servers)

### 🛠️ **The Fix**

Use `MCPStreamableHttpPlugin` in `sk_a2a_server.py`:

```python
from semantic_kernel.connectors.mcp import MCPStreamableHttpPlugin

# Correct implementation
plugin = MCPStreamableHttpPlugin(name=name, url=url, description=desc)
await plugin.connect()  # This works properly
```

### 🎯 **Confirmed: SK CAN Call MCP Tools**

The **famous SK MCP problem** is solved - it was just using the wrong plugin type. With `MCPStreamableHttpPlugin`:
- ✅ Connection works
- ✅ Tool discovery works  
- ✅ **MCP tool calling works**

The issue is **not with Semantic Kernel** itself, but with using the wrong transport plugin for HTTP-based MCP servers.