# HR Recruitment Multi-Agent Organizational Chart

## 🏢 **Master Level: HR Recruitment Organization**

```
                    HR RECRUITMENT MASTER COORDINATOR
                           (Port 5040 - Master)
                                    |
        ┌──────────────┬─────────────────┬─────────────────┬─────────────────┐
        |              |                 |                 |                 |
   JOB PIPELINE    ACQUISITION      EXPERIENCE         CLOSING         HR SUMMARIZATION
    TEAM AGENT      TEAM AGENT      TEAM AGENT       TEAM AGENT           AGENT
   (Port 5031)     (Port 5032)     (Port 5033)      (Port 5034)        (Port 5030)
   (Sequential)    (Parallel)      (Event-driven)   (Sequential)      (Cross-functional)
```

---

## 🎯 **Team Level: Specialized Multi-Agent Teams**

### **TEAM 1: Job Pipeline Team Agent**
**Mission**: Create, approve, and publish job postings
**Coordination**: A2A coordination with sub-agents
```
                    JOB PIPELINE TEAM AGENT
                         (Port 5031)
                             |
        ┌────────────────────┼────────────────────┐
        |                    |                    |
   JOB REQUISITION      COMPLIANCE           ANALYTICS
      AGENT               AGENT              AGENT
   (Specialist)         (Advisor)          (Reporter)
    Port 5020           Port 5029          Port 5028
```

### **TEAM 2: Acquisition Team Agent**
**Mission**: Find, screen, and validate candidates
**Coordination**: A2A coordination with parallel processing
```
                  ACQUISITION TEAM AGENT
                       (Port 5032)
                           |
        ┌──────────────────┼──────────────────┬─────────────────┐
        |                  |                  |                 |
   SOURCING           RESUME SCREENING    BACKGROUND        ANALYTICS
    AGENT               AGENT           VERIFICATION       AGENT
  (Specialist)        (Processor)        AGENT           (Metrics)
   Port 5021           Port 5022        (Validator)       Port 5028
                                        Port 5026
```

### **TEAM 3: Experience Team Agent**
**Mission**: Manage candidate journey and interactions
**Coordination**: A2A coordination with event-driven workflow
```
                 EXPERIENCE TEAM AGENT
                      (Port 5033)
                          |
        ┌─────────────────┼─────────────────┬─────────────────┐
        |                 |                 |                 |
  COMMUNICATION     INTERVIEW         ASSESSMENT         ANALYTICS
     AGENT          SCHEDULING          AGENT             AGENT
  (Specialist)        AGENT          (Evaluator)       (Tracker)
   Port 5023        (Coordinator)      Port 5025        Port 5028
                     Port 5024
```

### **TEAM 4: Closing Team Agent**
**Mission**: Finalize offers and complete hiring process
**Coordination**: A2A coordination with sequential approvals
```
                    CLOSING TEAM AGENT
                       (Port 5034)
                           |
        ┌──────────────────┼──────────────────┐
        |                  |                  |
   OFFER              COMPLIANCE         ANALYTICS
  MANAGEMENT            AGENT             AGENT
    AGENT            (Final Checks)    (Completion)
 (Specialist)         Port 5029         Port 5028
  Port 5027
```

### **TEAM 5: HR Summarization Agent**
**Mission**: Cross-functional content generation and analysis support
**Coordination**: Available to all teams for content synthesis
```
                 HR SUMMARIZATION AGENT
                       (Port 5030)
                          |
        ┌─────────────────┼─────────────────┐
        |                 |                 |
   RECRUITMENT        CANDIDATE         PROCESS
   SUMMARIES          PROFILES         ANALYSIS
   (Content Gen)      (Synthesis)     (Insights)
```

---

## 👤 **Agent Level: Individual AI Agents**

