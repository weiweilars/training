#!/usr/bin/env python3
"""
HR Recruitment System - SK Implementation Runner
Run HR recruitment agents using Semantic Kernel
Usage: python run_sk_agents.py <agent_name>
       python run_sk_agents.py --all
"""

import os
import sys
import subprocess
import argparse
import time

try:
    import psutil
    HAS_PSUTIL = True
except ImportError:
    HAS_PSUTIL = False

sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'tools'))
from hr_tools_config import AGENT_PORTS, INDIVIDUAL_AGENT_PORTS

def find_agent_config(agent_name):
    """Find agent config file in organized folder structure"""
    # Get the script directory and work from there
    script_dir = os.path.dirname(os.path.abspath(__file__))
    hr_system_root = os.path.join(script_dir, '..', '..')

    # Define search paths in order of preference
    search_paths = [
        os.path.join(hr_system_root, "hr_recruitment_agents", f"{agent_name}.yaml"),  # Legacy flat structure
        os.path.join(hr_system_root, "hr_recruitment_agents", "individual", f"{agent_name}.yaml"),  # Individual agents
        os.path.join(hr_system_root, "hr_recruitment_agents", "team_coordinators", f"{agent_name}.yaml"),  # Team coordinators
    ]

    for path in search_paths:
        abs_path = os.path.abspath(path)
        if os.path.exists(abs_path):
            return abs_path

    return None

def run_agent(agent_name):
    """Run a single agent with SK implementation"""

    if agent_name not in AGENT_PORTS:
        print(f"❌ Unknown agent: {agent_name}")
        print(f"Available agents: {', '.join(AGENT_PORTS.keys())}")
        return False

    port = AGENT_PORTS[agent_name]

    # Paths - use our local configs directly
    script_dir = os.path.dirname(os.path.abspath(__file__))
    sk_server_dir = os.path.join(script_dir, "..", "..", "..", "a2a_training", "5_sk_a2a_custom_mcp_agent")
    sk_server_dir = os.path.abspath(sk_server_dir)
    local_config = find_agent_config(agent_name)

    if not os.path.exists(f"{sk_server_dir}/sk_a2a_server.py"):
        print(f"❌ SK server not found: {sk_server_dir}/sk_a2a_server.py")
        return False

    if not local_config:
        print(f"❌ Config file not found for agent: {agent_name}")
        print("   Searched in: hr_recruitment_agents/[individual|team_coordinators]/")
        return False

    config_path = os.path.abspath(local_config)

    print(f"ℹ️  Using config: {config_path}")
    
    print(f"\n{'='*60}")
    print(f" Starting {agent_name} (Semantic Kernel) ")
    print(f"{'='*60}")
    print(f"Port: {port}")
    print(f"URL: http://localhost:{port}")
    print(f"Agent Card: http://localhost:{port}/.well-known/agent-card.json")
    print(f"{'='*60}")
    
    # Run the agent
    try:
        os.chdir(sk_server_dir)
        subprocess.run([
            sys.executable,
            "sk_a2a_server.py",
            "--config", config_path,
            "--port", str(port)
        ])
        
    except KeyboardInterrupt:
        print(f"\n✅ {agent_name} stopped")
    except Exception as e:
        print(f"❌ Error: {e}")
        return False
    
    return True

def clean_agent_ports():
    """Clean up any processes using agent ports"""
    cleaned_ports = []

    if HAS_PSUTIL:
        # Use psutil for better process detection
        for agent_name, port in AGENT_PORTS.items():
            for proc in psutil.process_iter(['pid', 'name']):
                try:
                    # Get connections separately since it's not a valid attr for process_iter
                    connections = proc.connections()
                    for conn in connections:
                        if hasattr(conn, 'laddr') and conn.laddr and conn.laddr.port == port:
                            print(f"🧹 Killing process {proc.info['pid']} using port {port} ({agent_name})")
                            proc.kill()
                            cleaned_ports.append(port)
                            break
                except (psutil.NoSuchProcess, psutil.AccessDenied, psutil.ZombieProcess):
                    continue
    else:
        # Fallback: use netstat/lsof to find processes
        for agent_name, port in AGENT_PORTS.items():
            try:
                # Try lsof first
                result = subprocess.run(
                    ["lsof", "-ti", f":{port}"], 
                    capture_output=True, text=True, timeout=5
                )
                if result.returncode == 0 and result.stdout.strip():
                    pids = result.stdout.strip().split('\n')
                    for pid in pids:
                        if pid:
                            print(f"🧹 Killing process {pid} using port {port} ({agent_name})")
                            subprocess.run(["kill", "-9", pid])
                            cleaned_ports.append(port)
            except (subprocess.TimeoutExpired, FileNotFoundError):
                # lsof not available, try netstat
                try:
                    result = subprocess.run(
                        ["netstat", "-tulpn"], 
                        capture_output=True, text=True, timeout=5
                    )
                    if result.returncode == 0:
                        for line in result.stdout.split('\n'):
                            if f":{port}" in line and "LISTEN" in line:
                                # Extract PID from netstat output
                                parts = line.split()
                                if len(parts) > 6 and "/" in parts[6]:
                                    pid = parts[6].split("/")[0]
                                    if pid.isdigit():
                                        print(f"🧹 Killing process {pid} using port {port} ({agent_name})")
                                        subprocess.run(["kill", "-9", pid])
                                        cleaned_ports.append(port)
                                        break
                except (subprocess.TimeoutExpired, FileNotFoundError):
                    pass
    
    if cleaned_ports:
        time.sleep(2)  # Wait for ports to be released
        print(f"✅ Cleaned {len(cleaned_ports)} ports")
    else:
        print("ℹ️  No ports needed cleaning")

