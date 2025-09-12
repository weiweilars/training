# SK A2A Agent - Semantic Kernel Agent-to-Agent Communication

Create specialized AI agents using Microsoft Semantic Kernel that can coordinate and communicate with other A2A agents to provide comprehensive, multi-agent solutions.

## 🎯 Key Feature: Agent-to-Agent Communication

This implementation transforms the MCP tool-calling paradigm into **A2A agent-to-agent communication**:

- ✅ **Configuration-driven agent creation** via YAML files
- ✅ **Dynamic agent management** - add/remove A2A agents at runtime
- ✅ **Session preservation** across agent topology changes
- ✅ **Auto-updating agent cards** based on connected agents
- ✅ **Full A2A protocol compliance**
- ✅ **Multi-agent coordination** and response synthesis
- ✅ **Cross-domain expertise** through agent specialization

## 🆚 Agent-to-Agent vs MCP Tool Approach

| Feature | MCP Tools Version | A2A Agent Version |
|---------|-------------------|-------------------|
| **Communication** | Tool Calling | Agent-to-Agent Messages |
| **Discovery** | Tool Schema | Agent Card & Capabilities |
| **Endpoints** | `tools/*` | `agents/*` |
| **Integration** | Function Plugins | Agent Communication |
| **Scalability** | Limited by Tools | Network of Agents |
| **Intelligence** | Tool Functions | Full AI Agents |
| **Coordination** | Sequential | Collaborative |

## 🤖 Agent Coordination Patterns

### Coordinator Agent Pattern
The main agent acts as a coordinator, routing requests to specialized agents:

```
User Request → Coordinator Agent → Weather Agent
                                → Task Agent  
                                → Research Agent
                                ↓
             Synthesized Response ← Coordinator Agent
```

### Multi-Domain Expertise
Each connected agent brings specialized capabilities:
- **Weather Agents**: Meteorological analysis and forecasting
- **Task Agents**: Project management and scheduling
- **Research Agents**: Information gathering and analysis
- **Data Agents**: Statistical analysis and visualization

## 📁 Available Agent Configurations

| Config File | Agent Type | Description | Default Port | Connected Agents |
|-------------|------------|-------------|--------------|------------------|
| `agentA.yaml` | **Weather Coordinator** | Coordinates weather-related queries | 5020 | Weather & Climate Agents |
| `agentB.yaml` | **Task Coordinator** | Manages productivity and projects | 5021 | Project & Schedule Agents |
| `agentC.yaml` | **Multi-Domain Coordinator** | Handles diverse, cross-domain queries | 5022 | Weather, Task, Research & Data Agents |

## 🚀 Quick Start

### 1. Prerequisites

#### Set up LLM Provider
```bash
# Create .env file with OpenAI credentials
echo "OPENAI_API_KEY=your_openai_api_key_here" > .env
```

#### Start Specialized A2A Agents
You need to have other A2A agents running that this coordinator can connect to:

```bash
# Example: Start specialized weather agent (port 5010)
cd ../5_sk_a2a_custom_mcp_agent
python sk_a2a_server.py --config agentA.yaml &

# Example: Start specialized calculator agent (port 5011) 
python sk_a2a_server.py --config agentB.yaml &

# Example: Start specialized multi-tool agent (port 5012)
python sk_a2a_server.py --config agentC.yaml &
```

### 2. Install Dependencies

```bash
cd 6_sk_a2a_agent_to_agent
pip install -r requirements.txt
```

### 3. Run Coordinator Agents

```bash
# Weather Coordinator Agent
python sk_a2a_server.py --config agentA.yaml

# Task Management Coordinator Agent
python sk_a2a_server.py --config agentB.yaml

# Multi-Domain Coordinator Agent
python sk_a2a_server.py --config agentC.yaml
```

### 4. Test Agent-to-Agent Communication

