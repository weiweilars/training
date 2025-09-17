#!/usr/bin/env python3
"""
Enhanced Network Tracer for HR Recruitment System
Captures agent-to-agent communication without modifying agents
"""

import asyncio
import aiohttp
import json
import time
import argparse
import subprocess
import threading
import queue
from datetime import datetime
from typing import Dict, List, Optional, Set
from colorama import init, Fore, Style
import re
import socket
import struct

# Initialize colorama for cross-platform colored output
init(autoreset=True)

class NetworkPacketCapture:
    """Captures HTTP traffic between agents using raw sockets"""

    def __init__(self, trace_queue: queue.Queue):
        self.trace_queue = trace_queue
        self.monitoring = False
        self.monitored_ports = {
            5020, 5021, 5022, 5023, 5024, 5025, 5026, 5027, 5028, 5029, 5030,  # Individual agents
            5031, 5032, 5033, 5034,  # Team coordinators
            5040,  # Master coordinator
            8051, 8052, 8053, 8061, 8062, 8063, 8071, 8072,  # MCP tools (partial list)
        }
        self.capture_thread = None

    def start_capture(self):
        """Start packet capture in background thread"""
        self.monitoring = True
        self.capture_thread = threading.Thread(target=self._capture_packets)
        self.capture_thread.daemon = True
        self.capture_thread.start()

    def stop_capture(self):
        """Stop packet capture"""
        self.monitoring = False
        if self.capture_thread:
            self.capture_thread.join(timeout=2)

    def _capture_packets(self):
        """Capture packets using tcpdump subprocess"""
        try:
            # Build port filter for tcpdump
            port_filter = " or ".join([f"port {p}" for p in self.monitored_ports])

            # Run tcpdump to capture HTTP traffic
            cmd = [
                "tcpdump", "-i", "lo", "-n", "-l", "-A",
                f"tcp and ({port_filter})",
                "and", "(((ip[2:2] - ((ip[0]&0xf)<<2)) - ((tcp[12]&0xf0)>>2)) != 0)"
            ]

            process = subprocess.Popen(
                cmd,
                stdout=subprocess.PIPE,
                stderr=subprocess.DEVNULL,
                universal_newlines=True
            )

            buffer = []
            current_packet = {}

            while self.monitoring:
                line = process.stdout.readline()
                if not line:
                    break

                # Parse tcpdump output
                if re.match(r'^\d{2}:\d{2}:\d{2}\.\d+', line):
                    # New packet timestamp
                    if current_packet:
                        self._process_packet(current_packet, ''.join(buffer))

                    # Extract source and destination
                    parts = line.split()
                    if len(parts) >= 5:
                        timestamp = parts[0]
                        src = parts[2].rstrip(',')
                        dst = parts[4].rstrip(':')
                        current_packet = {
                            'timestamp': timestamp,
                            'src': src,
                            'dst': dst
                        }
                        buffer = []
                else:
                    # Packet content
                    buffer.append(line)

            process.terminate()

        except Exception as e:
            print(f"{Fore.RED}Packet capture error: {e}{Style.RESET_ALL}")

    def _process_packet(self, packet_info: Dict, content: str):
        """Process captured packet and extract HTTP information"""
        try:
            # Look for HTTP request/response patterns
            if 'POST /' in content or 'GET /' in content:
                # HTTP Request
                method = 'POST' if 'POST' in content else 'GET'

                # Extract source and destination ports
                src_port = self._extract_port(packet_info['src'])
                dst_port = self._extract_port(packet_info['dst'])

                if src_port and dst_port:
                    # Look for JSON-RPC content
                    json_match = re.search(r'\{.*"jsonrpc".*\}', content, re.DOTALL)
                    payload = None
                    if json_match:
                        try:
                            payload = json.loads(json_match.group())
                        except:
                            pass

                    event = {
                        'timestamp': datetime.now().isoformat(),
                        'type': 'A2A_REQUEST',
                        'source_port': src_port,
                        'target_port': dst_port,
                        'method': method,
                        'payload': payload
                    }
                    self.trace_queue.put(event)

            elif 'HTTP/1.1' in content:
                # HTTP Response
                status_match = re.search(r'HTTP/1\.1 (\d{3})', content)
                if status_match:
                    status = int(status_match.group(1))

                    src_port = self._extract_port(packet_info['src'])
                    dst_port = self._extract_port(packet_info['dst'])

                    if src_port and dst_port:
                        # Look for JSON response
                        json_match = re.search(r'\{.*"result".*\}', content, re.DOTALL)
                        response = None
                        if json_match:
                            try:
                                response = json.loads(json_match.group())
                            except:
                                pass

                        event = {
                            'timestamp': datetime.now().isoformat(),
                            'type': 'A2A_RESPONSE',
                            'source_port': src_port,
                            'target_port': dst_port,
                            'status': status,
                            'response': response
                        }
                        self.trace_queue.put(event)

        except Exception as e:
            pass  # Silently ignore parsing errors

    def _extract_port(self, address: str) -> Optional[int]:
        """Extract port number from address string"""
        try:
            if '.' in address:
                # Format: 127.0.0.1.5040
                parts = address.split('.')
                if len(parts) == 5:
                    return int(parts[4])
            return None
        except:
            return None


