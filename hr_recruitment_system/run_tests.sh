#!/bin/bash
# Convenient wrapper for running tests
cd "$(dirname "$0")"

case "$1" in
    "tools")
        python tests/test_tools.py
        ;;
    "agents")
        python tests/test_individual_agents.py
        ;;
    "coordinators")
        python tests/test_coordinators.py
        ;;
    "master")
        python tests/test_master.py
        ;;
    "logging")
        python tests/test_with_detailed_logging.py
        ;;
    *)
        echo "Usage: $0 {tools|agents|coordinators|master|logging}"
        echo ""
        echo "Available test suites:"
        echo "  tools        - Test MCP tools"
        echo "  agents       - Test individual agents"
        echo "  coordinators - Test team coordinators"
        echo "  master       - Test master coordination"
        echo "  logging      - Test with detailed logging"
        ;;
esac