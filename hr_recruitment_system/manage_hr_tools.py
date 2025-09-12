#!/usr/bin/env python3
"""
HR Recruitment System - Simple Tool Manager
Start/stop MCP tools for demonstration
"""

import sys
import subprocess
import time
import argparse
from hr_tools_config import HR_TOOLS, AGENT_PORTS, get_tools_for_agent, get_all_agent_names

def list_tools():
    """Show all available tools"""
    print("🚀 HR Recruitment System - Available Tools")
    print("=" * 50)
    
    for agent_name in sorted(get_all_agent_names()):
        tools = get_tools_for_agent(agent_name)
        if tools:  # Only show agents that have tools
            print(f"\n📋 {agent_name.upper().replace('_', ' ')}:")
            for tool in tools:
                port = HR_TOOLS[tool]["port"]
                print(f"   {tool} (port {port})")
    
    print(f"\nTotal: {len(HR_TOOLS)} tools across {len(get_all_agent_names())} agents")

def start_tool(tool_name):
    """Start a single tool using the HTTP runner"""
    if tool_name not in HR_TOOLS:
        print(f"❌ Tool '{tool_name}' not found!")
        return False
    
    port = HR_TOOLS[tool_name]["port"]
    print(f"🚀 Starting {tool_name} on port {port}...")
    
    # Use the new HTTP runner script in stateful mode (for agent compatibility)
    cmd = [sys.executable, "run_hr_tool_http.py", tool_name]  # Default stateless mode
    subprocess.Popen(cmd, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    
    time.sleep(2)
    print(f"✅ {tool_name} started on http://localhost:{port}/mcp")
    return True

def start_agent_tools(agent_name):
    """Start all MCP tools for an agent"""
    tools = get_tools_for_agent(agent_name)
    if not tools:
        print(f"❌ Agent '{agent_name}' not found or has no tools!")
        return False
    
    print(f"🚀 Starting {agent_name} agent tools ({len(tools)} tools)...")
    
    for tool in tools:
        start_tool(tool)
        time.sleep(1)
    
    print(f"✅ {agent_name} agent tools fully started!")
    return True

def start_all():
    """Start all HR recruitment tools"""
    print(f"🚀 Starting ALL {len(HR_TOOLS)} HR Recruitment Tools...")
    print("This will take about 30 seconds...")
    
    count = 0
    for tool_name in HR_TOOLS:
        start_tool(tool_name)
        count += 1
        print(f"Progress: {count}/{len(HR_TOOLS)}")
        time.sleep(1)
    
    print("✅ All tools started!")

def cleanup():
    """Clean up MCP tool ports only (8051-8143)"""
    print("🧹 HR Tool Manager - MCP Tool Port Cleanup")
    print("=" * 50)
    
    tool_ports_cleaned = 0
    
    # Clean up only MCP tool ports, not agent ports
    for tool_name, config in HR_TOOLS.items():
        port = config["port"]
        tool_desc = f"{tool_name.replace('-', ' ').title()} MCP"
        
        # Try to find and kill processes on tool ports
        try:
            import psutil
            for proc in psutil.process_iter(['pid', 'connections']):
                try:
                    connections = proc.info['connections'] or []
                    for conn in connections:
                        if hasattr(conn, 'laddr') and conn.laddr and conn.laddr.port == port:
                            print(f"✓ Killed {tool_desc} (PID: {proc.info['pid']}) on port {port}")
                            proc.kill()
                            tool_ports_cleaned += 1
                            break
                except (psutil.NoSuchProcess, psutil.AccessDenied, psutil.ZombieProcess):
                    continue
        except ImportError:
            # Fallback without psutil
            try:
                result = subprocess.run(["lsof", "-ti", f":{port}"], 
                                      capture_output=True, text=True, timeout=5)
                if result.returncode == 0 and result.stdout.strip():
                    pids = result.stdout.strip().split('\n')
                    for pid in pids:
                        if pid:
                            subprocess.run(["kill", "-9", pid])
                            print(f"✓ Killed {tool_desc} (PID: {pid}) on port {port}")
                            tool_ports_cleaned += 1
            except (subprocess.TimeoutExpired, FileNotFoundError):
                continue
        
    
    # Show status for ports with no processes found
    if tool_ports_cleaned == 0:
        print("  No MCP tool processes found to clean")
    
    print(f"\n✅ MCP Tool cleanup completed!")
    print(f"   Cleaned {tool_ports_cleaned} tool ports")
    print(f"   Agent ports (5020-5029) left untouched - use 'python run_sk_agents.py --cleanup' for agents")

def test_tool(tool_name):
    """Test a tool"""
    if tool_name not in TOOLS:
        print(f"❌ Tool '{tool_name}' not found!")
        return False
    
    print(f"🧪 Testing {tool_name}...")
    result = subprocess.run([sys.executable, "test_recruitment_tools.py", "--tool", tool_name])
    return result.returncode == 0

def main():
    parser = argparse.ArgumentParser(description="HR Recruitment System - Simple Tool Manager")
    
    parser.add_argument("--list", action="store_true", help="List all tools")
    parser.add_argument("--start-tool", help="Start a specific tool")
    parser.add_argument("--start-agent-tools", help="Start all MCP tools for an agent")
    parser.add_argument("--start-all-tools", action="store_true", help="Start all 28 tools")
    parser.add_argument("--test", help="Test a specific tool")
    parser.add_argument("--cleanup", action="store_true", help="Clean up all ports")
    
    args = parser.parse_args()
    
    if args.list:
        list_tools()
    elif args.start_tool:
        start_tool(args.start_tool)
    elif args.start_agent_tools:
        start_agent_tools(args.start_agent_tools)
    elif args.start_all_tools:
        start_all()
    elif args.test:
        test_tool(args.test)
    elif args.cleanup:
        cleanup()
    else:
        print("HR Recruitment System Tool Manager")
        print("Usage examples:")
        print("  python manage_hr_tools.py --list")
        print("  python manage_hr_tools.py --start-tool job-creation")
        print("  python manage_hr_tools.py --start-agent-tools job-requisition")
        print("  python manage_hr_tools.py --start-all-tools")
        print("  python manage_hr_tools.py --test job-creation")
        print("  python manage_hr_tools.py --cleanup")

if __name__ == "__main__":
    main()