#!/usr/bin/env python3
"""
Interview Scheduling Agent - Interview Workflow MCP Server
Focused on interview process coordination, status tracking, and workflow management
Port: 8092
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

mcp = FastMCP(name="interview-workflow")

# Interview workflow database
interview_workflows_db = {}
interview_rounds_db = {}

@mcp.tool()
def create_interview_process(
    candidate_email: str,
    candidate_name: str,
    job_title: str,
    interview_rounds: str,
    total_duration_days: int = 14
) -> str:
    """
    Create complete interview process workflow for a candidate
    
    Args:
        candidate_email: Candidate's email address
        candidate_name: Candidate's full name
        job_title: Position being interviewed for
        interview_rounds: Comma-separated list of interview types (phone_screen,technical,behavioral,final)
        total_duration_days: Total days to complete all interviews
    """
    
    workflow_id = str(uuid.uuid4())[:8]
    rounds = [r.strip() for r in interview_rounds.split(",")]
    
    # Calculate interview spacing
    days_between_rounds = max(2, total_duration_days // len(rounds))
    
    interview_schedule = []
    current_date = datetime.now() + timedelta(days=2)  # Start in 2 days
    
    for i, round_type in enumerate(rounds):
        interview_schedule.append({
            "round_number": i + 1,
            "type": round_type,
            "status": "scheduled" if i == 0 else "pending",
            "estimated_date": current_date.strftime("%Y-%m-%d"),
            "duration_minutes": get_round_duration(round_type),
            "interviewers_needed": get_interviewer_count(round_type),
            "prerequisites": get_round_prerequisites(round_type)
        })
        current_date += timedelta(days=days_between_rounds)
    
    workflow = {
        "id": workflow_id,
        "candidate": {
            "email": candidate_email,
            "name": candidate_name
        },
        "job_title": job_title,
        "interview_schedule": interview_schedule,
        "overall_status": "in_progress",
        "current_round": 1,
        "total_rounds": len(rounds),
        "created_at": datetime.now().isoformat(),
        "estimated_completion": current_date.strftime("%Y-%m-%d"),
        "workflow_metrics": {
            "total_duration_days": total_duration_days,
            "rounds_completed": 0,
            "success_rate_prediction": random.randint(70, 90)
        }
    }
    
    interview_workflows_db[workflow_id] = workflow
    
    return json.dumps({
        "success": True,
        "workflow_id": workflow_id,
        "message": f"Interview process created for {candidate_name}",
        "workflow": workflow
    }, indent=2)

def get_round_duration(round_type: str) -> int:
    """Get standard duration for interview round type"""
    durations = {
        "phone_screen": 30,
        "technical": 90,
        "behavioral": 60,
        "final": 45,
        "panel": 90,
        "cultural": 45
    }
    return durations.get(round_type, 60)

def get_interviewer_count(round_type: str) -> int:
    """Get number of interviewers needed for round type"""
    counts = {
        "phone_screen": 1,
        "technical": 2,
        "behavioral": 1,
        "final": 3,
        "panel": 4,
        "cultural": 2
    }
    return counts.get(round_type, 1)

def get_round_prerequisites(round_type: str) -> list:
    """Get prerequisites for interview round"""
    prerequisites = {
        "phone_screen": ["resume_reviewed"],
        "technical": ["phone_screen_passed"],
        "behavioral": ["technical_assessment_completed"],
        "final": ["all_previous_rounds_passed"],
        "panel": ["individual_interviews_completed"],
        "cultural": ["technical_evaluation_completed"]
    }
    return prerequisites.get(round_type, [])

@mcp.tool()
def advance_interview_round(
    workflow_id: str,
    current_round_result: str,
    interviewer_feedback: str = "",
    next_round_adjustments: str = "{}"
) -> str:
    """
    Advance candidate to next interview round based on current round results
    
    Args:
        workflow_id: Interview workflow ID
        current_round_result: pass, fail, or conditional
        interviewer_feedback: Feedback from current round
        next_round_adjustments: JSON with any adjustments for next round
    """
    
    if workflow_id not in interview_workflows_db:
        return json.dumps({"success": False, "error": "Interview workflow not found"})
    
    workflow = interview_workflows_db[workflow_id]
    current_round = workflow["current_round"]
    
    try:
        adjustments = json.loads(next_round_adjustments) if next_round_adjustments != "{}" else {}
    except json.JSONDecodeError:
        adjustments = {}
    
    # Update current round status
    if current_round <= len(workflow["interview_schedule"]):
        current_round_info = workflow["interview_schedule"][current_round - 1]
        current_round_info["status"] = "completed"
        current_round_info["result"] = current_round_result
        current_round_info["feedback"] = interviewer_feedback
        current_round_info["completed_at"] = datetime.now().isoformat()
    
    # Update workflow metrics
    workflow["workflow_metrics"]["rounds_completed"] += 1
    
    advancement_result = {
        "workflow_id": workflow_id,
        "previous_round": current_round,
        "round_result": current_round_result,
        "advanced": False,
        "next_round": None,
        "workflow_status": "",
        "timestamp": datetime.now().isoformat()
    }
    
    if current_round_result == "fail":
        workflow["overall_status"] = "rejected"
        workflow["rejection_round"] = current_round
        workflow["completed_at"] = datetime.now().isoformat()
        advancement_result["workflow_status"] = "rejected"
        
    elif current_round_result in ["pass", "conditional"]:
        if current_round < workflow["total_rounds"]:
            # Advance to next round
            workflow["current_round"] += 1
            next_round_info = workflow["interview_schedule"][current_round]
            next_round_info["status"] = "scheduled"
            
            # Apply any adjustments
            for field, value in adjustments.items():
                if field in next_round_info:
                    next_round_info[field] = value
            
            advancement_result["advanced"] = True
            advancement_result["next_round"] = workflow["current_round"]
            advancement_result["workflow_status"] = "in_progress"
            
        else:
            # All rounds completed successfully
            workflow["overall_status"] = "completed"
            workflow["final_result"] = "hire_recommended"
            workflow["completed_at"] = datetime.now().isoformat()
            advancement_result["workflow_status"] = "completed"
    
    return json.dumps({
        "success": True,
        "advancement_result": advancement_result,
        "updated_workflow": workflow
    }, indent=2)

@mcp.tool()
def schedule_interview_round(
    workflow_id: str,
    round_number: int,
    proposed_datetime: str,
    interviewer_emails: str,
    location: str = "Video Call"
) -> str:
    """
    Schedule a specific interview round with interviewers
    
    Args:
        workflow_id: Interview workflow ID
        round_number: Which round to schedule (1, 2, 3, etc.)
        proposed_datetime: Proposed date and time (YYYY-MM-DD HH:MM)
        interviewer_emails: Comma-separated list of interviewer emails
        location: Location or "Video Call"
    """
    
    if workflow_id not in interview_workflows_db:
        return json.dumps({"success": False, "error": "Interview workflow not found"})
    
    workflow = interview_workflows_db[workflow_id]
    
    if round_number < 1 or round_number > len(workflow["interview_schedule"]):
        return json.dumps({"success": False, "error": "Invalid round number"})
    
    interviewers = [email.strip() for email in interviewer_emails.split(",")]
    round_info = workflow["interview_schedule"][round_number - 1]
    
    # Create scheduling details
    scheduling_id = str(uuid.uuid4())[:8]
    
    scheduling_details = {
        "scheduling_id": scheduling_id,
        "workflow_id": workflow_id,
        "round_number": round_number,
        "candidate_email": workflow["candidate"]["email"],
        "datetime": proposed_datetime,
        "duration_minutes": round_info["duration_minutes"],
        "interviewers": interviewers,
        "location": location,
        "meeting_link": f"https://meet.company.com/{scheduling_id}" if location == "Video Call" else "",
        "status": "scheduled",
        "scheduled_at": datetime.now().isoformat()
    }
    
    # Update round info
    round_info["scheduling_details"] = scheduling_details
    round_info["status"] = "scheduled"
    round_info["actual_datetime"] = proposed_datetime
    
    return json.dumps({
        "success": True,
        "scheduling_id": scheduling_id,
        "message": f"Interview round {round_number} scheduled successfully",
        "scheduling_details": scheduling_details
    }, indent=2)

@mcp.tool()
def reschedule_interview_round(
    workflow_id: str,
    round_number: int,
    new_datetime: str,
    reason: str = "Schedule conflict"
) -> str:
    """
    Reschedule an interview round
    
    Args:
        workflow_id: Interview workflow ID
        round_number: Round number to reschedule
        new_datetime: New date and time (YYYY-MM-DD HH:MM)
        reason: Reason for rescheduling
    """
    
    if workflow_id not in interview_workflows_db:
        return json.dumps({"success": False, "error": "Interview workflow not found"})
    
    workflow = interview_workflows_db[workflow_id]
    
    if round_number < 1 or round_number > len(workflow["interview_schedule"]):
        return json.dumps({"success": False, "error": "Invalid round number"})
    
    round_info = workflow["interview_schedule"][round_number - 1]
    
    # Log rescheduling
    if "reschedule_history" not in round_info:
        round_info["reschedule_history"] = []
    
    round_info["reschedule_history"].append({
        "old_datetime": round_info.get("actual_datetime", ""),
        "new_datetime": new_datetime,
        "reason": reason,
        "rescheduled_at": datetime.now().isoformat()
    })
    
    # Update with new time
    round_info["actual_datetime"] = new_datetime
    round_info["status"] = "rescheduled"
    
    return json.dumps({
        "success": True,
        "message": f"Interview round {round_number} rescheduled",
        "new_datetime": new_datetime,
        "reason": reason
    }, indent=2)

@mcp.tool()
def get_interview_workflow_status(workflow_id: str) -> str:
    """
    Get complete status of interview workflow
    
    Args:
        workflow_id: Interview workflow ID to check
    """
    
    if workflow_id not in interview_workflows_db:
        return json.dumps({"success": False, "error": "Interview workflow not found"})
    
    workflow = interview_workflows_db[workflow_id]
    
    # Calculate progress metrics
    completed_rounds = workflow["workflow_metrics"]["rounds_completed"]
    total_rounds = workflow["total_rounds"]
    progress_percentage = (completed_rounds / total_rounds) * 100 if total_rounds > 0 else 0
    
    # Estimate time to completion
    remaining_rounds = total_rounds - completed_rounds
    estimated_days_remaining = remaining_rounds * 3  # Average 3 days per round
    
    status_summary = {
        "workflow_id": workflow_id,
        "candidate_name": workflow["candidate"]["name"],
        "job_title": workflow["job_title"],
        "overall_status": workflow["overall_status"],
        "current_round": workflow["current_round"],
        "progress": {
            "completed_rounds": completed_rounds,
            "total_rounds": total_rounds,
            "percentage": round(progress_percentage, 1),
            "estimated_days_remaining": estimated_days_remaining
        },
        "next_action": get_next_action(workflow),
        "interview_schedule": workflow["interview_schedule"],
        "last_updated": datetime.now().isoformat()
    }
    
    return json.dumps({
        "success": True,
        "workflow_status": status_summary
    }, indent=2)

def get_next_action(workflow: dict) -> str:
    """Determine the next action needed for the workflow"""
    if workflow["overall_status"] == "completed":
        return "Process completed - proceed with offer"
    elif workflow["overall_status"] == "rejected":
        return "Candidate rejected - close process"
    else:
        current_round = workflow["current_round"]
        if current_round <= len(workflow["interview_schedule"]):
            round_info = workflow["interview_schedule"][current_round - 1]
            if round_info["status"] == "scheduled":
                return f"Conduct {round_info['type']} interview"
            else:
                return f"Schedule {round_info['type']} interview"
        return "Unknown next step"

if __name__ == "__main__":
    mcp.run(transport="http", host="0.0.0.0", port=8092)