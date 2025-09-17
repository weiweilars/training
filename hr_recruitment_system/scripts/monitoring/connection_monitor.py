#!/usr/bin/env python3
"""
Connection Monitor for HR Recruitment System
Monitors active network connections to detect agent-to-agent communication
Works without modifying agents or requiring sudo (uses netstat/ss)
"""

import asyncio
import aiohttp
import json
import time
import subprocess
import argparse
from datetime import datetime
from typing import Dict, List, Set, Tuple
from colorama import init, Fore, Style
import re

# Initialize colorama
init(autoreset=True)

class ConnectionMonitor:
    """Monitors network connections between agents"""

    def __init__(self):
        self.agent_ports = {
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
        # Add MCP tool ports
        for port in range(8051, 8144):
            self.agent_ports[port] = f"MCP_TOOL_{port}"

        self.connections = []
        self.connection_history = []

    def get_agent_name(self, port: int) -> str:
        """Get agent name from port"""
        return self.agent_ports.get(port, f"PORT_{port}")

    def capture_connections(self) -> List[Tuple[int, int]]:
        """Capture current TCP connections"""
        connections = set()

        try:
            # Try using ss first (faster than netstat)
            result = subprocess.run(
                ["ss", "-tn", "state", "established"],
                capture_output=True,
                text=True,
                timeout=2
            )
            output = result.stdout
        except (subprocess.CalledProcessError, FileNotFoundError, subprocess.TimeoutExpired):
            try:
                # Fallback to netstat
                result = subprocess.run(
                    ["netstat", "-tn"],
                    capture_output=True,
                    text=True,
                    timeout=2
                )
                output = result.stdout
            except:
                return []

        # Parse connections
        for line in output.split('\n'):
            # Look for localhost connections
            if '127.0.0.1' in line or 'localhost' in line:
                # Extract source and destination ports
                match = re.search(r'127\.0\.0\.1:(\d+)\s+127\.0\.0\.1:(\d+)', line)
                if match:
                    src_port = int(match.group(1))
                    dst_port = int(match.group(2))

                    # Filter for our agent ports
                    if src_port in self.agent_ports and dst_port in self.agent_ports:
                        connections.add((src_port, dst_port))

        return list(connections)

    def detect_new_connections(self, current_connections: List[Tuple[int, int]]) -> List[Tuple[int, int]]:
        """Detect new connections since last check"""
        current_set = set(current_connections)
        previous_set = set(self.connections)

        new_connections = current_set - previous_set
        self.connections = current_connections

        # Add to history
        for conn in new_connections:
            self.connection_history.append({
                'timestamp': datetime.now().isoformat(),
                'source_port': conn[0],
                'target_port': conn[1],
                'source_agent': self.get_agent_name(conn[0]),
                'target_agent': self.get_agent_name(conn[1])
            })

        return list(new_connections)


class ConnectionTracer:
    """Traces agent communication using connection monitoring"""

    def __init__(self, master_url: str = "http://localhost:5040"):
        self.master_url = master_url
        self.monitor = ConnectionMonitor()
        self.events = []
        self.a2a_communications = []

    async def trace_query(self, query: str, duration: int = 30):
        """Execute query and monitor connections"""
        print(f"\n{Fore.CYAN}=== CONNECTION MONITOR TRACER ==={Style.RESET_ALL}")
        print(f"Query: {query}")
        print(f"Master URL: {self.master_url}")
        print(f"Monitor Duration: {duration}s")
        print()

        # Start monitoring in background
        monitor_task = asyncio.create_task(self._monitor_connections(duration))

        try:
            # Check master agent
            print(f"{Fore.YELLOW}🔍 Checking master agent...{Style.RESET_ALL}")
            async with aiohttp.ClientSession() as session:
                try:
                    async with session.get(f"{self.master_url}/.well-known/agent-card.json") as response:
                        if response.status == 200:
                            print(f"{Fore.GREEN}✓ Master agent is online{Style.RESET_ALL}")
                        else:
                            print(f"{Fore.RED}✗ Master agent returned status {response.status}{Style.RESET_ALL}")
                            return
                except Exception as e:
                    print(f"{Fore.RED}✗ Cannot connect to master: {e}{Style.RESET_ALL}")
                    return

                # Send query
                print(f"\n{Fore.GREEN}🚀 Sending query to master...{Style.RESET_ALL}\n")

                payload = {
                    "jsonrpc": "2.0",
                    "method": "message/send",
                    "params": {
                        "message": {
                            "id": f"conn_trace_{int(time.time())}",
                            "timestamp": datetime.now().isoformat(),
                            "role": "user",
                            "content": query
                        }
                    },
                    "id": f"conn_trace_{int(time.time())}"
                }

                start_time = time.time()

                # Log request
                self.events.append({
                    'timestamp': datetime.now().isoformat(),
                    'type': 'CLIENT_REQUEST',
                    'target': 'MASTER_COORDINATOR',
                    'payload': payload
                })

                async with session.post(self.master_url, json=payload) as response:
                    result = await response.json()
                    duration_ms = (time.time() - start_time) * 1000

                    # Log response
                    self.events.append({
                        'timestamp': datetime.now().isoformat(),
                        'type': 'CLIENT_RESPONSE',
                        'source': 'MASTER_COORDINATOR',
                        'status': response.status,
                        'duration_ms': duration_ms,
                        'response': result
                    })

                    print(f"{Fore.GREEN}✓ Response received in {duration_ms:.1f}ms{Style.RESET_ALL}")

                    # Display response preview
                    if result.get('result', {}).get('result', {}).get('message'):
                        content = result['result']['result']['message'].get('content', '')
                        print(f"\n{Fore.CYAN}Response Preview:{Style.RESET_ALL}")
                        print(f"{content[:400]}...")

        finally:
            # Wait for monitoring to complete
            await monitor_task

            # Print results
            self._print_results()

    async def _monitor_connections(self, duration: int):
        """Monitor connections for the specified duration"""
        print(f"\n{Fore.YELLOW}📡 Monitoring agent connections...{Style.RESET_ALL}\n")

        end_time = time.time() + duration
        check_interval = 0.5  # Check every 500ms

        while time.time() < end_time:
            # Capture current connections
            current = self.monitor.capture_connections()

            # Detect new connections
            new_connections = self.monitor.detect_new_connections(current)

            # Log new connections
            for src_port, dst_port in new_connections:
                src_agent = self.monitor.get_agent_name(src_port)
                dst_agent = self.monitor.get_agent_name(dst_port)

                # Skip if it's a response (reverse connection)
                if (dst_port, src_port) not in [(c['source_port'], c['target_port'])
                                                for c in self.a2a_communications]:
                    self.a2a_communications.append({
                        'timestamp': datetime.now().isoformat(),
                        'source_port': src_port,
                        'target_port': dst_port,
                        'source_agent': src_agent,
                        'target_agent': dst_agent
                    })

                    # Display in real-time
                    timestamp = datetime.now().strftime('%H:%M:%S.%f')[:-3]
                    print(f"{Fore.MAGENTA}[{timestamp}] A2A DETECTED: {src_agent} → {dst_agent}")
                    print(f"    Connection: localhost:{src_port} → localhost:{dst_port}{Style.RESET_ALL}")

            await asyncio.sleep(check_interval)

        print(f"\n{Fore.YELLOW}📡 Monitoring complete{Style.RESET_ALL}")

    def _print_results(self):
        """Print monitoring results"""
        print(f"\n{Fore.CYAN}{'=' * 60}")
        print(f"=== CONNECTION MONITORING RESULTS ===")
        print(f"{'=' * 60}{Style.RESET_ALL}\n")

        if self.a2a_communications:
            print(f"{Fore.GREEN}✅ Agent-to-Agent Communications Detected:{Style.RESET_ALL}\n")

            # Group by source agent
            comm_by_source = {}
            for comm in self.a2a_communications:
                source = comm['source_agent']
                if source not in comm_by_source:
                    comm_by_source[source] = []
                comm_by_source[source].append(comm['target_agent'])

            # Display communication flow
            for source, targets in sorted(comm_by_source.items()):
                print(f"  {Fore.CYAN}{source}:{Style.RESET_ALL}")
                for target in set(targets):
                    print(f"    → {target}")

            print(f"\n{Fore.GREEN}Total A2A connections: {len(self.a2a_communications)}{Style.RESET_ALL}")

            # Show communication sequence
            print(f"\n{Fore.CYAN}Communication Sequence:{Style.RESET_ALL}")
            for i, comm in enumerate(self.a2a_communications[:10], 1):
                timestamp = comm['timestamp'].split('T')[1][:12]
                print(f"  {i}. [{timestamp}] {comm['source_agent']} → {comm['target_agent']}")

            if len(self.a2a_communications) > 10:
                print(f"  ... and {len(self.a2a_communications) - 10} more")

        else:
            print(f"{Fore.YELLOW}⚠️  No A2A communications detected{Style.RESET_ALL}")
            print(f"\nPossible reasons:")
            print(f"  1. The query was handled entirely by the Master Coordinator")
            print(f"  2. Agent communication happened too quickly to detect")
            print(f"  3. Agents are using a different communication method")
            print(f"\n{Fore.CYAN}Tip: Try a more complex query that requires multiple teams{Style.RESET_ALL}")

        # Save trace
        trace_data = {
            'events': self.events,
            'a2a_communications': self.a2a_communications,
            'connection_history': self.monitor.connection_history
        }

        filename = f"traces/connection_trace_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        with open(filename, 'w') as f:
            json.dump(trace_data, f, indent=2)

        print(f"\n{Fore.CYAN}Full trace saved to: {filename}{Style.RESET_ALL}")


async def main():
    parser = argparse.ArgumentParser(
        description='Connection Monitor for A2A Communication Tracing'
    )
    parser.add_argument('query', nargs='?',
                       default="I have 25 applications for DevOps Engineer. Screen resumes and schedule interviews.",
                       help='Query to send to master agent')
    parser.add_argument('--duration', type=int, default=30,
                       help='Monitoring duration in seconds')
    parser.add_argument('--master-url', default='http://localhost:5040/',
                       help='Master coordinator URL')

    args = parser.parse_args()

    print(f"{Fore.CYAN}Connection Monitor - A2A Communication Tracer{Style.RESET_ALL}")
    print(f"This tool monitors network connections to detect agent-to-agent communication")
    print(f"No sudo required, no agent modification needed!\n")

    tracer = ConnectionTracer(args.master_url)
    await tracer.trace_query(args.query, args.duration)


if __name__ == "__main__":
    asyncio.run(main())