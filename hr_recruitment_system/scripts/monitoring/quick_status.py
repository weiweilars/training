#!/usr/bin/env python3
"""
HR System Quick Status Check
Shows complete status of all components
"""

import requests
import time
from datetime import datetime
import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'tools'))
from hr_tools_config import HR_TOOLS

def check_agent(port, name):
    """Check if agent is online"""
    try:
        response = requests.get(f"http://localhost:{port}/.well-known/agent-card.json", timeout=1)
        if response.status_code == 200:
            return True, "✅ ONLINE"
        else:
            return False, "🟡 RESPONDING"
    except:
        return False, "❌ OFFLINE"

def check_tool(port, name):
    """Check if MCP tool is online"""
    try:
        response = requests.post(
            f"http://localhost:{port}/mcp",
            json={"jsonrpc": "2.0", "method": "tools/list", "params": {}, "id": 1},
            headers={"Accept": "application/json, text/event-stream"},
            timeout=1
        )
        if response.status_code == 200:
            return True, "✅ ONLINE"
        else:
            return False, "🟡 RESPONDING"
    except:
        return False, "❌ OFFLINE"

def main():
    print("=" * 70)
    print("  HR RECRUITMENT SYSTEM - COMPLETE STATUS REPORT")
    print("=" * 70)
    print(f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print()

    # Check MCP Tools
    print("🛠️  MCP TOOLS (28 configured tools)")
    print("-" * 50)

    # Group tools by category based on agent
    tool_categories = {
        "Job Requisition": [],
        "Sourcing": [],
        "Resume Screening": [],
        "Communication": [],
        "Interview Scheduling": [],
        "Assessment": [],
        "Background Verification": [],
        "Offer Management": [],
        "Analytics Reporting": [],
        "Compliance": []
    }

    # Map agent names to category names
    agent_to_category = {
        "job_requisition_agent": "Job Requisition",
        "sourcing_agent": "Sourcing",
        "resume_screening_agent": "Resume Screening",
        "communication_agent": "Communication",
        "interview_scheduling_agent": "Interview Scheduling",
        "assessment_agent": "Assessment",
        "background_verification_agent": "Background Verification",
        "offer_management_agent": "Offer Management",
        "analytics_reporting_agent": "Analytics Reporting",
        "compliance_agent": "Compliance"
    }

    # Group tools by their agent/category
    for tool_name, config in HR_TOOLS.items():
        agent = config.get("agent")
        if agent in agent_to_category:
            category = agent_to_category[agent]
            tool_categories[category].append((tool_name, config["port"]))

    total_tools = len(HR_TOOLS)
    online_tools = 0

    # Check each category
    for category, tools in tool_categories.items():
        if not tools:
            continue

        category_online = 0
        category_total = len(tools)

        for tool_name, port in tools:
            is_online, _ = check_tool(port, tool_name)
            if is_online:
                category_online += 1
                online_tools += 1

        status = "✅" if category_online == category_total else ("🟡" if category_online > 0 else "❌")
        ports_str = f"ports {', '.join(str(p) for _, p in tools)}" if len(tools) <= 3 else f"{len(tools)} tools"
        print(f"  {status} {category}: {category_online}/{category_total} online ({ports_str})")

    print(f"\n📊 Total MCP Tools: {online_tools}/{total_tools} online")

    # Check Individual Agents
    print("\n🤖 INDIVIDUAL AGENTS (Ports 5020-5030)")
    print("-" * 50)

    agents = [
        (5020, "job_requisition_agent"),
        (5021, "sourcing_agent"),
        (5022, "resume_screening_agent"),
        (5023, "communication_agent"),
        (5024, "interview_scheduling_agent"),
        (5025, "assessment_agent"),
        (5026, "background_verification_agent"),
        (5027, "offer_management_agent"),
        (5028, "analytics_reporting_agent"),
        (5029, "compliance_agent"),
        (5030, "hr_summarization_agent")
    ]

    online_agents = 0
    for port, name in agents:
        is_online, status = check_agent(port, name)
        print(f"  {status} Port {port}: {name}")
        if is_online:
            online_agents += 1

    print(f"\n📊 Total Agents: {online_agents}/{len(agents)} online")

    # Check Team Coordinators
    print("\n🎯 TEAM COORDINATORS")
    print("-" * 50)

    coordinators = [
        (5032, "acquisition_team_agent"),
        (5033, "experience_team_agent"),
        (5034, "closing_team_agent"),
        (5040, "master_coordinator_agent")
    ]

    online_coordinators = 0
    for port, name in coordinators:
        is_online, status = check_agent(port, name)
        print(f"  {status} Port {port}: {name}")
        if is_online:
            online_coordinators += 1

    print(f"\n📊 Total Coordinators: {online_coordinators}/{len(coordinators)} online")

    # Overall Summary
    print("\n" + "=" * 70)
    print("📊 SYSTEM SUMMARY")
    print("=" * 70)

    print(f"  MCP Tools:        {online_tools}/{total_tools} online ({(online_tools/total_tools)*100:.1f}%)")
    print(f"  Individual Agents: {online_agents}/{len(agents)} online ({(online_agents/len(agents))*100:.1f}%)")
    print(f"  Team Coordinators: {online_coordinators}/{len(coordinators)} online ({(online_coordinators/len(coordinators))*100:.1f}%)")

    # Calculate overall health
    total_components = total_tools + len(agents) + len(coordinators)
    online_components = online_tools + online_agents + online_coordinators
    health_percentage = (online_components / total_components) * 100

    print(f"\n  Overall System Health: {health_percentage:.1f}%")

    if health_percentage == 100:
        print("\n🎉 SYSTEM STATUS: FULLY OPERATIONAL - ALL COMPONENTS ONLINE!")
    elif health_percentage >= 90:
        print("\n✅ SYSTEM STATUS: OPERATIONAL - MOST COMPONENTS ONLINE")
    elif health_percentage >= 70:
        print("\n🟡 SYSTEM STATUS: PARTIALLY OPERATIONAL")
    else:
        print("\n❌ SYSTEM STATUS: DEGRADED - MANY COMPONENTS OFFLINE")

    print("=" * 70)

if __name__ == "__main__":
    main()