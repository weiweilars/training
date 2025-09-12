#!/usr/bin/env python3
"""
Job Requisition Agent - Job Templates MCP Server
Focused on template management and job posting standardization
Port: 8053
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

mcp = FastMCP(name="job-templates")

# Templates database
job_templates_db = {
    "software-engineer": {
        "id": "software-engineer",
        "name": "Software Engineer",
        "description": "Develop and maintain software applications using modern technologies.",
        "responsibilities": [
            "Design and develop scalable software solutions",
            "Write clean, maintainable code",
            "Participate in code reviews",
            "Collaborate with cross-functional teams"
        ],
        "required_skills": ["Programming", "Problem Solving", "Version Control"],
        "preferred_skills": ["Cloud Platforms", "DevOps", "Agile Methodologies"],
        "employment_type": "full-time",
        "experience_levels": ["entry", "mid", "senior"]
    },
    "product-manager": {
        "id": "product-manager", 
        "name": "Product Manager",
        "description": "Drive product strategy and roadmap development.",
        "responsibilities": [
            "Define product vision and strategy",
            "Gather and analyze user requirements",
            "Coordinate with engineering and design teams",
            "Monitor product metrics and KPIs"
        ],
        "required_skills": ["Product Strategy", "Market Research", "Analytics"],
        "preferred_skills": ["Agile", "SQL", "A/B Testing"],
        "employment_type": "full-time",
        "experience_levels": ["mid", "senior", "executive"]
    }
}

@mcp.tool()
def list_job_templates(category: str = "all") -> str:
    """
    List available job templates
    
    Args:
        category: Filter by category (all, engineering, product, marketing, etc.)
    """
    
    templates = list(job_templates_db.values())
    
    return json.dumps({
        "success": True,
        "total_templates": len(templates),
        "templates": templates
    }, indent=2)

@mcp.tool()
def get_job_template(template_id: str) -> str:
    """
    Get detailed job template
    
    Args:
        template_id: Template identifier (e.g., 'software-engineer')
    """
    
    if template_id not in job_templates_db:
        available = list(job_templates_db.keys())
        return json.dumps({
            "success": False,
            "error": f"Template not found. Available: {available}"
        })
    
    template = job_templates_db[template_id]
    
    return json.dumps({
        "success": True,
        "template": template
    }, indent=2)

@mcp.tool()
def create_job_from_template(
    template_id: str,
    title: str,
    department: str,
    location: str,
    experience_level: str = "mid",
    customizations: str = "{}"
) -> str:
    """
    Create a job posting from template
    
    Args:
        template_id: Template to use as base
        title: Specific job title
        department: Department/team
        location: Job location
        experience_level: entry, mid, senior, executive
        customizations: JSON string with field overrides
    """
    
    if template_id not in job_templates_db:
        return json.dumps({
            "success": False,
            "error": f"Template '{template_id}' not found"
        })
    
    template = job_templates_db[template_id].copy()
    
    try:
        custom_fields = json.loads(customizations) if customizations != "{}" else {}
    except json.JSONDecodeError:
        return json.dumps({
            "success": False,
            "error": "Invalid JSON in customizations"
        })
    
    # Create job posting from template
    job_posting = {
        "id": str(uuid.uuid4())[:8],
        "title": title,
        "department": department,
        "location": location,
        "experience_level": experience_level,
        "description": template.get("description", ""),
        "responsibilities": template.get("responsibilities", []).copy(),
        "required_skills": template.get("required_skills", []).copy(),
        "preferred_skills": template.get("preferred_skills", []).copy(),
        "employment_type": template.get("employment_type", "full-time"),
        "template_used": template_id,
        "created_at": datetime.now().isoformat(),
        "status": "draft"
    }
    
    # Apply customizations
    for field, value in custom_fields.items():
        if field in job_posting:
            job_posting[field] = value
    
    return json.dumps({
        "success": True,
        "job_id": job_posting["id"],
        "message": f"Job created from template '{template_id}'",
        "job_posting": job_posting
    }, indent=2)

@mcp.tool()
def create_custom_template(
    template_id: str,
    name: str,
    description: str,
    responsibilities: str,
    required_skills: str,
    preferred_skills: str = "",
    employment_type: str = "full-time"
) -> str:
    """
    Create a new job template
    
    Args:
        template_id: Unique identifier for template
        name: Template name
        description: Job description template
        responsibilities: Comma-separated responsibilities
        required_skills: Comma-separated required skills
        preferred_skills: Comma-separated preferred skills
        employment_type: Default employment type
    """
    
    if template_id in job_templates_db:
        return json.dumps({
            "success": False,
            "error": f"Template '{template_id}' already exists"
        })
    
    template = {
        "id": template_id,
        "name": name,
        "description": description,
        "responsibilities": [r.strip() for r in responsibilities.split(",")],
        "required_skills": [s.strip() for s in required_skills.split(",")],
        "preferred_skills": [s.strip() for s in preferred_skills.split(",") if s.strip()],
        "employment_type": employment_type,
        "experience_levels": ["entry", "mid", "senior"],
        "created_at": datetime.now().isoformat(),
        "custom": True
    }
    
    job_templates_db[template_id] = template
    
    return json.dumps({
        "success": True,
        "template_id": template_id,
        "message": f"Custom template '{name}' created",
        "template": template
    }, indent=2)

@mcp.tool()
def update_template(
    template_id: str,
    field: str,
    value: str
) -> str:
    """
    Update a field in existing template
    
    Args:
        template_id: Template to update
        field: Field name to update
        value: New value (comma-separated for lists)
    """
    
    if template_id not in job_templates_db:
        return json.dumps({
            "success": False,
            "error": f"Template '{template_id}' not found"
        })
    
    template = job_templates_db[template_id]
    
    # Handle list fields
    if field in ["responsibilities", "required_skills", "preferred_skills"]:
        template[field] = [item.strip() for item in value.split(",")]
    else:
        template[field] = value
    
    template["updated_at"] = datetime.now().isoformat()
    
    return json.dumps({
        "success": True,
        "message": f"Template '{template_id}' updated",
        "field": field,
        "new_value": template[field]
    }, indent=2)

if __name__ == "__main__":
    mcp.run(transport="http", host="0.0.0.0", port=8053)