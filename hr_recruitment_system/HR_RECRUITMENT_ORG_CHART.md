# HR Recruitment Multi-Agent Organizational Chart

## 🏢 **Master Level: HR Recruitment Organization**

```
                    HR RECRUITMENT MASTER COORDINATOR
                           (Port 5000 - Master)
                                    |
        ┌──────────────┬─────────────────┬─────────────────┬─────────────────┐
        |              |                 |                 |                 |
   JOB PIPELINE    ACQUISITION      EXPERIENCE         CLOSING           SUPPORT
      TEAM           TEAM            TEAM              TEAM              TEAM
   (Parallel)     (Parallel)      (Parallel)       (Sequential)      (Cross-functional)
```

---

## 🎯 **Team Level: Specialized Multi-Agent Teams**

### **TEAM 1: Job Pipeline Team** 
**Mission**: Create, approve, and publish job postings
**Coordination**: Sequential → Parallel with other teams
```
                    JOB PIPELINE TEAM LEAD
                         (Port 5020)
                             |
        ┌────────────────────┼────────────────────┐
        |                    |                    |
   JOB REQUISITION      COMPLIANCE           ANALYTICS
      AGENT               AGENT              AGENT
   (Team Leader)        (Advisor)          (Reporter)
    Port 5020           Port 5029          Port 5028
```

### **TEAM 2: Candidate Acquisition Team**
**Mission**: Find, screen, and validate candidates  
**Coordination**: Parallel processing, high throughput
```
                  ACQUISITION TEAM LEAD
                       (Port 5021)
                           |
        ┌──────────────────┼──────────────────┬─────────────────┐
        |                  |                  |                 |
   SOURCING           RESUME SCREENING    BACKGROUND        ANALYTICS
    AGENT               AGENT           VERIFICATION       AGENT
  (Team Leader)       (Processor)        AGENT           (Metrics)
   Port 5021           Port 5022        (Validator)       Port 5028
                                        Port 5026
```

### **TEAM 3: Candidate Experience Team**
**Mission**: Manage candidate journey and interactions
**Coordination**: Event-driven, candidate-centric
```
                 EXPERIENCE TEAM LEAD
                      (Port 5023)
                          |
        ┌─────────────────┼─────────────────┬─────────────────┐
        |                 |                 |                 |
  COMMUNICATION     INTERVIEW         ASSESSMENT         ANALYTICS
     AGENT          SCHEDULING          AGENT             AGENT
  (Team Leader)       AGENT          (Evaluator)       (Tracker)
   Port 5023        (Coordinator)      Port 5025        Port 5028
                     Port 5024
```

### **TEAM 4: Closing Team**
**Mission**: Finalize offers and complete hiring process
**Coordination**: Sequential with final approvals
```
                    CLOSING TEAM LEAD
                       (Port 5027)
                           |
        ┌──────────────────┼──────────────────┐
        |                  |                  |
   OFFER              COMPLIANCE         ANALYTICS
  MANAGEMENT            AGENT             AGENT
    AGENT            (Final Checks)    (Completion)
 (Team Leader)        Port 5029         Port 5028
  Port 5027
```

### **TEAM 5: Support Team**
**Mission**: Cross-functional support and oversight
**Coordination**: Always available, reactive
```
                     SUPPORT TEAM
                         |
        ┌────────────────┼────────────────┐
        |                |                |
   COMPLIANCE       ANALYTICS        AUDIT &
     AGENT           AGENT          REPORTING
  (Legal/Regulatory) (Metrics)      (Oversight)
    Port 5029        Port 5028       Port 5030
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

| Agent | Reports To | Collaborates With | Tools Count | Team Role |
|-------|-----------|-------------------|-------------|-----------|
| Job Requisition | Master Coordinator | Compliance, Analytics | 15 | Team Leader |
| Sourcing | Master Coordinator | Resume Screening, Background Check | 12 | Team Leader |
| Resume Screening | Sourcing Agent | Communication, Assessment | 8 | Processor |
| Communication | Master Coordinator | All Agents | 10 | Team Leader |
| Interview Scheduling | Communication Agent | Assessment, Offer Management | 6 | Coordinator |
| Assessment | Communication Agent | Resume Screening, Analytics | 4 | Evaluator |
| Background Check | Sourcing Agent | Compliance, Offer Management | 6 | Validator |
| Offer Management | Master Coordinator | Background Check, Compliance | 8 | Team Leader |
| Analytics | Master Coordinator | All Agents | 6 | Cross-Team |
| Compliance | Master Coordinator | All Agents | 4 | Cross-Team |

This organizational chart provides the blueprint for building your A2A multi-agent system with clear hierarchies, responsibilities, and tool assignments.