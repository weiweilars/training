# HR Recruitment System - Complete A2A Multi-Agent Architecture

This is a comprehensive **Agent-to-Agent (A2A)** HR recruitment system built with **3-level hierarchical architecture** featuring **28 MCP tools**, **11 individual agents**, **3 team coordinators**, and **1 master coordinator** with complete testing and management frameworks.

## 🏗️ System Architecture

![A2A Architecture](HR_RECRUITMENT_ORG_CHART.md)

Our system implements a **3-level hierarchical A2A architecture** as detailed in the [HR Organization Chart](HR_RECRUITMENT_ORG_CHART.md):

### **Level 1: Foundation Layer**
- **28 MCP Tools** (ports 8051-8143) - Specialized business logic servers
- **10 Agent Categories** - Job creation, sourcing, screening, communication, etc.

### **Level 2: Individual Specialists**
- **11 Individual Agents** (ports 5020-5030) - Specialist agents with dedicated MCP tools
- Each agent connects to 2-3 specialized MCP tool servers
- Handles specific domain expertise (job requisition, sourcing, screening, etc.)

### **Level 3: Team Coordination**
- **3 Team Coordinators** (ports 5032-5034) - Orchestrate related individual agents
  - **Acquisition Team** (5032): Sources, screens, validates candidates
  - **Experience Team** (5033): Manages interviews, assessments, communications
  - **Closing Team** (5034): Handles offers, negotiations, compliance
- **1 Master Coordinator** (5040): Orchestrates all team coordinators

## 📂 Complete System Structure

```
hr_recruitment_system/
├── 📋 **Main Access Files:**
│   ├── README.md                          # This comprehensive guide
│   ├── QUERY_TRACING_GUIDE.md             # Query tracing & debugging guide
│   ├── HR_RECRUITMENT_ORG_CHART.md        # System architecture & organization
│   ├── cleanup.sh                         # System cleanup & management
│   ├── start_tools.sh                     # ./start_tools.sh --start-all
│   ├── start_agents.sh                    # ./start_agents.sh --all
│   ├── start_coordinators.sh              # ./start_coordinators.sh --all
│   ├── run_tests.sh                       # ./run_tests.sh {tools|agents|coordinators|master|logging}
│   └── status.sh                          # ./status.sh
├──
├── 📂 **scripts/** - Organized system scripts
│   ├── tools/                             # MCP tools management
│   │   ├── manage_hr_tools.py             # MCP tools management
│   │   ├── hr_tools_config.py             # Central configuration & port mapping
│   │   └── run_hr_tool_http.py            # Individual tool HTTP server
│   ├── agents/                            # Agent execution
│   │   ├── run_sk_agents.py               # Individual agents runner
│   │   └── run_coordinators.py            # Team coordinators runner
│   └── monitoring/                        # System monitoring
│       ├── quick_status.py                # Complete system status
│       └── advanced_query_tracer.py       # Advanced query tracing & monitoring
├──
├── 🧪 **tests/** - 4-Level testing framework
│   ├── test_tools.py                      # Level 1: MCP tools testing
│   ├── test_individual_agents.py          # Level 2: Individual agents testing
│   ├── test_coordinators.py               # Level 3: Team coordinators testing
│   └── test_master.py                     # Level 4: Master integration testing
├──
├── 🔧 **recruitment_tools_focused/**      # 28 MCP tool implementations
├── 👥 **hr_recruitment_agents/**          # Agent configurations (organized)
│   ├── individual/                        # 11 individual specialist agents
│   └── team_coordinators/                 # 4 coordinator agents (3 teams + master)
├── 📊 **traces/**                         # Query tracing files (auto-created)
│   ├── trace_YYYYMMDD_HHMMSS.json         # Full trace data
│   └── trace_YYYYMMDD_HHMMSS_summary.json # Execution summaries
└── 📊 **test_logs/**                      # Generated test reports
    └── hr_test_*/                         # Comprehensive test reports
```

## ⚡ Quick Start Guide

### **🚀 Complete System Startup**

