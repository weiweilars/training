#!/usr/bin/env python3
"""
HR Recruitment System - Complete Test Suite Runner
Runs all 4 levels of testing in proper order
"""

import subprocess
import sys
import time
from datetime import datetime

class TestSuiteRunner:
    """Master test runner for all HR system tests"""

    def __init__(self):
        self.test_levels = [
            {
                "level": 1,
                "name": "MCP Tools Test",
                "script": "test_tools.py",
                "description": "Direct testing of MCP tools (foundation layer)",
                "required": True
            },
            {
                "level": 2,
                "name": "Individual Agents Test",
                "script": "test_individual_agents.py",
                "description": "Testing individual specialist agents with MCP tools",
                "required": True
            },
            {
                "level": 3,
                "name": "Team Coordinators Test",
                "script": "test_coordinators.py",
                "description": "Testing team coordination and A2A communication",
                "required": True
            },
            {
                "level": 4,
                "name": "Master Integration Test",
                "script": "test_master.py",
                "description": "Complete system integration and end-to-end workflows",
                "required": True
            }
        ]

        self.results = {}

    def run_test_level(self, test_config):
        """Run a single test level"""
        level = test_config["level"]
        name = test_config["name"]
        script = test_config["script"]
        description = test_config["description"]

        print(f"\n{'='*80}")
        print(f"🧪 LEVEL {level}: {name}")
        print(f"{'='*80}")
        print(f"Description: {description}")
        print(f"Script: {script}")
        print(f"Started: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print(f"{'='*80}")

        try:
            # Run the test script
            start_time = time.time()
            result = subprocess.run([
                sys.executable, script
            ], capture_output=True, text=True, timeout=300)  # 5 minute timeout

            end_time = time.time()
            duration = end_time - start_time

            success = result.returncode == 0

            self.results[level] = {
                "name": name,
                "script": script,
                "success": success,
                "duration": duration,
                "stdout": result.stdout,
                "stderr": result.stderr,
                "returncode": result.returncode
            }

            if success:
                print(f"✅ LEVEL {level} PASSED ({duration:.1f}s)")
            else:
                print(f"❌ LEVEL {level} FAILED ({duration:.1f}s)")
                if result.stderr:
                    print(f"Error output: {result.stderr[:500]}")

            return success

        except subprocess.TimeoutExpired:
            print(f"⏰ LEVEL {level} TIMEOUT (300s)")
            self.results[level] = {
                "name": name,
                "script": script,
                "success": False,
                "duration": 300,
                "error": "Timeout after 300 seconds"
            }
            return False
        except Exception as e:
            print(f"❌ LEVEL {level} ERROR: {str(e)}")
            self.results[level] = {
                "name": name,
                "script": script,
                "success": False,
                "duration": 0,
                "error": str(e)
            }
            return False

    def run_all_tests(self, start_level=1, stop_on_failure=True):
        """Run all test levels in sequence"""
        print(f"\n🚀 HR Recruitment System - Complete Test Suite")
        print(f"=" * 80)
        print(f"Testing all 4 levels of the HR recruitment system")
        print(f"Start level: {start_level}")
        print(f"Stop on failure: {stop_on_failure}")
        print(f"Total test levels: {len(self.test_levels)}")
        print(f"Started at: {datetime.now()}")
        print(f"=" * 80)

        overall_start_time = time.time()
        successful_levels = 0
        total_levels = len([t for t in self.test_levels if t["level"] >= start_level])

        for test_config in self.test_levels:
            if test_config["level"] < start_level:
                continue

            success = self.run_test_level(test_config)

            if success:
                successful_levels += 1
            else:
                if stop_on_failure and test_config["required"]:
                    print(f"\n🛑 Stopping test suite due to failure in required level {test_config['level']}")
                    break

            # Add delay between test levels
            if test_config["level"] < 4:  # Don't delay after last test
                time.sleep(2)

        overall_end_time = time.time()
        overall_duration = overall_end_time - overall_start_time

        # Generate final report
        self.generate_final_report(successful_levels, total_levels, overall_duration)

        return successful_levels == total_levels

    def generate_final_report(self, successful_levels, total_levels, overall_duration):
        """Generate comprehensive final report"""
        print(f"\n" + "=" * 80)
        print(f"🏁 COMPLETE TEST SUITE RESULTS")
        print(f"=" * 80)
        print(f"Total Duration: {overall_duration:.1f}s")
        print(f"Levels Completed: {successful_levels}/{total_levels}")
        success_rate = (successful_levels / total_levels * 100) if total_levels > 0 else 0
        print(f"Success Rate: {success_rate:.1f}%")
        print(f"Completed at: {datetime.now()}")
        print(f"=" * 80)

        # Level-by-level results
        for level_num in sorted(self.results.keys()):
            result = self.results[level_num]
            status = "✅ PASS" if result["success"] else "❌ FAIL"
            duration = result.get("duration", 0)

            print(f"\nLevel {level_num}: {result['name']}")
            print(f"  Status: {status} ({duration:.1f}s)")

            if not result["success"]:
                if "error" in result:
                    print(f"  Error: {result['error']}")
                elif result.get("stderr"):
                    print(f"  Error: {result['stderr'][:200]}...")

        # System Status Summary
        print(f"\n📊 System Status Summary:")

        if successful_levels == total_levels:
            print(f"🟢 ALL SYSTEMS GO - Complete HR recruitment system is operational")
            print(f"   ✅ MCP Tools Layer: Functional")
            print(f"   ✅ Individual Agents Layer: Functional")
            print(f"   ✅ Team Coordinators Layer: Functional")
            print(f"   ✅ Master Integration Layer: Functional")
        else:
            print(f"🔴 SYSTEM ISSUES DETECTED")

            # Determine what's working
            working_layers = []
            broken_layers = []

            for level_num, result in self.results.items():
                layer_names = {
                    1: "MCP Tools Layer",
                    2: "Individual Agents Layer",
                    3: "Team Coordinators Layer",
                    4: "Master Integration Layer"
                }

                layer_name = layer_names.get(level_num, f"Level {level_num}")

                if result["success"]:
                    working_layers.append(layer_name)
                else:
                    broken_layers.append(layer_name)

            for layer in working_layers:
                print(f"   ✅ {layer}: Functional")
            for layer in broken_layers:
                print(f"   ❌ {layer}: Issues detected")

        # Recommendations
        print(f"\n💡 Recommendations:")
        if successful_levels == total_levels:
            print(f"   🚀 System ready for production use")
            print(f"   📋 Consider running periodic health checks")
        else:
            print(f"   🔧 Fix issues in failed test levels before proceeding")
            if 1 in self.results and not self.results[1]["success"]:
                print(f"   🔧 Priority: Fix MCP tools - start with 'python manage_hr_tools.py --start-all'")
            if 2 in self.results and not self.results[2]["success"]:
                print(f"   🔧 Start individual agents - use 'python run_sk_agents.py --all'")
            if 3 in self.results and not self.results[3]["success"]:
                print(f"   🔧 Start team coordinators - use 'python run_coordinators.py --all'")

def main():
    """Main test runner function"""
    import argparse

    parser = argparse.ArgumentParser(description="Run HR System Complete Test Suite")
    parser.add_argument("--level", type=int, choices=[1,2,3,4],
                       help="Run specific test level only")
    parser.add_argument("--start-from", type=int, choices=[1,2,3,4], default=1,
                       help="Start testing from specific level")
    parser.add_argument("--continue-on-failure", action="store_true",
                       help="Continue testing even if a level fails")

    args = parser.parse_args()

    runner = TestSuiteRunner()

    if args.level:
        # Run single level
        test_config = next((t for t in runner.test_levels if t["level"] == args.level), None)
        if test_config:
            success = runner.run_test_level(test_config)
            print(f"\nLevel {args.level} {'PASSED' if success else 'FAILED'}")
            sys.exit(0 if success else 1)
        else:
            print(f"Invalid test level: {args.level}")
            sys.exit(1)
    else:
        # Run full test suite
        stop_on_failure = not args.continue_on_failure
        success = runner.run_all_tests(args.start_from, stop_on_failure)
        sys.exit(0 if success else 1)

if __name__ == "__main__":
    main()