#!/usr/bin/env python3
"""
HR Team Coordinators Test Suite
Test team coordinator agents (ports 5032-5034) and their A2A communication
This is Level 3 testing - team coordination functionality
"""

import asyncio
import aiohttp
import json
import time
import uuid
from datetime import datetime
from typing import Dict, List, Any
import sys

class TeamCoordinatorsTestSuite:
    """Test suite for HR team coordinator agents"""

    def __init__(self):
        self.base_url = "http://localhost"
        self.coordinators = {
            # Team Coordinator Agents (ports 5032-5034)
            "acquisition_team_agent": {
                "name": "Acquisition Team Agent",
                "port": 5032,
                "sub_agents": [
                    {"name": "sourcing_agent", "port": 5021},
                    {"name": "resume_screening_agent", "port": 5022},
                    {"name": "background_verification_agent", "port": 5026},
                    {"name": "analytics_reporting_agent", "port": 5028}
                ],
                "workflow_type": "parallel",
                "test_scenarios": [
                    {
                        "name": "Full Acquisition Pipeline",
                        "message": "Find and validate 5 Senior Python Developer candidates with 3+ years experience, screen their resumes, and run background checks. Generate acquisition metrics report."
                    },
                    {
                        "name": "Bulk Candidate Processing",
                        "message": "Process 10 Data Scientist applications: source additional similar candidates, screen all resumes for ML/Python skills, prioritize top 3 for verification."
                    }
                ]
            },
            "experience_team_agent": {
                "name": "Experience Team Agent",
                "port": 5033,
                "sub_agents": [
                    {"name": "communication_agent", "port": 5023},
                    {"name": "interview_scheduling_agent", "port": 5024},
                    {"name": "assessment_agent", "port": 5025},
                    {"name": "analytics_reporting_agent", "port": 5028}
                ],
                "workflow_type": "event_driven",
                "test_scenarios": [
                    {
                        "name": "Complete Interview Process",
                        "message": "Schedule technical interviews for 3 candidates (Sarah, Mike, Alex) for Senior Engineer roles. Send confirmation emails, create assessments, and track experience metrics."
                    },
                    {
                        "name": "Candidate Journey Optimization",
                        "message": "Optimize interview experience for remote candidates: schedule video interviews, send preparation materials, conduct assessments, gather feedback."
                    }
                ]
            },
            "closing_team_agent": {
                "name": "Closing Team Agent",
                "port": 5034,
                "sub_agents": [
                    {"name": "offer_management_agent", "port": 5027},
                    {"name": "compliance_agent", "port": 5029},
                    {"name": "analytics_reporting_agent", "port": 5028}
                ],
                "workflow_type": "sequential",
                "test_scenarios": [
                    {
                        "name": "Complete Offer Process",
                        "message": "Generate offer for selected candidate John Smith: $165k base, $25k bonus, equity package. Ensure compliance, handle negotiation, track closing metrics."
                    },
                    {
                        "name": "Multiple Offers Management",
                        "message": "Manage 3 simultaneous offers for different roles: Senior Engineer ($160k), Data Scientist ($145k), DevOps Lead ($155k). Handle compliance and negotiations."
                    }
                ]
            }
        }

        self.results = {}

    async def test_coordinator_health(self, session: aiohttp.ClientSession, coordinator_name: str, port: int):
        """Test if coordinator is running and responding"""
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

    async def test_sub_agents_connectivity(self, session: aiohttp.ClientSession, coordinator_name: str, sub_agents: List[Dict]):
        """Test connectivity to sub-agents"""
        connectivity_results = []

        for sub_agent in sub_agents:
            agent_name = sub_agent['name']
            port = sub_agent['port']

            try:
                url = f"{self.base_url}:{port}/.well-known/agent-card.json"
                async with session.get(url, timeout=aiohttp.ClientTimeout(total=3)) as response:
                    if response.status == 200:
                        connectivity_results.append({
                            "agent": agent_name,
                            "port": port,
                            "status": "ONLINE"
                        })
                    else:
                        connectivity_results.append({
                            "agent": agent_name,
                            "port": port,
                            "status": f"HTTP {response.status}"
                        })
            except Exception as e:
                connectivity_results.append({
                    "agent": agent_name,
                    "port": port,
                    "status": f"OFFLINE - {str(e)}"
                })

        return connectivity_results

    async def test_coordinator_workflow(self, session: aiohttp.ClientSession, coordinator_name: str, port: int, message: str):
        """Test coordinator's ability to orchestrate workflow using SK server JSON-RPC 2.0 API"""
        try:
            url = f"{self.base_url}:{port}"

            # Create JSON-RPC 2.0 payload for SK server
            session_id = f"test-{coordinator_name.lower().replace('_', '-')}-{int(time.time())}"
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

            async with session.post(url, json=payload, timeout=aiohttp.ClientTimeout(total=90)) as response:
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
            return False, f"Timeout after 90 seconds - coordinator may be orchestrating complex workflow"
        except Exception as e:
            return False, f"Workflow error: {str(e)}"

    async def test_single_coordinator(self, session: aiohttp.ClientSession, coordinator_name: str, config: Dict[str, Any]):
        """Test a single team coordinator"""
        port = config['port']
        print(f"\n🎯 Testing {config['name']} (port {port})")
        print("-" * 60)

        coordinator_results = {
            "health_check": None,
            "sub_agents_connectivity": [],
            "workflow_scenarios": []
        }

        # Test 1: Health Check
        print(f"  📡 Health check...", end=" ")
        health_success, health_result = await self.test_coordinator_health(session, coordinator_name, port)

        if health_success:
            print("✅ ONLINE")
            agent_card = health_result
            print(f"     Coordinator: {agent_card.get('name', 'Unknown')}")
            print(f"     Workflow: {config.get('workflow_type', 'Unknown')}")

            coordinator_results["health_check"] = "PASS"

            # Test 2: Sub-agents Connectivity
            print(f"  🔗 Sub-agents connectivity...")
            connectivity_results = await self.test_sub_agents_connectivity(session, coordinator_name, config['sub_agents'])
            coordinator_results["sub_agents_connectivity"] = connectivity_results

            online_count = 0
            for result in connectivity_results:
                if result["status"] == "ONLINE":
                    print(f"     ✅ {result['agent']} (port {result['port']})")
                    online_count += 1
                else:
                    print(f"     ❌ {result['agent']} (port {result['port']}): {result['status']}")

            print(f"     📊 Sub-agents online: {online_count}/{len(config['sub_agents'])}")

            # Test 3: Workflow Scenarios (only if some sub-agents are online)
            if online_count > 0:
                for i, scenario in enumerate(config['test_scenarios'], 1):
                    scenario_name = scenario['name']
                    message = scenario['message']

                    print(f"  🎯 Workflow {i}: {scenario_name}...")
                    print(f"     Task: {message[:80]}{'...' if len(message) > 80 else ''}")

                    workflow_success, workflow_result = await self.test_coordinator_workflow(
                        session, coordinator_name, port, message
                    )

                    if workflow_success:
                        response_text = workflow_result.get('response', 'No response content')[:100]
                        print(f"     ✅ PASS - {response_text}{'...' if len(response_text) >= 100 else ''}")
                        coordinator_results["workflow_scenarios"].append({
                            "name": scenario_name,
                            "status": "PASS",
                            "message": message,
                            "response": workflow_result.get('response', '')
                        })
                    else:
                        print(f"     ❌ FAIL - {workflow_result}")
                        coordinator_results["workflow_scenarios"].append({
                            "name": scenario_name,
                            "status": "FAIL",
                            "error": workflow_result,
                            "message": message
                        })

                    # Add delay between workflow tests
                    await asyncio.sleep(2)
            else:
                print(f"  ⚠️  Skipping workflow tests - no sub-agents online")

        else:
            print(f"❌ OFFLINE - {health_result}")
            coordinator_results["health_check"] = f"FAIL - {health_result}"

        self.results[coordinator_name] = coordinator_results

    async def run_all_tests(self, target_coordinators=None):
        """Run tests for all team coordinators or specific ones"""
        print(f"\n🧪 HR Team Coordinators Test Suite - Level 3 Testing")
        print(f"=" * 80)

        coordinators_to_test = target_coordinators or list(self.coordinators.keys())
        print(f"Testing {len(coordinators_to_test)} team coordinator agents")
        print(f"Testing A2A communication and workflow orchestration")
        print(f"Started at: {datetime.now()}")
        print(f"=" * 80)

        async with aiohttp.ClientSession() as session:
            # Test coordinators sequentially to avoid resource conflicts
            for coordinator_name in coordinators_to_test:
                if coordinator_name in self.coordinators:
                    config = self.coordinators[coordinator_name]
                    await self.test_single_coordinator(session, coordinator_name, config)

        # Generate final report
        return await self.generate_report()

    async def generate_report(self):
        """Generate comprehensive test report"""
        print(f"\n" + "=" * 80)
        print(f"🏁 Team Coordinators Test Results")
        print(f"=" * 80)

        online_coordinators = 0
        offline_coordinators = 0
        total_workflows = 0
        passed_workflows = 0
        total_sub_agents = 0
        online_sub_agents = 0

        for coordinator_name, results in self.results.items():
            config = self.coordinators.get(coordinator_name, {})
            coordinator_display_name = config.get('name', coordinator_name)

            if results["health_check"] == "PASS":
                online_coordinators += 1
                print(f"✅ {coordinator_display_name} ({config.get('workflow_type', 'unknown')} workflow)")

                # Sub-agents summary
                connectivity = results["sub_agents_connectivity"]
                sub_agents_online = sum(1 for r in connectivity if r["status"] == "ONLINE")
                total_sub_agents += len(connectivity)
                online_sub_agents += sub_agents_online

                print(f"   🔗 Sub-agents: {sub_agents_online}/{len(connectivity)} online")

                # Workflow scenarios
                for scenario in results["workflow_scenarios"]:
                    total_workflows += 1
                    if scenario["status"] == "PASS":
                        passed_workflows += 1
                        print(f"   ✅ {scenario['name']}")
                    else:
                        print(f"   ❌ {scenario['name']}: {scenario.get('error', 'Unknown error')}")

            else:
                offline_coordinators += 1
                print(f"❌ {coordinator_display_name}: {results['health_check']}")

        print(f"\n📊 Summary:")
        print(f"   Team Coordinators Online: {online_coordinators}")
        print(f"   Team Coordinators Offline: {offline_coordinators}")
        print(f"   Sub-agents Online: {online_sub_agents}/{total_sub_agents}")
        if total_workflows > 0:
            workflow_success_rate = (passed_workflows / total_workflows) * 100
            print(f"   Workflows Passed: {passed_workflows}/{total_workflows} ({workflow_success_rate:.1f}%)")

        print(f"\n💡 A2A Communication Status:")
        if online_sub_agents > 0:
            comm_health = (online_sub_agents / total_sub_agents) * 100 if total_sub_agents > 0 else 0
            print(f"   Agent-to-Agent connectivity: {comm_health:.1f}%")
            if comm_health >= 80:
                print(f"   🟢 A2A network is healthy")
            elif comm_health >= 50:
                print(f"   🟡 A2A network has some issues")
            else:
                print(f"   🔴 A2A network has major issues")
        else:
            print(f"   🔴 No A2A communication possible")

        return online_coordinators, offline_coordinators, passed_workflows, total_workflows

