# ADK A2A Agent Server - Dynamic Tool Management Training

An advanced A2A agent server that demonstrates **runtime tool management** capabilities. This implementation extends the base ADK A2A agent with the ability to add and remove MCP tools dynamically while preserving conversation sessions and maintaining A2A protocol compliance.

## 📜 A2A Protocol Compliance

This implementation is fully compliant with the official A2A (Agent2Agent) protocol specification, providing:

### **Required A2A Components**

1. **Agent Card Discovery** (A2A Spec Requirement)
   - Standard endpoint: `/.well-known/agent-card.json`

2. **Core JSON-RPC Methods** (A2A Spec Requirement)
   - `message/send` - Send messages to the agent
   - `tasks/get` - Retrieve task status by task ID
   - `tasks/cancel` - Cancel ongoing tasks
   - `send-task` - Legacy format support

3. **Dynamic Tool Management Methods** (Extension)
   - `tools/add` - Add MCP tools at runtime
   - `tools/remove` - Remove MCP tools at runtime
   - `tools/list` - List current active tools
   - `tools/history` - View tool change history

4. **Task Management** (A2A Spec Requirement)
   - Task lifecycle: submitted → working → completed/failed
   - Persistent task storage and retrieval

## ✨ Features

- **A2A Protocol Compliance**: Only required endpoints, fully compliant
- **Dynamic Tool Management**: Add/remove MCP tools at runtime with session preservation
- **Google ADK Integration**: Powered by Google's Agent Development Kit
- **Gemini LLM**: Advanced reasoning with gemini-2.0-flash-exp model
- **Dynamic MCP Tool Discovery**: Automatically discovers available tools from MCP server
- **Dynamic Agent Card**: Agent skills are generated based on discovered MCP tools
- **Session Preservation**: Maintains conversation context across tool changes
- **Intelligent Conversation**: LLM-powered responses with context and tool use
- **MCP Tool Integration**: HTTP calls to any discovered MCP tools
- **Streamable HTTP Support**: Handles FastMCP Streamable HTTP responses (SSE format)
- **Tool Change History**: Complete audit trail of tool additions/removals
- **Configurable**: Command-line arguments and environment variables

## 📍 Prerequisites

### 1. Google API Key Setup

You need a Google API key for Gemini access. The `.env` file should contain:

```bash
GOOGLE_API_KEY=your_google_api_key_here
```

### 2. Start MCP Tools

```bash
# Navigate to MCP training directory
cd ../mcp_training

# Start MCP tools for comprehensive testing
python run_http.py weather --port 8001 &      # Weather operations
python run_http.py calculator --port 8002 &   # Mathematical calculations

# Wait a moment for servers to start
sleep 2

# Verify servers are running
curl -s http://localhost:8001/mcp >/dev/null && echo "✅ Weather MCP running"
curl -s http://localhost:8002/mcp >/dev/null && echo "✅ Calculator MCP running"
```

**Note**: Both tools support dynamic addition/removal for comprehensive tool management testing.

### 3. Install ADK A2A Agent Dependencies

```bash
cd ../a2a_training/2_adk_a2a_toolManage_agent
pip install -r requirements.txt
```

## 🚀 Quick Start

### Start the ADK A2A Agent Server

```bash
# Navigate to the agent folder
cd 2_adk_a2a_toolManage_agent

# Default settings (connects to calculator MCP on port 8002, uses port 5002)
python adk_a2a_server.py --mcp-url http://localhost:8002/mcp

# With custom configuration  
python adk_a2a_server.py --mcp-url http://localhost:8002/mcp --port 5002

# With environment variables
MCP_TOOL_URL=http://localhost:8002/mcp python adk_a2a_server.py
```

The ADK A2A agent server will start on `http://localhost:5002` by default.

## 🧪 Testing the Dynamic Tool Management

### 1. Agent Discovery

```bash
# Test A2A compliant agent card (shows LLM capabilities)
curl -s http://localhost:5002/.well-known/agent-card.json | python -m json.tool

```

### 2. A2A Message Sending with LLM

```bash
# Send intelligent query using A2A message/send method and capture task ID
RESPONSE=$(curl -s -X POST http://localhost:5002 \
  -H "Content-Type: application/json" \
  -d '{
    "jsonrpc": "2.0",
    "id": "test-1",
    "method": "message/send",
    "params": {
      "message": {
        "content": "Can you calculate the square root of 144 and then multiply it by 5?"
      },
      "sessionId": "session-123"
    }
  }')

echo "$RESPONSE" | python -m json.tool

# Extract task ID from response
TASK_ID=$(echo "$RESPONSE" | python -c "import sys, json; print(json.load(sys.stdin)['result']['taskId'])")
echo "Task ID: $TASK_ID"
```

### 3. Conversational AI Testing

```bash
# Test general conversation capabilities
curl -X POST http://localhost:5002 \
  -H "Content-Type: application/json" \
  -d '{
    "jsonrpc": "2.0",
    "id": "test-conv",
    "method": "message/send",
    "params": {
      "message": {
        "content": "Hello! Can you explain what tools you have access to and how you can help me?"
      },
      "sessionId": "session-456"
    }
  }' | python -m json.tool
```

