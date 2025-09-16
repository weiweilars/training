#!/usr/bin/env python3
"""
Network-Level HR System Query Tracer
Captures all HTTP traffic between agents using network monitoring and HTTP proxying
"""

import asyncio
import json
import time
import argparse
import sys
import os
from datetime import datetime
from typing import Dict, List, Any, Optional
import aiohttp
import subprocess
from pathlib import Path
from colorama import init, Fore, Back, Style
import signal

# Initialize colorama
init(autoreset=True)

class NetworkTracer:
    """Enhanced tracer that captures inter-agent HTTP traffic"""

    def __init__(self, output_file: str = None):
        self.events = []
        self.start_time = time.time()
        self.output_file = output_file
        self.monitoring = False
        self.agent_sequence = []
        self.inter_agent_calls = []

        # All HR system agent ports
        self.agent_ports = {
            "MASTER_COORDINATOR": 5040,
            "JOB_PIPELINE_TEAM": 5031,
            "ACQUISITION_TEAM": 5032,
            "EXPERIENCE_TEAM": 5033,
            "CLOSING_TEAM": 5034,
            "JOB_REQUISITION": 5020,
            "SOURCING": 5021,
            "RESUME_SCREENING": 5022,
            "COMMUNICATION": 5028,
            "INTERVIEW_SCHEDULING": 5023,
            "ASSESSMENT": 5024,
            "BACKGROUND_VERIFICATION": 5025,
            "OFFER_MANAGEMENT": 5026,
            "ANALYTICS_REPORTING": 5029,
            "COMPLIANCE": 5027,
            "HR_SUMMARIZATION": 5030
        }

        # Reverse mapping for port -> agent name
        self.port_to_agent = {port: name for name, port in self.agent_ports.items()}

    def log_event(self, event_type: str, source: str, target: str, **kwargs):
        """Log a trace event"""
        event = {
            "timestamp": datetime.now().isoformat(),
            "event_id": f"{event_type.lower()}_{int(time.time() * 1000)}",
            "event_type": event_type,
            "source": source,
            "target": target,
            **kwargs
        }
        self.events.append(event)
        self._print_event(event)

        # Track agent interactions
        if event_type in ["HTTP_REQUEST", "INTER_AGENT_CALL"] and target != "UNKNOWN":
            if target not in self.agent_sequence:
                self.agent_sequence.append(target)
            if source not in self.agent_sequence and source not in ["QUERY_CLIENT", "MONITOR"]:
                self.agent_sequence.append(source)

        if event_type == "INTER_AGENT_CALL":
            self.inter_agent_calls.append({
                "timestamp": event["timestamp"],
                "source": source,
                "target": target,
                "method": kwargs.get("method", "UNKNOWN"),
                "url": kwargs.get("url", ""),
                "duration_ms": kwargs.get("duration_ms", 0)
            })

    def _print_event(self, event):
        """Print event in real-time"""
        timestamp = event["timestamp"][-12:-3]  # Show only time part
        source = event["source"]
        target = event["target"]
        event_type = event["event_type"]

        if event_type == "HTTP_REQUEST":
            method = event.get("method", "")
            url = event.get("url", "")
            print(f"[{timestamp}] {Fore.BLUE}{event_type}{Style.RESET_ALL} {source} → {target} {method} {url}")
        elif event_type == "HTTP_RESPONSE":
            status = event.get("status_code", "")
            duration = event.get("duration_ms", 0)
            print(f"[{timestamp}] {Fore.GREEN}{event_type}{Style.RESET_ALL} {source} → {target} {status} ({duration:.1f}ms)")
        elif event_type == "INTER_AGENT_CALL":
            method = event.get("method", "")
            print(f"[{timestamp}] {Fore.YELLOW}🔄 AGENT_CALL{Style.RESET_ALL} {source} → {target} {method}")
        else:
            print(f"[{timestamp}] {event_type} {source} → {target}")

    async def monitor_network_traffic(self, duration: int = 30):
        """Monitor network traffic for inter-agent HTTP calls"""
        print(f"{Fore.CYAN}🌐 Starting network monitoring for {duration}s...{Style.RESET_ALL}")
        self.monitoring = True

        # Start background monitoring
        monitor_task = asyncio.create_task(self._network_monitor_loop())

        # Wait for specified duration
        await asyncio.sleep(duration)

        # Stop monitoring
        self.monitoring = False
        monitor_task.cancel()

        try:
            await monitor_task
        except asyncio.CancelledError:
            pass

    async def _network_monitor_loop(self):
        """Main network monitoring loop"""
        previous_connections = set()

        while self.monitoring:
            try:
                # Monitor TCP connections to agent ports
                connections = await self._get_tcp_connections()

                # Detect new connections (potential HTTP calls)
                new_connections = connections - previous_connections
                for conn in new_connections:
                    await self._process_new_connection(conn)

                previous_connections = connections

                # Also monitor for HTTP traffic using ss (socket statistics)
                await self._monitor_http_traffic()

            except Exception as e:
                pass  # Continue monitoring despite errors

            await asyncio.sleep(0.5)  # Check every 500ms

    async def _get_tcp_connections(self) -> set:
        """Get current TCP connections involving agent ports"""
        connections = set()

        try:
            # Use ss command for better performance than netstat
            ports_pattern = "|".join(str(port) for port in self.agent_ports.values())
            cmd = f"ss -tn state established | grep -E ':({ports_pattern})'"

            process = await asyncio.create_subprocess_shell(
                cmd,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE
            )
            stdout, stderr = await process.communicate()

            if stdout:
                lines = stdout.decode().strip().split('\n')
                for line in lines:
                    if line.strip():
                        connections.add(line.strip())

        except Exception:
            pass

        return connections

    async def _process_new_connection(self, connection_line: str):
        """Process a new network connection"""
        try:
            # Parse ss output: ESTAB 0 0 local_ip:local_port foreign_ip:foreign_port
            parts = connection_line.split()
            if len(parts) >= 4:
                local_addr = parts[3]
                foreign_addr = parts[4]

                local_port = int(local_addr.split(':')[-1])
                foreign_port = int(foreign_addr.split(':')[-1])

                # Check if this involves agent ports
                local_agent = self.port_to_agent.get(local_port)
                foreign_agent = self.port_to_agent.get(foreign_port)

                if local_agent and foreign_agent and local_agent != foreign_agent:
                    self.log_event(
                        "INTER_AGENT_CALL",
                        source=foreign_agent,
                        target=local_agent,
                        method="HTTP",
                        local_port=local_port,
                        foreign_port=foreign_port
                    )
        except Exception:
            pass

    async def _monitor_http_traffic(self):
        """Monitor HTTP traffic using connection analysis"""
        try:
            # Use lsof to detect active HTTP connections
            for agent_name, port in self.agent_ports.items():
                cmd = f"lsof -i :{port} -sTCP:ESTABLISHED 2>/dev/null"

                process = await asyncio.create_subprocess_shell(
                    cmd,
                    stdout=asyncio.subprocess.PIPE,
                    stderr=asyncio.subprocess.PIPE
                )
                stdout, stderr = await process.communicate()

                if stdout:
                    # Parse lsof output for connections
                    lines = stdout.decode().strip().split('\n')[1:]  # Skip header
                    for line in lines:
                        if line.strip():
                            await self._parse_lsof_line(line, agent_name, port)

        except Exception:
            pass

    async def _parse_lsof_line(self, line: str, agent_name: str, port: int):
        """Parse lsof output line"""
        try:
            parts = line.split()
            if len(parts) >= 9:
                # lsof format: COMMAND PID USER FD TYPE DEVICE SIZE/OFF NODE NAME
                connection_info = parts[8]  # NAME field contains connection info

                if '->' in connection_info:
                    # This is an outgoing connection
                    local_part, remote_part = connection_info.split('->')
                    remote_port = int(remote_part.split(':')[-1])

                    # Check if remote port belongs to another agent
                    remote_agent = self.port_to_agent.get(remote_port)
                    if remote_agent and remote_agent != agent_name:
                        self.log_event(
                            "INTER_AGENT_CALL",
                            source=agent_name,
                            target=remote_agent,
                            method="HTTP_OUT",
                            local_port=port,
                            remote_port=remote_port
                        )
        except Exception:
            pass

