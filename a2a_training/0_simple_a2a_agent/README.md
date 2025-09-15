# Simple A2A Agent Server - Training Example

A minimal Agent-to-Agent (A2A) protocol compliant server implementation with HTTP MCP tool calling capabilities. This implementation follows the official A2A specification and provides only the required endpoints for A2A compliance.

## 📜 A2A Protocol Compliance

This implementation is compliant with the official A2A (Agent2Agent) protocol specification, providing:

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

## ✨ Features

- **Minimal A2A Compliance**: Only required endpoints, no extra bloat
- **Dynamic MCP Tool Discovery**: Automatically discovers available tools from MCP server
- **Dynamic Agent Card**: Agent skills are generated based on discovered MCP tools
- **MCP Tool Integration**: HTTP calls to any discovered MCP tools
- **Streamable HTTP Support**: Handles FastMCP Streamable HTTP responses (SSE format)
- **Intelligent Task Processing**: Matches user requests to appropriate discovered tools
- **Configurable**: Command-line arguments and environment variables

## 🚀 Quick Start

### Prerequisites

1. **Start Weather MCP Tool** (required dependency):
   ```bash
   # Navigate to MCP training directory
   cd ../mcp_training
   
   # Start weather MCP tool in stateless mode
   STATELESS_HTTP=true python run_http.py weather --port 8001
   ```

2. **Install A2A Agent Dependencies**:
   ```bash
   cd ../a2a_training/0_simple_a2a_agent
   pip install -r requirements.txt
   ```

### Start the A2A Agent Server

```bash
# Navigate to the agent folder
cd 0_simple_a2a_agent

# Default settings (connects to weather MCP on port 8001)
python simple_a2a_server.py

# With custom configuration
python simple_a2a_server.py --mcp-url http://localhost:8001/mcp --port 5001

# With environment variables
MCP_TOOL_URL=http://localhost:8001/mcp python simple_a2a_server.py
```

The A2A agent server will start on `http://localhost:5001` by default.

## 🔗 A2A Protocol Endpoints

This server implements the minimal required A2A endpoints:

### 1. Agent Discovery (A2A Required)
- **GET** `/.well-known/agent-card.json` - A2A compliant agent metadata

### 2. JSON-RPC Handler (A2A Required)
- **POST** `/` - JSON-RPC 2.0 endpoint supporting:
  - `message/send` - Send messages to agent
  - `tasks/get` - Get task status by ID  
  - `tasks/cancel` - Cancel running tasks
  - `send-task` - Legacy task format support

## 🧪 Testing the A2A Agent

### 1. Agent Discovery
```bash
# Test A2A compliant agent card
curl -s http://localhost:5001/.well-known/agent-card.json | python -m json.tool

```

### 2. A2A Message Sending (Standard Format)

#### Linux
```bash
# Send weather query using A2A message/send method and capture task ID
RESPONSE=$(curl -s -X POST http://localhost:5001 \
  -H "Content-Type: application/json" \
  -d '{
    "jsonrpc": "2.0",
    "id": "test-1",
    "method": "message/send",
    "params": {
      "message": {
        "content": "What is the weather in Tokyo?"
      },
      "sessionId": "session-123"
    }
  }')

echo "$RESPONSE" | python -m json.tool

# Extract task ID from response for dynamic retrieval
TASK_ID=$(echo "$RESPONSE" | python -c "import sys, json; data = json.load(sys.stdin); print(data['result']['taskId'])")
echo "Task ID: $TASK_ID"
```

#### macOS
```bash
# Send weather query using A2A message/send method and capture task ID
# Note: macOS may require python3 and proper encoding handling
RESPONSE=$(curl -s -X POST http://localhost:5001 \
  -H "Content-Type: application/json" \
  -d '{
    "jsonrpc": "2.0",
    "id": "test-1",
    "method": "message/send",
    "params": {
      "message": {
        "content": "What is the weather in Tokyo?"
      },
      "sessionId": "session-123"
    }
  }')

# Display formatted response (use python3 on macOS)
echo "$RESPONSE" | python3 -m json.tool

# Extract task ID - macOS version with better error handling
TASK_ID=$(echo "$RESPONSE" | python3 -c "
import sys, json
try:
    data = json.load(sys.stdin)
    print(data['result']['taskId'])
except json.JSONDecodeError:
    # If direct parsing fails, try saving to file first
    import tempfile
    with tempfile.NamedTemporaryFile(mode='w', delete=False, suffix='.json') as f:
        f.write(sys.stdin.read())
    with open(f.name, 'r') as f:
        data = json.load(f)
    print(data['result']['taskId'])
")
echo "Task ID: $TASK_ID"
```

#### Windows (PowerShell)
```powershell
# Send weather query using A2A message/send method and capture task ID
$headers = @{
    "Content-Type" = "application/json"
}

$body = @{
    jsonrpc = "2.0"
    id = "test-1"
    method = "message/send"
    params = @{
        message = @{
            content = "What is the weather in Tokyo?"
        }
        sessionId = "session-123"
    }
} | ConvertTo-Json -Depth 10

$response = Invoke-RestMethod -Uri "http://localhost:5001" -Method Post -Headers $headers -Body $body

# Display formatted response
$response | ConvertTo-Json -Depth 10

# Extract task ID
$taskId = $response.result.taskId
Write-Host "Task ID: $taskId"
```

