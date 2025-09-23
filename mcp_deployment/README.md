# MCP Deployment - Production Ready Server

A production-ready deployment server for MCP (Model Context Protocol) tools with **smart folder scanning**, **automatic environment detection**, streaming HTTP support, authentication, monitoring, and middleware capabilities.

## 🎯 Key Features

- **🔍 Smart Folder Scanning**: Automatically detects FastMCP instances with ANY variable name (`mcp`, `weather_api`, `math_server`, etc.)
- **🌍 Environment Auto-Detection**: Scans code for required environment variables and validates them
- **📡 Streaming HTTP Support**: Full support for streaming responses via JSON-RPC
- **🔐 Multiple Authentication Methods**: Bearer tokens, API keys, JWT, and Basic auth
- **📊 Monitoring & Metrics**: Built-in request monitoring with Prometheus export
- **🛡️ Security**: CORS, rate limiting, security headers, input validation
- **🚀 Production Ready**: Docker support, health checks, environment-based configuration

## 🚀 Quick Start

### 1. Setup Environment

```bash
# Create Python 3.11 virtual environment
python3.11 -m venv venv
source venv/bin/activate

# Install all dependencies (including FastMCP)
pip install -r requirements.txt
```

### 2. Test with Sample Tools

The deployment includes two test tools to demonstrate folder scanning:

```bash
# Activate virtual environment
source venv/bin/activate

# Test weather service (variable name: weather_api)
WEATHER_API_KEY=demo123 SERVICE_NAME=weather-test DEBUG_MODE=true WEATHER_UNITS=celsius RATE_LIMIT=100 python main.py test_tools/weather_service --port 8003

# Test calculator service (variable name: math_server)
CALC_SERVICE_NAME=math-test MATH_PRECISION=10 ENABLE_ADVANCED_MATH=true ALLOWED_OPERATIONS="+,-,*,/,%,^" MAX_CALCULATION_VALUE=999999 LOG_LEVEL=INFO python main.py test_tools/calc_server --port 8004
```

## 🧪 Manual Testing Guide

### Step 1: Environment Setup
```bash
# 1. Create virtual environment with Python 3.11 (required for FastMCP)
python3.11 -m venv venv
source venv/bin/activate

# 2. Install dependencies
pip install -r requirements.txt

# 3. Verify installation
python -c "import fastmcp; print('FastMCP installed successfully')"
```

### Step 2: Test Scanner (Optional)
```bash
# Test the smart scanner first
python test_scanner.py

# Expected output: Should find 2 tools with environment variables detected
```

### Step 3: Deploy Weather Service
```bash
# Deploy weather service with all required environment variables
WEATHER_API_KEY=demo123 SERVICE_NAME=weather-test DEBUG_MODE=true WEATHER_UNITS=celsius RATE_LIMIT=100 python main.py test_tools/weather_service --port 8003

# Server should start and show:
# - ✅ Found MCP tool: weather_api in test_tools/weather_service/weather_server.py
# - ✅ Required environment variables: DEBUG_MODE, WEATHER_UNITS, RATE_LIMIT, SERVICE_NAME, WEATHER_API_KEY
# - ✅ Server URL: http://0.0.0.0:8003
```

### Step 4: Test Weather Service API

In a new terminal, test the running service:

```bash
# 1. Test service info
curl -s http://localhost:8003/ | jq

# Expected: Service info with "MCP Deployment Server - weather-test"

# 2. Test health check
curl -s http://localhost:8003/health | jq

# Expected: {"status": "healthy", "tool": "weather-test", ...}

# 3. List available tools
curl -s -X POST http://localhost:8003/mcp \
  -H "Content-Type: application/json" \
  -d '{"jsonrpc":"2.0","method":"tools/list","params":{},"id":1}' | jq

# Expected: 2 tools - get_current_weather, get_weather_forecast

# 4. Call weather tool
curl -s -X POST http://localhost:8003/mcp \
  -H "Content-Type: application/json" \
  -d '{"jsonrpc":"2.0","method":"tools/call","params":{"name":"get_current_weather","arguments":{"city":"New York","country":"USA"}},"id":2}' | jq

# Expected: Weather data with environment variables applied (service: "weather-test", api_key_used: "demo123...")

# 5. Test streaming endpoint
curl -s -X POST http://localhost:8003/mcp/stream \
  -H "Content-Type: application/json" \
  -d '{"jsonrpc":"2.0","method":"tools/call","params":{"name":"get_weather_forecast","arguments":{"city":"London","days":5}},"id":3}' | jq

# Expected: 5-day forecast in JSON format
```

### Step 5: Deploy Calculator Service

Stop the weather service (Ctrl+C) and deploy calculator:

```bash
# Deploy calculator service with all required environment variables
CALC_SERVICE_NAME=math-test MATH_PRECISION=10 ENABLE_ADVANCED_MATH=true ALLOWED_OPERATIONS="+,-,*,/,%,^" MAX_CALCULATION_VALUE=999999 LOG_LEVEL=INFO python main.py test_tools/calc_server --port 8004

# Server should start and show:
# - ✅ Found MCP tool: math_server in test_tools/calc_server/math_engine.py
# - ✅ Required environment variables: MAX_CALCULATION_VALUE, ALLOWED_OPERATIONS, MATH_PRECISION, CALC_SERVICE_NAME, ENABLE_ADVANCED_MATH, LOG_LEVEL
```

### Step 6: Test Calculator Service API

