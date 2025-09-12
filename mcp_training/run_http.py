#!/usr/bin/env python3
"""
Universal HTTP Runner for Simple MCP Tools
Runs any of the simple MCP tools as HTTP servers for training purposes
"""

import sys
import os
import argparse
from pathlib import Path

def main():
    """Main entry point for running MCP tools via HTTP"""
    
    # Available tools
    available_tools = {
        "file": "simple_file_tool.py",
        "weather": "simple_weather_tool.py",
        "calculator": "simple_calculator_tool.py"
    }
    
    parser = argparse.ArgumentParser(
        description="Run simple MCP tools as HTTP servers for training",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=f"""
Available tools:
  file        - Simple file operations (list, read, write)
  weather     - Simple weather information (current, forecast, convert)
  calculator  - Simple calculator operations (basic math, advanced functions, expressions)

Examples:
  python run_http.py file
  python run_http.py weather --port 8002 --host 0.0.0.0
  python run_http.py calculator
        """
    )
    
    parser.add_argument(
        "tool",
        nargs='?',
        choices=list(available_tools.keys()),
        help="Name of the MCP tool to run"
    )
    
    parser.add_argument(
        "--port", "-p",
        type=int,
        default=8000,
        help="Port to run the HTTP server on (default: 8000)"
    )
    
    parser.add_argument(
        "--host",
        default="localhost",
        help="Host to bind the server to (default: localhost)"
    )
    
    parser.add_argument(
        "--list-tools", "-l",
        action="store_true",
        help="List all available tools and exit"
    )
    
    args = parser.parse_args()
    
    if args.list_tools:
        print("Available MCP tools:")
        for tool_name, tool_file in available_tools.items():
            print(f"  {tool_name:10} - {tool_file}")
        return
    
    if not args.tool:
        print("Error: tool argument is required (unless using --list-tools)")
        parser.print_help()
        return 1
    
    # Get the tool file path
    tool_file = available_tools[args.tool]
    tool_path = Path(__file__).parent / tool_file
    
    if not tool_path.exists():
        print(f"Error: Tool file not found: {tool_path}")
        return 1
    
    print(f"Starting {args.tool} MCP tool...")
    print(f"Tool file: {tool_file}")
    print(f"Server URL: http://{args.host}:{args.port}")
    print("Press Ctrl+C to stop the server")
    print("-" * 50)
    
    # Environment variables can be set by user when running the script
    
    # Import and run the selected tool
    try:
        # Add current directory to Python path so we can import the tool modules
        current_dir = str(Path(__file__).parent)
        if current_dir not in sys.path:
            sys.path.insert(0, current_dir)
        
        # Import the tool module
        module_name = tool_file.replace('.py', '')
        module = __import__(module_name)
        
        # Override the run method to use our specified port and host
        original_run = module.mcp.run
        
        def custom_run(transport="http", port=None, host=None, stateless_http=None):
            # Read STATELESS_HTTP environment variable directly
            env_stateless = os.getenv("STATELESS_HTTP", "true").lower() == "true"
            return original_run(
                transport="http", 
                port=args.port, 
                host=args.host,
                stateless_http=env_stateless
            )
        
        module.mcp.run = custom_run
        
        # Run the tool
        print(f"Initializing {args.tool} tool...")
        module.mcp.run()
        
    except KeyboardInterrupt:
        print(f"\n{args.tool.title()} MCP HTTP Server stopped.")
        return 0
    except ImportError as e:
        print(f"Error importing tool module: {e}")
        print("Make sure fastmcp is installed: pip install fastmcp")
        return 1
    except Exception as e:
        print(f"Error running {args.tool} tool: {e}")
        return 1

if __name__ == "__main__":
    exit_code = main()
    if exit_code:
        sys.exit(exit_code)