### 4. Task Management

```bash
# Get task status using the captured task ID
curl -X POST http://localhost:5002 \
  -H "Content-Type: application/json" \
  -d "{
    \"jsonrpc\": \"2.0\",
    \"id\": \"test-2\", 
    \"method\": \"tasks/get\",
    \"params\": {
      \"taskId\": \"$TASK_ID\"
    }
  }" | python -m json.tool
```

### 5. Dynamic Tool Management

#### Add Tool
```bash
# Add a new MCP tool dynamically (weather tool)
curl -X POST http://localhost:5002 \
  -H "Content-Type: application/json" \
  -d '{
    "jsonrpc": "2.0",
    "id": "add-tool-test",
    "method": "tools/add",
    "params": {
      "url": "http://localhost:8001/mcp"
    }
  }' | python -m json.tool
```

#### Remove Tool
```bash
# Remove an MCP tool dynamically (weather tool)
curl -X POST http://localhost:5002 \
  -H "Content-Type: application/json" \
  -d '{
    "jsonrpc": "2.0",
    "id": "remove-tool-test", 
    "method": "tools/remove",
    "params": {
      "url": "http://localhost:8001/mcp"
    }
  }' | python -m json.tool
```

#### List Current Tools
```bash
# Get list of currently active tools
curl -X POST http://localhost:5002 \
  -H "Content-Type: application/json" \
  -d '{
    "jsonrpc": "2.0",
    "id": "list-tools-test",
    "method": "tools/list",
    "params": {}
  }' | python -m json.tool
```

#### Tool Change History
```bash
# Get history of all tool additions/removals with timestamps and descriptions
curl -X POST http://localhost:5002 \
  -H "Content-Type: application/json" \
  -d '{
    "jsonrpc": "2.0",
    "id": "tool-history-test",
    "method": "tools/history", 
    "params": {}
  }' | python -m json.tool
```

**Enhanced History Format:**
```json
{
  "history": [
    {
      "action": "add",
      "url": "http://localhost:8001/mcp",
      "timestamp": "2025-09-08T16:27:34.179409",
      "session_preserved": true,
      "tool_descriptions": [
        {
          "name": "get_current_weather",
          "description": "Get current weather for cities..."
        },
        {
          "name": "convert_temperature", 
          "description": "Convert temperature between units..."
        }
      ]
    }
  ]
}
```

### 6. Dynamic Tool Management Demonstration

#### Session Continuity Test Script
```bash
# Run comprehensive capability change demonstration
python test_session_continuity.py
```

This test script demonstrates:
- **Starting with calculator tool**: Shows base mathematical capabilities
- **Adding weather tool**: Demonstrates multi-tool integration  
- **Removing weather tool**: Shows graceful capability reduction
- **Session preservation**: Maintains context across all changes
- **Complete audit trail**: Tracks all tool operations

**Expected Output:**
```
🧪 Testing Dynamic Tool Management and Capability Changes
🎯 CAPABILITY CHANGE SUMMARY:
   CALCULATOR:       Calculator ✅ | Weather ❌
   BOTH TOOLS:       Calculator ✅ | Weather ✅  
   CALCULATOR ONLY:  Calculator ✅ | Weather ❌
🎉 Dynamic tool management working perfectly!
```



## LLM-Powered Capabilities

### Advanced Conversational AI

The ADK agent provides sophisticated conversational capabilities:

1. **Context Awareness**: Maintains conversation context across messages
2. **Tool Integration**: Seamlessly uses MCP tools when appropriate
3. **Intelligent Responses**: Provides detailed, helpful explanations
4. **Session Management**: Remembers previous interactions within sessions

### Example Conversations

**Mathematical Analysis:**
- User: "Calculate the area of a circle with radius 5 and tell me what it means"
- Agent: Uses calculator tool, then provides contextual explanation

**Tool Explanation:**
- User: "What can you help me with?"  
- Agent: Lists available tools and explains capabilities in natural language

**Multi-step Reasoning:**
- User: "Calculate 25% of 200, then find the square root of that result"
- Agent: Makes multiple calculations and provides step-by-step explanation

### Currently Available MCP Tools

#### Calculator MCP Server (port 8002) - Default
1. **basic_math**: Perform basic mathematical operations (+, -, *, /, %, ^)
2. **advanced_math**: Advanced math functions (sqrt, sin, cos, tan, log, ln, exp, abs, ceil, floor)
3. **evaluate_expression**: Safely evaluate mathematical expressions

#### Weather MCP Server (port 8001) - Dynamic Addition
1. **get_current_weather**: Get current weather for cities
2. **get_weather_forecast**: Get weather forecast for specified days  
3. **convert_temperature**: Convert temperature between units

#### General Capabilities
- **Advanced conversation**: LLM-powered dialogue with context awareness
- **Dynamic tool integration**: Tools can be added/removed at runtime

## Configuration

### Command Line Options

```bash
python adk_a2a_server.py --help
```