### **Job Requisition Agent (Port 5020)**
**Role**: Job Pipeline Team Leader
**Responsibilities**: Job creation, approval workflow management
```
JOB REQUISITION AGENT
         |
    ┌────┼────┬────────────┐
    |    |    |            |
   JOB  JOB  JOB      COORDINATION
  CREATE WORKFLOW TEMPLATES   TOOLS
  Tools  Tools   Tools      A2A Comms
```

### **Sourcing Agent (Port 5021)**
**Role**: Acquisition Team Leader  
**Responsibilities**: Candidate discovery and talent pool management
```
SOURCING AGENT
       |
   ┌───┼───┬──────────┬────────────┐
   |   |   |          |            |
 SOCIAL TALENT CANDIDATE COORDINATION
SOURCING POOL  OUTREACH    TOOLS
 Tools  Tools   Tools    A2A Comms
```

### **Resume Screening Agent (Port 5022)**
**Role**: Acquisition Team Processor
**Responsibilities**: Resume analysis and candidate matching
```
RESUME SCREENING AGENT
          |
    ┌─────┼─────┬───────────┐
    |     |     |           |
 DOCUMENT MATCHING REPORTING COORDINATION
PROCESSING ENGINE  TOOLS    TOOLS
  Tools   Tools   Tools   A2A Comms
```

### **Communication Agent (Port 5023)**
**Role**: Experience Team Leader
**Responsibilities**: Candidate communication and experience management
```
COMMUNICATION AGENT
         |
    ┌────┼────┬─────────────┐
    |    |    |             |
  EMAIL ENGAGEMENT TEMPLATE COORDINATION
 SERVICE TRACKING  MGMT     TOOLS
  Tools   Tools    Tools   A2A Comms
```

### **Interview Scheduling Agent (Port 5024)**
**Role**: Experience Team Coordinator
**Responsibilities**: Interview coordination and calendar management
```
INTERVIEW SCHEDULING AGENT
           |
    ┌──────┼──────┬──────────┐
    |      |      |          |
 CALENDAR BOOKING REMINDER COORDINATION
INTEGRATION MGMT   SYSTEM    TOOLS
  Tools    Tools   Tools   A2A Comms
```

### **Assessment Agent (Port 5025)**
**Role**: Experience Team Evaluator
**Responsibilities**: Skills testing and candidate evaluation
```
ASSESSMENT AGENT
        |
   ┌────┼────┬──────────┐
   |    |    |          |
  TEST SCORING REPORT COORDINATION
 ENGINE SYSTEM SYSTEM   TOOLS
 Tools  Tools  Tools   A2A Comms
```

### **Background Verification Agent (Port 5026)**
**Role**: Acquisition Team Validator
**Responsibilities**: Background checks and verification
```
BACKGROUND VERIFICATION AGENT
            |
    ┌───────┼───────┬───────────┐
    |       |       |           |
 VERIFICATION EMPLOYMENT EDUCATION COORDINATION
   ENGINE     CHECK     CHECK     TOOLS
   Tools      Tools     Tools   A2A Comms
```

### **Offer Management Agent (Port 5027)**
**Role**: Closing Team Leader
**Responsibilities**: Offer creation and negotiation management
```
OFFER MANAGEMENT AGENT
         |
    ┌────┼────┬─────────────┐
    |    |    |             |
  OFFER NEGOTIATION APPROVAL COORDINATION
 GENERATION MGMT   WORKFLOW   TOOLS
  Tools     Tools   Tools    A2A Comms
```

### **Analytics & Reporting Agent (Port 5028)**
**Role**: Cross-Team Metrics Provider
**Responsibilities**: Data analysis and reporting across all teams
```
ANALYTICS & REPORTING AGENT
            |
    ┌───────┼───────┬───────────┐
    |       |       |           |
  METRICS DASHBOARD PREDICTIVE COORDINATION
  ENGINE  GENERATOR ANALYTICS   TOOLS
  Tools    Tools     Tools     A2A Comms
```

