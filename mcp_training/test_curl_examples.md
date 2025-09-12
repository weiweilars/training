# MCP Tools - Curl Testing Examples

This document provides curl commands for testing MCP tools in both stateless and stateful modes.

## Prerequisites

Start your MCP server first:
```bash
# For stateless mode (default)
STATELESS_HTTP=true python run_http.py file --port 8003
STATELESS_HTTP=true python run_http.py weather --port 8002
STATELESS_HTTP=true python run_http.py calculator --port 8001

# For stateful mode
STATELESS_HTTP=false python run_http.py file --port 8003
STATELESS_HTTP=false python run_http.py weather --port 8002
STATELESS_HTTP=false python run_http.py calculator --port 8001
```

## Stateless Mode Testing

In stateless mode, each request is independent. No session management is required.

### 1. File Tools (port 8000)

#### List Available Tools
```bash
curl -X POST http://localhost:8003/mcp \
  -H "Content-Type: application/json" \
  -H "Accept: application/json, text/event-stream" \
  -d '{
    "jsonrpc": "2.0",
    "id": 1,
    "method": "tools/list"
  }' 
```

#### List Files
```bash
curl -X POST http://localhost:8003/mcp \
  -H "Content-Type: application/json" \
  -H "Accept: application/json, text/event-stream" \
  -d '{
    "jsonrpc": "2.0",
    "id": 2,
    "method": "tools/call",
    "params": {
      "name": "list_files",
      "arguments": {}
    }
  }'
```

#### Write a File
```bash
curl -X POST http://localhost:8003/mcp \
  -H "Content-Type: application/json" \
  -H "Accept: application/json, text/event-stream" \
  -d '{
    "jsonrpc": "2.0",
    "id": 3,
    "method": "tools/call",
    "params": {
      "name": "write_file",
      "arguments": {
        "filepath": "test_file.txt",
        "content": "Hello from MCP curl test!"
      }
    }
  }' 
```

#### Read a File
```bash
curl -X POST http://localhost:8003/mcp \
  -H "Content-Type: application/json" \
  -H "Accept: application/json, text/event-stream" \
  -d '{
    "jsonrpc": "2.0",
    "id": 4,
    "method": "tools/call",
    "params": {
      "name": "read_file",
      "arguments": {
        "filepath": "test_file.txt"
      }
    }
  }' 
```

### 2. Weather Tools (port 8002)

Start weather server: `STATELESS_HTTP=true python run_http.py weather --port 8002`

#### List Available Tools
```bash
curl -X POST http://localhost:8002/mcp \
  -H "Content-Type: application/json" \
  -H "Accept: application/json, text/event-stream" \
  -d '{
    "jsonrpc": "2.0",
    "id": 1,
    "method": "tools/list"
  }' 
```

#### Get Current Weather
```bash
curl -X POST http://localhost:8002/mcp \
  -H "Content-Type: application/json" \
  -H "Accept: application/json, text/event-stream" \
  -d '{
    "jsonrpc": "2.0",
    "id": 5,
    "method": "tools/call",
    "params": {
      "name": "get_current_weather",
      "arguments": {
        "city": "London"
      }
    }
  }' 
```

#### Get Weather Forecast
```bash
curl -X POST http://localhost:8002/mcp \
  -H "Content-Type: application/json" \
  -H "Accept: application/json, text/event-stream" \
  -d '{
    "jsonrpc": "2.0",
    "id": 6,
    "method": "tools/call",
    "params": {
      "name": "get_weather_forecast",
      "arguments": {
        "city": "New York",
        "days": 3
      }
    }
  }' 
```

#### Convert Temperature
```bash
curl -X POST http://localhost:8002/mcp \
  -H "Content-Type: application/json" \
  -H "Accept: application/json, text/event-stream" \
  -d '{
    "jsonrpc": "2.0",
    "id": 7,
    "method": "tools/call",
    "params": {
      "name": "convert_temperature",
      "arguments": {
        "temperature": 32.0,
        "from_unit": "fahrenheit",
        "to_unit": "celsius"
      }
    }
  }' 
```

### 3. Calculator Tools (port 8001)

Start calculator server: `STATELESS_HTTP=true python run_http.py calculator --port 8001`

#### List Available Tools
```bash
curl -X POST http://localhost:8001/mcp \
  -H "Content-Type: application/json" \
  -H "Accept: application/json, text/event-stream" \
  -d '{
    "jsonrpc": "2.0",
    "id": 1,
    "method": "tools/list"
  }' 
```

