# HR System Query Tracing Guide

This guide shows you how to use the **fixed and enhanced** query tracing scripts to monitor and debug your HR recruitment system's agent interactions, tool calls, and execution flow.

## ✅ Recent Fixes Applied

Both query scripts have been **fixed and enhanced**:
- ✅ **JSON-RPC Method Fixed**: Changed from incorrect `"process_message"` to correct `"message/send"`
- ✅ **Enhanced Readability**: Full response content display (800 chars vs 100)
- ✅ **Better Formatting**: Clear `✅ Main Query Response:` labels for important results
- ✅ **Multi-Team Coordination**: Proven to work across all team boundaries

## Overview

The HR recruitment system has multiple layers of agents working in **Agent-to-Agent (A2A)** coordination:
- **Individual Agents** (ports 5020-5030): Job requisition, sourcing, screening, etc.
- **Team Coordinators** (ports 5032-5034): Acquisition, experience, closing teams
- **Master Coordinator** (port 5040): Orchestrates everything with intelligent delegation
- **Tool Servers** (ports 8051-8143): 28 MCP tools for specialized HR operations

## Scripts Available

### 1. `query_master_agent.py` - Basic Query Client ✅ FIXED
Simple, fast script for sending queries and capturing responses with colored logging.

### 2. `advanced_query_tracer.py` - Full System Tracer ✅ FIXED & ENHANCED
Advanced script that captures all HTTP traffic, agent calls, tool invocations, and multi-team coordination patterns.

## Quick Start

### Step 1: Setup Environment
```bash
cd hr_recruitment_system

# Create and activate virtual environment
python3 -m venv venv
source venv/bin/activate

# Install required dependencies
pip install semantic-kernel aiohttp requests colorama websockets
```

### Step 2: Start the System (Correct Order)
```bash
# 1. Start all MCP tool servers (Level 1 - Foundation)
./start_tools.sh --start-all

# 2. Start all individual agents (Level 2 - Specialists)
./start_agents.sh --all

# 3. Start team coordinators (Level 3 - Orchestration)
./start_coordinators.sh --all

# 4. Check system status
./status.sh
```

### Step 3: Run Queries with Tracing

#### Basic Query Logging
```bash
# Single query
python query_master_agent.py "Create a job posting for a Senior Python Developer"

# Interactive mode
python query_master_agent.py --interactive
```

#### Advanced Tracing
```bash
# Single query with full tracing
python advanced_query_tracer.py "Create a job posting for a Senior Python Developer"

# Interactive mode with custom trace duration
python advanced_query_tracer.py --interactive --trace-duration 60

# Save trace to specific file
python advanced_query_tracer.py "Complex hiring workflow" --output my_trace.json
```

## 🎯 Sample Queries to Test Different Coordination Patterns

### ✅ Single Team Queries

#### Simple Job Creation (Job Pipeline Team)
```bash
python advanced_query_tracer.py "Create a job posting for a Senior Python Developer in the Engineering department, remote location"
```
**Expected Path**: Master → Job Pipeline Team → Job Requisition Agent → Tool Servers

#### Basic Candidate Sourcing (Acquisition Team)
```bash
python advanced_query_tracer.py "Find candidates for our Software Engineer position with 3+ years React experience"
```
**Expected Path**: Master → Acquisition Team → Sourcing Agent → Tool Servers

### 🔄 Multi-Team Coordination Queries

#### Full Hiring Pipeline (All 3 Teams) ⭐
```bash
python advanced_query_tracer.py "We need to urgently hire 3 Senior Software Engineers for our AI team. Please create job postings, find candidates, screen them, schedule interviews, conduct assessments, and prepare offers. We need them to start within 6 weeks."
```
**Expected Teams**:
- **Acquisition Team** (5032) → Job creation, sourcing, screening
- **Experience Team** (5033) → Interviews, assessments, communication
- **Closing Team** (5034) → Offers, negotiations, compliance

#### Acquisition → Experience Workflow ⭐
```bash
python advanced_query_tracer.py "I have 25 applications for our DevOps Engineer position. The acquisition team should screen all resumes and identify top 8 candidates. Then the experience team should schedule interviews for next week and prepare assessments."
```
**Expected Teams**:
- **Acquisition Team** (5032) → Resume screening, candidate identification
- **Experience Team** (5033) → Interview scheduling, assessment preparation

#### Experience → Closing Workflow ⭐
```bash
python advanced_query_tracer.py "We completed interviews for the Marketing Manager position. The experience team needs to send assessment feedback to all 5 candidates and coordinate with the closing team to prepare competitive salary offers for the top 2 candidates, ensuring all compliance requirements are met."
```
**Expected Teams**:
- **Experience Team** (5033) → Assessment feedback, candidate communication
- **Closing Team** (5034) → Offer preparation, compliance verification