```bash
# 1. Start all MCP tool servers (Level 1 - Foundation)
./start_tools.sh --start-all

# 2. Start all individual agents (Level 2 - Specialists)
./start_agents.sh --all

# 3. Start team coordinators (Level 3 - Orchestration)
./start_coordinators.sh --all

# 4. Test complete system
./run_tests.sh master

# 5. Check system status
./status.sh

# 6. Cleanup everything when done
./cleanup.sh all
```

### **🔬 Development Workflow**

```bash
# Start specific agent with tools
./start_tools.sh --start-agent-tools job_requisition_agent
./start_agents.sh job_requisition_agent

# Test specific layer
./run_tests.sh agents      # Test individual agents
./run_tests.sh coordinators # Test coordinators

# Check system status anytime
./status.sh

# Cleanup specific layer
./cleanup.sh agents      # Clean only individual agents
./cleanup.sh coordinators # Clean coordinators + master
```

## 📋 System Management

### **🔧 MCP Tools Management (Level 1)**

```bash
# Convenient wrapper commands
./start_tools.sh --list                               # List all 28 tools and their ports
./start_tools.sh --start-all                          # Start all tools
./start_tools.sh --start-agent-tools job_requisition_agent # Start tools for specific agent

# Direct script access (organized)
python scripts/tools/manage_hr_tools.py --list
python scripts/tools/manage_hr_tools.py --start-all
python scripts/tools/manage_hr_tools.py --test job_requisition_agent
python scripts/tools/manage_hr_tools.py --cleanup
```

### **🤖 Individual Agents Management (Level 2)**

```bash
# Convenient wrapper commands
./start_agents.sh --list                              # List all 11 individual agents
./start_agents.sh job_requisition_agent               # Start single agent (development)
./start_agents.sh --all                               # Start all agents simultaneously (production)

# Direct script access (organized)
python scripts/agents/run_sk_agents.py --list
python scripts/agents/run_sk_agents.py job_requisition_agent
python scripts/agents/run_sk_agents.py --all
python scripts/agents/run_sk_agents.py --cleanup
```

### **🎯 Team Coordinators Management (Level 3)**

```bash
# Convenient wrapper commands
./start_coordinators.sh --list                        # List all coordinators (3 teams + 1 master)
./start_coordinators.sh acquisition_team_agent        # Start single coordinator
./start_coordinators.sh --all                         # Start all coordinators in proper order

# Direct script access (organized)
python scripts/agents/run_coordinators.py --list
python scripts/agents/run_coordinators.py acquisition_team_agent
python scripts/agents/run_coordinators.py --all
python scripts/agents/run_coordinators.py --cleanup
```

## 🧪 4-Level Testing Framework

Our testing framework validates each architectural level systematically:

### **Level 1: MCP Tools Testing**
```bash
# Convenient wrapper
./run_tests.sh tools                     # Test all 28 MCP tools

# Direct script access
python tests/test_tools.py
python tests/test_tools.py --tool job-creation
python tests/test_tools.py --agent sourcing_agent
```

### **Level 2: Individual Agents Testing**
```bash
# Convenient wrapper
./run_tests.sh agents                    # Test all 11 individual agents

# Direct script access
python tests/test_individual_agents.py
python tests/test_individual_agents.py --agent job_requisition_agent
python tests/test_individual_agents.py --list
```

### **Level 3: Team Coordinators Testing**
```bash
# Convenient wrapper
./run_tests.sh coordinators              # Test all team coordinators

# Direct script access
python tests/test_coordinators.py
python tests/test_coordinators.py --coordinator acquisition_team_agent
python tests/test_coordinators.py --list
```

### **Level 4: Master Integration Testing**
```bash
# Convenient wrapper
./run_tests.sh master                    # Complete system integration

# Direct script access
python tests/test_master.py
python tests/test_master.py --health-only
python tests/test_master.py --scenario 2
```

### **Query Tracing and Debugging** ✅ NEW
```bash
# Trace query execution with full A2A monitoring
python advanced_query_tracer.py "Create a job posting for Senior Developer"

# Interactive tracing mode
python advanced_query_tracer.py --interactive

# Test multi-team coordination
python advanced_query_tracer.py "We need to hire 3 engineers urgently - create jobs, find candidates, and prepare offers"
```

## 🧹 System Cleanup

Our `cleanup.sh` script provides granular cleanup control:

```bash
# Show current system status
./status.sh                # Quick system status
./cleanup.sh status        # Detailed cleanup status

# Clean specific layers
./cleanup.sh tools         # Clean MCP tools only
./cleanup.sh agents        # Clean individual agents only
./cleanup.sh coordinators  # Clean team coordinators + master

# Clean everything (proper dependency order)
./cleanup.sh all

# Show help
./cleanup.sh help
```

## 🛠️ Manual Setup Examples

### **Example 1: Single Agent End-to-End**

```bash
# 1. Start MCP tools for job requisition agent
./start_tools.sh --start-agent-tools job_requisition_agent
# Tools started: job-creation (8051), job-workflow (8052), job-templates (8053)

# 2. Start the job requisition agent
./start_agents.sh job_requisition_agent
# Agent started on port 5020

# 3. Test the agent (new terminal)
curl http://localhost:5020/.well-known/agent-card.json
./run_tests.sh agents

# 4. Check status and cleanup
./status.sh
./cleanup.sh agents && ./cleanup.sh tools
```

### **Example 2: Team Coordinator with Sub-agents**

```bash
# 1. Start MCP tools
./start_tools.sh --start-all

# 2. Start individual agents for acquisition team
./start_agents.sh sourcing_agent          # Port 5021
./start_agents.sh resume_screening_agent  # Port 5022
./start_agents.sh background_verification_agent # Port 5026
./start_agents.sh analytics_reporting_agent     # Port 5028

# 3. Wait for agents to be ready (2-3 seconds each)

# 4. Start acquisition team coordinator
./start_coordinators.sh acquisition_team_agent  # Port 5032

# 5. Test team coordination
./run_tests.sh coordinators

# 6. Check status and cleanup
./status.sh
./cleanup.sh all
```

### **Example 3: Complete System Manual Testing**

```bash
# 1. Start foundation layer
./start_tools.sh --start-all
sleep 5  # Allow tools to initialize

# 2. Start individual agents layer
./start_agents.sh --all &
sleep 10  # Allow agents to start

# 3. Start coordination layer
./start_coordinators.sh --all &
sleep 15  # Allow coordinators to connect

# 4. Check system health
./status.sh

# 5. Test complete integration
./run_tests.sh master

# 6. Test with query tracing
python advanced_query_tracer.py "Test complete system integration"

# 7. Cleanup everything
./cleanup.sh all
```

## 📊 System Statistics

- **Total Components**: 43 (28 tools + 11 agents + 4 coordinators)
- **MCP Tool Servers**: 28 across 10 domain areas
- **Individual Agents**: 11 specialist agents with dedicated tools
- **Team Coordinators**: 3 team coordinators + 1 master coordinator
- **Port Range**: Tools (8051-8143), Agents (5020-5030), Coordinators (5032-5034, 5040)
- **Architecture**: 3-level hierarchical A2A with proper dependency management
- **Testing Levels**: 4-level comprehensive testing framework
- **Management Scripts**: 6 specialized management and testing scripts

## 🎯 A2A Communication Workflows

### **Workflow Types by Team:**

1. **Acquisition Team** (Parallel Processing):
   - Sourcing Agent → Resume Screening Agent → Background Verification Agent
   - Analytics Agent tracks metrics throughout

2. **Experience Team** (Event-Driven):
   - Communication Agent ↔ Interview Scheduling Agent ↔ Assessment Agent
   - Analytics Agent monitors candidate experience

3. **Closing Team** (Sequential):
   - Offer Management Agent → Compliance Agent → Analytics Agent
   - Strict order for legal compliance

4. **Master Coordination** (Hierarchical):
   - Master Coordinator → Team Coordinators → Individual Agents → MCP Tools

## 🔧 Direct Testing Examples

### **Test MCP Tools Directly**
```bash
# Test job creation tool
curl -X POST http://localhost:8051/mcp \
  -H "Content-Type: application/json" \
  -H "Accept: application/json, text/event-stream" \
  -d '{"jsonrpc":"2.0","method":"tools/call","params":{"name":"create_job_draft","arguments":{"title":"Senior Python Developer","department":"Engineering","location":"Remote"}},"id":1}'

# Test skills matching tool
curl -X POST http://localhost:8072/mcp \
  -H "Content-Type: application/json" \
  -H "Accept: application/json, text/event-stream" \
  -d '{"jsonrpc":"2.0","method":"tools/call","params":{"name":"calculate_skills_match","arguments":{"candidate_skills":"Python, Django, React","required_skills":"Python, JavaScript, 3+ years"}},"id":2}'
```