- `--mcp-url`: MCP tool URL (default: `http://localhost:8002/mcp`)
- `--agent-id`: Agent ID (default: `adk-a2a-training-agent`)
- `--agent-name`: Agent name (default: `ADK A2A Training Agent`)
- `--port`: Server port (default: `5002`)

### Environment Variables

- `MCP_TOOL_URL`: MCP tool URL
- `AGENT_ID`: Agent ID
- `AGENT_NAME`: Agent name
- `AGENT_PORT`: Server port
- `GOOGLE_API_KEY`: Google API key for Gemini (required)

## Google ADK Integration

The agent integrates Google's Agent Development Kit:

- **LLM Model**: gemini-2.0-flash-exp
- **Session Management**: Maintains conversation context
- **Memory Service**: Remembers interactions
- **Tool Integration**: Seamlessly uses MCP tools
- **Runner Framework**: Coordinates all components

## Comparison with Simple A2A Agent

| Feature | Simple A2A Agent | ADK A2A Agent |
|---------|------------------|---------------|
| **LLM Power** | ❌ Rule-based responses | ✅ Google Gemini LLM |
| **Conversation** | ❌ Simple keyword matching | ✅ Advanced dialogue |
| **Context** | ❌ No memory | ✅ Session-aware |
| **Tool Use** | ⚠️ Hardcoded logic | ✅ Intelligent tool selection |
| **Responses** | ⚠️ Basic formatting | ✅ Natural, helpful responses |
| **A2A Compliance** | ✅ Full compliance | ✅ Full compliance |
| **Setup Complexity** | ✅ Simple | ⚠️ Requires Google API key |

## A2A Protocol Reference

This implementation follows the official A2A protocol specification:

- **Transport**: HTTP with JSON-RPC 2.0
- **Authentication**: None (type: "none")
- **Message Types**: Text only
- **Streaming**: Not supported  
- **Task Management**: Full lifecycle support
- **LLM Enhancement**: Powered by Google Gemini

The implementation demonstrates how to enhance A2A agents with advanced LLM capabilities while maintaining full protocol compliance.

## Troubleshooting

### Google API Key Issues

```bash
# Check if API key is set
echo $GOOGLE_API_KEY

# Verify .env file exists and contains key
cat .env
```

### ADK Dependencies

```bash
# Install/update ADK
pip install --upgrade google-adk

# Check ADK version
python -c "import google.adk; print('ADK installed')"
```

### Port Conflicts

```bash
# Use different port if 5002 is busy
python adk_a2a_server.py --port 5003
```

## Testing Scripts

This implementation includes a comprehensive test script:

### **test_session_continuity.py** - Session Preservation and Tool Management Testing
- Tests how conversation context is maintained across tool changes
- Demonstrates dynamic tool add/remove operations with session preservation
- Shows intelligent conversation flow (calculation → weather) across tool changes
- Complete audit trail with detailed history tracking

## 🧹 Cleanup Management

### Automated Cleanup Script

The `cleanup.sh` script helps manage running processes during development and testing:

```bash
# Clean up everything (MCP tools + A2A agent)
./cleanup.sh

# Clean up only MCP tool servers
./cleanup.sh tools

# Clean up only A2A agent server  
./cleanup.sh agent

# Show help and port configuration
./cleanup.sh help
```

### Port Management

| Component | Port | Description |
|-----------|------|-------------|
| **MCP Tools** | | |
| Calculator MCP (default) | 8002 | Mathematical calculations |
| Weather MCP (dynamic) | 8001 | Weather data and forecasting |
| **A2A Agent** | | |
| ADK A2A Agent | 5002 | LLM-powered agent with tool management |

### Cleanup Features

- ✅ **Smart Process Detection** - Uses `lsof` to find processes on ports
- ✅ **Graceful Termination** - Tries `SIGTERM` first, then `SIGKILL` if needed
- ✅ **Port Verification** - Confirms ports are actually freed
- ✅ **Selective Cleanup** - Clean tools, agent, or both
- ✅ **Colorful Output** - Clear status indicators and progress

### Troubleshooting

If ports are still in use after cleanup:

```bash
# Check what's using a specific port
lsof -i :5002

# Manual kill (replace PID with actual process ID)
kill -9 <PID>

# Check all our ports at once
lsof -i :8001 -i :8002 -i :5002
```


## Training Benefits

This ADK-powered A2A agent demonstrates:

1. **Dynamic Tool Management**: Runtime addition/removal of MCP tools with session preservation
2. **Multi-tool Integration**: Seamless coordination of Weather and Calculator tools
3. **LLM Integration**: How to add AI reasoning to A2A agents
4. **Protocol Compliance**: Maintaining A2A standards with enhanced capabilities  
5. **Tool Orchestration**: Intelligent use of MCP tools
6. **Session Management**: Context-aware conversations across tool changes
7. **Comprehensive Testing**: Automated test script demonstrating session continuity and tool management
8. **Dynamic Discovery**: Adaptive tool integration
9. **Production Patterns**: Real-world AI agent architecture