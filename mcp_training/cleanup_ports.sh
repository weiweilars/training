#!/bin/bash
# cleanup_ports.sh - Clean up all MCP servers and ports

echo "🧹 Cleaning up MCP servers..."

# Method 1: Kill all MCP server processes
echo "📍 Step 1: Killing MCP processes..."
pkill -f "python.*run_http.py" 2>/dev/null
sleep 1

# Method 2: Kill any remaining python processes on our ports
echo "📍 Step 2: Checking ports for remaining processes..."
for port in 8000 8001 8002 8003 8005 8007 8010 8011 8012 9000; do
  # Try to get PID using lsof (without sudo)
  PID=$(lsof -ti :$port 2>/dev/null)
  if [ ! -z "$PID" ]; then
    echo "🔫 Found process $PID on port $port - killing..."
    kill -9 $PID 2>/dev/null
  fi
  
  # Alternative: Try using ss to find PIDs
  if ss -tlnp | grep -q ":$port "; then
    echo "⚠️  Port $port still has a process - trying harder cleanup..."
    # Kill any python process that might be using this port
    pkill -f "python.*$port" 2>/dev/null
  fi
done

# Method 3: Force kill any remaining uvicorn processes (FastMCP uses uvicorn)
echo "📍 Step 3: Cleaning up uvicorn processes..."
pkill -f "uvicorn" 2>/dev/null

# Wait for cleanup
sleep 2

# Final verification
echo ""
echo "📊 Final port status check:"
all_clean=true
for port in 8000 8001 8002 8003; do
  if ss -tlnp | grep -q ":$port "; then
    echo "   Port $port: 🔴 STILL IN USE"
    all_clean=false
    # Show what's using it
    echo "      Process info: $(ss -tlnp | grep :$port | head -1)"
  else
    echo "   Port $port: 🟢 FREE"
  fi
done

# Check for remaining MCP processes
remaining=$(pgrep -f "python.*run_http.py" | wc -l)
if [ $remaining -eq 0 ]; then
  echo ""
  if [ "$all_clean" = true ]; then
    echo "✅ Complete cleanup successful - all ports free"
  else
    echo "⚠️  Some ports still in use - you may need manual intervention"
    echo "💡 Try: killall -9 python"
    echo "💡 Or restart your terminal/shell session"
  fi
else
  echo ""
  echo "⚠️  Warning: $remaining MCP processes still running:"
  pgrep -f "python.*run_http.py"
  echo "💡 Try: killall -9 python"
fi