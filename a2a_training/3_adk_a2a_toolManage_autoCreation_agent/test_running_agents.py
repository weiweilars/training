#!/usr/bin/env python3
"""
Simple test script for testing already-running agents

This test assumes all agents are already running and tests:
1. Agent connectivity and responsiveness
2. Agent card information
3. Basic functionality of each agent
4. Multi-tool capabilities

Prerequisites: Run these commands first:
cd ../mcp_training
python run_http.py weather --port 8001 &
python run_http.py calculator --port 8002 &

cd ../3_adk_a2a_toolManage_autoCreation_agent  
python adk_a2a_server.py --config agentA.yaml &  # Port 5010
python adk_a2a_server.py --config agentB.yaml &  # Port 5011
python adk_a2a_server.py --config agentC.yaml &  # Port 5012
"""

import asyncio
import aiohttp
import json
import time
from datetime import datetime

# ANSI color codes
class Colors:
    GREEN = '\033[92m'
    RED = '\033[91m'
    BLUE = '\033[94m'
    YELLOW = '\033[93m'
    CYAN = '\033[96m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'

def print_success(msg: str):
    print(f"{Colors.GREEN}✅ {msg}{Colors.ENDC}")

def print_error(msg: str):
    print(f"{Colors.RED}❌ {msg}{Colors.ENDC}")

def print_info(msg: str):
    print(f"{Colors.BLUE}ℹ️  {msg}{Colors.ENDC}")

def print_warning(msg: str):
    print(f"{Colors.YELLOW}⚠️  {msg}{Colors.ENDC}")

def print_header(msg: str):
    print(f"\n{Colors.CYAN}{Colors.BOLD}{'='*60}{Colors.ENDC}")
    print(f"{Colors.CYAN}{Colors.BOLD}{msg}{Colors.ENDC}")
    print(f"{Colors.CYAN}{Colors.BOLD}{'='*60}{Colors.ENDC}")

