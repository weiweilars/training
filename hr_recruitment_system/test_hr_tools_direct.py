#!/usr/bin/env python3
"""
HR MCP Tools Direct Tester
Test any HR MCP tool in stateless mode by discovering and testing tools dynamically
Adapted from test_stateless_mcp.py with HR-specific argument generation
"""

import requests
import json
import sys
import argparse

# HR MCP Tools with their ports
HR_TOOLS = {
    # Job Requisition Agent
    "job-creation": 8051,
    "job-workflow": 8052, 
    "job-templates": 8053,
    
    # Sourcing Agent  
    "social-sourcing": 8061,
    "talent-pool": 8062,
    "outreach": 8063,
    
    # Resume Screening Agent
    "document-processing": 8071,
    "matching-engine": 8072,
    
    # Communication Agent
    "email-service": 8081,
    "engagement-tracking": 8082,
    
    # Interview Scheduling Agent
    "calendar-integration": 8091,
    "interview-workflow": 8092,
    "meeting-management": 8093,
    
    # Assessment Agent
    "test-engine": 8101,
    "assessment-library": 8102,
    "results-analysis": 8103,
    
    # Offer Management Agent
    "offer-generation": 8111,
    "negotiation-management": 8112,
    "contract-management": 8113,
    
    # Analytics & Reporting Agent
    "metrics-engine": 8121,
    "dashboard-generator": 8122,
    "predictive-analytics": 8123,
    
    # Compliance Agent
    "regulatory-engine": 8131,
    "data-privacy": 8132,
    "audit-management": 8133,
    
    # Background Verification Agent
    "verification-engine": 8141,
    "reference-check": 8142,
    "credential-validation": 8143
}

