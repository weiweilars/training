#!/usr/bin/env python3
"""
Port Consistency Checker
Verifies all port configurations across the HR system
"""

import json
import requests
import yaml
import os
from pathlib import Path

def check_running_services():
    """Check what services are actually running"""
    print("=== CURRENTLY RUNNING SERVICES ===")

    # Check coordinators
    coordinator_ports = [5032, 5033, 5034, 5040]
    print("\nCoordinators:")
    for port in coordinator_ports:
        try:
            response = requests.get(f"http://localhost:{port}/.well-known/agent-card.json", timeout=2)
            if response.status_code == 200:
                data = response.json()
                print(f"  Port {port}: ✅ {data['name']}")
            else:
                print(f"  Port {port}: ❌ HTTP {response.status_code}")
        except:
            print(f"  Port {port}: ❌ NOT RUNNING")

    # Check individual agents
    agent_ports = list(range(5020, 5031))
    print("\nIndividual Agents:")
    for port in agent_ports:
        try:
            response = requests.get(f"http://localhost:{port}/.well-known/agent-card.json", timeout=2)
            if response.status_code == 200:
                data = response.json()
                print(f"  Port {port}: ✅ {data['name']}")
            else:
                print(f"  Port {port}: ❌ HTTP {response.status_code}")
        except:
            print(f"  Port {port}: ❌ NOT RUNNING")

def check_config_files():
    """Check all configuration files for port references"""
    print("\n=== CONFIGURATION FILE ANALYSIS ===")

    issues = []

    # Check coordinator configs
    coordinator_dir = Path("hr_recruitment_agents/team_coordinators")
    if coordinator_dir.exists():
        print(f"\nChecking {coordinator_dir}:")
        for config_file in coordinator_dir.glob("*.yaml"):
            print(f"  📁 {config_file.name}")
            with open(config_file, 'r') as f:
                content = f.read()

            # Look for port references
            import re
            port_refs = re.findall(r'localhost:(\d+)', content)
            if port_refs:
                print(f"    Port references: {', '.join(port_refs)}")

                # Check for invalid ports
                for port in port_refs:
                    port_num = int(port)
                    if port_num == 5031:  # Known problematic port
                        issues.append(f"{config_file.name}: References non-existent port 5031")
            else:
                print(f"    No port references found")

    # Check quick_status.py
    status_file = Path("scripts/monitoring/quick_status.py")
    if status_file.exists():
        print(f"\nChecking {status_file.name}:")
        with open(status_file, 'r') as f:
            content = f.read()

        # Extract coordinator ports from quick_status.py
        import re
        coordinator_match = re.search(r'coordinator_ports = \{([^}]+)\}', content, re.DOTALL)
        if coordinator_match:
            coordinator_section = coordinator_match.group(1)
            port_matches = re.findall(r':\s*(\d+)', coordinator_section)
            print(f"    Coordinator ports in status checker: {', '.join(port_matches)}")

    return issues

def check_start_scripts():
    """Check start scripts for port assignments"""
    print("\n=== START SCRIPT ANALYSIS ===")

    # Check if start scripts exist and what they reference
    scripts = [
        "start_agents.sh",
        "start_coordinators.sh",
        "start_tools.sh"
    ]

    for script in scripts:
        if Path(script).exists():
            print(f"\n📁 {script}:")
            with open(script, 'r') as f:
                content = f.read()

            # Look for port references
            import re
            port_refs = re.findall(r'(\d{4,5})', content)
            if port_refs:
                unique_ports = sorted(set(port_refs))
                print(f"    Port references: {', '.join(unique_ports)}")

def main():
    print("🔍 HR SYSTEM PORT CONSISTENCY CHECK")
    print("=" * 50)

    # Change to script directory
    os.chdir(Path(__file__).parent)

    # Check running services
    check_running_services()

    # Check configuration files
    issues = check_config_files()

    # Check start scripts
    check_start_scripts()

    # Summary
    print("\n=== SUMMARY ===")
    if issues:
        print("❌ ISSUES FOUND:")
        for issue in issues:
            print(f"  • {issue}")
    else:
        print("✅ No obvious port inconsistencies found in configs")

    print("\n📋 RECOMMENDED PORT MAPPING:")
    print("  Individual Agents: 5020-5029 (10 agents)")
    print("  Team Coordinators: 5032-5034 (3 teams)")
    print("  Master Coordinator: 5040")
    print("  MCP Tools: 8051-8143 (28 tools)")

if __name__ == "__main__":
    main()