#### Basic Math Operations
```bash
# Addition
curl -X POST http://localhost:8001/mcp \
  -H "Content-Type: application/json" \
  -H "Accept: application/json, text/event-stream" \
  -d '{
    "jsonrpc": "2.0",
    "id": 2,
    "method": "tools/call",
    "params": {
      "name": "basic_math",
      "arguments": {
        "operation": "+",
        "a": 15,
        "b": 25
      }
    }
  }'

# Division
curl -X POST http://localhost:8001/mcp \
  -H "Content-Type: application/json" \
  -H "Accept: application/json, text/event-stream" \
  -d '{
    "jsonrpc": "2.0",
    "id": 3,
    "method": "tools/call",
    "params": {
      "name": "basic_math",
      "arguments": {
        "operation": "/",
        "a": 100,
        "b": 4
      }
    }
  }'

# Power operation
curl -X POST http://localhost:8001/mcp \
  -H "Content-Type: application/json" \
  -H "Accept: application/json, text/event-stream" \
  -d '{
    "jsonrpc": "2.0",
    "id": 4,
    "method": "tools/call",
    "params": {
      "name": "basic_math",
      "arguments": {
        "operation": "^",
        "a": 2,
        "b": 8
      }
    }
  }'
```

#### Advanced Math Functions
```bash
# Square root
curl -X POST http://localhost:8001/mcp \
  -H "Content-Type: application/json" \
  -H "Accept: application/json, text/event-stream" \
  -d '{
    "jsonrpc": "2.0",
    "id": 5,
    "method": "tools/call",
    "params": {
      "name": "advanced_math",
      "arguments": {
        "function": "sqrt",
        "value": 16
      }
    }
  }'

# Sine function
curl -X POST http://localhost:8001/mcp \
  -H "Content-Type: application/json" \
  -H "Accept: application/json, text/event-stream" \
  -d '{
    "jsonrpc": "2.0",
    "id": 6,
    "method": "tools/call",
    "params": {
      "name": "advanced_math",
      "arguments": {
        "function": "sin",
        "value": 1.57
      }
    }
  }'

# Logarithm with custom base
curl -X POST http://localhost:8001/mcp \
  -H "Content-Type: application/json" \
  -H "Accept: application/json, text/event-stream" \
  -d '{
    "jsonrpc": "2.0",
    "id": 7,
    "method": "tools/call",
    "params": {
      "name": "advanced_math",
      "arguments": {
        "function": "log",
        "value": 8,
        "extra_param": 2
      }
    }
  }'
```

#### Expression Evaluation
```bash
# Simple expression
curl -X POST http://localhost:8001/mcp \
  -H "Content-Type: application/json" \
  -H "Accept: application/json, text/event-stream" \
  -d '{
    "jsonrpc": "2.0",
    "id": 8,
    "method": "tools/call",
    "params": {
      "name": "evaluate_expression",
      "arguments": {
        "expression": "2 + 3 * 4"
      }
    }
  }'

# Complex expression with functions
curl -X POST http://localhost:8001/mcp \
  -H "Content-Type: application/json" \
  -H "Accept: application/json, text/event-stream" \
  -d '{
    "jsonrpc": "2.0",
    "id": 9,
    "method": "tools/call",
    "params": {
      "name": "evaluate_expression",
      "arguments": {
        "expression": "sqrt(16) + sin(pi/2) * 10"
      }
    }
  }'
```

## Stateful Mode Testing

In stateful mode, you must establish a session first, then maintain it across requests.

### 1. File Tools (Stateful - port 8003)

Start server: `STATELESS_HTTP=false python run_http.py file --port 8003`

#### Initialize Session
```bash
# Step 1: Initialize the session
RESPONSE=$(curl -s -i -X POST http://localhost:8003/mcp \
  -H "Content-Type: application/json" \
  -H "Accept: application/json, text/event-stream" \
  -d '{
    "jsonrpc": "2.0",
    "id": 1,
    "method": "initialize",
    "params": {
      "protocolVersion": "2024-11-05",
      "capabilities": {
        "roots": {"listChanged": true},
        "sampling": {}
      },
      "clientInfo": {
        "name": "curl-test-client",
        "version": "1.0.0"
      }
    }
  }')

# Extract session ID from response headers
SESSION_ID=$(echo "$RESPONSE" | grep -i 'mcp-session-id:' | cut -d' ' -f2 | tr -d '\r')
echo "Session ID: $SESSION_ID"
```

#### Send Required Notifications
```bash
# Step 2: Send initialized notification
curl -X POST http://localhost:8003/mcp \
  -H "Content-Type: application/json" \
  -H "Accept: application/json, text/event-stream" \
  -H "Mcp-Session-Id: $SESSION_ID" \
  -d '{
    "jsonrpc": "2.0",
    "method": "notifications/initialized"
  }'
```

