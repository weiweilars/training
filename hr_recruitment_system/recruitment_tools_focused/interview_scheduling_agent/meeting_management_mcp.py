#!/usr/bin/env python3
"""
Interview Scheduling Agent - Meeting Management MCP Server
Focused on room booking, equipment setup, reminders, and meeting logistics
Port: 8093
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

mcp = FastMCP(name="meeting-management")

# Meeting resources database
meeting_rooms_db = {
    "conf-room-a": {
        "name": "Conference Room A",
        "capacity": 8,
        "equipment": ["projector", "whiteboard", "video_conference"],
        "location": "Floor 2, Building A"
    },
    "conf-room-b": {
        "name": "Conference Room B", 
        "capacity": 12,
        "equipment": ["projector", "whiteboard", "video_conference", "recording"],
        "location": "Floor 3, Building A"
    },
    "phone-booth-1": {
        "name": "Phone Booth 1",
        "capacity": 2,
        "equipment": ["phone", "monitor"],
        "location": "Floor 2, Building A"
    }
}

meeting_bookings_db = {}
reminder_schedules_db = {}

@mcp.tool()
def book_meeting_room(
    datetime_slot: str,
    duration_minutes: int,
    attendee_count: int,
    required_equipment: str = "",
    meeting_type: str = "interview",
    special_requirements: str = ""
) -> str:
    """
    Book meeting room for interview with required equipment
    
    Args:
        datetime_slot: Date and time (YYYY-MM-DD HH:MM)
        duration_minutes: Meeting duration in minutes
        attendee_count: Number of attendees
        required_equipment: Comma-separated equipment needs (projector,whiteboard,video_conference)
        meeting_type: Type of meeting (interview, panel, assessment)
        special_requirements: Any special setup requirements
    """
    
    equipment_needed = [eq.strip() for eq in required_equipment.split(",") if eq.strip()]
    
    # Find available room that meets requirements
    suitable_rooms = []
    for room_id, room_info in meeting_rooms_db.items():
        if room_info["capacity"] >= attendee_count:
            if not equipment_needed or all(eq in room_info["equipment"] for eq in equipment_needed):
                # Check availability (mock check)
                if is_room_available(room_id, datetime_slot, duration_minutes):
                    suitable_rooms.append((room_id, room_info))
    
    if not suitable_rooms:
        return json.dumps({
            "success": False,
            "error": "No suitable rooms available for the requested time slot",
            "suggestions": get_alternative_suggestions(datetime_slot, attendee_count)
        })
    
    # Book the first suitable room
    room_id, room_info = suitable_rooms[0]
    booking_id = str(uuid.uuid4())[:8]
    
    booking = {
        "booking_id": booking_id,
        "room_id": room_id,
        "room_name": room_info["name"],
        "datetime": datetime_slot,
        "duration_minutes": duration_minutes,
        "attendee_count": attendee_count,
        "meeting_type": meeting_type,
        "equipment_booked": equipment_needed,
        "special_requirements": special_requirements,
        "status": "confirmed",
        "booked_at": datetime.now().isoformat(),
        "setup_notes": generate_setup_notes(equipment_needed, special_requirements)
    }
    
    meeting_bookings_db[booking_id] = booking
    
    return json.dumps({
        "success": True,
        "booking": booking,
        "room_details": room_info,
        "alternative_rooms": [{"id": r[0], "name": r[1]["name"]} for r in suitable_rooms[1:3]]
    }, indent=2)

def is_room_available(room_id: str, datetime_slot: str, duration_minutes: int) -> bool:
    """Check if room is available (mock implementation)"""
    # Mock availability check - 85% chance room is available
    return random.random() > 0.15

def get_alternative_suggestions(datetime_slot: str, attendee_count: int) -> list:
    """Generate alternative time/room suggestions"""
    suggestions = []
    base_time = datetime.strptime(datetime_slot, "%Y-%m-%d %H:%M")
    
    for i in range(3):
        alt_time = base_time + timedelta(hours=i+1)
        suggestions.append({
            "datetime": alt_time.strftime("%Y-%m-%d %H:%M"),
            "available_rooms": list(meeting_rooms_db.keys())[:2]
        })
    
    return suggestions

def generate_setup_notes(equipment: list, special_requirements: str) -> list:
    """Generate setup instructions for the room"""
    notes = []
    
    if "projector" in equipment:
        notes.append("Set up projector and test screen sharing")
    if "video_conference" in equipment:
        notes.append("Test video conference equipment and internet connection")
    if "whiteboard" in equipment:
        notes.append("Ensure whiteboard markers are available")
    if "recording" in equipment:
        notes.append("Set up recording equipment and test audio levels")
    
    if special_requirements:
        notes.append(f"Special setup: {special_requirements}")
    
    notes.append("Ensure room temperature is comfortable")
    notes.append("Provide water and basic refreshments")
    
    return notes

@mcp.tool()
def setup_interview_reminders(
    booking_id: str,
    reminder_schedule: str = "24h,2h,30m",
    attendee_emails: str = "",
    custom_message: str = ""
) -> str:
    """
    Set up automated reminders for interview meeting
    
    Args:
        booking_id: Meeting booking ID
        reminder_schedule: Comma-separated reminder times (24h,2h,30m,15m)
        attendee_emails: Comma-separated list of attendee emails
        custom_message: Custom message to include in reminders
    """
    
    if booking_id not in meeting_bookings_db:
        return json.dumps({"success": False, "error": "Booking not found"})
    
    booking = meeting_bookings_db[booking_id]
    attendees = [email.strip() for email in attendee_emails.split(",") if email.strip()]
    reminder_times = [r.strip() for r in reminder_schedule.split(",")]
    
    reminder_id = str(uuid.uuid4())[:8]
    
    # Calculate actual reminder times
    meeting_time = datetime.strptime(booking["datetime"], "%Y-%m-%d %H:%M")
    scheduled_reminders = []
    
    for reminder_time in reminder_times:
        if reminder_time.endswith('h'):
            hours = int(reminder_time[:-1])
            reminder_datetime = meeting_time - timedelta(hours=hours)
        elif reminder_time.endswith('m'):
            minutes = int(reminder_time[:-1])
            reminder_datetime = meeting_time - timedelta(minutes=minutes)
        else:
            continue
        
        scheduled_reminders.append({
            "reminder_time": reminder_datetime.isoformat(),
            "time_before": reminder_time,
            "status": "scheduled"
        })
    
    reminder_config = {
        "reminder_id": reminder_id,
        "booking_id": booking_id,
        "attendees": attendees,
        "meeting_details": {
            "datetime": booking["datetime"],
            "room_name": booking["room_name"],
            "duration_minutes": booking["duration_minutes"]
        },
        "scheduled_reminders": scheduled_reminders,
        "custom_message": custom_message,
        "created_at": datetime.now().isoformat(),
        "status": "active"
    }
    
    reminder_schedules_db[reminder_id] = reminder_config
    
    return json.dumps({
        "success": True,
        "reminder_id": reminder_id,
        "message": f"Reminders set up for {len(attendees)} attendees",
        "reminder_schedule": reminder_config
    }, indent=2)

@mcp.tool()
def prepare_interview_materials(
    booking_id: str,
    interview_type: str,
    candidate_name: str,
    job_title: str,
    materials_needed: str = "resume,job_description,interview_guide"
) -> str:
    """
    Prepare and organize materials needed for the interview
    
    Args:
        booking_id: Meeting booking ID
        interview_type: Type of interview (technical, behavioral, final, panel)
        candidate_name: Name of candidate being interviewed
        job_title: Position being interviewed for
        materials_needed: Comma-separated list of required materials
    """
    
    if booking_id not in meeting_bookings_db:
        return json.dumps({"success": False, "error": "Booking not found"})
    
    booking = meeting_bookings_db[booking_id]
    materials_list = [m.strip() for m in materials_needed.split(",")]
    
    preparation_id = str(uuid.uuid4())[:8]
    
    # Generate material preparation checklist
    material_checklist = []
    
    for material in materials_list:
        if material == "resume":
            material_checklist.append({
                "item": "Candidate Resume",
                "description": f"Print copies of {candidate_name}'s resume for all interviewers",
                "copies_needed": booking["attendee_count"],
                "status": "pending"
            })
        elif material == "job_description":
            material_checklist.append({
                "item": "Job Description",
                "description": f"Current job posting for {job_title}",
                "copies_needed": booking["attendee_count"],
                "status": "pending"
            })
        elif material == "interview_guide":
            material_checklist.append({
                "item": "Interview Guide",
                "description": f"Structured questions for {interview_type} interview",
                "copies_needed": booking["attendee_count"],
                "status": "pending"
            })
        elif material == "assessment_materials":
            material_checklist.append({
                "item": "Assessment Materials",
                "description": "Technical challenges or assessment sheets",
                "copies_needed": 1,
                "status": "pending"
            })
        elif material == "evaluation_forms":
            material_checklist.append({
                "item": "Evaluation Forms",
                "description": "Interview feedback and scoring forms",
                "copies_needed": booking["attendee_count"],
                "status": "pending"
            })
    
    # Add standard materials
    material_checklist.extend([
        {
            "item": "Name Tags",
            "description": "Name tags for all participants",
            "copies_needed": booking["attendee_count"] + 1,  # Include candidate
            "status": "pending"
        },
        {
            "item": "Water and Refreshments",
            "description": "Basic refreshments for interview participants",
            "copies_needed": 1,
            "status": "pending"
        },
        {
            "item": "Technical Setup",
            "description": "Test all equipment and ensure WiFi access",
            "copies_needed": 1,
            "status": "pending"
        }
    ])
    
    preparation_plan = {
        "preparation_id": preparation_id,
        "booking_id": booking_id,
        "interview_details": {
            "candidate_name": candidate_name,
            "job_title": job_title,
            "interview_type": interview_type,
            "room_name": booking["room_name"],
            "datetime": booking["datetime"]
        },
        "material_checklist": material_checklist,
        "preparation_deadline": (datetime.strptime(booking["datetime"], "%Y-%m-%d %H:%M") - timedelta(hours=2)).isoformat(),
        "responsible_person": "facilities_coordinator",
        "created_at": datetime.now().isoformat(),
        "status": "pending"
    }
    
    return json.dumps({
        "success": True,
        "preparation_id": preparation_id,
        "message": f"Material preparation plan created for {candidate_name}'s interview",
        "checklist_items": len(material_checklist),
        "preparation_plan": preparation_plan
    }, indent=2)

@mcp.tool()
def manage_virtual_meeting(
    booking_id: str,
    platform: str = "zoom",
    meeting_settings: str = "{}"
) -> str:
    """
    Set up and manage virtual meeting for remote interviews
    
    Args:
        booking_id: Meeting booking ID
        platform: Video platform (zoom, teams, meet, webex)
        meeting_settings: JSON with platform-specific settings
    """
    
    if booking_id not in meeting_bookings_db:
        return json.dumps({"success": False, "error": "Booking not found"})
    
    booking = meeting_bookings_db[booking_id]
    
    try:
        settings = json.loads(meeting_settings) if meeting_settings != "{}" else {}
    except json.JSONDecodeError:
        settings = {}
    
    meeting_id = str(uuid.uuid4())[:8]
    
    # Generate virtual meeting details
    virtual_meeting = {
        "meeting_id": meeting_id,
        "booking_id": booking_id,
        "platform": platform,
        "meeting_url": f"https://{platform}.com/j/{meeting_id}",
        "meeting_password": f"HR{random.randint(1000, 9999)}",
        "phone_dial_in": f"+1-555-{random.randint(100, 999)}-{random.randint(1000, 9999)}",
        "meeting_duration": booking["duration_minutes"],
        "scheduled_time": booking["datetime"],
        "host_controls": {
            "recording_enabled": settings.get("recording", True),
            "screen_sharing": settings.get("screen_sharing", True),
            "chat_enabled": settings.get("chat", True),
            "waiting_room": settings.get("waiting_room", True)
        },
        "backup_platform": "phone_conference",
        "technical_support_contact": "tech-support@company.com",
        "created_at": datetime.now().isoformat()
    }
    
    # Update booking with virtual meeting info
    booking["virtual_meeting"] = virtual_meeting
    
    return json.dumps({
        "success": True,
        "virtual_meeting": virtual_meeting,
        "meeting_instructions": generate_virtual_meeting_instructions(virtual_meeting),
        "technical_checklist": [
            "Test video and audio 15 minutes before meeting",
            "Ensure stable internet connection",
            "Have backup phone number ready",
            "Share meeting details with all participants 24 hours prior"
        ]
    }, indent=2)

def generate_virtual_meeting_instructions(meeting_info: dict) -> dict:
    """Generate instructions for virtual meeting participants"""
    return {
        "for_candidate": {
            "join_url": meeting_info["meeting_url"],
            "password": meeting_info["meeting_password"],
            "backup_phone": meeting_info["phone_dial_in"],
            "instructions": [
                "Join 5 minutes early to test audio/video",
                "Ensure you're in a quiet environment",
                "Have your resume and questions ready",
                "Test your internet connection beforehand"
            ]
        },
        "for_interviewers": {
            "host_url": meeting_info["meeting_url"] + "?role=host",
            "admin_password": "admin_" + meeting_info["meeting_password"],
            "controls": [
                "Recording will start automatically",
                "Waiting room is enabled",
                "Screen sharing available for technical demos",
                "Chat function enabled for private notes"
            ]
        }
    }

@mcp.tool()
def cancel_meeting_booking(
    booking_id: str,
    cancellation_reason: str,
    notify_attendees: bool = True
) -> str:
    """
    Cancel meeting booking and handle cleanup
    
    Args:
        booking_id: Meeting booking ID to cancel
        cancellation_reason: Reason for cancellation
        notify_attendees: Whether to send cancellation notifications
    """
    
    if booking_id not in meeting_bookings_db:
        return json.dumps({"success": False, "error": "Booking not found"})
    
    booking = meeting_bookings_db[booking_id]
    booking["status"] = "cancelled"
    booking["cancellation_reason"] = cancellation_reason
    booking["cancelled_at"] = datetime.now().isoformat()
    
    cancellation_tasks = []
    
    if notify_attendees:
        cancellation_tasks.append("Send cancellation notifications to all attendees")
    
    cancellation_tasks.extend([
        f"Release {booking['room_name']} for the time slot",
        "Cancel any equipment reservations",
        "Update calendar invitations",
        "Clean up virtual meeting if applicable"
    ])
    
    # Cancel associated reminders
    related_reminders = [r for r in reminder_schedules_db.values() if r["booking_id"] == booking_id]
    for reminder in related_reminders:
        reminder["status"] = "cancelled"
    
    return json.dumps({
        "success": True,
        "message": f"Meeting booking {booking_id} cancelled successfully",
        "cancellation_reason": cancellation_reason,
        "cleanup_tasks": cancellation_tasks,
        "reminders_cancelled": len(related_reminders)
    }, indent=2)

if __name__ == "__main__":
    mcp.run(transport="http", host="0.0.0.0", port=8093)