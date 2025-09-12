#!/usr/bin/env python3
"""
Sourcing Agent - Candidate Outreach MCP Server
Focused on candidate contact, outreach campaigns, and response tracking
Port: 8063
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

mcp = FastMCP(name="candidate-outreach")

# Outreach databases
outreach_campaigns_db = {}
outreach_messages_db = {}
response_tracking_db = {}

# Message templates
message_templates = {
    "initial_contact": {
        "subject": "Exciting {role} Opportunity at {company}",
        "body": """Hi {candidate_name},

I hope this message finds you well. I came across your profile and was impressed by your background in {skills}.

We have an exciting {role} opportunity at {company} that I think would be perfect for you. The role involves {key_responsibilities} and offers {benefits}.

Would you be open to a brief conversation to learn more?

Best regards,
{recruiter_name}"""
    },
    "follow_up": {
        "subject": "Re: {role} Opportunity - Following Up",
        "body": """Hi {candidate_name},

I wanted to follow up on my previous message about the {role} position at {company}.

I understand you're likely busy, but I believe this could be a great opportunity for someone with your {skills} background.

If you're interested or have any questions, I'd be happy to schedule a quick 15-minute call.

Best regards,
{recruiter_name}"""
    }
}

@mcp.tool()
def create_outreach_campaign(
    campaign_name: str,
    target_role: str,
    company_name: str,
    message_template: str = "initial_contact",
    candidate_emails: str = "",
    personalization_data: str = "{}"
) -> str:
    """
    Create a new outreach campaign
    
    Args:
        campaign_name: Name for the campaign
        target_role: Role being recruited for
        company_name: Company name
        message_template: Template to use (initial_contact, follow_up)
        candidate_emails: Comma-separated list of candidate emails
        personalization_data: JSON with per-candidate customization
    """
    
    campaign_id = str(uuid.uuid4())[:8]
    
    try:
        personalization = json.loads(personalization_data) if personalization_data != "{}" else {}
    except json.JSONDecodeError:
        personalization = {}
    
    email_list = [email.strip() for email in candidate_emails.split(",") if email.strip()]
    
    campaign = {
        "id": campaign_id,
        "name": campaign_name,
        "target_role": target_role,
        "company_name": company_name,
        "message_template": message_template,
        "candidate_emails": email_list,
        "personalization_data": personalization,
        "status": "draft",  # draft, active, paused, completed
        "created_at": datetime.now().isoformat(),
        "stats": {
            "total_candidates": len(email_list),
            "messages_sent": 0,
            "responses_received": 0,
            "positive_responses": 0
        }
    }
    
    outreach_campaigns_db[campaign_id] = campaign
    
    return json.dumps({
        "success": True,
        "campaign_id": campaign_id,
        "message": f"Outreach campaign '{campaign_name}' created",
        "campaign": campaign
    }, indent=2)

@mcp.tool()
def send_outreach_message(
    candidate_email: str,
    candidate_name: str,
    role: str,
    company: str,
    template_name: str = "initial_contact",
    custom_variables: str = "{}",
    recruiter_name: str = "Jane Recruiter"
) -> str:
    """
    Send individual outreach message to candidate
    
    Args:
        candidate_email: Candidate's email address
        candidate_name: Candidate's full name
        role: Position being recruited for
        company: Company name
        template_name: Message template to use
        custom_variables: JSON with additional template variables
        recruiter_name: Name of recruiter sending message
    """
    
    if template_name not in message_templates:
        available_templates = list(message_templates.keys())
        return json.dumps({
            "success": False,
            "error": f"Template not found. Available: {available_templates}"
        })
    
    try:
        custom_vars = json.loads(custom_variables) if custom_variables != "{}" else {}
    except json.JSONDecodeError:
        custom_vars = {}
    
    message_id = str(uuid.uuid4())[:8]
    template = message_templates[template_name]
    
    # Template variables
    template_vars = {
        "candidate_name": candidate_name,
        "role": role,
        "company": company,
        "recruiter_name": recruiter_name,
        "skills": custom_vars.get("skills", "your expertise"),
        "key_responsibilities": custom_vars.get("responsibilities", "exciting challenges"),
        "benefits": custom_vars.get("benefits", "competitive compensation and growth opportunities"),
        **custom_vars
    }
    
    # Fill template
    subject = template["subject"].format(**template_vars)
    body = template["body"].format(**template_vars)
    
    # Mock message sending
    message_record = {
        "id": message_id,
        "candidate_email": candidate_email,
        "candidate_name": candidate_name,
        "subject": subject,
        "body": body,
        "template_used": template_name,
        "sent_at": datetime.now().isoformat(),
        "delivery_status": "sent",
        "opened": False,
        "clicked": False,
        "replied": False,
        "response_sentiment": None
    }
    
    outreach_messages_db[message_id] = message_record
    
    # Mock delivery tracking (simulate email delivery)
    delivery_probability = 0.95  # 95% delivery rate
    if random.random() < delivery_probability:
        message_record["delivery_status"] = "delivered"
    else:
        message_record["delivery_status"] = "failed"
        message_record["failure_reason"] = random.choice(["invalid_email", "bounced", "blocked"])
    
    return json.dumps({
        "success": True,
        "message_id": message_id,
        "message": f"Outreach message sent to {candidate_name}",
        "delivery_status": message_record["delivery_status"],
        "message_details": {
            "to": candidate_email,
            "subject": subject,
            "template": template_name,
            "sent_at": message_record["sent_at"]
        }
    }, indent=2)

@mcp.tool()
def launch_outreach_campaign(campaign_id: str, delay_between_messages: int = 30) -> str:
    """
    Launch an outreach campaign to send messages to all candidates
    
    Args:
        campaign_id: Campaign to launch
        delay_between_messages: Seconds between messages (to avoid spam)
    """
    
    if campaign_id not in outreach_campaigns_db:
        return json.dumps({
            "success": False,
            "error": "Campaign not found"
        })
    
    campaign = outreach_campaigns_db[campaign_id]
    
    if campaign["status"] != "draft":
        return json.dumps({
            "success": False,
            "error": f"Campaign already {campaign['status']}"
        })
    
    campaign["status"] = "active"
    campaign["launched_at"] = datetime.now().isoformat()
    
    sent_messages = []
    failed_messages = []
    
    for email in campaign["candidate_emails"]:
        # Get personalization data for this candidate
        personalization = campaign["personalization_data"].get(email, {})
        candidate_name = personalization.get("name", "Candidate")
        
        # Send message
        result = json.loads(send_outreach_message(
            candidate_email=email,
            candidate_name=candidate_name,
            role=campaign["target_role"],
            company=campaign["company_name"],
            template_name=campaign["message_template"],
            custom_variables=json.dumps(personalization)
        ))
        
        if result["success"] and result.get("delivery_status") == "delivered":
            sent_messages.append({
                "email": email,
                "message_id": result["message_id"],
                "name": candidate_name
            })
        else:
            failed_messages.append({
                "email": email,
                "error": result.get("error", "Delivery failed")
            })
    
    # Update campaign stats
    campaign["stats"]["messages_sent"] = len(sent_messages)
    campaign["stats"]["delivery_failures"] = len(failed_messages)
    
    return json.dumps({
        "success": True,
        "campaign_id": campaign_id,
        "message": f"Campaign launched: {len(sent_messages)}/{len(campaign['candidate_emails'])} messages sent",
        "launch_results": {
            "successful_sends": len(sent_messages),
            "failed_sends": len(failed_messages),
            "success_rate": round((len(sent_messages) / len(campaign['candidate_emails'])) * 100, 2) if campaign['candidate_emails'] else 0,
            "sent_messages": sent_messages,
            "failed_messages": failed_messages
        }
    }, indent=2)

@mcp.tool()
def track_message_engagement(message_id: str = "", candidate_email: str = "") -> str:
    """
    Track engagement for outreach messages
    
    Args:
        message_id: Specific message ID to track
        candidate_email: Track all messages to specific candidate
    """
    
    if message_id:
        if message_id not in outreach_messages_db:
            return json.dumps({
                "success": False,
                "error": "Message not found"
            })
        
        message = outreach_messages_db[message_id]
        
        # Mock engagement tracking
        if not message.get("engagement_simulated"):
            # Simulate engagement based on realistic rates
            message["opened"] = random.random() < 0.25  # 25% open rate
            if message["opened"]:
                message["clicked"] = random.random() < 0.15  # 15% click rate if opened
                message["replied"] = random.random() < 0.08  # 8% reply rate if opened
                if message["replied"]:
                    message["response_sentiment"] = random.choice(["positive", "neutral", "negative"])
            message["engagement_simulated"] = True
        
        return json.dumps({
            "success": True,
            "message_engagement": {
                "message_id": message_id,
                "candidate_email": message["candidate_email"],
                "sent_at": message["sent_at"],
                "opened": message["opened"],
                "clicked": message.get("clicked", False),
                "replied": message.get("replied", False),
                "response_sentiment": message.get("response_sentiment"),
                "engagement_score": sum([
                    message["opened"],
                    message.get("clicked", False),
                    message.get("replied", False)
                ])
            }
        }, indent=2)
    
    elif candidate_email:
        candidate_messages = [msg for msg in outreach_messages_db.values() 
                            if msg["candidate_email"] == candidate_email]
        
        if not candidate_messages:
            return json.dumps({
                "success": False,
                "error": f"No messages found for {candidate_email}"
            })
        
        # Calculate engagement stats
        total_messages = len(candidate_messages)
        opened_count = sum(1 for msg in candidate_messages if msg.get("opened", False))
        replied_count = sum(1 for msg in candidate_messages if msg.get("replied", False))
        
        return json.dumps({
            "success": True,
            "candidate_engagement": {
                "candidate_email": candidate_email,
                "total_messages": total_messages,
                "messages_opened": opened_count,
                "messages_replied": replied_count,
                "open_rate": round((opened_count / total_messages) * 100, 2) if total_messages > 0 else 0,
                "reply_rate": round((replied_count / total_messages) * 100, 2) if total_messages > 0 else 0,
                "last_message": max(candidate_messages, key=lambda x: x["sent_at"])["sent_at"]
            }
        }, indent=2)
    
    else:
        return json.dumps({
            "success": False,
            "error": "Either message_id or candidate_email must be provided"
        })

@mcp.tool()
def schedule_follow_up_outreach(
    original_message_id: str,
    follow_up_days: int = 7,
    template_name: str = "follow_up",
    custom_notes: str = ""
) -> str:
    """
    Schedule follow-up outreach for non-responsive candidates
    
    Args:
        original_message_id: ID of original message to follow up on
        follow_up_days: Days to wait before follow-up
        template_name: Template for follow-up message
        custom_notes: Additional notes for follow-up
    """
    
    if original_message_id not in outreach_messages_db:
        return json.dumps({
            "success": False,
            "error": "Original message not found"
        })
    
    original_message = outreach_messages_db[original_message_id]
    
    # Check if candidate already replied
    if original_message.get("replied", False):
        return json.dumps({
            "success": False,
            "error": "Candidate already replied to original message"
        })
    
    follow_up_id = str(uuid.uuid4())[:8]
    follow_up_date = (datetime.now() + timedelta(days=follow_up_days)).isoformat()
    
    follow_up_record = {
        "id": follow_up_id,
        "original_message_id": original_message_id,
        "candidate_email": original_message["candidate_email"],
        "candidate_name": original_message["candidate_name"],
        "template_name": template_name,
        "scheduled_for": follow_up_date,
        "custom_notes": custom_notes,
        "status": "scheduled",
        "created_at": datetime.now().isoformat()
    }
    
    # In a real system, this would be stored in a scheduling system
    response_tracking_db[follow_up_id] = follow_up_record
    
    return json.dumps({
        "success": True,
        "follow_up_id": follow_up_id,
        "message": f"Follow-up scheduled for {original_message['candidate_name']}",
        "follow_up_details": follow_up_record
    }, indent=2)

if __name__ == "__main__":
    mcp.run(transport="http", host="0.0.0.0", port=8063)