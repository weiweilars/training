#!/bin/bash
#
# HR Recruitment System Cleanup Script
# Clean up processes for different system layers
# Usage: ./cleanup.sh [coordinators|agents|tools|all]
#

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Function to print colored output
print_status() {
    echo -e "${BLUE}🧹 $1${NC}"
}

print_success() {
    echo -e "${GREEN}✅ $1${NC}"
}

print_warning() {
    echo -e "${YELLOW}⚠️  $1${NC}"
}

print_error() {
    echo -e "${RED}❌ $1${NC}"
}

# Function to clean coordinators and master
cleanup_coordinators() {
    print_status "Cleaning up Team Coordinators and Master..."

    if command -v python3 &> /dev/null; then
        python3 scripts/agents/run_coordinators.py --cleanup
    elif command -v python &> /dev/null; then
        python scripts/agents/run_coordinators.py --cleanup
    else
        print_error "Python not found"
        return 1
    fi

    print_success "Coordinators cleanup completed"
}

# Function to clean individual agents
cleanup_agents() {
    print_status "Cleaning up Individual Agents..."

    if command -v python3 &> /dev/null; then
        python3 scripts/agents/run_sk_agents.py --cleanup
    elif command -v python &> /dev/null; then
        python scripts/agents/run_sk_agents.py --cleanup
    else
        print_error "Python not found"
        return 1
    fi

    print_success "Individual agents cleanup completed"
}

# Function to clean MCP tools
cleanup_tools() {
    print_status "Cleaning up MCP Tools..."

    if command -v python3 &> /dev/null; then
        python3 scripts/tools/manage_hr_tools.py --cleanup
    elif command -v python &> /dev/null; then
        python scripts/tools/manage_hr_tools.py --cleanup
    else
        print_error "Python not found"
        return 1
    fi

    print_success "MCP tools cleanup completed"
}

# Function to clean everything
cleanup_all() {
    print_status "Cleaning up ALL HR System Components..."
    echo "=========================================="

    # Clean in reverse dependency order
    echo -e "\n${YELLOW}Phase 1: Team Coordinators and Master${NC}"
    cleanup_coordinators

    echo -e "\n${YELLOW}Phase 2: Individual Agents${NC}"
    cleanup_agents

    echo -e "\n${YELLOW}Phase 3: MCP Tools${NC}"
    cleanup_tools

    # Additional cleanup for any remaining processes
    echo -e "\n${YELLOW}Phase 4: Additional Process Cleanup${NC}"
    cleanup_additional_processes

    echo "=========================================="
    print_success "Complete system cleanup finished"
}

# Function to clean additional processes that might be missed
cleanup_additional_processes() {
    print_status "Cleaning additional processes..."

    # Clean any Python processes running HR-related scripts
    HR_PROCESSES=$(pgrep -f "sk_a2a_server.py\|run_http.py\|manage_hr_tools.py" 2>/dev/null || true)

    if [ ! -z "$HR_PROCESSES" ]; then
        print_status "Found additional HR processes, cleaning..."
        echo "$HR_PROCESSES" | while read -r pid; do
            if kill -0 "$pid" 2>/dev/null; then
                print_status "Killing process $pid"
                kill -TERM "$pid" 2>/dev/null || true
                sleep 1
                # Force kill if still running
                if kill -0 "$pid" 2>/dev/null; then
                    kill -KILL "$pid" 2>/dev/null || true
                fi
            fi
        done
        print_success "Additional processes cleaned"
    else
        print_status "No additional HR processes found"
    fi

    # Clean any remaining processes on HR ports
    print_status "Checking for processes on HR ports..."

    # HR Agent ports (5020-5040)
    # MCP Tool ports (8051-8143)
    HR_PORTS="5020 5021 5022 5023 5024 5025 5026 5027 5028 5029 5030 5031 5032 5033 5034 5040"
    TOOL_PORTS=$(seq 8051 8143)
    ALL_PORTS="$HR_PORTS $TOOL_PORTS"

    for port in $ALL_PORTS; do
        if command -v lsof &> /dev/null; then
            PIDS=$(lsof -ti :$port 2>/dev/null || true)
            if [ ! -z "$PIDS" ]; then
                print_status "Cleaning port $port (PIDs: $PIDS)"
                echo "$PIDS" | xargs -r kill -TERM 2>/dev/null || true
                sleep 0.5
                # Force kill if still running
                REMAINING_PIDS=$(lsof -ti :$port 2>/dev/null || true)
                if [ ! -z "$REMAINING_PIDS" ]; then
                    echo "$REMAINING_PIDS" | xargs -r kill -KILL 2>/dev/null || true
                fi
            fi
        fi
    done

    print_success "Port cleanup completed"
}