### **Compliance Agent (Port 5029)**
**Role**: Cross-Team Legal Advisor
**Responsibilities**: Regulatory compliance and legal oversight
```
COMPLIANCE AGENT
        |
   ┌────┼────┬─────────────┐
   |    |    |             |
  EEOC  AUDIT  DATA      COORDINATION
 CHECK  TRAIL PRIVACY      TOOLS
 Tools  Tools  Tools     A2A Comms
```

### **HR Summarization Agent (Port 5030)**
**Role**: Content Generation Specialist
**Responsibilities**: Recruitment content synthesis and analysis
```
HR SUMMARIZATION AGENT
          |
     ┌────┼────┐
     |    |    |
  CONTENT TEXT  ANALYSIS
    GEN  SYNTH  REPORTS
   (Pure LLM Agent)
```

### **Job Pipeline Team Agent (Port 5031)**
**Role**: Team Coordinator - Job Creation Workflow
**Responsibilities**: Coordinates job requisition, compliance, and analytics
```
JOB PIPELINE TEAM AGENT
         |
    ┌────┼────┬──────────┐
    |    |    |          |
   JOB  COMP  ANALYTICS A2A COORD
  REQ.  AGT   AGENT     COMMS
 (5020) (5029) (5028)
```

### **Acquisition Team Agent (Port 5032)**
**Role**: Team Coordinator - Candidate Acquisition
**Responsibilities**: Coordinates sourcing, screening, and background verification
```
ACQUISITION TEAM AGENT
         |
    ┌────┼────┬──────────┬──────────┐
    |    |    |          |          |
 SOURCING RESUME BG VERIFY ANALYTICS A2A COORD
  AGENT   AGT    AGENT    AGENT     COMMS
 (5021)  (5022)  (5026)   (5028)
```

### **Experience Team Agent (Port 5033)**
**Role**: Team Coordinator - Candidate Experience
**Responsibilities**: Coordinates communication, scheduling, and assessment
```
EXPERIENCE TEAM AGENT
         |
    ┌────┼────┬──────────┬──────────┐
    |    |    |          |          |
  COMM  INTERVIEW ASSESS  ANALYTICS A2A COORD
  AGENT  SCHED   AGENT   AGENT     COMMS
 (5023)  (5024)  (5025)   (5028)
```

### **Closing Team Agent (Port 5034)**
**Role**: Team Coordinator - Offer Management
**Responsibilities**: Coordinates offer management, compliance, and analytics
```
CLOSING TEAM AGENT
         |
    ┌────┼────┬──────────┐
    |    |    |          |
  OFFER  COMP  ANALYTICS A2A COORD
  MGMT   AGT   AGENT     COMMS
 (5027) (5029) (5028)
```

### **HR Team Coordinator Agent (Port 5040)**
**Role**: Master Coordinator
**Responsibilities**: Orchestrates all team agents and workflows
```
HR TEAM COORDINATOR AGENT
          |
     ┌────┼────┬────────┬────────┐
     |    |    |        |        |
   JOB  ACQUI  EXPER   CLOSING  A2A COORD
  PIPELINE SITION IENCE   TEAM    COMMS
  (5031)  (5032) (5033)  (5034)
```

---

## 🔧 **Tool Level: MCP Servers and Individual Tools**

### **Example: Job Requisition Agent Tools Breakdown**
```
JOB REQUISITION AGENT (Port 5020)
│
├── 🔧 Job Creation MCP Server (Port 8051)
│   ├── create_job_draft()
│   ├── update_job_description() 
│   ├── add_job_responsibilities()
│   ├── set_job_requirements()
│   └── get_job_draft()
│
├── ⚙️ Job Workflow MCP Server (Port 8052)
│   ├── submit_for_approval()
│   ├── approve_job_posting()
│   ├── publish_job_posting()
│   ├── get_workflow_status()
│   └── list_pending_approvals()
│
└── 📋 Job Templates MCP Server (Port 8053)
    ├── list_job_templates()
    ├── get_job_template()
    ├── create_job_from_template()
    ├── create_custom_template()
    └── update_template()
```

---

