# ADK A2A Agent Server - Configuration-Driven Agent Creation

Create different specialized AI agents with configurable personalities, tools, and behaviors using YAML configuration files.

## 🎯 Key Feature: Configuration-Driven Agent Creation

Instead of hardcoding agent properties, you can now create different agents by simply pointing to different YAML configuration files:

```bash
# Create a Weather Specialist Agent
python adk_a2a_server.py --config agentA.yaml --port 5010

# Create a File Management Agent  
python adk_a2a_server.py --config agentB.yaml --port 5011

# Create a Multi-Tool Assistant
python adk_a2a_server.py --config agentC.yaml --port 5012
```

Each agent will have its own personality, description, tools, and behavior based on the configuration file.

## 📁 Available Agent Configurations

| Config File | Agent Type | Description | Default Port | Tools |
|-------------|------------|-------------|--------------|-------|
| `agentA.yaml` | **Weather Specialist** | Expert in weather analysis and forecasting | 5010 | Weather MCP |
| `agentB.yaml` | **Calculator Agent** | Mathematical calculations and computations | 5011 | Calculator MCP |
| `agentC.yaml` | **Multi-Tool Assistant** | Versatile agent with multiple capabilities | 5012 | Weather + Calculator MCPs |

## 🚀 Quick Start

### 1. Prerequisites

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
cd adk_a2a_toolManage_autoCreation_agent
pip install -r requirements.txt
```

### 3. Run Different Agent Types

```bash
# Weather Specialist Agent (professional, meteorology expert)
python adk_a2a_server.py --config agentA.yaml

# Calculator Agent (precise, mathematical calculations)
python adk_a2a_server.py --config agentB.yaml  

# Multi-Tool Assistant (versatile, general-purpose helper)
python adk_a2a_server.py --config agentC.yaml
```

### 4. Test Different Agent Personalities

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

# Test Calculator Agent (port 5011)  
curl -X POST http://localhost:5011 \
  -H "Content-Type: application/json" \
  -d '{
    "jsonrpc": "2.0",
    "method": "message/send",
    "params": {
      "message": {"content": "Can you calculate the square root of 144 and then multiply it by 5?"},
      "sessionId": "test-calc"
    },
    "id": "1"
  }' | python -m json.tool
```

## ⚙️ YAML Configuration Structure

### Agent Configuration Format

```yaml
agent:
  id: "agent-unique-id"
  name: "Agent Display Name"
  version: "1.0.0"
  description: "Detailed agent description for the agent card"
  
  # Agent Card Properties (shown to users)
  card:
    greeting: "Hello! I'm your specialized agent..."
    instructions: "I can help you with specific tasks..."
    
  # Agent Personality & Behavior
  personality:
    style: "professional and informative"
    tone: "helpful and knowledgeable" 
    expertise: "specific domain expertise"
    
  # Default MCP Tools
  tools:
    default_urls:
      - "http://localhost:8001/mcp"  # Weather MCP
      - "http://localhost:8002/mcp"  # Calculator MCP
    
  # Server Configuration
  server:
    default_port: 5010
    host: "0.0.0.0"
    
  # LLM Configuration  
  llm:
    model: "gemini-2.0-flash-exp"
    system_prompt: "You are a specialized AI agent..."
```

## 🛠️ Command Line Options

### Configuration Mode (Recommended)

```bash
# Load full configuration from YAML file
python adk_a2a_server.py --config agentA.yaml

# Override specific values
python adk_a2a_server.py --config agentA.yaml --port 5020 --mcp-url http://localhost:8002/mcp
```

### Legacy Mode (Individual Parameters)

```bash
# Traditional command line arguments (backward compatible)
python adk_a2a_server.py --agent-name "My Custom Agent" --port 5015 --mcp-url http://localhost:8001/mcp
```

## 🎭 Agent Personality Examples

### Weather Specialist Agent (`agentA.yaml`)

- **Personality**: Professional and informative
- **Expertise**: Meteorology and weather analysis
- **Greeting**: "Hello! I'm your Weather Specialist Agent. I can help you with weather forecasts, current conditions, temperature conversions, and climate analysis."
- **Behavior**: Focuses on providing accurate weather information

### Calculator Agent (`agentB.yaml`)

- **Personality**: Precise and analytical
- **Expertise**: Mathematics and computational analysis
- **Greeting**: "Hi! I'm your Calculator Agent. I can help you with mathematical calculations, solve equations, evaluate expressions, and perform various computational tasks."
- **Behavior**: Provides accurate mathematical results and shows calculation steps

### Multi-Tool Assistant (`agentC.yaml`)

- **Personality**: Versatile and adaptive
- **Expertise**: General assistance with specialized tools
- **Greeting**: "Hello! I'm your Multi-Tool Assistant. I can help with weather information, mathematical calculations, and a wide variety of tasks using my comprehensive toolset."
- **Behavior**: Selects appropriate tools based on user needs

## 🔧 Testing Your Configuration

### Test Agent Creation

```bash
# Test Weather Specialist
python adk_a2a_server.py --config agentA.yaml --port 5010 &

# Check agent card
curl http://localhost:5010/.well-known/agent-card.json | python -c "import sys, json; data=json.load(sys.stdin); print(json.dumps({'name': data['name'], 'description': data['description'], 'greeting': data['greeting']}, indent=2))"

# Expected output:
{
  "name": "Weather Specialist Agent",
  "description": "A specialized AI agent focused on weather analysis, forecasting, and climate-related queries. Equipped with advanced weather tools for comprehensive meteorological insights.",
  "greeting": "Hello! I'm your Weather Specialist Agent. I can help you with weather forecasts, current conditions, temperature conversions, and climate analysis."
}
```

