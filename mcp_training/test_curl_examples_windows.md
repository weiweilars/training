# MCP Tools - Windows PowerShell Testing Examples

This document provides PowerShell commands for testing MCP tools in both stateless and stateful modes on Windows.

## Prerequisites

Start your MCP server first:
```powershell
# For stateless mode (default)
$env:STATELESS_HTTP = "true"
python run_http.py file --port 8003
python run_http.py weather --port 8002
python run_http.py calculator --port 8001

# For stateful mode
$env:STATELESS_HTTP = "false"
python run_http.py file --port 8003
python run_http.py weather --port 8002
python run_http.py calculator --port 8001
```

## Important Variables for Stateful Mode

⚠️ **Critical**: Use the correct session ID variables:
- **File Tools (port 8003)**: Use `$FILE_SESSION_ID` 
- **Calculator Tools (port 8001)**: Use `$CALC_SESSION_ID`
- **Weather Tools (port 8002)**: Use `$WEATHER_SESSION_ID`
- **Never use**: `$SESSION_ID` (this will cause "Unknown tool" errors)

## Stateless Mode Testing

In stateless mode, each request is independent. No session management is required.

### 1. File Tools (port 8003)

#### List Available Tools (PowerShell Method)
```powershell
$headers = @{ "Content-Type" = "application/json" }
$body = @"
{
  "jsonrpc": "2.0",
  "id": 1,
  "method": "tools/list"
}
"@
$response = Invoke-WebRequest -Uri "http://localhost:8003/mcp" -Method POST -Headers $headers -Body $body
$response.Content | ConvertFrom-Json | ConvertTo-Json -Depth 10
```

#### List Available Tools (curl method)
```powershell
curl -X POST http://localhost:8003/mcp `
  -H "Content-Type: application/json" `
  -H "Accept: application/json, text/event-stream" `
  -d '{
    "jsonrpc": "2.0",
    "id": 1,
    "method": "tools/list"
  }'
