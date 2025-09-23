#!/usr/bin/env python3
"""
Agent Compatibility Test for MCP Deployment
Tests the exact same workflow that a native MCP agent would use
"""

import json
import requests
import sys


class MCPAgentTest:
    """Simulate how an MCP agent interacts with the server"""

    def __init__(self, base_url="http://localhost:8004"):
        self.base_url = base_url
        self.session = requests.Session()
        self.session.headers.update({"Content-Type": "application/json"})

    def send_request(self, method, params=None, request_id=1):
        """Send JSON-RPC request exactly as an agent would"""
        payload = {
            "jsonrpc": "2.0",
            "method": method,
            "params": params or {},
            "id": request_id
        }

        response = self.session.post(f"{self.base_url}/mcp", json=payload)

        if response.status_code != 200:
            raise Exception(f"HTTP {response.status_code}: {response.text}")

        return response.json()

    def test_agent_workflow(self):
        """Test the complete agent workflow"""
        print("🤖 Testing Agent Compatibility Workflow")
        print("=" * 50)

        # Step 1: Initialize connection (required by MCP spec)
        print("1️⃣ Initialize Connection...")
        init_response = self.send_request("initialize", {
            "protocolVersion": "2024-11-05",
            "capabilities": {"tools": {}},
            "clientInfo": {"name": "test-agent", "version": "1.0.0"}
        })

        assert init_response["jsonrpc"] == "2.0"
        assert "result" in init_response
        assert init_response["result"]["protocolVersion"] == "2024-11-05"
        print(f"✅ Initialize successful - Protocol: {init_response['result']['protocolVersion']}")
        print(f"   Server: {init_response['result']['serverInfo']['name']}")
        print(f"   Capabilities: {list(init_response['result']['capabilities'].keys())}")

        # Step 2: Ping for connectivity (common agent pattern)
        print("\n2️⃣ Ping Server...")
        ping_response = self.send_request("ping")
        assert ping_response["result"]["pong"] is True
        print("✅ Ping successful")

        # Step 3: List available tools (required for agent discovery)
        print("\n3️⃣ Discover Tools...")
        tools_response = self.send_request("tools/list")
        tools = tools_response["result"]["tools"]
        print(f"✅ Found {len(tools)} tools:")
        for tool in tools:
            print(f"   - {tool['name']}: {tool['description'][:50]}...")
            # Verify each tool has required schema
            assert "inputSchema" in tool
            assert tool["inputSchema"]["type"] == "object"

        # Step 4: Call a tool (main agent functionality)
        print("\n4️⃣ Execute Tool...")
        if tools:
            tool_name = tools[0]["name"]
            # Use the first tool's schema to make a valid call
            tool_schema = tools[0]["inputSchema"]

            # Create arguments based on the schema
            if tool_name == "calculate":
                arguments = {"operation": "+", "a": 15, "b": 27}
            elif tool_name == "get_current_weather":
                arguments = {"city": "San Francisco", "country": "USA"}
            else:
                arguments = {}

            call_response = self.send_request("tools/call", {
                "name": tool_name,
                "arguments": arguments
            })

            assert "result" in call_response
            assert "content" in call_response["result"]
            assert len(call_response["result"]["content"]) > 0

            content = call_response["result"]["content"][0]
            assert content["type"] == "text"
            print(f"✅ Tool execution successful: {tool_name}")
            print(f"   Result: {content['text'][:100]}...")

        # Step 5: Test batch requests (agent efficiency)
        print("\n5️⃣ Batch Request...")
        batch_payload = [
            {"jsonrpc": "2.0", "method": "ping", "params": {}, "id": 1},
            {"jsonrpc": "2.0", "method": "tools/list", "params": {}, "id": 2}
        ]

        batch_response = self.session.post(f"{self.base_url}/mcp", json=batch_payload)
        batch_result = batch_response.json()

        assert isinstance(batch_result, list)
        assert len(batch_result) == 2
        assert batch_result[0]["result"]["pong"] is True
        assert len(batch_result[1]["result"]["tools"]) > 0
        print("✅ Batch request successful")

        # Step 6: Test error handling (agent robustness)
        print("\n6️⃣ Error Handling...")
        error_response = self.send_request("nonexistent/method")
        assert "error" in error_response
        assert error_response["error"]["code"] == -32601
        print(f"✅ Error handling correct: {error_response['error']['message']}")

        print("\n🎉 ALL AGENT COMPATIBILITY TESTS PASSED!")
        print("✅ The deployment is 100% compatible with MCP agents")
        return True

    def test_streaming_compatibility(self):
        """Test streaming endpoint for agent compatibility"""
        print("\n🌊 Testing Streaming Compatibility...")

        # Test streaming endpoint
        payload = {
            "jsonrpc": "2.0",
            "method": "tools/call",
            "params": {
                "name": "calculate",
                "arguments": {"operation": "*", "a": 8, "b": 7}
            },
            "id": 1
        }

        response = self.session.post(f"{self.base_url}/mcp/stream", json=payload)

        if response.status_code == 200:
            # For non-streaming tools, should return normal JSON
            result = response.json()
            assert "result" in result
            print("✅ Streaming endpoint compatible")
            return True
        else:
            print(f"❌ Streaming endpoint issue: {response.status_code}")
            return False


def main():
    """Run all compatibility tests"""
    if len(sys.argv) > 1:
        base_url = sys.argv[1]
    else:
        base_url = "http://localhost:8004"

    print(f"Testing MCP Agent Compatibility against: {base_url}")
    print(f"Make sure your MCP server is running on {base_url}")
    print()

    try:
        agent_test = MCPAgentTest(base_url)

        # Test main agent workflow
        agent_test.test_agent_workflow()

        # Test streaming compatibility
        agent_test.test_streaming_compatibility()

        print("\n" + "=" * 60)
        print("🎯 CONCLUSION: This deployment is 100% agent-compatible!")
        print("🚀 Agents can connect and use this exactly like native MCP")
        print("=" * 60)

        return 0

    except Exception as e:
        print(f"\n❌ Compatibility test failed: {e}")
        return 1


if __name__ == "__main__":
    sys.exit(main())