class HRMCPTester:
    def __init__(self, tool_name=None, port=None):
        if tool_name and tool_name in HR_TOOLS:
            self.tool_name = tool_name
            self.port = HR_TOOLS[tool_name]
            self.base_url = f"http://localhost:{self.port}"
        elif port:
            self.port = port
            self.base_url = f"http://localhost:{port}"
            self.tool_name = f"port-{port}"
        else:
            self.base_url = "http://localhost:8051"  # Default to job-creation
            self.tool_name = "job-creation"
            self.port = 8051
            
    def list_available_hr_tools(self):
        """List all available HR tools"""
        print("🔧 Available HR MCP Tools:")
        print("=" * 50)
        
        for tool_name, port in HR_TOOLS.items():
            print(f"  {tool_name:<25} Port {port}")
        
        print(f"\nTotal: {len(HR_TOOLS)} tools")
        print("Use: python test_hr_tools_direct.py --tool <tool-name>")
        
    def list_tools(self):
        """Get list of available tools from MCP server"""
        print(f"🔍 Discovering tools at {self.base_url} ({self.tool_name})...")
        
        payload = {
            "jsonrpc": "2.0",
            "id": 1,
            "method": "tools/list"
        }
        
        headers = {
            "Content-Type": "application/json",
            "Accept": "application/json, text/event-stream"
        }
        
        try:
            response = requests.post(f"{self.base_url}/mcp", json=payload, headers=headers, timeout=10)
            
            if response.status_code == 200:
                if response.headers.get('content-type', '').startswith('text/event-stream'):
                    lines = response.text.strip().split('\n')
                    for line in lines:
                        if line.startswith('data: '):
                            data = line[6:]
                            try:
                                result = json.loads(data)
                                if 'result' in result and 'tools' in result['result']:
                                    tools = result['result']['tools']
                                    print(f"✅ Found {len(tools)} tools:")
                                    for i, tool in enumerate(tools, 1):
                                        print(f"  {i}. {tool['name']}: {tool.get('description', 'No description')}")
                                    return tools
                                elif 'error' in result:
                                    print(f"❌ Error listing tools: {result['error']['message']}")
                                    return None
                            except json.JSONDecodeError:
                                print(f"Failed to parse tools response: {data}")
                                return None
                else:
                    result = response.json()
                    if 'result' in result and 'tools' in result['result']:
                        tools = result['result']['tools']
                        print(f"✅ Found {len(tools)} tools:")
                        for i, tool in enumerate(tools, 1):
                            print(f"  {i}. {tool['name']}: {tool.get('description', 'No description')}")
                        return tools
                    elif 'error' in result:
                        print(f"❌ Error listing tools: {result['error']['message']}")
                        return None
            else:
                print(f"❌ Failed to list tools ({response.status_code}): {response.text}")
                return None
                
        except requests.ConnectionError:
            print(f"❌ Cannot connect to {self.base_url}")
            print(f"Make sure the {self.tool_name} MCP server is running")
            return None
        except Exception as e:
            print(f"❌ Error listing tools: {e}")
            return None
    
    def get_tool_schema(self, tool_name):
        """Get schema for a specific tool"""
        payload = {
            "jsonrpc": "2.0",
            "id": 1,
            "method": "tools/list"
        }
        
        headers = {
            "Content-Type": "application/json",
            "Accept": "application/json, text/event-stream"
        }
        
        try:
            response = requests.post(f"{self.base_url}/mcp", json=payload, headers=headers, timeout=10)
            
            if response.status_code == 200:
                if response.headers.get('content-type', '').startswith('text/event-stream'):
                    lines = response.text.strip().split('\n')
                    for line in lines:
                        if line.startswith('data: '):
                            data = line[6:]
                            try:
                                result = json.loads(data)
                                if 'result' in result and 'tools' in result['result']:
                                    tools = result['result']['tools']
                                    for tool in tools:
                                        if tool['name'] == tool_name:
                                            return tool
                            except json.JSONDecodeError:
                                pass
                else:
                    result = response.json()
                    if 'result' in result and 'tools' in result['result']:
                        tools = result['result']['tools']
                        for tool in tools:
                            if tool['name'] == tool_name:
                                return tool
        except Exception as e:
            print(f"Error getting tool schema: {e}")
        
        return None
    
    def generate_hr_sample_arguments(self, tool_schema):
        """Generate HR-specific sample arguments based on tool schema"""
        if 'inputSchema' not in tool_schema:
            return {}
        
        schema = tool_schema['inputSchema']
        properties = schema.get('properties', {})
        required = schema.get('required', [])
        
        args = {}
        
        for prop_name, prop_schema in properties.items():
            prop_type = prop_schema.get('type', 'string')
            prop_lower = prop_name.lower()
            
            # HR-specific argument generation
            if 'title' in prop_lower or 'job_title' in prop_lower:
                args[prop_name] = "Senior Python Developer"
            elif 'department' in prop_lower:
                args[prop_name] = "Engineering"
            elif 'location' in prop_lower:
                args[prop_name] = "San Francisco, CA"
            elif 'salary' in prop_lower:
                args[prop_name] = 150000
            elif 'experience' in prop_lower or 'years' in prop_lower:
                args[prop_name] = 5
            elif 'skills' in prop_lower:
                args[prop_name] = ["Python", "Django", "PostgreSQL", "AWS"]
            elif 'keywords' in prop_lower:
                args[prop_name] = "Python developer"
            elif 'name' in prop_lower and 'candidate' in prop_lower:
                args[prop_name] = "John Smith"
            elif 'email' in prop_lower:
                args[prop_name] = "john.smith@example.com"
            elif 'resume' in prop_lower or 'cv' in prop_lower:
                args[prop_name] = "John Smith - 5 years Python experience, Stanford CS degree"
            elif 'company' in prop_lower:
                args[prop_name] = "Google"
            elif 'school' in prop_lower or 'university' in prop_lower:
                args[prop_name] = "Stanford University"
            elif 'degree' in prop_lower:
                args[prop_name] = "BS Computer Science"
            elif 'message' in prop_lower:
                args[prop_name] = "Thank you for your interest in our Senior Python Developer position."
            elif 'subject' in prop_lower:
                args[prop_name] = "Interview Invitation - Senior Python Developer"
            elif 'date' in prop_lower or 'time' in prop_lower:
                args[prop_name] = "2024-03-15T14:00:00Z"
            elif prop_type == 'string':
                args[prop_name] = f"sample_{prop_name}"
            elif prop_type == 'number' or prop_type == 'integer':
                args[prop_name] = 42
            elif prop_type == 'boolean':
                args[prop_name] = True
            elif prop_type == 'array':
                args[prop_name] = ["sample_item"]
            
        # Only include required fields if we have a lot of properties
        if len(properties) > 3 and required:
            args = {k: v for k, v in args.items() if k in required}
        
        return args
    
    def test_tool(self, tool_name, custom_args=None):
        """Test a specific tool"""
        print(f"\n🧪 Testing tool: {tool_name}")
        print("-" * 40)
        
        # Get tool schema for better argument generation
        tool_schema = self.get_tool_schema(tool_name)
        
        if custom_args:
            arguments = custom_args
        elif tool_schema:
            arguments = self.generate_hr_sample_arguments(tool_schema)
        else:
            arguments = {}
        
        print(f"Arguments: {json.dumps(arguments, indent=2)}")
        
        payload = {
            "jsonrpc": "2.0",
            "id": 2,
            "method": "tools/call",
            "params": {
                "name": tool_name,
                "arguments": arguments
            }
        }
        
        headers = {
            "Content-Type": "application/json",
            "Accept": "application/json, text/event-stream"
        }
        
        try:
            response = requests.post(f"{self.base_url}/mcp", json=payload, headers=headers, timeout=15)
            print(f"Response status: {response.status_code}")
            
            if response.status_code == 200:
                if response.headers.get('content-type', '').startswith('text/event-stream'):
                    lines = response.text.strip().split('\n')
                    for line in lines:
                        if line.startswith('data: '):
                            data = line[6:]
                            try:
                                result = json.loads(data)
                                if 'error' in result:
                                    print(f"❌ Tool error: {result['error']['message']}")
                                    return False
                                elif 'result' in result:
                                    print(f"✅ Tool call successful!")
                                    if 'content' in result['result']:
                                        content = result['result']['content'][0]['text']
                                        # Try to parse as JSON for pretty printing
                                        try:
                                            parsed = json.loads(content)
                                            print(f"📋 Result: {json.dumps(parsed, indent=2)[:300]}...")
                                        except:
                                            print(f"📋 Result: {content[:300]}...")
                                    else:
                                        print(f"📋 Result: {json.dumps(result['result'], indent=2)[:300]}...")
                                    return True
                            except json.JSONDecodeError:
                                print(f"Failed to parse response: {data}")
                                return False
                else:
                    result = response.json()
                    if 'error' in result:
                        print(f"❌ Tool error: {result['error']['message']}")
                        return False
                    else:
                        print(f"✅ Tool call successful!")
                        print(f"📋 Result: {json.dumps(result.get('result', {}), indent=2)[:300]}...")
                        return True
            else:
                print(f"❌ Request failed ({response.status_code}): {response.text}")
                return False
                
        except Exception as e:
            print(f"❌ Tool test failed: {e}")
            return False
    
    def run_tests(self, specific_tool_function=None, custom_args=None):
        """Run tests on MCP server"""
        print(f"Testing HR MCP Tool Server - STATELESS Mode")
        print(f"Tool: {self.tool_name}")
        print(f"Server: {self.base_url}")
        print("=" * 60)
        
        # Get available tools
        tools = self.list_tools()
        if not tools:
            return False
        
        if specific_tool_function:
            # Test specific tool function
            if any(tool['name'] == specific_tool_function for tool in tools):
                return self.test_tool(specific_tool_function, custom_args)
            else:
                print(f"❌ Tool function '{specific_tool_function}' not found")
                print("Available functions:")
                for tool in tools:
                    print(f"  - {tool['name']}")
                return False
        else:
            # Test all tools
            success_count = 0
            for tool in tools:
                success = self.test_tool(tool['name'])
                if success:
                    success_count += 1
            
            print(f"\n📊 Results: {success_count}/{len(tools)} tools passed")
            return success_count == len(tools)

