#!/usr/bin/env python3
"""
HR Master Coordinator Test Suite
Test the master coordinator agent (port 5040) and complete system integration
This is Level 4 testing - full system orchestration and end-to-end workflows
"""

import asyncio
import aiohttp
import json
import time
import uuid
from datetime import datetime
from typing import Dict, List, Any
import sys

class MasterCoordinatorTestSuite:
    """Test suite for the master coordinator and complete system integration"""

    def __init__(self):
        self.base_url = "http://localhost"
        self.master_coordinator = {
            "name": "Master Coordinator Agent",
            "port": 5040,
            "team_coordinators": [
                {"name": "acquisition_team_agent", "port": 5032, "mission": "Find, screen, and validate candidates"},
                {"name": "experience_team_agent", "port": 5033, "mission": "Manage candidate journey and interactions"},
                {"name": "closing_team_agent", "port": 5034, "mission": "Finalize offers and complete hiring process"}
            ],
            "test_scenarios": [
                {
                    "name": "Complete End-to-End Hiring Process",
                    "message": "Execute complete hiring process for Senior Software Engineer role: source candidates, screen resumes, schedule interviews, conduct assessments, generate offers, handle negotiations, and ensure compliance. Track metrics throughout.",
                    "expected_coordination": ["acquisition_team_agent", "experience_team_agent", "closing_team_agent"],
                    "complexity": "high"
                },
                {
                    "name": "Bulk Hiring Campaign",
                    "message": "Launch hiring campaign for 5 engineering positions (2 Senior Engineers, 2 Data Scientists, 1 DevOps Lead). Coordinate parallel processing across all teams while maintaining quality standards.",
                    "expected_coordination": ["acquisition_team_agent", "experience_team_agent", "closing_team_agent"],
                    "complexity": "very_high"
                },
                {
                    "name": "Emergency Hiring Request",
                    "message": "Handle urgent hiring request for critical DevOps Engineer role needed within 2 weeks. Prioritize speed while maintaining compliance and quality. Coordinate expedited workflow across all teams.",
                    "expected_coordination": ["acquisition_team_agent", "experience_team_agent", "closing_team_agent"],
                    "complexity": "high"
                },
                {
                    "name": "Hiring Process Optimization",
                    "message": "Analyze current hiring processes across all teams, identify bottlenecks, and recommend optimizations. Focus on reducing time-to-hire while improving candidate experience and compliance.",
                    "expected_coordination": ["acquisition_team_agent", "experience_team_agent", "closing_team_agent"],
                    "complexity": "medium"
                },
                {
                    "name": "Quarterly Hiring Analytics",
                    "message": "Generate comprehensive quarterly hiring report including metrics from all teams: sourcing effectiveness, interview success rates, offer acceptance rates, compliance status, and recommendations for next quarter.",
                    "expected_coordination": ["acquisition_team_agent", "experience_team_agent", "closing_team_agent"],
                    "complexity": "medium"
                }
            ]
        }

        self.system_health = {}
        self.results = {}

    async def test_system_health_check(self, session: aiohttp.ClientSession):
        """Test complete system health - all layers"""
        print(f"🏥 System Health Check - All Layers")
        print("-" * 60)

        health_results = {
            "master_coordinator": None,
            "team_coordinators": {},
            "individual_agents": {},
            "mcp_tools": {}
        }

        # Test Master Coordinator
        print(f"  🎯 Master Coordinator (port 5040)...", end=" ")
        try:
            url = f"{self.base_url}:5040/.well-known/agent-card.json"
            async with session.get(url, timeout=aiohttp.ClientTimeout(total=5)) as response:
                if response.status == 200:
                    print("✅ ONLINE")
                    health_results["master_coordinator"] = "ONLINE"
                else:
                    print(f"❌ HTTP {response.status}")
                    health_results["master_coordinator"] = f"HTTP {response.status}"
        except Exception as e:
            print(f"❌ OFFLINE")
            health_results["master_coordinator"] = f"OFFLINE - {str(e)}"

        # Test Team Coordinators
        print(f"  🎯 Team Coordinators...")
        for coordinator in self.master_coordinator["team_coordinators"]:
            coord_name = coordinator["name"]
            port = coordinator["port"]
            print(f"     {coord_name} (port {port})...", end=" ")

            try:
                url = f"{self.base_url}:{port}/.well-known/agent-card.json"
                async with session.get(url, timeout=aiohttp.ClientTimeout(total=3)) as response:
                    if response.status == 200:
                        print("✅")
                        health_results["team_coordinators"][coord_name] = "ONLINE"
                    else:
                        print(f"❌ HTTP {response.status}")
                        health_results["team_coordinators"][coord_name] = f"HTTP {response.status}"
            except Exception as e:
                print(f"❌ OFFLINE")
                health_results["team_coordinators"][coord_name] = f"OFFLINE"

        # Test Sample Individual Agents
        print(f"  🤖 Individual Agents (sample)...")
        sample_agents = [
            {"name": "job_requisition_agent", "port": 5020},
            {"name": "sourcing_agent", "port": 5021},
            {"name": "communication_agent", "port": 5023},
            {"name": "analytics_reporting_agent", "port": 5028}
        ]

        for agent in sample_agents:
            agent_name = agent["name"]
            port = agent["port"]
            print(f"     {agent_name} (port {port})...", end=" ")

            try:
                url = f"{self.base_url}:{port}/.well-known/agent-card.json"
                async with session.get(url, timeout=aiohttp.ClientTimeout(total=3)) as response:
                    if response.status == 200:
                        print("✅")
                        health_results["individual_agents"][agent_name] = "ONLINE"
                    else:
                        print("❌")
                        health_results["individual_agents"][agent_name] = f"HTTP {response.status}"
            except Exception as e:
                print("❌")
                health_results["individual_agents"][agent_name] = "OFFLINE"

        # Test Sample MCP Tools
        print(f"  🛠️  MCP Tools (sample)...")
        sample_tools = [
            {"name": "job-creation", "port": 8051},
            {"name": "social-sourcing", "port": 8061},
            {"name": "email-service", "port": 8081},
            {"name": "metrics-engine", "port": 8121}
        ]

        for tool in sample_tools:
            tool_name = tool["name"]
            port = tool["port"]
            print(f"     {tool_name} (port {port})...", end=" ")

            try:
                url = f"http://localhost:{port}/mcp"
                data = {"jsonrpc": "2.0", "method": "tools/list", "params": {}, "id": 1}
                headers = {'Content-Type': 'application/json', 'Accept': 'application/json, text/event-stream'}

                async with session.post(url, json=data, headers=headers, timeout=aiohttp.ClientTimeout(total=3)) as response:
                    if response.status == 200:
                        print("✅")
                        health_results["mcp_tools"][tool_name] = "ONLINE"
                    else:
                        print("❌")
                        health_results["mcp_tools"][tool_name] = f"HTTP {response.status}"
            except Exception as e:
                print("❌")
                health_results["mcp_tools"][tool_name] = "OFFLINE"

        self.system_health = health_results
        return health_results

    async def test_master_coordination(self, session: aiohttp.ClientSession, scenario: Dict[str, Any]):
        """Test master coordinator's orchestration capabilities"""
        port = self.master_coordinator["port"]
        scenario_name = scenario["name"]
        message = scenario["message"]
        complexity = scenario.get("complexity", "medium")

        print(f"\n🎯 Master Coordination Test: {scenario_name}")
        print(f"Complexity: {complexity.upper()}")
        print(f"Message: {message[:100]}{'...' if len(message) > 100 else ''}")
        print("-" * 80)

        try:
            url = f"{self.base_url}:{port}"

            # Create JSON-RPC 2.0 payload for SK server
            session_id = f"test-master-{int(time.time())}"
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

            # Timeout based on complexity
            timeout_map = {
                "medium": 30,
                "high": 60,
                "very_high": 90
            }
            timeout = timeout_map.get(complexity, 45)

            print(f"  ⏳ Executing master coordination (timeout: {timeout}s)...")

            async with session.post(url, json=payload, timeout=aiohttp.ClientTimeout(total=timeout)) as response:
                if response.status == 200:
                    result = await response.json()
                    print(f"  ✅ Master coordination successful")

                    # Extract actual response from nested JSON-RPC structure
                    actual_response = None
                    if 'result' in result and 'result' in result['result']:
                        inner_result = result['result']['result']
                        if isinstance(inner_result, dict) and 'message' in inner_result:
                            actual_response = inner_result['message'].get('content', '')
                        else:
                            actual_response = str(inner_result)
                    else:
                        actual_response = json.dumps(result)

                    # Analyze response for coordination patterns
                    response_content = actual_response.lower() if actual_response else ""
                    coordinated_teams = []

                    for expected_team in scenario.get("expected_coordination", []):
                        if expected_team.replace("_", "").replace("-", "") in response_content.replace("_", "").replace("-", ""):
                            coordinated_teams.append(expected_team)

                    if coordinated_teams:
                        print(f"  🔗 Teams coordinated: {', '.join(coordinated_teams)}")

                    return True, {
                        "response": actual_response,
                        "coordinated_teams": coordinated_teams,
                        "complexity": complexity
                    }
                else:
                    error_text = await response.text()
                    print(f"  ❌ Master coordination failed: HTTP {response.status}")
                    return False, f"HTTP {response.status}: {error_text[:200]}"

        except asyncio.TimeoutError:
            print(f"  ⏰ Master coordination timeout after {timeout}s")
            return False, f"Timeout after {timeout}s"
        except Exception as e:
            print(f"  ❌ Master coordination error: {str(e)}")
            return False, f"Error: {str(e)}"

    async def run_integration_tests(self):
        """Run complete integration tests"""
        print(f"\n🧪 HR Master Coordinator Test Suite - Level 4 Testing")
        print(f"=" * 90)
        print(f"Testing complete system integration and end-to-end workflows")
        print(f"Master Coordinator: {self.master_coordinator['name']} (port {self.master_coordinator['port']})")
        print(f"Started at: {datetime.now()}")
        print(f"=" * 90)

        async with aiohttp.ClientSession() as session:
            # Phase 1: System Health Check
            print(f"\n📋 Phase 1: System Health Assessment")
            health_results = await self.test_system_health_check(session)

            # Only proceed if master coordinator is online
            if health_results.get("master_coordinator") != "ONLINE":
                print(f"\n❌ Cannot proceed: Master Coordinator is offline")
                return False

            # Phase 2: Master Coordination Tests
            print(f"\n📋 Phase 2: Master Coordination Scenarios")

            scenario_results = []
            for i, scenario in enumerate(self.master_coordinator["test_scenarios"], 1):
                print(f"\n--- Scenario {i}/{len(self.master_coordinator['test_scenarios'])} ---")

                success, result = await self.test_master_coordination(session, scenario)
                scenario_results.append({
                    "scenario": scenario,
                    "success": success,
                    "result": result
                })

                # Add delay between complex scenarios
                if scenario.get("complexity") in ["high", "very_high"]:
                    print(f"  ⏳ Cooling down for {3}s before next scenario...")
                    await asyncio.sleep(3)
                else:
                    await asyncio.sleep(1)

            # Phase 3: Generate Final Report
            await self.generate_integration_report(health_results, scenario_results)

    async def generate_integration_report(self, health_results: Dict, scenario_results: List[Dict]):
        """Generate comprehensive integration test report"""
        print(f"\n" + "=" * 90)
        print(f"🏁 Master Coordinator Integration Test Results")
        print(f"=" * 90)

        # System Health Summary
        print(f"🏥 System Health Summary:")
        print(f"   Master Coordinator: {'✅' if health_results.get('master_coordinator') == 'ONLINE' else '❌'} {health_results.get('master_coordinator', 'Unknown')}")

        team_coordinators_online = sum(1 for status in health_results.get("team_coordinators", {}).values() if status == "ONLINE")
        team_coordinators_total = len(health_results.get("team_coordinators", {}))
        print(f"   Team Coordinators: {team_coordinators_online}/{team_coordinators_total} online")

        individual_agents_online = sum(1 for status in health_results.get("individual_agents", {}).values() if status == "ONLINE")
        individual_agents_total = len(health_results.get("individual_agents", {}))
        print(f"   Individual Agents: {individual_agents_online}/{individual_agents_total} online (sample)")

        mcp_tools_online = sum(1 for status in health_results.get("mcp_tools", {}).values() if status == "ONLINE")
        mcp_tools_total = len(health_results.get("mcp_tools", {}))
        print(f"   MCP Tools: {mcp_tools_online}/{mcp_tools_total} online (sample)")

        # Master Coordination Results
        print(f"\n🎯 Master Coordination Results:")
        successful_scenarios = 0
        total_scenarios = len(scenario_results)

        complexity_stats = {"medium": [], "high": [], "very_high": []}

        for result in scenario_results:
            scenario = result["scenario"]
            success = result["success"]
            scenario_name = scenario["name"]
            complexity = scenario.get("complexity", "medium")

            complexity_stats[complexity].append(success)

            if success:
                successful_scenarios += 1
                coordinated_teams = result["result"].get("coordinated_teams", [])
                print(f"   ✅ {scenario_name}")
                if coordinated_teams:
                    print(f"      🔗 Coordinated: {', '.join(coordinated_teams)}")
            else:
                error = result["result"]
                print(f"   ❌ {scenario_name}: {error}")

        # Success Rate Analysis
        print(f"\n📊 Performance Analysis:")
        if total_scenarios > 0:
            success_rate = (successful_scenarios / total_scenarios) * 100
            print(f"   Overall Success Rate: {successful_scenarios}/{total_scenarios} ({success_rate:.1f}%)")

            # Complexity breakdown
            for complexity, results in complexity_stats.items():
                if results:
                    complexity_success = sum(results)
                    complexity_total = len(results)
                    complexity_rate = (complexity_success / complexity_total) * 100
                    print(f"   {complexity.capitalize()} Complexity: {complexity_success}/{complexity_total} ({complexity_rate:.1f}%)")

        # System Integration Health
        print(f"\n🏗️ System Integration Health:")
        total_components = (
            (1 if health_results.get("master_coordinator") == "ONLINE" else 0) +
            team_coordinators_online +
            individual_agents_online +
            mcp_tools_online
        )
        max_components = (
            1 +  # master coordinator
            team_coordinators_total +
            individual_agents_total +
            mcp_tools_total
        )

        if max_components > 0:
            integration_health = (total_components / max_components) * 100
            print(f"   Integration Health: {integration_health:.1f}%")

            if integration_health >= 90:
                print(f"   🟢 Excellent - Full system operational")
            elif integration_health >= 75:
                print(f"   🟡 Good - System mostly operational")
            elif integration_health >= 50:
                print(f"   🟠 Fair - System partially operational")
            else:
                print(f"   🔴 Poor - System has major issues")

        # Recommendations
        print(f"\n💡 Recommendations:")
        if successful_scenarios == total_scenarios and total_components == max_components:
            print(f"   🚀 System is fully operational and ready for production use")
        else:
            if health_results.get("master_coordinator") != "ONLINE":
                print(f"   🔧 Priority: Fix master coordinator connectivity")
            if team_coordinators_online < team_coordinators_total:
                print(f"   🔧 Fix team coordinator connectivity issues")
            if successful_scenarios < total_scenarios:
                print(f"   🔧 Review failed coordination scenarios")
            if mcp_tools_online < mcp_tools_total:
                print(f"   🔧 Ensure all MCP tools are running")

        return successful_scenarios, total_scenarios, integration_health if max_components > 0 else 0

