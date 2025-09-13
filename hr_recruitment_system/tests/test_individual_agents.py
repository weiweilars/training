#!/usr/bin/env python3
"""
HR Individual Agents Test Suite
Test individual specialist agents (ports 5020-5030) with their MCP tools
This is Level 2 testing - individual agent functionality
"""

import asyncio
import aiohttp
import json
import time
import uuid
from datetime import datetime
from typing import Dict, List, Any
import sys

class IndividualAgentsTestSuite:
    """Test suite for individual HR specialist agents"""

    def __init__(self, timeout=60, retry_failed=True):
        self.base_url = "http://localhost"
        self.timeout = timeout
        self.retry_failed = retry_failed
        self.agents = {
            # Individual Specialist Agents (ports 5020-5030)
            "job_requisition_agent": {
                "name": "Job Requisition Agent",
                "port": 5020,
                "expected_tools": ["job-creation", "job-workflow", "job-templates"],
                "test_scenarios": [
                    {
                        "name": "Create Senior Software Engineer Position",
                        "message": "Create a job posting for a Senior Software Engineer requiring 5+ years Python experience, AWS knowledge, and microservices architecture. Location: San Francisco, CA. Salary: $140k-$180k."
                    },
                    {
                        "name": "Generate Job Template",
                        "message": "Create a reusable job template for Data Science positions including required skills, preferred qualifications, and standard responsibilities."
                    }
                ]
            },
            "sourcing_agent": {
                "name": "Sourcing Agent",
                "port": 5021,
                "expected_tools": ["social-sourcing", "talent-pool", "outreach"],
                "test_scenarios": [
                    {
                        "name": "Source Python Developers",
                        "message": "Find Python developers with Django experience in the San Francisco Bay Area. Focus on candidates with 3-5 years experience."
                    },
                    {
                        "name": "Outreach Campaign",
                        "message": "Create an outreach campaign for reaching passive candidates interested in remote DevOps positions."
                    }
                ]
            },
            "resume_screening_agent": {
                "name": "Resume Screening Agent",
                "port": 5022,
                "expected_tools": ["document-processing", "matching-engine"],
                "test_scenarios": [
                    {
                        "name": "Screen Software Engineer Resume",
                        "message": "Screen this resume for a Senior Software Engineer position: 'John Smith - 6 years Python/Django, AWS, Docker, Kubernetes, microservices architecture, startup experience.'"
                    },
                    {
                        "name": "Batch Resume Analysis",
                        "message": "Analyze and rank 5 candidates for a Data Scientist role requiring Python, ML, and SQL skills."
                    }
                ]
            },
            "communication_agent": {
                "name": "Communication Agent",
                "port": 5023,
                "expected_tools": ["email-service", "engagement-tracking"],
                "test_scenarios": [
                    {
                        "name": "Send Interview Invitation",
                        "message": "Send an interview invitation email to john.doe@example.com for a Senior Developer position scheduled for next Tuesday at 2 PM PST."
                    },
                    {
                        "name": "Follow-up Campaign",
                        "message": "Create a follow-up email sequence for candidates who haven't responded to initial outreach in 1 week."
                    }
                ]
            },
            "interview_scheduling_agent": {
                "name": "Interview Scheduling Agent",
                "port": 5024,
                "expected_tools": ["calendar-integration", "interview-workflow", "meeting-management"],
                "test_scenarios": [
                    {
                        "name": "Schedule Technical Interview",
                        "message": "Schedule a technical interview for candidate Sarah Johnson with engineers Mike and Alice for next week. Candidate prefers afternoon slots."
                    },
                    {
                        "name": "Reschedule Interview",
                        "message": "Reschedule the interview for candidate ID 12345 due to interviewer conflict. Find alternative slots this week."
                    }
                ]
            },
            "assessment_agent": {
                "name": "Assessment Agent",
                "port": 5025,
                "expected_tools": ["test-engine", "assessment-library", "results-analysis"],
                "test_scenarios": [
                    {
                        "name": "Create Python Assessment",
                        "message": "Create a Python coding assessment for a mid-level developer position including algorithms, data structures, and Django framework questions."
                    },
                    {
                        "name": "Analyze Assessment Results",
                        "message": "Analyze assessment results for candidate with scores: Python 85%, Algorithms 75%, System Design 90%. Provide recommendation."
                    }
                ]
            },
            "background_verification_agent": {
                "name": "Background Verification Agent",
                "port": 5026,
                "expected_tools": ["verification-engine", "reference-check", "credential-validation"],
                "test_scenarios": [
                    {
                        "name": "Verify Employment History",
                        "message": "Verify employment history for candidate claiming 3 years at Google as Senior Software Engineer and 2 years at startup as Tech Lead."
                    },
                    {
                        "name": "Education Verification",
                        "message": "Verify Computer Science degree from Stanford University for candidate applying for Principal Engineer role."
                    }
                ]
            },
            "offer_management_agent": {
                "name": "Offer Management Agent",
                "port": 5027,
                "expected_tools": ["offer-generation", "negotiation-management", "contract-management"],
                "test_scenarios": [
                    {
                        "name": "Generate Offer Package",
                        "message": "Generate offer for Senior Software Engineer: $160k base, $20k bonus, equity, standard benefits, start date in 2 weeks."
                    },
                    {
                        "name": "Handle Counter-Offer",
                        "message": "Candidate countered with $175k base salary request. Analyze and provide negotiation recommendations within approved budget range."
                    }
                ]
            },
            "analytics_reporting_agent": {
                "name": "Analytics Reporting Agent",
                "port": 5028,
                "expected_tools": ["metrics-engine", "dashboard-generator", "predictive-analytics"],
                "test_scenarios": [
                    {
                        "name": "Generate Hiring Metrics",
                        "message": "Generate hiring metrics report for Q4 2024 including time-to-hire, source effectiveness, and conversion rates by role."
                    },
                    {
                        "name": "Predict Hiring Needs",
                        "message": "Analyze trends and predict hiring needs for engineering team in Q1 2025 based on historical data and growth projections."
                    }
                ]
            },
            "compliance_agent": {
                "name": "Compliance Agent",
                "port": 5029,
                "expected_tools": ["regulatory-engine", "data-privacy", "audit-management"],
                "test_scenarios": [
                    {
                        "name": "GDPR Compliance Check",
                        "message": "Review our candidate data handling process for GDPR compliance, particularly regarding data retention and consent management."
                    },
                    {
                        "name": "Equal Opportunity Audit",
                        "message": "Conduct equal opportunity audit of our hiring process for the past 6 months, analyze demographics and identify potential bias."
                    }
                ]
            },
            "hr_summarization_agent": {
                "name": "HR Summarization Agent",
                "port": 5030,
                "expected_tools": [],  # Uses general MCP tools
                "test_scenarios": [
                    {
                        "name": "Summarize Interview Feedback",
                        "message": "Summarize interview feedback from 4 interviewers for candidate applying to Senior Developer role. Include technical skills, cultural fit, and recommendation."
                    },
                    {
                        "name": "Weekly Hiring Summary",
                        "message": "Create a weekly summary of hiring activities: 15 applications received, 8 phone screens, 3 technical interviews, 1 offer extended."
                    }
                ]
            }
        }

        self.results = {}

    async def test_agent_health(self, session: aiohttp.ClientSession, agent_name: str, port: int):
        """Test if agent is running and responding"""
        try:
            url = f"{self.base_url}:{port}/.well-known/agent-card.json"
            async with session.get(url, timeout=aiohttp.ClientTimeout(total=5)) as response:
                if response.status == 200:
                    agent_card = await response.json()
                    return True, agent_card
                else:
                    return False, f"HTTP {response.status}"
        except Exception as e:
            return False, f"Connection error: {str(e)}"

    async def test_agent_conversation(self, session: aiohttp.ClientSession, agent_name: str, port: int, message: str):
        """Test agent conversation capability using SK server JSON-RPC 2.0 API"""
        try:
            url = f"{self.base_url}:{port}"

            # Create JSON-RPC 2.0 payload for SK server
            session_id = f"test-{agent_name.lower().replace('_', '-')}-{int(time.time())}"
            request_id = f"req-{int(time.time())}"

            payload = {
                "jsonrpc": "2.0",
                "method": "message/send",
                "params": {
                    "message": {"content": message},
                    "sessionId": session_id
                },
                "id": request_id
            }

            async with session.post(url, json=payload, timeout=aiohttp.ClientTimeout(total=self.timeout)) as response:
                if response.status == 200:
                    result = await response.json()
                    # Extract actual response from nested JSON-RPC structure
                    if 'result' in result and 'result' in result['result']:
                        actual_response = result['result']['result']
                        if isinstance(actual_response, dict) and 'message' in actual_response:
                            response_content = actual_response['message'].get('content', 'No content')
                            return True, {"response": response_content, "full_result": result}
                        else:
                            return True, {"response": str(actual_response), "full_result": result}
                    else:
                        return True, {"response": "Response received", "full_result": result}
                else:
                    error_text = await response.text()
                    return False, f"HTTP {response.status}: {error_text[:200]}"

        except asyncio.TimeoutError:
            return False, f"Timeout after {self.timeout} seconds - agent may be processing complex request"
        except Exception as e:
            return False, f"Conversation error: {str(e)}"

    async def test_single_agent(self, session: aiohttp.ClientSession, agent_name: str, config: Dict[str, Any]):
        """Test a single individual agent"""
        port = config['port']
        print(f"\n🤖 Testing {config['name']} (port {port})")
        print("-" * 50)

        agent_results = {
            "health_check": None,
            "scenarios": []
        }

        # Test 1: Health Check
        print(f"  📡 Health check...", end=" ")
        health_success, health_result = await self.test_agent_health(session, agent_name, port)

        if health_success:
            print("✅ ONLINE")
            agent_card = health_result
            print(f"     Agent: {agent_card.get('name', 'Unknown')}")
            print(f"     Version: {agent_card.get('version', 'Unknown')}")

            agent_results["health_check"] = "PASS"

            # Test 2: Conversation Scenarios
            for i, scenario in enumerate(config['test_scenarios'], 1):
                scenario_name = scenario['name']
                message = scenario['message']

                print(f"  🎯 Scenario {i}: {scenario_name}...")
                print(f"     Message: {message[:100]}{'...' if len(message) > 100 else ''}")

                conv_success, conv_result = await self.test_agent_conversation(
                    session, agent_name, port, message
                )

                if conv_success:
                    response_text = conv_result.get('response', 'No response content')[:150]
                    print(f"     ✅ PASS - {response_text}{'...' if len(response_text) >= 150 else ''}")
                    agent_results["scenarios"].append({
                        "name": scenario_name,
                        "status": "PASS",
                        "message": message,
                        "response": conv_result.get('response', '')
                    })
                else:
                    print(f"     ❌ FAIL - {conv_result}")
                    agent_results["scenarios"].append({
                        "name": scenario_name,
                        "status": "FAIL",
                        "error": conv_result,
                        "message": message
                    })

                # Add delay between scenarios to prevent overload
                await asyncio.sleep(2)

        else:
            print(f"❌ OFFLINE - {health_result}")
            agent_results["health_check"] = f"FAIL - {health_result}"

        self.results[agent_name] = agent_results

    async def run_all_tests(self, target_agents=None):
        """Run tests for all individual agents or specific ones"""
        print(f"\n🧪 HR Individual Agents Test Suite - Level 2 Testing")
        print(f"=" * 70)

        agents_to_test = target_agents or list(self.agents.keys())
        print(f"Testing {len(agents_to_test)} individual specialist agents")
        print(f"Started at: {datetime.now()}")
        print(f"=" * 70)

        async with aiohttp.ClientSession() as session:
            tasks = []
            for agent_name in agents_to_test:
                if agent_name in self.agents:
                    config = self.agents[agent_name]
                    tasks.append(self.test_single_agent(session, agent_name, config))

            await asyncio.gather(*tasks)

        # Generate final report
        return await self.generate_report()

    async def generate_report(self):
        """Generate comprehensive test report"""
        print(f"\n" + "=" * 70)
        print(f"🏁 Individual Agents Test Results")
        print(f"=" * 70)

        online_agents = 0
        offline_agents = 0
        total_scenarios = 0
        passed_scenarios = 0

        for agent_name, results in self.results.items():
            config = self.agents.get(agent_name, {})
            agent_display_name = config.get('name', agent_name)

            if results["health_check"] == "PASS":
                online_agents += 1
                print(f"✅ {agent_display_name}")

                for scenario in results["scenarios"]:
                    total_scenarios += 1
                    if scenario["status"] == "PASS":
                        passed_scenarios += 1
                        print(f"   ✅ {scenario['name']}")
                    else:
                        print(f"   ❌ {scenario['name']}: {scenario.get('error', 'Unknown error')}")
            else:
                offline_agents += 1
                print(f"❌ {agent_display_name}: {results['health_check']}")

        print(f"\n📊 Summary:")
        print(f"   Agents Online: {online_agents}")
        print(f"   Agents Offline: {offline_agents}")
        if total_scenarios > 0:
            success_rate = (passed_scenarios / total_scenarios) * 100
            print(f"   Scenarios Passed: {passed_scenarios}/{total_scenarios} ({success_rate:.1f}%)")

        return online_agents, offline_agents, passed_scenarios, total_scenarios