```

#### List Files
```powershell
$headers = @{ "Content-Type" = "application/json" }
$body = @"
{
  "jsonrpc": "2.0",
  "id": 2,
  "method": "tools/call",
  "params": {
    "name": "list_files",
    "arguments": {}
  }
}
"@
$response = Invoke-WebRequest -Uri "http://localhost:8003/mcp" -Method POST -Headers $headers -Body $body
$response.Content | ConvertFrom-Json | ConvertTo-Json -Depth 10
```

#### Write a File
```powershell
$headers = @{ "Content-Type" = "application/json" }
$body = @"
{
  "jsonrpc": "2.0",
  "id": 3,
  "method": "tools/call",
  "params": {
    "name": "write_file",
    "arguments": {
      "filepath": "test_file.txt",
      "content": "Hello from MCP PowerShell test!"
    }
  }
}
"@
$response = Invoke-WebRequest -Uri "http://localhost:8003/mcp" -Method POST -Headers $headers -Body $body
$response.Content | ConvertFrom-Json | ConvertTo-Json -Depth 10
```

#### Read a File
```powershell
$headers = @{ "Content-Type" = "application/json" }
$body = @"
{
  "jsonrpc": "2.0",
  "id": 4,
  "method": "tools/call",
  "params": {
    "name": "read_file",
    "arguments": {
      "filepath": "test_file.txt"
    }
  }
}
"@
$response = Invoke-WebRequest -Uri "http://localhost:8003/mcp" -Method POST -Headers $headers -Body $body
$response.Content | ConvertFrom-Json | ConvertTo-Json -Depth 10
```

### 2. Weather Tools (port 8002)

Start weather server: `python run_http.py weather --port 8002`

#### List Available Tools
```powershell
$headers = @{ "Content-Type" = "application/json" }
$body = @"
{
  "jsonrpc": "2.0",
  "id": 1,
  "method": "tools/list"
}
"@
$response = Invoke-WebRequest -Uri "http://localhost:8002/mcp" -Method POST -Headers $headers -Body $body
$response.Content | ConvertFrom-Json | ConvertTo-Json -Depth 10
```

#### Get Current Weather
```powershell
$headers = @{ "Content-Type" = "application/json" }
$body = @"
{
  "jsonrpc": "2.0",
  "id": 5,
  "method": "tools/call",
  "params": {
    "name": "get_current_weather",
    "arguments": {
      "city": "London"
    }
  }
}
"@
$response = Invoke-WebRequest -Uri "http://localhost:8002/mcp" -Method POST -Headers $headers -Body $body
$response.Content | ConvertFrom-Json | ConvertTo-Json -Depth 10
```

#### Get Weather Forecast
```powershell
$headers = @{ "Content-Type" = "application/json" }
$body = @"
{
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
}
"@
$response = Invoke-WebRequest -Uri "http://localhost:8002/mcp" -Method POST -Headers $headers -Body $body
$response.Content | ConvertFrom-Json | ConvertTo-Json -Depth 10
```

#### Convert Temperature
```powershell
$headers = @{ "Content-Type" = "application/json" }
$body = @"
{
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
}
"@
$response = Invoke-WebRequest -Uri "http://localhost:8002/mcp" -Method POST -Headers $headers -Body $body
$response.Content | ConvertFrom-Json | ConvertTo-Json -Depth 10
```

### 3. Calculator Tools (port 8001)

#### List Available Tools (PowerShell Method)
```powershell
$headers = @{ "Content-Type" = "application/json" }
$body = @"
{
  "jsonrpc": "2.0",
  "id": 1,
  "method": "tools/list"
}
"@
$response = Invoke-WebRequest -Uri "http://localhost:8001/mcp" -Method POST -Headers $headers -Body $body
$response.Content | ConvertFrom-Json | ConvertTo-Json -Depth 10
```

#### Basic Math Operation (PowerShell Method)
```powershell
$headers = @{ "Content-Type" = "application/json" }
$body = @"
{
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
}
"@
$response = Invoke-WebRequest -Uri "http://localhost:8001/mcp" -Method POST -Headers $headers -Body $body
$response.Content | ConvertFrom-Json | ConvertTo-Json -Depth 10
```

#### Advanced Math Function (curl method)
```powershell
curl -X POST http://localhost:8001/mcp `
  -H "Content-Type: application/json" `
  -H "Accept: application/json, text/event-stream" `
  -d '{
    "jsonrpc": "2.0",
    "id": 3,
    "method": "tools/call",
    "params": {
      "name": "advanced_math",
      "arguments": {
        "function": "sqrt",
        "value": 16
      }
    }
  }'
```

#### Expression Evaluation (curl method)
```powershell
curl -X POST http://localhost:8001/mcp `
  -H "Content-Type: application/json" `
  -H "Accept: application/json, text/event-stream" `
  -d '{
    "jsonrpc": "2.0",
    "id": 4,
    "method": "tools/call",
    "params": {
      "name": "evaluate_expression",
      "arguments": {
        "expression": "2 + 3 * 4"
      }
    }
  }'
```

## Stateful Mode Testing

In stateful mode, you must establish a session first, then maintain it across requests.

### 1. File Tools (Stateful - port 8003)

Start server: `$env:STATELESS_HTTP="false"; python run_http.py file --port 8003`

#### Initialize Session
```powershell
# Step 1: Initialize file session
$headers = @{ "Content-Type" = "application/json"; "Accept" = "application/json, text/event-stream" }
$initBody = @"
{
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
      "name": "powershell-file-client",
      "version": "1.0.0"
    }
  }
}
"@

$fileResponse = Invoke-WebRequest -Uri "http://localhost:8003/mcp" -Method POST -Headers $headers -Body $initBody

# Extract file session ID from headers
$FILE_SESSION_ID = $fileResponse.Headers.'mcp-session-id'
Write-Output "File Session ID: $FILE_SESSION_ID"

