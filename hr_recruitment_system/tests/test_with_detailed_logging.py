#!/usr/bin/env python3
"""
HR System Test with Detailed Logging
Demonstrates comprehensive logging during test execution
"""

import subprocess
import time
import os
import json
from datetime import datetime
import requests

def create_test_session():
    """Create a test session with logging"""
    session_id = f"hr_test_{int(time.time())}"
    logs_dir = f"../test_logs/{session_id}"

    # Create directory structure
    os.makedirs(f"{logs_dir}/component_activity", exist_ok=True)
    os.makedirs(f"{logs_dir}/test_results", exist_ok=True)
    os.makedirs(f"{logs_dir}/api_calls", exist_ok=True)

    print(f"🚀 Starting HR System Test with Detailed Logging")
    print(f"🆔 Session ID: {session_id}")
    print(f"📁 Logs Directory: {logs_dir}")
    print("=" * 80)

    return session_id, logs_dir

def log_component_status(logs_dir):
    """Log current status of all system components"""
    status_log = f"{logs_dir}/component_activity/system_status.log"

    components = {
        "mcp_tools": [
            {"name": "job-creation", "port": 8051},
            {"name": "social-sourcing", "port": 8061},
            {"name": "email-service", "port": 8081},
            {"name": "metrics-engine", "port": 8121}
        ],
        "individual_agents": [
            {"name": "job_requisition_agent", "port": 5020},
            {"name": "sourcing_agent", "port": 5021},
            {"name": "communication_agent", "port": 5023},
            {"name": "analytics_reporting_agent", "port": 5028}
        ],
        "coordinators": [
            {"name": "acquisition_team_agent", "port": 5032},
            {"name": "experience_team_agent", "port": 5033},
            {"name": "closing_team_agent", "port": 5034},
            {"name": "master_coordinator_agent", "port": 5040}
        ]
    }

    status_data = {
        "timestamp": datetime.now().isoformat(),
        "components": {}
    }

    with open(status_log, "a") as f:
        f.write(f"\n=== System Status Check at {datetime.now()} ===\n")

        for component_type, component_list in components.items():
            f.write(f"\n{component_type.upper()}:\n")
            status_data["components"][component_type] = []

            for component in component_list:
                name = component["name"]
                port = component["port"]

                try:
                    # Try to connect to health endpoint
                    if component_type == "mcp_tools":
                        # MCP tools use JSON-RPC
                        response = requests.post(
                            f"http://localhost:{port}/mcp",
                            json={"jsonrpc": "2.0", "method": "tools/list", "params": {}, "id": 1},
                            headers={"Accept": "application/json, text/event-stream"},
                            timeout=3
                        )
                    else:
                        # Agents use agent-card endpoint
                        response = requests.get(
                            f"http://localhost:{port}/.well-known/agent-card.json",
                            timeout=3
                        )

                    if response.status_code == 200:
                        status = "🟢 ONLINE"
                        data = response.json() if response.headers.get('content-type', '').startswith('application/json') else {}
                        f.write(f"  {name} (:{port}): {status}\n")

                        # Log additional info for agents
                        if component_type != "mcp_tools" and 'name' in data:
                            f.write(f"    Name: {data.get('name', 'Unknown')}\n")
                            f.write(f"    Version: {data.get('version', 'Unknown')}\n")

                        status_data["components"][component_type].append({
                            "name": name,
                            "port": port,
                            "status": "online",
                            "response_data": data
                        })
                    else:
                        status = "🟡 RESPONDING"
                        f.write(f"  {name} (:{port}): {status} (HTTP {response.status_code})\n")
                        status_data["components"][component_type].append({
                            "name": name,
                            "port": port,
                            "status": "responding",
                            "http_code": response.status_code
                        })

                except requests.exceptions.ConnectionError:
                    status = "🔴 OFFLINE"
                    f.write(f"  {name} (:{port}): {status} (Connection refused)\n")
                    status_data["components"][component_type].append({
                        "name": name,
                        "port": port,
                        "status": "offline",
                        "error": "connection_refused"
                    })
                except requests.exceptions.Timeout:
                    status = "🟡 TIMEOUT"
                    f.write(f"  {name} (:{port}): {status} (Request timeout)\n")
                    status_data["components"][component_type].append({
                        "name": name,
                        "port": port,
                        "status": "timeout",
                        "error": "timeout"
                    })
                except Exception as e:
                    status = "❌ ERROR"
                    f.write(f"  {name} (:{port}): {status} ({str(e)})\n")
                    status_data["components"][component_type].append({
                        "name": name,
                        "port": port,
                        "status": "error",
                        "error": str(e)
                    })

    # Save JSON status
    with open(f"{logs_dir}/component_activity/status.json", "w") as f:
        json.dump(status_data, f, indent=2)

    print(f"📊 Component status logged to: {status_log}")
    return status_data

