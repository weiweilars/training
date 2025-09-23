#!/usr/bin/env python3
"""
Test the MCP scanner with our test tools
"""

import sys
from pathlib import Path
from utils.scanner import MCPToolScanner
from utils.logger import setup_logger


def test_scanner_with_folder(folder_path: Path, logger):
    """Test scanner with a specific folder"""
    print(f"\n{'='*60}")
    print(f"TESTING: {folder_path}")
    print(f"{'='*60}")

    scanner = MCPToolScanner(logger)

    try:
        result = scanner.scan_folder(folder_path)

        if result:
            print(f"✅ Found MCP tool!")
            print(f"📁 File: {result['file_path']}")
            print(f"🐍 Module: {result['module_name']}")
            print(f"🔧 Instance: {result['instance_name']}")
            print(f"📦 Instance info: {result['instance_info']}")

            # Environment variables
            env_vars = result.get('env_vars', [])
            if env_vars:
                print(f"🌍 Environment variables found: {len(env_vars)}")
                for var in env_vars:
                    print(f"   - {var}")

                # Test validation
                validation = scanner.validate_environment(env_vars)
                if validation['missing']:
                    print(f"❌ Missing env vars: {validation['missing']}")
                if validation['present']:
                    print(f"✅ Present env vars: {list(validation['present'].keys())}")
            else:
                print("🌍 No environment variables detected")

            # Check for additional files
            if result.get('requirements_path'):
                print(f"📋 Requirements: {result['requirements_path']}")

            if result.get('env_example_path'):
                print(f"📄 Env example: {result['env_example_path']}")
                env_example = result.get('env_vars_from_example', {})
                if env_example:
                    print(f"   Example vars: {list(env_example.keys())}")

            return True
        else:
            print("❌ No MCP tool found")
            return False

    except Exception as e:
        print(f"💥 Error: {e}")
        return False


def main():
    """Test the scanner with our test tools"""
    logger = setup_logger("test_scanner", "INFO")

    print("🔍 Testing MCP Tool Scanner")
    print("Testing with custom test tools...")

    # Test paths
    weather_path = Path("test_tools/weather_service")
    calc_path = Path("test_tools/calc_server")

    success_count = 0

    # Test weather service
    if weather_path.exists():
        if test_scanner_with_folder(weather_path, logger):
            success_count += 1
    else:
        print(f"❌ Weather tool not found at: {weather_path}")

    # Test calculator service
    if calc_path.exists():
        if test_scanner_with_folder(calc_path, logger):
            success_count += 1
    else:
        print(f"❌ Calculator tool not found at: {calc_path}")

    print(f"\n{'='*60}")
    print(f"SUMMARY: {success_count}/2 tools detected successfully")
    print(f"{'='*60}")

    if success_count == 2:
        print("🎉 All tests passed! Scanner working correctly.")
        print("\nNext steps:")
        print("1. Set environment variables for the tools")
        print("2. Test deployment with: python main.py test_tools/weather_service")
        print("3. Test deployment with: python main.py test_tools/calc_server")
    else:
        print("⚠️  Some tests failed. Check the scanner implementation.")

    return 0 if success_count == 2 else 1


if __name__ == "__main__":
    sys.exit(main())