# Send initialized notification
$notifyHeaders = $headers.Clone()
$notifyHeaders.'Mcp-Session-Id' = $FILE_SESSION_ID
$notifyBody = @"
{
  "jsonrpc": "2.0",
  "method": "notifications/initialized"
}
"@
Invoke-WebRequest -Uri "http://localhost:8003/mcp" -Method POST -Headers $notifyHeaders -Body $notifyBody | Out-Null
```

#### Test File Operations with Session
```powershell
# List available tools
$sessionHeaders = @{ 
    "Content-Type" = "application/json"
    "Accept" = "application/json, text/event-stream"
    "Mcp-Session-Id" = $FILE_SESSION_ID
}

$toolsBody = @"
{
  "jsonrpc": "2.0",
  "id": 2,
  "method": "tools/list"
}
"@
$response = Invoke-WebRequest -Uri "http://localhost:8003/mcp" -Method POST -Headers $sessionHeaders -Body $toolsBody
$response.Content | ConvertFrom-Json | ConvertTo-Json -Depth 10

# List files
$listBody = @"
{
  "jsonrpc": "2.0",
  "id": 3,
  "method": "tools/call",
  "params": {
    "name": "list_files",
    "arguments": {}
  }
}
"@
$response = Invoke-WebRequest -Uri "http://localhost:8003/mcp" -Method POST -Headers $sessionHeaders -Body $listBody
$response.Content | ConvertFrom-Json | ConvertTo-Json -Depth 10

# Write file
$writeBody = @"
{
  "jsonrpc": "2.0",
  "id": 4,
  "method": "tools/call",
  "params": {
    "name": "write_file",
    "arguments": {
      "filepath": "stateful_test.txt",
      "content": "Hello from stateful MCP PowerShell test!"
    }
  }
}
"@
$response = Invoke-WebRequest -Uri "http://localhost:8003/mcp" -Method POST -Headers $sessionHeaders -Body $writeBody
$response.Content | ConvertFrom-Json | ConvertTo-Json -Depth 10

# Read file
$readBody = @"
{
  "jsonrpc": "2.0",
  "id": 5,
  "method": "tools/call",
  "params": {
    "name": "read_file",
    "arguments": {
      "filepath": "stateful_test.txt"
    }
  }
}
"@
$response = Invoke-WebRequest -Uri "http://localhost:8003/mcp" -Method POST -Headers $sessionHeaders -Body $readBody
$response.Content | ConvertFrom-Json | ConvertTo-Json -Depth 10
```

#### Complete Stateful File Test Script
```powershell
# Save as: Test-StatefulFileTools.ps1
param(
    [string]$ServerUrl = "http://localhost:8003"
)

Write-Output "📁 Starting stateful file tools test..."

# Initialize session
$headers = @{ "Content-Type" = "application/json"; "Accept" = "application/json, text/event-stream" }
$initBody = @"
{
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
      "name": "powershell-file-client",
      "version": "1.0.0"
    }
  }
}
"@

