#!/usr/bin/env python3
"""
Resume Screening Agent - Matching Engine MCP Server  
Focused on skills matching, scoring, and candidate ranking
Port: 8072
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

mcp = FastMCP(name="matching-engine")

@mcp.tool()
def calculate_skills_match(
    candidate_skills: str,
    required_skills: str,
    preferred_skills: str = "",
    skill_weights: str = '{"required": 0.7, "preferred": 0.3}'
) -> str:
    """Calculate skills matching score"""
    
    try:
        weights = json.loads(skill_weights)
    except:
        weights = {"required": 0.7, "preferred": 0.3}
    
    candidate_list = [s.strip().lower() for s in candidate_skills.split(",")]
    required_list = [s.strip().lower() for s in required_skills.split(",")]
    preferred_list = [s.strip().lower() for s in preferred_skills.split(",") if s.strip()]
    
    required_matches = [skill for skill in required_list if skill in candidate_list]
    preferred_matches = [skill for skill in preferred_list if skill in candidate_list]
    
    required_score = len(required_matches) / len(required_list) if required_list else 0
    preferred_score = len(preferred_matches) / len(preferred_list) if preferred_list else 0
    
    overall_score = (required_score * weights["required"] + preferred_score * weights["preferred"]) * 100
    
    return json.dumps({
        "success": True,
        "skills_matching": {
            "overall_score": round(overall_score, 2),
            "required_skills_score": round(required_score * 100, 2),
            "preferred_skills_score": round(preferred_score * 100, 2),
            "matched_required": required_matches,
            "matched_preferred": preferred_matches,
            "missing_required": [s for s in required_list if s not in candidate_list]
        }
    }, indent=2)

@mcp.tool()
def rank_candidates(candidates_data: str, job_requirements: str) -> str:
    """Rank multiple candidates by fit score"""
    
    try:
        candidates = json.loads(candidates_data)
        requirements = json.loads(job_requirements)
    except json.JSONDecodeError:
        return json.dumps({"success": False, "error": "Invalid JSON input"})
    
    ranked_candidates = []
    
    for candidate in candidates:
        # Calculate overall fit score
        fit_score = random.randint(60, 95)  # Mock calculation
        
        candidate_ranking = {
            **candidate,
            "fit_score": fit_score,
            "ranking_factors": {
                "skills_match": random.randint(70, 100),
                "experience_match": random.randint(60, 95),
                "education_match": random.randint(75, 100),
                "location_preference": random.randint(80, 100)
            }
        }
        ranked_candidates.append(candidate_ranking)
    
    # Sort by fit score
    ranked_candidates.sort(key=lambda x: x["fit_score"], reverse=True)
    
    return json.dumps({
        "success": True,
        "total_candidates": len(ranked_candidates),
        "ranked_candidates": ranked_candidates,
        "top_candidate": ranked_candidates[0] if ranked_candidates else None
    }, indent=2)

if __name__ == "__main__":
    mcp.run(transport="http", host="0.0.0.0", port=8072)