# Function to show system status
show_status() {
    print_status "HR System Status Check..."
    echo "=========================================="

    # Check coordinators and master
    echo -e "\n${BLUE}Team Coordinators & Master:${NC}"
    COORD_PORTS="5032 5033 5034 5040"
    for port in $COORD_PORTS; do
        if command -v curl &> /dev/null; then
            if curl -s --connect-timeout 2 "http://localhost:$port/.well-known/agent-card.json" &> /dev/null; then
                echo "  ✅ Port $port: ONLINE"
            else
                echo "  ❌ Port $port: OFFLINE"
            fi
        else
            if command -v lsof &> /dev/null; then
                if lsof -ti :$port &> /dev/null; then
                    echo "  ✅ Port $port: PROCESS RUNNING"
                else
                    echo "  ❌ Port $port: NO PROCESS"
                fi
            fi
        fi
    done

    # Check individual agents
    echo -e "\n${BLUE}Individual Agents:${NC}"
    AGENT_PORTS="5020 5021 5022 5023 5024 5025 5026 5027 5028 5029 5030"
    AGENTS_ONLINE=0
    for port in $AGENT_PORTS; do
        if command -v curl &> /dev/null; then
            if curl -s --connect-timeout 2 "http://localhost:$port/.well-known/agent-card.json" &> /dev/null; then
                echo "  ✅ Port $port: ONLINE"
                ((AGENTS_ONLINE++))
            else
                echo "  ❌ Port $port: OFFLINE"
            fi
        else
            if command -v lsof &> /dev/null; then
                if lsof -ti :$port &> /dev/null; then
                    echo "  ✅ Port $port: PROCESS RUNNING"
                    ((AGENTS_ONLINE++))
                else
                    echo "  ❌ Port $port: NO PROCESS"
                fi
            fi
        fi
    done
    echo "  📊 Agents online: $AGENTS_ONLINE/11"

    # Check sample MCP tools
    echo -e "\n${BLUE}MCP Tools (sample):${NC}"
    SAMPLE_TOOL_PORTS="8051 8061 8071 8081 8091 8101 8111 8121 8131 8141"
    TOOLS_ONLINE=0
    for port in $SAMPLE_TOOL_PORTS; do
        if command -v curl &> /dev/null; then
            if curl -s --connect-timeout 2 -H "Accept: application/json, text/event-stream" -X POST "http://localhost:$port/mcp" -d '{"jsonrpc":"2.0","method":"tools/list","params":{},"id":1}' &> /dev/null; then
                echo "  ✅ Port $port: ONLINE"
                ((TOOLS_ONLINE++))
            else
                echo "  ❌ Port $port: OFFLINE"
            fi
        else
            if command -v lsof &> /dev/null; then
                if lsof -ti :$port &> /dev/null; then
                    echo "  ✅ Port $port: PROCESS RUNNING"
                    ((TOOLS_ONLINE++))
                else
                    echo "  ❌ Port $port: NO PROCESS"
                fi
            fi
        fi
    done
    echo "  📊 Sample tools online: $TOOLS_ONLINE/10"

    echo "=========================================="
}

# Function to show usage
show_usage() {
    echo "HR Recruitment System Cleanup Script"
    echo "====================================="
    echo "Usage: $0 [OPTION]"
    echo ""
    echo "Options:"
    echo "  coordinators    Clean team coordinators and master coordinator"
    echo "  agents          Clean individual specialist agents"
    echo "  tools           Clean MCP tool servers"
    echo "  all             Clean everything (coordinators + agents + tools)"
    echo "  status          Show current system status"
    echo "  help            Show this help message"
    echo ""
    echo "Examples:"
    echo "  $0 all                # Clean entire system"
    echo "  $0 coordinators       # Clean only coordinators"
    echo "  $0 agents             # Clean only individual agents"
    echo "  $0 tools              # Clean only MCP tools"
    echo "  $0 status             # Check system status"
    echo ""
    echo "Note: Cleanup is performed in dependency order to avoid issues"
}

# Main script logic
main() {
    case "${1:-}" in
        "coordinators"|"coord")
            cleanup_coordinators
            ;;
        "agents"|"agent")
            cleanup_agents
            ;;
        "tools"|"tool")
            cleanup_tools
            ;;
        "all"|"")
            cleanup_all
            ;;
        "status"|"stat")
            show_status
            ;;
        "help"|"-h"|"--help")
            show_usage
            ;;
        *)
            print_error "Unknown option: $1"
            echo ""
            show_usage
            exit 1
            ;;
    esac
}

# Check if script is being run directly
if [[ "${BASH_SOURCE[0]}" == "${0}" ]]; then
    echo "🧹 HR Recruitment System Cleanup"
    echo "================================="
    main "$@"
fi