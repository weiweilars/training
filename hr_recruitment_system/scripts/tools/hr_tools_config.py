#!/usr/bin/env python3
"""
HR Tools Configuration
Centralized configuration for all HR MCP tools and agents
"""

# Complete HR MCP Tools configuration
HR_TOOLS = {
    # Job Requisition Agent Tools
    "job-creation": {
        "port": 8051,
        "file": "recruitment_tools_focused/job_requisition_agent/job_creation_mcp.py",
        "agent": "job_requisition_agent"
    },
    "job-workflow": {
        "port": 8052,
        "file": "recruitment_tools_focused/job_requisition_agent/job_workflow_mcp.py", 
        "agent": "job_requisition_agent"
    },
    "job-templates": {
        "port": 8053,
        "file": "recruitment_tools_focused/job_requisition_agent/job_templates_mcp.py",
        "agent": "job_requisition_agent"
    },
    
    # Sourcing Agent Tools
    "social-sourcing": {
        "port": 8061,
        "file": "recruitment_tools_focused/sourcing_agent/social_sourcing_mcp.py",
        "agent": "sourcing_agent"
    },
    "talent-pool": {
        "port": 8062,
        "file": "recruitment_tools_focused/sourcing_agent/talent_pool_mcp.py",
        "agent": "sourcing_agent"
    },
    "outreach": {
        "port": 8063,
        "file": "recruitment_tools_focused/sourcing_agent/outreach_mcp.py",
        "agent": "sourcing_agent"
    },
    
    # Resume Screening Agent Tools
    "document-processing": {
        "port": 8071,
        "file": "recruitment_tools_focused/resume_screening_agent/document_processing_mcp.py",
        "agent": "resume_screening_agent"
    },
    "matching-engine": {
        "port": 8072,
        "file": "recruitment_tools_focused/resume_screening_agent/matching_engine_mcp.py",
        "agent": "resume_screening_agent"
    },
    
    # Communication Agent Tools
    "email-service": {
        "port": 8081,
        "file": "recruitment_tools_focused/communication_agent/email_service_mcp.py",
        "agent": "communication_agent"
    },
    "engagement-tracking": {
        "port": 8082,
        "file": "recruitment_tools_focused/communication_agent/engagement_tracking_mcp.py",
        "agent": "communication_agent"
    },
    
    # Interview Scheduling Agent Tools
    "calendar-integration": {
        "port": 8091,
        "file": "recruitment_tools_focused/interview_scheduling_agent/calendar_integration_mcp.py",
        "agent": "interview_scheduling_agent"
    },
    "interview-workflow": {
        "port": 8092,
        "file": "recruitment_tools_focused/interview_scheduling_agent/interview_workflow_mcp.py",
        "agent": "interview_scheduling_agent"
    },
    "meeting-management": {
        "port": 8093,
        "file": "recruitment_tools_focused/interview_scheduling_agent/meeting_management_mcp.py",
        "agent": "interview_scheduling_agent"
    },
    
    # Assessment Agent Tools
    "test-engine": {
        "port": 8101,
        "file": "recruitment_tools_focused/assessment_agent/test_engine_mcp.py",
        "agent": "assessment_agent"
    },
    "assessment-library": {
        "port": 8102,
        "file": "recruitment_tools_focused/assessment_agent/assessment_library_mcp.py",
        "agent": "assessment_agent"
    },
    "results-analysis": {
        "port": 8103,
        "file": "recruitment_tools_focused/assessment_agent/results_analysis_mcp.py",
        "agent": "assessment_agent"
    },
    
    # Offer Management Agent Tools
    "offer-generation": {
        "port": 8111,
        "file": "recruitment_tools_focused/offer_management_agent/offer_generation_mcp.py",
        "agent": "offer_management_agent"
    },
    "negotiation-management": {
        "port": 8112,
        "file": "recruitment_tools_focused/offer_management_agent/negotiation_management_mcp.py",
        "agent": "offer_management_agent"
    },
    "contract-management": {
        "port": 8113,
        "file": "recruitment_tools_focused/offer_management_agent/contract_management_mcp.py",
        "agent": "offer_management_agent"
    },
    
    # Analytics & Reporting Agent Tools
    "metrics-engine": {
        "port": 8121,
        "file": "recruitment_tools_focused/analytics_reporting_agent/metrics_engine_mcp.py",
        "agent": "analytics_reporting_agent"
    },
    "dashboard-generator": {
        "port": 8122,
        "file": "recruitment_tools_focused/analytics_reporting_agent/dashboard_generator_mcp.py",
        "agent": "analytics_reporting_agent"
    },
    "predictive-analytics": {
        "port": 8123,
        "file": "recruitment_tools_focused/analytics_reporting_agent/predictive_analytics_mcp.py",
        "agent": "analytics_reporting_agent"
    },
    
    # Compliance Agent Tools
    "regulatory-engine": {
        "port": 8131,
        "file": "recruitment_tools_focused/compliance_agent/regulatory_engine_mcp.py",
        "agent": "compliance_agent"
    },
    "data-privacy": {
        "port": 8132,
        "file": "recruitment_tools_focused/compliance_agent/data_privacy_mcp.py",
        "agent": "compliance_agent"
    },
    "audit-management": {
        "port": 8133,
        "file": "recruitment_tools_focused/compliance_agent/audit_management_mcp.py",
        "agent": "compliance_agent"
    },
    
    # Background Verification Agent Tools
    "verification-engine": {
        "port": 8141,
        "file": "recruitment_tools_focused/background_verification_agent/verification_engine_mcp.py",
        "agent": "background_verification_agent"
    },
    "reference-check": {
        "port": 8142,
        "file": "recruitment_tools_focused/background_verification_agent/reference_check_mcp.py",
        "agent": "background_verification_agent"
    },
    "credential-validation": {
        "port": 8143,
        "file": "recruitment_tools_focused/background_verification_agent/credential_validation_mcp.py",
        "agent": "background_verification_agent"
    }
}

