#!/usr/bin/env python3
"""
Job Requisition Agent - Job Workflow MCP Server
Focused on approval workflows, status management, and publishing
Port: 8052
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

mcp = FastMCP(name="job-workflow")

# Workflow database
job_workflows_db = {}
approval_history_db = {}

@mcp.tool()
def submit_for_approval(
    draft_id: str,
    approver_email: str,
    priority: str = "normal",
    notes: str = ""
) -> str:
    """
    Submit job posting for approval
    
    Args:
        draft_id: Job draft ID to submit
        approver_email: Email of person who needs to approve
        priority: normal, high, urgent
        notes: Additional notes for approver
    """
    
    workflow_id = str(uuid.uuid4())[:8]
    
    workflow = {
        "id": workflow_id,
        "draft_id": draft_id,
        "status": "pending_approval",
        "approver_email": approver_email,
        "priority": priority,
        "notes": notes,
        "submitted_at": datetime.now().isoformat(),
        "approval_deadline": None
    }
    
    job_workflows_db[workflow_id] = workflow
    
    return json.dumps({
        "success": True,
        "workflow_id": workflow_id,
        "message": f"Job submitted for approval to {approver_email}",
        "workflow": workflow
    }, indent=2)

@mcp.tool()
def approve_job_posting(
    workflow_id: str,
    approved: bool = True,
    comments: str = "",
    approver_name: str = "Manager"
) -> str:
    """
    Approve or reject a job posting
    
    Args:
        workflow_id: Workflow ID to approve/reject
        approved: True to approve, False to reject
        comments: Approval/rejection comments
        approver_name: Name of approver
    """
    
    if workflow_id not in job_workflows_db:
        return json.dumps({"success": False, "error": "Workflow not found"})
    
    workflow = job_workflows_db[workflow_id]
    workflow["status"] = "approved" if approved else "rejected"
    workflow["approved_at"] = datetime.now().isoformat()
    workflow["approver_comments"] = comments
    workflow["approver_name"] = approver_name
    
    # Log approval history
    approval_record = {
        "workflow_id": workflow_id,
        "draft_id": workflow["draft_id"],
        "decision": "approved" if approved else "rejected",
        "approver": approver_name,
        "comments": comments,
        "timestamp": datetime.now().isoformat()
    }
    
    if workflow_id not in approval_history_db:
        approval_history_db[workflow_id] = []
    approval_history_db[workflow_id].append(approval_record)
    
    return json.dumps({
        "success": True,
        "workflow_id": workflow_id,
        "decision": "approved" if approved else "rejected",
        "message": f"Job posting {'approved' if approved else 'rejected'}",
        "approval_record": approval_record
    }, indent=2)

@mcp.tool()
def publish_job_posting(
    workflow_id: str,
    job_boards: str = "internal,linkedin,indeed",
    publish_immediately: bool = True
) -> str:
    """
    Publish approved job posting to job boards
    
    Args:
        workflow_id: Workflow ID (must be approved)
        job_boards: Comma-separated list of job boards
        publish_immediately: Whether to publish now or schedule
    """
    
    if workflow_id not in job_workflows_db:
        return json.dumps({"success": False, "error": "Workflow not found"})
    
    workflow = job_workflows_db[workflow_id]
    if workflow["status"] != "approved":
        return json.dumps({
            "success": False, 
            "error": "Job must be approved before publishing"
        })
    
    boards = [b.strip() for b in job_boards.split(",")]
    
    publication_record = {
        "workflow_id": workflow_id,
        "draft_id": workflow["draft_id"],
        "job_boards": boards,
        "published_at": datetime.now().isoformat() if publish_immediately else None,
        "status": "published" if publish_immediately else "scheduled",
        "posting_urls": {
            board: f"https://{board}.com/jobs/{workflow['draft_id']}" 
            for board in boards
        }
    }
    
    workflow["publication"] = publication_record
    workflow["status"] = "published"
    
    return json.dumps({
        "success": True,
        "message": f"Job posting published to {len(boards)} platforms",
        "publication": publication_record
    }, indent=2)

@mcp.tool()
def get_workflow_status(workflow_id: str) -> str:
    """Get current status of job posting workflow"""
    
    if workflow_id not in job_workflows_db:
        return json.dumps({"success": False, "error": "Workflow not found"})
    
    workflow = job_workflows_db[workflow_id]
    history = approval_history_db.get(workflow_id, [])
    
    return json.dumps({
        "success": True,
        "workflow": workflow,
        "approval_history": history
    }, indent=2)

@mcp.tool()
def list_pending_approvals(approver_email: str = "") -> str:
    """List all job postings pending approval"""
    
    pending = []
    for workflow in job_workflows_db.values():
        if workflow["status"] == "pending_approval":
            if not approver_email or workflow["approver_email"] == approver_email:
                pending.append(workflow)
    
    return json.dumps({
        "success": True,
        "pending_approvals": pending,
        "count": len(pending)
    }, indent=2)

if __name__ == "__main__":
    mcp.run(transport="http", host="0.0.0.0", port=8052)