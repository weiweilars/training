#!/usr/bin/env python3
"""
HR Tools Test Suite
Test all MCP tools directly without agents
This is Level 1 testing - foundation layer
"""

import requests
import json
import sys
import time
from datetime import datetime

class HRToolsTester:
    """Direct testing of HR MCP tools"""

    def __init__(self):
        # HR MCP Tools with their ports organized by agent
        self.tools = {
            # Job Requisition Agent Tools
            "job-creation": {"port": 8051, "agent": "job_requisition"},
            "job-workflow": {"port": 8052, "agent": "job_requisition"},
            "job-templates": {"port": 8053, "agent": "job_requisition"},

            # Sourcing Agent Tools
            "social-sourcing": {"port": 8061, "agent": "sourcing"},
            "talent-pool": {"port": 8062, "agent": "sourcing"},
            "outreach": {"port": 8063, "agent": "sourcing"},

            # Resume Screening Agent Tools
            "document-processing": {"port": 8071, "agent": "resume_screening"},
            "matching-engine": {"port": 8072, "agent": "resume_screening"},

            # Communication Agent Tools
            "email-service": {"port": 8081, "agent": "communication"},
            "engagement-tracking": {"port": 8082, "agent": "communication"},

            # Interview Scheduling Agent Tools
            "calendar-integration": {"port": 8091, "agent": "interview_scheduling"},
            "interview-workflow": {"port": 8092, "agent": "interview_scheduling"},
            "meeting-management": {"port": 8093, "agent": "interview_scheduling"},

            # Assessment Agent Tools
            "test-engine": {"port": 8101, "agent": "assessment"},
            "assessment-library": {"port": 8102, "agent": "assessment"},
            "results-analysis": {"port": 8103, "agent": "assessment"},

            # Offer Management Agent Tools
            "offer-generation": {"port": 8111, "agent": "offer_management"},
            "negotiation-management": {"port": 8112, "agent": "offer_management"},
            "contract-management": {"port": 8113, "agent": "offer_management"},

            # Analytics Reporting Agent Tools
            "metrics-engine": {"port": 8121, "agent": "analytics_reporting"},
            "dashboard-generator": {"port": 8122, "agent": "analytics_reporting"},
            "predictive-analytics": {"port": 8123, "agent": "analytics_reporting"},

            # Compliance Agent Tools
            "regulatory-engine": {"port": 8131, "agent": "compliance"},
            "data-privacy": {"port": 8132, "agent": "compliance"},
            "audit-management": {"port": 8133, "agent": "compliance"},

            # Background Verification Agent Tools
            "verification-engine": {"port": 8141, "agent": "background_verification"},
            "reference-check": {"port": 8142, "agent": "background_verification"},
            "credential-validation": {"port": 8143, "agent": "background_verification"},
        }

        self.results = {}
        self.headers = {
            'Content-Type': 'application/json',
            'Accept': 'application/json, text/event-stream'
        }

    def test_tool_connection(self, tool_name, port):
        """Test if tool server is responding"""
        try:
            url = f"http://localhost:{port}/mcp"
            data = {
                "jsonrpc": "2.0",
                "method": "tools/list",
                "params": {},
                "id": 1
            }
            response = requests.post(url, json=data, headers=self.headers, timeout=5)

            if response.status_code == 200:
                # Parse event stream response
                content = response.text
                if "event: message" in content:
                    # Extract JSON from event stream
                    lines = content.split('\n')
                    for line in lines:
                        if line.startswith('data: '):
                            json_data = line[6:]  # Remove 'data: ' prefix
                            try:
                                result = json.loads(json_data)
                                if 'result' in result and 'tools' in result['result']:
                                    return True, result['result']['tools']
                            except json.JSONDecodeError:
                                continue

            return False, f"HTTP {response.status_code}: {response.text[:200]}"

        except requests.exceptions.RequestException as e:
            return False, f"Connection error: {str(e)}"

    def test_sample_tool_call(self, tool_name, port, available_tools):
        """Test calling a sample tool function"""
        if not available_tools:
            return False, "No tools available"

        # Get first available tool
        first_tool = available_tools[0]
        tool_func_name = first_tool.get('name', '')

        # Generate sample arguments based on tool name patterns
        sample_args = self.generate_sample_args(tool_func_name, tool_name)

        try:
            url = f"http://localhost:{port}/mcp"
            data = {
                "jsonrpc": "2.0",
                "method": "tools/call",
                "params": {
                    "name": tool_func_name,
                    "arguments": sample_args
                },
                "id": 2
            }

            response = requests.post(url, json=data, headers=self.headers, timeout=10)

            if response.status_code == 200:
                return True, f"Tool call successful: {tool_func_name}"
            else:
                return False, f"Tool call failed: HTTP {response.status_code}"

        except requests.exceptions.RequestException as e:
            return False, f"Tool call error: {str(e)}"

    def generate_sample_args(self, tool_func_name, tool_name):
        """Generate sample arguments for tool testing"""
        if "create_job" in tool_func_name:
            return {
                "title": "Test Software Engineer",
                "department": "Engineering",
                "location": "Remote"
            }
        elif "calculate_skills" in tool_func_name:
            return {
                "candidate_skills": "Python, Django, React",
                "required_skills": "Python, JavaScript"
            }
        elif "send_email" in tool_func_name:
            return {
                "recipient": "test@example.com",
                "subject": "Test Email",
                "message": "This is a test message"
            }
        elif "schedule_interview" in tool_func_name:
            return {
                "candidate_id": "test-123",
                "interviewer_email": "interviewer@example.com",
                "datetime": "2024-01-15T10:00:00Z"
            }
        else:
            # Generic fallback
            return {}

    def run_all_tests(self):
        """Run comprehensive tool testing"""
        print(f"\n🧪 HR Tools Test Suite - Level 1 Testing")
        print(f"=" * 60)
        print(f"Testing {len(self.tools)} MCP tools directly")
        print(f"Started at: {datetime.now()}")
        print(f"=" * 60)

        passed = 0
        failed = 0

        for tool_name, config in self.tools.items():
            port = config['port']
            agent = config['agent']

            print(f"\n🔧 Testing {tool_name} (port {port}) for {agent} agent")
            print("-" * 40)

            # Test 1: Connection
            print(f"  📡 Connection test...", end=" ")
            conn_success, conn_result = self.test_tool_connection(tool_name, port)

            if conn_success:
                print("✅ PASS")
                available_tools = conn_result

                # Test 2: Sample tool call
                print(f"  🛠️  Tool call test...", end=" ")
                call_success, call_result = self.test_sample_tool_call(tool_name, port, available_tools)

                if call_success:
                    print("✅ PASS")
                    passed += 1
                    self.results[tool_name] = "PASS"
                else:
                    print(f"❌ FAIL - {call_result}")
                    failed += 1
                    self.results[tool_name] = f"FAIL - {call_result}"
            else:
                print(f"❌ FAIL - {conn_result}")
                failed += 1
                self.results[tool_name] = f"FAIL - {conn_result}"

        # Final results
        print(f"\n" + "=" * 60)
        print(f"🏁 HR Tools Test Results")
        print(f"=" * 60)
        print(f"✅ Passed: {passed}")
        print(f"❌ Failed: {failed}")
        print(f"📊 Success Rate: {(passed/(passed+failed)*100):.1f}%" if (passed+failed) > 0 else "0%")

        if failed > 0:
            print(f"\n❌ Failed Tools:")
            for tool_name, result in self.results.items():
                if result.startswith("FAIL"):
                    print(f"   - {tool_name}: {result}")

        return passed, failed

