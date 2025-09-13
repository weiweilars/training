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
├── 📋 HR_RECRUITMENT_ORG_CHART.md         # System architecture & organization
├── 🔧 recruitment_tools_focused/          # 28 MCP tool implementations
├── 👥 hr_recruitment_agents/              # Agent configurations (organized)
│   ├── individual/                        # 11 individual specialist agents
│   └── team_coordinators/                 # 4 coordinator agents (3 teams + master)
├── ⚙️ hr_tools_config.py                  # Central configuration & port mapping
├── 🚀 manage_hr_tools.py                  # MCP tools management
├── 🤖 run_sk_agents.py                    # Individual agents runner
├── 🎯 run_coordinators.py                 # Team coordinators runner
├── 🧪 test_tools.py                       # Level 1: MCP tools testing
├── 🧪 test_individual_agents.py           # Level 2: Individual agents testing
├── 🧪 test_coordinators.py                # Level 3: Team coordinators testing
├── 🧪 test_master.py                      # Level 4: Master integration testing
├── 🧪 run_all_tests.py                    # Complete test suite runner
├── 🧹 cleanup.sh                          # System cleanup & management
└── 📖 README.md                           # This comprehensive guide
```

## ⚡ Quick Start Guide

### **🚀 Complete System Startup**

```bash
# 1. Start all MCP tool servers (Level 1 - Foundation)
python manage_hr_tools.py --start-all

# 2. Start all individual agents (Level 2 - Specialists)
python run_sk_agents.py --all

# 3. Start team coordinators (Level 3 - Orchestration)
python run_coordinators.py --all

# 4. Test complete system
python run_all_tests.py

# 5. Check system status
./cleanup.sh status

# 6. Cleanup everything when done
./cleanup.sh all
```

### **🔬 Development Workflow**

```bash
# Start specific agent with tools
python manage_hr_tools.py --start-agent-tools job_requisition_agent
python run_sk_agents.py job_requisition_agent

# Test specific layer
python run_all_tests.py --level 2  # Test individual agents
python run_all_tests.py --level 3  # Test coordinators

# Cleanup specific layer
./cleanup.sh agents      # Clean only individual agents
./cleanup.sh coordinators # Clean coordinators + master
```

## 📋 System Management

### **🔧 MCP Tools Management (Level 1)**

```bash
# List all 28 tools and their ports
python manage_hr_tools.py --list

# Start all tools
python manage_hr_tools.py --start-all

# Start tools for specific agent
python manage_hr_tools.py --start-agent-tools job_requisition_agent

# Test specific tool
python manage_hr_tools.py --test job_requisition_agent

# Cleanup tools
python manage_hr_tools.py --cleanup
```

### **🤖 Individual Agents Management (Level 2)**

```bash
# List all 11 individual agents
python run_sk_agents.py --list

# Start single agent (development)
python run_sk_agents.py job_requisition_agent

# Start all agents simultaneously (production)
python run_sk_agents.py --all

# Cleanup agent processes
python run_sk_agents.py --cleanup
```

### **🎯 Team Coordinators Management (Level 3)**

```bash
# List all coordinators (3 teams + 1 master)
python run_coordinators.py --list

# Start single coordinator
python run_coordinators.py acquisition_team_agent

# Start all coordinators in proper order
python run_coordinators.py --all

# Cleanup coordinators
python run_coordinators.py --cleanup
```

## 🧪 4-Level Testing Framework

Our testing framework validates each architectural level systematically:

### **Level 1: MCP Tools Testing**
```bash
python test_tools.py                    # Test all 28 MCP tools
python test_tools.py --tool job-creation # Test specific tool
python test_tools.py --agent sourcing_agent # Test tools for agent
```

### **Level 2: Individual Agents Testing**
```bash
python test_individual_agents.py         # Test all 11 individual agents
python test_individual_agents.py --agent job_requisition_agent
python test_individual_agents.py --list  # Show available agents
```

### **Level 3: Team Coordinators Testing**
```bash
python test_coordinators.py              # Test all team coordinators
python test_coordinators.py --coordinator acquisition_team_agent
python test_coordinators.py --list       # Show available coordinators
```

### **Level 4: Master Integration Testing**
```bash
python test_master.py                    # Complete system integration
python test_master.py --health-only      # System health check only
python test_master.py --scenario 2       # Run specific scenario
```

### **Complete Test Suite**
```bash
python run_all_tests.py                  # Run all 4 levels
python run_all_tests.py --level 3        # Run specific level
python run_all_tests.py --start-from 2   # Start from level 2
python run_all_tests.py --continue-on-failure # Don't stop on failures
```

## 🧹 System Cleanup

Our `cleanup.sh` script provides granular cleanup control:

```bash
# Show current system status
./cleanup.sh status

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
python manage_hr_tools.py --start-agent-tools job_requisition_agent
# Tools started: job-creation (8051), job-workflow (8052), job-templates (8053)

# 2. Start the job requisition agent
python run_sk_agents.py job_requisition_agent
# Agent started on port 5020

# 3. Test the agent (new terminal)
curl http://localhost:5020/.well-known/agent-card.json
python test_individual_agents.py --agent job_requisition_agent

# 4. Cleanup
./cleanup.sh agents && ./cleanup.sh tools
```

### **Example 2: Team Coordinator with Sub-agents**

```bash
# 1. Start MCP tools
python manage_hr_tools.py --start-all

# 2. Start individual agents for acquisition team
python run_sk_agents.py sourcing_agent          # Port 5021
python run_sk_agents.py resume_screening_agent  # Port 5022
python run_sk_agents.py background_verification_agent # Port 5026
python run_sk_agents.py analytics_reporting_agent     # Port 5028

# 3. Wait for agents to be ready (2-3 seconds each)

# 4. Start acquisition team coordinator
python run_coordinators.py acquisition_team_agent  # Port 5032

# 5. Test team coordination
python test_coordinators.py --coordinator acquisition_team_agent

# 6. Cleanup
./cleanup.sh all
```

### **Example 3: Complete System Manual Testing**

```bash
# 1. Start foundation layer
python manage_hr_tools.py --start-all
sleep 5  # Allow tools to initialize

# 2. Start individual agents layer
python run_sk_agents.py --all &
sleep 10  # Allow agents to start

# 3. Start coordination layer
python run_coordinators.py --all &
sleep 15  # Allow coordinators to connect

# 4. Check system health
./cleanup.sh status

# 5. Test complete integration
python test_master.py

# 6. Cleanup everything
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

- **[HR_RECRUITMENT_ORG_CHART.md](HR_RECRUITMENT_ORG_CHART.md)**: Complete system architecture, team structures, and relationships
- **[hr_tools_config.py](hr_tools_config.py)**: Central configuration with all port mappings and tool definitions
- **Individual Agent Configs**: `hr_recruitment_agents/individual/*.yaml` - 11 specialist agent configurations
- **Coordinator Configs**: `hr_recruitment_agents/team_coordinators/*.yaml` - 4 coordinator configurations

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