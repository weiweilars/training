#!/usr/bin/env python3
"""
HR Recruitment System - Team Coordinator Runner
Run team coordinator agents using Semantic Kernel with proper startup order
Usage: python run_coordinators.py <coordinator_name>
       python run_coordinators.py --all
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

# Team Coordinator Agent Ports (different from individual agents)
COORDINATOR_PORTS = {
    "acquisition_team_agent": 5032,
    "experience_team_agent": 5033,
    "closing_team_agent": 5034,
    "master_coordinator_agent": 5040
}

# Startup order - individual coordinators first, master last
STARTUP_ORDER = [
    "acquisition_team_agent",    # Must start before master
    "experience_team_agent",     # Must start before master
    "closing_team_agent",        # Must start before master
    "master_coordinator_agent"   # Starts last, connects to others
]

def find_coordinator_config(coordinator_name):
    """Find coordinator config file in team_coordinators folder"""
    # Get the script directory and work from there
    script_dir = os.path.dirname(os.path.abspath(__file__))
    hr_system_root = os.path.join(script_dir, '..', '..')

    config_path = os.path.join(hr_system_root, "hr_recruitment_agents", "team_coordinators", f"{coordinator_name}.yaml")
    abs_config_path = os.path.abspath(config_path)

    if os.path.exists(abs_config_path):
        return abs_config_path

    return None

def run_coordinator(coordinator_name):
    """Run a single team coordinator with SK implementation"""

    if coordinator_name not in COORDINATOR_PORTS:
        print(f"❌ Unknown coordinator: {coordinator_name}")
        print(f"Available coordinators: {', '.join(COORDINATOR_PORTS.keys())}")
        return False

    port = COORDINATOR_PORTS[coordinator_name]

    # Paths - use our local configs directly
    script_dir = os.path.dirname(os.path.abspath(__file__))
    sk_server_dir = os.path.join(script_dir, "..", "..", "..", "a2a_training", "5_sk_a2a_custom_mcp_agent")
    sk_server_dir = os.path.abspath(sk_server_dir)
    local_config = find_coordinator_config(coordinator_name)

    if not os.path.exists(f"{sk_server_dir}/sk_a2a_server.py"):
        print(f"❌ SK server not found: {sk_server_dir}/sk_a2a_server.py")
        return False

    if not local_config:
        print(f"❌ Config file not found for coordinator: {coordinator_name}")
        print("   Searched in: ../../hr_recruitment_agents/team_coordinators/")
        return False

    config_path = os.path.abspath(local_config)

    print(f"ℹ️  Using config: {config_path}")

    print(f"\n{'='*60}")
    print(f" Starting {coordinator_name} (Team Coordinator) ")
    print(f"{'='*60}")
    print(f"Port: {port}")
    print(f"URL: http://localhost:{port}")
    print(f"Agent Card: http://localhost:{port}/.well-known/agent-card.json")
    print(f"{'='*60}")

    # Run the coordinator
    try:
        os.chdir(sk_server_dir)
        subprocess.run([
            sys.executable,
            "sk_a2a_server.py",
            "--config", config_path,
            "--port", str(port)
        ])

    except KeyboardInterrupt:
        print(f"\n✅ {coordinator_name} stopped")
    except Exception as e:
        print(f"❌ Error: {e}")
        return False

    return True

def clean_coordinator_ports():
    """Clean up any processes using coordinator ports"""
    cleaned_ports = []

    if HAS_PSUTIL:
        # Use psutil for better process detection
        for coordinator_name, port in COORDINATOR_PORTS.items():
            for proc in psutil.process_iter(['pid', 'name']):
                try:
                    connections = proc.connections()
                    for conn in connections:
                        if hasattr(conn, 'laddr') and conn.laddr and conn.laddr.port == port:
                            print(f"🧹 Killing process {proc.info['pid']} using port {port} ({coordinator_name})")
                            proc.kill()
                            cleaned_ports.append(port)
                            break
                except (psutil.NoSuchProcess, psutil.AccessDenied, psutil.ZombieProcess):
                    continue
    else:
        # Fallback: use netstat/lsof to find processes
        for coordinator_name, port in COORDINATOR_PORTS.items():
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
                            print(f"🧹 Killing process {pid} using port {port} ({coordinator_name})")
                            subprocess.run(["kill", "-9", pid])
                            cleaned_ports.append(port)
            except (subprocess.TimeoutExpired, FileNotFoundError):
                pass

    if cleaned_ports:
        time.sleep(2)  # Wait for ports to be released
        print(f"✅ Cleaned {len(cleaned_ports)} ports")
    else:
        print("ℹ️  No ports needed cleaning")

def start_coordinator_background(coordinator_name):
    """Start a single coordinator in the background"""
    if coordinator_name not in COORDINATOR_PORTS:
        print(f"❌ Unknown coordinator: {coordinator_name}")
        return None

    port = COORDINATOR_PORTS[coordinator_name]
    local_config = find_coordinator_config(coordinator_name)
    script_dir = os.path.dirname(os.path.abspath(__file__))
    sk_server_dir = os.path.join(script_dir, "..", "..", "..", "a2a_training", "5_sk_a2a_custom_mcp_agent")
    sk_server_dir = os.path.abspath(sk_server_dir)

    if not local_config:
        print(f"❌ Config file not found for coordinator: {coordinator_name}")
        return None

    if not os.path.exists(f"{sk_server_dir}/sk_a2a_server.py"):
        print(f"❌ SK server not found: {sk_server_dir}/sk_a2a_server.py")
        return None

    config_path = os.path.abspath(local_config)

    print(f"🚀 Starting {coordinator_name} on port {port}...")

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
        print(f"❌ Failed to start {coordinator_name}: {e}")
        return None

def wait_for_coordinator_ready(coordinator_name, port, timeout=30):
    """Wait for coordinator to be ready and accepting connections"""
    import urllib.request
    import urllib.error

    print(f"⏳ Waiting for {coordinator_name} to be ready...")
    start_time = time.time()

    while time.time() - start_time < timeout:
        try:
            # Try to access the agent card endpoint
            urllib.request.urlopen(f"http://localhost:{port}/.well-known/agent-card.json", timeout=2)
            print(f"✅ {coordinator_name} is ready!")
            return True
        except (urllib.error.URLError, urllib.error.HTTPError):
            time.sleep(1)
            continue

    print(f"⚠️  Timeout waiting for {coordinator_name} to be ready")
    return False

def run_all_coordinators():
    """Run all team coordinators in proper startup order"""
    print(f"\n{'='*70}")
    print(f" Starting Team Coordinator Agents in Proper Order ")
    print(f"{'='*70}")
    print("📋 Startup Order:")
    print("   1. Individual Team Coordinators (acquisition, experience, closing)")
    print("   2. Master Coordinator (connects to individual coordinators)")
    print(f"{'='*70}")

    # Clean ports first
    clean_coordinator_ports()

    processes = {}
    failed_coordinators = []

    # Start coordinators in proper order
    for i, coordinator_name in enumerate(STARTUP_ORDER, 1):
        print(f"\n🔄 Step {i}/{len(STARTUP_ORDER)}: Starting {coordinator_name}")

        proc = start_coordinator_background(coordinator_name)
        if proc:
            processes[coordinator_name] = proc

            # Wait for individual coordinators to be ready before starting master
            if coordinator_name != "master_coordinator_agent":
                port = COORDINATOR_PORTS[coordinator_name]
                if wait_for_coordinator_ready(coordinator_name, port):
                    print(f"✅ {coordinator_name} ready for connections")
                    # Add delay before next coordinator
                    time.sleep(2)
                else:
                    print(f"⚠️  {coordinator_name} may not be fully ready")
            else:
                # Master coordinator - give it more time to connect to others
                time.sleep(5)
        else:
            failed_coordinators.append(coordinator_name)
            print(f"❌ Failed to start {coordinator_name}")

    if failed_coordinators:
        print(f"\n❌ Failed to start: {', '.join(failed_coordinators)}")

    if not processes:
        print("\n❌ No coordinators started successfully")
        return False

    print(f"\n✅ Started {len(processes)} coordinators successfully:")
    print("-" * 50)
    for coordinator_name in STARTUP_ORDER:
        if coordinator_name in processes:
            port = COORDINATOR_PORTS[coordinator_name]
            print(f"{coordinator_name:<30} Port {port:<6} http://localhost:{port}")

    print(f"\n💡 Architecture: Individual Coordinators → Master Coordinator")
    print(f"Press Ctrl+C to stop all coordinators")

    # Wait and handle shutdown
    try:
        while True:
            # Check if any process died
            dead_coordinators = []
            for coordinator_name, proc in processes.items():
                if proc.poll() is not None:
                    dead_coordinators.append(coordinator_name)

            for coordinator_name in dead_coordinators:
                print(f"⚠️  Coordinator {coordinator_name} stopped unexpectedly")
                del processes[coordinator_name]

            if not processes:
                print("\n❌ All coordinators have stopped")
                break

            time.sleep(1)

    except KeyboardInterrupt:
        print(f"\n🛑 Stopping all coordinators...")

        # Kill processes in reverse order (master first, then individual coordinators)
        shutdown_order = list(reversed(STARTUP_ORDER))

        for coordinator_name in shutdown_order:
            if coordinator_name in processes:
                proc = processes[coordinator_name]
                try:
                    proc.terminate()
                    proc.wait(timeout=5)
                    print(f"✅ Stopped {coordinator_name}")
                except subprocess.TimeoutExpired:
                    proc.kill()
                    print(f"🔪 Force killed {coordinator_name}")
                except Exception as e:
                    print(f"⚠️  Error stopping {coordinator_name}: {e}")

    return True

def list_coordinators():
    """List all available coordinators"""
    print(f"\n{'='*70}")
    print(f" Available HR Team Coordinator Agents (Semantic Kernel) ")
    print(f"{'='*70}")

    print("📋 Individual Team Coordinators:")
    for coordinator_name in STARTUP_ORDER[:-1]:  # All except master
        port = COORDINATOR_PORTS[coordinator_name]
        print(f"   {coordinator_name:<30} Port {port}")

    print("\n📋 Master Coordinator:")
    master_name = STARTUP_ORDER[-1]
    port = COORDINATOR_PORTS[master_name]
    print(f"   {master_name:<30} Port {port}")

    print(f"\n💡 Startup Order: {' → '.join(STARTUP_ORDER)}")
    print(f"\nUsage: python run_coordinators.py <coordinator_name>")
    print(f"Example: python run_coordinators.py acquisition_team_agent")
    print(f"         python run_coordinators.py --all  (starts all in proper order)")

def main():
    parser = argparse.ArgumentParser(description="Run HR Team Coordinator Agents with Semantic Kernel")
    parser.add_argument("coordinator", nargs="?", help="Coordinator to start")
    parser.add_argument("--list", action="store_true", help="List available coordinators")
    parser.add_argument("--all", action="store_true", help="Start all coordinators in proper order")
    parser.add_argument("--cleanup", action="store_true", help="Clean up coordinator ports")

    args = parser.parse_args()

    if args.list:
        list_coordinators()
        return 0

    if args.cleanup:
        print("🧹 Cleaning up coordinator ports...")
        clean_coordinator_ports()
        print("✅ Coordinator cleanup complete!")
        return 0

    if args.all:
        return 0 if run_all_coordinators() else 1

    if not args.coordinator:
        list_coordinators()
        return 1

    return 0 if run_coordinator(args.coordinator) else 1

if __name__ == "__main__":
    sys.exit(main())