def test_agent_with_logging(agent_name, port, logs_dir):
    """Test a specific agent and log the interaction"""
    print(f"\n🧪 Testing {agent_name} with detailed logging...")

    api_log = f"{logs_dir}/api_calls/{agent_name}_api_calls.log"
    test_result_log = f"{logs_dir}/test_results/{agent_name}_test.json"

    test_message = "Create a job posting for a Senior Python Developer with 5+ years experience"

    test_data = {
        "agent_name": agent_name,
        "port": port,
        "test_message": test_message,
        "timestamp": datetime.now().isoformat(),
        "api_calls": [],
        "result": None
    }

    try:
        # Log the API call
        with open(api_log, "w") as f:
            f.write(f"=== API Call Log for {agent_name} ===\n")
            f.write(f"Timestamp: {datetime.now()}\n")
            f.write(f"Agent: {agent_name}\n")
            f.write(f"Port: {port}\n")
            f.write(f"Test Message: {test_message}\n")
            f.write("=" * 60 + "\n")

        # 1. Check agent health
        print(f"  📡 Checking {agent_name} health...")
        health_url = f"http://localhost:{port}/.well-known/agent-card.json"

        health_response = requests.get(health_url, timeout=5)

        with open(api_log, "a") as f:
            f.write(f"\n1. HEALTH CHECK:\n")
            f.write(f"   URL: {health_url}\n")
            f.write(f"   Status: {health_response.status_code}\n")
            f.write(f"   Response: {health_response.text[:200]}...\n")

        test_data["api_calls"].append({
            "type": "health_check",
            "url": health_url,
            "status_code": health_response.status_code,
            "success": health_response.status_code == 200
        })

        if health_response.status_code != 200:
            print(f"  ❌ {agent_name} health check failed")
            test_data["result"] = "health_check_failed"
            return test_data

        print(f"  ✅ {agent_name} is healthy")

        # 2. Send test message
        print(f"  💬 Sending test message to {agent_name}...")

        message_url = f"http://localhost:{port}"
        payload = {
            "jsonrpc": "2.0",
            "method": "message/send",
            "params": {
                "message": {"content": test_message},
                "sessionId": f"test-{agent_name}-{int(time.time())}"
            },
            "id": f"test-{int(time.time())}"
        }

        message_response = requests.post(
            message_url,
            json=payload,
            headers={"Content-Type": "application/json"},
            timeout=30
        )

        with open(api_log, "a") as f:
            f.write(f"\n2. MESSAGE SEND:\n")
            f.write(f"   URL: {message_url}\n")
            f.write(f"   Payload: {json.dumps(payload, indent=2)}\n")
            f.write(f"   Status: {message_response.status_code}\n")
            f.write(f"   Response: {message_response.text[:500]}...\n")

        test_data["api_calls"].append({
            "type": "message_send",
            "url": message_url,
            "payload": payload,
            "status_code": message_response.status_code,
            "success": message_response.status_code == 200,
            "response_preview": message_response.text[:200]
        })

        if message_response.status_code == 200:
            print(f"  ✅ {agent_name} processed message successfully")

            try:
                response_data = message_response.json()
                # Try to extract the actual response
                if 'result' in response_data and 'result' in response_data['result']:
                    actual_response = response_data['result']['result']
                    if isinstance(actual_response, dict) and 'message' in actual_response:
                        content = actual_response['message'].get('content', '')
                        print(f"  📝 Response: {content[:100]}...")
                        test_data["result"] = "success"
                        test_data["response_content"] = content
                    else:
                        test_data["result"] = "success_no_content"
                else:
                    test_data["result"] = "success_unknown_format"

            except Exception as e:
                print(f"  ⚠️  Could not parse JSON response: {e}")
                test_data["result"] = "success_parse_error"
        else:
            print(f"  ❌ {agent_name} failed to process message (HTTP {message_response.status_code})")
            test_data["result"] = "message_send_failed"

    except Exception as e:
        print(f"  ❌ Error testing {agent_name}: {e}")
        test_data["result"] = "error"
        test_data["error"] = str(e)

        with open(api_log, "a") as f:
            f.write(f"\nERROR: {e}\n")

    # Save test results
    with open(test_result_log, "w") as f:
        json.dump(test_data, f, indent=2)

    print(f"  📊 Test results saved to: {test_result_log}")
    return test_data

