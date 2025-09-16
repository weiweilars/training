#!/usr/bin/env python3
"""
Advanced HR System Query Tracer
Captures all HTTP traffic, agent-to-agent calls, and tool invocations
during query processing with real-time monitoring.

Usage: python advanced_query_tracer.py "Your query here"
       python advanced_query_tracer.py --interactive
       python advanced_query_tracer.py --trace-duration 60 "complex query"
"""

import asyncio
import json
import time
import argparse
import sys
import os
import logging
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional, Set
import aiohttp
import threading
from dataclasses import dataclass, asdict, field
from colorama import init, Fore, Back, Style
import re
import subprocess
from pathlib import Path

# Initialize colorama for colored output
init(autoreset=True)

@dataclass
class TraceEvent:
    timestamp: str
    event_id: str
    event_type: str  # HTTP_REQUEST, HTTP_RESPONSE, AGENT_CALL, TOOL_CALL, LOG_ENTRY
    source: str      # MASTER, ACQUISITION, EXPERIENCE, CLOSING, TOOL_SERVER, etc.
    target: str      # Target of the operation
    method: Optional[str] = None
    url: Optional[str] = None
    status_code: Optional[int] = None
    headers: Optional[Dict] = None
    payload: Optional[Any] = None
    response: Optional[Any] = None
    duration_ms: Optional[float] = None
    error: Optional[str] = None
    metadata: Dict[str, Any] = field(default_factory=dict)

class NetworkTracer:
    """Traces network traffic between agents and tools"""

    def __init__(self, logger):
        self.logger = logger
        self.active_requests: Dict[str, TraceEvent] = {}
        self.request_counter = 0

    async def trace_request(self, method: str, url: str, headers: Dict = None,
                          payload: Any = None, source: str = "UNKNOWN") -> str:
        """Start tracing a request"""
        self.request_counter += 1
        event_id = f"req_{self.request_counter}_{int(time.time() * 1000)}"

        event = TraceEvent(
            timestamp=datetime.now().isoformat(),
            event_id=event_id,
            event_type="HTTP_REQUEST",
            source=source,
            target=self._extract_target_from_url(url),
            method=method,
            url=url,
            headers=headers or {},
            payload=payload
        )

        self.active_requests[event_id] = event
        self.logger.log_trace_event(event)
        return event_id

    async def trace_response(self, event_id: str, status_code: int,
                           response: Any = None, error: str = None):
        """Complete tracing a request with response"""
        if event_id in self.active_requests:
            request_event = self.active_requests[event_id]
            start_time = datetime.fromisoformat(request_event.timestamp)
            duration = (datetime.now() - start_time).total_seconds() * 1000

            response_event = TraceEvent(
                timestamp=datetime.now().isoformat(),
                event_id=f"{event_id}_response",
                event_type="HTTP_RESPONSE",
                source=request_event.target,
                target=request_event.source,
                method=request_event.method,
                url=request_event.url,
                status_code=status_code,
                response=response,
                duration_ms=duration,
                error=error,
                metadata={"request_id": event_id}
            )

            self.logger.log_trace_event(response_event)
            del self.active_requests[event_id]

    def _extract_target_from_url(self, url: str) -> str:
        """Extract target agent/service from URL"""
        if ":5020" in url: return "JOB_REQUISITION"
        elif ":5021" in url: return "SOURCING"
        elif ":5022" in url: return "RESUME_SCREENING"
        elif ":5023" in url: return "INTERVIEW_SCHEDULING"
        elif ":5024" in url: return "ASSESSMENT"
        elif ":5025" in url: return "BACKGROUND_VERIFICATION"
        elif ":5026" in url: return "OFFER_MANAGEMENT"
        elif ":5027" in url: return "COMPLIANCE"
        elif ":5028" in url: return "COMMUNICATION"
        elif ":5029" in url: return "ANALYTICS_REPORTING"
        elif ":5032" in url: return "ACQUISITION_TEAM"
        elif ":5033" in url: return "EXPERIENCE_TEAM"
        elif ":5034" in url: return "CLOSING_TEAM"
        elif ":5040" in url: return "MASTER_COORDINATOR"
        elif ":8051" in url: return "TOOL_SERVER_1"
        elif ":8052" in url: return "TOOL_SERVER_2"
        elif ":8053" in url: return "TOOL_SERVER_3"
        else: return "UNKNOWN"

