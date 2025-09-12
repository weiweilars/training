#!/usr/bin/env python3
"""
Port Cleanup Script for HR Recruitment System
Kills all running processes on agent and MCP tool ports to clean up the system.
"""

import subprocess
import sys
import signal
import os

# HR Recruitment System Port Mappings
AGENT_PORTS = {
    "Job Requisition Agent": 5020,
    "Sourcing Agent": 5021, 
    "Resume Screening Agent": 5022,
    "Communication Agent": 5023,
    "Interview Scheduling Agent": 5024,
    "Assessment Agent": 5025,
    "Background Verification Agent": 5026,
    "Offer Management Agent": 5027,
    "Analytics & Reporting Agent": 5028,
    "Compliance Agent": 5029
}

MCP_TOOL_PORTS = {
    # Job Requisition Tools (8051-8053)
    "Job Creation MCP": 8051,
    "Job Workflow MCP": 8052,
    "Job Templates MCP": 8053,
    
    # Sourcing Tools (8061-8063)
    "Social Media Sourcing MCP": 8061,
    "Talent Pool Management MCP": 8062,
    "Candidate Outreach MCP": 8063,
    
    # Resume Screening Tools (8071-8072)
    "Document Processing MCP": 8071,
    "Matching Engine MCP": 8072,
    
    # Communication Tools (8081-8082)
    "Email Service MCP": 8081,
    "Engagement Tracking MCP": 8082,
    
    # Interview Scheduling Tools (8091-8093)
    "Calendar Integration MCP": 8091,
    "Interview Workflow MCP": 8092,
    "Meeting Management MCP": 8093,
    
    # Assessment Tools (8101-8103)
    "Test Engine MCP": 8101,
    "Assessment Library MCP": 8102,
    "Results Analysis MCP": 8103,
    
    # Offer Management Tools (8111-8113)
    "Offer Generation MCP": 8111,
    "Negotiation Management MCP": 8112,
    "Contract Management MCP": 8113,
    
    # Analytics & Reporting Tools (8121-8123)
    "Metrics Engine MCP": 8121,
    "Dashboard Generator MCP": 8122,
    "Predictive Analytics MCP": 8123,
    
    # Compliance Tools (8131-8133)
    "Regulatory Engine MCP": 8131,
    "Data Privacy MCP": 8132,
    "Audit Management MCP": 8133,
    
    # Background Verification Tools (8141-8143)
    "Verification Engine MCP": 8141,
    "Reference Check MCP": 8142,
    "Credential Validation MCP": 8143
}

def kill_process_on_port(port, service_name):
    """Kill process running on specified port"""
    try:
        # Find PID using port
        result = subprocess.run(
            ['lsof', '-ti', f':{port}'], 
            capture_output=True, 
            text=True, 
            check=False
        )
        
        if result.returncode == 0 and result.stdout.strip():
            pids = result.stdout.strip().split('\n')
            for pid in pids:
                if pid:
                    try:
                        os.kill(int(pid), signal.SIGTERM)
                        print(f"✓ Killed {service_name} (PID: {pid}) on port {port}")
                    except ProcessLookupError:
                        print(f"  Process {pid} already terminated")
                    except Exception as e:
                        print(f"  Error killing PID {pid}: {e}")
        else:
            print(f"  No process found on port {port} for {service_name}")
            
    except FileNotFoundError:
        # lsof not available, try alternative method
        try:
            result = subprocess.run(
                ['netstat', '-tlnp'], 
                capture_output=True, 
                text=True, 
                check=False
            )
            if result.returncode == 0:
                lines = result.stdout.split('\n')
                for line in lines:
                    if f':{port} ' in line and 'LISTEN' in line:
                        parts = line.split()
                        if len(parts) > 6 and '/' in parts[6]:
                            pid = parts[6].split('/')[0]
                            try:
                                os.kill(int(pid), signal.SIGTERM)
                                print(f"✓ Killed {service_name} (PID: {pid}) on port {port}")
                            except:
                                print(f"  Could not kill PID {pid}")
                        break
                else:
                    print(f"  No process found on port {port} for {service_name}")
        except:
            print(f"  Could not check port {port} for {service_name}")

