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
User Request → Coordinator Agent → Weather Agent (AgentA)
                                → Calculator Agent (AgentB)
                                ↓
             Synthesized Response ← Coordinator Agent
```

### Multi-Domain Expertise
Each connected agent brings specialized capabilities:
- **Weather Agent (AgentA)**: Meteorological analysis and forecasting
- **Calculator Agent (AgentB)**: Mathematical computations and analysis
- **Coordinator Agent**: Routes requests and synthesizes responses from specialized agents

## 📁 Available Agent Configurations

| Config File | Agent Type | Description | Default Port | Connected Agents |
|-------------|------------|-------------|--------------|------------------|
| `dynamic_coordinator.yaml` | **Dynamic Coordinator** | Self-documenting agent that adapts description based on connected sub-agents | 5025 | Dynamically discovered agents |

This configuration demonstrates the intelligent dynamic agent card generation using an external summarization agent.

## 🚀 Quick Start

### Prerequisites
```bash
# 1. Set up LLM Provider (create .env file with OpenAI credentials)
echo "OPENAI_API_KEY=your_openai_api_key_here" > .env

# 2. Install Dependencies
pip install -r requirements.txt
```

### Dependency Architecture
**Important**: The system has a layered dependency structure:
1. **MCP Tools** (ports 8001, 8002) - Foundation layer
   - Weather tool on 8001
   - Calculator tool on 8002
2. **Specialized Agents** (ports 5010, 5011) - Each uses specific MCP tools
   - AgentA on 5010 (Weather Specialist) → Weather MCP
   - AgentB on 5011 (Calculator Agent) → Calculator MCP
3. **Summarization Agent** (port 5030) - Meta-services
4. **Coordinator Agent** (port 5025) - Orchestrates specialized agents

### Quick Start

Follow the dependency order for proper system startup:

```bash
# 1. Start MCP tool servers (foundation layer)
cd ../../mcp_training
python run_http.py weather --port 8001 &      # Weather tools
python run_http.py calculator --port 8002 &   # Calculator tools

# 2. Start specialized agents (capability layer)
cd ../a2a_training/5_sk_a2a_custom_mcp_agent
python sk_a2a_server.py --config agentA.yaml &             # Port 5010 (Weather)
python sk_a2a_server.py --config agentB.yaml &             # Port 5011 (Calculator)
python sk_a2a_server.py --config summarization_agent.yaml & # Port 5030 (Summarizer)

# 3. Start coordinator (orchestration layer)
cd ../6_sk_a2a_agent_to_agent
python sk_a2a_server.py --config dynamic_coordinator.yaml & # Port 5025

# 4. Test the system
python test_dynamic_agent_card.py
```

**Cleanup:**
```bash
./cleanup.sh all          # Clean everything
./cleanup.sh agents       # Clean agents only
./cleanup.sh tools        # Clean MCP tools only
```
```

## 💬 Multi-Agent Message Examples

The coordinator demonstrates true multi-agent orchestration by routing requests to specialized agents and synthesizing their responses.

### Example 1: Weather Query (Single Agent)
```bash
# Simple weather query - routed to AgentA (Weather Specialist)
curl -X POST http://localhost:5025 \
  -H "Content-Type: application/json" \
  -d '{
    "jsonrpc": "2.0",
    "method": "message/send",
    "params": {
      "message": {"content": "What is the current weather in Tokyo?"},
      "sessionId": "weather-test"
    },
    "id": "weather-query"
  }' | python -m json.tool
```

### Example 2: After Adding Calculator Agent
```bash
# First, add the calculator agent
curl -X POST http://localhost:5025 \
  -H "Content-Type: application/json" \
  -d '{
    "jsonrpc": "2.0",
    "method": "agents/add",
    "params": {"url": "http://localhost:5011"},
    "id": "add-calc"
  }' | python -m json.tool

# Now test multi-agent coordination
curl -X POST http://localhost:5025 \
  -H "Content-Type: application/json" \
  -d '{
    "jsonrpc": "2.0",
    "method": "message/send",
    "params": {
      "message": {"content": "Get the temperature in Tokyo and London, then calculate the average temperature between them"},
      "sessionId": "multi-agent-test"
    },
    "id": "weather-math-query"
  }' | python -m json.tool
```

### Example 3: Complex Multi-Step Coordination
```bash
# Complex query requiring both weather data and mathematical computation
curl -X POST http://localhost:5025 \
  -H "Content-Type: application/json" \
  -d '{
    "jsonrpc": "2.0",
    "method": "message/send",
    "params": {
      "message": {"content": "If the temperature in Paris is currently above 20°C, calculate how much warmer it is compared to 15°C, and convert the difference to Fahrenheit"},
      "sessionId": "complex-coordination"
    },
    "id": "complex-query"
  }' | python -m json.tool
```

