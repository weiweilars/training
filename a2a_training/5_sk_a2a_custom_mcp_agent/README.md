# SK A2A Agent - Semantic Kernel Configuration-Driven Agent Creation

Create different specialized AI agents using Microsoft Semantic Kernel with configurable personalities, tools, and behaviors through YAML configuration files.

## 🎯 Key Feature: Semantic Kernel-Powered Dynamic Agents

This implementation provides the **exact same functionality** as the ADK version but powered by **Microsoft Semantic Kernel** instead of Google ADK:

- ✅ **Configuration-driven agent creation** via YAML files
- ✅ **Dynamic tool management** - add/remove MCP tools at runtime
- ✅ **Session preservation** across tool changes (improved for SK)
- ✅ **Auto-updating agent cards** based on available tools
- ✅ **Full A2A protocol compliance**
- ✅ **Multiple LLM support** (OpenAI, Azure OpenAI)

## 🆚 SK vs ADK Implementation

| Feature | ADK Version | SK Version |
|---------|-------------|------------|
| **LLM Provider** | Google Gemini | OpenAI/Azure |
| **Framework** | Google ADK | Microsoft Semantic Kernel |
| **Session Management** | ADK Sessions | Enhanced SK ChatHistory |
| **Tool Integration** | ADK MCP Toolset | SK Plugin System |
| **Configuration** | YAML ✅ | YAML ✅ |
| **Dynamic Tools** | ✅ | ✅ |
| **A2A Compliance** | ✅ | ✅ |
| **Agent Cards** | ✅ | ✅ |

## 📁 Available Agent Configurations

The same YAML configurations work with both ADK and SK versions:

| Config File | Agent Type | Description | Default Port | Tools |
|-------------|------------|-------------|--------------|-------|
| `agentA.yaml` | **Weather Specialist** | Expert in weather analysis and forecasting | 5010 | Weather MCP |
| `agentB.yaml` | **Calculator Specialist** | Mathematical computations and calculations | 5011 | Calculator MCP |
| `agentC.yaml` | **Multi-Tool Assistant** | Versatile agent with multiple capabilities | 5012 | Weather + Calculator MCPs |

## 🚀 Quick Start

### 1. Prerequisites

#### Set up LLM Provider (Choose One)

**Option A: OpenAI**
```bash
# Create .env file with OpenAI credentials
echo "OPENAI_API_KEY=your_openai_api_key_here" > .env
```

**Option B: Azure OpenAI**
```bash
# Create .env file with Azure OpenAI credentials
cat > .env << EOF
AZURE_OPENAI_API_KEY=your_azure_api_key_here
AZURE_OPENAI_ENDPOINT=https://your-resource.openai.azure.com/
AZURE_OPENAI_DEPLOYMENT_NAME=your-deployment-name
EOF
```


#### Start MCP Tool Servers
```bash
# Make sure MCP tool servers are running
cd ../mcp_training

# Start weather MCP tool (for agentA and agentC)
python run_http.py weather --port 8001 &

# Start calculator MCP tool (for agentB and agentC)  
python run_http.py calculator --port 8002 &
```

### 2. Install Dependencies

```bash
cd 5_sk_a2a_custom_mcp_agent
pip install -r requirements.txt
```

### 3. Run Different Agent Types

```bash
# Weather Specialist Agent (using Semantic Kernel)
python sk_a2a_server.py --config agentA.yaml

# Calculator Specialist Agent (using Semantic Kernel)
python sk_a2a_server.py --config agentB.yaml  

# Multi-Tool Assistant (using Semantic Kernel)
python sk_a2a_server.py --config agentC.yaml
```

### 4. Test Agent Functionality

```bash
# Test Weather Specialist Agent (port 5010)
curl -X POST http://localhost:5010 \
  -H "Content-Type: application/json" \
  -d '{
    "jsonrpc": "2.0",
    "method": "message/send", 
    "params": {
      "message": {"content": "What is the weather like in Tokyo?"},
      "sessionId": "test-weather"
    },
    "id": "1"
  }' | python -m json.tool

# Test dynamic calculator tool addition
curl -X POST http://localhost:5010 \
  -H "Content-Type: application/json" \
  -d '{
    "jsonrpc": "2.0",
    "method": "tools/add",
    "params": {"url": "http://localhost:8002/mcp"},
    "id": "add-calculator-tools"
  }' | python -m json.tool
```

## 🔧 Advanced Multi-Tool Testing

Test the Multi-Tool Assistant (agentC) with complex queries that require multiple tools working together:

### Start Multi-Tool Assistant (AgentC)
```bash
# Start agentC with both weather and file tools
python sk_a2a_server.py --config agentC.yaml
```

### Add Calculator Tools Dynamically
```bash
# Add calculator tools to enable math operations
curl -X POST http://localhost:5012 \
  -H "Content-Type: application/json" \
  -d '{
    "jsonrpc": "2.0",
    "method": "tools/add",
    "params": {"url": "http://localhost:8002/mcp"},
    "id": "add-calculator"
  }' | python -m json.tool
```

### Complex Multi-Tool Queries

#### Weather + Math Average Calculation
```bash
# Get temperatures from two cities and calculate average
curl -X POST http://localhost:5012 \
  -H "Content-Type: application/json" \
  -d '{
    "jsonrpc": "2.0",
    "method": "message/send", 
    "params": {
      "message": {"content": "Get the weather temperatures for both Paris and Tokyo, then use basic math to calculate the average temperature between them"},
      "sessionId": "multi-tool-test"
    },
    "id": "weather-math-query"
  }' | python -m json.tool
```

