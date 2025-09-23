#!/usr/bin/env python3
"""
Main entry point for MCP Deployment Server
"""

import sys
import os
import argparse
import asyncio
from pathlib import Path
import uvicorn

from app import create_app, MCPDeploymentWrapper
from config.settings import load_settings
from utils.logger import setup_logger
from utils.scanner import MCPToolScanner


def main():
    """Main entry point"""
    parser = argparse.ArgumentParser(
        description="Production-ready MCP Deployment Server",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Scan folder for MCP tool
  python main.py /path/to/mcp/folder

  # Run specific Python file
  python main.py tool.py

  # Run with custom port
  python main.py /path/to/folder --port 8080

  # Run with authentication enabled
  AUTH_ENABLED=true AUTH_TYPE=bearer VALID_BEARER_TOKENS=secret123 python main.py folder/

  # Set required environment variables for the tool
  API_KEY=xxx OPENAI_API_KEY=yyy python main.py mcp_tool_folder/

  # Run with monitoring and detailed logging
  MONITORING_DETAILED_LOGGING=true python main.py folder/ --log-level debug

  # Run in production mode with multiple workers
  ENVIRONMENT=production python main.py folder/ --workers 4
        """
    )

    parser.add_argument(
        "path",
        help="Path to MCP tool folder or Python file"
    )

    parser.add_argument(
        "--port", "-p",
        type=int,
        help="Port to run the HTTP server on (overrides PORT env var)"
    )

    parser.add_argument(
        "--host",
        help="Host to bind the server to (overrides HOST env var)"
    )

    parser.add_argument(
        "--workers", "-w",
        type=int,
        help="Number of worker processes (overrides WORKERS env var)"
    )

    parser.add_argument(
        "--log-level",
        choices=["debug", "info", "warning", "error"],
        help="Logging level (overrides LOG_LEVEL env var)"
    )

    parser.add_argument(
        "--reload",
        action="store_true",
        help="Enable auto-reload for development"
    )

    args = parser.parse_args()

    # Load settings
    settings = load_settings()

    # Override settings with command line arguments
    if args.port:
        settings.PORT = args.port
    if args.host:
        settings.HOST = args.host
    if args.workers:
        settings.WORKERS = args.workers
    if args.log_level:
        settings.LOG_LEVEL = args.log_level

    # Setup logging
    logger = setup_logger(
        "mcp_deployment",
        level=settings.LOG_LEVEL,
        format_type=settings.LOG_FORMAT,
        log_file=settings.LOG_FILE
    )

    # Resolve path
    input_path = Path(args.path)
    if not input_path.exists():
        # Try relative to current directory
        input_path = Path.cwd() / args.path
        if not input_path.exists():
            logger.error(f"Path not found: {args.path}")
            return 1

    try:
        # Scan for MCP tool
        scanner = MCPToolScanner(logger)
        logger.info(f"Scanning for MCP tool in: {input_path}")

        tool_info = scanner.scan_folder(input_path)

        if not tool_info:
            logger.error(f"No FastMCP instance found in {input_path}")
            logger.info("Make sure your folder contains a Python file with a FastMCP instance")
            return 1

        # Display found tool information
        logger.info(f"Found MCP tool: {tool_info['instance_name']} in {tool_info['file_path']}")

        # Check for environment variables
        if tool_info.get('env_vars'):
            logger.info(f"Required environment variables: {', '.join(tool_info['env_vars'])}")

            # Validate environment
            validation = scanner.validate_environment(tool_info['env_vars'])
            if validation['missing']:
                logger.warning(f"Missing environment variables: {', '.join(validation['missing'])}")
                logger.warning("Set these variables before running or the tool may not work properly")

                # Check if there's an .env.example
                if tool_info.get('env_example_path'):
                    logger.info(f"Check {tool_info['env_example_path']} for example values")

        # Load the MCP tool
        logger.info(f"Loading MCP tool from: {tool_info['file_path']}")

        # Create a module wrapper that matches the old structure
        class MCPModule:
            def __init__(self, mcp_instance):
                self.mcp = mcp_instance

        mcp_instance = scanner.load_tool(tool_info)
        mcp_module = MCPModule(mcp_instance)

        # Create wrapper
        mcp_wrapper = MCPDeploymentWrapper(mcp_module, settings)

        # Create Starlette app
        app = create_app(mcp_wrapper, settings)

        logger.info(f"Starting MCP Deployment Server")
        logger.info(f"Tool: {mcp_wrapper.mcp.name}")
        logger.info(f"Environment: {settings.ENVIRONMENT}")
        logger.info(f"Server URL: http://{settings.HOST}:{settings.PORT}")
        logger.info(f"Auth Enabled: {settings.AUTH_ENABLED}")
        logger.info(f"Streaming Enabled: {settings.MCP_STREAMING_ENABLED}")

        if settings.AUTH_ENABLED:
            logger.info(f"Auth Type: {settings.AUTH_TYPE}")

        if settings.ENVIRONMENT == "development" or args.reload:
            logger.warning("Running in development mode with auto-reload")
            # Set environment variable for module-level app creation
            os.environ["MCP_TOOL_PATH"] = str(input_path)
            # Run with reload for development
            uvicorn.run(
                "main:app",
                host=settings.HOST,
                port=settings.PORT,
                reload=True,
                log_level=settings.LOG_LEVEL.lower()
            )
        else:
            # Run production server
            if settings.WORKERS > 1:
                logger.info(f"Running with {settings.WORKERS} workers")
                uvicorn.run(
                    app,
                    host=settings.HOST,
                    port=settings.PORT,
                    workers=settings.WORKERS,
                    log_level=settings.LOG_LEVEL.lower(),
                    access_log=settings.MONITORING_ENABLED
                )
            else:
                uvicorn.run(
                    app,
                    host=settings.HOST,
                    port=settings.PORT,
                    log_level=settings.LOG_LEVEL.lower(),
                    access_log=settings.MONITORING_ENABLED
                )

    except ImportError as e:
        logger.error(f"Error importing tool module: {e}")
        logger.error("Make sure the tool file has a valid 'mcp' attribute")
        return 1
    except Exception as e:
        logger.error(f"Error running server: {e}", exc_info=True)
        return 1

    return 0


# For development reload support
app = None
if __name__ != "__main__":
    # This is for uvicorn reload mode
    import os
    tool_path_str = os.getenv("MCP_TOOL_PATH", "")
    if tool_path_str:
        settings = load_settings()
        tool_path = Path(tool_path_str)
        if tool_path.exists():
            scanner = MCPToolScanner()
            tool_info = scanner.scan_folder(tool_path)
            if tool_info:
                class MCPModule:
                    def __init__(self, mcp_instance):
                        self.mcp = mcp_instance

                mcp_instance = scanner.load_tool(tool_info)
                mcp_module = MCPModule(mcp_instance)
                mcp_wrapper = MCPDeploymentWrapper(mcp_module, settings)
                app = create_app(mcp_wrapper, settings)


if __name__ == "__main__":
    exit_code = main()
    if exit_code:
        sys.exit(exit_code)