class LogCapture:
    """Captures logs from running agents"""

    def __init__(self, logger):
        self.logger = logger
        self.monitoring = False
        self.log_patterns = {
            "agent_call": re.compile(r"Agent\s+(\w+).*called", re.IGNORECASE),
            "tool_call": re.compile(r"Tool\s+(\w+).*called", re.IGNORECASE),
            "mcp_request": re.compile(r"MCP.*request.*(\w+)", re.IGNORECASE),
            "error": re.compile(r"ERROR.*", re.IGNORECASE),
            "warning": re.compile(r"WARNING.*", re.IGNORECASE)
        }

    async def start_monitoring(self, duration: int = 60):
        """Start monitoring agent logs"""
        self.monitoring = True
        end_time = time.time() + duration

        self.logger.log_trace_event(TraceEvent(
            timestamp=datetime.now().isoformat(),
            event_id=f"log_monitor_{int(time.time())}",
            event_type="LOG_MONITORING_START",
            source="SYSTEM",
            target="ALL_AGENTS",
            metadata={"duration": duration}
        ))

        while self.monitoring and time.time() < end_time:
            await self._capture_agent_logs()
            await asyncio.sleep(5)  # Increased from 2s to 5s to reduce API calls

    async def _capture_agent_logs(self):
        """Capture current agent logs (simplified version)"""
        # In a real implementation, this would tail log files or connect to log streams
        # For now, we'll simulate by checking agent health and status

        agent_ports = {
            "MASTER_COORDINATOR": 5040,
            "ACQUISITION_TEAM": 5032,
            "EXPERIENCE_TEAM": 5033,
            "CLOSING_TEAM": 5034,
            "JOB_REQUISITION": 5020,
            "SOURCING": 5021,
            "RESUME_SCREENING": 5022
        }

        async with aiohttp.ClientSession() as session:
            for agent_name, port in agent_ports.items():
                try:
                    # Add small delay to avoid rate limits
                    await asyncio.sleep(0.2)  # 200ms delay between agent checks

                    # Check agent card endpoint instead of health
                    async with session.get(f"http://localhost:{port}/.well-known/agent-card.json",
                                         timeout=aiohttp.ClientTimeout(total=2)) as response:
                        if response.status == 200:
                            agent_data = await response.json()

                            self.logger.log_trace_event(TraceEvent(
                                timestamp=datetime.now().isoformat(),
                                event_id=f"status_{agent_name}_{int(time.time())}",
                                event_type="AGENT_STATUS",
                                source="MONITOR",
                                target=agent_name,
                                status_code=200,
                                response={
                                    "name": agent_data.get("name"),
                                    "status": agent_data.get("metadata", {}).get("status", "unknown"),
                                    "version": agent_data.get("version")
                                },
                                metadata={"port": port}
                            ))
                except:
                    pass  # Agent might be down

    def stop_monitoring(self):
        """Stop log monitoring"""
        self.monitoring = False

