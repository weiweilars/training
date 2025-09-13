#!/bin/bash
# Convenient wrapper for starting MCP tools
cd "$(dirname "$0")"
python scripts/tools/manage_hr_tools.py "$@"