#### International Hiring (Complex Multi-Team) ⭐
```bash
python advanced_query_tracer.py "We're hiring internationally for our London office. The acquisition team should source European candidates, the experience team should coordinate virtual interviews across time zones, and the closing team must ensure UK visa sponsorship compliance."
```
**Expected Teams**: All teams working together with international complexity

### 📊 Status and Analytics Queries
```bash
python advanced_query_tracer.py "What's the status of all my recent job postings and how many candidates have applied?"
```
**Expected Path**: Master → Experience Team → Analytics Agent → Tool Servers

## 📊 Understanding the Enhanced Output

### ✅ Improved Readability Features
- **Enhanced Response Display**: Main query responses show full content (800 chars vs 100)
- **Clear Visual Indicators**: `✅ Main Query Response:` labels for important results
- **Better Content Extraction**: Shows actual job postings and coordination messages instead of JSON noise
- **Intelligent Filtering**: Focuses on meaningful events while preserving trace completeness

### Color Coding
- **🔵 Blue**: HTTP requests
- **🟢 Green**: HTTP responses (success) + Main query response labels
- **🔴 Red**: Errors
- **🟣 Magenta**: Agent calls
- **🟡 Yellow**: Tool calls
- **⚫ Gray**: System events and monitoring

### Trace Event Types
- `HTTP_REQUEST`: Request sent to an agent
- `HTTP_RESPONSE`: Response received from an agent (now with enhanced content display)
- `AGENT_CALL`: One agent calling another
- `TOOL_CALL`: Agent using an MCP tool
- `AGENT_STATUS`: Health check results (minimized for readability)
- `LOG_MONITORING_START`: System monitoring initiation

### Key Information Captured
1. **Multi-Team Coordination**: See explicit delegation to specific team agents (5032, 5033, 5034)
2. **Agent Interaction Sequence**: Which agents were called in order
3. **Workflow Dependencies**: How teams hand off tasks to each other
4. **Tool Usage**: What tools were invoked and by whom
5. **Timing**: How long each operation took (especially useful for 5-10 second responses)
6. **Readable Content**: Actual job postings, coordination messages, and results
7. **Errors**: Any failures in the chain

## 🔧 Troubleshooting Common Issues

### ✅ FIXED: "Method not found: process_message" Error
**Problem**: `{"code": -32601, "message": "Method not found: process_message"}`
**Solution**: Both scripts have been fixed to use the correct `"message/send"` method.

### Virtual Environment Setup
```bash
# Create venv if not exists
python3 -m venv venv
source venv/bin/activate

# Install all required dependencies
pip install semantic-kernel aiohttp requests colorama websockets
```

### Agents Not Responding
```bash
# Check if agents are running
./status.sh

# Clean up and restart in correct order
./cleanup.sh all
./start_tools.sh --start-all
./start_agents.sh --all
./start_coordinators.sh --all
```

### Connection Refused Errors
- ✅ **Ensure proper startup order**: Tools → Individual Agents → Team Coordinators
- ✅ **Check virtual environment**: Make sure `source venv/bin/activate` is run
- ✅ **Verify ports**: Use `./status.sh` to check which services are running
- ✅ **Wait for startup**: Allow 5-10 seconds between each startup step

### "Master agent not available" Error
```bash
# Verify master coordinator is running
curl http://localhost:5040/.well-known/agent-card.json

# If not running, restart coordinators
./start_coordinators.sh --all
```

## Advanced Usage

### Custom Master URL
```bash
python advanced_query_tracer.py "query" --master-url http://localhost:5040
```

### Extended Tracing Duration
```bash
python advanced_query_tracer.py "complex query" --trace-duration 120
```

### Automatic Trace Organization ✅ NEW
```bash
# All traces are automatically saved to traces/ directory
python advanced_query_tracer.py "query"  # Automatically saves to traces/trace_YYYYMMDD_HHMMSS.json

# Custom output location (still within traces/)
python advanced_query_tracer.py "query" --output traces/custom_trace.json

# Manual timestamp naming
python advanced_query_tracer.py "query" --output traces/$(date +%Y%m%d_%H%M%S).json
```

## Sample Output Analysis

When you run a query, you'll see output like:
```
[14:30:15.123] HTTP_REQUEST CLIENT → MASTER_COORDINATOR POST /chat
    Payload: {"message": "Create job posting...", "conversation_id": "trace_..."}

[14:30:15.145] HTTP_RESPONSE MASTER_COORDINATOR → CLIENT 200 (22.5ms)
    Response: {"status": "processing", "workflow_id": "..."}

[14:30:15.150] HTTP_REQUEST MASTER_COORDINATOR → ACQUISITION_TEAM POST /delegate
    Payload: {"task": "job_creation", "details": {...}}

[14:30:15.180] HTTP_REQUEST ACQUISITION_TEAM → JOB_REQUISITION POST /create_job
    Payload: {"title": "Senior Python Developer", ...}

[14:30:15.200] HTTP_REQUEST JOB_REQUISITION → TOOL_SERVER_1 POST /mcp
    Payload: {"method": "tools/call", "params": {"name": "create_job_draft"}}
```

