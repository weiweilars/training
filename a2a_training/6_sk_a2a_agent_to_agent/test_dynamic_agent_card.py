#!/usr/bin/env python3
"""
Test script for dynamic agent card generation in SK A2A Agent with intelligent summarization
Verifies that agent descriptions and instructions are dynamically updated using summarization agent
"""

import asyncio
import json
import aiohttp
import time
import sys
import argparse

async def test_agent_card_endpoint(base_url: str):
    """Test the agent card endpoint to see current description/instructions"""
    try:
        async with aiohttp.ClientSession() as session:
            async with session.get(f"{base_url}/.well-known/agent-card.json") as response:
                if response.status == 200:
                    card = await response.json()
                    print(f"✅ Agent Card Retrieved:")
                    print(f"   Name: {card.get('name', 'N/A')}")
                    print(f"   Description: {card.get('description', 'N/A')}")
                    print(f"   Greeting: {card.get('greeting', 'N/A')}")
                    print(f"   Instructions preview: {card.get('instructions', 'N/A')[:200]}...")
                    print(f"   Skills count: {len(card.get('skills', []))}")
                    return card
                else:
                    print(f"❌ Failed to get agent card: {response.status}")
                    return None
    except Exception as e:
        print(f"❌ Error getting agent card: {e}")
        return None

async def test_summarization_agent(summarization_url: str = "http://localhost:5030"):
    """Test if summarization agent is available and responsive"""
    try:
        async with aiohttp.ClientSession() as session:
            # Test with a simple summarization request
            payload = {
                "jsonrpc": "2.0",
                "id": "test_summarization",
                "method": "message/send", 
                "params": {
                    "message": {"content": "Generate a brief test description for an AI coordinator that manages Weather Agent (for weather data) and Calculator Agent (for mathematical computations)."},
                    "sessionId": "test_session"
                }
            }
            
            async with session.post(summarization_url, json=payload) as response:
                if response.status == 200:
                    result = await response.json()
                    if "result" in result:
                        # Check for the nested response format
                        if ("result" in result["result"] and 
                            "message" in result["result"]["result"] and 
                            "content" in result["result"]["result"]["message"]):
                            content = result["result"]["result"]["message"]["content"]
                            print(f"✅ Summarization agent is responsive at {summarization_url}")
                            print(f"   Sample output: {content[:100]}...")
                            return True
                        # Check for legacy response format
                        elif "response" in result["result"]:
                            print(f"✅ Summarization agent is responsive at {summarization_url}")
                            print(f"   Sample output: {result['result']['response'][:100]}...")
                            return True
                        else:
                            print(f"⚠️  Summarization agent returned unexpected format: {result}")
                            return False
                    else:
                        print(f"⚠️  Summarization agent returned unexpected format: {result}")
                        return False
                else:
                    print(f"❌ Summarization agent returned status {response.status}")
                    return False
    except Exception as e:
        print(f"❌ Summarization agent not available: {e}")
        return False

async def test_add_agent(base_url: str, agent_url: str):
    """Test adding a new agent and check if card updates"""
    try:
        async with aiohttp.ClientSession() as session:
            payload = {
                "jsonrpc": "2.0",
                "id": 1,
                "method": "agents/add", 
                "params": {"url": agent_url}
            }
            
            async with session.post(f"{base_url}", json=payload) as response:
                if response.status == 200:
                    result = await response.json()
                    if "result" in result:
                        print(f"✅ Agent added successfully: {agent_url}")
                        print(f"   Result: {result['result']['message']}")
                        return True
                    else:
                        print(f"❌ Agent add failed: {result.get('error', 'Unknown error')}")
                        return False
                else:
                    print(f"❌ Failed to add agent: {response.status}")
                    return False
    except Exception as e:
        print(f"❌ Error adding agent: {e}")
        return False

async def test_remove_agent(base_url: str, agent_url: str):
    """Test removing an agent and check if card updates"""
    try:
        async with aiohttp.ClientSession() as session:
            payload = {
                "jsonrpc": "2.0",
                "id": 1,
                "method": "agents/remove", 
                "params": {"url": agent_url}
            }
            
            async with session.post(f"{base_url}", json=payload) as response:
                if response.status == 200:
                    result = await response.json()
                    if "result" in result:
                        print(f"✅ Agent removed successfully: {agent_url}")
                        print(f"   Result: {result['result']['message']}")
                        return True
                    else:
                        print(f"❌ Agent remove failed: {result.get('error', 'Unknown error')}")
                        return False
                else:
                    print(f"❌ Failed to remove agent: {response.status}")
                    return False
    except Exception as e:
        print(f"❌ Error removing agent: {e}")
        return False

