#!/usr/bin/env python3
"""
Debug the scan_folder method specifically
"""

from pathlib import Path
from utils.scanner import MCPToolScanner


def debug_scan_folder():
    """Debug scan folder method"""
    scanner = MCPToolScanner()

    folder_path = Path("test_tools/weather_service")
    print(f"Testing folder: {folder_path}")
    print(f"Exists: {folder_path.exists()}")
    print(f"Is dir: {folder_path.is_dir()}")

    # Get python files
    python_files = list(folder_path.glob("**/*.py"))
    print(f"Python files found: {python_files}")

    for file_path in python_files:
        print(f"\nProcessing: {file_path}")

        # Check skip patterns
        skip_patterns = ["__pycache__", "test_", "setup.py", "__init__.py"]
        should_skip = any(pattern in str(file_path) for pattern in skip_patterns)
        print(f"Should skip: {should_skip}")

        if not should_skip:
            try:
                result = scanner.scan_file(file_path)
                print(f"scan_file result: {result}")

                if result:
                    print("✅ Found MCP tool, scanning env vars...")
                    scanner.scan_env_vars(folder_path)
                    print(f"Env vars: {scanner.env_vars}")

                    # Check for additional files
                    requirements_path = folder_path / "requirements.txt"
                    env_example = folder_path / ".env.example"

                    print(f"Requirements exists: {requirements_path.exists()}")
                    print(f"Env example exists: {env_example.exists()}")

                    # Add all the info
                    result["env_vars"] = list(scanner.env_vars)
                    result["folder_path"] = folder_path

                    if requirements_path.exists():
                        result["requirements_path"] = requirements_path

                    if env_example.exists():
                        result["env_example_path"] = env_example
                        result["env_vars_from_example"] = scanner.parse_env_example(env_example)

                    print(f"Final result: {result}")
                    return result
                else:
                    print("❌ No MCP tool found")

            except Exception as e:
                print(f"💥 Error: {e}")

    print("❌ No tool found in any file")
    return None


if __name__ == "__main__":
    debug_scan_folder()