#### Test File Operations with Session
```bash
# List tools
curl -X POST http://localhost:8003/mcp \
  -H "Content-Type: application/json" \
  -H "Accept: application/json, text/event-stream" \
  -H "Mcp-Session-Id: $SESSION_ID" \
  -d '{
    "jsonrpc": "2.0",
    "id": 2,
    "method": "tools/list"
  }'

# List files
curl -X POST http://localhost:8003/mcp \
  -H "Content-Type: application/json" \
  -H "Accept: application/json, text/event-stream" \
  -H "Mcp-Session-Id: $SESSION_ID" \
  -d '{
    "jsonrpc": "2.0",
    "id": 3,
    "method": "tools/call",
    "params": {
      "name": "list_files",
      "arguments": {}
    }
  }' 

# Write file
curl -X POST http://localhost:8003/mcp \
  -H "Content-Type: application/json" \
  -H "Accept: application/json, text/event-stream" \
  -H "Mcp-Session-Id: $SESSION_ID" \
  -d '{
    "jsonrpc": "2.0",
    "id": 4,
    "method": "tools/call",
    "params": {
      "name": "write_file",
      "arguments": {
        "filepath": "stateful_test.txt",
        "content": "Hello from stateful MCP test!"
      }
    }
  }'

# Read file
curl -X POST http://localhost:8003/mcp \
  -H "Content-Type: application/json" \
  -H "Accept: application/json, text/event-stream" \
  -H "Mcp-Session-Id: $SESSION_ID" \
  -d '{
    "jsonrpc": "2.0",
    "id": 5,
    "method": "tools/call",
    "params": {
      "name": "read_file",
      "arguments": {
        "filepath": "stateful_test.txt"
      }
    }
  }' 
```

### 2. Weather Tools (Stateful - port 8002)

Start server: `STATELESS_HTTP=false python run_http.py weather --port 8002`

#### Initialize Session
```bash
# Step 1: Initialize weather session
WEATHER_RESPONSE=$(curl -s -i -X POST http://localhost:8002/mcp \
  -H "Content-Type: application/json" \
  -H "Accept: application/json, text/event-stream" \
  -d '{
    "jsonrpc": "2.0",
    "id": 1,
    "method": "initialize",
    "params": {
      "protocolVersion": "2024-11-05",
      "capabilities": {
        "roots": {"listChanged": true},
        "sampling": {}
      },
      "clientInfo": {
        "name": "curl-weather-client",
        "version": "1.0.0"
      }
    }
  }')

# Extract weather session ID
WEATHER_SESSION_ID=$(echo "$WEATHER_RESPONSE" | grep -i 'mcp-session-id:' | cut -d' ' -f2 | tr -d '\r')
echo "Weather Session ID: $WEATHER_SESSION_ID"

# Send initialized notification
curl -X POST http://localhost:8002/mcp \
  -H "Content-Type: application/json" \
  -H "Accept: application/json, text/event-stream" \
  -H "Mcp-Session-Id: $WEATHER_SESSION_ID" \
  -d '{
    "jsonrpc": "2.0",
    "method": "notifications/initialized"
  }'
```

#### Test Weather Operations with Session
```bash
# List weather tools
curl -X POST http://localhost:8002/mcp \
  -H "Content-Type: application/json" \
  -H "Accept: application/json, text/event-stream" \
  -H "Mcp-Session-Id: $WEATHER_SESSION_ID" \
  -d '{
    "jsonrpc": "2.0",
    "id": 2,
    "method": "tools/list"
  }' 

# Get current weather
curl -X POST http://localhost:8002/mcp \
  -H "Content-Type: application/json" \
  -H "Accept: application/json, text/event-stream" \
  -H "Mcp-Session-Id: $WEATHER_SESSION_ID" \
  -d '{
    "jsonrpc": "2.0",
    "id": 3,
    "method": "tools/call",
    "params": {
      "name": "get_current_weather",
      "arguments": {
        "city": "Tokyo"
      }
    }
  }' 

# Get weather forecast
curl -X POST http://localhost:8002/mcp \
  -H "Content-Type: application/json" \
  -H "Accept: application/json, text/event-stream" \
  -H "Mcp-Session-Id: $WEATHER_SESSION_ID" \
  -d '{
    "jsonrpc": "2.0",
    "id": 4,
    "method": "tools/call",
    "params": {
      "name": "get_weather_forecast",
      "arguments": {
        "city": "London",
        "days": 5
      }
    }
  }'

# Convert temperature
curl -X POST http://localhost:8002/mcp \
  -H "Content-Type: application/json" \
  -H "Accept: application/json, text/event-stream" \
  -H "Mcp-Session-Id: $WEATHER_SESSION_ID" \
  -d '{
    "jsonrpc": "2.0",
    "id": 5,
    "method": "tools/call",
    "params": {
      "name": "convert_temperature",
      "arguments": {
        "temperature": 25.0,
        "from_unit": "celsius",
        "to_unit": "fahrenheit"
      }
    }
  }' 
```

