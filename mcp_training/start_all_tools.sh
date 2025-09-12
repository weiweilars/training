#!/bin/bash

# Start all MCP tools with standardized ports
# This script ensures consistent ports across all a2a_training examples

echo "🚀 Starting MCP Tools with standardized ports..."
echo "================================================"
echo "Port 8000: File tool"
echo "Port 8001: Weather tool"
echo "Port 8002: Calculator tool"
echo "================================================"

# Kill any existing processes on these ports
echo "🔧 Cleaning up existing processes..."
lsof -ti:8000 | xargs -r kill -9 2>/dev/null
lsof -ti:8001 | xargs -r kill -9 2>/dev/null
lsof -ti:8002 | xargs -r kill -9 2>/dev/null

sleep 1

# Start the tools
echo "📂 Starting File tool on port 8000..."
python run_http.py file --port 8000 &
FILE_PID=$!

echo "🌤️  Starting Weather tool on port 8001..."
python run_http.py weather --port 8001 &
WEATHER_PID=$!

echo "🧮 Starting Calculator tool on port 8002..."
python run_http.py calculator --port 8002 &
CALC_PID=$!

sleep 2

# Verify all services are running
echo ""
echo "✅ Verifying services..."
if curl -s http://localhost:8000/mcp >/dev/null 2>&1; then
    echo "   ✓ File tool running on port 8000"
else
    echo "   ✗ File tool failed to start"
fi

if curl -s http://localhost:8001/mcp >/dev/null 2>&1; then
    echo "   ✓ Weather tool running on port 8001"
else
    echo "   ✗ Weather tool failed to start"
fi

if curl -s http://localhost:8002/mcp >/dev/null 2>&1; then
    echo "   ✓ Calculator tool running on port 8002"
else
    echo "   ✗ Calculator tool failed to start"
fi

echo ""
echo "📝 Process IDs:"
echo "   File tool: $FILE_PID"
echo "   Weather tool: $WEATHER_PID"
echo "   Calculator tool: $CALC_PID"
echo ""
echo "💡 To stop all tools, run: pkill -f 'python.*run_http.py'"
echo "💡 Or use: kill $FILE_PID $WEATHER_PID $CALC_PID"