class AdvancedQueryTracer:
    """Main tracer class that coordinates all tracing activities"""

    def __init__(self, output_file: Optional[str] = None):
        self.events: List[TraceEvent] = []
        self.output_file = output_file
        self.start_time = time.time()
        self.network_tracer = NetworkTracer(self)
        self.log_capture = LogCapture(self)
        self.agent_sequence: List[str] = []
        self.tool_calls: List[Dict] = []

        # Setup logging
        self.setup_logging()

    def setup_logging(self):
        """Setup logging configuration"""
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
        )
        self.logger = logging.getLogger(__name__)

    def log_trace_event(self, event: TraceEvent):
        """Log a trace event"""
        self.events.append(event)
        self._print_event(event)

        # Track sequences
        if event.event_type == "HTTP_REQUEST" and event.target != "UNKNOWN":
            if event.target not in self.agent_sequence:
                self.agent_sequence.append(event.target)

        # Track tool calls
        if "tool" in event.event_type.lower() or "mcp" in str(event.payload).lower():
            self.tool_calls.append({
                "timestamp": event.timestamp,
                "source": event.source,
                "target": event.target,
                "details": event.payload
            })

    def _print_event(self, event: TraceEvent):
        """Print colorized trace event"""
        # Skip repetitive agent status events for cleaner output (unless in verbose mode)
        if (event.event_type == "AGENT_STATUS" and
            hasattr(self, 'quiet_mode') and self.quiet_mode and
            not self._is_first_status_for_agent(event)):
            return

        timestamp = f"{Fore.CYAN}{event.timestamp[-12:-3]}{Style.RESET_ALL}"

        # Color by event type
        type_colors = {
            'HTTP_REQUEST': Fore.BLUE,
            'HTTP_RESPONSE': Fore.GREEN,
            'AGENT_CALL': Fore.MAGENTA,
            'TOOL_CALL': Fore.YELLOW,
            'LOG_ENTRY': Fore.WHITE,
            'AGENT_HEALTH': Fore.LIGHTBLACK_EX
        }
        event_type = f"{type_colors.get(event.event_type, Fore.WHITE)}{event.event_type}{Style.RESET_ALL}"

        # Color by source
        source_color = Fore.LIGHTCYAN_EX if "TEAM" in event.source else Fore.LIGHTBLUE_EX
        source = f"{source_color}{event.source}{Style.RESET_ALL}"

        target = f"{Fore.LIGHTGREEN_EX}{event.target}{Style.RESET_ALL}"

        # Format based on event type
        if event.event_type == "HTTP_REQUEST":
            method = f"{Fore.YELLOW}{event.method}{Style.RESET_ALL}"
            url_path = event.url.split('/')[-1] if event.url else ""
            print(f"[{timestamp}] {event_type} {source} → {target} {method} /{url_path}")

            if event.payload:
                payload_preview = str(event.payload)[:100] + "..." if len(str(event.payload)) > 100 else str(event.payload)
                print(f"    {Fore.LIGHTBLACK_EX}Payload: {payload_preview}{Style.RESET_ALL}")

        elif event.event_type == "HTTP_RESPONSE":
            status_color = Fore.GREEN if event.status_code < 400 else Fore.RED
            status = f"{status_color}{event.status_code}{Style.RESET_ALL}"
            duration = f"({event.duration_ms:.1f}ms)" if event.duration_ms else ""
            print(f"[{timestamp}] {event_type} {source} → {target} {status} {duration}")

            if event.error:
                print(f"    {Fore.RED}Error: {event.error}{Style.RESET_ALL}")
            elif event.response:
                # Show full response for main query results
                if (event.source == "MASTER_COORDINATOR" and
                    event.target == "QUERY_CLIENT" and
                    event.duration_ms and event.duration_ms > 1000):
                    print(f"    {Fore.GREEN}✅ Main Query Response:{Style.RESET_ALL}")
                    try:
                        if isinstance(event.response, dict) and 'result' in event.response:
                            result = event.response['result']
                            if isinstance(result, dict) and 'result' in result:
                                message_content = result['result'].get('message', {}).get('content', '')
                                if message_content:
                                    print(f"    {Fore.WHITE}{message_content[:800]}{'...' if len(message_content) > 800 else ''}{Style.RESET_ALL}")
                                    return
                        # Fallback
                        response_str = json.dumps(event.response, indent=2)[:500]
                        print(f"    {Fore.LIGHTBLACK_EX}{response_str}{'...' if len(response_str) >= 500 else ''}{Style.RESET_ALL}")
                    except:
                        print(f"    {Fore.LIGHTBLACK_EX}{str(event.response)[:500]}{'...' if len(str(event.response)) > 500 else ''}{Style.RESET_ALL}")
                else:
                    response_preview = str(event.response)[:150] + "..." if len(str(event.response)) > 150 else str(event.response)
                    print(f"    {Fore.LIGHTBLACK_EX}Response: {response_preview}{Style.RESET_ALL}")

        else:
            print(f"[{timestamp}] {event_type} {source} → {target}")
            if event.metadata:
                print(f"    {Fore.LIGHTBLACK_EX}Metadata: {event.metadata}{Style.RESET_ALL}")

    def _is_first_status_for_agent(self, event: TraceEvent) -> bool:
        """Check if this is the first status event for this agent"""
        if not hasattr(self, '_seen_agents'):
            self._seen_agents = set()

        agent_key = f"{event.source}_{event.target}"
        if agent_key not in self._seen_agents:
            self._seen_agents.add(agent_key)
            return True
        return False

    def set_quiet_mode(self, quiet: bool):
        """Enable/disable quiet mode to reduce noise"""
        self.quiet_mode = quiet

