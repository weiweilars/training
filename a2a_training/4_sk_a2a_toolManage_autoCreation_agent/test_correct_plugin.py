#!/usr/bin/env python3
"""Test SK with correct MCPStreamableHttpPlugin"""

import asyncio
import logging
from semantic_kernel import Kernel
from semantic_kernel.connectors.mcp import MCPStreamableHttpPlugin
from semantic_kernel.agents import ChatCompletionAgent
from semantic_kernel.connectors.ai.open_ai import OpenAIChatCompletion
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Configure logging
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

async def test_correct_plugin():
    """Test MCPStreamableHttpPlugin with calculator MCP server"""
    try:
        # Initialize kernel
        kernel = Kernel()
        
        # Add OpenAI service
        if os.getenv("OPENAI_API_KEY"):
            chat_service = OpenAIChatCompletion(
                ai_model_id="gpt-3.5-turbo",
                api_key=os.getenv("OPENAI_API_KEY")
            )
            kernel.add_service(chat_service)
        
        logger.info("Testing MCPStreamableHttpPlugin...")
        
        # Try the CORRECT plugin type
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
        
        # Create agent
        agent = ChatCompletionAgent(
            kernel=kernel,
            name="test_agent",
            description="Test agent with MCP tools"
        )
        
        logger.info("✅ Agent created successfully!")
        
        # Test tool calling
        from semantic_kernel.contents.chat_history import ChatHistory
        from semantic_kernel.contents.chat_message_content import ChatMessageContent
        from semantic_kernel.contents.utils.author_role import AuthorRole
        
        chat_history = ChatHistory()
        user_message = ChatMessageContent(
            role=AuthorRole.USER,
            content="Calculate 789 * 123"
        )
        chat_history.add_message(user_message)
        
        logger.info("Testing tool invocation...")
        response = await agent.get_response(
            messages=chat_history,
            user_id="test_user",
            session_id="test_session"
        )
        
        logger.info(f"Response: {response}")
        
        # Close plugin
        await plugin.close()
        
    except Exception as e:
        logger.error(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(test_correct_plugin())