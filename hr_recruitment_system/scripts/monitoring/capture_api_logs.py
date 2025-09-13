#!/usr/bin/env python3
"""
API Call Logger for HR System
Captures HTTP requests and tool calls during testing
"""

import subprocess
import time
import os
import json
import signal
import sys
from datetime import datetime

class APILogger:
    """Capture API calls and tool usage during tests"""

    def __init__(self, session_id=None):
        self.session_id = session_id or f"api_logs_{int(time.time())}"
        self.logs_dir = f"../../test_logs/{self.session_id}"
        os.makedirs(self.logs_dir, exist_ok=True)
        self.monitoring_processes = {}

    def start_port_monitoring(self, port_ranges, component_type):
        """Start monitoring HTTP traffic on specific port ranges"""

        for port_range in port_ranges:
            if isinstance(port_range, int):
                ports = [port_range]
            elif isinstance(port_range, tuple):
                ports = list(range(port_range[0], port_range[1] + 1))
            else:
                ports = port_range

            for port in ports[:5]:  # Limit to first 5 ports per range to avoid too many processes
                self.start_single_port_monitor(port, component_type)

    def start_single_port_monitor(self, port, component_type):
        """Monitor a single port for HTTP requests"""
        log_file = f"{self.logs_dir}/{component_type}_port_{port}.log"

        # Use netstat and ss to monitor connections
        monitor_script = f'''#!/bin/bash
LOG_FILE="{log_file}"
PORT={port}
COMPONENT="{component_type}"

echo "$(date): Starting API monitoring for $COMPONENT on port $PORT" > "$LOG_FILE"

while true; do
    # Check if port is active
    if netstat -tln 2>/dev/null | grep ":$PORT " > /dev/null; then
        echo "$(date): Port $PORT is active ($COMPONENT)" >> "$LOG_FILE"

        # Monitor connections
        CONNECTIONS=$(ss -tuln | grep ":$PORT " | wc -l)
        if [ "$CONNECTIONS" -gt 0 ]; then
            echo "$(date): Active connections: $CONNECTIONS" >> "$LOG_FILE"
        fi

        # Try to capture any HTTP activity using lsof
        if command -v lsof > /dev/null; then
            PID=$(lsof -ti:$PORT 2>/dev/null | head -1)
            if [ ! -z "$PID" ]; then
                PROC_NAME=$(ps -p $PID -o comm= 2>/dev/null || echo "unknown")
                echo "$(date): Process: $PROC_NAME (PID: $PID)" >> "$LOG_FILE"

                # Check if process is using significant CPU (indicates activity)
                CPU=$(ps -p $PID -o %cpu= 2>/dev/null | xargs)
                if [ ! -z "$CPU" ] && [ $(echo "$CPU > 1" | bc 2>/dev/null || echo 0) -eq 1 ]; then
                    echo "$(date): High CPU activity detected: $CPU%" >> "$LOG_FILE"
                fi
            fi
        fi
    else
        echo "$(date): Port $PORT inactive" >> "$LOG_FILE"
    fi

    sleep 10  # Check every 10 seconds
done
'''

        # Write the script
        script_file = f"{self.logs_dir}/monitor_port_{port}.sh"
        with open(script_file, 'w') as f:
            f.write(monitor_script)

        # Make executable
        os.chmod(script_file, 0o755)

        # Start monitoring
        try:
            proc = subprocess.Popen(['/bin/bash', script_file],
                                  stdout=subprocess.DEVNULL,
                                  stderr=subprocess.DEVNULL)
            self.monitoring_processes[f"port_{port}"] = proc
            print(f"📊 Monitoring port {port} ({component_type})")
        except Exception as e:
            print(f"⚠️  Could not start monitoring port {port}: {e}")

    def start_http_request_capture(self):
        """Capture HTTP requests using netstat/ss monitoring"""

        print(f"🔍 Starting HTTP request monitoring...")

        # MCP Tools (sample of ports)
        mcp_ports = [8051, 8061, 8071, 8081, 8091, 8101]  # Sample
        self.start_port_monitoring(mcp_ports, "mcp_tools")

        # Individual Agents
        agent_ports = list(range(5020, 5031))
        self.start_port_monitoring(agent_ports, "agents")

        # Coordinators
        coordinator_ports = [5032, 5033, 5034, 5040]
        self.start_port_monitoring(coordinator_ports, "coordinators")

    def create_real_time_summary(self):
        """Create a script to show real-time API activity"""

        summary_script = f'''#!/bin/bash
LOGS_DIR="{self.logs_dir}"

echo "🔍 HR System API Activity Monitor"
echo "================================="
echo "📁 Logs Directory: $LOGS_DIR"
echo "🕒 Started: $(date)"
echo ""

while true; do
    clear
    echo "🔍 HR System API Activity Monitor - $(date)"
    echo "================================="
    echo ""

    echo "🛠️  MCP Tools Activity:"
    for log in $LOGS_DIR/mcp_tools_port_*.log; do
        if [ -f "$log" ]; then
            port=$(basename "$log" | grep -o 'port_[0-9]*' | cut -d'_' -f2)
            last_line=$(tail -1 "$log" 2>/dev/null || echo "No activity")
            echo "  Port $port: $last_line"
        fi
    done | head -5

    echo ""
    echo "🤖 Agents Activity:"
    for log in $LOGS_DIR/agents_port_*.log; do
        if [ -f "$log" ]; then
            port=$(basename "$log" | grep -o 'port_[0-9]*' | cut -d'_' -f2)
            last_line=$(tail -1 "$log" 2>/dev/null || echo "No activity")
            echo "  Port $port: $last_line"
        fi
    done

    echo ""
    echo "🎯 Coordinators Activity:"
    for log in $LOGS_DIR/coordinators_port_*.log; do
        if [ -f "$log" ]; then
            port=$(basename "$log" | grep -o 'port_[0-9]*' | cut -d'_' -f2)
            last_line=$(tail -1 "$log" 2>/dev/null || echo "No activity")
            echo "  Port $port: $last_line"
        fi
    done

    echo ""
    echo "Press Ctrl+C to stop monitoring..."
    sleep 5
done
'''

        monitor_file = f"{self.logs_dir}/real_time_monitor.sh"
        with open(monitor_file, 'w') as f:
            f.write(summary_script)
        os.chmod(monitor_file, 0o755)

        print(f"📊 Real-time monitor created: {monitor_file}")
        print(f"   Run with: bash {monitor_file}")

        return monitor_file

    def create_log_analyzer(self):
        """Create a script to analyze the captured logs"""

        analyzer_script = f'''#!/usr/bin/env python3
import os
import re
from datetime import datetime
from collections import defaultdict

def analyze_logs():
    logs_dir = "{self.logs_dir}"
    print(f"📊 Analyzing API logs in {{logs_dir}}")
    print("=" * 60)

    # Analyze each component type
    components = {{"mcp_tools": [], "agents": [], "coordinators": []}}

    for filename in os.listdir(logs_dir):
        if filename.endswith('.log'):
            component_type = filename.split('_port_')[0]
            if component_type in components:
                components[component_type].append(filename)

    for comp_type, log_files in components.items():
        if log_files:
            print(f"\\n🔍 {{comp_type.upper()}} Activity Summary:")
            print("-" * 40)

            for log_file in sorted(log_files)[:10]:  # Show first 10
                log_path = os.path.join(logs_dir, log_file)
                port = log_file.split('_port_')[1].split('.')[0]

                try:
                    with open(log_path, 'r') as f:
                        lines = f.readlines()

                    active_count = sum(1 for line in lines if 'active' in line.lower())
                    connection_count = sum(1 for line in lines if 'connection' in line.lower())
                    activity_count = sum(1 for line in lines if 'activity' in line.lower())

                    status = "🟢 Active" if active_count > 0 else "🔴 Inactive"
                    print(f"  Port {{port}}: {{status}} ({{len(lines)}} log entries)")
                    if connection_count > 0:
                        print(f"    └─ Connections detected: {{connection_count}}")
                    if activity_count > 0:
                        print(f"    └─ High activity periods: {{activity_count}}")

                except Exception as e:
                    print(f"  Port {{port}}: ❌ Error reading log: {{e}}")

    print(f"\\n📋 Analysis complete. Check individual log files for details.")
    print(f"📁 Logs location: {{logs_dir}}")

if __name__ == "__main__":
    analyze_logs()
'''

        analyzer_file = f"{self.logs_dir}/analyze_logs.py"
        with open(analyzer_file, 'w') as f:
            f.write(analyzer_script)
        os.chmod(analyzer_file, 0o755)

        print(f"📈 Log analyzer created: {analyzer_file}")
        return analyzer_file

    def stop_monitoring(self):
        """Stop all monitoring processes"""
        print(f"🛑 Stopping API monitoring...")

        for name, proc in self.monitoring_processes.items():
            try:
                proc.terminate()
                proc.wait(timeout=3)
                print(f"✅ Stopped {name}")
            except:
                try:
                    proc.kill()
                    print(f"🔪 Force killed {name}")
                except:
                    print(f"⚠️  Could not stop {name}")

        # Clean up script files
        for filename in os.listdir(self.logs_dir):
            if filename.startswith('monitor_port_') and filename.endswith('.sh'):
                try:
                    os.remove(f"{self.logs_dir}/{filename}")
                except:
                    pass

def main():
    """Start API logging for current test session"""
    logger = APILogger()

    try:
        print(f"🚀 Starting HR System API Monitoring")
        print(f"📁 Logs Directory: {logger.logs_dir}")

        logger.start_http_request_capture()

        # Create monitoring tools
        monitor_script = logger.create_real_time_summary()
        analyzer_script = logger.create_log_analyzer()

        print(f"\\n🔧 Monitoring Tools Created:")
        print(f"  📊 Real-time monitor: bash {monitor_script}")
        print(f"  📈 Log analyzer: python {analyzer_script}")
        print(f"\\n⏳ Monitoring started. Run your tests now...")
        print(f"   Press Ctrl+C to stop monitoring")

        # Keep running until interrupted
        while True:
            time.sleep(10)

    except KeyboardInterrupt:
        print(f"\\n🛑 Monitoring stopped by user")
    finally:
        logger.stop_monitoring()

        print(f"\\n📋 Final Summary:")
        print(f"  📁 All logs saved in: {logger.logs_dir}")
        print(f"  📈 Analyze with: python {logger.logs_dir}/analyze_logs.py")

if __name__ == "__main__":
    main()