This shows:
1. Query sent to master coordinator
2. Master delegates to acquisition team
3. Acquisition team calls job requisition agent
4. Job requisition agent uses MCP tool

## Files Generated

### Trace Files (Automatically Organized) ✅ NEW
All trace files are automatically saved in the `traces/` directory:
- `traces/trace_YYYYMMDD_HHMMSS.json`: Full trace data
- `traces/trace_YYYYMMDD_HHMMSS_summary.json`: Execution summary
- The `traces/` directory is automatically created if it doesn't exist
- All trace files are excluded from git via `.gitignore`

### Log Files
- Individual agent logs (if configured)
- System health checks
- Error logs

## Performance Tips

1. **Start with shorter traces** (30s) for quick debugging
2. **Use specific queries** to test particular agent paths
3. **Save traces** for complex scenarios to analyze later
4. **Compare traces** before/after changes to see differences

## Integration with Development

### Debug Workflow
1. Run trace on failing query
2. Identify where the chain breaks
3. Check specific agent logs
4. Fix issue and re-trace
5. Compare before/after traces

### Performance Analysis
1. Look for slow HTTP responses (>1000ms)
2. Identify bottleneck agents
3. Check tool call frequencies
4. Optimize based on patterns

## Example Scenarios

### Scenario 1: Job Creation Not Working
```bash
# Trace the creation process
python advanced_query_tracer.py "Create a Software Engineer position"

# Look for:
# - Did master coordinator receive the query?
# - Which team did it delegate to?
# - Did the team call the right individual agent?
# - Were the tool calls successful?
```

### Scenario 2: Slow Response Times
```bash
# Run with extended monitoring
python advanced_query_tracer.py "Complex hiring workflow" --trace-duration 90

# Check summary for:
# - Total execution time
# - Individual request durations
# - Number of agent hops
# - Tool call overhead
```

### Scenario 3: Missing Agent Interactions
```bash
# Use interactive mode to test step by step
python advanced_query_tracer.py --interactive

# Try queries like:
# "Test acquisition team"
# "Test experience team"
# "Test closing team"
# "Test master coordination"
```

## 🚀 Enhanced A2A Multi-Team Coordination Features

### ✅ What's New and Fixed

#### **Fixed Scripts**
- ✅ **JSON-RPC Method**: Corrected `"process_message"` → `"message/send"`
- ✅ **Enhanced Readability**: 800-character response display vs 100
- ✅ **Clear Visual Indicators**: `✅ Main Query Response:` for important results
- ✅ **Better Content Extraction**: Shows actual coordination messages and job postings

#### **Multi-Team Coordination Proven**
- ✅ **Master Coordinator** (5040) → Intelligent task delegation
- ✅ **Acquisition Team** (5032) → Job creation, sourcing, screening
- ✅ **Experience Team** (5033) → Interviews, assessments, communication
- ✅ **Closing Team** (5034) → Offers, negotiations, compliance

### 🎯 Key Coordination Patterns

1. **Sequential Workflows**: Acquisition → Experience → Closing
2. **Parallel Processing**: Multiple teams working simultaneously
3. **Dependency Management**: Teams waiting for handoffs from other teams
4. **Intelligent Delegation**: Master coordinator choosing appropriate teams

### 📊 Sample Output Quality

**Before Fix**:
```
Response: {"jsonrpc": "2.0", "id": "trace_175796852", "result": {"taskId": "560bf149-2eb6"...
```

**After Enhancement**:
```
✅ Main Query Response:
Alright, I will coordinate activities with the respective team agents...

### **Acquisition Team Agent (5032)**,
Please screen the 25 applications we have received for the DevOps Engineer position.

### **Experience Team Agent (5033)**,
Once the Acquisition Team provides the list of the top 8 candidates...

### **Closing Team Agent (5034)**,
Please prepare competitive salary offers for the top 2 candidates...
```

### 🎉 Ready for Production Use

This comprehensive tracing system now provides **crystal-clear visibility** into your **Agent-to-Agent (A2A) multi-team HR recruitment workflows**, helping you understand exactly how queries flow through the system and identify any issues in the agent interaction chain.

**Perfect for**:
- 🔍 **Debugging multi-team workflows**
- 📈 **Performance analysis across team boundaries**
- 🎯 **Understanding A2A coordination patterns**
- 🛠️ **Development and testing of complex hiring pipelines**