#!/usr/bin/env python3
"""
Job Requisition Agent - Job Creation MCP Server
Focused on creating, editing, and managing job posting content
Port: 8051
"""

try:
    from fastmcp import FastMCP
    MCP_AVAILABLE = True
except ImportError:
    MCP_AVAILABLE = False
    class FastMCP:
        def __init__(self, name):
            self.name = name
        def tool(self):
            def decorator(func):
                return func
            return decorator
        def run(self, **kwargs):
            print("FastMCP fallback - demo mode")

import json
import uuid
from datetime import datetime
from typing import Dict, List, Optional

mcp = FastMCP(name="job-creation")

# Job drafts database
job_drafts_db = {}

@mcp.tool()
def create_job_draft(
    title: str,
    department: str,
    location: str,
    employment_type: str = "full-time",
    salary_min: int = 50000,
    salary_max: int = 100000
) -> str:
    """
    Create a new job posting draft
    
    Args:
        title: Job title
        department: Department/team name
        location: Job location
        employment_type: full-time, part-time, contract, internship
        salary_min: Minimum salary
        salary_max: Maximum salary
    """
    
    draft_id = str(uuid.uuid4())[:8]
    
    job_draft = {
        "id": draft_id,
        "title": title,
        "department": department,
        "location": location,
        "employment_type": employment_type,
        "salary_range": {"min": salary_min, "max": salary_max},
        "description": "",
        "responsibilities": [],
        "required_skills": [],
        "preferred_skills": [],
        "benefits": [],
        "status": "draft",
        "created_at": datetime.now().isoformat(),
        "updated_at": datetime.now().isoformat()
    }
    
    job_drafts_db[draft_id] = job_draft
    
    return json.dumps({
        "success": True,
        "draft_id": draft_id,
        "message": f"Job draft created for '{title}'",
        "draft": job_draft
    }, indent=2)

@mcp.tool()
def update_job_description(draft_id: str, description: str) -> str:
    """Update job description"""
    
    if draft_id not in job_drafts_db:
        return json.dumps({"success": False, "error": "Draft not found"})
    
    job_drafts_db[draft_id]["description"] = description
    job_drafts_db[draft_id]["updated_at"] = datetime.now().isoformat()
    
    return json.dumps({
        "success": True,
        "message": "Job description updated",
        "draft_id": draft_id
    }, indent=2)

@mcp.tool()
def add_job_responsibilities(draft_id: str, responsibilities: str) -> str:
    """Add responsibilities to job posting"""
    
    if draft_id not in job_drafts_db:
        return json.dumps({"success": False, "error": "Draft not found"})
    
    resp_list = [r.strip() for r in responsibilities.split(",")]
    job_drafts_db[draft_id]["responsibilities"].extend(resp_list)
    job_drafts_db[draft_id]["updated_at"] = datetime.now().isoformat()
    
    return json.dumps({
        "success": True,
        "message": f"Added {len(resp_list)} responsibilities",
        "responsibilities": resp_list
    }, indent=2)

@mcp.tool()
def set_job_requirements(
    draft_id: str, 
    required_skills: str, 
    preferred_skills: str = "",
    experience_level: str = "mid"
) -> str:
    """Set skill requirements for the job"""
    
    if draft_id not in job_drafts_db:
        return json.dumps({"success": False, "error": "Draft not found"})
    
    job_drafts_db[draft_id]["required_skills"] = [s.strip() for s in required_skills.split(",")]
    job_drafts_db[draft_id]["preferred_skills"] = [s.strip() for s in preferred_skills.split(",") if s.strip()]
    job_drafts_db[draft_id]["experience_level"] = experience_level
    job_drafts_db[draft_id]["updated_at"] = datetime.now().isoformat()
    
    return json.dumps({
        "success": True,
        "message": "Job requirements updated",
        "required_skills": job_drafts_db[draft_id]["required_skills"],
        "preferred_skills": job_drafts_db[draft_id]["preferred_skills"]
    }, indent=2)

@mcp.tool()
def get_job_draft(draft_id: str) -> str:
    """Retrieve job draft details"""
    
    if draft_id not in job_drafts_db:
        return json.dumps({"success": False, "error": "Draft not found"})
    
    return json.dumps({
        "success": True,
        "draft": job_drafts_db[draft_id]
    }, indent=2)

if __name__ == "__main__":
    mcp.run(transport="http", host="0.0.0.0", port=8051)