# Individual Specialist Agents (for start_agents.sh)
INDIVIDUAL_AGENT_PORTS = {
    "job_requisition_agent": 5020,
    "sourcing_agent": 5021,
    "resume_screening_agent": 5022,
    "communication_agent": 5023,
    "interview_scheduling_agent": 5024,
    "assessment_agent": 5025,
    "background_verification_agent": 5026,
    "offer_management_agent": 5027,
    "analytics_reporting_agent": 5028,
    "compliance_agent": 5029,
    "hr_summarization_agent": 5030,
}

# Team Coordinator Agents (for start_coordinators.sh)
COORDINATOR_AGENT_PORTS = {
    "job_pipeline_team_agent": 5031,
    "acquisition_team_agent": 5032,
    "experience_team_agent": 5033,
    "closing_team_agent": 5034,
    "master_coordinator_agent": 5040
}

# All Agent ports (for backward compatibility)
AGENT_PORTS = {**INDIVIDUAL_AGENT_PORTS, **COORDINATOR_AGENT_PORTS}

def get_tools_for_agent(agent_name):
    """Get all tool names for a specific agent"""
    return [tool_name for tool_name, config in HR_TOOLS.items() if config["agent"] == agent_name]

def get_agent_tools_config(agent_name):
    """Get complete tool configurations for an agent"""
    return {tool_name: config for tool_name, config in HR_TOOLS.items() if config["agent"] == agent_name}

def get_all_agent_names():
    """Get all unique agent names"""
    return list(set(config["agent"] for config in HR_TOOLS.values()))

def get_tools_by_port_range(start_port, end_port):
    """Get tools within a port range"""
    return {name: config for name, config in HR_TOOLS.items() 
            if start_port <= config["port"] <= end_port}

# Agent test configurations
AGENT_TEST_CONFIG = {
    "job_requisition_agent": {
        "test": "Create a Senior Python Developer job posting with $140k-180k salary in San Francisco. Set up approval workflow."
    },
    "sourcing_agent": {
        "test": "Find React developers with 5+ years experience in Seattle. Create talent pool and launch outreach campaign."
    },
    "resume_screening_agent": {
        "test": "Screen resume: John Smith, 6 years Python/Django, Facebook/Google experience, Stanford MS CS. Match against Senior Backend Engineer role."
    },
    "communication_agent": {
        "test": "Send interview invitation to john.doe@example.com for Senior Developer position next Tuesday 2PM. Track engagement."
    },
    "interview_scheduling_agent": {
        "test": "Schedule technical interview for Sarah Wilson with engineering team next week. 2-hour slot with coding and system design."
    },
    "assessment_agent": {
        "test": "Create technical assessment for Senior Python Developer: API development, database queries, system design questions."
    },
    "background_verification_agent": {
        "test": "Verify background for Michael Chen: employment at previous companies, check references, validate MIT CS degree."
    },
    "offer_management_agent": {
        "test": "Generate offer for Senior Software Engineer: $150k salary, equity package, benefits. Handle negotiations and prepare contract."
    },
    "analytics_reporting_agent": {
        "test": "Generate Q4 recruitment analytics: hiring metrics, time-to-fill, source effectiveness, predict Q1 hiring needs."
    },
    "compliance_agent": {
        "test": "Ensure GDPR and EEOC compliance in recruitment process. Audit data handling practices and generate compliance reports."
    },
    "hr_summarization_agent": {
        "test": "Generate recruitment summary for Q4 hiring: 25 positions filled, 150 candidates processed, team performance analysis."
    },
    "job_pipeline_team_agent": {
        "test": "Coordinate job creation workflow for Senior Python Developer position: create posting, ensure compliance, track analytics."
    },
    "acquisition_team_agent": {
        "test": "Coordinate candidate acquisition for React Developer role: source candidates, screen resumes, run background checks."
    },
    "experience_team_agent": {
        "test": "Coordinate candidate experience for 5 finalists: manage communications, schedule interviews, conduct assessments."
    },
    "closing_team_agent": {
        "test": "Coordinate offer process for top candidate: generate offer, handle negotiations, ensure compliance, complete hire."
    },
    "master_coordinator_agent": {
        "test": "Orchestrate full hiring process for Senior Software Engineer: coordinate all teams, manage 15 candidates in pipeline."
    }
}

def get_agent_test_config():
    """Get complete agent configuration for testing"""
    agents = {}
    for agent_name, port in AGENT_PORTS.items():
        tools = get_tools_for_agent(agent_name)
        # Format tools as "tool-name:port" for backward compatibility
        tool_strings = [f"{tool}:{HR_TOOLS[tool]['port']}" for tool in tools]
        
        agents[agent_name] = {
            "port": port,
            "tools": tool_strings,
            "test": AGENT_TEST_CONFIG.get(agent_name, {}).get("test", f"Test {agent_name} functionality")
        }
    return agents