def start_agent_background(agent_name):
    """Start a single agent in the background"""
    if agent_name not in AGENT_PORTS:
        print(f"❌ Unknown agent: {agent_name}")
        return None

    port = AGENT_PORTS[agent_name]
    local_config = find_agent_config(agent_name)
    script_dir = os.path.dirname(os.path.abspath(__file__))
    sk_server_dir = os.path.join(script_dir, "..", "..", "..", "a2a_training", "5_sk_a2a_custom_mcp_agent")
    sk_server_dir = os.path.abspath(sk_server_dir)

    if not local_config:
        print(f"❌ Config file not found for agent: {agent_name}")
        return None

    if not os.path.exists(f"{sk_server_dir}/sk_a2a_server.py"):
        print(f"❌ SK server not found: {sk_server_dir}/sk_a2a_server.py")
        return None

    config_path = os.path.abspath(local_config)
    # No need to copy - use config directly
    
    print(f"🚀 Starting {agent_name} on port {port}...")
    
    # Start in background
    try:
        proc = subprocess.Popen([
            sys.executable,
            "sk_a2a_server.py",
            "--config", config_path,
            "--port", str(port)
        ], cwd=sk_server_dir)
        
        return proc
    except Exception as e:
        print(f"❌ Failed to start {agent_name}: {e}")
        return None

def run_all_agents():
    """Run all INDIVIDUAL agents simultaneously in background (not coordinators)"""
    print(f"\n{'='*70}")
    print(f" Starting ALL Individual HR Agents (Semantic Kernel) ")
    print(f"{'='*70}")
    print(f" Note: This starts only individual agents (ports 5020-5030)")
    print(f" Use start_coordinators.sh for team coordinators")
    print(f"{'='*70}")

    # Clean ports first
    clean_agent_ports()

    processes = {}
    failed_agents = []

    # Start only individual agents
    for agent_name in INDIVIDUAL_AGENT_PORTS.keys():
        proc = start_agent_background(agent_name)
        if proc:
            processes[agent_name] = proc
        else:
            failed_agents.append(agent_name)

        # Add small delay between starts to avoid resource contention
        time.sleep(1)
    
    if failed_agents:
        print(f"\n❌ Failed to start: {', '.join(failed_agents)}")
    
    if not processes:
        print("\n❌ No agents started successfully")
        return False
    
    print(f"\n✅ Started {len(processes)} individual agents successfully:")
    print("-" * 50)
    for agent_name, port in INDIVIDUAL_AGENT_PORTS.items():
        if agent_name in processes:
            print(f"{agent_name:<30} Port {port:<6} http://localhost:{port}")
    
    print(f"\nPress Ctrl+C to stop all agents")
    
    # Wait and handle shutdown
    try:
        while True:
            # Check if any process died
            dead_agents = []
            for agent_name, proc in processes.items():
                if proc.poll() is not None:
                    dead_agents.append(agent_name)
            
            for agent_name in dead_agents:
                print(f"⚠️  Agent {agent_name} stopped unexpectedly")
                del processes[agent_name]
            
            if not processes:
                print("\n❌ All agents have stopped")
                break
            
            time.sleep(1)
            
    except KeyboardInterrupt:
        print(f"\n🛑 Stopping all agents...")
        
        # Kill all processes
        for agent_name, proc in processes.items():
            try:
                proc.terminate()
                proc.wait(timeout=5)
                print(f"✅ Stopped {agent_name}")
            except subprocess.TimeoutExpired:
                proc.kill()
                print(f"🔪 Force killed {agent_name}")
            except Exception as e:
                print(f"⚠️  Error stopping {agent_name}: {e}")
    
    return True

def list_agents():
    """List all available agents"""
    print(f"\n{'='*70}")
    print(f" Available Individual HR Agents (Semantic Kernel) ")
    print(f"{'='*70}")

    for agent_name, port in INDIVIDUAL_AGENT_PORTS.items():
        print(f"{agent_name:<30} Port {port:<6} http://localhost:{port}")

    print(f"\n{'='*70}")
    print(f" Available Coordinator Agents (use start_coordinators.sh) ")
    print(f"{'='*70}")

    from hr_tools_config import COORDINATOR_AGENT_PORTS
    for agent_name, port in COORDINATOR_AGENT_PORTS.items():
        print(f"{agent_name:<30} Port {port:<6} http://localhost:{port}")

    print(f"\nUsage: python run_sk_agents.py <individual_agent_name>")
    print(f"Example: python run_sk_agents.py job_requisition_agent")
    print(f"For coordinators: use start_coordinators.sh")

def main():
    parser = argparse.ArgumentParser(description="Run HR Recruitment Agents with Semantic Kernel")
    parser.add_argument("agent", nargs="?", help="Agent to start")
    parser.add_argument("--list", action="store_true", help="List available agents")
    parser.add_argument("--all", action="store_true", help="Start all agents simultaneously")
    parser.add_argument("--cleanup", action="store_true", help="Clean up agent ports")
    
    args = parser.parse_args()
    
    if args.list:
        list_agents()
        return 0
    
    if args.cleanup:
        print("🧹 Cleaning up agent ports...")
        clean_agent_ports()
        print("✅ Agent cleanup complete!")
        return 0
    
    if args.all:
        return 0 if run_all_agents() else 1
    
    if not args.agent:
        list_agents()
        return 1
    
    return 0 if run_agent(args.agent) else 1

if __name__ == "__main__":
    sys.exit(main())