def main():
    parser = argparse.ArgumentParser(description='Test HR MCP tools in stateless mode')
    parser.add_argument('--list', action='store_true', help='List all available HR MCP tools')
    parser.add_argument('--tool', choices=list(HR_TOOLS.keys()), 
                       help='HR MCP tool to test (e.g., job-creation, social-sourcing)')
    parser.add_argument('--port', type=int, help='Specific port to test (alternative to --tool)')
    parser.add_argument('--function', help='Specific tool function to test (default: test all functions)')
    parser.add_argument('--args', help='JSON string of custom arguments for tool function')
    
    args = parser.parse_args()
    
    if args.list:
        tester = HRMCPTester()
        tester.list_available_hr_tools()
        return
    
    if not args.tool and not args.port:
        print("❌ Must specify --tool or --port")
        print("Use --list to see available tools")
        return
    
    custom_args = None
    if args.args:
        try:
            custom_args = json.loads(args.args)
        except json.JSONDecodeError:
            print("❌ Invalid JSON in --args parameter")
            return
    
    tester = HRMCPTester(args.tool, args.port)
    success = tester.run_tests(args.function, custom_args)
    
    print("\n" + "=" * 60)
    if success:
        print("🎉 All tests PASSED!")
    else:
        print("💥 Some tests FAILED!")

if __name__ == "__main__":
    main()