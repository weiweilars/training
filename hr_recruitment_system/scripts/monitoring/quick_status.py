#!/usr/bin/env python3
"""
Quick System Status Checker
Provides a comprehensive overview of all HR system components
"""

import asyncio
import aiohttp
import time
import json
from datetime import datetime
from typing import Dict, List, Any, Optional

# Color output support
try:
    from colorama import init, Fore, Style
    init(autoreset=True)
    HAS_COLOR = True
except ImportError:
    HAS_COLOR = False
    # Fallback color definitions
    class Fore:
        RED = GREEN = YELLOW = BLUE = CYAN = MAGENTA = WHITE = ""
    class Style:
        RESET_ALL = ""

class SystemStatus:
    """Main system status checker"""

    def __init__(self):
        self.tool_ports = {
            "job-creation": 8051,
            "job-workflow": 8052,
            "job-templates": 8053,
            "social-sourcing": 8061,
            "talent-pool": 8062,
            "outreach": 8063,
            "document-processing": 8071,
            "matching-engine": 8072,
            "email-service": 8081,
            "engagement-tracking": 8082,
            "calendar-integration": 8091,
            "interview-workflow": 8092,
            "meeting-management": 8093,
            "test-engine": 8101,
            "assessment-library": 8102,
            "results-analysis": 8103,
            "offer-generation": 8111,
            "negotiation-management": 8112,
            "contract-management": 8113,
            "metrics-engine": 8121,
            "dashboard-generator": 8122,
            "predictive-analytics": 8123,
            "regulatory-engine": 8131,
            "data-privacy": 8132,
            "audit-management": 8133,
            "verification-engine": 8141,
            "reference-check": 8142,
            "credential-validation": 8143
        }

        self.agent_ports = {
            "job_requisition_agent": 5020,
            "sourcing_agent": 5021,
            "resume_screening_agent": 5022,
            "interview_scheduling_agent": 5023,
            "assessment_agent": 5024,
            "background_verification_agent": 5025,
            "offer_management_agent": 5026,
            "compliance_agent": 5027,
            "communication_agent": 5028,
            "analytics_reporting_agent": 5029,
            "hr_summarization_agent": 5030
        }

        self.coordinator_ports = {
            "job_pipeline_team_agent": 5031,
            "acquisition_team_agent": 5032,
            "experience_team_agent": 5033,
            "closing_team_agent": 5034,
            "master_coordinator": 5040
        }

    async def check_service(self, name: str, port: int, service_type: str) -> Dict[str, Any]:
        """Check if a service is running"""
        try:
            timeout = aiohttp.ClientTimeout(total=3)
            async with aiohttp.ClientSession(timeout=timeout) as session:
                if service_type == "tool":
                    # For MCP tools, check /mcp endpoint with tools/list
                    url = f"http://localhost:{port}/mcp"
                    headers = {
                        "Content-Type": "application/json",
                        "Accept": "application/json, text/event-stream"
                    }
                    payload = {
                        "jsonrpc": "2.0",
                        "method": "tools/list",
                        "id": 1
                    }
                else:
                    # For agents, check agent card
                    url = f"http://localhost:{port}/.well-known/agent-card.json"
                    headers = {}
                    payload = None

                if service_type == "tool":
                    async with session.post(url, json=payload, headers=headers) as response:
                        if response.status == 200:
                            # MCP tools return text/event-stream, just check they respond
                            try:
                                response_text = await response.text()
                                # If we get any response, the tool is running
                                return {
                                    "status": "running",
                                    "port": port,
                                    "response_time": response.headers.get("X-Response-Time", "N/A"),
                                    "data": {"response": "MCP tool responding"}
                                }
                            except:
                                return {
                                    "status": "running",
                                    "port": port,
                                    "response_time": response.headers.get("X-Response-Time", "N/A"),
                                    "data": {"response": "MCP tool responding"}
                                }
                        else:
                            return {
                                "status": "error",
                                "port": port,
                                "error": f"HTTP {response.status}"
                            }
                else:
                    async with session.get(url) as response:
                        if response.status == 200:
                            data = await response.json()
                            return {
                                "status": "running",
                                "port": port,
                                "response_time": response.headers.get("X-Response-Time", "N/A"),
                                "data": data
                            }
                        else:
                            return {
                                "status": "error",
                                "port": port,
                                "error": f"HTTP {response.status}"
                            }
        except asyncio.TimeoutError:
            return {
                "status": "timeout",
                "port": port,
                "error": "Connection timeout"
            }
        except Exception as e:
            return {
                "status": "down",
                "port": port,
                "error": str(e)
            }

    async def check_all_services(self) -> Dict[str, Dict[str, Any]]:
        """Check all system services"""
        tasks = []
        service_info = {}

        # Check tools
        for name, port in self.tool_ports.items():
            task = self.check_service(name, port, "tool")
            tasks.append((f"tool_{name}", task))

        # Check agents
        for name, port in self.agent_ports.items():
            task = self.check_service(name, port, "agent")
            tasks.append((f"agent_{name}", task))

        # Check coordinators
        for name, port in self.coordinator_ports.items():
            task = self.check_service(name, port, "coordinator")
            tasks.append((f"coordinator_{name}", task))

        # Execute all checks concurrently
        results = await asyncio.gather(*[task for _, task in tasks], return_exceptions=True)

        # Build results dictionary
        for (service_name, _), result in zip(tasks, results):
            if isinstance(result, Exception):
                service_info[service_name] = {
                    "status": "error",
                    "error": str(result)
                }
            else:
                service_info[service_name] = result

        return service_info

    def print_status_header(self):
        """Print status header"""
        print(f"\n{Fore.CYAN}{'='*80}{Style.RESET_ALL}")
        print(f"{Fore.CYAN}HR RECRUITMENT SYSTEM - QUICK STATUS CHECK{Style.RESET_ALL}")
        print(f"{Fore.CYAN}Timestamp: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}{Style.RESET_ALL}")
        print(f"{Fore.CYAN}{'='*80}{Style.RESET_ALL}\n")

    def print_service_group(self, title: str, services: Dict[str, Any], prefix: str):
        """Print status for a group of services"""
        print(f"{Fore.YELLOW}{title}{Style.RESET_ALL}")
        print(f"{Fore.YELLOW}{'-' * len(title)}{Style.RESET_ALL}")

        running = 0
        total = 0

        for name, info in services.items():
            if not name.startswith(prefix):
                continue

            total += 1
            display_name = name.replace(prefix, "").replace("_", " ").title()
            port = info.get("port", "N/A")
            status = info.get("status", "unknown")

            if status == "running":
                running += 1
                print(f"{Fore.GREEN}✓{Style.RESET_ALL} {display_name:<30} Port {port:<5} {Fore.GREEN}RUNNING{Style.RESET_ALL}")
            elif status == "timeout":
                print(f"{Fore.YELLOW}⚠{Style.RESET_ALL} {display_name:<30} Port {port:<5} {Fore.YELLOW}TIMEOUT{Style.RESET_ALL}")
            else:
                error = info.get("error", "Unknown error")
                print(f"{Fore.RED}✗{Style.RESET_ALL} {display_name:<30} Port {port:<5} {Fore.RED}DOWN{Style.RESET_ALL} ({error})")

        # Summary
        if total > 0:
            percentage = (running / total) * 100
            color = Fore.GREEN if percentage == 100 else Fore.YELLOW if percentage >= 50 else Fore.RED
            print(f"\n{color}Status: {running}/{total} services running ({percentage:.1f}%){Style.RESET_ALL}\n")
        else:
            print(f"\n{Fore.YELLOW}No services found in this category{Style.RESET_ALL}\n")

    def print_summary(self, services: Dict[str, Any]):
        """Print overall system summary"""
        total_services = len(services)
        running_services = sum(1 for s in services.values() if s.get("status") == "running")

        print(f"{Fore.CYAN}{'='*80}{Style.RESET_ALL}")
        print(f"{Fore.CYAN}SYSTEM SUMMARY{Style.RESET_ALL}")
        print(f"{Fore.CYAN}{'='*80}{Style.RESET_ALL}")

        # Overall status
        percentage = (running_services / total_services) * 100 if total_services > 0 else 0
        if percentage == 100:
            status_color = Fore.GREEN
            status_text = "FULLY OPERATIONAL"
        elif percentage >= 75:
            status_color = Fore.YELLOW
            status_text = "MOSTLY OPERATIONAL"
        elif percentage >= 25:
            status_color = Fore.YELLOW
            status_text = "PARTIALLY OPERATIONAL"
        else:
            status_color = Fore.RED
            status_text = "SYSTEM DOWN"

        print(f"Overall Status: {status_color}{status_text}{Style.RESET_ALL}")
        print(f"Services Running: {running_services}/{total_services} ({percentage:.1f}%)")

        # Component breakdown
        tools_running = sum(1 for name, s in services.items()
                          if name.startswith("tool_") and s.get("status") == "running")
        tools_total = sum(1 for name in services.keys() if name.startswith("tool_"))

        agents_running = sum(1 for name, s in services.items()
                           if name.startswith("agent_") and s.get("status") == "running")
        agents_total = sum(1 for name in services.keys() if name.startswith("agent_"))

        coordinators_running = sum(1 for name, s in services.items()
                                 if name.startswith("coordinator_") and s.get("status") == "running")
        coordinators_total = sum(1 for name in services.keys() if name.startswith("coordinator_"))

        print(f"\nComponent Breakdown:")
        print(f"  MCP Tools:     {tools_running}/{tools_total}")
        print(f"  Agents:        {agents_running}/{agents_total}")
        print(f"  Coordinators:  {coordinators_running}/{coordinators_total}")

        # Recommendations
        print(f"\n{Fore.CYAN}Recommendations:{Style.RESET_ALL}")
        if percentage == 100:
            print(f"{Fore.GREEN}✓ System is fully operational{Style.RESET_ALL}")
        else:
            if tools_running < tools_total:
                print(f"{Fore.YELLOW}• Start missing MCP tools: ./start_tools.sh --start-all{Style.RESET_ALL}")
            if agents_running < agents_total:
                print(f"{Fore.YELLOW}• Start missing agents: ./start_agents.sh --all{Style.RESET_ALL}")
            if coordinators_running < coordinators_total:
                print(f"{Fore.YELLOW}• Start missing coordinators: ./start_coordinators.sh --all{Style.RESET_ALL}")

        print(f"{Fore.CYAN}{'='*80}{Style.RESET_ALL}\n")

async def main():
    """Main function"""
    status_checker = SystemStatus()

    # Print header
    status_checker.print_status_header()

    print(f"{Fore.BLUE}Checking all system components...{Style.RESET_ALL}\n")

    # Check all services
    start_time = time.time()
    services = await status_checker.check_all_services()
    check_time = time.time() - start_time

    # Print results by category
    status_checker.print_service_group("MCP TOOLS (Level 1 - Foundation)", services, "tool_")
    status_checker.print_service_group("INDIVIDUAL AGENTS (Level 2 - Specialists)", services, "agent_")
    status_checker.print_service_group("COORDINATORS (Level 3 - Orchestration)", services, "coordinator_")

    # Print summary
    status_checker.print_summary(services)

    print(f"{Fore.CYAN}Status check completed in {check_time:.2f} seconds{Style.RESET_ALL}")

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print(f"\n{Fore.YELLOW}Status check interrupted by user{Style.RESET_ALL}")
    except Exception as e:
        print(f"\n{Fore.RED}Error during status check: {e}{Style.RESET_ALL}")