## 🎉 Configuration Benefits

### Before (Hardcoded)
- ❌ One agent type only
- ❌ Code changes required for new agents
- ❌ No personality customization
- ❌ Fixed tool configurations

### After (Configuration-Driven)
- ✅ Multiple specialized agent types
- ✅ Create new agents with YAML files
- ✅ Rich personality customization
- ✅ Flexible tool configurations
- ✅ Easy deployment of agent fleets
- ✅ No code changes needed

## 🔧 Dynamic Tool Management

Each configuration-driven agent **also supports all dynamic tool management features** from the base toolManage agent:

### Adding/Removing Tools at Runtime

```bash
# Add a new MCP tool dynamically
curl -X POST http://localhost:5010 \
  -H "Content-Type: application/json" \
  -d '{
    "jsonrpc": "2.0",
    "method": "tools/add",
    "params": {"url": "http://localhost:8002/mcp"},
    "id": "add-calc"
  }'

# Remove an MCP tool dynamically  
curl -X POST http://localhost:5010 \
  -H "Content-Type: application/json" \
  -d '{
    "jsonrpc": "2.0", 
    "method": "tools/remove",
    "params": {"url": "http://localhost:8002/mcp"},
    "id": "remove-calc"
  }'

# List current tools
curl -X POST http://localhost:5010 \
  -H "Content-Type: application/json" \
  -d '{
    "jsonrpc": "2.0",
    "method": "tools/list", 
    "params": {},
    "id": "list-tools"
  }'

# View tool change history
curl -X POST http://localhost:5010 \
  -H "Content-Type: application/json" \
  -d '{
    "jsonrpc": "2.0",
    "method": "tools/history",
    "params": {},
    "id": "tool-history"
  }'
```

### Agent Card Auto-Update

When you add/remove tools dynamically, **the agent card automatically updates** to reflect new capabilities:

```bash
# Test dynamic agent card updates
python test_agent_card_updates.py
```

This demonstrates that configuration-driven agents have **all the same dynamic capabilities** as the base toolManage agents, plus the added benefit of YAML configuration.

## 📚 Complete A2A Protocol Compliance

Each configuration-driven agent is fully A2A protocol compliant with these endpoints:

- **GET** `/.well-known/agent-card.json` - Agent discovery with dynamic skills
- **POST** `/` - JSON-RPC 2.0 handler supporting:
  - `message/send` - Intelligent LLM-powered conversations
  - `tasks/get` - Task status retrieval
  - `tasks/cancel` - Task cancellation
  - `tools/add` - Dynamic tool addition
  - `tools/remove` - Dynamic tool removal  
  - `tools/list` - Current tool listing
  - `tools/history` - Tool change audit trail

## 🧪 Test Scripts

| Test Script | Purpose | What it Tests |
|-------------|---------|---------------|
| `test_agent_card_updates.py` | Agent card updates | Tests that agent cards update when tools are added/removed |
| `test_multi_agent_creation.py` | Multi-agent creation | Creates multiple agent types and verifies their individual configurations |

## 🧹 Cleanup Management

### Automated Cleanup Script

The `cleanup.sh` script helps manage running processes during development and testing:

```bash
# Clean up everything (MCP tools + A2A agents)
./cleanup.sh

# Clean up only MCP tool servers
./cleanup.sh tools

# Clean up only A2A agent servers  
./cleanup.sh agents

# Show help and port configuration
./cleanup.sh help
```

### Port Management

| Component | Port | Description |
|-----------|------|-------------|
| **MCP Tools** | | |
| Weather MCP | 8001 | Weather data and forecasting |
| Calculator MCP | 8002 | Mathematical calculations |
| **A2A Agents** | | |
| Weather Specialist | 5010 | Agent A (agentA.yaml) |
| Calculator Agent | 5011 | Agent B (agentB.yaml) |
| Multi-Tool Assistant | 5012 | Agent C (agentC.yaml) |

### Cleanup Features

- ✅ **Smart Process Detection** - Uses `lsof` to find processes on ports
- ✅ **Graceful Termination** - Tries `SIGTERM` first, then `SIGKILL` if needed
- ✅ **Port Verification** - Confirms ports are actually freed
- ✅ **Selective Cleanup** - Clean tools, agents, or both
- ✅ **Colorful Output** - Clear status indicators and progress

### Troubleshooting

If ports are still in use after cleanup:

```bash
# Check what's using a specific port
lsof -i :5010

# Manual kill (replace PID with actual process ID)
kill -9 <PID>

# Check all our ports at once
lsof -i :8001 -i :8002 -i :5010 -i :5011 -i :5012
```

## 🚀 Summary

You can now create unlimited specialized agents with **both** configuration-driven setup **and** dynamic tool management:

```bash
# Create a Weather Specialist that can dynamically add calculator tools
python adk_a2a_server.py --config agentA.yaml

# Create a Calculator Agent that can dynamically add weather tools  
python adk_a2a_server.py --config agentB.yaml

# All agents support runtime tool changes while maintaining their configured personalities
```

**Key Benefits:**
- ✅ **Configuration-driven creation** - No code changes for new agent types
- ✅ **Dynamic tool management** - Runtime addition/removal of MCP tools  
- ✅ **Session preservation** - Conversations continue across tool changes
- ✅ **Auto-updating agent cards** - Skills reflect current tool capabilities
- ✅ **Full A2A compliance** - All protocol requirements met
- ✅ **Personality retention** - Configured behavior maintained throughout changes

No code changes needed - just pure configuration **plus** runtime flexibility! 🎯