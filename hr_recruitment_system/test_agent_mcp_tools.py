#!/usr/bin/env python3
"""
Complete HR Agent MCP Tool Testing
Tests all 11 HR agents for MCP tool calling functionality
"""

import asyncio
import httpx
import json
import time
import argparse
from datetime import datetime
from typing import Dict, List, Any
from hr_tools_config import get_agent_test_config

# Get agent configuration from centralized config
AGENTS = get_agent_test_config()

async def test_agent(agent_name: str, config: Dict[str, Any]) -> Dict[str, Any]:
    """Test single agent for MCP tool calling"""
    print(f"\n🧪 Testing {agent_name}...")
    
    port = config["port"]
    test_query = config["test"]
    
    # Test agent availability
    try:
        async with httpx.AsyncClient(timeout=10.0) as client:
            # Check if agent is running
            card_response = await client.get(f"http://localhost:{port}/.well-known/agent-card.json")
            agent_running = card_response.status_code == 200
            
            if not agent_running:
                return {
                    "agent": agent_name,
                    "success": False,
                    "error": f"Agent not running on port {port}",
                    "tools_called": [],
                    "mcp_requests": 0,
                    "response_time": 0.0
                }
            
            # Send test query
            payload = {
                "jsonrpc": "2.0",
                "method": "message/send", 
                "params": {"content": test_query},
                "id": 1
            }
            
            start_time = time.time()
            response = await client.post(f"http://localhost:{port}", json=payload)
            response_time = time.time() - start_time
            
            if response.status_code != 200:
                return {
                    "agent": agent_name,
                    "success": False,
                    "error": f"HTTP {response.status_code}",
                    "tools_called": [],
                    "mcp_requests": 0,
                    "response_time": response_time
                }
            
            result_data = response.json()
            
            # Extract agent response
            agent_response = ""
            if "result" in result_data and "result" in result_data["result"]:
                agent_result = result_data["result"]["result"]
                if "message" in agent_result and "content" in agent_result["message"]:
                    agent_response = agent_result["message"]["content"]
            
            # For now, we'll analyze response content to detect tool usage patterns
            # In a real scenario, you'd capture agent logs to verify actual tool calls
            tools_detected = analyze_response_for_tools(agent_response, config["tools"])
            mcp_requests = len([t for t in tools_detected if t])  # Approximate
            
            success = len(tools_detected) > 0 and len(agent_response) > 100
            
            print(f"   ⏱️  Response: {response_time:.2f}s")
            print(f"   🔧 Tools detected: {tools_detected}")
            print(f"   💬 Response: {len(agent_response)} chars")
            
            return {
                "agent": agent_name,
                "success": success,
                "tools_called": tools_detected,
                "mcp_requests": mcp_requests,
                "response_time": response_time,
                "response_preview": agent_response[:200] + "..." if len(agent_response) > 200 else agent_response,
                "error": None
            }
            
    except Exception as e:
        return {
            "agent": agent_name,
            "success": False,
            "error": str(e),
            "tools_called": [],
            "mcp_requests": 0,
            "response_time": 0.0
        }

def analyze_response_for_tools(response: str, expected_tools: List[str]) -> List[str]:
    """Analyze response content for evidence of tool usage"""
    detected_tools = []
    
    # Look for structured data, IDs, specific formatting that indicates tool results
    indicators = [
        "id\":", "ID:", "created", "generated", "processed", 
        "search_id", "campaign_id", "pool_id", "draft_id",
        "linkedin.com", "github.com", "match_score", "profiles",
        "workflow", "approval", "verification", "assessment"
    ]
    
    response_lower = response.lower()
    
    # Count indicators of tool usage
    tool_indicators = sum(1 for indicator in indicators if indicator.lower() in response_lower)
    
    # If response has multiple tool indicators and is substantial, likely used tools
    if tool_indicators >= 2 and len(response) > 200:
        detected_tools = ["tool_activity_detected"]
    
    return detected_tools

async def main():
    parser = argparse.ArgumentParser(description="Test HR Agent MCP Tool Calling")
    parser.add_argument("--agent", choices=list(AGENTS.keys()), help="Test specific agent")
    parser.add_argument("--all", action="store_true", help="Test all agents")
    parser.add_argument("--list", action="store_true", help="List available agents")
    
    args = parser.parse_args()
    
    if args.list:
        print("📋 Available HR Agents:")
        print("="*50)
        for name, config in AGENTS.items():
            tools_count = len(config["tools"])
            print(f"🤖 {name} (port {config['port']}) - {tools_count} MCP tools")
        return
    
    print("🧪 HR Agent MCP Tool Testing")
    print("="*50)
    print(f"📅 Started: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    results = []
    
    if args.agent:
        # Test single agent
        print(f"🎯 Testing {args.agent} only")
        result = await test_agent(args.agent, AGENTS[args.agent])
        results.append(result)
    elif args.all or not args.agent:
        # Test all agents
        print(f"🤖 Testing all {len(AGENTS)} agents...")
        
        for agent_name, config in AGENTS.items():
            result = await test_agent(agent_name, config)
            results.append(result)
            await asyncio.sleep(1)  # Small delay between tests
    else:
        print("❓ Use --agent <name>, --all, or --list")
        return
    
    # Print summary
    print(f"\n{'='*60}")
    print("📊 TEST RESULTS")
    print(f"{'='*60}")
    
    successful = [r for r in results if r["success"]]
    failed = [r for r in results if not r["success"]]
    
    print(f"✅ Successful: {len(successful)}/{len(results)}")
    print(f"❌ Failed: {len(failed)}/{len(results)}")
    
    if successful:
        print(f"\n✅ WORKING AGENTS:")
        for result in successful:
            tools = f"({len(result['tools_called'])} tools)" if result['tools_called'] else ""
            print(f"   🟢 {result['agent']} - {result['response_time']:.2f}s {tools}")
    
    if failed:
        print(f"\n❌ FAILED AGENTS:")
        for result in failed:
            print(f"   🔴 {result['agent']}: {result['error']}")
    
    print(f"\n📈 SUCCESS RATE: {len(successful)/len(results)*100:.1f}%")
    
    # Show detailed results for successful agents
    if successful and (args.agent or len(successful) <= 3):
        print(f"\n📋 DETAILED RESULTS:")
        for result in successful[:3]:  # Show first 3 detailed
            print(f"\n🤖 {result['agent']}:")
            print(f"   Response: {result['response_preview']}")

if __name__ == "__main__":
    asyncio.run(main())