```bash
# Test Weather Coordinator (routes to weather agents)
curl -X POST http://localhost:5020 \
  -H "Content-Type: application/json" \
  -d '{
    "jsonrpc": "2.0",
    "method": "message/send",
    "params": {
      "message": {"content": "What is the weather forecast for Tokyo and how does it compare to seasonal averages?"},
      "sessionId": "weather-coordination-test"
    },
    "id": "1"
  }' | python -m json.tool

# Test dynamic agent addition
curl -X POST http://localhost:5020 \
  -H "Content-Type: application/json" \
  -d '{
    "jsonrpc": "2.0",
    "method": "agents/add",
    "params": {"url": "http://localhost:5015"},
    "id": "add-data-agent"
  }' | python -m json.tool
```

## 🔧 Dynamic Agent Management

### Adding/Removing Agents at Runtime

```bash
# Add a new A2A agent dynamically
curl -X POST http://localhost:5020 \
  -H "Content-Type: application/json" \
  -d '{
    "jsonrpc": "2.0",
    "method": "agents/add",
    "params": {"url": "http://localhost:5016"},
    "id": "add-analysis-agent"
  }'

# Remove an A2A agent dynamically  
curl -X POST http://localhost:5020 \
  -H "Content-Type: application/json" \
  -d '{
    "jsonrpc": "2.0",
    "method": "agents/remove", 
    "params": {"url": "http://localhost:5016"},
    "id": "remove-analysis-agent"
  }'

# List connected agents
curl -X POST http://localhost:5020 \
  -H "Content-Type: application/json" \
  -d '{
    "jsonrpc": "2.0",
    "method": "agents/list",
    "params": {},
    "id": "list-agents"
  }'
```

## 💡 Agent Coordination Features

### Intelligent Routing
The coordinator agent analyzes user requests and routes them to the most appropriate specialized agents:

```yaml
# In agent configuration
llm:
  system_prompt: "You work with specialized A2A agents. When users ask questions, intelligently coordinate with the most relevant agents to provide comprehensive responses."
```

### Response Synthesis  
Responses from multiple agents are synthesized into coherent, comprehensive answers:

```python
# The coordinator combines multiple agent responses
weather_response = await weather_agent.send_message("Get Tokyo forecast")
climate_response = await climate_agent.send_message("Get Tokyo seasonal data") 
# Synthesize into comprehensive weather analysis
```

### Session Context Preservation
Each agent maintains conversation context while allowing dynamic topology changes:

```python
# Sessions preserved across agent network changes
session_data = self._sessions[session_id]
chat_history = session_data["chat_history"]
```

## 🌐 Agent Network Topologies

### Hub-and-Spoke (Coordinator Pattern)
```
      Weather Agent
            ↑
User ↔ Coordinator ↔ Task Agent
            ↓
      Research Agent
```

### Mesh Network (Peer-to-Peer)
```
Weather ↔ Climate
   ↑         ↓
User ↔ Coordinator ↔ Research
   ↓         ↑
Task ↔ Analysis
```

## 📚 API Endpoints

Enhanced A2A protocol with agent management:

- **GET** `/.well-known/agent-card.json` - Agent discovery with connected agents
- **POST** `/` - JSON-RPC 2.0 handler:
  - `message/send` - Send messages (routed through connected agents)
  - `tasks/get` - Get task status
  - `tasks/cancel` - Cancel tasks
  - `agents/add` - Add A2A agents dynamically
  - `agents/remove` - Remove A2A agents
  - `agents/list` - List connected agents
  - `agents/history` - View agent topology changes

## 🔍 Agent Discovery Process

### 1. Agent Card Fetching
```python
# Fetch agent capabilities
agent_card = await client.get(f"{agent_url}/.well-known/agent-card.json")
capabilities = agent_card.get("skills", [])
```

### 2. Capability Registration  
```python
# Register agent capabilities as kernel functions
for capability in capabilities:
    kernel_func = create_agent_function(capability)
    plugin_functions[capability["name"]] = kernel_func
```