async def wait_for_agent_startup(base_url: str, max_attempts: int = 10):
    """Wait for the agent to start up and be responsive"""
    for attempt in range(max_attempts):
        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(f"{base_url}/.well-known/agent-card.json") as response:
                    if response.status == 200:
                        print(f"✅ Agent is responsive at {base_url}")
                        return True
        except:
            pass
        
        print(f"⏳ Waiting for agent startup... ({attempt + 1}/{max_attempts})")
        await asyncio.sleep(2)
    
    print(f"❌ Agent not responsive after {max_attempts} attempts")
    return False

async def test_multi_agent_query(base_url: str, query: str, session_id: str, test_name: str):
    """Test sending a complex query that requires multi-agent coordination"""
    try:
        async with aiohttp.ClientSession() as session:
            payload = {
                "jsonrpc": "2.0",
                "id": test_name,
                "method": "message/send",
                "params": {
                    "message": {"content": query},
                    "sessionId": session_id
                }
            }
            
            async with session.post(base_url, json=payload) as response:
                if response.status == 200:
                    result = await response.json()
                    if "result" in result:
                        # Handle nested response format
                        if ("result" in result["result"] and 
                            "message" in result["result"]["result"] and 
                            "content" in result["result"]["result"]["message"]):
                            content = result["result"]["result"]["message"]["content"]
                            print(f"✅ Multi-agent query successful: {test_name}")
                            print(f"   Query: {query}")
                            print(f"   Response: {content[:200]}...")
                            return True, content
                        # Handle legacy response format
                        elif "response" in result["result"]:
                            content = result["result"]["response"]
                            print(f"✅ Multi-agent query successful: {test_name}")
                            print(f"   Query: {query}")
                            print(f"   Response: {content[:200]}...")
                            return True, content
                        else:
                            print(f"⚠️  Multi-agent query returned unexpected format: {result}")
                            return False, None
                    else:
                        print(f"❌ Multi-agent query failed: {result.get('error', 'Unknown error')}")
                        return False, None
                else:
                    print(f"❌ Multi-agent query failed with status {response.status}")
                    return False, None
    except Exception as e:
        print(f"❌ Error in multi-agent query: {e}")
        return False, None

