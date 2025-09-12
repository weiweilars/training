#!/bin/bash
# Enhanced Cleanup script for SK A2A Agent-to-Agent Communication

# Port definitions - Complete system coverage
MCP_PORTS="8001,8002"           # Weather, Calculator MCP tools
SINGLE_AGENT_PORTS="5010,5011" # AgentA (Weather), AgentB (Calculator)  
MULTI_AGENT_PORTS="5025,5030"  # Coordinator, Summarization agent
ALL_AGENT_PORTS="5010,5011,5025,5030"
ALL_PORTS="8001,8002,5010,5011,5025,5030"

show_help() {
    echo "🧹 Enhanced Cleanup Script for SK A2A Agent System"
    echo ""
    echo "Usage: $0 [OPTION]"
    echo ""
    echo "Options:"
    echo "  tools        Clean up only MCP tool servers (ports 8001, 8002)"
    echo "  single       Clean up only single specialized agents (ports 5010, 5011)"
    echo "  multi        Clean up only multi-agent system (coordinator + summarizer: 5025, 5030)"
    echo "  agents       Clean up all agents (single + multi, but keep tools running)"
    echo "  all          Clean up everything (tools + all agents) [DEFAULT]"
    echo "  help         Show this help message"
    echo ""
    echo "Port Configuration:"
    echo "  🛠️  MCP Tools:"
    echo "     8001 - Weather MCP tool server"
    echo "     8002 - Calculator MCP tool server"
    echo ""
    echo "  🤖 Single Agents:"
    echo "     5010 - AgentA (Weather Specialist)"
    echo "     5011 - AgentB (Calculator Agent)"
    echo ""
    echo "  🌐 Multi-Agent System:"
    echo "     5025 - Dynamic Coordinator Agent"
    echo "     5030 - Summarization Agent"
    echo ""
    echo "Examples:"
    echo "  ./cleanup.sh tools      # Clean only MCP tools, keep agents running"
    echo "  ./cleanup.sh single     # Clean only AgentA/AgentB, keep coordinator"
    echo "  ./cleanup.sh multi      # Clean only coordinator system"
    echo "  ./cleanup.sh agents     # Clean all agents, keep MCP tools"
    echo "  ./cleanup.sh           # Clean everything"
}

cleanup_ports() {
    local ports=$1
    local description=$2
    
    if [ -n "$ports" ]; then
        echo "   Cleaning up $description (ports: $ports)..."
        lsof -ti:$ports 2>/dev/null | xargs -r kill -9 2>/dev/null
    fi
}

verify_cleanup() {
    local ports=$1
    local description=$2
    
    if [ -n "$ports" ]; then
        PORTS_IN_USE=$(lsof -i:$ports 2>/dev/null | wc -l)
        
        if [ "$PORTS_IN_USE" -eq "0" ]; then
            echo "✅ $description cleaned up successfully!"
        else
            echo "⚠️  Some $description processes may still be running:"
            lsof -i:$ports 2>/dev/null | head -10
        fi
    fi
}

cleanup_processes() {
    local pattern=$1
    local description=$2
    
    if [ -n "$pattern" ]; then
        echo "   Stopping $description processes..."
        pkill -f "$pattern" 2>/dev/null
    fi
}

# Parse command line arguments
case "${1:-all}" in
    "tools")
        echo "🧹 Cleaning up MCP Tool servers only..."
        cleanup_processes "python.*run_http.py" "MCP tool"
        cleanup_ports "$MCP_PORTS" "MCP tool servers"
        sleep 2
        verify_cleanup "$MCP_PORTS" "MCP tool servers"
        echo ""
        echo "💡 Agents are still running. To restart tools:"
        echo "   cd ../../mcp_training && python run_http.py weather --port 8001 &"
        echo "   cd ../../mcp_training && python run_http.py calculator --port 8002 &"
        ;;
        
    "single")
        echo "🧹 Cleaning up single specialized agents only..."
        cleanup_processes "python.*sk_a2a_server.py.*(agentA|agentB)" "specialized agent"
        cleanup_ports "$SINGLE_AGENT_PORTS" "specialized agents"
        sleep 2
        verify_cleanup "$SINGLE_AGENT_PORTS" "specialized agents"
        echo ""
        echo "💡 Multi-agent system and tools are still running. To restart single agents:"
        echo "   cd ../5_sk_a2a_custom_mcp_agent"
        echo "   python sk_a2a_server.py --config agentA.yaml &"
        echo "   python sk_a2a_server.py --config agentB.yaml &"
        ;;
        
    "multi")
        echo "🧹 Cleaning up multi-agent system only..."
        cleanup_processes "python.*sk_a2a_server.py.*(dynamic_coordinator|summarization)" "multi-agent system"
        cleanup_ports "$MULTI_AGENT_PORTS" "multi-agent system"
        sleep 2
        verify_cleanup "$MULTI_AGENT_PORTS" "multi-agent system"
        echo ""
        echo "💡 Single agents and tools are still running. To restart multi-agent system:"
        echo "   cd ../5_sk_a2a_custom_mcp_agent && python sk_a2a_server.py --config summarization_agent.yaml &"
        echo "   python sk_a2a_server.py --config dynamic_coordinator.yaml &"
        ;;
        
    "agents")
        echo "🧹 Cleaning up all agents (keeping MCP tools)..."
        cleanup_processes "python.*sk_a2a_server.py" "all A2A agent"
        cleanup_ports "$ALL_AGENT_PORTS" "all agents"
        sleep 2
        verify_cleanup "$ALL_AGENT_PORTS" "all agents"
        echo ""
        echo "💡 MCP tools are still running. To restart agents:"
        echo "   ./demo_dynamic_features.sh --start-services (agents only)"
        ;;
        
    "all")
        echo "🧹 Cleaning up everything (tools + all agents)..."
        cleanup_processes "python.*run_http.py" "MCP tool"
        cleanup_processes "python.*sk_a2a_server.py" "A2A agent"
        cleanup_ports "$ALL_PORTS" "all services"
        sleep 2
        verify_cleanup "$ALL_PORTS" "all services"
        echo ""
        echo "💡 To start everything again:"
        echo "   ./demo_dynamic_features.sh --start-services"
        ;;
        
    "help"|"-h"|"--help")
        show_help
        exit 0
        ;;
        
    *)
        echo "❌ Unknown option: $1"
        echo "   Use './cleanup.sh help' to see available options"
        exit 1
        ;;
esac