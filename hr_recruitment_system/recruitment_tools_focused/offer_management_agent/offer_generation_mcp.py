#!/usr/bin/env python3
"""
Offer Management Agent - Offer Generation MCP Server  
Port: 8111
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
from datetime import datetime, timedelta
import random

mcp = FastMCP(name="offer-generation")

@mcp.tool()
def generate_offer(
    candidate_email: str,
    job_title: str,
    base_salary: int,
    bonus_percent: int = 10,
    equity_shares: int = 1000,
    start_date: str = ""
) -> str:
    """Generate job offer for candidate"""
    
    offer_id = str(uuid.uuid4())[:8]
    if not start_date:
        start_date = (datetime.now() + timedelta(weeks=2)).strftime("%Y-%m-%d")
    
    offer = {
        "offer_id": offer_id,
        "candidate_email": candidate_email,
        "position": job_title,
        "compensation": {
            "base_salary": base_salary,
            "bonus_percent": bonus_percent,
            "equity_shares": equity_shares,
            "total_value": base_salary * (1 + bonus_percent/100)
        },
        "start_date": start_date,
        "expires_on": (datetime.now() + timedelta(days=7)).strftime("%Y-%m-%d"),
        "status": "pending",
        "generated_at": datetime.now().isoformat()
    }
    
    return json.dumps({
        "success": True,
        "offer": offer
    }, indent=2)

@mcp.tool()
def track_offer_status(offer_id: str) -> str:
    """Track status of job offer"""
    
    status = random.choice(["pending", "accepted", "declined", "negotiating"])
    
    return json.dumps({
        "success": True,
        "offer_id": offer_id,
        "status": status,
        "last_updated": datetime.now().isoformat()
    }, indent=2)

if __name__ == "__main__":
    mcp.run(transport="http", host="0.0.0.0", port=8111)