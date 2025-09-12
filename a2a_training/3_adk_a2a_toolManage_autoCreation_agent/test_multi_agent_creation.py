#!/usr/bin/env python3
"""
Test script for verifying multiple agent creation with different YAML configurations

This test:
1. Starts three different agents with different YAML configs
2. Verifies each agent has correct identity (name, ID, description)
3. Checks that each agent has the correct tools attached
4. Tests agent-specific behaviors and responses
"""

import subprocess
import asyncio
import aiohttp
import json
import time
import sys
import os
from datetime import datetime
from typing import Dict, List, Any, Optional

# ANSI color codes
class Colors:
    HEADER = '\033[95m'
    BLUE = '\033[94m'
    CYAN = '\033[96m'
    GREEN = '\033[92m'
    WARNING = '\033[93m'
    FAIL = '\033[91m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'

def print_header(msg: str):
    print(f"\n{Colors.HEADER}{Colors.BOLD}{'='*70}{Colors.ENDC}")
    print(f"{Colors.HEADER}{Colors.BOLD}{msg}{Colors.ENDC}")
    print(f"{Colors.HEADER}{Colors.BOLD}{'='*70}{Colors.ENDC}")

def print_section(msg: str):
    print(f"\n{Colors.CYAN}{Colors.BOLD}{msg}{Colors.ENDC}")
    print(f"{Colors.CYAN}{'-'*len(msg)}{Colors.ENDC}")

def print_success(msg: str):
    print(f"{Colors.GREEN}✅ {msg}{Colors.ENDC}")

def print_error(msg: str):
    print(f"{Colors.FAIL}❌ {msg}{Colors.ENDC}")

def print_info(msg: str):
    print(f"{Colors.BLUE}ℹ️  {msg}{Colors.ENDC}")

def print_warning(msg: str):
    print(f"{Colors.WARNING}⚠️  {msg}{Colors.ENDC}")

class AgentManager:
    """Manages starting and stopping agent processes"""
    
    def __init__(self):
        self.processes = {}
        
    def start_agent(self, config_file: str, port: int, name: str) -> bool:
        """Start an agent with the specified configuration"""
        try:
            cmd = [
                sys.executable,
                "adk_a2a_server.py",
                "--config", config_file,
                "--port", str(port)
            ]
            
            print_info(f"Starting {name} on port {port}...")
            print_info(f"Command: {' '.join(cmd)}")
            
            # Start the process
            process = subprocess.Popen(
                cmd,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True
            )
            
            self.processes[name] = process
            
            # Give it time to start
            time.sleep(5)
            
            # Check if it's still running
            if process.poll() is None:
                print_success(f"{name} started successfully (PID: {process.pid})")
                return True
            else:
                stdout, stderr = process.communicate(timeout=1)
                print_error(f"{name} failed to start")
                if stderr:
                    print_error(f"Error: {stderr[:200]}")
                return False
                
        except Exception as e:
            print_error(f"Failed to start {name}: {str(e)}")
            return False
    
    def stop_all(self):
        """Stop all running agents"""
        for name, process in self.processes.items():
            if process.poll() is None:
                print_info(f"Stopping {name}...")
                process.terminate()
                try:
                    process.wait(timeout=5)
                except subprocess.TimeoutExpired:
                    process.kill()
                print_success(f"{name} stopped")