#### Weather + Temperature Conversion + Math
```bash
# Get weather, convert temperature, and perform calculation
curl -X POST http://localhost:5012 \
  -H "Content-Type: application/json" \
  -d '{
    "jsonrpc": "2.0",
    "method": "message/send", 
    "params": {
      "message": {"content": "Get the current temperature in London, then convert it to Fahrenheit and add 10 degrees to the result"},
      "sessionId": "complex-test"
    },
    "id": "complex-multi-tool"
  }' | python -m json.tool
```

These queries will demonstrate that the agent:
1. **Uses weather tools** to fetch real temperature data
2. **Uses calculator tools** to perform mathematical operations  
3. **Combines results** intelligently in natural language responses

Expected behavior: The agent makes actual HTTP calls to both MCP servers and combines their results.

## 💡 Semantic Kernel Specific Features

### Enhanced Session Management

The SK implementation includes improved session management:

```python
# Sessions are maintained using SK's ChatHistory
# Each session preserves:
- Complete conversation history
- Tool usage context
- User preferences
- Session metadata
```

### Plugin System Integration

MCP tools are integrated as SK plugins:

```python
# Each MCP server becomes an SK plugin
# Tools are registered as kernel functions
# Automatic function calling support
```

### Multiple LLM Support

Unlike ADK (Gemini only), SK supports multiple providers:

```yaml
# In your agent YAML config:
llm:
  model: "gpt-3.5-turbo"        # OpenAI
  # model: "gpt-4"               # OpenAI GPT-4
  # model: "your-deployment"     # Azure OpenAI
```

## 🧪 Testing

### Test Agent Card Updates
```bash
# Verify agent cards update when tools change
python test_agent_card_updates.py
```

### Test Multi-Agent Creation
```bash
# Test creating multiple agents with different configs
python test_multi_agent_creation.py
```

## 📚 API Endpoints

Same A2A protocol compliance as ADK version:

- **GET** `/.well-known/agent-card.json` - Agent discovery
- **POST** `/` - JSON-RPC 2.0 handler:
  - `message/send` - Send messages to agent
  - `tasks/get` - Get task status
  - `tasks/cancel` - Cancel tasks
  - `tools/add` - Add MCP tools dynamically
  - `tools/remove` - Remove MCP tools
  - `tools/list` - List current tools
  - `tools/history` - View tool change history

## 🔍 Troubleshooting

### Semantic Kernel Installation Issues

```bash
# Ensure you have the latest SK version
pip install --upgrade semantic-kernel

# For Azure OpenAI support
pip install semantic-kernel[azure]
```

### LLM Provider Configuration

```bash
# Check environment variables
python -c "import os; print('OPENAI_API_KEY' in os.environ)"

# Test SK connection
python -c "from semantic_kernel import Kernel; k = Kernel(); print('SK initialized')"
```

### Session Persistence

The SK implementation maintains sessions better than the reference implementation by using:
- `ChatHistory` objects per session
- Proper context preservation
- Session metadata tracking

### Port Cleanup

Before starting fresh tests, clean up all background processes and ports:

```bash
# Kill all Python processes (MCP servers and agents)
pkill -f "python.*run_http.py"
pkill -f "python.*sk_a2a_server.py"

# Alternative: Kill specific processes by port
# Find processes using ports
lsof -ti:5010,5011,5012,8003,8004,8005 | xargs -r kill -9

# Verify all ports are free
lsof -i:5010,5011,5012,8003,8004,8005

# Start clean - restart MCP servers
cd ../mcp_training
python run_http.py weather --port 8001 &
python run_http.py calculator --port 8002 &

# Then start agents
cd ../5_sk_a2a_custom_mcp_agent
python sk_a2a_server.py --config agentA.yaml &  # Port 5010
python sk_a2a_server.py --config agentB.yaml &  # Port 5011  
python sk_a2a_server.py --config agentC.yaml &  # Port 5012
```

## 🎉 Benefits of SK Implementation

1. **Provider Flexibility**: Use OpenAI, Azure, or other LLMs
2. **Better Session Management**: Enhanced conversation context preservation
3. **Plugin Ecosystem**: Leverage SK's extensive plugin system
4. **Enterprise Ready**: Azure AD integration, security features
5. **Active Development**: Microsoft's ongoing SK improvements

## 🔗 Comparison with ADK Version

Both implementations provide:
- ✅ Same YAML configuration format
- ✅ Same dynamic tool management
- ✅ Same A2A protocol compliance
- ✅ Same test scripts
- ✅ Same agent personalities

Choose based on your needs:
- **Use ADK version**: If you prefer Google Gemini and have Google Cloud infrastructure
- **Use SK version**: If you prefer OpenAI/Azure and want Microsoft ecosystem integration

## 🚀 Summary

This Semantic Kernel implementation provides **complete feature parity** with the ADK version while offering:

- **More LLM choices** (OpenAI, Azure, etc.)
- **Better session management** through SK's ChatHistory
- **Enterprise integration** options
- **Same ease of use** with YAML configurations

Create unlimited specialized agents with configuration files and enjoy the flexibility of Microsoft's Semantic Kernel! 🎯