### 3. Calculator Tools (Stateful - port 8001)

Start server: `STATELESS_HTTP=false python run_http.py calculator --port 8001`

#### Initialize Session
```bash
# Step 1: Initialize calculator session
CALC_RESPONSE=$(curl -s -i -X POST http://localhost:8001/mcp \
  -H "Content-Type: application/json" \
  -H "Accept: application/json, text/event-stream" \
  -d '{
    "jsonrpc": "2.0",
    "id": 1,
    "method": "initialize",
    "params": {
      "protocolVersion": "2024-11-05",
      "capabilities": {
        "roots": {"listChanged": true},
        "sampling": {}
      },
      "clientInfo": {
        "name": "curl-calculator-client",
        "version": "1.0.0"
      }
    }
  }')

# Extract session ID from response headers
CALC_SESSION_ID=$(echo "$CALC_RESPONSE" | grep -i 'mcp-session-id:' | cut -d' ' -f2 | tr -d '\r')
echo "Calculator Session ID: $CALC_SESSION_ID"
```

#### Send Required Notifications
```bash
# Step 2: Send notifications/initialized
curl -X POST http://localhost:8001/mcp \
  -H "Content-Type: application/json" \
  -H "Accept: application/json, text/event-stream" \
  -H "Mcp-Session-Id: $CALC_SESSION_ID" \
  -d '{
    "jsonrpc": "2.0",
    "method": "notifications/initialized"
  }'
```

#### Use Calculator Tools with Session
```bash
# Basic math with session
curl -X POST http://localhost:8001/mcp \
  -H "Content-Type: application/json" \
  -H "Accept: application/json, text/event-stream" \
  -H "Mcp-Session-Id: $CALC_SESSION_ID" \
  -d '{
    "jsonrpc": "2.0",
    "id": 3,
    "method": "tools/call",
    "params": {
      "name": "basic_math",
      "arguments": {
        "operation": "*",
        "a": 12,
        "b": 8
      }
    }
  }'

# Advanced math with session
curl -X POST http://localhost:8001/mcp \
  -H "Content-Type: application/json" \
  -H "Accept: application/json, text/event-stream" \
  -H "Mcp-Session-Id: $CALC_SESSION_ID" \
  -d '{
    "jsonrpc": "2.0",
    "id": 4,
    "method": "tools/call",
    "params": {
      "name": "advanced_math",
      "arguments": {
        "function": "cos",
        "value": 3.14159
      }
    }
  }'

# Expression evaluation with session
curl -X POST http://localhost:8001/mcp \
  -H "Content-Type: application/json" \
  -H "Accept: application/json, text/event-stream" \
  -H "Mcp-Session-Id: $CALC_SESSION_ID" \
  -d '{
    "jsonrpc": "2.0",
    "id": 5,
    "method": "tools/call",
    "params": {
      "name": "evaluate_expression",
      "arguments": {
        "expression": "pow(2, 3) + sqrt(25)"
      }
    }
  }' 
```

## Troubleshooting

### Common Issues
1. **Connection refused**: Make sure the MCP server is running
2. **Method not found**: Verify the tool name is correct
3. **Session ID missing**: Server might not support stateful mode
4. **JSON parse error**: Check your JSON syntax in the curl command
5. **Tool call failed**: Check the arguments match the tool's expected parameters

### Port Issues & Cleanup

#### Quick Cleanup Script
```bash
#!/bin/bash
# cleanup_mcp_servers.sh

echo "🧹 Cleaning up MCP servers..."

# Kill all MCP servers
pkill -f "python.*run_http.py" 2>/dev/null

# Wait and check specific ports
sleep 1
for port in 8000 8001 8002; do
  if lsof -Pi :$port -sTCP:LISTEN -t >/dev/null 2>&1; then
    echo "🔫 Killing process on port $port"
    sudo fuser -k ${port}/tcp 2>/dev/null
  fi
done

echo "✅ Cleanup complete"
```

#### Server Management
```bash
# Start servers in background
STATELESS_HTTP=true python run_http.py file --port 8000 &
STATELESS_HTTP=true python run_http.py calculator --port 8001 &
STATELESS_HTTP=true python run_http.py weather --port 8002 &

# Check if servers are running
curl -s http://localhost:8000/mcp >/dev/null && echo "✅ File server running"
curl -s http://localhost:8001/mcp >/dev/null && echo "✅ Calculator server running"
curl -s http://localhost:8002/mcp >/dev/null && echo "✅ Weather server running"

# Kill background servers
kill $(jobs -p)
```

### Notes
- Use `jq` for pretty JSON formatting, or remove `| jq` if not installed
- File tools default to port 8000, calculator tools to port 8001, weather tools to port 8002
- Session IDs are required for stateful mode operations
- Always send the `notifications/initialized` message after session initialization