### 3. Dynamic Updates
```python
# Agent cards update when topology changes
if success:
    await agent.discover_a2a_agents()
    logger.info(f"Agent card updated after adding agent: {agent_url}")
```

## 🎯 Use Cases

### 1. Multi-Domain Research
"Research climate change impacts on agriculture in Japan"
- Routes to: Weather Agent + Research Agent + Data Agent
- Synthesizes: Weather patterns + Research papers + Statistical analysis

### 2. Project Management
"Plan a software release considering weather impacts on data center operations"
- Routes to: Task Agent + Weather Agent + Infrastructure Agent  
- Synthesizes: Project timeline + Weather forecast + Infrastructure planning

### 3. Complex Analysis
"Analyze sales performance correlation with weather patterns"
- Routes to: Data Agent + Weather Agent + Analysis Agent
- Synthesizes: Sales data + Weather data + Statistical correlation

## 🏗️ Architecture Benefits

1. **Scalable Intelligence**: Add specialized agents without code changes
2. **Domain Expertise**: Each agent focuses on specific capabilities  
3. **Fault Tolerance**: System continues if individual agents fail
4. **Load Distribution**: Workload spread across multiple agents
5. **Specialized Optimization**: Each agent optimized for its domain
6. **Network Effects**: Agents can learn from each other's outputs

## 🔧 Configuration Examples

### Weather Coordinator Agent
```yaml
agents:
  default_urls:
    - "http://localhost:5010"  # Weather Specialist
    - "http://localhost:5011"  # Climate Analysis
```

### Multi-Domain Coordinator
```yaml
agents:
  default_urls:
    - "http://localhost:5010"  # Weather
    - "http://localhost:5012"  # Tasks  
    - "http://localhost:5014"  # Research
    - "http://localhost:5015"  # Data Analysis
```

## 🚀 Summary

This A2A agent-to-agent implementation provides:

- **Agent Network Orchestration** instead of tool calling
- **Multi-agent coordination** for comprehensive solutions  
- **Dynamic topology management** with session preservation
- **Specialized domain expertise** through agent coordination
- **Scalable intelligence** that grows with your agent network

Create unlimited specialized agent networks with configuration files and harness the power of collaborative AI agents! 🤖🌐

## 🔍 Troubleshooting

### Port Cleanup

Before starting fresh tests, clean up all background processes and ports:

```bash
# Kill all Python processes (A2A agents and underlying MCP servers)
pkill -f "python.*sk_a2a_server.py"
pkill -f "python.*run_http.py"

# Alternative: Kill specific processes by port
# Find processes using coordination ports and underlying service ports
lsof -ti:5020,5021,5022,5010,5011,5012,8003,8004,8005 | xargs -r kill -9

# Verify all ports are free
lsof -i:5020,5021,5022,5010,5011,5012,8003,8004,8005

# Start clean - first restart underlying MCP servers if needed
cd ../mcp_training
python run_http.py weather --port 8001 &
python run_http.py calculator --port 8002 &

# Then start underlying A2A agents
cd ../5_sk_a2a_custom_mcp_agent
python sk_a2a_server.py --config agentA.yaml &  # Port 5010
python sk_a2a_server.py --config agentB.yaml &  # Port 5011
python sk_a2a_server.py --config agentC.yaml &  # Port 5012

# Finally start coordinator agents
cd ../6_sk_a2a_agent_to_agent
python sk_a2a_server.py --config agentA.yaml &  # Port 5020
python sk_a2a_server.py --config agentB.yaml &  # Port 5021
python sk_a2a_server.py --config agentC.yaml &  # Port 5022
```

## 🔗 Next Steps

1. **Create Specialized Agents**: Build domain-specific A2A agents
2. **Design Agent Networks**: Plan coordination patterns for your use case
3. **Implement Custom Protocols**: Extend agent communication patterns  
4. **Scale Horizontally**: Deploy agents across multiple servers
5. **Add Intelligence**: Implement agent learning and adaptation