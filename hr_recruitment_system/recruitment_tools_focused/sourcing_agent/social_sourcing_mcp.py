#!/usr/bin/env python3
"""
Sourcing Agent - Social Media Sourcing MCP Server
Focused on LinkedIn, GitHub, and social platform candidate discovery
Port: 8061
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

mcp = FastMCP(name="social-sourcing")

# Mock candidate data
mock_profiles = {
    "linkedin": [
        {
            "name": "Sarah Chen",
            "headline": "Senior Software Engineer at TechCorp",
            "location": "San Francisco, CA",
            "skills": ["Python", "React", "AWS", "Kubernetes"],
            "experience_years": 6,
            "profile_url": "https://linkedin.com/in/sarahchen",
            "mutual_connections": 12
        },
        {
            "name": "Mike Rodriguez", 
            "headline": "Full Stack Developer",
            "location": "Austin, TX",
            "skills": ["JavaScript", "Node.js", "MongoDB", "Docker"],
            "experience_years": 4,
            "profile_url": "https://linkedin.com/in/mikerodriguez",
            "mutual_connections": 8
        }
    ],
    "github": [
        {
            "username": "alexdev2024",
            "name": "Alex Johnson",
            "location": "Seattle, WA", 
            "public_repos": 45,
            "followers": 234,
            "primary_language": "Python",
            "languages": ["Python", "Go", "JavaScript", "Rust"],
            "contributions_last_year": 1250,
            "profile_url": "https://github.com/alexdev2024"
        }
    ]
}

@mcp.tool()
def search_linkedin_profiles(
    keywords: str,
    location: str = "",
    experience_level: str = "",
    company: str = "",
    max_results: int = 20
) -> str:
    """
    Search LinkedIn for candidate profiles
    
    Args:
        keywords: Skills, job titles, or keywords to search
        location: Geographic location filter
        experience_level: entry, mid, senior, executive
        company: Current or previous company name
        max_results: Maximum results to return (1-50)
    """
    
    search_id = str(uuid.uuid4())[:8]
    results = []
    
    # Mock search logic
    for profile in mock_profiles["linkedin"]:
        # Simple keyword matching
        keywords_lower = keywords.lower()
        if (keywords_lower in profile["headline"].lower() or 
            any(keywords_lower in skill.lower() for skill in profile["skills"])):
            
            # Location filter
            if location and location.lower() not in profile["location"].lower():
                continue
                
            # Add match score
            profile_copy = profile.copy()
            profile_copy["match_score"] = random.randint(75, 95)
            profile_copy["last_active"] = "2 days ago"
            profile_copy["open_to_work"] = random.choice([True, False])
            results.append(profile_copy)
    
    # Add more mock results
    for i in range(min(max_results - len(results), 8)):
        results.append({
            "name": f"LinkedIn Candidate {i+3}",
            "headline": f"Software Engineer with {keywords}",
            "location": location or "Remote",
            "skills": keywords.split(",")[:3] + ["Git", "Agile"],
            "experience_years": random.randint(2, 8),
            "profile_url": f"https://linkedin.com/in/candidate{i+3}",
            "mutual_connections": random.randint(0, 20),
            "match_score": random.randint(70, 90),
            "last_active": f"{random.randint(1, 14)} days ago",
            "open_to_work": random.choice([True, False])
        })
    
    return json.dumps({
        "success": True,
        "search_id": search_id,
        "platform": "linkedin",
        "search_criteria": {
            "keywords": keywords,
            "location": location,
            "experience_level": experience_level,
            "company": company
        },
        "total_found": len(results),
        "profiles": results[:max_results]
    }, indent=2)

@mcp.tool()
def search_github_developers(
    programming_language: str,
    location: str = "",
    min_repos: int = 5,
    min_followers: int = 10,
    max_results: int = 15
) -> str:
    """
    Search GitHub for developer profiles
    
    Args:
        programming_language: Primary programming language
        location: Geographic location
        min_repos: Minimum public repositories
        min_followers: Minimum follower count
        max_results: Maximum results to return
    """
    
    search_id = str(uuid.uuid4())[:8]
    results = []
    
    # Generate mock GitHub profiles
    for i in range(max_results):
        developer = {
            "username": f"{programming_language.lower()}_dev_{i+1}",
            "name": f"GitHub Developer {i+1}",
            "location": location or random.choice(["San Francisco, CA", "New York, NY", "Berlin, Germany"]),
            "public_repos": random.randint(min_repos, 80),
            "followers": random.randint(min_followers, 500),
            "following": random.randint(10, 200),
            "primary_language": programming_language,
            "languages": [programming_language] + random.sample(["JavaScript", "Python", "Go", "TypeScript", "Java"], 2),
            "contributions_last_year": random.randint(200, 2000),
            "profile_url": f"https://github.com/{programming_language.lower()}_dev_{i+1}",
            "popular_repos": [
                f"{programming_language.lower()}-project-{j+1}" for j in range(3)
            ],
            "bio": f"Passionate {programming_language} developer",
            "hireable": random.choice([True, False, None])
        }
        results.append(developer)
    
    return json.dumps({
        "success": True,
        "search_id": search_id,
        "platform": "github",
        "search_criteria": {
            "programming_language": programming_language,
            "location": location,
            "min_repos": min_repos,
            "min_followers": min_followers
        },
        "total_found": len(results),
        "developers": results
    }, indent=2)

@mcp.tool()
def get_profile_details(profile_url: str) -> str:
    """
    Get detailed information about a specific profile
    
    Args:
        profile_url: Full URL to the profile (LinkedIn or GitHub)
    """
    
    # Determine platform from URL
    platform = "linkedin" if "linkedin.com" in profile_url else "github" if "github.com" in profile_url else "unknown"
    
    if platform == "unknown":
        return json.dumps({
            "success": False,
            "error": "Unsupported profile URL. Supports LinkedIn and GitHub only."
        })
    
    # Mock detailed profile data
    if platform == "linkedin":
        profile_details = {
            "basic_info": {
                "name": "Sarah Chen",
                "headline": "Senior Software Engineer at TechCorp",
                "location": "San Francisco, CA",
                "profile_url": profile_url,
                "profile_image": f"https://linkedin.com/profile-image/{profile_url.split('/')[-1]}"
            },
            "experience": [
                {
                    "title": "Senior Software Engineer",
                    "company": "TechCorp",
                    "duration": "2021 - Present",
                    "description": "Lead development of microservices architecture"
                },
                {
                    "title": "Software Engineer", 
                    "company": "StartupXYZ",
                    "duration": "2019 - 2021",
                    "description": "Full-stack web development"
                }
            ],
            "skills": ["Python", "React", "AWS", "Kubernetes", "Docker", "PostgreSQL"],
            "education": [
                {
                    "degree": "BS Computer Science",
                    "school": "UC Berkeley",
                    "year": "2019"
                }
            ],
            "activity": {
                "recent_posts": 5,
                "last_active": "2 days ago",
                "engagement_rate": "high"
            }
        }
    else:  # GitHub
        profile_details = {
            "basic_info": {
                "username": "alexdev2024",
                "name": "Alex Johnson",
                "location": "Seattle, WA",
                "profile_url": profile_url,
                "bio": "Full-stack developer passionate about open source"
            },
            "stats": {
                "public_repos": 45,
                "followers": 234,
                "following": 150,
                "contributions_last_year": 1250
            },
            "languages": {
                "Python": "40%",
                "JavaScript": "25%", 
                "Go": "20%",
                "TypeScript": "15%"
            },
            "popular_repositories": [
                {
                    "name": "awesome-python-tools",
                    "description": "Collection of useful Python tools",
                    "stars": 123,
                    "forks": 45,
                    "language": "Python"
                },
                {
                    "name": "react-dashboard",
                    "description": "Modern React dashboard template",
                    "stars": 89,
                    "forks": 23,
                    "language": "JavaScript"
                }
            ]
        }
    
    return json.dumps({
        "success": True,
        "platform": platform,
        "profile_details": profile_details,
        "retrieved_at": datetime.now().isoformat()
    }, indent=2)

@mcp.tool()
def boolean_search_advanced(
    platform: str,
    search_query: str,
    filters: str = "{}",
    max_results: int = 25
) -> str:
    """
    Perform advanced Boolean search across platforms
    
    Args:
        platform: linkedin, github, or both
        search_query: Boolean search query (e.g., "(Python OR Django) AND (Senior OR Lead)")
        filters: JSON string with additional filters
        max_results: Maximum results to return
    """
    
    try:
        filter_options = json.loads(filters) if filters != "{}" else {}
    except json.JSONDecodeError:
        filter_options = {}
    
    search_id = str(uuid.uuid4())[:8]
    
    # Mock boolean search parsing
    query_analysis = {
        "original_query": search_query,
        "parsed_terms": {
            "required_terms": ["Python", "Senior"],
            "optional_terms": ["Django", "Lead"],
            "excluded_terms": []
        },
        "complexity": "medium"
    }
    
    # Mock results with higher match scores for Boolean searches
    results = []
    platforms_to_search = [platform] if platform != "both" else ["linkedin", "github"]
    
    for search_platform in platforms_to_search:
        platform_results = random.randint(5, 15)
        for i in range(platform_results):
            result = {
                "platform": search_platform,
                "name": f"Boolean Result {len(results)+1}",
                "match_score": random.randint(80, 98),  # Higher scores for Boolean
                "matching_terms": random.sample(["Python", "Django", "Senior", "Lead"], 2),
                "profile_url": f"https://{search_platform}.com/profile{len(results)+1}",
                "relevance_rank": len(results) + 1
            }
            
            if search_platform == "linkedin":
                result.update({
                    "headline": "Senior Python Developer with Django expertise",
                    "location": random.choice(["San Francisco, CA", "New York, NY", "Austin, TX"])
                })
            else:  # GitHub
                result.update({
                    "username": f"python_expert_{len(results)+1}",
                    "primary_language": "Python",
                    "public_repos": random.randint(20, 100)
                })
            
            results.append(result)
    
    # Sort by match score
    results.sort(key=lambda x: x["match_score"], reverse=True)
    
    return json.dumps({
        "success": True,
        "search_id": search_id,
        "query_analysis": query_analysis,
        "platforms_searched": platforms_to_search,
        "total_results": len(results),
        "results": results[:max_results],
        "search_tips": [
            "Use AND, OR, NOT for complex queries",
            "Use quotes for exact phrases",
            "Use parentheses to group terms",
            "Combine with filters for better targeting"
        ]
    }, indent=2)

if __name__ == "__main__":
    mcp.run(transport="http", host="0.0.0.0", port=8061)