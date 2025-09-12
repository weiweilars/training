#!/bin/bash

# Cleanup script for training environment ports
# Kills all processes using MCP tool ports (8xxx) and A2A agent ports (5xxx)

echo "🧹 Cleaning up training environment ports..."

# Function to kill processes on specific ports
cleanup_port() {
    local port=$1
    local description=$2
    
    # Find processes using the port
    pids=$(lsof -ti :$port 2>/dev/null)
    
    if [ -n "$pids" ]; then
        echo "   🔪 Killing $description on port $port (PIDs: $pids)"
        kill -9 $pids 2>/dev/null
    else
        echo "   ✅ Port $port is already free ($description)"
    fi
}

# Kill processes by pattern (more thorough)
cleanup_pattern() {
    local pattern=$1
    local description=$2
    
    pids=$(pgrep -f "$pattern" 2>/dev/null)
    
    if [ -n "$pids" ]; then
        echo "   🔪 Killing $description processes (PIDs: $pids)"
        pkill -9 -f "$pattern" 2>/dev/null
    else
        echo "   ✅ No $description processes running"
    fi
}

echo ""
echo "🎯 MCP Tool Servers (8xxx ports):"
cleanup_port 8000 "MCP tools (default)"
cleanup_port 8001 "MCP database tool"
cleanup_port 8002 "MCP weather tool"
cleanup_port 8003 "MCP file tool"  
cleanup_port 8004 "MCP weather tool (alt)"
cleanup_port 8005 "MCP tools (backup)"

echo ""
echo "🤖 A2A Agent Servers (5xxx ports):"
cleanup_port 5000 "A2A agents (default)"
cleanup_port 5001 "A2A simple agent"
cleanup_port 5002 "A2A ADK agent"
cleanup_port 5003 "A2A ADK agent (alt)"
cleanup_port 5004 "A2A agents (backup)"
cleanup_port 5005 "A2A ADK toolManage agent"
cleanup_port 5006 "A2A agents (extra)"

echo ""
echo "🔍 Process Pattern Cleanup:"
cleanup_pattern "python.*run_http.py" "MCP HTTP servers"
cleanup_pattern "python.*adk_a2a_server.py" "ADK A2A agents"
cleanup_pattern "python.*simple_a2a_server.py" "Simple A2A agents"

echo ""
echo "📊 Port Status Check:"
echo "   MCP Tools (8xxx):"
for port in 8000 8001 8002 8003 8004 8005; do
    if lsof -ti :$port >/dev/null 2>&1; then
        echo "   ❌ Port $port: STILL IN USE"
    else
        echo "   ✅ Port $port: FREE"
    fi
done

echo "   A2A Agents (5xxx):"
for port in 5000 5001 5002 5003 5004 5005 5006; do
    if lsof -ti :$port >/dev/null 2>&1; then
        echo "   ❌ Port $port: STILL IN USE"
    else
        echo "   ✅ Port $port: FREE"
    fi
done

echo ""
echo "🎉 Port cleanup complete!"
echo ""
echo "💡 Usage examples after cleanup:"
echo "   # Start MCP tools:"
echo "   python run_http.py weather --port 8004"
echo "   python run_http.py file --port 8003"
echo ""
echo "   # Start A2A agents:" 
echo "   python adk_a2a_server.py --port 5005"
echo "   python simple_a2a_server.py --port 5001"