try {
    $fileResponse = Invoke-WebRequest -Uri "$ServerUrl/mcp" -Method POST -Headers $headers -Body $initBody
    $FILE_SESSION_ID = $fileResponse.Headers.'mcp-session-id'
    
    if (-not $FILE_SESSION_ID) {
        Write-Error "❌ Failed to get session ID for file tools"
        return
    }
    
    Write-Output "✅ File Session ID: $FILE_SESSION_ID"
    
    # Send notifications
    $sessionHeaders = $headers.Clone()
    $sessionHeaders.'Mcp-Session-Id' = $FILE_SESSION_ID
    
    $notifyBody = @"
{
  "jsonrpc": "2.0",
  "method": "notifications/initialized"
}
"@
    Invoke-WebRequest -Uri "$ServerUrl/mcp" -Method POST -Headers $sessionHeaders -Body $notifyBody | Out-Null
    
    Write-Output "📋 Testing file operations..."
    
    # Test multiple file operations
    Write-Output "  📝 Writing test files..."
    for ($i = 1; $i -le 3; $i++) {
        $timestamp = Get-Date -Format "yyyy-MM-dd HH:mm:ss"
        $writeBody = @"
{
  "jsonrpc": "2.0",
  "id": $($i + 10),
  "method": "tools/call",
  "params": {
    "name": "write_file",
    "arguments": {
      "filepath": "test_file_$i.txt",
      "content": "This is test file #$i created in stateful mode`nSession ID: $FILE_SESSION_ID`nTimestamp: $timestamp"
    }
  }
}
"@
        $response = Invoke-WebRequest -Uri "$ServerUrl/mcp" -Method POST -Headers $sessionHeaders -Body $writeBody
        $result = $response.Content | ConvertFrom-Json
        $filepath = $result.result.content[0].text | ConvertFrom-Json | Select-Object -ExpandProperty filepath
        Write-Output "    ✅ Created: $filepath"
    }
    
    Write-Output "  📖 Reading files back..."
    for ($i = 1; $i -le 3; $i++) {
        $readBody = @"
{
  "jsonrpc": "2.0",
  "id": $($i + 20),
  "method": "tools/call",
  "params": {
    "name": "read_file",
    "arguments": {
      "filepath": "test_file_$i.txt"
    }
  }
}
"@
        $response = Invoke-WebRequest -Uri "$ServerUrl/mcp" -Method POST -Headers $sessionHeaders -Body $readBody
        $result = $response.Content | ConvertFrom-Json
        $content = $result.result.content[0].text | ConvertFrom-Json | Select-Object -ExpandProperty content
        $firstLine = $content.Split("`n")[0]
        Write-Output "    📄 test_file_$i.txt: $firstLine"
    }
    
    Write-Output "  📊 Final file listing..."
    $listBody = @"
{
  "jsonrpc": "2.0",
  "id": 30,
  "method": "tools/call",
  "params": {
    "name": "list_files",
    "arguments": {}
  }
}
"@
    $response = Invoke-WebRequest -Uri "$ServerUrl/mcp" -Method POST -Headers $sessionHeaders -Body $listBody
    $result = $response.Content | ConvertFrom-Json
    $fileCount = $result.result.content[0].text | ConvertFrom-Json | Select-Object -ExpandProperty file_count
    Write-Output "    📁 Total files: $fileCount"
    
    Write-Output "✅ Stateful file tools test completed"
}
catch {
    Write-Error "Test failed: $($_.Exception.Message)"
}
```

### 2. Weather Tools (Stateful - port 8002)

Start server: `$env:STATELESS_HTTP="false"; python run_http.py weather --port 8002`

#### Initialize Session
```powershell
# Step 1: Initialize weather session
$headers = @{ "Content-Type" = "application/json"; "Accept" = "application/json, text/event-stream" }
$initBody = @"
{
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
      "name": "powershell-weather-client",
      "version": "1.0.0"
    }
  }
}
"@

$weatherResponse = Invoke-WebRequest -Uri "http://localhost:8002/mcp" -Method POST -Headers $headers -Body $initBody

# Extract weather session ID
$WEATHER_SESSION_ID = $weatherResponse.Headers.'mcp-session-id'
Write-Output "Weather Session ID: $WEATHER_SESSION_ID"

# Send initialized notification
$notifyHeaders = $headers.Clone()
$notifyHeaders.'Mcp-Session-Id' = $WEATHER_SESSION_ID
$notifyBody = @"
{
  "jsonrpc": "2.0",
  "method": "notifications/initialized"
}
"@
Invoke-WebRequest -Uri "http://localhost:8002/mcp" -Method POST -Headers $notifyHeaders -Body $notifyBody | Out-Null
```

#### Test Weather Operations with Session
```powershell
# List weather tools
$sessionHeaders = @{ 
    "Content-Type" = "application/json"
    "Accept" = "application/json, text/event-stream"
    "Mcp-Session-Id" = $WEATHER_SESSION_ID
}

$toolsBody = @"
{
  "jsonrpc": "2.0",
  "id": 2,
  "method": "tools/list"
}
"@
$response = Invoke-WebRequest -Uri "http://localhost:8002/mcp" -Method POST -Headers $sessionHeaders -Body $toolsBody
$response.Content | ConvertFrom-Json | ConvertTo-Json -Depth 10

