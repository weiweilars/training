#!/usr/bin/env python3
"""
Test script to verify agent card updates work with configuration-driven agents
Tests both YAML configuration and dynamic tool management features
"""

import asyncio
import aiohttp
import json
from datetime import datetime

# ANSI color codes
class Colors:
    GREEN = '\033[92m'
    FAIL = '\033[91m'
    BLUE = '\033[94m'
    WARNING = '\033[93m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'

def print_success(msg):
    print(f"{Colors.GREEN}✅ {msg}{Colors.ENDC}")

def print_error(msg):
    print(f"{Colors.FAIL}❌ {msg}{Colors.ENDC}")

def print_info(msg):
    print(f"{Colors.BLUE}ℹ️  {msg}{Colors.ENDC}")

def print_warning(msg):
    print(f"{Colors.WARNING}⚠️  {msg}{Colors.ENDC}")

async def get_agent_card(session, port):
    """Get agent card from the specified port"""
    try:
        async with session.get(f"http://localhost:{port}/.well-known/agent-card.json") as response:
            if response.status == 200:
                return await response.json()
            else:
                print_error(f"Failed to get agent card: HTTP {response.status}")
                return None
    except Exception as e:
        print_error(f"Error getting agent card: {str(e)}")
        return None

async def add_tool(session, port, tool_url):
    """Add a tool to the agent"""
    payload = {
        "jsonrpc": "2.0",
        "method": "tools/add",
        "params": {"url": tool_url},
        "id": f"add-test-{port}"
    }
    
    try:
        async with session.post(f"http://localhost:{port}", json=payload) as response:
            if response.status == 200:
                result = await response.json()
                return result.get('result', {})
            else:
                print_error(f"Failed to add tool: HTTP {response.status}")
                return None
    except Exception as e:
        print_error(f"Error adding tool: {str(e)}")
        return None

async def remove_tool(session, port, tool_url):
    """Remove a tool from the agent"""
    payload = {
        "jsonrpc": "2.0",
        "method": "tools/remove",
        "params": {"url": tool_url},
        "id": f"remove-test-{port}"
    }
    
    try:
        async with session.post(f"http://localhost:{port}", json=payload) as response:
            if response.status == 200:
                result = await response.json()
                return result.get('result', {})
            else:
                print_error(f"Failed to remove tool: HTTP {response.status}")
                return None
    except Exception as e:
        print_error(f"Error removing tool: {str(e)}")
        return None

async def test_agent_card_updates():
    """Test that agent card is updated when tools are added/removed with config-driven agents"""
    
    print(f"{Colors.BOLD}🧪 Testing Configuration-Driven Agent Card Updates{Colors.ENDC}")
    print(f"Test started: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("="*70)
    
    # Test with the Weather Specialist Agent (configured via agentA.yaml)
    port = 5010
    print_info(f"Testing with Weather Specialist Agent (agentA.yaml) on port {port}")
    
    async with aiohttp.ClientSession() as session:
        
        # Step 1: Get initial agent card
        print_info("Step 1: Getting initial agent card...")
        initial_card = await get_agent_card(session, port)
        
        if not initial_card:
            print_error("Cannot get initial agent card. Is the agent running?")
            return
        
        initial_skills = [skill.get('name') for skill in initial_card.get('skills', [])]
        print_success(f"Initial skills: {initial_skills}")
        
        # Wait between steps to avoid model overload
        await asyncio.sleep(3)
        
        # Step 2: Add calculator tool
        print_info("Step 2: Adding calculator tool...")
        add_result = await add_tool(session, port, "http://localhost:8002/mcp")
        
        if add_result:
            print_success(f"Add tool result: {add_result}")
            
            # Wait a moment for the update to propagate
            await asyncio.sleep(2)
            
            # Get updated agent card
            updated_card = await get_agent_card(session, port)
            if updated_card:
                updated_skills = [skill.get('name') for skill in updated_card.get('skills', [])]
                print_success(f"Updated skills after adding: {updated_skills}")
                
                # Check if calculator tools were added
                calc_tools = ['basic_math', 'advanced_math', 'evaluate_expression']
                calc_tools_found = any(tool in updated_skills for tool in calc_tools)
                
                if calc_tools_found:
                    print_success("✨ Agent card successfully updated with new calculator tools!")
                else:
                    print_error("Agent card was not updated with calculator tools")
            else:
                print_error("Failed to get updated agent card")
        else:
            print_error("Failed to add tool")
        
        # Wait between steps to avoid model overload  
        await asyncio.sleep(3)
        
        # Step 3: Remove calculator tool
        print_info("Step 3: Removing calculator tool...")
        remove_result = await remove_tool(session, port, "http://localhost:8002/mcp")
        
        if remove_result:
            print_success(f"Remove tool result: {remove_result}")
            
            # Wait a moment for the update to propagate
            await asyncio.sleep(2)
            
            # Get final agent card
            final_card = await get_agent_card(session, port)
            if final_card:
                final_skills = [skill.get('name') for skill in final_card.get('skills', [])]
                print_success(f"Final skills after removing: {final_skills}")
                
                # Check if calculator tools were removed
                calc_tools = ['basic_math', 'advanced_math', 'evaluate_expression']
                calc_tools_found = any(tool in final_skills for tool in calc_tools)
                
                if not calc_tools_found:
                    print_success("✨ Agent card successfully updated - calculator tools removed!")
                else:
                    print_error("Agent card was not updated - calculator tools still present")
                    
                # Check if we're back to initial state
                if set(final_skills) == set(initial_skills):
                    print_success("🎉 Agent card restored to initial state!")
                else:
                    print_warning("Agent card differs from initial state")
            else:
                print_error("Failed to get final agent card")
        else:
            print_error("Failed to remove tool")
    
    print("="*70)
    print(f"Test completed: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")

if __name__ == "__main__":
    print("🚀 Make sure the Weather Specialist Agent is running on port 5010")
    print("   Run: python adk_a2a_server.py --config agentA.yaml --port 5010")
    print()
    
    try:
        asyncio.run(test_agent_card_updates())
    except Exception as e:
        print_error(f"Test failed with error: {e}")
        print("   Make sure the agent is running and accessible")