class TracedHTTPSession:
    """HTTP session that traces all requests"""

    def __init__(self, tracer: AdvancedQueryTracer, source: str = "CLIENT"):
        self.tracer = tracer
        self.source = source
        self.session = None

    async def __aenter__(self):
        self.session = aiohttp.ClientSession()
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        if self.session:
            await self.session.close()

    async def request(self, method: str, url: str, **kwargs):
        """Traced HTTP request"""
        # Start tracing
        event_id = await self.tracer.network_tracer.trace_request(
            method, url,
            headers=kwargs.get('headers', {}),
            payload=kwargs.get('json') or kwargs.get('data'),
            source=self.source
        )

        try:
            # Make actual request
            async with self.session.request(method, url, **kwargs) as response:
                response_data = await response.text()
                try:
                    response_json = json.loads(response_data)
                except:
                    response_json = response_data

                # Complete tracing
                await self.tracer.network_tracer.trace_response(
                    event_id, response.status, response_json
                )

                return response, response_json

        except Exception as e:
            # Log error
            await self.tracer.network_tracer.trace_response(
                event_id, 0, None, str(e)
            )
            raise

    async def get(self, url: str, **kwargs):
        return await self.request("GET", url, **kwargs)

    async def post(self, url: str, **kwargs):
        return await self.request("POST", url, **kwargs)

async def query_with_tracing(tracer: AdvancedQueryTracer, query: str,
                           master_url: str = "http://localhost:5040",
                           trace_duration: int = 30):
    """Execute query with full tracing"""

    print(f"{Back.BLUE}{Fore.WHITE}=== STARTING TRACED QUERY EXECUTION ==={Style.RESET_ALL}")
    print(f"Query: {Fore.YELLOW}{query}{Style.RESET_ALL}")
    print(f"Master URL: {master_url}")
    print(f"Trace Duration: {trace_duration}s")
    print()

    # Start log monitoring
    monitor_task = asyncio.create_task(tracer.log_capture.start_monitoring(trace_duration))

    try:
        async with TracedHTTPSession(tracer, "QUERY_CLIENT") as session:

            # Check master agent status
            try:
                response, agent_info = await session.get(f"{master_url}/.well-known/agent-card.json")
                if response.status == 200:
                    print(f"{Fore.GREEN}✅ Master agent is online{Style.RESET_ALL}")
                else:
                    print(f"{Fore.RED}❌ Master agent not responding properly{Style.RESET_ALL}")
                    return None
            except Exception as e:
                print(f"{Fore.RED}❌ Cannot connect to master agent: {e}{Style.RESET_ALL}")
                return None

            # Send the actual query using JSON-RPC
            payload = {
                "jsonrpc": "2.0",
                "method": "message/send",
                "params": {
                    "message": {
                        "id": f"msg_{int(time.time())}",
                        "timestamp": datetime.now().isoformat(),
                        "role": "user",
                        "content": query
                    }
                },
                "id": f"trace_{int(time.time())}"
            }

            print(f"\n{Fore.CYAN}🚀 Sending query to master agent...{Style.RESET_ALL}\n")

            response, result = await session.post(
                f"{master_url}/",
                json=payload,
                headers={"Content-Type": "application/json"}
            )

            if response.status == 200:
                print(f"\n{Fore.GREEN}✅ Query completed successfully{Style.RESET_ALL}")
                return result
            else:
                print(f"\n{Fore.RED}❌ Query failed with status {response.status}{Style.RESET_ALL}")
                return None

    finally:
        # Stop monitoring
        tracer.log_capture.stop_monitoring()
        if not monitor_task.done():
            monitor_task.cancel()