def main():
    """Main testing function"""
    import argparse

    parser = argparse.ArgumentParser(description="Test HR MCP Tools Directly")
    parser.add_argument("--tool", help="Test specific tool only")
    parser.add_argument("--agent", help="Test tools for specific agent only")

    args = parser.parse_args()

    tester = HRToolsTester()

    if args.tool:
        if args.tool in tester.tools:
            config = tester.tools[args.tool]
            print(f"Testing single tool: {args.tool}")
            conn_success, conn_result = tester.test_tool_connection(args.tool, config['port'])
            if conn_success:
                call_success, call_result = tester.test_sample_tool_call(args.tool, config['port'], conn_result)
                print(f"Result: {'PASS' if call_success else 'FAIL'}")
            else:
                print(f"Connection failed: {conn_result}")
        else:
            print(f"Unknown tool: {args.tool}")
            print(f"Available tools: {', '.join(tester.tools.keys())}")
    elif args.agent:
        # Test tools for specific agent
        agent_tools = {k: v for k, v in tester.tools.items() if v['agent'] == args.agent}
        if agent_tools:
            print(f"Testing tools for {args.agent} agent:")
            for tool_name in agent_tools:
                print(f"- {tool_name}")
            # Could implement filtered testing here
        else:
            print(f"No tools found for agent: {args.agent}")
    else:
        # Run all tests
        passed, failed = tester.run_all_tests()
        sys.exit(0 if failed == 0 else 1)

if __name__ == "__main__":
    main()