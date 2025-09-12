# MCP Tools Training Materials

Simplified, single-page examples of MCP (Model Context Protocol) tools for training purposes.

## Quick Start

```bash
# Install dependencies (optional)
pip install fastmcp

# List available tools
python run_http.py --list-tools

# Start a tool server
python run_http.py file

# Test the server
curl -X POST http://localhost:8000/mcp \
  -H "Content-Type: application/json" \
  -d '{"jsonrpc": "2.0", "id": 1, "method": "tools/list"}' | jq
```

## Available Tools

| Tool | File | Purpose | Key Functions |
|------|------|---------|---------------|
| **File** | `simple_file_tool.py` | File operations | `list_files`, `read_file`, `write_file` |
| **Weather** | `simple_weather_tool.py` | Weather info (mock data) | `get_current_weather`, `get_weather_forecast`, `convert_temperature` |
| **Calculator** | `simple_calculator_tool.py` | Mathematical operations | `basic_math`, `advanced_math`, `evaluate_expression` |

## Usage

### Universal Launcher
Use `run_http.py` to start any tool as an HTTP server:

```bash
# Basic usage (stateless mode, port 8000)
python run_http.py file
python run_http.py weather --host 0.0.0.0 --port 8002
python run_http.py calculator --port 8003

# Server modes
python run_http.py file                        # Stateless (default)
STATELESS_HTTP=false python run_http.py file  # Stateful (session-based)
```

### Direct Execution
Run tools directly in stdio mode:
```bash
python simple_file_tool.py
python simple_weather_tool.py
python simple_calculator_tool.py
```

## Testing

### Basic Testing
```bash
# Start server
python run_http.py file

# List tools
curl -X POST http://localhost:8000/mcp \
  -H "Content-Type: application/json" \
  -d '{"jsonrpc": "2.0", "id": 1, "method": "tools/list"}' | jq

# Call a tool
curl -X POST http://localhost:8000/mcp \
  -H "Content-Type: application/json" \
  -d '{"jsonrpc": "2.0", "id": 2, "method": "tools/call", 
       "params": {"name": "list_files", "arguments": {}}}' | jq
```

### Complete Testing Guide
See **[test_curl_examples.md](test_curl_examples.md)** for:
- All tools with various arguments
- Both stateless and stateful modes
- Ready-to-use bash scripts

## Setup

### Requirements
- Python 3.7+
- `fastmcp` package (required)

### Installation
```bash
# Optional: Create virtual environment
python -m venv venv && source venv/bin/activate

# Install required dependencies
pip install -r requirements.txt
# OR: pip install fastmcp

# Verify setup
python run_http.py --list-tools
```

### Configuration (Optional)
```bash
# Server mode (only set if you want stateful mode)
export STATELESS_HTTP="true"                 # Default is stateless

# Weather settings  
export WEATHER_UNITS="celsius"                
export WEATHER_API_KEY="your_api_key_here"    # For real weather API

# Calculator settings
export CALC_PRECISION="6"                     # Decimal places for results
```

## Troubleshooting

### Port Issues
```bash
# Find what's using the port
lsof -i :8000

# Kill process or use different port
kill <PID>
python run_http.py file --port 8001

# Clean up all MCP servers
pkill -f "python.*run_http.py"
```

### Background Jobs
```bash
jobs                    # List background jobs
kill %1                 # Kill specific job
kill $(jobs -p)         # Kill all background jobs
```

## Features & Training

### Key Features
- **Single-page design** - Each tool in one file for easy learning
- **Minimal dependencies** - Standard library + FastMCP
- **Universal runner** - One script runs any tool  
- **Dual modes** - Stateless (simple) & stateful (session-based)
- **Safety & mocking** - Safe database queries, mock weather data

### MCP Server Modes
| Mode | Usage | Best For |
|------|-------|----------|
| **Stateless** (default) | `python run_http.py file` | Simple testing, curl examples |
| **Stateful** | `STATELESS_HTTP=false python run_http.py file` | Advanced clients, sessions |

### Training Use Cases
- Learn MCP tool patterns and FastMCP framework
- Practice HTTP server deployment and client communication  
- Explore different tool types (file, weather, calculator)
- Develop custom MCP tools using these as templates