async def query_with_network_tracing(query: str, master_url: str = "http://localhost:5040",
                                   trace_duration: int = 30, output_file: str = None):
    """Execute query with enhanced network-level tracing"""

    tracer = NetworkTracer(output_file)

    print(f"{Back.BLUE}{Fore.WHITE}=== NETWORK-LEVEL TRACED QUERY EXECUTION ==={Style.RESET_ALL}")
    print(f"Query: {Fore.YELLOW}{query}{Style.RESET_ALL}")
    print(f"Master URL: {master_url}")
    print(f"Network Trace Duration: {trace_duration}s")
    print()

    # Start network monitoring in background
    monitor_task = asyncio.create_task(tracer.monitor_network_traffic(trace_duration))

    # Wait a moment for monitoring to start
    await asyncio.sleep(0.5)

    # Check if master agent is online
    async with aiohttp.ClientSession() as session:
        try:
            tracer.log_event("HTTP_REQUEST", "QUERY_CLIENT", "MASTER_COORDINATOR",
                           method="GET", url=f"{master_url}/.well-known/agent-card.json")

            async with session.get(f"{master_url}/.well-known/agent-card.json") as response:
                if response.status == 200:
                    agent_data = await response.json()
                    tracer.log_event("HTTP_RESPONSE", "MASTER_COORDINATOR", "QUERY_CLIENT",
                                   status_code=200, duration_ms=0,
                                   response=agent_data)
                    print(f"✅ Master agent is online: {agent_data.get('name', 'Unknown')}")
                else:
                    print(f"❌ Master agent not responding: HTTP {response.status}")
                    return
        except Exception as e:
            print(f"❌ Cannot connect to master agent: {e}")
            return

    print(f"\n🚀 Sending query to master agent...")

    # Send the actual query
    payload = {
        "jsonrpc": "2.0",
        "method": "message/send",
        "params": {
            "message": {
                "id": f"netrace_{int(time.time())}",
                "timestamp": datetime.now().isoformat(),
                "role": "user",
                "content": query
            }
        },
        "id": f"netrace_query_{int(time.time())}"
    }

    start_time = time.time()

    async with aiohttp.ClientSession() as session:
        try:
            tracer.log_event("HTTP_REQUEST", "QUERY_CLIENT", "MASTER_COORDINATOR",
                           method="POST", url=master_url, payload=payload)

            async with session.post(master_url, json=payload) as response:
                query_duration = (time.time() - start_time) * 1000
                response_data = await response.text()

                try:
                    response_json = json.loads(response_data)
                except:
                    response_json = response_data

                tracer.log_event("HTTP_RESPONSE", "MASTER_COORDINATOR", "QUERY_CLIENT",
                               status_code=response.status, duration_ms=query_duration,
                               response=response_json)

                if response.status == 200:
                    print(f"✅ Query completed in {query_duration:.1f}ms")

                    # Extract and display response content
                    content = extract_response_content(response_json)
                    if content:
                        print(f"\n{Fore.GREEN}📋 Master Coordinator Response:{Style.RESET_ALL}")
                        print(f"{content[:500]}{'...' if len(content) > 500 else ''}")
                else:
                    print(f"❌ Query failed: HTTP {response.status}")

        except Exception as e:
            print(f"❌ Query error: {e}")

    # Wait for network monitoring to complete
    await monitor_task

    # Print comprehensive summary
    print_network_summary(tracer)

    # Save results
    if tracer.output_file:
        save_network_trace(tracer)