### **Test Individual Agent Directly**
```bash
# Check agent health
curl http://localhost:5020/.well-known/agent-card.json

# Send conversation to agent
curl -X POST http://localhost:5020/conversations \
  -H "Content-Type: application/json" \
  -d '{
    "messages": [{
      "id": "msg-1",
      "timestamp": "'$(date -Iseconds)'",
      "role": "user",
      "content": "Create a job posting for a Senior Software Engineer with 5+ years Python experience"
    }]
  }'
```

## 🛠️ Setup Requirements

### **Prerequisites**
1. **Python Environment**: Python 3.8+ with required dependencies
2. **SK Server Backend**: `../a2a_training/5_sk_a2a_custom_mcp_agent/` must be available
3. **Port Availability**: Ensure ports 5020-5040 and 8051-8143 are free
4. **Dependencies**: FastMCP, Semantic Kernel, aiohttp, requests

### **Environment Setup**
```bash
# Install dependencies (if not already installed)
pip install fastmcp semantic-kernel aiohttp requests

# Verify SK server backend exists
ls ../a2a_training/5_sk_a2a_custom_mcp_agent/sk_a2a_server.py

# Check port availability
./cleanup.sh status
```

## 📚 Key Files Reference

### **📋 Main Documentation**
- **[README.md](README.md)**: This comprehensive guide
- **[HR_RECRUITMENT_ORG_CHART.md](HR_RECRUITMENT_ORG_CHART.md)**: Complete system architecture, team structures, and relationships
- **[QUERY_TRACING_GUIDE.md](QUERY_TRACING_GUIDE.md)**: Query tracing, debugging, and A2A monitoring guide

### **⚙️ Core Configuration**
- **[scripts/tools/hr_tools_config.py](scripts/tools/hr_tools_config.py)**: Central configuration with all port mappings and tool definitions
- **Individual Agent Configs**: `hr_recruitment_agents/individual/*.yaml` - 11 specialist agent configurations
- **Coordinator Configs**: `hr_recruitment_agents/team_coordinators/*.yaml` - 4 coordinator configurations

### **🚀 Convenient Entry Points**
- **[start_tools.sh](start_tools.sh)**: Start MCP tools with various options
- **[start_agents.sh](start_agents.sh)**: Start individual agents
- **[start_coordinators.sh](start_coordinators.sh)**: Start team coordinators
- **[run_tests.sh](run_tests.sh)**: Run any test level with simple commands
- **[status.sh](status.sh)**: Quick system status overview
- **[cleanup.sh](cleanup.sh)**: System cleanup and management

## 🎉 Production Ready Features

✅ **Complete A2A Architecture**: 3-level hierarchical agent communication
✅ **Proper Dependency Management**: Startup/shutdown in correct order
✅ **Comprehensive Testing**: 4-level testing framework with health checks
✅ **Production Management**: Granular cleanup, status monitoring, error handling
✅ **Scalable Design**: Individual components can be started/stopped independently
✅ **Real MCP Integration**: 28 actual MCP tool servers with business logic
✅ **Session Management**: Semantic Kernel provides conversation context preservation
✅ **Multi-Agent Coordination**: Teams can work in parallel, sequential, or event-driven modes

## 🚀 Ready for Advanced Use Cases

This system provides the complete foundation for:

1. **Multi-Agent Workflows**: Complex hiring pipelines with multiple agent coordination
2. **A2A Communication**: Agents can communicate directly without human intervention
3. **Team-Based Processing**: Different workflow patterns per team (parallel, sequential, event-driven)
4. **Master Orchestration**: High-level coordination of entire hiring processes
5. **Production Deployment**: Full management, testing, and cleanup capabilities
6. **Extensibility**: Easy to add new agents, tools, or modify team structures

The HR recruitment system is now **100% complete** with full A2A multi-agent architecture ready for production use!