def print_execution_summary(tracer: AdvancedQueryTracer):
    """Print detailed execution summary"""
    total_time = time.time() - tracer.start_time

    print(f"\n{Back.CYAN}{Fore.WHITE}=== EXECUTION TRACE SUMMARY ==={Style.RESET_ALL}")
    print(f"Total execution time: {Fore.YELLOW}{total_time:.2f}s{Style.RESET_ALL}")
    print(f"Total trace events: {Fore.YELLOW}{len(tracer.events)}{Style.RESET_ALL}")

    # Show agent responses in detail
    print_agent_responses(tracer)

    # Agent interaction sequence
    if tracer.agent_sequence:
        print(f"\n{Fore.CYAN}Agent Interaction Sequence:{Style.RESET_ALL}")
        sequence_str = " → ".join(tracer.agent_sequence)
        print(f"  {Fore.LIGHTBLUE_EX}{sequence_str}{Style.RESET_ALL}")

    # Tool calls summary
    if tracer.tool_calls:
        print(f"\n{Fore.YELLOW}Tool Calls ({len(tracer.tool_calls)}):{Style.RESET_ALL}")
        for i, tool_call in enumerate(tracer.tool_calls[:5], 1):  # Show first 5
            print(f"  {i}. {tool_call['source']} → {tool_call['target']} at {tool_call['timestamp'][-8:]}")
        if len(tracer.tool_calls) > 5:
            print(f"  ... and {len(tracer.tool_calls) - 5} more")

def print_agent_responses(tracer: AdvancedQueryTracer):
    """Print detailed agent responses"""
    responses = [e for e in tracer.events if e.event_type == "HTTP_RESPONSE" and e.response]

    if not responses:
        print(f"\n{Fore.YELLOW}⚠️  No agent responses captured{Style.RESET_ALL}")
        return

    print(f"\n{Back.GREEN}{Fore.WHITE}=== DETAILED AGENT RESPONSES ==={Style.RESET_ALL}")

    for i, response_event in enumerate(responses, 1):
        agent_name = format_agent_name(response_event.source)
        port = extract_port_from_url(response_event.url) if response_event.url else "N/A"

        print(f"\n{Fore.CYAN}🤖 AGENT {i}: {agent_name}{Style.RESET_ALL}")
        print(f"   📍 Port: {port}")
        print(f"   ⏱️  Response Time: {response_event.duration_ms:.1f}ms" if response_event.duration_ms else "   ⏱️  Response Time: N/A")
        print(f"   📊 Status: {get_status_color(response_event.status_code)}{response_event.status_code}{Style.RESET_ALL}")

        # Extract and display agent's actual response
        agent_response = extract_agent_response_content(response_event.response)
        if agent_response:
            print(f"   💬 Response:")
            # Wrap long responses
            wrapped_response = wrap_response_text(agent_response, indent="      ")
            print(f"{Fore.LIGHTGREEN_EX}{wrapped_response}{Style.RESET_ALL}")
        else:
            print(f"   💬 Response: {Fore.YELLOW}[No readable response content]{Style.RESET_ALL}")

        # Show any errors
        if response_event.error:
            print(f"   ❌ Error: {Fore.RED}{response_event.error}{Style.RESET_ALL}")

        if i < len(responses):
            print(f"   {Fore.BLUE}{'─' * 80}{Style.RESET_ALL}")

