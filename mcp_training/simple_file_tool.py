#!/usr/bin/env python3
"""
Simple File Tool - Training Example
Single-page MCP tool for basic file operations
"""

import os
import json
from datetime import datetime
from pathlib import Path

try:
    from fastmcp import FastMCP
except ImportError:
    print("❌ ERROR: FastMCP not found!")
    print("📦 Install required dependency:")
    print("   pip install fastmcp")
    print("💡 Or run: pip install -r requirements.txt")
    exit(1)

# Configuration
stateless_mode = os.getenv("STATELESS_HTTP", "true").lower() == "true"

# Create MCP instance
mcp = FastMCP(name="simple-file-tool")

@mcp.tool()
def list_files(directory: str = ".") -> str:
    """
    List files in a directory
    
    Args:
        directory: Directory path (default: current directory)
        
    Returns:
        List of files in JSON format
    """
    try:
        path = Path(directory)
        
        if not path.exists():
            return json.dumps({"error": f"Directory does not exist: {directory}"})
        
        files = []
        for item in path.iterdir():
            if item.is_file():
                files.append({
                    "name": item.name,
                    "size_bytes": item.stat().st_size,
                    "modified": datetime.fromtimestamp(item.stat().st_mtime).isoformat()
                })
        
        return json.dumps({
            "directory": directory,
            "file_count": len(files),
            "files": files,
            "listed_at": datetime.now().isoformat()
        }, indent=2)
        
    except Exception as e:
        return json.dumps({"error": f"Failed to list files: {str(e)}"})

@mcp.tool()
def read_file(filepath: str) -> str:
    """
    Read file contents
    
    Args:
        filepath: Path to the file to read
        
    Returns:
        File contents in JSON format
    """
    try:
        path = Path(filepath)
        
        if not path.exists():
            return json.dumps({"error": f"File does not exist: {filepath}"})
        
        with open(filepath, 'r', encoding='utf-8') as f:
            content = f.read()
        
        return json.dumps({
            "filepath": filepath,
            "content": content,
            "size_bytes": len(content.encode()),
            "read_at": datetime.now().isoformat()
        }, indent=2)
        
    except Exception as e:
        return json.dumps({"error": f"Failed to read file: {str(e)}"})

@mcp.tool()
def write_file(filepath: str, content: str) -> str:
    """
    Write content to a file
    
    Args:
        filepath: Path where to write the file
        content: Content to write
        
    Returns:
        Write operation status
    """
    try:
        path = Path(filepath)
        path.parent.mkdir(parents=True, exist_ok=True)
        
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(content)
        
        return json.dumps({
            "status": "success",
            "filepath": filepath,
            "content_length": len(content),
            "written_at": datetime.now().isoformat()
        }, indent=2)
        
    except Exception as e:
        return json.dumps({"error": f"Failed to write file: {str(e)}"})

if __name__ == "__main__":
    print(f"Simple File Tool - {mcp.name}")
    print("Starting MCP server...")
    mcp.run(stateless_http=stateless_mode)