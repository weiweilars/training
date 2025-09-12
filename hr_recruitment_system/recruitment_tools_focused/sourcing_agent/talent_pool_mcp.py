#!/usr/bin/env python3
"""
Sourcing Agent - Talent Pool Management MCP Server
Focused on building, managing, and organizing talent pools
Port: 8062
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
import random

mcp = FastMCP(name="talent-pool")

# Talent pool database
talent_pools_db = {}
pool_candidates_db = {}

@mcp.tool()
def create_talent_pool(
    pool_name: str,
    description: str,
    target_roles: str,
    required_skills: str,
    location_preferences: str = "",
    experience_range: str = "2-8"
) -> str:
    """
    Create a new talent pool for specific roles/skills
    
    Args:
        pool_name: Name for the talent pool
        description: Description of the talent pool purpose
        target_roles: Comma-separated list of target job titles
        required_skills: Comma-separated list of required skills
        location_preferences: Preferred locations (optional)
        experience_range: Experience range like "2-8" years
    """
    
    pool_id = str(uuid.uuid4())[:8]
    
    talent_pool = {
        "id": pool_id,
        "name": pool_name,
        "description": description,
        "criteria": {
            "target_roles": [r.strip() for r in target_roles.split(",")],
            "required_skills": [s.strip() for s in required_skills.split(",")],
            "location_preferences": [l.strip() for l in location_preferences.split(",") if l.strip()],
            "experience_range": experience_range
        },
        "stats": {
            "total_candidates": 0,
            "active_candidates": 0,
            "contacted_candidates": 0
        },
        "created_at": datetime.now().isoformat(),
        "created_by": "sourcing_agent",
        "status": "active"
    }
    
    talent_pools_db[pool_id] = talent_pool
    pool_candidates_db[pool_id] = []
    
    return json.dumps({
        "success": True,
        "pool_id": pool_id,
        "message": f"Talent pool '{pool_name}' created successfully",
        "talent_pool": talent_pool
    }, indent=2)

@mcp.tool()
def add_candidate_to_pool(
    pool_id: str,
    candidate_name: str,
    candidate_email: str,
    candidate_skills: str,
    source: str,
    profile_url: str = "",
    notes: str = ""
) -> str:
    """
    Add a candidate to an existing talent pool
    
    Args:
        pool_id: Target talent pool ID
        candidate_name: Candidate's full name
        candidate_email: Candidate's email address
        candidate_skills: Comma-separated list of skills
        source: Where candidate was found (linkedin, github, referral, etc.)
        profile_url: Link to candidate's profile
        notes: Additional notes about the candidate
    """
    
    if pool_id not in talent_pools_db:
        return json.dumps({
            "success": False,
            "error": "Talent pool not found"
        })
    
    # Check for duplicate email in pool
    existing_candidates = pool_candidates_db[pool_id]
    for candidate in existing_candidates:
        if candidate["email"].lower() == candidate_email.lower():
            return json.dumps({
                "success": False,
                "error": "Candidate already exists in this pool"
            })
    
    candidate_id = str(uuid.uuid4())[:8]
    skills_list = [s.strip() for s in candidate_skills.split(",")]
    
    # Calculate skill match score
    pool_skills = talent_pools_db[pool_id]["criteria"]["required_skills"]
    skill_matches = sum(1 for skill in pool_skills if skill.lower() in [s.lower() for s in skills_list])
    match_score = (skill_matches / len(pool_skills)) * 100 if pool_skills else 0
    
    candidate = {
        "id": candidate_id,
        "name": candidate_name,
        "email": candidate_email.lower(),
        "skills": skills_list,
        "source": source,
        "profile_url": profile_url,
        "notes": notes,
        "match_score": round(match_score, 2),
        "status": "new",  # new, contacted, interested, not_interested
        "added_at": datetime.now().isoformat(),
        "last_contacted": None,
        "response_status": None
    }
    
    pool_candidates_db[pool_id].append(candidate)
    
    # Update pool stats
    talent_pools_db[pool_id]["stats"]["total_candidates"] += 1
    talent_pools_db[pool_id]["stats"]["active_candidates"] += 1
    
    return json.dumps({
        "success": True,
        "candidate_id": candidate_id,
        "message": f"Candidate '{candidate_name}' added to pool '{talent_pools_db[pool_id]['name']}'",
        "match_score": match_score,
        "candidate": candidate
    }, indent=2)

@mcp.tool()
def search_talent_pools(
    skills: str = "",
    roles: str = "",
    location: str = "",
    min_candidates: int = 0
) -> str:
    """
    Search existing talent pools by criteria
    
    Args:
        skills: Skills to match against pool requirements
        roles: Target roles to match
        location: Location preferences
        min_candidates: Minimum number of candidates in pool
    """
    
    matching_pools = []
    search_skills = [s.strip().lower() for s in skills.split(",") if s.strip()]
    search_roles = [r.strip().lower() for r in roles.split(",") if r.strip()]
    
    for pool in talent_pools_db.values():
        if pool["stats"]["total_candidates"] < min_candidates:
            continue
        
        match_score = 0
        total_criteria = 0
        
        # Check skill matches
        if search_skills:
            pool_skills = [s.lower() for s in pool["criteria"]["required_skills"]]
            skill_matches = sum(1 for skill in search_skills if skill in pool_skills)
            match_score += (skill_matches / len(search_skills)) * 40
            total_criteria += 40
        
        # Check role matches  
        if search_roles:
            pool_roles = [r.lower() for r in pool["criteria"]["target_roles"]]
            role_matches = sum(1 for role in search_roles 
                             if any(role in pool_role for pool_role in pool_roles))
            match_score += (role_matches / len(search_roles)) * 40
            total_criteria += 40
        
        # Check location
        if location:
            pool_locations = [l.lower() for l in pool["criteria"]["location_preferences"]]
            location_match = any(location.lower() in loc for loc in pool_locations)
            match_score += 20 if location_match else 0
            total_criteria += 20
        
        if total_criteria > 0:
            final_score = (match_score / total_criteria) * 100
            if final_score > 50:  # Only include pools with >50% match
                pool_copy = pool.copy()
                pool_copy["match_score"] = round(final_score, 2)
                matching_pools.append(pool_copy)
    
    # Sort by match score
    matching_pools.sort(key=lambda x: x["match_score"], reverse=True)
    
    return json.dumps({
        "success": True,
        "search_criteria": {
            "skills": skills,
            "roles": roles,
            "location": location,
            "min_candidates": min_candidates
        },
        "matching_pools": matching_pools,
        "total_found": len(matching_pools)
    }, indent=2)

@mcp.tool()
def get_pool_candidates(
    pool_id: str,
    status_filter: str = "all",
    min_match_score: int = 0,
    sort_by: str = "match_score",
    limit: int = 20
) -> str:
    """
    Get candidates from a talent pool with filtering options
    
    Args:
        pool_id: Talent pool ID
        status_filter: Filter by status (all, new, contacted, interested, not_interested)
        min_match_score: Minimum match score (0-100)
        sort_by: Sort field (match_score, added_at, name)
        limit: Maximum candidates to return
    """
    
    if pool_id not in talent_pools_db:
        return json.dumps({
            "success": False,
            "error": "Talent pool not found"
        })
    
    candidates = pool_candidates_db[pool_id]
    pool_info = talent_pools_db[pool_id]
    
    # Apply filters
    filtered_candidates = []
    for candidate in candidates:
        if status_filter != "all" and candidate["status"] != status_filter:
            continue
        if candidate["match_score"] < min_match_score:
            continue
        filtered_candidates.append(candidate)
    
    # Sort candidates
    if sort_by == "match_score":
        filtered_candidates.sort(key=lambda x: x["match_score"], reverse=True)
    elif sort_by == "added_at":
        filtered_candidates.sort(key=lambda x: x["added_at"], reverse=True)
    elif sort_by == "name":
        filtered_candidates.sort(key=lambda x: x["name"])
    
    return json.dumps({
        "success": True,
        "pool_info": {
            "id": pool_id,
            "name": pool_info["name"],
            "total_candidates": pool_info["stats"]["total_candidates"]
        },
        "filters_applied": {
            "status": status_filter,
            "min_match_score": min_match_score,
            "sort_by": sort_by
        },
        "candidates_found": len(filtered_candidates),
        "candidates": filtered_candidates[:limit]
    }, indent=2)

@mcp.tool()
def update_candidate_status(
    pool_id: str,
    candidate_email: str,
    new_status: str,
    notes: str = ""
) -> str:
    """
    Update a candidate's status within a talent pool
    
    Args:
        pool_id: Talent pool ID
        candidate_email: Candidate's email address
        new_status: new, contacted, interested, not_interested, hired
        notes: Additional notes about the status change
    """
    
    if pool_id not in talent_pools_db:
        return json.dumps({
            "success": False,
            "error": "Talent pool not found"
        })
    
    candidates = pool_candidates_db[pool_id]
    candidate_found = None
    
    for candidate in candidates:
        if candidate["email"] == candidate_email.lower():
            candidate_found = candidate
            break
    
    if not candidate_found:
        return json.dumps({
            "success": False,
            "error": "Candidate not found in this pool"
        })
    
    old_status = candidate_found["status"]
    candidate_found["status"] = new_status
    candidate_found["status_updated_at"] = datetime.now().isoformat()
    
    if notes:
        if "status_notes" not in candidate_found:
            candidate_found["status_notes"] = []
        candidate_found["status_notes"].append({
            "timestamp": datetime.now().isoformat(),
            "status": new_status,
            "notes": notes
        })
    
    # Update pool stats
    if new_status == "contacted" and old_status != "contacted":
        talent_pools_db[pool_id]["stats"]["contacted_candidates"] += 1
    
    return json.dumps({
        "success": True,
        "message": f"Status updated from '{old_status}' to '{new_status}'",
        "candidate_email": candidate_email,
        "status_change": {
            "from": old_status,
            "to": new_status,
            "timestamp": candidate_found["status_updated_at"],
            "notes": notes
        }
    }, indent=2)

if __name__ == "__main__":
    mcp.run(transport="http", host="0.0.0.0", port=8062)