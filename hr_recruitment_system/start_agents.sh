#!/bin/bash
# Convenient wrapper for starting SK agents
cd "$(dirname "$0")"
python scripts/agents/run_sk_agents.py "$@"