### Example 4: Testing Agent Capabilities Evolution
```bash
# Check what the coordinator can do initially (weather only)
curl -X POST http://localhost:5025 \
  -H "Content-Type: application/json" \
  -d '{
    "jsonrpc": "2.0", 
    "method": "message/send",
    "params": {
      "message": {"content": "What capabilities do you have? List what kinds of questions you can help me with."},
      "sessionId": "capability-test"
    },
    "id": "capabilities-before"
  }' | python -m json.tool

# Add calculator agent
curl -X POST http://localhost:5025 \
  -H "Content-Type: application/json" \
  -d '{
    "jsonrpc": "2.0",
    "method": "agents/add", 
    "params": {"url": "http://localhost:5011"},
    "id": "add-calculator"
  }' | python -m json.tool

# Check capabilities again (weather + math)
curl -X POST http://localhost:5025 \
  -H "Content-Type: application/json" \
  -d '{
    "jsonrpc": "2.0",
    "method": "message/send", 
    "params": {
      "message": {"content": "What capabilities do you have now? How have your abilities expanded?"},
      "sessionId": "capability-test"
    },
    "id": "capabilities-after"
  }' | python -m json.tool
```

### Example 5: Demonstration of Agent Coordination
```bash
# Query that requires coordination between multiple agents
curl -X POST http://localhost:5025 \
  -H "Content-Type: application/json" \
  -d '{
    "jsonrpc": "2.0",
    "method": "message/send",
    "params": {
      "message": {"content": "Compare the weather in 3 different cities and tell me which city has a temperature closest to 22 degrees Celsius. Show your calculation steps."},
      "sessionId": "coordination-demo"
    },
    "id": "coordination-query"
  }' | python -m json.tool
```

### Expected Coordinator Behavior

The coordinator should demonstrate:

1. **Intelligent Routing**: 
   - Weather queries → AgentA (Weather Specialist)
   - Math queries → AgentB (Calculator Agent) 
   - Complex queries → Both agents with synthesis

2. **Response Synthesis**:
   - Combines weather data from AgentA with calculations from AgentB
   - Provides coherent, comprehensive answers
   - Shows understanding of multi-step processes

3. **Dynamic Capability Awareness**:
   - Adapts responses based on currently connected agents
   - Explains capability changes when agents are added/removed
   - Maintains conversation context across topology changes

4. **Agent Card Updates**:
   - Description automatically updates when agents are added/removed
   - Skills reflect current connected agent capabilities
   - Greeting adapts to available functionalities

```

## 🔧 Dynamic Agent Management

### Adding/Removing Agents at Runtime

```bash
# Add agentB (Calculator Agent) dynamically (and watch description update!)
# Note: AgentA (Weather) is already connected by default
curl -X POST http://localhost:5025 \
  -H "Content-Type: application/json" \
  -d '{
    "jsonrpc": "2.0",
    "method": "agents/add",
    "params": {"url": "http://localhost:5011"},
    "id": "add-calculator-agent"
  }'

# Remove the default weather agent dynamically
curl -X POST http://localhost:5025 \
  -H "Content-Type: application/json" \
  -d '{
    "jsonrpc": "2.0",
    "method": "agents/remove", 
    "params": {"url": "http://localhost:5010"},
    "id": "remove-weather-agent"
  }'

# Re-add the weather agent back
curl -X POST http://localhost:5025 \
  -H "Content-Type: application/json" \
  -d '{
    "jsonrpc": "2.0",
    "method": "agents/add",
    "params": {"url": "http://localhost:5010"},
    "id": "re-add-weather-agent"
  }'

# List connected agents
curl -X POST http://localhost:5025 \
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

### Get Agent Model Card
```bash
# Get the current agent model card (shows connected agents and capabilities)
curl -X GET http://localhost:5025/.well-known/agent-card.json | python -m json.tool
```

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

### 1. Weather-Math Integration
"What's the average temperature between Tokyo and London, and how much warmer is it in Fahrenheit?"
- Routes to: Weather Agent (get temperatures) + Calculator Agent (compute average, convert units)
- Synthesizes: Weather data + Mathematical computation + Unit conversion

### 2. Complex Calculations with Context
"If it's 25°C in Paris, convert to Fahrenheit and calculate how much I'd save on heating if I moved there from a place that's 10°C"
- Routes to: Weather Agent (temperature context) + Calculator Agent (conversion and difference)
- Synthesizes: Weather context + Temperature conversion + Cost analysis

