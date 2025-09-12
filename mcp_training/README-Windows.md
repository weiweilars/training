# MCP Tools Training Materials - Windows PowerShell Guide

Simplified, single-page examples of MCP (Model Context Protocol) tools for training purposes - **Windows PowerShell Edition**.

## Quick Start

```powershell
# Install dependencies (optional)
pip install fastmcp

# List available tools
python run_http.py --list-tools

# Start a tool server
python run_http.py file

# Test the server (requires curl or Invoke-WebRequest)
# Option 1: Using curl (if available)
curl -X POST http://localhost:8000/mcp `
  -H "Content-Type: application/json" `
  -d '{"jsonrpc": "2.0", "id": 1, "method": "tools/list"}'

# Option 2: Using PowerShell Invoke-WebRequest
$headers = @{ "Content-Type" = "application/json" }
$body = '{"jsonrpc": "2.0", "id": 1, "method": "tools/list"}'
Invoke-WebRequest -Uri "http://localhost:8000/mcp" -Method POST -Headers $headers -Body $body
```

## Available Tools

| Tool | File | Purpose | Key Functions |
|------|------|---------|---------------|
| **File** | `simple_file_tool.py` | File operations | `list_files`, `read_file`, `write_file` |
| **Weather** | `simple_weather_tool.py` | Weather info (mock data) | `get_current_weather`, `get_weather_forecast`, `convert_temperature` |

## Usage

### Universal Launcher
Use `run_http.py` to start any tool as an HTTP server:

```powershell
# Basic usage (stateless mode, port 8000)
python run_http.py file
python run_http.py weather --host 0.0.0.0 --port 8002

# Server modes
python run_http.py file                        # Stateless (default)
$env:STATELESS_HTTP="false"; python run_http.py file  # Stateful (session-based)

# Alternative syntax for environment variables
Set-Variable -Name "STATELESS_HTTP" -Value "false"
python run_http.py file
```

### Direct Execution
Run tools directly in stdio mode:
```powershell
python simple_file_tool.py
python simple_weather_tool.py
```

## Testing

### Basic Testing with PowerShell

```powershell
# Start server
python run_http.py file

# List tools using Invoke-WebRequest
$headers = @{ "Content-Type" = "application/json" }
$body = '{"jsonrpc": "2.0", "id": 1, "method": "tools/list"}'
$response = Invoke-WebRequest -Uri "http://localhost:8000/mcp" -Method POST -Headers $headers -Body $body
$response.Content | ConvertFrom-Json | ConvertTo-Json -Depth 10

# Call a tool
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
$response = Invoke-WebRequest -Uri "http://localhost:8000/mcp" -Method POST -Headers $headers -Body $body
$response.Content | ConvertFrom-Json | ConvertTo-Json -Depth 10
```

### Using curl in PowerShell (if curl is available)

```powershell
# List tools
curl -X POST http://localhost:8000/mcp `
  -H "Content-Type: application/json" `
  -d '{"jsonrpc": "2.0", "id": 1, "method": "tools/list"}'

# Call a tool
curl -X POST http://localhost:8000/mcp `
  -H "Content-Type: application/json" `
  -d '{"jsonrpc": "2.0", "id": 2, "method": "tools/call", "params": {"name": "list_files", "arguments": {}}}'
```

### Complete Testing Guide
See **[test_curl_examples_windows.md](test_curl_examples_windows.md)** for:
- All tools with various arguments
- Both stateless and stateful modes
- Ready-to-use PowerShell scripts

## Setup

### Requirements
- Python 3.7+
- `fastmcp` package (required)
- PowerShell 5.1+ or PowerShell Core 7+

### Installation
```powershell
# Optional: Create virtual environment
python -m venv venv
./venv/Scripts/Activate.ps1

# Install required dependencies
pip install -r requirements.txt
# OR: pip install fastmcp

# Verify setup
python run_http.py --list-tools
```