async def verify_agent_card(port: int, expected_config: Dict[str, Any]) -> Dict[str, bool]:
    """Verify agent card matches expected configuration"""
    results = {
        'accessible': False,
        'id_match': False,
        'name_match': False,
        'description_exists': False,
        'greeting_exists': False,
        'tools_correct': False
    }
    
    url = f"http://localhost:{port}/.well-known/agent-card.json"
    
    async with aiohttp.ClientSession() as session:
        try:
            async with session.get(url) as response:
                if response.status == 200:
                    results['accessible'] = True
                    agent_card = await response.json()
                    
                    # Verify ID
                    if agent_card.get('id') == expected_config['id']:
                        results['id_match'] = True
                        print_success(f"  ID matches: {expected_config['id']}")
                    else:
                        print_error(f"  ID mismatch: expected '{expected_config['id']}', got '{agent_card.get('id')}'")
                    
                    # Verify name
                    if agent_card.get('name') == expected_config['name']:
                        results['name_match'] = True
                        print_success(f"  Name matches: {expected_config['name']}")
                    else:
                        print_error(f"  Name mismatch: expected '{expected_config['name']}', got '{agent_card.get('name')}'")
                    
                    # Verify description
                    if agent_card.get('description'):
                        results['description_exists'] = True
                        desc_preview = agent_card['description'][:80] + "..." if len(agent_card['description']) > 80 else agent_card['description']
                        print_success(f"  Description: {desc_preview}")
                    else:
                        print_warning("  Description missing")
                    
                    # Verify greeting
                    if agent_card.get('greeting'):
                        results['greeting_exists'] = True
                        greeting_preview = agent_card['greeting'][:80] + "..." if len(agent_card['greeting']) > 80 else agent_card['greeting']
                        print_success(f"  Greeting: {greeting_preview}")
                    else:
                        print_warning("  Greeting missing")
                    
                    # Verify tools/skills
                    skills = agent_card.get('skills', [])
                    skill_names = [skill.get('name', '') for skill in skills]
                    
                    # Check if expected tool types are reflected
                    tools_ok = True
                    for tool_type in expected_config['tools']:
                        if tool_type == 'weather':
                            if not any('weather' in name.lower() or 'temperature' in name.lower() for name in skill_names):
                                print_warning(f"  Weather tools not found in skills")
                                tools_ok = False
                        elif tool_type == 'file':
                            if not any('file' in name.lower() or 'list' in name.lower() or 'read' in name.lower() for name in skill_names):
                                print_warning(f"  File tools not found in skills")
                                tools_ok = False
                    
                    if tools_ok:
                        results['tools_correct'] = True
                        print_success(f"  Tools/Skills: {skill_names}")
                    
                else:
                    print_error(f"  Failed to access agent card: HTTP {response.status}")
                    
        except aiohttp.ClientError as e:
            print_error(f"  Cannot connect to agent on port {port}: {str(e)}")
        except Exception as e:
            print_error(f"  Error verifying agent card: {str(e)}")
    
    return results

async def test_agent_functionality(port: int, test_query: str, expected_keywords: List[str]) -> bool:
    """Test if agent responds appropriately to queries"""
    async with aiohttp.ClientSession() as session:
        try:
            # Send test message
            payload = {
                "jsonrpc": "2.0",
                "method": "message/send",
                "params": {
                    "message": {"content": test_query},
                    "sessionId": f"test-{port}-{int(time.time())}"
                },
                "id": f"test-{port}"
            }
            
            async with session.post(f"http://localhost:{port}", json=payload) as response:
                if response.status == 200:
                    result = await response.json()
                    task_id = result.get('result', {}).get('taskId')
                    
                    if task_id:
                        print_info(f"  Task created: {task_id}")
                        
                        # Wait for task completion
                        await asyncio.sleep(5)
                        
                        # Get task result
                        get_payload = {
                            "jsonrpc": "2.0",
                            "method": "tasks/get",
                            "params": {"taskId": task_id},
                            "id": f"get-{port}"
                        }
                        
                        async with session.post(f"http://localhost:{port}", json=get_payload) as response:
                            task_result = await response.json()
                            message = task_result.get('result', {}).get('result', {}).get('message', {}).get('content', '')
                            
                            if message:
                                # Check for expected keywords
                                found_keywords = [kw for kw in expected_keywords if kw.lower() in message.lower()]
                                
                                if found_keywords:
                                    print_success(f"  Response contains expected keywords: {found_keywords}")
                                    print_info(f"  Response preview: {message[:150]}...")
                                    return True
                                else:
                                    print_warning(f"  Response doesn't contain expected keywords")
                                    print_info(f"  Expected: {expected_keywords}")
                                    print_info(f"  Response: {message[:150]}...")
                                    return False
                            else:
                                print_error("  No response content")
                                return False
                    else:
                        print_error("  No task ID returned")
                        return False
                else:
                    print_error(f"  Failed to send message: HTTP {response.status}")
                    return False
                    
        except Exception as e:
            print_error(f"  Error testing functionality: {str(e)}")
            return False

