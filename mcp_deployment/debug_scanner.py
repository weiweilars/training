#!/usr/bin/env python3
"""
Debug the scanner to see what's happening
"""

import ast
from pathlib import Path
from utils.scanner import FastMCPAnalyzer


def debug_file(file_path: Path):
    """Debug a single file"""
    print(f"\n🔍 Debugging: {file_path}")

    # Test scan_file method
    from utils.scanner import MCPToolScanner
    scanner = MCPToolScanner()
    result = scanner.scan_file(file_path)
    print(f"🔧 scan_file result: {result}")

    with open(file_path, 'r') as f:
        content = f.read()

    # Check for FastMCP patterns
    patterns = ["FastMCP", "fastmcp"]
    for pattern in patterns:
        if pattern in content:
            print(f"✅ Found pattern '{pattern}' in file")
        else:
            print(f"❌ Pattern '{pattern}' not found")

    try:
        tree = ast.parse(content)
        analyzer = FastMCPAnalyzer()
        analyzer.visit(tree)

        print(f"📦 Imports found: {analyzer.imports}")
        print(f"🔧 MCP instances found: {analyzer.mcp_instances}")

        if not analyzer.mcp_instances:
            print("\n🔍 Let's check the AST structure...")
            # Look for assignment nodes
            for node in ast.walk(tree):
                if isinstance(node, ast.Assign):
                    for target in node.targets:
                        if isinstance(target, ast.Name):
                            if isinstance(node.value, ast.Call):
                                if hasattr(node.value.func, 'id'):
                                    print(f"   Assignment: {target.id} = {node.value.func.id}()")
                                elif hasattr(node.value.func, 'attr'):
                                    if hasattr(node.value.func.value, 'id'):
                                        print(f"   Assignment: {target.id} = {node.value.func.value.id}.{node.value.func.attr}()")

    except Exception as e:
        print(f"💥 AST parsing error: {e}")


def main():
    weather_file = Path("test_tools/weather_service/weather_server.py")
    calc_file = Path("test_tools/calc_server/math_engine.py")

    if weather_file.exists():
        debug_file(weather_file)

    if calc_file.exists():
        debug_file(calc_file)


if __name__ == "__main__":
    main()