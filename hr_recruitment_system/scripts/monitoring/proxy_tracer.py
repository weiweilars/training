#!/usr/bin/env python3
"""
Proxy-based Tracer for HR Recruitment System
Intercepts agent-to-agent communication using an HTTP proxy approach
No agent modification required - just need to configure proxy settings
"""

import asyncio
import aiohttp
from aiohttp import web
import json
import time
import argparse
from datetime import datetime
from typing import Dict, List, Optional, Set
from colorama import init, Fore, Style
import threading
import queue

# Initialize colorama
init(autoreset=True)

class ProxyServer:
    """HTTP proxy server that intercepts and logs agent communication"""

    def __init__(self, proxy_port: int, trace_queue: queue.Queue):
        self.proxy_port = proxy_port
        self.trace_queue = trace_queue
        self.app = web.Application()
        self.app.router.add_route('*', '/{path:.*}', self.handle_request)
        self.runner = None
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

    def get_agent_name(self, url: str) -> str:
        """Extract agent name from URL"""
        try:
            if 'localhost:' in url:
                port = int(url.split('localhost:')[1].split('/')[0])
                return self.agent_map.get(port, f"AGENT_{port}")
        except:
            pass
        return "UNKNOWN"

    async def handle_request(self, request):
        """Handle proxied request"""
        # Get the target URL
        target_url = str(request.url)

        # Parse the actual target from the request
        if 'Host' in request.headers:
            host = request.headers['Host']
            target_url = f"http://{host}{request.path_qs}"

        # Read request body
        request_body = None
        if request.content_length:
            request_body = await request.read()
            try:
                request_json = json.loads(request_body)
            except:
                request_json = None
        else:
            request_json = None

        # Log the request
        event = {
            'timestamp': datetime.now().isoformat(),
            'type': 'PROXY_REQUEST',
            'method': request.method,
            'url': target_url,
            'source': request.remote,
            'target': self.get_agent_name(target_url),
            'headers': dict(request.headers),
            'payload': request_json
        }
        self.trace_queue.put(event)

        # Forward the request
        async with aiohttp.ClientSession() as session:
            try:
                # Prepare headers (remove hop-by-hop headers)
                headers = dict(request.headers)
                for header in ['Host', 'Connection', 'Keep-Alive',
                             'Proxy-Connection', 'TE', 'Trailer',
                             'Transfer-Encoding', 'Upgrade']:
                    headers.pop(header, None)

                # Make the actual request
                async with session.request(
                    method=request.method,
                    url=target_url,
                    headers=headers,
                    data=request_body if request_body else None,
                    allow_redirects=False,
                    timeout=aiohttp.ClientTimeout(total=60)
                ) as response:
                    # Read response
                    response_body = await response.read()
                    try:
                        response_json = json.loads(response_body)
                    except:
                        response_json = None

                    # Log the response
                    event = {
                        'timestamp': datetime.now().isoformat(),
                        'type': 'PROXY_RESPONSE',
                        'status': response.status,
                        'url': target_url,
                        'source': self.get_agent_name(target_url),
                        'headers': dict(response.headers),
                        'response': response_json
                    }
                    self.trace_queue.put(event)

                    # Return response to client
                    return web.Response(
                        body=response_body,
                        status=response.status,
                        headers=response.headers
                    )

            except Exception as e:
                # Log error
                event = {
                    'timestamp': datetime.now().isoformat(),
                    'type': 'PROXY_ERROR',
                    'url': target_url,
                    'error': str(e)
                }
                self.trace_queue.put(event)

                return web.Response(
                    text=json.dumps({"error": str(e)}),
                    status=500,
                    content_type='application/json'
                )

    async def start(self):
        """Start the proxy server"""
        self.runner = web.AppRunner(self.app)
        await self.runner.setup()
        site = web.TCPSite(self.runner, 'localhost', self.proxy_port)
        await site.start()
        print(f"{Fore.GREEN}✓ Proxy server started on port {self.proxy_port}{Style.RESET_ALL}")

    async def stop(self):
        """Stop the proxy server"""
        if self.runner:
            await self.runner.cleanup()