def generate_comprehensive_report(session_id, logs_dir, test_results):
    """Generate comprehensive test report"""
    report_file = f"{logs_dir}/COMPREHENSIVE_TEST_REPORT.md"

    with open(report_file, "w") as f:
        f.write(f"# HR System Comprehensive Test Report\n\n")
        f.write(f"**Session ID**: {session_id}\n")
        f.write(f"**Generated**: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
        f.write(f"**Logs Directory**: `{logs_dir}`\n\n")

        f.write(f"## Test Summary\n\n")
        total_tests = len(test_results)
        successful_tests = sum(1 for result in test_results if result.get('result') == 'success')

        f.write(f"- **Total Tests**: {total_tests}\n")
        f.write(f"- **Successful**: {successful_tests}\n")
        f.write(f"- **Failed**: {total_tests - successful_tests}\n")
        f.write(f"- **Success Rate**: {(successful_tests/total_tests)*100:.1f}%\n\n")

        f.write(f"## Individual Agent Results\n\n")
        for result in test_results:
            agent_name = result['agent_name']
            port = result['port']
            status = result['result']

            if status == 'success':
                icon = "✅"
            elif status.startswith('success'):
                icon = "🟡"
            else:
                icon = "❌"

            f.write(f"### {icon} {agent_name} (Port {port})\n")
            f.write(f"- **Status**: {status}\n")
            f.write(f"- **API Calls**: {len(result['api_calls'])}\n")

            if 'response_content' in result:
                content = result['response_content'][:200]
                f.write(f"- **Response Preview**: {content}...\n")

            f.write(f"- **Detailed Logs**: `{logs_dir}/api_calls/{agent_name}_api_calls.log`\n")
            f.write(f"- **Test Data**: `{logs_dir}/test_results/{agent_name}_test.json`\n\n")

        f.write(f"## Log Files Reference\n\n")
        f.write(f"### System Status\n")
        f.write(f"- Component Status Log: `{logs_dir}/component_activity/system_status.log`\n")
        f.write(f"- Status JSON: `{logs_dir}/component_activity/status.json`\n\n")

        f.write(f"### API Call Logs\n")
        for result in test_results:
            agent_name = result['agent_name']
            f.write(f"- {agent_name}: `{logs_dir}/api_calls/{agent_name}_api_calls.log`\n")

        f.write(f"\n### Test Result Data\n")
        for result in test_results:
            agent_name = result['agent_name']
            f.write(f"- {agent_name}: `{logs_dir}/test_results/{agent_name}_test.json`\n")

        f.write(f"\n## How to Analyze Logs\n\n")
        f.write(f"```bash\n")
        f.write(f"# View system status\n")
        f.write(f"cat {logs_dir}/component_activity/system_status.log\n\n")
        f.write(f"# View API calls for specific agent\n")
        f.write(f"cat {logs_dir}/api_calls/job_requisition_agent_api_calls.log\n\n")
        f.write(f"# View test results\n")
        f.write(f"cat {logs_dir}/test_results/*.json | jq .\n\n")
        f.write(f"# Check which tools were called\n")
        f.write(f"grep -r 'Status: 200' {logs_dir}/api_calls/\n")
        f.write(f"```\n")

    print(f"\n📋 Comprehensive report generated: {report_file}")
    return report_file

def main():
    """Run comprehensive test with detailed logging"""
    session_id, logs_dir = create_test_session()

    # 1. Log system status
    print(f"📊 Logging system status...")
    status_data = log_component_status(logs_dir)

    # 2. Test sample agents with detailed logging
    agents_to_test = [
        {"name": "job_requisition_agent", "port": 5020},
        {"name": "sourcing_agent", "port": 5021},
        {"name": "acquisition_team_agent", "port": 5032}
    ]

    test_results = []
    for agent in agents_to_test:
        result = test_agent_with_logging(agent["name"], agent["port"], logs_dir)
        test_results.append(result)

    # 3. Generate comprehensive report
    report_file = generate_comprehensive_report(session_id, logs_dir, test_results)

    print(f"\n" + "=" * 80)
    print(f"🎉 COMPREHENSIVE TEST WITH LOGGING COMPLETE")
    print(f"=" * 80)
    print(f"📁 All logs and results: {logs_dir}")
    print(f"📋 Comprehensive report: {report_file}")
    print(f"🆔 Session ID: {session_id}")

    # Show quick summary
    successful_tests = sum(1 for result in test_results if result.get('result') == 'success')
    total_tests = len(test_results)
    print(f"📊 Success Rate: {successful_tests}/{total_tests} ({(successful_tests/total_tests)*100:.1f}%)")

    return logs_dir

if __name__ == "__main__":
    main()