# HR Recruitment System - Complete MCP Implementation

This folder contains the complete HR recruitment system implementation with **28 MCP tools across 11 specialized agents** with comprehensive testing framework and simplified management tools.

## 📂 Folder Structure

```
hr_recruitment_system/
├── 🔧 mcp_tools_hr/                    # 28 MCP tools (main implementation)
├── 👥 hr_recruitment_agents/           # 11 Agent YAML configurations
├── 🚀 run_recruitment_http.py          # MCP tool server deployment
├── 🤖 run_sk_agents.py                 # Semantic Kernel agent runner
├── 🛠️ manage_hr_tools.py               # Simplified tool management
├── 🧹 cleanup_ports.py                 # Port cleanup utility
├── 🧪 test_agent_mcp_tools.py          # Quick test framework (all agents)
├── 🔍 test_with_logs.py                # Detailed log verification
└── 📊 test_hr_agents.py                # Comprehensive test suite
```

## ⚡ Quick Start Guide

### **Recommended Workflow**

```bash
# 1. Start all MCP tools
python manage_hr_tools.py --start-all-tools

# 2. Start all agents
python run_sk_agents.py --all

# 3. Test the system
python test_agent_mcp_tools.py --all

# 4. Cleanup when done
python manage_hr_tools.py --cleanup  # Clean MCP tools
python run_sk_agents.py --cleanup     # Clean agents
```

### **Development Workflow**

```bash
# 1. Start tools for specific agent
python manage_hr_tools.py --start-agent-tools job_requisition_agent

# 2. Start the agent
python run_sk_agents.py job_requisition_agent

# 3. Test the agent
python test_agent_mcp_tools.py --agent job_requisition_agent
```

# 📋 Complete Usage Guide

## 🚀 Management Commands

### **Tool Management**
```bash
# List tools and ports
python manage_hr_tools.py --list-tools

# Start all tools
python manage_hr_tools.py --start-all-tools

# Start specific tools
python manage_hr_tools.py --start-tool job-creation
python manage_hr_tools.py --start-agent-tools job_requisition_agent

# Cleanup tools
python manage_hr_tools.py --cleanup
```

### **Agent Management**
```bash
# List agents
python run_sk_agents.py --list

# Start single agent (development)
python run_sk_agents.py job_requisition_agent

# Start all agents (production)
python run_sk_agents.py --all

# Cleanup agents
python run_sk_agents.py --cleanup
```

## 🧪 Testing Framework

```bash
# Quick agent testing
python test_agent_mcp_tools.py --list
python test_agent_mcp_tools.py --agent job_requisition_agent
python test_agent_mcp_tools.py --all


# Detailed log analysis
python test_with_logs.py --agent job_requisition_agent

# Comprehensive test suite
python test_hr_agents.py
```

## 🛠️ Complete Workflow Examples

### **Example 1: Test Single Agent End-to-End**
```bash
# 1. Start agent tools
python manage_hr_tools.py --start-agent-tools job_requisition_agent

# 2. In another terminal, start the agent
python run_sk_agents.py job_requisition_agent

# 3. Test the agent (quick verification)
python test_agent_mcp_tools.py --agent job_requisition_agent

# 4. Cleanup when done
python manage_hr_tools.py --cleanup  # Clean tools
python run_sk_agents.py --cleanup     # Clean agents
# Press Ctrl+C in agent terminal
```

### **Example 2: Run All Agents and Test Together**
```bash
# 1. Start all agent tools
python manage_hr_tools.py --start-all-tools

# 2. Start all agents simultaneously
python run_sk_agents.py --all &

# 3. Wait for startup, then run comprehensive tests
sleep 10
python test_hr_agents.py

# 4. Or run quick tests
python test_agent_mcp_tools.py --all

# 5. Cleanup everything
python manage_hr_tools.py --cleanup  # Clean tools
python run_sk_agents.py --cleanup     # Clean agents
# Kill all agent processes with Ctrl+C
```


## 🎯 System Architecture

The system implements a multi-agent organizational structure with **11 specialized agents** organized into teams. Each agent has dedicated MCP servers handling specific domain aspects.

## 📊 Statistics

