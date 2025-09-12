#!/usr/bin/env python3
"""Test direct MCP tool calling without agent"""

import asyncio
import logging
from semantic_kernel import Kernel
from semantic_kernel.connectors.mcp import MCPStreamableHttpPlugin
from semantic_kernel.functions import KernelArguments

# Configure logging
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

async def test_direct_tool_call():
    """Test calling MCP tools directly through the plugin"""
    try:
        # Initialize kernel
        kernel = Kernel()
        
        logger.info("Testing MCPStreamableHttpPlugin direct tool calling...")
        
        # Create and connect plugin
        plugin = MCPStreamableHttpPlugin(
            name="calculator_plugin",
            url="http://localhost:8002/mcp",
            description="Calculator MCP tools"
        )
        
        logger.info("Connecting to MCP server...")
        await plugin.connect()
        logger.info("✅ Connected successfully!")
        
        # Add plugin to kernel
        kernel.add_plugin(plugin)
        logger.info("✅ Plugin added to kernel!")
        
        # List available functions
        logger.info("Available functions in kernel:")
        for plugin_name, plugin_obj in kernel.plugins.items():
            logger.info(f"  Plugin: {plugin_name}")
            for func_name, func in plugin_obj.functions.items():
                logger.info(f"    - {func_name}: {func.description}")
        
        # Try to call a tool directly
        logger.info("\nTesting direct tool call: basic_math")
        
        # Create arguments for the tool
        arguments = KernelArguments(
            operation="*",
            a=789,
            b=123
        )
        
        # Try to invoke the function
        result = await kernel.invoke(
            plugin_name="calculator_plugin",
            function_name="basic_math",
            arguments=arguments
        )
        
        logger.info(f"✅ Tool call successful! Result: {result}")
        
        # Close plugin
        await plugin.close()
        
    except Exception as e:
        logger.error(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(test_direct_tool_call())