def extract_response_content(response_data: Any) -> str:
    """Extract readable content from response"""
    if isinstance(response_data, dict):
        if "result" in response_data:
            result = response_data["result"]
            if isinstance(result, dict):
                if "result" in result and "message" in result["result"]:
                    return result["result"]["message"].get("content", "")
                elif "message" in result:
                    msg = result["message"]
                    if isinstance(msg, dict):
                        return msg.get("content", str(msg))
                    else:
                        return str(msg)
        elif "message" in response_data:
            return str(response_data["message"])

    return str(response_data) if response_data else ""

def print_network_summary(tracer: NetworkTracer):
    """Print comprehensive network trace summary"""
    total_time = time.time() - tracer.start_time

    print(f"\n{Back.CYAN}{Fore.WHITE}=== NETWORK TRACE SUMMARY ==={Style.RESET_ALL}")
    print(f"Total execution time: {Fore.YELLOW}{total_time:.2f}s{Style.RESET_ALL}")
    print(f"Total events captured: {Fore.YELLOW}{len(tracer.events)}{Style.RESET_ALL}")

    # Inter-agent calls summary
    if tracer.inter_agent_calls:
        print(f"\n{Fore.YELLOW}🔄 Inter-Agent Communications ({len(tracer.inter_agent_calls)}):{Style.RESET_ALL}")
        for i, call in enumerate(tracer.inter_agent_calls[:10], 1):  # Show first 10
            timestamp = call["timestamp"][-12:-3]
            print(f"  {i}. [{timestamp}] {call['source']} → {call['target']} ({call['method']})")

        if len(tracer.inter_agent_calls) > 10:
            print(f"  ... and {len(tracer.inter_agent_calls) - 10} more")
    else:
        print(f"\n{Fore.YELLOW}⚠️  No inter-agent communications detected{Style.RESET_ALL}")
        print(f"   This might indicate:")
        print(f"   • Agents are responding directly without delegation")
        print(f"   • A2A communication is not properly configured")
        print(f"   • Network monitoring missed the connections")

    # Agent interaction sequence
    if tracer.agent_sequence:
        print(f"\n{Fore.CYAN}Agent Interaction Sequence:{Style.RESET_ALL}")
        sequence_str = " → ".join(tracer.agent_sequence)
        print(f"  {Fore.LIGHTBLUE_EX}{sequence_str}{Style.RESET_ALL}")

    # Event type breakdown
    event_types = {}
    for event in tracer.events:
        event_types[event["event_type"]] = event_types.get(event["event_type"], 0) + 1

    print(f"\n{Fore.MAGENTA}Event Type Breakdown:{Style.RESET_ALL}")
    for event_type, count in sorted(event_types.items()):
        print(f"  {event_type}: {count}")