class AgentTester:
    def __init__(self):
        self.agents = {
            "Weather Specialist": {
                "port": 5010,
                "expected_id": "weather-specialist-agent",
                "test_query": "What is the weather like in Paris?"
            },
            "Calculator Specialist": {
                "port": 5011,
                "expected_id": "calculator-specialist-agent",
                "test_query": "Calculate 25 multiplied by 4, then add 10 to the result"
            },
            "Multi-Tool Assistant": {
                "port": 5012,
                "expected_id": "multi-tool-assistant",
                "test_query": "Get the weather in Tokyo and calculate the average if the temperature is 25 degrees"
            }
        }
        self.session = None
        self.results = {}

    async def __aenter__(self):
        self.session = aiohttp.ClientSession()
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        if self.session:
            await self.session.close()

    async def check_agent_card(self, agent_name: str, port: int) -> bool:
        """Check if agent is running and get its card"""
        try:
            url = f"http://localhost:{port}/.well-known/agent-card.json"
            async with self.session.get(url, timeout=5) as response:
                if response.status == 200:
                    card = await response.json()
                    agent_id = card.get('id', 'unknown')
                    expected_id = self.agents[agent_name]['expected_id']
                    
                    if agent_id == expected_id:
                        print_success(f"{agent_name} is running (ID: {agent_id})")
                        return True
                    else:
                        print_error(f"{agent_name} ID mismatch: expected {expected_id}, got {agent_id}")
                        return False
                else:
                    print_error(f"{agent_name} returned status {response.status}")
                    return False
        except Exception as e:
            print_error(f"{agent_name} not accessible: {e}")
            return False

    async def send_message(self, agent_name: str, port: int, message: str) -> dict:
        """Send a message to an agent and get response"""
        try:
            url = f"http://localhost:{port}"
            payload = {
                "jsonrpc": "2.0",
                "method": "message/send",
                "params": {
                    "message": {"content": message},
                    "sessionId": f"test-{agent_name.lower().replace(' ', '-')}-{int(time.time())}"
                },
                "id": f"test-{int(time.time())}"
            }
            
            async with self.session.post(url, json=payload, timeout=30) as response:
                if response.status == 200:
                    result = await response.json()
                    if 'result' in result and 'content' in result['result']:
                        return {
                            "success": True,
                            "content": result['result']['content'],
                            "response": result
                        }
                    else:
                        return {
                            "success": False,
                            "error": f"Unexpected response format: {result}"
                        }
                else:
                    text = await response.text()
                    return {
                        "success": False,
                        "error": f"HTTP {response.status}: {text}"
                    }
        except Exception as e:
            return {
                "success": False,
                "error": f"Request failed: {e}"
            }

    async def test_agent_functionality(self, agent_name: str, port: int, query: str):
        """Test basic functionality of an agent"""
        print_info(f"Testing {agent_name} with query: '{query}'")
        
        result = await self.send_message(agent_name, port, query)
        
        if result["success"]:
            content = result["content"]
            print_success(f"{agent_name} responded successfully")
            print(f"   Response: {content[:100]}{'...' if len(content) > 100 else ''}")
            
            # Check for tool usage indicators
            response_lower = content.lower()
            if any(keyword in response_lower for keyword in ['temperature', 'weather', 'degrees', 'celsius', 'fahrenheit']):
                print_info(f"   ✓ {agent_name} appears to be using weather tools")
            
            if any(keyword in response_lower for keyword in ['calculate', 'result', 'equals', 'math', 'multiply', 'add']):
                print_info(f"   ✓ {agent_name} appears to be using calculator tools")
                
            return True
        else:
            print_error(f"{agent_name} failed: {result['error']}")
            return False

    async def test_multi_tool_capability(self):
        """Test the multi-tool agent's ability to use both weather and calculator tools"""
        print_info("Testing Multi-Tool Assistant with complex query requiring both tools...")
        
        query = "Get the weather temperatures for both Paris and Tokyo, then calculate the average temperature between them"
        result = await self.send_message("Multi-Tool Assistant", 5012, query)
        
        if result["success"]:
            content = result["content"]
            response_lower = content.lower()
            
            has_weather = any(keyword in response_lower for keyword in ['paris', 'tokyo', 'temperature', 'weather', 'degrees'])
            has_math = any(keyword in response_lower for keyword in ['average', 'calculate', 'result', 'divided'])
            
            if has_weather and has_math:
                print_success("Multi-Tool Assistant successfully used both weather and calculator tools")
                print(f"   Response: {content[:150]}{'...' if len(content) > 150 else ''}")
                return True
            else:
                print_warning(f"Multi-Tool Assistant may not have used both tools (weather: {has_weather}, math: {has_math})")
                print(f"   Response: {content[:150]}{'...' if len(content) > 150 else ''}")
                return False
        else:
            print_error(f"Multi-Tool Assistant failed: {result['error']}")
            return False

    async def run_tests(self):
        """Run all tests"""
        print_header("Agent Connectivity Test")
        
        # Test 1: Check if all agents are running
        connectivity_results = {}
        for agent_name, config in self.agents.items():
            connectivity_results[agent_name] = await self.check_agent_card(agent_name, config["port"])
        
        # Test 2: Test basic functionality
        print_header("Agent Functionality Test")
        functionality_results = {}
        
        for agent_name, config in self.agents.items():
            if connectivity_results[agent_name]:
                functionality_results[agent_name] = await self.test_agent_functionality(
                    agent_name, config["port"], config["test_query"]
                )
            else:
                print_warning(f"Skipping functionality test for {agent_name} (not connected)")
                functionality_results[agent_name] = False
        
        # Test 3: Multi-tool capability test
        print_header("Multi-Tool Capability Test")
        multi_tool_success = False
        if connectivity_results.get("Multi-Tool Assistant", False):
            multi_tool_success = await self.test_multi_tool_capability()
        else:
            print_warning("Skipping multi-tool test (Multi-Tool Assistant not connected)")
        
        # Test Results Summary
        print_header("Test Results Summary")
        
        all_connected = all(connectivity_results.values())
        all_functional = all(functionality_results.values())
        
        for agent_name in self.agents.keys():
            connected = connectivity_results.get(agent_name, False)
            functional = functionality_results.get(agent_name, False)
            
            status = "✅ PASS" if connected and functional else "❌ FAIL"
            print(f"{agent_name}: {status}")
            if not connected:
                print(f"   - Not connected")
            elif not functional:
                print(f"   - Connected but not functional")
        
        print(f"\nMulti-Tool Test: {'✅ PASS' if multi_tool_success else '❌ FAIL'}")
        
        overall_success = all_connected and all_functional and multi_tool_success
        print(f"\n{'🎉 ALL TESTS PASSED!' if overall_success else '⚠️  SOME TESTS FAILED'}")
        
        if not overall_success:
            print("\nTo start the agents:")
            print("cd ../mcp_training")
            print("python run_http.py weather --port 8004 &")
            print("python run_http.py calculator --port 8005 &")
            print("cd ../5_sk_a2a_custom_mcp_agent")
            print("python sk_a2a_server.py --config agentA.yaml &")
            print("python sk_a2a_server.py --config agentB.yaml &")
            print("python sk_a2a_server.py --config agentC.yaml &")

async def main():
    print_header(f"SK A2A Agent Test Suite - {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print_info("Testing already-running agents...")
    
    async with AgentTester() as tester:
        await tester.run_tests()

if __name__ == "__main__":
    asyncio.run(main())