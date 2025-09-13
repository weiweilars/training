#!/bin/bash
# Convenient wrapper for starting coordinators
cd "$(dirname "$0")"
python scripts/agents/run_coordinators.py "$@"