- **Total MCP Servers**: 28 (100% Complete)
- **Individual Tools**: 75+ tools across all servers  
- **Agents with Full Tool Sets**: 11/11 (100%)
- **Agent Port Range**: 5020-5030 (systematic allocation)
- **Tool Port Range**: 8051-8143 (systematic allocation) 
- **Architecture**: Focused design (2-3 servers per agent)
- **Testing Framework**: 3 comprehensive test scripts
- **Management Tools**: Simplified scripts for deployment and cleanup

## 🛠️ Technical Details

- **Framework**: FastMCP with stateless HTTP transport
- **Testing**: Comprehensive tool-specific argument generation
- **Deployment**: Individual server deployment with port management
- **Protocol**: MCP (Model Control Protocol) for tool communication

## 🛠️ Setup Requirements

### **Prerequisites**
1. **Python Environment**: Ensure all dependencies are installed
2. **Semantic Kernel Server**: The `sk_a2a_custom_mcp_agent` backend must be available
3. **Port Availability**: Agents use ports 5020-5030, MCP tools use ports 8051-8143

### **Direct Testing with curl**

**Test MCP Tools Directly**:
```bash
# Dynamic tool testing (recommended)
python test_hr_tools_direct.py --list
python test_hr_tools_direct.py --tool job-creation
python test_hr_tools_direct.py --tool social-sourcing --function search_linkedin

# Manual curl testing
curl -X POST http://localhost:8051/mcp \
  -H "Content-Type: application/json" \
  -d '{"jsonrpc":"2.0","method":"tools/call","params":{"name":"create_job_draft","arguments":{"title":"Senior Python Developer","department":"Engineering"}},"id":1}'

curl -X POST http://localhost:8061/mcp \
  -H "Content-Type: application/json" \
  -d '{"jsonrpc":"2.0","method":"tools/call","params":{"name":"search_linkedin","arguments":{"keywords":"Python developer","location":"San Francisco"}},"id":1}'
```

**Test Agents Directly**:
```bash
# Check agent availability
curl http://localhost:5020/.well-known/agent-card.json

# Send message to job requisition agent
curl -X POST http://localhost:5020 \
  -H "Content-Type: application/json" \
  -d '{"jsonrpc":"2.0","method":"message/send","params":{"content":"Create a Senior Python Developer job posting"},"id":1}'

# Send message to sourcing agent
curl -X POST http://localhost:5021 \
  -H "Content-Type: application/json" \
  -d '{"jsonrpc":"2.0","method":"message/send","params":{"content":"Find Python developers in Seattle"},"id":1}'
```

## 🎯 Implementation Comparison

| Feature | Semantic Kernel (SK) | Agent Development Kit (ADK) |
|---------|---------------------|------------------------------|
| **Context Preservation** | ✅ Full conversation history | ❌ Stateless |
| **Session Management** | ✅ Per-session isolation | ❌ No sessions |
| **Tool Integration** | ✅ Advanced MCP plugins | ✅ Basic MCP support |
| **Performance** | 🟡 Moderate overhead | ✅ Lightweight |
| **Multi-Agent Support** | ✅ Run all simultaneously | ✅ Individual instances |
| **Recommended For** | Production, complex workflows | Testing, simple tasks |

## 📚 Documentation

- **HR_RECRUITMENT_ORG_CHART.md**: Complete organizational hierarchy, team structures, agent relationships, and port assignments
- **manage_hr_tools.py**: Simplified tool management script for quick setup and cleanup
- **test_agent_mcp_tools.py**: Quick agent testing with MCP tool calling verification
- **test_with_logs.py**: Detailed log analysis to prove MCP tool calling vs LLM fallback
- **test_hr_agents.py**: Comprehensive test suite with scenario-based validation for all agents

## 🎉 Ready for A2A Implementation

This system provides the complete foundation for:
1. ✅ All MCP tools built (28/28 servers)
2. ✅ SK & ADK agent implementations  
3. 🤝 Agent-to-Agent communication
4. 👥 Multi-agent team coordination
5. 🎯 Master orchestration layer
6. ✅ Context preservation & session management (SK)
7. ✅ Automatic port cleanup & process management

The HR recruitment system is now 100% complete with both SK and ADK implementations ready for production use!