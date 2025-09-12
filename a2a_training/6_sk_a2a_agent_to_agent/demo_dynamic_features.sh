#!/bin/bash
# Streamlined Demo and Service Manager for SK A2A Agent-to-Agent Communication

show_help() {
    echo "🚀 SK A2A Agent-to-Agent Demo & Service Manager"
    echo "=============================================="
    echo ""
    echo "This manages the complete multi-agent system with MCP tools, specialized agents,"
    echo "summarization agent, and dynamic coordinator."
    echo ""
    echo "Usage: $0 [OPTION]"
    echo ""
    echo "Options:"
    echo "  --start-services    Start all required services (MCP tools + agents)"
    echo "  --test             Run comprehensive automated test"
    echo "  --cleanup          Stop all services and cleanup"
    echo "  --status           Check which services are running"
    echo "  --help             Show this help message"
    echo ""
    echo "Service Architecture:"
    echo "  🛠️  MCP Tools (Foundation Layer):"
    echo "     8001 - Weather MCP tool"
    echo "     8002 - Calculator MCP tool"
    echo ""  
    echo "  🤖 Specialized Agents (Capability Layer):"
    echo "     5010 - AgentA (Weather Specialist)"
    echo "     5011 - AgentB (Calculator Agent)"
    echo ""
    echo "  🌐 Multi-Agent System (Orchestration Layer):"
    echo "     5030 - Summarization Agent (for dynamic card generation)"
    echo "     5025 - Dynamic Coordinator (orchestrates other agents)"
    echo ""
    echo "Quick Start:"
    echo "  ./demo_dynamic_features.sh --start-services"
    echo "  ./demo_dynamic_features.sh --test"
    echo "  ./demo_dynamic_features.sh --cleanup"
}

start_all_services() {
    echo "🚀 Starting Complete Multi-Agent System..."
    echo "   This will start: MCP Tools → Specialized Agents → Coordinator System"
    echo ""
    
    # Cleanup first
    ./cleanup.sh > /dev/null 2>&1
    
    # Start MCP tools (foundation layer)
    echo "1️⃣  Starting MCP tool servers..."
    cd ../../mcp_training
    python run_http.py weather --port 8001 > /dev/null 2>&1 &
    python run_http.py calculator --port 8002 > /dev/null 2>&1 &
    
    # Wait for MCP tools
    sleep 2
    
    # Start specialized agents
    echo "2️⃣  Starting specialized agents..."
    cd ../a2a_training/5_sk_a2a_custom_mcp_agent
    python sk_a2a_server.py --config agentA.yaml > /dev/null 2>&1 &  # Weather specialist
    python sk_a2a_server.py --config agentB.yaml > /dev/null 2>&1 &  # Calculator agent
    python sk_a2a_server.py --config summarization_agent.yaml > /dev/null 2>&1 &  # Summarizer
    
    # Wait for specialized agents
    sleep 3
    
    # Start coordinator
    echo "3️⃣  Starting dynamic coordinator..."
    cd ../6_sk_a2a_agent_to_agent
    python sk_a2a_server.py --config dynamic_coordinator.yaml > /dev/null 2>&1 &
    
    # Wait for coordinator
    sleep 3
    
    # Verify services
    echo "4️⃣  Verifying services..."
    SERVICES_RUNNING=0
    
    for port in 8001 8002 5010 5011 5030 5025; do
        if lsof -i:$port > /dev/null 2>&1; then
            ((SERVICES_RUNNING++))
        fi
    done
    
    if [ "$SERVICES_RUNNING" -eq "6" ]; then
        echo "✅ All services started successfully!"
        echo ""
        echo "🎯 System Ready! You can now:"
        echo "   • Run tests: ./demo_dynamic_features.sh --test"
        echo "   • Check status: ./demo_dynamic_features.sh --status"  
        echo "   • Manual testing: See README.md examples"
        echo "   • Cleanup when done: ./demo_dynamic_features.sh --cleanup"
    else
        echo "⚠️  Only $SERVICES_RUNNING/6 services started. Check for port conflicts or errors."
        echo "   Use: ./demo_dynamic_features.sh --status"
    fi
}

check_service_status() {
    echo "📊 Multi-Agent System Status"
    echo "=============================="
    echo ""
    
    declare -A services=(
        ["8001"]="Weather MCP Tool"
        ["8002"]="Calculator MCP Tool"
        ["5010"]="AgentA (Weather Specialist)"
        ["5011"]="AgentB (Calculator Agent)" 
        ["5030"]="Summarization Agent"
        ["5025"]="Dynamic Coordinator"
    )
    
    RUNNING=0
    TOTAL=6
    
    for port in 8001 8002 5010 5011 5030 5025; do
        if lsof -i:$port > /dev/null 2>&1; then
            echo "✅ Port $port: ${services[$port]}"
            ((RUNNING++))
        else
            echo "❌ Port $port: ${services[$port]} (not running)"
        fi
    done
    
    echo ""
    echo "Status: $RUNNING/$TOTAL services running"
    
    if [ "$RUNNING" -eq "$TOTAL" ]; then
        echo "🎉 Full system operational! Ready for testing."
    elif [ "$RUNNING" -gt "0" ]; then
        echo "⚠️  Partial system running. Use --start-services to start all."
    else
        echo "🚫 No services running. Use --start-services to start the system."
    fi
}

run_comprehensive_test() {
    echo "🧪 Running Comprehensive Multi-Agent Test..."
    echo "   This tests: Service availability + Dynamic cards + Multi-agent coordination"
    echo ""
    
    if ! command -v python &> /dev/null; then
        echo "❌ Python not found. Please install Python to run tests."
        exit 1
    fi
    
    # Run the test
    python test_dynamic_agent_card.py
}

# Parse command line arguments
case "${1:-help}" in
    "--start-services"|"start")
        start_all_services
        ;;
        
    "--test"|"test")
        run_comprehensive_test
        ;;
        
    "--cleanup"|"cleanup")
        ./cleanup.sh
        ;;
        
    "--status"|"status")
        check_service_status
        ;;
        
    "--help"|"help"|"")
        show_help
        ;;
        
    *)
        echo "❌ Unknown option: $1"
        echo "   Use '--help' to see available options"
        exit 1
        ;;
esac