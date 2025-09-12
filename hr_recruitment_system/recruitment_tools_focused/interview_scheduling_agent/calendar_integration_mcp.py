#!/usr/bin/env python3
"""
Interview Scheduling Agent - Calendar Integration MCP Server
Port: 8091
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

mcp = FastMCP(name="calendar-integration")

@mcp.tool()
def check_availability(
    interviewer_emails: str,
    date_range: str,
    duration_minutes: int = 60
) -> str:
    """Check calendar availability for interviewers"""
    
    interviewers = [email.strip() for email in interviewer_emails.split(",")]
    start_date, end_date = date_range.split(" to ")
    
    # Mock availability slots
    available_slots = []
    current_date = datetime.strptime(start_date, "%Y-%m-%d")
    end_date_obj = datetime.strptime(end_date, "%Y-%m-%d")
    
    while current_date <= end_date_obj:
        for hour in [9, 10, 11, 14, 15, 16]:  # Business hours
            if random.random() > 0.3:  # 70% chance available
                available_slots.append({
                    "date": current_date.strftime("%Y-%m-%d"),
                    "time": f"{hour:02d}:00",
                    "duration_minutes": duration_minutes,
                    "available_interviewers": len(interviewers)
                })
        current_date += timedelta(days=1)
    
    return json.dumps({
        "success": True,
        "available_slots": available_slots[:20],  # Limit to 20 slots
        "total_slots_found": len(available_slots)
    }, indent=2)

@mcp.tool()
def book_interview_slot(
    datetime_slot: str,
    attendee_emails: str,
    interview_type: str = "technical",
    duration_minutes: int = 60
) -> str:
    """Book an interview slot on calendars"""
    
    booking_id = str(uuid.uuid4())[:8]
    attendees = [email.strip() for email in attendee_emails.split(",")]
    
    booking = {
        "booking_id": booking_id,
        "datetime": datetime_slot,
        "attendees": attendees,
        "interview_type": interview_type,
        "duration_minutes": duration_minutes,
        "status": "confirmed",
        "meeting_link": f"https://meet.company.com/{booking_id}",
        "booked_at": datetime.now().isoformat()
    }
    
    return json.dumps({
        "success": True,
        "booking": booking
    }, indent=2)

if __name__ == "__main__":
    mcp.run(transport="http", host="0.0.0.0", port=8091)