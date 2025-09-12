# MCP Connection Issue - ADK A2A Agent

## Issue Description
The MCP Python SDK has an async generator cleanup issue that causes a `RuntimeError: Attempted to exit cancel scope in a different task than it was entered in`. This error occurs when using `MCPToolset` with Google ADK in the adk_a2a_agent, even though the tools work correctly.

## How to Reproduce the Issue

### Prerequisites
1. Python 3.8+ 
2. Two terminal windows
3. Working directory: `training-materials/a2a_training/adk_a2a_agent`

### Step 1: Set Up Environment

```bash
# Navigate to the adk_a2a_agent directory
cd training-materials/a2a_training/adk_a2a_agent

# Create and activate virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install required packages from existing requirements.txt
pip install -r requirements.txt
```

### Step 2: Start Weather MCP Server

```bash
# Terminal 1: Start the weather MCP server
cd ../../mcp_training

# Note: The MCP server requires fastmcp (should already be installed in mcp_training)
# If not installed: pip install fastmcp

python run_http.py weather --port 8001

# You should see:
# FastMCP 2.0
# Server URL: http://localhost:8001/mcp
# Uvicorn running on http://localhost:8001
```

### Step 3: Start ADK A2A Agent

```bash
# Terminal 2: Start ADK agent with MCP tools
cd ../a2a_training/adk_a2a_agent
python adk_a2a_server.py --mcp-url http://localhost:8001/mcp --port 5003

# You should see:
# Agent ID: adk-a2a-training-agent
# Agent Name: ADK A2A Training Agent
# MCP Tool URL: http://localhost:8001/mcp
# Port: 5003
# INFO: Discovered 3 MCP tools: ['get_current_weather', 'get_weather_forecast', 'convert_temperature']
```

### Step 4: Test and Observe the Error

#### Option A: Send a Test Request (Shows Error After Success)
```bash
# In a new terminal, send a test request
curl -X POST http://localhost:5003/ \
  -H "Content-Type: application/json" \
  -d '{
    "jsonrpc": "2.0",
    "id": 1,
    "method": "message/send",
    "params": {
      "message": {"content": "What is the weather in London?"},
      "sessionId": "test-session-1"
    }
  }' | python -m json.tool
```

#### Option B: Use Legacy Format
```bash
curl -X POST http://localhost:5003 \
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
        "parts": [{"text": "Tell me the current weather in Paris"}]
      }
    }
  }' | python -m json.tool
```

## Expected Behavior vs Actual Behavior

### Expected (What Works)
- The request succeeds
- You receive a valid JSON response with weather data
- The tool is called successfully

Example successful response:
```json
{
  "jsonrpc": "2.0",
  "id": 1,
  "result": {
    "taskId": "...",
    "status": "completed",
    "result": {
      "message": {
        "role": "agent",
        "content": "The current weather in London is overcast with a temperature of 18 degrees Celsius..."
      }
    }
  }
}
```

### Actual (The Error in Logs)
In the ADK agent terminal, after the successful response, you'll see:

```
INFO:__main__:ADK agent response generated successfully
ERROR:asyncio:an error occurred during closing of asynchronous generator <async_generator object streamablehttp_client at 0x...>
  File ".../mcp/client/streamable_http.py", line 476, in streamablehttp_client
    async with anyio.create_task_group() as tg:
  ...
RuntimeError: Attempted to exit cancel scope in a different task than it was entered in
```

## Quick Test Script

Create this test script in the adk_a2a_agent directory:

```bash
cat > test_mcp_issue.py << 'EOF'
#!/usr/bin/env python3
import asyncio
from google.adk.tools.mcp_tool.mcp_toolset import MCPToolset, StreamableHTTPConnectionParams

async def test():
    print("Connecting to MCP server...")
    toolset = MCPToolset(
        connection_params=StreamableHTTPConnectionParams(url="http://localhost:8001/mcp")
    )
    tools = await toolset.get_tools()
    print(f"Found {len(tools)} tools - SUCCESS!")
    print("Error will appear during cleanup...")
    # The error occurs when the async generator is cleaned up

if __name__ == "__main__":
    asyncio.run(test())
EOF

# Run it
python test_mcp_issue.py
```

## What's Happening?

1. **Connection Phase**: MCPToolset connects to the MCP server successfully
2. **Tool Discovery**: Tools are discovered and listed correctly
3. **Tool Execution**: Tools can be called and return correct results
4. **Cleanup Phase**: ❌ ERROR - The async generator cleanup fails

The issue occurs because:
- The MCP SDK uses AnyIO's task groups for async operations
- AnyIO requires cancel scopes to be entered/exited in the same task
- During cleanup, Python's garbage collector runs the cleanup in a different task
- This violates AnyIO's constraints → RuntimeError

## Verification Checklist

✅ **Tool calls succeed** - You get weather data  
✅ **Response is valid** - JSON response is well-formed  
❌ **Clean shutdown fails** - RuntimeError in logs  
❌ **Logs are noisy** - Error messages after each request  

## Impact

- **Functionality**: ✅ Works (tools execute correctly)
- **User Experience**: ✅ Fine (users get correct responses)
- **Developer Experience**: ❌ Poor (error logs are confusing)
- **Production Readiness**: ⚠️ Warning (monitoring systems may trigger alerts)

## Root Cause

The issue is in `mcp/client/streamable_http.py`:
```python
async with anyio.create_task_group() as tg:  # Task group created in task A
    # ... operations ...
    yield  # Control returns to caller
# Later, cleanup happens in task B → ERROR
```

## Known Issue References

- [MCP SDK Issue #521](https://github.com/modelcontextprotocol/python-sdk/issues/521) - Main tracking issue
- [Google ADK Issue #2196](https://github.com/google/adk-python/issues/2196) - ADK integration issue
- [MCP SDK Issue #915](https://github.com/modelcontextprotocol/python-sdk/issues/915) - Related streaming issue

## Workarounds Available

1. **Custom MCP Client** (`../adk_a2a_custom_mcp_agent/custom_mcp_client.py`)
   - Uses direct HTTP calls instead of SDK streaming
   - Completely avoids the async generator issue

2. **Error Suppression** (Not recommended for production)
   - Catch and log the specific RuntimeError
   - Allows operations to continue

3. **Context Manager Wrapper**
   - Ensures cleanup happens in the same task
   - Requires modifying the ADK agent code

## Testing Different Scenarios

### Test 1: Multiple Sequential Requests
```bash
for i in {1..3}; do
  curl -X POST http://localhost:5003/ \
    -H "Content-Type: application/json" \
    -d "{\"jsonrpc\": \"2.0\", \"id\": $i, \"method\": \"message/send\", 
         \"params\": {\"message\": {\"content\": \"Weather in city $i?\"}, 
                      \"sessionId\": \"test-$i\"}}" 
  echo ""
done
```

### Test 2: Check Agent Card (No Tools Called)
```bash
curl http://localhost:5003/.well-known/agent-card.json | python -m json.tool
```

### Test 3: Direct MCP Server Test
```bash
curl -X POST http://localhost:8001/mcp \
  -H "Content-Type: application/json" \
  -H "Accept: application/json, text/event-stream" \
  -d '{"jsonrpc": "2.0", "id": 1, "method": "tools/list"}'
```

## Summary

The MCP connection issue is a **known SDK bug** that:
- Doesn't affect functionality (tools work)
- Causes error logs during cleanup
- Is tracked in multiple GitHub issues
- Has workarounds available (custom client being the most reliable)