#### Windows (Command Prompt with curl)
```batch
REM Send weather query using curl on Windows
curl -s -X POST http://localhost:5001 ^
  -H "Content-Type: application/json" ^
  -d "{\"jsonrpc\": \"2.0\", \"id\": \"test-1\", \"method\": \"message/send\", \"params\": {\"message\": {\"content\": \"What is the weather in Tokyo?\"}, \"sessionId\": \"session-123\"}}" > response.json

REM Display formatted response
type response.json | python -m json.tool

REM Extract task ID (requires Python installed)
for /f "delims=" %%i in ('type response.json ^| python -c "import sys, json; data = json.load(sys.stdin); print(data['result']['taskId'])"') do set TASK_ID=%%i
echo Task ID: %TASK_ID%
```

### 3. Task Management

#### Linux / macOS
```bash
# Get task status using the dynamically captured task ID
curl -X POST http://localhost:5001 \
  -H "Content-Type: application/json" \
  -d "{
    \"jsonrpc\": \"2.0\",
    \"id\": \"test-2\",
    \"method\": \"tasks/get\",
    \"params\": {
      \"taskId\": \"$TASK_ID\"
    }
  }" | python3 -m json.tool

# Cancel the task using the dynamically captured task ID
curl -X POST http://localhost:5001 \
  -H "Content-Type: application/json" \
  -d "{
    \"jsonrpc\": \"2.0\",
    \"id\": \"test-3\",
    \"method\": \"tasks/cancel\",
    \"params\": {
      \"taskId\": \"$TASK_ID\"
    }
  }" | python3 -m json.tool
```

#### Windows (PowerShell)
```powershell
# Get task status using the captured task ID
$getTaskBody = @{
    jsonrpc = "2.0"
    id = "test-2"
    method = "tasks/get"
    params = @{
        taskId = $taskId
    }
} | ConvertTo-Json -Depth 10

Invoke-RestMethod -Uri "http://localhost:5001" -Method Post -Headers $headers -Body $getTaskBody | ConvertTo-Json -Depth 10

# Cancel the task
$cancelTaskBody = @{
    jsonrpc = "2.0"
    id = "test-3"
    method = "tasks/cancel"
    params = @{
        taskId = $taskId
    }
} | ConvertTo-Json -Depth 10

Invoke-RestMethod -Uri "http://localhost:5001" -Method Post -Headers $headers -Body $cancelTaskBody | ConvertTo-Json -Depth 10
```

#### Windows (Command Prompt)
```batch
REM Get task status (uses TASK_ID from previous command)
curl -X POST http://localhost:5001 ^
  -H "Content-Type: application/json" ^
  -d "{\"jsonrpc\": \"2.0\", \"id\": \"test-2\", \"method\": \"tasks/get\", \"params\": {\"taskId\": \"%TASK_ID%\"}}" | python -m json.tool

REM Cancel the task
curl -X POST http://localhost:5001 ^
  -H "Content-Type: application/json" ^
  -d "{\"jsonrpc\": \"2.0\", \"id\": \"test-3\", \"method\": \"tasks/cancel\", \"params\": {\"taskId\": \"%TASK_ID%\"}}" | python -m json.tool
```

### 4. Legacy Format Support
```bash
# Legacy send-task format (backward compatibility)
curl -X POST http://localhost:5001 \
  -H "Content-Type: application/json" \
  -d '{
    "jsonrpc": "2.0",
    "id": "legacy-test",
    "method": "send-task",
    "params": {
      "id": "task-123",
      "sessionId": "session-456",
      "message": {
        "role": "user", 
        "parts": [{"text": "Hello, how are you?"}]
      }
    }
  }' | python -m json.tool
```

## 🔍 Dynamic Tool Discovery

The agent automatically discovers what tools are available from the connected MCP server:

1. **At startup and first request**: Calls `tools/list` on the MCP server
2. **Agent card generation**: Dynamically creates skills based on discovered tools
3. **Request processing**: Matches user messages to appropriate discovered tools
4. **Intelligent routing**: Uses tool descriptions and keywords to select the right tool

### Currently Discovered Tools (from weather MCP server)

1. **get_current_weather**: Get current weather for cities
2. **get_weather_forecast**: Get weather forecast for specified days  
3. **convert_temperature**: Convert temperature between units
4. **General responses**: For non-tool conversations

## ⚙️ Configuration

### Command Line Options
```bash
python simple_a2a_server.py --help
```

- `--mcp-url`: MCP tool URL (default: `http://localhost:8001/mcp`)
- `--agent-id`: Agent ID (default: `simple-a2a-training-agent`)
- `--agent-name`: Agent name (default: `Simple A2A Training Agent`)
- `--port`: Server port (default: `5001`)

### Environment Variables
- `MCP_TOOL_URL`: MCP tool URL
- `AGENT_ID`: Agent ID
- `AGENT_NAME`: Agent name
- `AGENT_PORT`: Server port

## 🔧 MCP Tool Integration

The agent integrates with MCP tools via HTTP:
- **Weather**: `get_current_weather` - Get weather data for cities
- **Time**: `get_current_time` - Get current time (placeholder)
- **Math**: `calculate` - Perform calculations (placeholder)

The agent automatically detects task intent and calls appropriate MCP tools:
- Weather queries trigger calls to the weather MCP tool
- Simple responses for non-weather queries

## 📚 A2A Protocol Reference

This implementation follows the official A2A protocol specification:
- **Transport**: HTTP with JSON-RPC 2.0
- **Authentication**: None (type: "none")
- **Message Types**: Text only
- **Streaming**: Not supported  
- **Task Management**: Full lifecycle support

The minimal implementation demonstrates core A2A concepts without unnecessary complexity.