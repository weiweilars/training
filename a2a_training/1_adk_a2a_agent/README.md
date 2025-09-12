# ADK-Powered A2A Agent Server - Training Example

An advanced Agent-to-Agent (A2A) protocol compliant server implementation powered by Google's Agent Development Kit (ADK) with Gemini LLM integration and HTTP MCP tool calling capabilities. This implementation combines the A2A protocol compliance with powerful LLM reasoning and dynamic tool discovery.

## A2A Protocol Compliance

This implementation is fully compliant with the official A2A (Agent2Agent) protocol specification, providing:

### **Required A2A Components**

1. **Agent Card Discovery** (A2A Spec Requirement)
   - Standard endpoint: `/.well-known/agent-card.json`

2. **Core JSON-RPC Methods** (A2A Spec Requirement)
   - `message/send` - Send messages to the agent
   - `tasks/get` - Retrieve task status by task ID
   - `tasks/cancel` - Cancel ongoing tasks
   - `send-task` - Legacy format support

3. **Task Management** (A2A Spec Requirement)
   - Task lifecycle: submitted → working → completed/failed
   - Persistent task storage and retrieval

## Features

- **A2A Protocol Compliance**: Only required endpoints, fully compliant
- **Google ADK Integration**: Powered by Google's Agent Development Kit
- **Gemini LLM**: Advanced reasoning with gemini-1.5-flash-latest model
- **Dynamic MCP Tool Discovery**: Automatically discovers available tools from MCP server
- **Dynamic Agent Card**: Agent skills are generated based on discovered MCP tools
- **Intelligent Conversation**: LLM-powered responses with context and tool use
- **MCP Tool Integration**: HTTP calls to any discovered MCP tools
- **Streamable HTTP Support**: Handles FastMCP Streamable HTTP responses (SSE format)
- **Session Management**: Maintains conversation context across interactions
- **Configurable**: Command-line arguments and environment variables

## Prerequisites

### 1. Google API Key Setup

You need a Google API key for Gemini access. The `.env` file should contain:

```bash
GOOGLE_API_KEY=your_google_api_key_here
```

### 2. Start Weather MCP Tool (required dependency)

```bash
# Navigate to MCP training directory
cd ../mcp_training

# Start weather MCP tool in stateless mode
STATELESS_HTTP=true python run_http.py weather --port 8002
```

### 3. Install ADK A2A Agent Dependencies

```bash
cd ../a2a_training/adk_a2a_agent
pip install -r requirements.txt
```

## Quick Start

### Start the ADK A2A Agent Server

```bash
# Navigate to the agent folder
cd adk_a2a_agent

# Default settings (connects to weather MCP on port 8002, uses port 5002)
python adk_a2a_server.py

# With custom configuration
python adk_a2a_server.py --mcp-url http://localhost:8002/mcp --port 5005

# With environment variables
MCP_TOOL_URL=http://localhost:8002/mcp python adk_a2a_server.py
```

The ADK A2A agent server will start on `http://localhost:5002` by default.

## A2A Protocol Endpoints

This server implements the minimal required A2A endpoints:

### 1. Agent Discovery (A2A Required)
- **GET** `/.well-known/agent-card.json` - A2A compliant agent metadata with LLM info

### 2. JSON-RPC Handler (A2A Required)
- **POST** `/` - JSON-RPC 2.0 endpoint supporting:
  - `message/send` - Send messages to LLM agent
  - `tasks/get` - Get task status by ID  
  - `tasks/cancel` - Cancel running tasks
  - `send-task` - Legacy task format support

## Testing the ADK A2A Agent

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
        "content": "What is the weather like in Tokyo? Please provide a detailed analysis."
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

### 5. Legacy Format Support

```bash
# Legacy send-task format (backward compatibility)
curl -X POST http://localhost:5002 \
  -H "Content-Type: application/json" \
  -d '{
    "jsonrpc": "2.0",
    "id": "legacy-test",
    "method": "send-task",
    "params": {
      "id": "task-123",
      "sessionId": "session-789",
      "message": {
        "role": "user", 
        "parts": [{"text": "Can you help me understand the weather patterns?"}]
      }
    }
  }' | python -m json.tool
```

## LLM-Powered Capabilities

### Advanced Conversational AI

The ADK agent provides sophisticated conversational capabilities:

1. **Context Awareness**: Maintains conversation context across messages
2. **Tool Integration**: Seamlessly uses MCP tools when appropriate
3. **Intelligent Responses**: Provides detailed, helpful explanations
4. **Session Management**: Remembers previous interactions within sessions

### Example Conversations

**Weather Analysis:**
- User: "What's the weather in Stockholm and what should I wear?"
- Agent: Uses weather tool, then provides clothing recommendations based on conditions

**Tool Explanation:**
- User: "What can you help me with?"  
- Agent: Lists available tools and explains capabilities in natural language

**Multi-step Reasoning:**
- User: "Compare the weather in London and Tokyo"
- Agent: Makes multiple tool calls and provides comparative analysis

## Dynamic Tool Discovery

The agent automatically discovers and integrates with available MCP tools:

1. **At startup**: Calls `tools/list` on the MCP server
2. **Agent card generation**: Dynamically creates skills based on discovered tools
3. **LLM integration**: Makes tools available to the LLM for intelligent use
4. **Adaptive responses**: Uses appropriate tools based on user queries

### Currently Discovered Tools (from weather MCP server)

1. **get_current_weather**: Get current weather for cities
2. **get_weather_forecast**: Get weather forecast for specified days  
3. **convert_temperature**: Convert temperature between units
4. **General conversation**: Advanced LLM-powered dialogue

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

- **LLM Model**: gemini-1.5-flash-latest
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
python adk_a2a_server.py --port 5005
```

### Agent Initialization Issues

If you encounter "Agent not initialized. Call create() first." error:

```bash
# This error was fixed - ensure you're using the latest code
# The agent now properly calls initialize_adk_agent() during startup
```

### Agent Name Validation Errors

If you see agent name validation errors like "Found invalid agent name":

```bash
# This error was fixed - agent names are now automatically converted
# to valid identifiers (spaces → underscores)
# e.g., "ADK A2A Training Agent" → "ADK_A2A_Training_Agent"
```

## Training Benefits

This ADK-powered A2A agent demonstrates:

1. **LLM Integration**: How to add AI reasoning to A2A agents
2. **Protocol Compliance**: Maintaining A2A standards with enhanced capabilities  
3. **Tool Orchestration**: Intelligent use of MCP tools
4. **Session Management**: Context-aware conversations
5. **Dynamic Discovery**: Adaptive tool integration
6. **Production Patterns**: Real-world AI agent architecture