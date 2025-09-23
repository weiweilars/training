"""
MCP Tool Scanner - Detects FastMCP instances and environment variables in Python files
"""

import ast
import importlib.util
import sys
import os
import re
from pathlib import Path
from typing import Dict, List, Optional, Any, Set
import subprocess


class MCPToolScanner:
    """Scans folders for FastMCP tool instances and their environment dependencies"""

    def __init__(self, logger=None):
        self.logger = logger
        self.mcp_info = None
        self.env_vars = set()

    def scan_folder(self, folder_path: Path) -> Optional[Dict[str, Any]]:
        """Scan folder for MCP tool and its dependencies"""
        if not folder_path.exists():
            raise ValueError(f"Folder does not exist: {folder_path}")

        if not folder_path.is_dir():
            # If it's a file, scan just that file
            if folder_path.suffix == '.py':
                return self.scan_single_file(folder_path)
            raise ValueError(f"Path is not a directory or Python file: {folder_path}")

        # Scan all Python files
        python_files = list(folder_path.glob("**/*.py"))

        if self.logger:
            self.logger.info(f"Scanning {len(python_files)} Python files in {folder_path}")

        for file_path in python_files:
            # Skip __pycache__, test files, and setup files
            skip_patterns = ["__pycache__", "setup.py", "__init__.py"]
            # More specific test file patterns
            if (any(pattern in str(file_path) for pattern in skip_patterns) or
                file_path.name.startswith("test_") or
                "/test/" in str(file_path) or
                "/tests/" in str(file_path)):
                continue

            try:
                result = self.scan_file(file_path)
                if result:
                    # Found MCP instance, now scan for env vars
                    self.scan_env_vars(folder_path)

                    # Check for requirements.txt
                    requirements_path = folder_path / "requirements.txt"
                    if requirements_path.exists():
                        result["requirements_path"] = requirements_path

                    # Check for .env.example
                    env_example = folder_path / ".env.example"
                    if env_example.exists():
                        result["env_example_path"] = env_example
                        result["env_vars_from_example"] = self.parse_env_example(env_example)

                    result["env_vars"] = list(self.env_vars)
                    result["folder_path"] = folder_path

                    if self.logger:
                        self.logger.info(f"Found MCP tool: {result['instance_name']} in {file_path}")
                        if self.env_vars:
                            self.logger.info(f"Required environment variables: {', '.join(self.env_vars)}")

                    return result

            except Exception as e:
                if self.logger:
                    self.logger.debug(f"Error scanning {file_path}: {e}")

        return None

    def scan_single_file(self, file_path: Path) -> Optional[Dict[str, Any]]:
        """Scan a single Python file"""
        result = self.scan_file(file_path)
        if result:
            # Scan the file and its directory for env vars
            self.scan_env_vars(file_path.parent)
            result["env_vars"] = list(self.env_vars)
            result["folder_path"] = file_path.parent
        return result

    def scan_file(self, file_path: Path) -> Optional[Dict[str, Any]]:
        """Scan a single Python file for FastMCP instances"""
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()

        # Quick check if file might contain FastMCP
        if not any(pattern in content for pattern in ["FastMCP", "fastmcp"]):
            return None

        try:
            tree = ast.parse(content)
            analyzer = FastMCPAnalyzer()
            analyzer.visit(tree)

            if analyzer.mcp_instances:
                # Get the first (or most likely main) instance
                instance_name = list(analyzer.mcp_instances.keys())[0]
                instance_info = analyzer.mcp_instances[instance_name]

                return {
                    "file_path": file_path,
                    "module_name": file_path.stem,
                    "instance_name": instance_name,
                    "instance_info": instance_info,
                    "relative_path": file_path.name
                }
        except SyntaxError as e:
            if self.logger:
                self.logger.debug(f"Syntax error parsing {file_path}: {e}")

        return None

    def scan_env_vars(self, folder_path: Path) -> Set[str]:
        """Scan folder for environment variable usage"""
        env_patterns = [
            r'os\.getenv\(["\']([A-Z_][A-Z0-9_]*)["\']',  # os.getenv("VAR")
            r'os\.environ\.get\(["\']([A-Z_][A-Z0-9_]*)["\']',  # os.environ.get("VAR")
            r'os\.environ\[["\']([A-Z_][A-Z0-9_]*)["\']',  # os.environ["VAR"]
            r'getenv\(["\']([A-Z_][A-Z0-9_]*)["\']',  # getenv("VAR")
            r'environ\[["\']([A-Z_][A-Z0-9_]*)["\']',  # environ["VAR"]
        ]

        python_files = list(folder_path.glob("**/*.py"))

        for file_path in python_files:
            if "__pycache__" in str(file_path):
                continue

            try:
                with open(file_path, 'r', encoding='utf-8') as f:
                    content = f.read()

                for pattern in env_patterns:
                    matches = re.findall(pattern, content)
                    self.env_vars.update(matches)

            except Exception as e:
                if self.logger:
                    self.logger.debug(f"Error scanning {file_path} for env vars: {e}")

        # Filter out common Python/system env vars
        system_vars = {'PATH', 'HOME', 'USER', 'PYTHONPATH', 'PWD', 'LANG', 'LC_ALL', 'SHELL'}
        self.env_vars = self.env_vars - system_vars

        return self.env_vars

    def parse_env_example(self, env_file: Path) -> Dict[str, str]:
        """Parse .env.example file for environment variables"""
        env_vars = {}

        try:
            with open(env_file, 'r', encoding='utf-8') as f:
                for line in f:
                    line = line.strip()
                    # Skip comments and empty lines
                    if line.startswith('#') or not line:
                        continue

                    # Parse KEY=value format
                    if '=' in line:
                        key, value = line.split('=', 1)
                        key = key.strip()
                        value = value.strip().strip('"').strip("'")
                        env_vars[key] = value

        except Exception as e:
            if self.logger:
                self.logger.debug(f"Error parsing env example: {e}")

        return env_vars

    def load_tool(self, tool_info: Dict[str, Any]) -> Any:
        """Load a specific MCP tool from file"""
        file_path = tool_info["file_path"]
        instance_name = tool_info["instance_name"]

        # Add folder to Python path for imports
        folder_path = tool_info.get("folder_path", file_path.parent)
        if str(folder_path) not in sys.path:
            sys.path.insert(0, str(folder_path))

        # Load the module
        spec = importlib.util.spec_from_file_location(
            tool_info["module_name"],
            file_path
        )

        if spec is None or spec.loader is None:
            raise ImportError(f"Could not load module from {file_path}")

        module = importlib.util.module_from_spec(spec)
        sys.modules[spec.name] = module

        try:
            # Execute the module
            spec.loader.exec_module(module)
        except Exception as e:
            if self.logger:
                self.logger.error(f"Error executing module: {e}")
            # Try to provide helpful error message about missing env vars
            if "getenv" in str(e) or "environ" in str(e):
                raise EnvironmentError(
                    f"Module failed to load, likely missing environment variables. "
                    f"Required vars: {', '.join(tool_info.get('env_vars', []))}"
                )
            raise

        # Get the MCP instance
        if hasattr(module, instance_name):
            return getattr(module, instance_name)

        # Try common names if specific instance not found
        for common_name in ['mcp', 'app', 'server', 'tool', 'agent']:
            if hasattr(module, common_name):
                instance = getattr(module, common_name)
                # Check if it's a FastMCP instance
                if hasattr(instance, '__class__') and 'FastMCP' in str(instance.__class__):
                    return instance

        raise AttributeError(f"Could not find MCP instance '{instance_name}' in {file_path}")

    def validate_environment(self, required_vars: List[str]) -> Dict[str, str]:
        """Validate that required environment variables are set"""
        missing_vars = []
        env_values = {}

        for var in required_vars:
            value = os.getenv(var)
            if value is None:
                missing_vars.append(var)
            else:
                env_values[var] = value

        if missing_vars:
            if self.logger:
                self.logger.warning(f"Missing environment variables: {', '.join(missing_vars)}")

        return {
            "missing": missing_vars,
            "present": env_values
        }


