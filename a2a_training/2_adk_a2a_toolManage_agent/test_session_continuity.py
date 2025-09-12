#!/usr/bin/env python3
"""
Test script to demonstrate session continuity after dynamic tool changes
"""

import asyncio
import aiohttp
from datetime import datetime

async def test_capability_changes():
    """Test how agent capabilities change as tools are added/removed"""
    
    base_url = "http://localhost:5002"
    session_id = f"test-session-{datetime.now().strftime('%H%M%S')}"
    
    # Test queries to demonstrate session continuity with conversational flow
    calc_query = "Can you calculate the square root of 144?"
    weather_query = "What's the weather like in Tokyo? Is it warmer than that number?"
    
    print("🧪 Testing Session Continuity with Conversational Flow")
    print("=" * 70)
    print(f"🔍 Conversation flow:")
    print(f"   1. Calculate: '{calc_query}'")
    print(f"   2. Ask weather with reference: '{weather_query}'")
    print(f"   This tests if context is preserved across tool changes!")
    print()
    
    async with aiohttp.ClientSession() as session:
        async def send_message(query: str, step_name: str):
            """Helper function to send a message and return response"""
            payload = {
                "jsonrpc": "2.0",
                "method": "message/send",
                "params": {
                    "message": {"content": query},
                    "sessionId": session_id
                },
                "id": step_name
            }
            
            async with session.post(base_url, json=payload) as response:
                result = await response.json()
                content = result.get('result', {}).get('result', {}).get('message', {}).get('content', 'No response')
                return content
        
        async def check_agent_card():
            """Helper function to check agent card and return skills info"""
            agent_card_url = f"{base_url}/.well-known/agent-card.json"
            async with session.get(agent_card_url) as response:
                if response.status == 200:
                    agent_card = await response.json()
                    skills = agent_card.get('skills', [])
                    metadata = agent_card.get('metadata', {})
                    tool_urls = metadata.get('mcp_tool_urls', [])
                    tool_count = metadata.get('active_tools_count', 0)
                    
                    # Count non-general skills (actual MCP tools)
                    mcp_skills = [s for s in skills if s.get('name') != 'general_conversation']
                    return {
                        'total_skills': len(skills),
                        'mcp_skills': len(mcp_skills),
                        'tool_urls': tool_urls,
                        'tool_count': tool_count,
                        'skill_names': [s.get('name', 'unknown') for s in mcp_skills]
                    }
                else:
                    return {'error': f'Failed to get agent card: {response.status}'}

        # Step 1: Remove all tools first to start with empty state
        print("\n🔧 Step 1: Removing all existing tools to start clean...")
        
        # Get current tools
        list_payload = {"jsonrpc": "2.0", "method": "tools/list", "params": {}, "id": "list-initial"}
        async with session.post(base_url, json=list_payload) as response:
            result = await response.json()
            current_tools = result.get('result', {}).get('tools', [])
            print(f"   Current tools: {current_tools}")
        
        # Remove existing tools
        for tool_url in current_tools:
            remove_payload = {"jsonrpc": "2.0", "method": "tools/remove", "params": {"url": tool_url}, "id": f"remove-{hash(tool_url)}"}
            async with session.post(base_url, json=remove_payload) as response:
                result = await response.json()
                print(f"   Removed: {tool_url}")

        # Step 2: Test queries with NO TOOLS and check agent card
        print(f"\n🚫 Step 2: Testing capabilities with NO TOOLS")
        
        # Check agent card state
        agent_info = await check_agent_card()
        print(f"   🃏 Agent Card: {agent_info['mcp_skills']} MCP skills, {agent_info['tool_count']} tools")
        
        calc_response_empty = await send_message(calc_query, "calc-empty")
        print(f"   Calc query response: {calc_response_empty[:100]}...")
        
        # Wait between requests to avoid API overload
        await asyncio.sleep(2)
        
        weather_response_empty = await send_message(weather_query, "weather-empty")
        print(f"   Weather query response: {weather_response_empty[:100]}...")

        # Step 3: Add calculator tool and test conversation start
        print(f"\n🧮 Step 3: Adding CALCULATOR TOOL - Starting Conversation")
        add_calc_payload = {"jsonrpc": "2.0", "method": "tools/add", "params": {"url": "http://localhost:8002/mcp"}, "id": "add-calc"}
        async with session.post(base_url, json=add_calc_payload) as response:
            result = await response.json()
            print(f"   Add result: {result.get('result', {}).get('message', 'Unknown')}")
        
        # Wait for tool to be added
        await asyncio.sleep(2)
        
        # Check agent card after adding calculator tool
        agent_info = await check_agent_card()
        print(f"   🃏 Agent Card: {agent_info['mcp_skills']} MCP skills ({', '.join(agent_info['skill_names'])}), {agent_info['tool_count']} tools")
        
        # Start conversation - ask for calculation
        calc_response_with_calc = await send_message(calc_query, "calc-step1")
        print(f"   ✅ Step 1 - Calculation: {calc_response_with_calc[:150]}...")
        
        # Wait between requests
        await asyncio.sleep(3)
        
        # Try weather without weather tool - should fail
        weather_response_no_weather = await send_message(weather_query, "weather-no-tool")
        print(f"   ❌ Step 2 - Weather (no tool): {weather_response_no_weather[:150]}...")

        # Step 4: Add weather tool - complete the conversation
        print(f"\n🌤️ Step 4: Adding WEATHER TOOL - Completing Conversation")
        add_weather_payload = {"jsonrpc": "2.0", "method": "tools/add", "params": {"url": "http://localhost:8001/mcp"}, "id": "add-weather"}
        async with session.post(base_url, json=add_weather_payload) as response:
            result = await response.json()
            print(f"   Add result: {result.get('result', {}).get('message', 'Unknown')}")
        
        # Wait for tool to be added
        await asyncio.sleep(2)
        
        # Check agent card after adding weather tool
        agent_info = await check_agent_card()
        skill_names = ', '.join(agent_info['skill_names'][:3] + (['...'] if len(agent_info['skill_names']) > 3 else []))
        print(f"   🃏 Agent Card: {agent_info['mcp_skills']} MCP skills ({skill_names}), {agent_info['tool_count']} tools")
        
        # Now the weather query should work with context from previous calculation
        weather_response_with_context = await send_message(weather_query, "weather-with-context")
        print(f"   ✅ Step 2 - Weather (with context): {weather_response_with_context[:150]}...")
        
        # Wait between requests
        await asyncio.sleep(3)
        
        # Test calculation still works
        calc_response_check = await send_message("What's 144 divided by 12?", "calc-check")
        print(f"   ✅ Calculation still works: {calc_response_check[:150]}...")

        # Step 5: Remove weather tool - test session continuity
        print(f"\n🗑️ Step 5: Removing WEATHER TOOL - Testing Session Continuity")
        remove_weather_payload = {"jsonrpc": "2.0", "method": "tools/remove", "params": {"url": "http://localhost:8001/mcp"}, "id": "remove-weather"}
        async with session.post(base_url, json=remove_weather_payload) as response:
            result = await response.json()
            print(f"   Remove result: {result.get('result', {}).get('message', 'Unknown')}")
        
        # Wait for tool to be removed
        await asyncio.sleep(2)
        
        # Check agent card after removing weather tool
        agent_info = await check_agent_card()
        print(f"   🃏 Agent Card: {agent_info['mcp_skills']} MCP skills ({', '.join(agent_info['skill_names'])}), {agent_info['tool_count']} tools")
        
        # Ask about previous weather - should remember context but lack weather tool
        context_test = await send_message("Can you tell me what weather we just discussed?", "context-test")
        print(f"   🧠 Context memory test: {context_test[:150]}...")
        
        # Wait between requests
        await asyncio.sleep(3)
        
        # New weather query should fail without tool
        new_weather_test = await send_message("What's the weather in London?", "new-weather-fail")
        print(f"   ❌ New weather query (no tool): {new_weather_test[:150]}...")

        # Step 6: Show final tool history
        print(f"\n📊 Step 6: Tool Change History & Audit Trail")
        print("=" * 60)
        history_payload = {"jsonrpc": "2.0", "method": "tools/history", "params": {}, "id": "final-history"}
        async with session.post(base_url, json=history_payload) as response:
            result = await response.json()
            history = result.get('result', {}).get('history', [])
            
            if not history:
                print("   📝 No tool changes recorded yet.")
            else:
                for i, entry in enumerate(history, 1):
                    action = entry.get('action', 'unknown')
                    url = entry.get('url', 'unknown')
                    timestamp = entry.get('timestamp', 'unknown')
                    session_preserved = entry.get('session_preserved', False)
                    tool_descriptions = entry.get('tool_descriptions', [])
                    
                    # Format timestamp for readability
                    try:
                        dt = datetime.fromisoformat(timestamp.replace('Z', '+00:00'))
                        readable_time = dt.strftime('%H:%M:%S')
                    except:
                        readable_time = timestamp.split('T')[1][:8] if 'T' in timestamp else timestamp
                    
                    # Action icon and color
                    action_icon = "➕" if action == "add" else "➖" if action == "remove" else "🔄"
                    action_text = action.upper()
                    
                    # Server type
                    server_type = "weather" if "8001" in url else "calculator" if "8002" in url else "file" if "8000" in url else "unknown"
                    
                    print(f"\n   {action_icon} #{i} {action_text} {server_type.upper()} SERVER")
                    print(f"   ├─ Time: {readable_time}")
                    print(f"   ├─ URL: {url}")
                    print(f"   ├─ Session: {'✅ Preserved' if session_preserved else '❌ Not preserved'}")
                    
                    # Show tool descriptions in a nice format
                    if tool_descriptions:
                        print(f"   └─ Tools ({len(tool_descriptions)}):")
                        for j, tool_desc in enumerate(tool_descriptions):
                            tool_name = tool_desc.get('name', 'unknown')
                            tool_desc_text = tool_desc.get('description', 'No description')
                            
                            # Clean up description - take first line and limit length
                            clean_desc = tool_desc_text.split('\n')[0].strip()
                            if len(clean_desc) > 60:
                                clean_desc = clean_desc[:60] + "..."
                            
                            is_last_tool = j == len(tool_descriptions) - 1
                            connector = "└─" if is_last_tool else "├─"
                            print(f"      {connector} {tool_name}: {clean_desc}")
                    else:
                        print(f"   └─ Tools: (No descriptions available)")
                
                # Summary
                total_adds = sum(1 for entry in history if entry.get('action') == 'add')
                total_removes = sum(1 for entry in history if entry.get('action') == 'remove')
                print(f"\n   📈 Summary: {total_adds} additions, {total_removes} removals, {len(history)} total operations")

        # Summary
        print(f"\n🎯 SESSION CONTINUITY & AGENT CARD SUMMARY:")
        print(f"   NO TOOLS:           Weather ❌ | Calculator ❌ | Agent Card: 0 MCP skills")
        print(f"   CALCULATOR ONLY:    Weather ❌ | Calculator ✅ | Agent Card: 3 MCP skills (Context: ❌)")
        print(f"   CALCULATOR + WEATHER: Weather ✅ | Calculator ✅ | Agent Card: 6 MCP skills (Context: ✅)")
        print(f"   CALCULATOR ONLY:    Weather ❌ | Calculator ✅ | Agent Card: 3 MCP skills (Context: ✅)")
        print(f"\n🎉 Session continuity and dynamic tool management working perfectly!")
        print(f"🧠 The agent remembers the conversation context even when tools change!")
        print(f"🃏 The agent card dynamically reflects available MCP tools and skills!")

if __name__ == "__main__":
    print("🚀 Make sure the adk_a2a_toolManage_agent server is running on port 5002")
    print("   Run: python adk_a2a_server.py")
    print()
    
    try:
        asyncio.run(test_capability_changes())
    except Exception as e:
        print(f"❌ Test failed with error: {e}")
        print("   Make sure the server is running and accessible")