def cleanup_agent_ports():
    """Clean up only agent ports (5020-5029)"""
    print("🧹 HR Recruitment System - Agent Port Cleanup")
    print("=" * 50)
    
    print("\n📋 Cleaning up Agent Ports (5020-5029):")
    for agent_name, port in AGENT_PORTS.items():
        kill_process_on_port(port, agent_name)
    
    print(f"\n✅ Agent port cleanup completed! Cleaned {len(AGENT_PORTS)} agent ports")

def cleanup_tool_ports():
    """Clean up only MCP tool ports (8051-8143)"""
    print("🧹 HR Recruitment System - MCP Tool Port Cleanup")
    print("=" * 50)
    
    print("\n🔧 Cleaning up MCP Tool Ports (8051-8143):")
    for tool_name, port in MCP_TOOL_PORTS.items():
        kill_process_on_port(port, tool_name)
    
    print(f"\n✅ MCP tool port cleanup completed! Cleaned {len(MCP_TOOL_PORTS)} MCP tool ports")

def cleanup_all_ports():
    """Clean up all HR recruitment system ports"""
    print("🧹 HR Recruitment System - Full Port Cleanup")
    print("=" * 50)
    
    # Cleanup Agent Ports
    print("\n📋 Cleaning up Agent Ports (5020-5029):")
    for agent_name, port in AGENT_PORTS.items():
        kill_process_on_port(port, agent_name)
    
    # Cleanup MCP Tool Ports  
    print("\n🔧 Cleaning up MCP Tool Ports (8051-8143):")
    for tool_name, port in MCP_TOOL_PORTS.items():
        kill_process_on_port(port, tool_name)
    
    print("\n✅ Full port cleanup completed!")
    print(f"   Cleaned {len(AGENT_PORTS)} agent ports")
    print(f"   Cleaned {len(MCP_TOOL_PORTS)} MCP tool ports")

def show_port_status():
    """Show current port usage status"""
    print("📊 HR Recruitment System Port Status")
    print("=" * 50)
    
    all_ports = {**AGENT_PORTS, **MCP_TOOL_PORTS}
    active_ports = []
    
    for service_name, port in all_ports.items():
        try:
            result = subprocess.run(
                ['lsof', '-ti', f':{port}'], 
                capture_output=True, 
                text=True, 
                check=False
            )
            if result.returncode == 0 and result.stdout.strip():
                active_ports.append((service_name, port))
                print(f"🟢 Port {port}: {service_name} (ACTIVE)")
            else:
                print(f"⚫ Port {port}: {service_name} (INACTIVE)")
        except FileNotFoundError:
            print(f"❓ Port {port}: {service_name} (UNKNOWN - lsof not available)")
    
    print(f"\nSummary: {len(active_ports)} active ports out of {len(all_ports)} total")

def main():
    if len(sys.argv) > 1:
        if sys.argv[1] == '--agents':
            cleanup_agent_ports()
        elif sys.argv[1] == '--tools':
            cleanup_tool_ports()
        elif sys.argv[1] == '--all':
            cleanup_all_ports()
        elif sys.argv[1] == '--status':
            show_port_status()
        elif sys.argv[1] == '--help':
            print("HR Recruitment System Port Cleanup Tool")
            print("\nUsage:")
            print("  python cleanup_ports.py           # Clean up all ports (default)")
            print("  python cleanup_ports.py --all     # Clean up all ports")
            print("  python cleanup_ports.py --agents  # Clean up only agent ports (5020-5029)")
            print("  python cleanup_ports.py --tools   # Clean up only MCP tool ports (8051-8143)")
            print("  python cleanup_ports.py --status  # Show port status")
            print("  python cleanup_ports.py --help    # Show this help")
            print("\nPort Ranges:")
            print("  Agent Ports: 5020-5029 (10 agents)")
            print("  MCP Tool Ports: 8051-8143 (25 tools)")
            print("\nExamples:")
            print("  python cleanup_ports.py --agents  # Only kill agent processes")
            print("  python cleanup_ports.py --tools   # Only kill MCP tool processes")
            print("  python cleanup_ports.py --status  # Check what's running")
        else:
            print(f"Unknown option: {sys.argv[1]}")
            print("Use --help for usage information")
    else:
        cleanup_all_ports()

if __name__ == "__main__":
    main()