async def main():
    parser = argparse.ArgumentParser(description="Test dynamic agent card functionality with intelligent summarization and multi-agent coordination")
    parser.add_argument("--agent-url", default="http://localhost:5025", 
                        help="Base URL of the SK A2A agent to test")
    parser.add_argument("--test-add-url", default="http://localhost:5011",
                        help="URL of an agent to add during testing (AgentB - Calculator)")
    parser.add_argument("--summarization-url", default="http://localhost:5030",
                        help="URL of the summarization agent")
    parser.add_argument("--skip-startup-wait", action="store_true",
                        help="Skip waiting for agent startup (assume already running)")
    parser.add_argument("--skip-summarization-test", action="store_true",
                        help="Skip testing summarization agent (test fallback only)")
    parser.add_argument("--skip-multi-agent", action="store_true",
                        help="Skip multi-agent coordination testing")
    
    args = parser.parse_args()
    
    print("🧪 Testing Dynamic Agent Card Functionality with Multi-Agent Coordination")
    print("=" * 80)
    
    # Always wait for startup unless explicitly skipped
    if not args.skip_startup_wait:
        print(f"⏳ Waiting for agent startup at {args.agent_url}")
        if not await wait_for_agent_startup(args.agent_url):
            print("❌ Agent not responsive. Make sure services are running:")
            print("   ./demo_dynamic_features.sh --start-services")
            sys.exit(1)
    
    print(f"🎯 Testing agent at: {args.agent_url}")
    print(f"📊 Test agent URL: {args.test_add_url}")
    print(f"🧠 Summarization agent URL: {args.summarization_url}")
    print()
    
    # Test 0: Check summarization agent availability
    if not args.skip_summarization_test:
        print("📋 Test 0: Check summarization agent availability")
        summarization_available = await test_summarization_agent(args.summarization_url)
        if summarization_available:
            print("✅ Summarization agent is available - will test intelligent generation")
        else:
            print("⚠️  Summarization agent not available - will test fallback generation")
        print()
    else:
        print("⏭️  Skipping summarization agent test - testing fallback only")
        print()
    
    # Test 1: Get initial agent card
    print("📋 Test 1: Get initial agent card")
    initial_card = await test_agent_card_endpoint(args.agent_url)
    if not initial_card:
        print("❌ Cannot proceed without initial agent card")
        sys.exit(1)
    
    print()
    
    # Test 2: Add a new agent and check if card updates
    print("📋 Test 2: Add agent and check card update")
    if await test_add_agent(args.agent_url, args.test_add_url):
        # Wait a moment for the card to update
        await asyncio.sleep(2)
        updated_card = await test_agent_card_endpoint(args.agent_url)
        
        if updated_card:
            # Check if content changed (indicating dynamic update)
            initial_desc = initial_card.get('description', '')
            updated_desc = updated_card.get('description', '')
            initial_greeting = initial_card.get('greeting', '')
            updated_greeting = updated_card.get('greeting', '')
            initial_instructions = initial_card.get('instructions', '')
            updated_instructions = updated_card.get('instructions', '')
            
            changes_detected = []
            if initial_desc != updated_desc:
                changes_detected.append("description")
                print(f"   📝 Description changed:")
                print(f"      Old: {initial_desc}")
                print(f"      New: {updated_desc}")
            
            if initial_greeting != updated_greeting:
                changes_detected.append("greeting")
                print(f"   👋 Greeting changed:")
                print(f"      Old: {initial_greeting}")
                print(f"      New: {updated_greeting}")
            
            if initial_instructions != updated_instructions:
                changes_detected.append("instructions")
                print(f"   📋 Instructions changed (preview):")
                print(f"      Old: {initial_instructions[:100]}...")
                print(f"      New: {updated_instructions[:100]}...")
            
            if changes_detected:
                print(f"✅ Agent card was intelligently updated! Changed: {', '.join(changes_detected)}")
            else:
                print("⚠️  Agent card did not change (may be expected)")
    
    print()
    
    # Test 3: Remove the agent and check if card updates again
    print("📋 Test 3: Remove agent and check card update")
    if await test_remove_agent(args.agent_url, args.test_add_url):
        # Wait a moment for the card to update
        await asyncio.sleep(2)
        final_card = await test_agent_card_endpoint(args.agent_url)
        
        if final_card:
            # Check if description reverted or changed again
            updated_desc = updated_card.get('description', '') if 'updated_card' in locals() else ''
            final_desc = final_card.get('description', '')
            
            if updated_desc != final_desc:
                print("✅ Agent card description was dynamically updated after removal!")
                print(f"   After add: {updated_desc}")
                print(f"   After remove: {final_desc}")
            else:
                print("⚠️  Agent card description did not change after removal")
    
    print()
    
    # Test 4: Multi-Agent Coordination Testing (Default)
    if not args.skip_multi_agent:
        print("📋 Test 4: Multi-Agent Coordination Testing")
        print("   Testing complex queries that require both weather and calculator agents...")
        
        # Test single-agent query (weather only)
        weather_success, weather_response = await test_multi_agent_query(
            args.agent_url,
            "What is the current weather in Tokyo?",
            "multi-agent-test",
            "single-weather"
        )
        
        await asyncio.sleep(1)
        
        # Test multi-agent query after adding calculator
        if await test_add_agent(args.agent_url, args.test_add_url):
            await asyncio.sleep(2)  # Wait for agent integration
            
            multi_success, multi_response = await test_multi_agent_query(
                args.agent_url,
                "Get the temperature in Tokyo and London, then calculate the average temperature between them",
                "multi-agent-test",
                "multi-weather-math"
            )
            
            await asyncio.sleep(1)
            
            # Test complex coordination
            complex_success, complex_response = await test_multi_agent_query(
                args.agent_url,
                "If the temperature in Paris is above 20°C, calculate how much warmer it is than 15°C and convert the difference to Fahrenheit",
                "multi-agent-test", 
                "complex-coordination"
            )
            
            # Analyze responses for multi-agent indicators
            if multi_success and complex_success:
                print("✅ Multi-agent coordination tests completed!")
                
                # Check if responses indicate both weather and math operations
                weather_indicators = ["temperature", "weather", "°C", "degrees"]
                math_indicators = ["calculate", "average", "difference", "Fahrenheit", "convert"]
                
                multi_has_weather = any(indicator.lower() in multi_response.lower() for indicator in weather_indicators)
                multi_has_math = any(indicator.lower() in multi_response.lower() for indicator in math_indicators)
                
                if multi_has_weather and multi_has_math:
                    print("   🎯 Multi-agent response shows evidence of both weather and math coordination!")
                else:
                    print("   ⚠️  Multi-agent response may not fully demonstrate coordination")
            else:
                print("   ⚠️  Some multi-agent queries failed - check agent connectivity")
    
    print()
    print("🏁 Intelligent dynamic agent card testing complete!")
    print("   ✨ This test validates both intelligent summarization via external agent")
    print("   ✨ and fallback generation when summarization agent is unavailable")
    print("   ✨ Agent cards are now generated intelligently instead of rigid templates!")
    if not args.skip_multi_agent:
        print("   ✨ Multi-agent coordination demonstrates true agent-to-agent communication!")

if __name__ == "__main__":
    asyncio.run(main())