def main():
    """Main testing function"""
    import argparse

    parser = argparse.ArgumentParser(description="Test HR Individual Specialist Agents")
    parser.add_argument("--agent", help="Test specific agent only")
    parser.add_argument("--list", action="store_true", help="List available agents")
    parser.add_argument("--timeout", type=int, default=60, help="Timeout in seconds for each request (default: 60)")
    parser.add_argument("--fast", action="store_true", help="Fast mode: shorter timeouts for quick testing")
    parser.add_argument("--no-retry", action="store_true", help="Disable retry on failures")

    args = parser.parse_args()

    # Set timeout based on mode
    timeout = 15 if args.fast else args.timeout
    retry_failed = not args.no_retry

    tester = IndividualAgentsTestSuite(timeout=timeout, retry_failed=retry_failed)

    if args.list:
        print("Available individual agents:")
        for agent_name, config in tester.agents.items():
            print(f"  {agent_name}: {config['name']} (port {config['port']})")
        return

    target_agents = [args.agent] if args.agent else None

    if args.agent and args.agent not in tester.agents:
        print(f"Unknown agent: {args.agent}")
        print(f"Available agents: {', '.join(tester.agents.keys())}")
        sys.exit(1)

    try:
        online, offline, passed, total = asyncio.run(tester.run_all_tests(target_agents))
        # Exit with error if any agents offline or scenarios failed
        sys.exit(0 if offline == 0 and (total == 0 or passed == total) else 1)
    except KeyboardInterrupt:
        print("\n🛑 Testing interrupted by user")
        sys.exit(1)

if __name__ == "__main__":
    main()