def save_network_trace(tracer: NetworkTracer):
    """Save network trace data"""
    # Save full trace
    with open(tracer.output_file, 'w') as f:
        json.dump(tracer.events, f, indent=2)
    print(f"{Fore.GREEN}Full network trace saved to: {tracer.output_file}{Style.RESET_ALL}")

    # Save summary
    summary_file = tracer.output_file.replace('.json', '_network_summary.json')
    summary = {
        "total_time": time.time() - tracer.start_time,
        "total_events": len(tracer.events),
        "agent_sequence": tracer.agent_sequence,
        "inter_agent_calls": tracer.inter_agent_calls,
        "event_counts": {}
    }

    for event in tracer.events:
        summary["event_counts"][event["event_type"]] = summary["event_counts"].get(event["event_type"], 0) + 1

    with open(summary_file, 'w') as f:
        json.dump(summary, f, indent=2)
    print(f"{Fore.GREEN}Summary saved to: {summary_file}{Style.RESET_ALL}")

async def main():
    parser = argparse.ArgumentParser(description="Network-Level HR System Query Tracer")
    parser.add_argument("query", nargs="?", help="Query to send to master agent")
    parser.add_argument("--master-url", default="http://localhost:5040", help="Master agent URL")
    parser.add_argument("--output", "-o", help="Output file for trace data (JSON format)")
    parser.add_argument("--trace-duration", type=int, default=60, help="Duration to monitor network traffic")

    args = parser.parse_args()

    if not args.query:
        print("Please provide a query to trace")
        return 1

    # Create output file if not specified
    if args.output:
        output_file = args.output
    else:
        traces_dir = Path("traces")
        traces_dir.mkdir(exist_ok=True)
        output_file = traces_dir / f"network_trace_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"

    # Run the network-traced query
    await query_with_network_tracing(
        args.query,
        args.master_url,
        args.trace_duration,
        str(output_file)
    )

    return 0

if __name__ == "__main__":
    try:
        exit_code = asyncio.run(main())
        sys.exit(exit_code)
    except KeyboardInterrupt:
        print(f"\n{Fore.YELLOW}Network tracing interrupted by user{Style.RESET_ALL}")
        sys.exit(1)
    except Exception as e:
        print(f"\n{Fore.RED}Error during network tracing: {e}{Style.RESET_ALL}")
        sys.exit(1)