class FastMCPAnalyzer(ast.NodeVisitor):
    """AST analyzer to find FastMCP instances in Python code"""

    def __init__(self):
        self.mcp_instances = {}
        self.imports = {}
        self.current_class = None

    def visit_Import(self, node):
        """Track imports"""
        for alias in node.names:
            if 'fastmcp' in alias.name.lower():
                self.imports[alias.asname or alias.name] = alias.name
        self.generic_visit(node)

    def visit_ImportFrom(self, node):
        """Track from imports"""
        if node.module and 'fastmcp' in node.module.lower():
            for alias in node.names:
                self.imports[alias.asname or alias.name] = f"{node.module}.{alias.name}"
        self.generic_visit(node)

    def visit_Assign(self, node):
        """Find variable assignments of FastMCP instances"""
        # Check if this is a FastMCP instantiation
        if isinstance(node.value, ast.Call):
            if self._is_fastmcp_call(node.value):
                # Get the variable name(s)
                for target in node.targets:
                    if isinstance(target, ast.Name):
                        instance_info = self._extract_instance_info(node.value)
                        self.mcp_instances[target.id] = instance_info

        self.generic_visit(node)

    def visit_ClassDef(self, node):
        """Track class definitions"""
        old_class = self.current_class
        self.current_class = node.name
        self.generic_visit(node)
        self.current_class = old_class

    def _is_fastmcp_call(self, call_node):
        """Check if a call node is creating a FastMCP instance"""
        if isinstance(call_node.func, ast.Name):
            # Direct call like FastMCP()
            return call_node.func.id in self.imports or 'FastMCP' in call_node.func.id
        elif isinstance(call_node.func, ast.Attribute):
            # Call like fastmcp.FastMCP()
            if isinstance(call_node.func.value, ast.Name):
                module_name = call_node.func.value.id
                return module_name in self.imports and 'FastMCP' in call_node.func.attr
        return False

    def _extract_instance_info(self, call_node):
        """Extract information from FastMCP instantiation"""
        info = {
            "type": "FastMCP",
            "args": {},
            "class_context": self.current_class
        }

        # Extract keyword arguments
        for keyword in call_node.keywords:
            if keyword.arg:
                info["args"][keyword.arg] = self._get_value(keyword.value)

        # Extract positional arguments (first is usually name)
        if call_node.args and len(call_node.args) > 0:
            info["args"]["name"] = self._get_value(call_node.args[0])

        return info

    def _get_value(self, node):
        """Extract value from AST node"""
        if isinstance(node, ast.Constant):
            return node.value
        elif isinstance(node, ast.Str):
            return node.s
        elif isinstance(node, ast.Name):
            return f"<variable:{node.id}>"
        else:
            return f"<{node.__class__.__name__}>"