### Configuration (Optional)
```powershell
# Server mode (only set if you want stateful mode)
$env:STATELESS_HTTP = "false"                 # Default is stateless

# Weather settings  
$env:WEATHER_UNITS = "celsius"                
$env:WEATHER_API_KEY = "your_api_key_here"    # For real weather API

# Alternative: Use Set-Variable for session scope
Set-Variable -Name "STATELESS_HTTP" -Value "false" -Scope Global
```

## Troubleshooting

### Port Issues
```powershell
# Find what's using the port
netstat -an | findstr ":8000"
Get-NetTCPConnection -LocalPort 8000 -ErrorAction SilentlyContinue

# Kill process using port
$processId = (Get-NetTCPConnection -LocalPort 8000).OwningProcess
Stop-Process -Id $processId -Force

# Use different port
python run_http.py file --port 8001

# Clean up all MCP servers
Get-Process | Where-Object {$_.ProcessName -eq "python" -and $_.CommandLine -like "*run_http.py*"} | Stop-Process -Force
```

### Background Jobs
```powershell
# Start server in background
Start-Job -ScriptBlock { python run_http.py file }

# List background jobs
Get-Job

# Stop specific job
Stop-Job -Id 1

# Stop all jobs
Get-Job | Stop-Job

# Remove completed jobs
Get-Job | Remove-Job
```

### PowerShell-Specific Solutions
```powershell
# If Invoke-WebRequest has SSL issues
[System.Net.ServicePointManager]::ServerCertificateValidationCallback = {$true}

# Set TLS version if needed
[System.Net.ServicePointManager]::SecurityProtocol = [System.Net.SecurityProtocolType]::Tls12

# For older PowerShell versions, install curl
# Via Chocolatey: choco install curl
# Via Scoop: scoop install curl
```

## PowerShell Helper Functions

### Create reusable functions for testing:

```powershell
# Add to your PowerShell profile or script
function Test-MCPTool {
    param(
        [string]$Url = "http://localhost:8000/mcp",
        [string]$Method = "tools/list",
        [int]$Id = 1,
        [hashtable]$Params = @{}
    )
    
    $headers = @{ "Content-Type" = "application/json" }
    $body = @{
        jsonrpc = "2.0"
        id = $Id
        method = $Method
    }
    
    if ($Params.Count -gt 0) {
        $body.params = $Params
    }
    
    $jsonBody = $body | ConvertTo-Json -Depth 10
    
    try {
        $response = Invoke-WebRequest -Uri $Url -Method POST -Headers $headers -Body $jsonBody
        $response.Content | ConvertFrom-Json | ConvertTo-Json -Depth 10
    }
    catch {
        Write-Error "Request failed: $($_.Exception.Message)"
    }
}

# Usage examples:
# Test-MCPTool
# Test-MCPTool -Method "tools/call" -Params @{ name = "list_files"; arguments = @{} }
```

## Features & Training

### Key Features
- **Single-page design** - Each tool in one file for easy learning
- **Minimal dependencies** - Standard library + FastMCP
- **Universal runner** - One script runs any tool  
- **Dual modes** - Stateless (simple) & stateful (session-based)
- **Safety & mocking** - Safe database queries, mock weather data
- **Windows compatibility** - PowerShell scripts and commands

### MCP Server Modes
| Mode | Usage | Best For |
|------|-------|----------|
| **Stateless** (default) | `python run_http.py file` | Simple testing, PowerShell examples |
| **Stateful** | `$env:STATELESS_HTTP="false"; python run_http.py file` | Advanced clients, sessions |

### Training Use Cases
- Learn MCP tool patterns and FastMCP framework
- Practice HTTP server deployment and client communication using PowerShell
- Explore different tool types (file, weather) with Windows-native commands
- Develop custom MCP tools using these as templates
- Master PowerShell web request techniques for API testing

## Windows-Specific Notes

1. **PowerShell Execution Policy**: You may need to run `Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser` to run scripts
2. **Path Separators**: Use forward slashes in URLs, backslashes in local paths
3. **JSON Escaping**: Be careful with quotes in JSON strings within PowerShell
4. **Environment Variables**: Use `$env:VARIABLE_NAME` syntax
5. **Background Processes**: Use `Start-Job` instead of `&` for background execution