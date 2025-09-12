#!/bin/bash

# Cleanup script for SK A2A Custom MCP Agents and MCP Tools
# Usage: ./cleanup.sh [tools|agents|all]

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

# Default agent ports (from YAML configs)
AGENT_A_PORT=5010  # Weather Specialist Agent
AGENT_B_PORT=5011  # Calculator Specialist Agent
AGENT_C_PORT=5012  # Multi-Tool Assistant

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

cleanup_agents() {
    print_header "Cleaning Up SK A2A Custom MCP Agents"
    print_info "Stopping SK A2A agent servers..."
    
    cleanup_port $AGENT_A_PORT "Weather Specialist Agent"
    cleanup_port $AGENT_B_PORT "Calculator Specialist Agent" 
    cleanup_port $AGENT_C_PORT "Multi-Tool Assistant"
    
    print_success "SK A2A agents cleanup completed"
}

cleanup_all() {
    cleanup_tools
    echo
    cleanup_agents
}

show_usage() {
    echo -e "${BOLD}SK A2A Custom MCP Agent Cleanup Script${NC}"
    echo
    echo -e "${BOLD}Usage:${NC}"
    echo "  $0 [OPTION]"
    echo
    echo -e "${BOLD}Options:${NC}"
    echo "  tools     Clean up MCP tool servers (ports $WEATHER_PORT, $CALCULATOR_PORT)"
    echo "  agents    Clean up SK A2A agent servers (ports $AGENT_A_PORT, $AGENT_B_PORT, $AGENT_C_PORT)"
    echo "  all       Clean up both MCP tools and SK A2A agents (default)"
    echo "  help      Show this help message"
    echo
    echo -e "${BOLD}Examples:${NC}"
    echo "  $0                # Clean up everything"
    echo "  $0 all            # Clean up everything"
    echo "  $0 tools          # Clean up only MCP tools"
    echo "  $0 agents         # Clean up only SK A2A agents"
    echo
    echo -e "${BOLD}Port Configuration:${NC}"
    echo "  MCP Tools:"
    echo "    Weather MCP:    $WEATHER_PORT"
    echo "    Calculator MCP: $CALCULATOR_PORT"
    echo "  SK A2A Agents:"
    echo "    Agent A (Weather):      $AGENT_A_PORT"
    echo "    Agent B (Calculator):   $AGENT_B_PORT"
    echo "    Agent C (Multi-Tool):   $AGENT_C_PORT"
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
    "agents")
        cleanup_agents
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