#!/usr/bin/env python3
"""
A2A Test Client - Training Example
Simple client to test the A2A agent server
"""

import asyncio
import aiohttp
import json
import uuid
from datetime import datetime

SERVER_URL = "http://localhost:5001"

async def test_agent_discovery():
    """Test agent discovery endpoint"""
    print("🔍 Testing Agent Discovery...")
    
    async with aiohttp.ClientSession() as session:
        async with session.get(f"{SERVER_URL}/.well-known/agent-card.json") as response:
            if response.status == 200:
                data = await response.json()
                print(f"✅ Agent Info: {json.dumps(data, indent=2)}")
            else:
                print(f"❌ Failed: HTTP {response.status}")

async def send_a2a_task(message: str, task_description: str):
    """Send an A2A task request"""
    print(f"\n📤 Testing {task_description}...")
    
    request_payload = {
        "jsonrpc": "2.0",
        "id": str(uuid.uuid4()),
        "method": "send-task",
        "params": {
            "id": str(uuid.uuid4()),
            "sessionId": f"test-session-{datetime.now().timestamp()}", 
            "message": {
                "role": "user",
                "parts": [
                    {"text": message}
                ]
            }
        }
    }
    
    async with aiohttp.ClientSession() as session:
        async with session.post(
            SERVER_URL,
            json=request_payload,
            headers={"Content-Type": "application/json"}
        ) as response:
            if response.status == 200:
                data = await response.json()
                print(f"✅ Response: {json.dumps(data, indent=2)}")
            else:
                error_text = await response.text()
                print(f"❌ Failed: HTTP {response.status} - {error_text}")

async def test_tool_endpoints():
    """Test tool-related endpoints"""
    print("\n🔧 Testing Tool Endpoints...")
    
    # Test list tools
    async with aiohttp.ClientSession() as session:
        async with session.get(f"{SERVER_URL}/list_tools") as response:
            if response.status == 200:
                data = await response.json()
                print(f"✅ Tools: {json.dumps(data, indent=2)}")
            else:
                print(f"❌ List tools failed: HTTP {response.status}")
        
        # Test tool history  
        async with session.get(f"{SERVER_URL}/get_tool_history") as response:
            if response.status == 200:
                data = await response.json()
                print(f"✅ Tool History: {json.dumps(data, indent=2)}")
            else:
                print(f"❌ Tool history failed: HTTP {response.status}")

async def test_health_check():
    """Test health check endpoint"""
    print("\n❤️ Testing Health Check...")
    
    async with aiohttp.ClientSession() as session:
        async with session.get(f"{SERVER_URL}/health") as response:
            if response.status == 200:
                data = await response.json()
                print(f"✅ Health: {json.dumps(data, indent=2)}")
            else:
                print(f"❌ Health check failed: HTTP {response.status}")

async def run_tests():
    """Run all tests"""
    print("🚀 Starting A2A Agent Server Tests")
    print("=" * 50)
    
    try:
        # Test agent discovery
        await test_agent_discovery()
        
        # Test different types of tasks
        await send_a2a_task("What's the weather in New York?", "Weather Query")
        await send_a2a_task("What time is it?", "Time Query")
        await send_a2a_task("Calculate 15 + 27", "Math Calculation")
        await send_a2a_task("Hello, how are you?", "General Message")
        
        # Test tool endpoints
        await test_tool_endpoints()
        
        # Test health check
        await test_health_check()
        
        print("\n✅ All tests completed!")
        
    except Exception as e:
        print(f"\n❌ Test failed: {e}")

if __name__ == "__main__":
    print("🧪 A2A Test Client - Training Example")
    print("Make sure the A2A server is running on localhost:5001")
    print()
    
    asyncio.run(run_tests())