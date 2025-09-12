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

3. **Dynamic Tool Management Methods** (Extension)
   - `tools/add` - Add MCP tools at runtime
   - `tools/remove` - Remove MCP tools at runtime
   - `tools/list` - List current active tools
   - `tools/history` - View tool change history

4. **Task Management** (A2A Spec Requirement)
   - Task lifecycle: submitted → working → completed/failed
   - Persistent task storage and retrieval

## Features

- **A2A Protocol Compliance**: Only required endpoints, fully compliant
- **Dynamic Tool Management**: Add/remove MCP tools at runtime with session preservation
- **Google ADK Integration**: Powered by Google's Agent Development Kit
- **Gemini LLM**: Advanced reasoning with gemini-1.5-flash-latest model
- **Dynamic MCP Tool Discovery**: Automatically discovers available tools from MCP server
- **Dynamic Agent Card**: Agent skills are generated based on discovered MCP tools
- **Session Preservation**: Maintains conversation context across tool changes
- **Intelligent Conversation**: LLM-powered responses with context and tool use
- **MCP Tool Integration**: HTTP calls to any discovered MCP tools
- **Streamable HTTP Support**: Handles FastMCP Streamable HTTP responses (SSE format)
- **Tool Change History**: Complete audit trail of tool additions/removals
- **Configurable**: Command-line arguments and environment variables

## Prerequisites

### 1. Google API Key Setup

You need a Google API key for Gemini access. The `.env` file should contain:

```bash
GOOGLE_API_KEY=your_google_api_key_here
```

### 2. Start MCP Tools

```bash
# Navigate to MCP training directory
cd ../mcp_training

# Start all three MCP tools for comprehensive testing
python run_http.py weather --port 8004 &      # Weather operations
python run_http.py file --port 8003 &         # File operations  
python run_http.py calculator --port 8005 &   # Mathematical calculations

# Wait a moment for servers to start
sleep 2

# Verify servers are running
curl -s http://localhost:8004/mcp >/dev/null && echo "✅ Weather MCP running"
curl -s http://localhost:8003/mcp >/dev/null && echo "✅ File MCP running" 
curl -s http://localhost:8005/mcp >/dev/null && echo "✅ Calculator MCP running"
```

**Note**: All three tools support dynamic addition/removal for comprehensive tool management testing.

### 3. Install ADK A2A Agent Dependencies

```bash
cd ../a2a_training/2_adk_a2a_toolManage_agent
pip install -r requirements.txt
```

## Quick Start

### Start the ADK A2A Agent Server

```bash
# Navigate to the agent folder
cd 2_adk_a2a_toolManage_agent

# Default settings (connects to weather MCP on port 8004, uses port 5002)
python adk_a2a_server.py --mcp-url http://localhost:8004/mcp

# With custom configuration
python adk_a2a_server.py --mcp-url http://localhost:8004/mcp --port 5002

# With environment variables
MCP_TOOL_URL=http://localhost:8004/mcp python adk_a2a_server.py
```

The ADK A2A agent server will start on `http://localhost:5002` by default.

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

### 5. Dynamic Tool Management

#### Add Tool
```bash
# Add a new MCP tool dynamically
curl -X POST http://localhost:5002 \
  -H "Content-Type: application/json" \
  -d '{
    "jsonrpc": "2.0",
    "id": "add-tool-test",
    "method": "tools/add",
    "params": {
      "url": "http://localhost:8003/mcp"
    }
  }' | python -m json.tool
```

#### Remove Tool
```bash
# Remove an MCP tool dynamically
curl -X POST http://localhost:5002 \
  -H "Content-Type: application/json" \
  -d '{
    "jsonrpc": "2.0",
    "id": "remove-tool-test", 
    "method": "tools/remove",
    "params": {
      "url": "http://localhost:8003/mcp"
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
      "url": "http://localhost:8003/mcp",
      "timestamp": "2025-09-08T16:27:34.179409",
      "session_preserved": true,
      "tool_descriptions": [
        {
          "name": "list_files",
          "description": "List files in a directory..."
        },
        {
          "name": "read_file", 
          "description": "Read file contents..."
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
- **Starting with no tools**: Shows base LLM capabilities
- **Adding weather tool**: Demonstrates tool integration  
- **Adding file tool**: Shows multi-tool capability
- **Removing tools**: Shows graceful capability reduction
- **Session preservation**: Maintains context across all changes
- **Complete audit trail**: Tracks all tool operations

**Expected Output:**
```
🧪 Testing Dynamic Tool Management and Capability Changes
🎯 CAPABILITY CHANGE SUMMARY:
   NO TOOLS:      Weather ❌ | Files ❌
   WEATHER TOOL:  Weather ✅ | Files ❌  
   BOTH TOOLS:    Weather ✅ | Files ❌*
   WEATHER ONLY:  Weather ✅ | Files ❌
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

**Weather Analysis:**
- User: "What's the weather in Stockholm and what should I wear?"
- Agent: Uses weather tool, then provides clothing recommendations based on conditions

**Tool Explanation:**
- User: "What can you help me with?"  
- Agent: Lists available tools and explains capabilities in natural language

**Multi-step Reasoning:**
- User: "Compare the weather in London and Tokyo"
- Agent: Makes multiple tool calls and provides comparative analysis

### Currently Available MCP Tools

#### Weather MCP Server (port 8004)
1. **get_current_weather**: Get current weather for cities
2. **get_weather_forecast**: Get weather forecast for specified days  
3. **convert_temperature**: Convert temperature between units

#### File MCP Server (port 8003)
1. **list_files**: List files in a directory
2. **read_file**: Read contents of a file
3. **write_file**: Write content to a file

#### Calculator MCP Server (port 8001)
1. **basic_math**: Perform basic mathematical operations (+, -, *, /, %, ^)
2. **advanced_math**: Advanced math functions (sqrt, sin, cos, tan, log, ln, exp, abs, ceil, floor)
3. **evaluate_expression**: Safely evaluate mathematical expressions

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
python adk_a2a_server.py --port 5003
```

## Testing Scripts

This implementation includes a comprehensive test script:

### **test_session_continuity.py** - Session Preservation and Tool Management Testing
- Tests how conversation context is maintained across tool changes
- Demonstrates dynamic tool add/remove operations with session preservation
- Shows intelligent conversation flow (weather → calculation) across tool changes
- Complete audit trail with detailed history tracking


## Training Benefits

This ADK-powered A2A agent demonstrates:

1. **Dynamic Tool Management**: Runtime addition/removal of MCP tools with session preservation
2. **Multi-tool Integration**: Seamless coordination of Weather, File, and Calculator tools
3. **LLM Integration**: How to add AI reasoning to A2A agents
4. **Protocol Compliance**: Maintaining A2A standards with enhanced capabilities  
5. **Tool Orchestration**: Intelligent use of MCP tools
6. **Session Management**: Context-aware conversations across tool changes
7. **Comprehensive Testing**: Automated test script demonstrating session continuity and tool management
8. **Dynamic Discovery**: Adaptive tool integration
9. **Production Patterns**: Real-world AI agent architecture