def format_agent_name(source: str) -> str:
    """Format agent name for display"""
    agent_names = {
        "MASTER_COORDINATOR": "Master Coordinator Agent",
        "JOB_REQUISITION": "Job Requisition Agent",
        "SOURCING": "Sourcing Agent",
        "RESUME_SCREENING": "Resume Screening Agent",
        "COMMUNICATION": "Communication Agent",
        "INTERVIEW_SCHEDULING": "Interview Scheduling Agent",
        "ASSESSMENT": "Assessment Agent",
        "BACKGROUND_VERIFICATION": "Background Verification Agent",
        "OFFER_MANAGEMENT": "Offer Management Agent",
        "ANALYTICS_REPORTING": "Analytics & Reporting Agent",
        "COMPLIANCE": "Compliance Agent",
        "ACQUISITION_TEAM": "Acquisition Team Coordinator",
        "EXPERIENCE_TEAM": "Experience Team Coordinator",
        "CLOSING_TEAM": "Closing Team Coordinator",
        "JOB_PIPELINE_TEAM": "Job Pipeline Team Coordinator"
    }
    return agent_names.get(source, source.replace("_", " ").title())

def extract_port_from_url(url: str) -> str:
    """Extract port from URL"""
    import re
    match = re.search(r':(\d+)', url)
    return match.group(1) if match else "N/A"

def get_status_color(status_code: int) -> str:
    """Get color for status code"""
    if status_code == 200:
        return Fore.GREEN
    elif 400 <= status_code < 500:
        return Fore.YELLOW
    elif status_code >= 500:
        return Fore.RED
    else:
        return Fore.WHITE

def extract_agent_response_content(response_data: Any) -> str:
    """Extract the actual agent response content from response data"""
    if not response_data:
        return ""

    try:
        # Handle different response formats
        if isinstance(response_data, dict):
            # JSON-RPC response format
            if "result" in response_data:
                result = response_data["result"]
                if isinstance(result, dict):
                    # Check for message content
                    if "result" in result and "message" in result["result"]:
                        return result["result"]["message"].get("content", "")
                    elif "message" in result:
                        if isinstance(result["message"], dict):
                            return result["message"].get("content", "")
                        else:
                            return str(result["message"])
                    elif "content" in result:
                        return result["content"]
                    else:
                        return str(result)
                else:
                    return str(result)

            # Direct message format
            elif "message" in response_data:
                msg = response_data["message"]
                if isinstance(msg, dict):
                    return msg.get("content", str(msg))
                else:
                    return str(msg)

            # Agent card format
            elif "name" in response_data and "description" in response_data:
                return f"Agent: {response_data['name']} - {response_data['description']}"

            # Generic dict - try to find content
            else:
                for key in ["content", "response", "text", "data"]:
                    if key in response_data:
                        return str(response_data[key])
                return str(response_data)

        # String response
        elif isinstance(response_data, str):
            return response_data

        # Other types
        else:
            return str(response_data)

    except Exception as e:
        return f"[Error extracting response: {e}]"

def wrap_response_text(text: str, indent: str = "", max_width: int = 100) -> str:
    """Wrap long text for better readability"""
    if not text:
        return f"{indent}[Empty response]"

    # Clean up the text
    text = text.strip()
    if len(text) <= max_width:
        return f"{indent}{text}"

    # Split into lines and wrap
    lines = []
    words = text.split()
    current_line = ""

    for word in words:
        if len(current_line + " " + word) <= max_width:
            current_line += (" " if current_line else "") + word
        else:
            if current_line:
                lines.append(f"{indent}{current_line}")
            current_line = word

    if current_line:
        lines.append(f"{indent}{current_line}")

    return "\n".join(lines)

    # Event type breakdown
    event_types = {}
    for event in tracer.events:
        event_types[event.event_type] = event_types.get(event.event_type, 0) + 1

    print(f"\n{Fore.MAGENTA}Event Type Breakdown:{Style.RESET_ALL}")
    for event_type, count in sorted(event_types.items()):
        print(f"  {event_type}: {count}")

    # HTTP requests summary
    http_requests = [e for e in tracer.events if e.event_type == "HTTP_REQUEST"]
    if http_requests:
        print(f"\n{Fore.GREEN}HTTP Requests Summary:{Style.RESET_ALL}")
        targets = {}
        for req in http_requests:
            targets[req.target] = targets.get(req.target, 0) + 1

        for target, count in sorted(targets.items()):
            print(f"  {target}: {count} requests")