async def run_tests():
    """Main test runner"""
    print_header("Multi-Agent Creation Test Suite")
    print(f"Test started: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    # Agent configurations
    agents = [
        {
            'config_file': 'agentA.yaml',
            'port': 5010,
            'name': 'Weather Specialist Agent',
            'id': 'weather-specialist-agent',
            'tools': ['weather'],
            'test_query': 'What is the weather in Paris?',
            'expected_keywords': ['weather', 'temperature', 'paris']
        },
        {
            'config_file': 'agentB.yaml',
            'port': 5011,
            'name': 'File Management Agent',
            'id': 'file-manager-agent',
            'tools': ['file'],
            'test_query': 'Can you list files in the current directory?',
            'expected_keywords': ['file', 'directory', 'list']
        },
        {
            'config_file': 'agentC.yaml',
            'port': 5012,
            'name': 'Multi-Tool Assistant',
            'id': 'multi-tool-assistant',
            'tools': ['weather', 'file'],
            'test_query': 'What tools do you have available?',
            'expected_keywords': ['weather', 'file', 'tool']
        }
    ]
    
    # Start agent manager
    manager = AgentManager()
    
    try:
        # Phase 1: Start all agents
        print_header("Phase 1: Starting Agents")
        
        start_results = {}
        for agent in agents:
            success = manager.start_agent(
                agent['config_file'],
                agent['port'],
                agent['name']
            )
            start_results[agent['name']] = success
            
            if not success:
                print_warning(f"Skipping tests for {agent['name']} as it failed to start")
        
        # Wait for all agents to fully initialize
        print_info("\nWaiting for agents to fully initialize...")
        await asyncio.sleep(5)
        
        # Phase 2: Verify agent cards
        print_header("Phase 2: Verifying Agent Cards")
        
        card_results = {}
        for agent in agents:
            if start_results.get(agent['name'], False):
                print_section(f"Verifying {agent['name']} (port {agent['port']})")
                results = await verify_agent_card(agent['port'], agent)
                card_results[agent['name']] = results
        
        # Phase 3: Test agent functionality
        print_header("Phase 3: Testing Agent Functionality")
        
        func_results = {}
        for agent in agents:
            if start_results.get(agent['name'], False):
                print_section(f"Testing {agent['name']} (port {agent['port']})")
                print_info(f"  Query: {agent['test_query']}")
                success = await test_agent_functionality(
                    agent['port'],
                    agent['test_query'],
                    agent['expected_keywords']
                )
                func_results[agent['name']] = success
        
        # Phase 4: Summary
        print_header("Test Results Summary")
        
        all_passed = True
        for agent in agents:
            name = agent['name']
            print(f"\n{Colors.BOLD}{name}:{Colors.ENDC}")
            
            # Start status
            if start_results.get(name, False):
                print(f"  {Colors.GREEN}✅ Started successfully{Colors.ENDC}")
            else:
                print(f"  {Colors.FAIL}❌ Failed to start{Colors.ENDC}")
                all_passed = False
                continue
            
            # Card verification
            if name in card_results:
                card = card_results[name]
                passed = all([
                    card['accessible'],
                    card['id_match'],
                    card['name_match'],
                    card['description_exists']
                ])
                if passed:
                    print(f"  {Colors.GREEN}✅ Agent card verified{Colors.ENDC}")
                else:
                    print(f"  {Colors.WARNING}⚠️  Agent card issues{Colors.ENDC}")
                    all_passed = False
            
            # Functionality test
            if name in func_results:
                if func_results[name]:
                    print(f"  {Colors.GREEN}✅ Functionality test passed{Colors.ENDC}")
                else:
                    print(f"  {Colors.WARNING}⚠️  Functionality test issues{Colors.ENDC}")
                    all_passed = False
        
        print("\n" + "="*70)
        if all_passed:
            print(f"{Colors.GREEN}{Colors.BOLD}🎉 ALL TESTS PASSED!{Colors.ENDC}")
            print(f"{Colors.GREEN}All agents were created correctly with their respective YAML configurations!{Colors.ENDC}")
        else:
            print(f"{Colors.WARNING}{Colors.BOLD}⚠️  Some tests had issues{Colors.ENDC}")
            print(f"{Colors.WARNING}Please check the logs above for details{Colors.ENDC}")
        
    finally:
        # Clean up
        print_header("Cleanup")
        manager.stop_all()
        print_success("All agents stopped")
    
    print(f"\nTest completed: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")

if __name__ == "__main__":
    # Check if we're in the right directory
    required_files = ['agentA.yaml', 'agentB.yaml', 'agentC.yaml', 'adk_a2a_server.py']
    missing_files = [f for f in required_files if not os.path.exists(f)]
    
    if missing_files:
        print_error(f"Missing required files: {missing_files}")
        print_error("Please run this script from the directory containing the agent YAML files")
        sys.exit(1)
    
    # Check if MCP tools are running
    print_header("Pre-flight Checks")
    print_info("Checking if MCP tools are running...")
    print_info("Expected: Weather tool on port 8004, File tool on port 8003")
    print_warning("If not running, start them with:")
    print("  cd ../mcp_training")
    print("  python run_http.py weather --port 8004")
    print("  python run_http.py file --port 8003")
    
    input("\nPress Enter to continue with the test...")
    
    # Run the tests
    asyncio.run(run_tests())