class ProxyTracer:
    """Tracer that uses proxy to intercept agent communication"""

    def __init__(self, proxy_port: int = 8888):
        self.proxy_port = proxy_port
        self.trace_queue = queue.Queue()
        self.events = []
        self.proxy_server = ProxyServer(proxy_port, self.trace_queue)

    async def trace_query(self, query: str, master_url: str, duration: int = 30):
        """Execute query through proxy and trace communication"""
        print(f"\n{Fore.CYAN}=== PROXY-BASED A2A TRACER ==={Style.RESET_ALL}")
        print(f"Query: {query}")
        print(f"Proxy Port: {self.proxy_port}")
        print(f"Master URL: {master_url}")
        print(f"Trace Duration: {duration}s")
        print()

        # Start proxy server
        await self.proxy_server.start()

        # Process events in background
        event_processor = threading.Thread(target=self._process_events)
        event_processor.daemon = True
        event_processor.start()

        # Configure proxy for the client session
        proxy_url = f"http://localhost:{self.proxy_port}"

        try:
            print(f"{Fore.YELLOW}📡 Sending query through proxy...{Style.RESET_ALL}\n")

            # Note: For this to work fully, agents would need to use the proxy
            # For demonstration, we'll make the initial request through proxy
            async with aiohttp.ClientSession() as session:
                payload = {
                    "jsonrpc": "2.0",
                    "method": "message/send",
                    "params": {
                        "message": {
                            "id": f"proxy_trace_{int(time.time())}",
                            "timestamp": datetime.now().isoformat(),
                            "role": "user",
                            "content": query
                        }
                    },
                    "id": f"proxy_trace_{int(time.time())}"
                }

                # Send request (would go through proxy if configured)
                async with session.post(master_url, json=payload) as response:
                    result = await response.json()
                    print(f"{Fore.GREEN}✓ Response received{Style.RESET_ALL}")

                    if result.get('result', {}).get('result', {}).get('message'):
                        content = result['result']['result']['message'].get('content', '')
                        print(f"\n{Fore.CYAN}Response Preview:{Style.RESET_ALL}")
                        print(f"{content[:300]}...")

            # Continue monitoring
            print(f"\n{Fore.YELLOW}📡 Monitoring for {duration} seconds...{Style.RESET_ALL}")
            await asyncio.sleep(duration)

        finally:
            # Stop proxy
            await self.proxy_server.stop()

            # Process remaining events
            time.sleep(1)
            while not self.trace_queue.empty():
                self._process_single_event()

            # Print summary
            self._print_summary()

    def _process_events(self):
        """Process events from queue"""
        while True:
            try:
                self._process_single_event()
            except:
                time.sleep(0.1)

    def _process_single_event(self):
        """Process a single event"""
        try:
            event = self.trace_queue.get(timeout=0.5)
            self.events.append(event)
            self._display_event(event)
        except queue.Empty:
            pass

    def _display_event(self, event: Dict):
        """Display an event in colored format"""
        timestamp = event['timestamp'].split('T')[1][:12]
        event_type = event['type']

        if event_type == 'PROXY_REQUEST':
            print(f"{Fore.MAGENTA}[{timestamp}] PROXY_REQUEST")
            print(f"    {event['method']} {event['url']}")
            if event.get('payload'):
                print(f"    Payload: {str(event['payload'])[:100]}...{Style.RESET_ALL}")

        elif event_type == 'PROXY_RESPONSE':
            print(f"{Fore.GREEN}[{timestamp}] PROXY_RESPONSE")
            print(f"    Status: {event['status']} from {event['source']}{Style.RESET_ALL}")

        elif event_type == 'PROXY_ERROR':
            print(f"{Fore.RED}[{timestamp}] PROXY_ERROR")
            print(f"    URL: {event['url']}")
            print(f"    Error: {event['error']}{Style.RESET_ALL}")

    def _print_summary(self):
        """Print summary of captured events"""
        print(f"\n{Fore.CYAN}=== PROXY TRACE SUMMARY ==={Style.RESET_ALL}")
        print(f"Total events captured: {len(self.events)}")

        # Count event types
        event_counts = {}
        intercepted_calls = []

        for event in self.events:
            event_type = event['type']
            event_counts[event_type] = event_counts.get(event_type, 0) + 1

            if event_type == 'PROXY_REQUEST':
                url = event.get('url', '')
                if 'localhost' in url and '5040' not in url:
                    intercepted_calls.append(url)

        print(f"Event breakdown:")
        for event_type, count in sorted(event_counts.items()):
            print(f"  {event_type}: {count}")

        if intercepted_calls:
            print(f"\n{Fore.GREEN}✅ Intercepted A2A Calls:{Style.RESET_ALL}")
            for call in intercepted_calls[:10]:
                print(f"  {call}")
        else:
            print(f"\n{Fore.YELLOW}ℹ️  No A2A calls intercepted")
            print(f"   Note: Agents need to be configured to use the proxy")
            print(f"   Or use the network_tracer.py with sudo for transparent capture{Style.RESET_ALL}")

        # Save trace
        filename = f"traces/proxy_trace_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        with open(filename, 'w') as f:
            json.dump(self.events, f, indent=2)
        print(f"\nTrace saved to: {filename}")


async def main():
    parser = argparse.ArgumentParser(description='Proxy-based A2A Tracer')
    parser.add_argument('query', nargs='?', help='Query to send')
    parser.add_argument('--proxy-port', type=int, default=8888, help='Proxy server port')
    parser.add_argument('--master-url', default='http://localhost:5040/', help='Master URL')
    parser.add_argument('--duration', type=int, default=30, help='Trace duration')

    args = parser.parse_args()

    if not args.query:
        args.query = "Create a job posting for Senior Developer"

    tracer = ProxyTracer(args.proxy_port)
    await tracer.trace_query(args.query, args.master_url, args.duration)


if __name__ == "__main__":
    asyncio.run(main())