# Get current weather
$weatherBody = @"
{
  "jsonrpc": "2.0",
  "id": 3,
  "method": "tools/call",
  "params": {
    "name": "get_current_weather",
    "arguments": {
      "city": "Tokyo"
    }
  }
}
"@
$response = Invoke-WebRequest -Uri "http://localhost:8002/mcp" -Method POST -Headers $sessionHeaders -Body $weatherBody
$response.Content | ConvertFrom-Json | ConvertTo-Json -Depth 10

# Get weather forecast
$forecastBody = @"
{
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
}
"@
$response = Invoke-WebRequest -Uri "http://localhost:8002/mcp" -Method POST -Headers $sessionHeaders -Body $forecastBody
$response.Content | ConvertFrom-Json | ConvertTo-Json -Depth 10

# Convert temperature
$convertBody = @"
{
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
}
"@
$response = Invoke-WebRequest -Uri "http://localhost:8002/mcp" -Method POST -Headers $sessionHeaders -Body $convertBody
$response.Content | ConvertFrom-Json | ConvertTo-Json -Depth 10
```

### 3. Calculator Tools (Stateful - port 8001)

#### Initialize Session
```powershell
# Step 1: Initialize calculator session
$initBody = @"
{
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
      "name": "powershell-calculator-client",
      "version": "1.0.0"
    }
  }
}
"@

$headers = @{ "Content-Type" = "application/json"; "Accept" = "application/json, text/event-stream" }
$initResponse = Invoke-WebRequest -Uri "http://localhost:8001/mcp" -Method POST -Headers $headers -Body $initBody

# Extract session ID from response headers
$CALC_SESSION_ID = $initResponse.Headers.'mcp-session-id'[0]
Write-Output "Calculator Session ID: $CALC_SESSION_ID"

# Step 2: Send notifications/initialized
$notificationBody = @"
{
  "jsonrpc": "2.0",
  "method": "notifications/initialized"
}
"@

$sessionHeaders = @{ "Content-Type" = "application/json"; "Accept" = "application/json, text/event-stream"; "Mcp-Session-Id" = $CALC_SESSION_ID }
$notificationResponse = Invoke-WebRequest -Uri "http://localhost:8001/mcp" -Method POST -Headers $sessionHeaders -Body $notificationBody
```

#### Test Calculator Operations with Session
```powershell
# Basic math with session
$mathBody = @"
{
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
}
"@
$mathResponse = Invoke-WebRequest -Uri "http://localhost:8001/mcp" -Method POST -Headers $sessionHeaders -Body $mathBody
$mathResponse.Content | ConvertFrom-Json | ConvertTo-Json -Depth 10

# Advanced math with session
$advancedBody = @"
{
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
}
"@
$advancedResponse = Invoke-WebRequest -Uri "http://localhost:8001/mcp" -Method POST -Headers $sessionHeaders -Body $advancedBody
$advancedResponse.Content | ConvertFrom-Json | ConvertTo-Json -Depth 10

# Expression evaluation with session
$expressionBody = @"
{
  "jsonrpc": "2.0",
  "id": 5,
  "method": "tools/call",
  "params": {
    "name": "evaluate_expression",
    "arguments": {
      "expression": "pow(2, 3) + sqrt(25)"
    }
  }
}
"@
$expressionResponse = Invoke-WebRequest -Uri "http://localhost:8001/mcp" -Method POST -Headers $sessionHeaders -Body $expressionBody
$expressionResponse.Content | ConvertFrom-Json | ConvertTo-Json -Depth 10
```

## Complete Test Scripts

### File Tools Test Script
```powershell
# Save as: Test-FileTools.ps1
param(
    [string]$ServerUrl = "http://localhost:8003"
)

Write-Output "🔄 Testing File Tools (Stateless and Stateful modes)..."

# Test stateless mode
Write-Output "📁 Testing Stateless File Tools..."
Write-Output "  🔍 Listing available tools..."

$headers = @{ "Content-Type" = "application/json" }
$body = '{"jsonrpc": "2.0", "id": 1, "method": "tools/list"}'