class EnhancedNetworkTracer:
    """Enhanced tracer that captures all agent-to-agent communication"""

    def __init__(self, master_url: str = "http://localhost:5040"):
        self.master_url = master_url
        self.trace_queue = queue.Queue()
        self.events = []
        self.agent_map = {
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
        # Add MCP tools
        for i, port in enumerate(range(8051, 8144)):
            self.agent_map[port] = f"MCP_TOOL_{port}"

    def get_agent_name(self, port: int) -> str:
        """Get agent name from port number"""
        return self.agent_map.get(port, f"UNKNOWN_{port}")

    async def trace_query(self, query: str, duration: int = 30):
        """Execute query and trace all agent communication"""
        print(f"\n{Fore.CYAN}=== ENHANCED NETWORK TRACER ==={Style.RESET_ALL}")
        print(f"Query: {query}")
        print(f"Trace Duration: {duration}s")
        print(f"Master URL: {self.master_url}")
        print()

        # Check if we have permission to capture packets
        try:
            subprocess.run(["tcpdump", "--version"],
                         capture_output=True, check=True)
        except (subprocess.CalledProcessError, FileNotFoundError):
            print(f"{Fore.YELLOW}⚠️  tcpdump not available or no permission.")
            print(f"   For full A2A tracing, run with: sudo python {__file__}")
            print(f"   Falling back to basic tracing...{Style.RESET_ALL}\n")
            return await self._basic_trace(query, duration)

        # Start packet capture
        packet_capture = NetworkPacketCapture(self.trace_queue)
        packet_capture.start_capture()

        # Start event processor
        event_processor = threading.Thread(target=self._process_events)
        event_processor.daemon = True
        event_processor.start()

        try:
            # Send query to master
            print(f"{Fore.GREEN}🚀 Sending query to master agent...{Style.RESET_ALL}\n")

            start_time = time.time()

            async with aiohttp.ClientSession() as session:
                payload = {
                    "jsonrpc": "2.0",
                    "method": "message/send",
                    "params": {
                        "message": {
                            "id": f"trace_{int(time.time())}",
                            "timestamp": datetime.now().isoformat(),
                            "role": "user",
                            "content": query
                        }
                    },
                    "id": f"trace_{int(time.time())}"
                }

                # Log the initial request
                self._log_event({
                    'timestamp': datetime.now().isoformat(),
                    'type': 'CLIENT_REQUEST',
                    'source_port': 0,
                    'target_port': 5040,
                    'payload': payload
                })

                # Send request
                async with session.post(self.master_url, json=payload) as response:
                    result = await response.json()

                    # Log the response
                    self._log_event({
                        'timestamp': datetime.now().isoformat(),
                        'type': 'CLIENT_RESPONSE',
                        'source_port': 5040,
                        'target_port': 0,
                        'status': response.status,
                        'response': result,
                        'duration_ms': (time.time() - start_time) * 1000
                    })

                    # Continue monitoring for the specified duration
                    print(f"\n{Fore.YELLOW}📡 Monitoring A2A communication...{Style.RESET_ALL}\n")
                    await asyncio.sleep(duration)

        finally:
            # Stop packet capture
            packet_capture.stop_capture()

            # Process any remaining events
            time.sleep(1)
            while not self.trace_queue.empty():
                self._process_single_event()

            # Print summary
            self._print_summary()

    async def _basic_trace(self, query: str, duration: int):
        """Fallback to basic tracing without packet capture"""
        # This would be similar to the original tracer
        # but we'll skip it for now since we want network capture
        print(f"{Fore.RED}Basic tracing not implemented in this version{Style.RESET_ALL}")

    def _process_events(self):
        """Process events from queue"""
        while True:
            try:
                self._process_single_event()
            except:
                time.sleep(0.1)

    def _process_single_event(self):
        """Process a single event from queue"""
        try:
            event = self.trace_queue.get(timeout=0.5)
            self._log_event(event)
        except queue.Empty:
            pass

    def _log_event(self, event: Dict):
        """Log and display an event"""
        self.events.append(event)

        timestamp = event['timestamp'].split('T')[1][:12]
        event_type = event['type']

        if event_type == 'CLIENT_REQUEST':
            print(f"{Fore.BLUE}[{timestamp}] CLIENT → MASTER")
            print(f"    Query: {event['payload']['params']['message']['content'][:100]}...{Style.RESET_ALL}")

        elif event_type == 'CLIENT_RESPONSE':
            print(f"{Fore.GREEN}[{timestamp}] MASTER → CLIENT (%.1fms)" % event.get('duration_ms', 0))
            if event.get('response', {}).get('result', {}).get('result', {}).get('message'):
                content = event['response']['result']['result']['message'].get('content', '')
                print(f"    Response: {content[:200]}...{Style.RESET_ALL}")

        elif event_type == 'A2A_REQUEST':
            source = self.get_agent_name(event['source_port'])
            target = self.get_agent_name(event['target_port'])
            print(f"{Fore.MAGENTA}[{timestamp}] {source} → {target} (A2A)")
            if event.get('payload'):
                if 'message' in str(event['payload']):
                    print(f"    Message: {str(event['payload'])[:100]}...")
            print(Style.RESET_ALL)

        elif event_type == 'A2A_RESPONSE':
            source = self.get_agent_name(event['source_port'])
            target = self.get_agent_name(event['target_port'])
            print(f"{Fore.CYAN}[{timestamp}] {source} ← {target} (A2A Response)")
            print(f"    Status: {event.get('status', 'unknown')}{Style.RESET_ALL}")

    def _print_summary(self):
        """Print trace summary"""
        print(f"\n{Fore.CYAN}=== TRACE SUMMARY ==={Style.RESET_ALL}")

        # Count event types
        event_counts = {}
        a2a_pairs = set()

        for event in self.events:
            event_type = event['type']
            event_counts[event_type] = event_counts.get(event_type, 0) + 1

            if event_type == 'A2A_REQUEST':
                source = self.get_agent_name(event['source_port'])
                target = self.get_agent_name(event['target_port'])
                a2a_pairs.add((source, target))

        print(f"Total events captured: {len(self.events)}")
        print(f"Event breakdown:")
        for event_type, count in sorted(event_counts.items()):
            print(f"  {event_type}: {count}")

        if a2a_pairs:
            print(f"\n{Fore.GREEN}✅ Agent-to-Agent Communication Detected:{Style.RESET_ALL}")
            for source, target in sorted(a2a_pairs):
                print(f"  {source} → {target}")
        else:
            print(f"\n{Fore.YELLOW}⚠️  No A2A communication captured")
            print(f"   This might be because:")
            print(f"   1. The query didn't trigger A2A calls")
            print(f"   2. Need sudo permission for packet capture")
            print(f"   3. Agents are using different communication method{Style.RESET_ALL}")

        # Save to file
        filename = f"traces/network_trace_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        with open(filename, 'w') as f:
            json.dump(self.events, f, indent=2)
        print(f"\nFull trace saved to: {filename}")


async def main():
    parser = argparse.ArgumentParser(description='Enhanced Network Tracer for A2A Communication')
    parser.add_argument('query', nargs='?', help='Query to send to master agent')
    parser.add_argument('--duration', type=int, default=30, help='Trace duration in seconds')
    parser.add_argument('--master-url', default='http://localhost:5040/', help='Master coordinator URL')

    args = parser.parse_args()

    if not args.query:
        args.query = "Create a job posting for Senior Python Developer"

    tracer = EnhancedNetworkTracer(args.master_url)
    await tracer.trace_query(args.query, args.duration)


if __name__ == "__main__":
    asyncio.run(main())