def main():
    """Main testing function"""
    import argparse

    parser = argparse.ArgumentParser(description="Test HR Master Coordinator and System Integration")
    parser.add_argument("--health-only", action="store_true", help="Run only system health check")
    parser.add_argument("--scenario", type=int, help="Run specific scenario only (1-based index)")

    args = parser.parse_args()

    tester = MasterCoordinatorTestSuite()

    try:
        if args.health_only:
            print("Running system health check only...")
            async def health_check_only():
                async with aiohttp.ClientSession() as session:
                    health_results = await tester.test_system_health_check(session)
                    return health_results

            health = asyncio.run(health_check_only())
            print(f"\nHealth check complete. Master coordinator: {health.get('master_coordinator', 'Unknown')}")
        elif args.scenario:
            scenario_index = args.scenario - 1
            if 0 <= scenario_index < len(tester.master_coordinator["test_scenarios"]):
                scenario = tester.master_coordinator["test_scenarios"][scenario_index]
                print(f"Running single scenario: {scenario['name']}")

                async def single_scenario_test():
                    async with aiohttp.ClientSession() as session:
                        success, result = await tester.test_master_coordination(session, scenario)
                        return success

                success = asyncio.run(single_scenario_test())
                sys.exit(0 if success else 1)
            else:
                print(f"Invalid scenario index. Available scenarios: 1-{len(tester.master_coordinator['test_scenarios'])}")
                sys.exit(1)
        else:
            # Run full integration tests
            asyncio.run(tester.run_integration_tests())

    except KeyboardInterrupt:
        print("\n🛑 Testing interrupted by user")
        sys.exit(1)

if __name__ == "__main__":
    main()