def main():
    """Main testing function"""
    import argparse

    parser = argparse.ArgumentParser(description="Test HR Team Coordinator Agents")
    parser.add_argument("--coordinator", help="Test specific coordinator only")
    parser.add_argument("--list", action="store_true", help="List available coordinators")

    args = parser.parse_args()

    tester = TeamCoordinatorsTestSuite()

    if args.list:
        print("Available team coordinators:")
        for coordinator_name, config in tester.coordinators.items():
            print(f"  {coordinator_name}: {config['name']} (port {config['port']}) - {config['workflow_type']} workflow")
            print(f"    Sub-agents: {', '.join([sa['name'] for sa in config['sub_agents']])}")
        return

    target_coordinators = [args.coordinator] if args.coordinator else None

    if args.coordinator and args.coordinator not in tester.coordinators:
        print(f"Unknown coordinator: {args.coordinator}")
        print(f"Available coordinators: {', '.join(tester.coordinators.keys())}")
        sys.exit(1)

    try:
        online, offline, passed, total = asyncio.run(tester.run_all_tests(target_coordinators))
        # Exit with error if any coordinators offline or workflows failed
        sys.exit(0 if offline == 0 and (total == 0 or passed == total) else 1)
    except KeyboardInterrupt:
        print("\n🛑 Testing interrupted by user")
        sys.exit(1)

if __name__ == "__main__":
    main()