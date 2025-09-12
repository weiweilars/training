#!/bin/bash

# Cleanup script for ADK A2A ToolManage Agent and MCP Tools
# Usage: ./cleanup.sh [tools|agent|all]

set -e

# ANSI color codes
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
BOLD='\033[1m'
NC='\033[0m' # No Color

# Default MCP tool ports
WEATHER_PORT=8001
CALCULATOR_PORT=8002

# Default A2A agent port
AGENT_PORT=5002

print_header() {
    echo -e "${BLUE}${BOLD}================================${NC}"
    echo -e "${BLUE}${BOLD} $1${NC}"
    echo -e "${BLUE}${BOLD}================================${NC}"
}

print_success() {
    echo -e "${GREEN}✅ $1${NC}"
}

print_error() {
    echo -e "${RED}❌ $1${NC}"
}

print_info() {
    echo -e "${BLUE}ℹ️  $1${NC}"
}

print_warning() {
    echo -e "${YELLOW}⚠️  $1${NC}"
}

cleanup_port() {
    local port=$1
    local name=$2
    
    # Find processes using the port
    local pids=$(lsof -ti:$port 2>/dev/null || true)
    
    if [ -n "$pids" ]; then
        print_info "Found processes on port $port ($name): $pids"
        
        for pid in $pids; do
            # Get process name
            local proc_name=$(ps -p $pid -o comm= 2>/dev/null || echo "unknown")
            print_info "  Killing PID $pid ($proc_name)"
            
            # Try graceful termination first
            kill -TERM $pid 2>/dev/null || true
            sleep 2
            
            # Force kill if still running
            if kill -0 $pid 2>/dev/null; then
                print_warning "  Process $pid still running, force killing..."
                kill -KILL $pid 2>/dev/null || true
            fi
        done
        
        # Verify port is free
        sleep 1
        local remaining=$(lsof -ti:$port 2>/dev/null || true)
        if [ -z "$remaining" ]; then
            print_success "Port $port ($name) cleaned up"
        else
            print_error "Failed to clean up port $port ($name)"
        fi
    else
        print_info "Port $port ($name) is already free"
    fi
}

cleanup_tools() {
    print_header "Cleaning Up MCP Tools"
    print_info "Stopping MCP tool servers..."
    
    cleanup_port $WEATHER_PORT "Weather MCP"
    cleanup_port $CALCULATOR_PORT "Calculator MCP"
    
    print_success "MCP tools cleanup completed"
}

cleanup_agent() {
    print_header "Cleaning Up ADK A2A Agent"
    print_info "Stopping ADK A2A agent server..."
    
    cleanup_port $AGENT_PORT "ADK A2A Agent"
    
    print_success "ADK A2A agent cleanup completed"
}

cleanup_all() {
    cleanup_tools
    echo
    cleanup_agent
}

show_usage() {
    echo -e "${BOLD}ADK A2A ToolManage Agent Cleanup Script${NC}"
    echo
    echo -e "${BOLD}Usage:${NC}"
    echo "  $0 [OPTION]"
    echo
    echo -e "${BOLD}Options:${NC}"
    echo "  tools     Clean up MCP tool servers (ports $WEATHER_PORT, $CALCULATOR_PORT)"
    echo "  agent     Clean up ADK A2A agent server (port $AGENT_PORT)"
    echo "  all       Clean up both MCP tools and A2A agent (default)"
    echo "  help      Show this help message"
    echo
    echo -e "${BOLD}Examples:${NC}"
    echo "  $0                # Clean up everything"
    echo "  $0 all            # Clean up everything"
    echo "  $0 tools          # Clean up only MCP tools"
    echo "  $0 agent          # Clean up only A2A agent"
    echo
    echo -e "${BOLD}Port Configuration:${NC}"
    echo "  MCP Tools:"
    echo "    Weather MCP:     $WEATHER_PORT"
    echo "    Calculator MCP:  $CALCULATOR_PORT"
    echo "  A2A Agent:"
    echo "    ADK A2A Agent:   $AGENT_PORT"
}

# Check if lsof is available
if ! command -v lsof &> /dev/null; then
    print_error "lsof command not found. Please install it:"
    print_info "  Ubuntu/Debian: sudo apt-get install lsof"
    print_info "  CentOS/RHEL:   sudo yum install lsof"
    print_info "  macOS:         brew install lsof (if needed)"
    exit 1
fi

# Main logic
case "${1:-all}" in
    "tools")
        cleanup_tools
        ;;
    "agent")
        cleanup_agent
        ;;
    "all"|"")
        cleanup_all
        ;;
    "help"|"-h"|"--help")
        show_usage
        ;;
    *)
        print_error "Unknown option: $1"
        echo
        show_usage
        exit 1
        ;;
esac

echo
print_success "Cleanup completed! 🧹"