try {
    $response = Invoke-WebRequest -Uri "$ServerUrl/mcp" -Method POST -Headers $headers -Body $body
    $result = $response.Content | ConvertFrom-Json
    $tools = $result.result.tools | ForEach-Object { "    - $($_.name)" }
    $tools | Write-Output
}
catch {
    Write-Output "❌ Stateless mode test failed: $($_.Exception.Message)"
}

# Test stateful mode
Write-Output "📁 Testing Stateful File Tools..."
$headers = @{ "Content-Type" = "application/json"; "Accept" = "application/json, text/event-stream" }
$initBody = @"
{
  "jsonrpc": "2.0",
  "id": 1,
  "method": "initialize",
  "params": {
    "protocolVersion": "2024-11-05",
    "capabilities": {"roots": {"listChanged": true}, "sampling": {}},
    "clientInfo": {"name": "powershell-file-test", "version": "1.0.0"}
  }
}
"@

try {
    $fileResponse = Invoke-WebRequest -Uri "$ServerUrl/mcp" -Method POST -Headers $headers -Body $initBody
    $FILE_SESSION_ID = $fileResponse.Headers.'mcp-session-id'
    
    if ($FILE_SESSION_ID) {
        Write-Output "✅ Got file session ID: $FILE_SESSION_ID"
        
        $sessionHeaders = $headers.Clone()
        $sessionHeaders.'Mcp-Session-Id' = $FILE_SESSION_ID
        
        $notifyBody = '{"jsonrpc": "2.0", "method": "notifications/initialized"}'
        Invoke-WebRequest -Uri "$ServerUrl/mcp" -Method POST -Headers $sessionHeaders -Body $notifyBody | Out-Null
        
        Write-Output "  🔍 Listing tools with session..."
        $toolsBody = '{"jsonrpc": "2.0", "id": 2, "method": "tools/list"}'
        $response = Invoke-WebRequest -Uri "$ServerUrl/mcp" -Method POST -Headers $sessionHeaders -Body $toolsBody
        $result = $response.Content | ConvertFrom-Json
        $tools = $result.result.tools | ForEach-Object { "    - $($_.name)" }
        $tools | Write-Output
        
        Write-Output "  📝 Testing file operations..."
        $writeBody = @"
{
  "jsonrpc": "2.0",
  "id": 3,
  "method": "tools/call",
  "params": {
    "name": "write_file",
    "arguments": {
      "filepath": "session_test.txt",
      "content": "File created with session ID: $FILE_SESSION_ID"
    }
  }
}
"@
        $response = Invoke-WebRequest -Uri "$ServerUrl/mcp" -Method POST -Headers $sessionHeaders -Body $writeBody
        $result = $response.Content | ConvertFrom-Json
        $filepath = $result.result.content[0].text | ConvertFrom-Json | Select-Object -ExpandProperty filepath
        Write-Output "    ✅ $filepath created"
        
        $readBody = @"
{
  "jsonrpc": "2.0",
  "id": 4,
  "method": "tools/call",
  "params": {
    "name": "read_file",
    "arguments": {
      "filepath": "session_test.txt"
    }
  }
}
"@
        $response = Invoke-WebRequest -Uri "$ServerUrl/mcp" -Method POST -Headers $sessionHeaders -Body $readBody
        $result = $response.Content | ConvertFrom-Json
        $content = $result.result.content[0].text | ConvertFrom-Json | Select-Object -ExpandProperty content
        Write-Output "    📖 File content: $content"
    }
    else {
        Write-Output "❌ Server is in stateless mode"
    }
}
catch {
    Write-Output "❌ Stateful mode test failed: $($_.Exception.Message)"
}

Write-Output "✅ File tools test completed"
```

### Weather Tools Test Script
```powershell
# Save as: Test-WeatherTools.ps1
param(
    [string]$ServerUrl = "http://localhost:8002"
)

Write-Output "🌤️ Testing Weather Tools (Stateless and Stateful modes)..."

