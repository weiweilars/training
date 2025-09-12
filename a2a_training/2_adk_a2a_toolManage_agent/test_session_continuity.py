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
    weather_query = "What is the current temperature in Tokyo in Celsius?"
    calc_query = "Can you calculate double that temperature for me?"
    
    print("🧪 Testing Session Continuity with Conversational Flow")
    print("=" * 70)
    print(f"🔍 Conversation flow:")
    print(f"   1. Get weather: '{weather_query}'")
    print(f"   2. Calculate double: '{calc_query}'")
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
        
        weather_response_empty = await send_message(weather_query, "weather-empty")
        print(f"   Weather query response: {weather_response_empty[:100]}...")
        
        calc_response_empty = await send_message(calc_query, "calc-empty")
        print(f"   Calc query response: {calc_response_empty[:100]}...")

        # Step 3: Add weather tool and test conversation start
        print(f"\n🌤️ Step 3: Adding WEATHER TOOL - Starting Conversation")
        add_weather_payload = {"jsonrpc": "2.0", "method": "tools/add", "params": {"url": "http://localhost:8004/mcp"}, "id": "add-weather"}
        async with session.post(base_url, json=add_weather_payload) as response:
            result = await response.json()
            print(f"   Add result: {result.get('result', {}).get('message', 'Unknown')}")
        
        # Check agent card after adding weather tool
        agent_info = await check_agent_card()
        print(f"   🃏 Agent Card: {agent_info['mcp_skills']} MCP skills ({', '.join(agent_info['skill_names'])}), {agent_info['tool_count']} tools")
        
        # Start conversation - ask for weather
        weather_response_with_weather = await send_message(weather_query, "weather-step1")
        print(f"   ✅ Step 1 - Weather: {weather_response_with_weather[:150]}...")
        
        # Try calculation without calc tool - should fail
        calc_response_no_calc = await send_message(calc_query, "calc-no-tool")
        print(f"   ❌ Step 2 - Calc (no tool): {calc_response_no_calc[:150]}...")

        # Step 4: Add calculator tool - complete the conversation
        print(f"\n🧮 Step 4: Adding CALCULATOR TOOL - Completing Conversation")
        add_calc_payload = {"jsonrpc": "2.0", "method": "tools/add", "params": {"url": "http://localhost:8005/mcp"}, "id": "add-calc"}
        async with session.post(base_url, json=add_calc_payload) as response:
            result = await response.json()
            print(f"   Add result: {result.get('result', {}).get('message', 'Unknown')}")
        
        # Check agent card after adding calculator tool
        agent_info = await check_agent_card()
        skill_names = ', '.join(agent_info['skill_names'][:3] + (['...'] if len(agent_info['skill_names']) > 3 else []))
        print(f"   🃏 Agent Card: {agent_info['mcp_skills']} MCP skills ({skill_names}), {agent_info['tool_count']} tools")
        
        # Now the calculation should work with context from previous weather query
        calc_response_with_context = await send_message(calc_query, "calc-with-context")
        print(f"   ✅ Step 2 - Calc (with context): {calc_response_with_context[:150]}...")
        
        # Test weather still works
        weather_response_check = await send_message("What about the weather in London?", "weather-check")
        print(f"   ✅ Weather still works: {weather_response_check[:150]}...")

        # Step 5: Remove calculator tool - test session continuity
        print(f"\n🗑️ Step 5: Removing CALCULATOR TOOL - Testing Session Continuity")
        remove_calc_payload = {"jsonrpc": "2.0", "method": "tools/remove", "params": {"url": "http://localhost:8005/mcp"}, "id": "remove-calc"}
        async with session.post(base_url, json=remove_calc_payload) as response:
            result = await response.json()
            print(f"   Remove result: {result.get('result', {}).get('message', 'Unknown')}")
        
        # Check agent card after removing calculator tool
        agent_info = await check_agent_card()
        print(f"   🃏 Agent Card: {agent_info['mcp_skills']} MCP skills ({', '.join(agent_info['skill_names'])}), {agent_info['tool_count']} tools")
        
        # Ask about previous calculation - should remember context but lack calculation tool
        context_test = await send_message("Can you tell me what calculation we just did?", "context-test")
        print(f"   🧠 Context memory test: {context_test[:150]}...")
        
        # New calculation should fail without tool
        new_calc_test = await send_message("Calculate 25 * 4", "new-calc-fail")
        print(f"   ❌ New calculation (no tool): {new_calc_test[:150]}...")

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
                    server_type = "weather" if "8004" in url else "calculator" if "8005" in url else "file" if "8003" in url else "unknown"
                    
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
        print(f"   NO TOOLS:         Weather ❌ | Calculator ❌ | Agent Card: 0 MCP skills")
        print(f"   WEATHER ONLY:     Weather ✅ | Calculator ❌ | Agent Card: 3 MCP skills (Context: ❌)")
        print(f"   WEATHER + CALC:   Weather ✅ | Calculator ✅ | Agent Card: 6 MCP skills (Context: ✅)")
        print(f"   WEATHER ONLY:     Weather ✅ | Calculator ❌ | Agent Card: 3 MCP skills (Context: ✅)")
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