```bash
# 1. Test service info
curl -s http://localhost:8004/ | jq

# Expected: Service info with "MCP Deployment Server - math-test"

# 2. List calculator tools
curl -s -X POST http://localhost:8004/mcp \
  -H "Content-Type: application/json" \
  -d '{"jsonrpc":"2.0","method":"tools/list","params":{},"id":1}' | jq '.result.tools[] | .name'

# Expected: "calculate", "advanced_function", "get_service_info"

# 3. Test calculator function
curl -s -X POST http://localhost:8004/mcp \
  -H "Content-Type: application/json" \
  -d '{"jsonrpc":"2.0","method":"tools/call","params":{"name":"calculate","arguments":{"operation":"+","a":15,"b":25}},"id":2}' | jq '.result.content[0].text' | jq

# Expected: {"operation": "15 + 25", "result": 40, "precision": 10, "service": "math-test", "max_value_limit": 999999.0, ...}

# 4. Test advanced math
curl -s -X POST http://localhost:8004/mcp \
  -H "Content-Type: application/json" \
  -d '{"jsonrpc":"2.0","method":"tools/call","params":{"name":"advanced_function","arguments":{"function":"sqrt","value":16}},"id":3}' | jq '.result.content[0].text' | jq

# Expected: Square root calculation result

# 5. Get service configuration
curl -s -X POST http://localhost:8004/mcp \
  -H "Content-Type: application/json" \
  -d '{"jsonrpc":"2.0","method":"tools/call","params":{"name":"get_service_info","arguments":{}},"id":4}' | jq '.result.content[0].text' | jq

# Expected: Service configuration showing all environment variables applied
```

## 🔧 Configuration

All configuration is done via environment variables. See `.env.example` for all available options.

### Key Settings

- `AUTH_ENABLED`: Enable/disable authentication
- `AUTH_TYPE`: Authentication method (bearer, api_key, jwt, basic)
- `MONITORING_ENABLED`: Enable request monitoring
- `MCP_STREAMING_ENABLED`: Enable streaming responses
- `RATE_LIMIT_ENABLED`: Enable rate limiting

## 📡 API Endpoints

- `/` - Service information
- `/mcp` - Main MCP endpoint (JSON-RPC)
- `/mcp/stream` - Streaming MCP endpoint
- `/health` - Health check
- `/metrics` - Prometheus metrics

## 🌊 Streaming Support

The deployment supports streaming responses via the dedicated `/mcp/stream` endpoint or by adding the `X-Stream-Response: true` header to regular `/mcp` requests.

## 🔐 Testing Authentication (Optional)

To test authentication features, deploy with auth enabled:

```bash
# Test with Bearer token authentication
AUTH_ENABLED=true AUTH_TYPE=bearer VALID_BEARER_TOKENS=secret123,secret456 WEATHER_API_KEY=demo123 SERVICE_NAME=weather-test python main.py test_tools/weather_service --port 8005

# Test authenticated request
curl -H "Authorization: Bearer secret123" -X POST http://localhost:8005/mcp \
  -H "Content-Type: application/json" \
  -d '{"jsonrpc":"2.0","method":"tools/list","params":{},"id":1}'

# Test unauthenticated request (should fail)
curl -X POST http://localhost:8005/mcp \
  -H "Content-Type: application/json" \
  -d '{"jsonrpc":"2.0","method":"tools/list","params":{},"id":1}'
```

## 🚀 Deploy Your Own MCP Tools

To deploy your own MCP tools:

```bash
# 1. Point to your MCP tool folder
# The scanner will automatically find FastMCP instances regardless of variable name
python main.py /path/to/your/mcp/tool/folder

# 2. The scanner will detect and warn about missing environment variables
# Example output:
# ✅ Found MCP tool: my_custom_tool in your_tool.py
# ⚠️  Missing environment variables: API_KEY, DATABASE_URL
# 💡 Set these variables before running

# 3. Set the required environment variables and deploy
API_KEY=your_key DATABASE_URL=your_db python main.py /path/to/your/tool
```

## 🐳 Docker Deployment

Build and run with Docker Compose:

```bash
# Basic deployment
docker-compose up -d

# With monitoring stack (Prometheus + Grafana)
docker-compose --profile monitoring up -d
```

## 📊 Monitoring

The server provides detailed metrics in Prometheus format at `/metrics`. Metrics include:
- Request counts by endpoint and status
- Response latency percentiles
- Error rates
- Active connections

## 🛡️ Security Features

- Multiple authentication methods (Bearer, API Key, JWT, Basic)
- Security headers (CSP, HSTS, etc.)
- Rate limiting per client
- Input validation and sanitization
- Request ID tracking for audit trails

## 🔧 Development

Run in development mode with auto-reload:

```bash
source venv/bin/activate
python main.py path/to/tool --reload --log-level debug
```

## 📁 Folder Structure

```
mcp_deployment/
├── main.py                    # Main entry point
├── app.py                     # Starlette application
├── requirements.txt           # Dependencies
├── .env.example              # Environment template
├── test_scanner.py           # Scanner test script
├── venv/                     # Virtual environment
├── middleware/               # Authentication, monitoring, CORS
├── config/                   # Settings management
├── utils/                    # Scanner and logger utilities
└── test_tools/              # Sample tools for testing
    ├── weather_service/     # Weather tool (weather_api variable)
    └── calc_server/         # Calculator tool (math_server variable)
```

## 🎯 What Makes This Special

1. **Smart Detection**: Automatically finds MCP tools with ANY variable name
2. **Environment Intelligence**: Scans code for required environment variables
3. **Zero Configuration**: Just point to a folder and deploy
4. **Production Ready**: Full enterprise features out of the box
5. **Streaming Support**: Built-in streaming HTTP responses
6. **Flexible Authentication**: Multiple auth methods supported

Perfect for deploying any FastMCP tool to production! 🚀