# Test stateless mode
Write-Output "🌍 Testing Stateless Weather Tools..."
Write-Output "  🔍 Listing available tools..."

$headers = @{ "Content-Type" = "application/json" }
$body = '{"jsonrpc": "2.0", "id": 1, "method": "tools/list"}'

try {
    $response = Invoke-WebRequest -Uri "$ServerUrl/mcp" -Method POST -Headers $headers -Body $body
    $result = $response.Content | ConvertFrom-Json
    $tools = $result.result.tools | ForEach-Object { "    - $($_.name)" }
    $tools | Write-Output
}
catch {
    Write-Output "❌ Stateless mode test failed: $($_.Exception.Message)"
}

# Test stateful mode
Write-Output "🌍 Testing Stateful Weather Tools..."
$headers = @{ "Content-Type" = "application/json"; "Accept" = "application/json, text/event-stream" }
$initBody = @"
{
  "jsonrpc": "2.0",
  "id": 1,
  "method": "initialize",
  "params": {
    "protocolVersion": "2024-11-05",
    "capabilities": {"roots": {"listChanged": true}, "sampling": {}},
    "clientInfo": {"name": "powershell-weather-test", "version": "1.0.0"}
  }
}
"@

try {
    $weatherResponse = Invoke-WebRequest -Uri "$ServerUrl/mcp" -Method POST -Headers $headers -Body $initBody
    $WEATHER_SESSION_ID = $weatherResponse.Headers.'mcp-session-id'
    
    if ($WEATHER_SESSION_ID) {
        Write-Output "✅ Got weather session ID: $WEATHER_SESSION_ID"
        
        $sessionHeaders = $headers.Clone()
        $sessionHeaders.'Mcp-Session-Id' = $WEATHER_SESSION_ID
        
        $notifyBody = '{"jsonrpc": "2.0", "method": "notifications/initialized"}'
        Invoke-WebRequest -Uri "$ServerUrl/mcp" -Method POST -Headers $sessionHeaders -Body $notifyBody | Out-Null
        
        Write-Output "  🔍 Listing tools with session..."
        $toolsBody = '{"jsonrpc": "2.0", "id": 2, "method": "tools/list"}'
        $response = Invoke-WebRequest -Uri "$ServerUrl/mcp" -Method POST -Headers $sessionHeaders -Body $toolsBody
        $result = $response.Content | ConvertFrom-Json
        $tools = $result.result.tools | ForEach-Object { "    - $($_.name)" }
        $tools | Write-Output
    }
    else {
        Write-Output "❌ Weather server is in stateless mode"
    }
}
catch {
    Write-Output "❌ Stateful mode test failed: $($_.Exception.Message)"
}

Write-Output "✅ Weather tools test completed"
```

Make scripts executable:
```powershell
# Set execution policy if needed
Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser

# Run the scripts
.\Test-FileTools.ps1
.\Test-WeatherTools.ps1
```

## Response Formats

### Success Response
```json
{
  "jsonrpc": "2.0",
  "id": 2,
  "result": {
    "content": [
      {
        "type": "text",
        "text": "{\"directory\": \"./workspace\", \"file_count\": 1, \"files\": [...], \"listed_at\": \"2024-01-01T12:00:00\"}"
      }
    ]
  }
}
```

### Error Response
```json
{
  "jsonrpc": "2.0",
  "id": 2,
  "error": {
    "code": -32601,
    "message": "Method not found"
  }
}
```

## Troubleshooting

### Common Issues
1. **Connection refused**: Make sure the MCP server is running
2. **Method not found**: Verify the tool name is correct
3. **Session ID missing**: Server might not support stateful mode
4. **JSON parse error**: Check your JSON syntax in the PowerShell command
5. **Tool call failed**: Check the arguments match the tool's expected parameters
6. **"Unknown tool" error**: Make sure you're using the correct session ID variable:
   - For file tools: Use `$FILE_SESSION_ID` (not `$SESSION_ID`)
   - For weather tools: Use `$WEATHER_SESSION_ID`
7. **Session not initialized**: Make sure you run the initialization steps first:
   ```powershell
   # For file tools - must run this first:
   $fileResponse = Invoke-WebRequest -Uri "http://localhost:8003/mcp" ...
   $FILE_SESSION_ID = $fileResponse.Headers.'mcp-session-id'
   
   # For weather tools - must run this first:
   $weatherResponse = Invoke-WebRequest -Uri "http://localhost:8002/mcp" ...
   $WEATHER_SESSION_ID = $weatherResponse.Headers.'mcp-session-id'
   ```

### Windows PowerShell Specific Issues

#### SSL/TLS Issues
```powershell
# Bypass SSL certificate validation (for testing only)
[System.Net.ServicePointManager]::ServerCertificateValidationCallback = {$true}