### 3. Multi-Step Weather Analysis
"Compare the weather in 3 cities and find which one has the temperature closest to 20°C"
- Routes to: Weather Agent (get all temperatures) + Calculator Agent (find closest to target)
- Synthesizes: Multiple weather queries + Mathematical comparison + Recommendation

## 🏗️ Architecture Benefits

1. **Scalable Intelligence**: Add specialized agents without code changes
2. **Domain Expertise**: Each agent focuses on specific capabilities  
3. **Fault Tolerance**: System continues if individual agents fail
4. **Load Distribution**: Workload spread across multiple agents
5. **Specialized Optimization**: Each agent optimized for its domain
6. **Network Effects**: Agents can learn from each other's outputs

## 🔧 Configuration Examples

### Dynamic Coordinator Agent
```yaml
agents:
  default_urls:
    - "http://localhost:5010"  # Weather Specialist Agent (AgentA) - connected by default

# Agent description and instructions will be automatically generated
# based on the capabilities discovered from connected agents
```

## 🚀 Summary

This A2A agent-to-agent implementation provides:

- **Agent Network Orchestration** instead of tool calling
- **Multi-agent coordination** for comprehensive solutions  
- **Dynamic topology management** with session preservation
- **Specialized domain expertise** through agent coordination
- **Scalable intelligence** that grows with your agent network

Create unlimited specialized agent networks with configuration files and harness the power of collaborative AI agents! 🤖🌐

## 🔧 Understanding the System Architecture

The multi-agent system has a clear layered dependency structure:

**Layer 1: MCP Tools (Foundation)**
- Provide actual capabilities (weather data, calculations)
- Must start first - agents depend on them

**Layer 2: Specialized Agents (Capabilities)**  
- Each agent wraps MCP tools with AI intelligence
- AgentA (Weather) + AgentB (Calculator) + Summarizer

**Layer 3: Coordinator (Orchestration)**
- Manages other agents and synthesizes responses
- Starts with AgentA connected, can add/remove others dynamically

This architecture demonstrates true **emergent capabilities** - the coordinator can do weather+math analysis by orchestrating specialized agents, even though it doesn't directly access MCP tools.

### Enhanced Cleanup Options

The cleanup script now supports granular cleanup of different system components:

```bash
# Clean everything (default)
./cleanup.sh
./cleanup.sh all

# Clean only MCP tool servers (keep agents running)
./cleanup.sh tools

# Clean only specialized agents (AgentA/AgentB, keep coordinator running)
./cleanup.sh single  

# Clean only multi-agent system (coordinator + summarizer, keep single agents)
./cleanup.sh multi

# Clean all agents but keep MCP tools running
./cleanup.sh agents

# Show help with port configurations
./cleanup.sh help
```

**Use Cases:**
- `./cleanup.sh tools` - Restart just the MCP layer while keeping agents
- `./cleanup.sh single` - Test coordinator with fresh specialized agents
- `./cleanup.sh multi` - Restart coordination layer while keeping capabilities
- `./cleanup.sh agents` - Reset all AI agents but keep foundation tools

**Manual cleanup (if needed):**
```bash
# All services
lsof -ti:5025,5030,5010,5011,8001,8002 | xargs -r kill -9

# Just agents  
lsof -ti:5025,5030,5010,5011 | xargs -r kill -9

# Just tools
lsof -ti:8001,8002 | xargs -r kill -9
```

## 🔍 Troubleshooting

### Common Issues

1. **Port Already in Use**: Run cleanup commands before starting services
2. **Agents Won't Start**: Ensure MCP tools are running first (ports 8001, 8002)
3. **"MCP tool connection failed"**: Start MCP tools before agents:
   ```bash
   cd ../../mcp_training
   python run_http.py weather --port 8001 &
   python run_http.py calculator --port 8002 &
   ```
4. **Summarization Agent Unavailable**: Ensure port 5030 is free and the agent is running
5. **Dynamic Updates Not Working**: Check that the summarization agent is responsive
6. **Agent Addition Fails**: Verify target agent is running and accessible

## 🔗 Next Steps

1. **Create Specialized Agents**: Build domain-specific A2A agents
2. **Design Agent Networks**: Plan coordination patterns for your use case
3. **Implement Custom Protocols**: Extend agent communication patterns  
4. **Scale Horizontally**: Deploy agents across multiple servers
5. **Add Intelligence**: Implement agent learning and adaptation