## 🎯 **Implementation Strategy**

### **Phase 1: Build Individual Agents**
1. ✅ Create MCP tools (COMPLETED)
2. Build individual AI agents with ADK
3. Test each agent independently

### **Phase 2: Build Sub-Teams**
1. Implement A2A communication between agents
2. Create team coordination logic
3. Test team workflows

### **Phase 3: Build Master Coordination**
1. Create Master Coordinator agent
2. Implement multi-team orchestration
3. Add parallel workflow management

### **Phase 4: Add Intelligence**
1. Event-driven triggers
2. Predictive analytics
3. Adaptive team formation

---

## 📊 **Agent Relationship Matrix**

### **Level 1: Individual Specialist Agents**
| Agent | Reports To | Tools Count | Specialization |
|-------|-----------|-------------|----------------|
| Job Requisition (5020) | Job Pipeline Team | 3 | Job creation and management |
| Sourcing (5021) | Acquisition Team | 3 | Candidate sourcing and discovery |
| Resume Screening (5022) | Acquisition Team | 2 | Resume analysis and matching |
| Communication (5023) | Experience Team | 2 | Candidate communications |
| Interview Scheduling (5024) | Experience Team | 3 | Interview coordination |
| Assessment (5025) | Experience Team | 3 | Skills testing and evaluation |
| Background Verification (5026) | Acquisition Team | 3 | Background checks and validation |
| Offer Management (5027) | Closing Team | 3 | Offer creation and negotiation |
| Analytics Reporting (5028) | All Team Agents | 3 | Cross-team metrics and reporting |
| Compliance (5029) | Job Pipeline & Closing Teams | 3 | Legal and regulatory compliance |

### **Level 2: Team Coordinator Agents**
| Team Agent | Reports To | Coordinates | Team Mission |
|------------|-----------|-------------|--------------|
| Job Pipeline Team (5031) | Master Coordinator | Job Req, Compliance, Analytics | Job creation workflow |
| Acquisition Team (5032) | Master Coordinator | Sourcing, Resume, BG Check, Analytics | Candidate acquisition |
| Experience Team (5033) | Master Coordinator | Comm, Scheduling, Assessment, Analytics | Candidate experience |
| Closing Team (5034) | Master Coordinator | Offer Mgmt, Compliance, Analytics | Offer finalization |

### **Level 3: Master Coordination**
| Agent | Role | Coordinates | Purpose |
|-------|------|-------------|---------|
| HR Team Coordinator (5040) | Master Orchestrator | All Team Agents | End-to-end recruitment |

### **Support Agent**
| Agent | Role | Serves | Purpose |
|-------|------|--------|---------|
| HR Summarization (5030) | Content Specialist | All Teams | Content generation and synthesis |

## 🏗️ **Implementation Summary**

This organizational chart provides the blueprint for a **3-Level Hierarchical A2A Multi-Agent System**:

### **Architecture Highlights:**
- **16 Total Agents**: 10 specialists + 4 team coordinators + 1 master coordinator + 1 support agent
- **28 MCP Tools**: All individual agent tools remain intact
- **Pure A2A Communication**: No MCP tools needed for coordination
- **Scalable Design**: Easy to add new teams or specialists

### **Port Allocation:**
- **5020-5029**: Individual specialist agents
- **5030**: HR Summarization Agent (support)
- **5031-5034**: Team coordinator agents
- **5040**: Master coordinator agent
- **8051-8143**: MCP tool servers (by agent groupings)

### **Key Benefits:**
1. **Clear Separation of Concerns**: Each level has distinct responsibilities
2. **Fault Tolerance**: Team agents can operate independently if master coordinator fails
3. **Parallel Processing**: Teams can work simultaneously on different aspects
4. **Easy Scaling**: Add new specialists to existing teams or create new teams
5. **Consistent Communication**: All coordination uses A2A patterns from 6_sk_agent_to_agent

This system implements sophisticated workforce automation with intelligent coordination at multiple organizational levels.