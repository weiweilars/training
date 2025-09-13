#!/usr/bin/env python3
"""
Generic HR MCP Tool HTTP Server
Run any HR MCP tool with configurable HTTP transport (stateless or stateful)
"""

import sys
import os
import argparse
import importlib.util
from hr_tools_config import HR_TOOLS

def load_mcp_from_file(file_path):
    """Load MCP instance from a Python file"""
    if not os.path.exists(file_path):
        raise FileNotFoundError(f"Tool file not found: {file_path}")
    
    # Load the module
    spec = importlib.util.spec_from_file_location("mcp_module", file_path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    
    # Find the MCP instance (usually named 'mcp')
    if hasattr(module, 'mcp'):
        return module.mcp
    else:
        raise AttributeError(f"No 'mcp' instance found in {file_path}")

def run_tool_http(tool_name, port=None, stateless=True, host="0.0.0.0"):
    """Run an HR tool with HTTP transport"""
    
    if tool_name not in HR_TOOLS:
        print(f"❌ Unknown tool: {tool_name}")
        print(f"Available tools: {', '.join(HR_TOOLS.keys())}")
        return False
    
    tool_config = HR_TOOLS[tool_name]
    tool_port = port or tool_config["port"]
    tool_file = tool_config["file"]
    
    print(f"🚀 Starting {tool_name} HTTP Server")
    print(f"📁 File: {tool_file}")
    print(f"🌐 URL: http://{host}:{tool_port}/mcp")
    print(f"🔧 Mode: {'Stateless' if stateless else 'Stateful'} HTTP")
    print("-" * 60)
    
    try:
        # Load the MCP instance from the tool file
        mcp_instance = load_mcp_from_file(tool_file)
        
        # Override the run method to properly pass stateless_http parameter
        original_run = mcp_instance.run
        
        def custom_run(transport="http", port=None, host=None, stateless_http=None):
            return original_run(
                transport="http", 
                port=tool_port, 
                host=host,
                stateless_http=stateless
            )
        
        mcp_instance.run = custom_run
        
        # Run the server
        print(f"🎯 Starting server on http://{host}:{tool_port}")
        print(f"🔧 Stateless HTTP: {stateless}")
        mcp_instance.run()
        
    except KeyboardInterrupt:
        print(f"\n✅ {tool_name} HTTP server stopped")
        return True
    except Exception as e:
        print(f"❌ Error running {tool_name}: {e}")
        return False

def list_tools():
    """List all available HR tools"""
    print("🔧 Available HR MCP Tools:")
    print("=" * 60)
    for tool_name, config in HR_TOOLS.items():
        print(f"  {tool_name:<25} Port {config['port']:<6} {config['file']}")
    print(f"\nTotal: {len(HR_TOOLS)} tools")

def main():
    parser = argparse.ArgumentParser(description="Run HR MCP tools with HTTP transport")
    parser.add_argument("tool", nargs="?", choices=list(HR_TOOLS.keys()), 
                       help="HR tool to run")
    parser.add_argument("--list", action="store_true", 
                       help="List available tools")
    parser.add_argument("--port", type=int, 
                       help="Custom port (overrides default)")
    parser.add_argument("--stateful", action="store_true", 
                       help="Use stateful HTTP mode (with sessions, default is stateless)")
    parser.add_argument("--host", default="0.0.0.0", 
                       help="Host to bind to (default: 0.0.0.0)")
    
    args = parser.parse_args()
    
    if args.list:
        list_tools()
        return
    
    if not args.tool:
        print("❌ Please specify a tool to run or use --list")
        parser.print_help()
        return
    
    success = run_tool_http(
        tool_name=args.tool,
        port=args.port,
        stateless=not args.stateful,  # Default to stateless (True) unless --stateful is specified
        host=args.host
    )
    
    if not success:
        sys.exit(1)

if __name__ == "__main__":
    main()