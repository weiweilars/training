#!/usr/bin/env python3
"""
Simple Network Monitor - Monitor inter-agent HTTP traffic
"""

import subprocess
import time
import json
from datetime import datetime

def monitor_agent_connections(duration=30):
    """Monitor connections between agent ports"""

    agent_ports = {
        5040: "MASTER_COORDINATOR",
        5031: "JOB_PIPELINE_TEAM",
        5032: "ACQUISITION_TEAM",
        5033: "EXPERIENCE_TEAM",
        5034: "CLOSING_TEAM",
        5020: "JOB_REQUISITION",
        5021: "SOURCING",
        5022: "RESUME_SCREENING",
        5023: "INTERVIEW_SCHEDULING",
        5024: "ASSESSMENT",
        5025: "BACKGROUND_VERIFICATION",
        5026: "OFFER_MANAGEMENT",
        5027: "COMPLIANCE",
        5028: "COMMUNICATION",
        5029: "ANALYTICS_REPORTING",
        5030: "HR_SUMMARIZATION"
    }

    print(f"🌐 Monitoring inter-agent connections for {duration}s...")
    print("=" * 60)

    start_time = time.time()
    connections_seen = set()

    while time.time() - start_time < duration:
        try:
            # Get current connections
            result = subprocess.run([
                'ss', '-tn', 'state', 'established'
            ], capture_output=True, text=True, timeout=2)

            if result.returncode == 0:
                lines = result.stdout.strip().split('\n')

                for line in lines:
                    if not line.strip() or 'Local' in line:
                        continue

                    # Parse ss output
                    parts = line.split()
                    if len(parts) >= 4:
                        try:
                            local_addr = parts[3]
                            foreign_addr = parts[4]

                            local_port = int(local_addr.split(':')[-1])
                            foreign_port = int(foreign_addr.split(':')[-1])

                            # Check if both are agent ports
                            local_agent = agent_ports.get(local_port)
                            foreign_agent = agent_ports.get(foreign_port)

                            if local_agent and foreign_agent and local_agent != foreign_agent:
                                connection_key = f"{foreign_agent}->{local_agent}"
                                if connection_key not in connections_seen:
                                    timestamp = datetime.now().strftime("%H:%M:%S.%f")[:-3]
                                    print(f"[{timestamp}] 🔄 {foreign_agent} → {local_agent} (ports {foreign_port}→{local_port})")
                                    connections_seen.add(connection_key)

                        except (ValueError, IndexError):
                            continue

            time.sleep(0.2)  # Check every 200ms

        except subprocess.TimeoutExpired:
            continue
        except Exception as e:
            print(f"Error monitoring: {e}")
            continue

    print("=" * 60)
    print(f"✅ Monitoring complete. Found {len(connections_seen)} unique inter-agent connections:")

    if connections_seen:
        for i, conn in enumerate(sorted(connections_seen), 1):
            print(f"  {i}. {conn}")
    else:
        print("  ⚠️  No inter-agent connections detected")
        print("     This could mean:")
        print("     • Agents are handling requests internally")
        print("     • A2A communication is not happening")
        print("     • Network monitoring missed the connections")

    return list(connections_seen)

if __name__ == "__main__":
    import sys
    duration = int(sys.argv[1]) if len(sys.argv) > 1 else 30
    connections = monitor_agent_connections(duration)

    # Save results
    result = {
        "timestamp": datetime.now().isoformat(),
        "duration": duration,
        "connections": connections,
        "total_connections": len(connections)
    }

    with open(f"traces/network_monitor_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json", 'w') as f:
        json.dump(result, f, indent=2)