# ADK A2A Agent - Configuration-Driven Agent Creation

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
| `agentB.yaml` | **File Manager** | Document management and file operations | 5011 | File MCP |
| `agentC.yaml` | **Multi-Tool Assistant** | Versatile agent with multiple capabilities | 5012 | Weather + File MCPs |

## 🚀 Quick Start

### 1. Prerequisites

```bash
# Make sure MCP tool servers are running
cd ../mcp_training

# Start weather MCP tool (for agentA and agentC)
python run_http.py weather --port 8004 &

# Start file MCP tool (for agentB and agentC)  
python run_http.py file --port 8003 &
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

# File Management Agent (organized, systematic file operations)
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
  }' | jq

# Test File Manager Agent (port 5011)  
curl -X POST http://localhost:5011 \
  -H "Content-Type: application/json" \
  -d '{
    "jsonrpc": "2.0",
    "method": "message/send",
    "params": {
      "message": {"content": "Can you list the files in the current directory?"},
      "sessionId": "test-files"
    },
    "id": "1"
  }' | jq
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
      - "http://localhost:8004/mcp"  # Weather MCP
      - "http://localhost:8003/mcp"  # File MCP
    
  # Server Configuration
  server:
    default_port: 5010
    host: "0.0.0.0"
    
  # LLM Configuration  
  llm:
    model: "gemini-1.5-flash-latest"
    system_prompt: "You are a specialized AI agent..."
```

## 🛠️ Command Line Options

### Configuration Mode (Recommended)

```bash
# Load full configuration from YAML file
python adk_a2a_server.py --config agentA.yaml

# Override specific values
python adk_a2a_server.py --config agentA.yaml --port 5020 --mcp-url http://localhost:8005/mcp
```

### Legacy Mode (Individual Parameters)

```bash
# Traditional command line arguments (backward compatible)
python adk_a2a_server.py --agent-name "My Custom Agent" --port 5015 --mcp-url http://localhost:8004/mcp
```

## 🎭 Agent Personality Examples

### Weather Specialist Agent (`agentA.yaml`)

- **Personality**: Professional and informative
- **Expertise**: Meteorology and weather analysis
- **Greeting**: "Hello! I'm your Weather Specialist Agent. I can help you with weather forecasts, current conditions, temperature conversions, and climate analysis."
- **Behavior**: Focuses on providing accurate weather information

### File Management Agent (`agentB.yaml`)

- **Personality**: Organized and systematic
- **Expertise**: File system management and document organization
- **Greeting**: "Hi! I'm your File Management Agent. I can help you with file operations, document organization, reading files, and managing your file system."
- **Behavior**: Emphasizes security and asks for confirmation before changes

### Multi-Tool Assistant (`agentC.yaml`)

- **Personality**: Versatile and adaptive
- **Expertise**: General assistance with specialized tools
- **Greeting**: "Hello! I'm your Multi-Tool Assistant. I can help with weather information, file management, and a wide variety of tasks using my comprehensive toolset."
- **Behavior**: Selects appropriate tools based on user needs

## 🔧 Testing Your Configuration

### Test Agent Creation

```bash
# Test Weather Specialist
python adk_a2a_server.py --config agentA.yaml --port 5010 &

# Check agent card
curl http://localhost:5010/.well-known/agent-card.json | jq '{name, description, greeting}'

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
    "params": {"url": "http://localhost:8003/mcp"},
    "id": "add-files"
  }'

# Remove an MCP tool dynamically  
curl -X POST http://localhost:5010 \
  -H "Content-Type: application/json" \
  -d '{
    "jsonrpc": "2.0", 
    "method": "tools/remove",
    "params": {"url": "http://localhost:8003/mcp"},
    "id": "remove-files"
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

## 🚀 Summary

You can now create unlimited specialized agents with **both** configuration-driven setup **and** dynamic tool management:

```bash
# Create a Weather Specialist that can dynamically add file tools
python adk_a2a_server.py --config agentA.yaml

# Create a File Manager that can dynamically add weather tools  
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