# Set TLS version
[System.Net.ServicePointManager]::SecurityProtocol = [System.Net.SecurityProtocolType]::Tls12
```

#### Execution Policy Issues
```powershell
# Check current execution policy
Get-ExecutionPolicy

# Set execution policy for current user
Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser

# Run script with bypass (one-time)
PowerShell -ExecutionPolicy Bypass -File ".\Test-FileTools.ps1"
```

#### JSON Formatting Issues
```powershell
# When dealing with complex JSON, use here-strings (@" ... "@)
$body = @"
{
  "jsonrpc": "2.0",
  "id": 1,
  "method": "tools/list"
}
"@

# For single-line JSON, escape quotes carefully
$body = '{"jsonrpc": "2.0", "id": 1, "method": "tools/list"}'
```

### Port Issues & Cleanup

#### Quick Cleanup Script
```powershell
# Save as: Cleanup-MCPServers.ps1
Write-Output "🧹 Cleaning up MCP servers..."

# Kill all MCP servers
Get-Process | Where-Object {
    $_.ProcessName -eq "python" -and 
    $_.CommandLine -like "*run_http.py*"
} | Stop-Process -Force

# Wait and check specific ports
Start-Sleep -Seconds 1
foreach ($port in @(8000, 8001, 8002, 8003)) {
    try {
        $connection = Get-NetTCPConnection -LocalPort $port -ErrorAction SilentlyContinue
        if ($connection) {
            Write-Output "🔫 Killing process on port $port"
            $processId = $connection.OwningProcess
            Stop-Process -Id $processId -Force
        }
    }
    catch {
        # Port not in use, continue
    }
}

Write-Output "✅ Cleanup complete"
```

#### Server Management
```powershell
# Start servers in background
$fileJob = Start-Job -ScriptBlock { python run_http.py file --port 8003 }
$calcJob = Start-Job -ScriptBlock { python run_http.py calculator --port 8001 }
$weatherJob = Start-Job -ScriptBlock { python run_http.py weather --port 8002 }

# Check if servers are running
try {
    $response = Invoke-WebRequest -Uri "http://localhost:8003/mcp" -Method GET -TimeoutSec 5
    Write-Output "✅ File server running"
}
catch {
    Write-Output "❌ File server not responding"
}

try {
    $response = Invoke-WebRequest -Uri "http://localhost:8001/mcp" -Method GET -TimeoutSec 5
    Write-Output "✅ Calculator server running"
}
catch {
    Write-Output "❌ Calculator server not responding"
}

try {
    $response = Invoke-WebRequest -Uri "http://localhost:8002/mcp" -Method GET -TimeoutSec 5
    Write-Output "✅ Weather server running"
}
catch {
    Write-Output "❌ Weather server not responding"
}

# Stop background jobs
Get-Job | Stop-Job
Get-Job | Remove-Job
```

### Notes
- Use `ConvertFrom-Json | ConvertTo-Json -Depth 10` for pretty JSON formatting
- File tools default to port 8003, calculator tools to port 8001, weather tools to port 8002
- Session IDs are required for stateful mode operations
- Always send the `notifications/initialized` message after session initialization
- PowerShell variables use `$` prefix, headers are case-sensitive
- Use `@{ }` for hashtables (headers) and `@" "@` for multi-line strings (JSON bodies)