def save_trace_data(tracer: AdvancedQueryTracer):
    """Save trace data to files"""
    if tracer.output_file:
        # Save all events
        events_file = tracer.output_file
        with open(events_file, 'w') as f:
            json.dump([asdict(event) for event in tracer.events], f, indent=2)
        print(f"{Fore.GREEN}Full trace saved to: {events_file}{Style.RESET_ALL}")

        # Save summary
        summary_file = events_file.replace('.json', '_summary.json')
        summary = {
            "total_time": time.time() - tracer.start_time,
            "total_events": len(tracer.events),
            "agent_sequence": tracer.agent_sequence,
            "tool_calls": tracer.tool_calls,
            "event_counts": {}
        }

        for event in tracer.events:
            summary["event_counts"][event.event_type] = summary["event_counts"].get(event.event_type, 0) + 1

        with open(summary_file, 'w') as f:
            json.dump(summary, f, indent=2)
        print(f"{Fore.GREEN}Summary saved to: {summary_file}{Style.RESET_ALL}")

async def main():
    parser = argparse.ArgumentParser(description="Advanced HR System Query Tracer")
    parser.add_argument("query", nargs="?", help="Query to send to master agent")
    parser.add_argument("--interactive", "-i", action="store_true", help="Run in interactive mode")
    parser.add_argument("--master-url", default="http://localhost:5040", help="Master agent URL")
    parser.add_argument("--output", "-o", help="Output file for trace data (JSON format)")
    parser.add_argument("--trace-duration", type=int, default=30, help="Duration to trace for")

    args = parser.parse_args()

    # Create tracer with organized output directory
    if args.output:
        output_file = args.output
    else:
        # Create traces directory if it doesn't exist
        traces_dir = Path("traces")
        traces_dir.mkdir(exist_ok=True)
        output_file = traces_dir / f"trace_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"

    tracer = AdvancedQueryTracer(str(output_file))

    try:
        if args.interactive:
            print(f"{Fore.GREEN}=== Advanced HR Query Tracer - Interactive Mode ==={Style.RESET_ALL}")
            print(f"{Fore.YELLOW}Enter queries to trace. Type 'quit' to exit.{Style.RESET_ALL}")
            print()

            while True:
                try:
                    query = input(f"{Fore.LIGHTGREEN_EX}Query > {Style.RESET_ALL}").strip()

                    if query.lower() in ['quit', 'exit', 'q']:
                        break

                    if not query:
                        continue

                    await query_with_tracing(tracer, query, args.master_url, args.trace_duration)
                    print_execution_summary(tracer)
                    print()

                except KeyboardInterrupt:
                    print(f"\n{Fore.YELLOW}Exiting...{Style.RESET_ALL}")
                    break

        elif args.query:
            await query_with_tracing(tracer, args.query, args.master_url, args.trace_duration)
            print_execution_summary(tracer)
        else:
            parser.print_help()
            return 1

    finally:
        save_trace_data(tracer)

    return 0

if __name__ == "__main__":
    try:
        exit_code = asyncio.run(main())
        sys.exit(exit_code)
    except KeyboardInterrupt:
        print(f"\n{Fore.YELLOW}Interrupted by user{Style.RESET_ALL}")
        sys.exit(1)