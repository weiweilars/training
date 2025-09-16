#!/usr/bin/env python3
"""
Custom A2A Agent Client
Replaces MCP client functionality to call other A2A agents instead of MCP tools
"""

import asyncio
import httpx
import json
import uuid
from typing import Dict, Any, List, Optional


class CustomA2AClient:
    """Custom A2A client that calls other A2A agents"""
    
    def __init__(self, agent_url: str):
        self.agent_url = agent_url.rstrip('/')  # Remove trailing slash if any
        self.session_id = str(uuid.uuid4())
        self.initialized = False
        self.agent_card = None
        
    async def _parse_response(self, response) -> Optional[Dict[str, Any]]:
        """Parse HTTP response from A2A agent"""
        if response.status_code != 200:
            print(f"A2A agent returned status {response.status_code}: {response.text}")
            return None
        
        try:
            # A2A agents return JSON responses
            return response.json()
        except Exception as e:
            print(f"Failed to parse A2A response: {e}")
            return None
        
    async def initialize(self) -> Dict[str, Any]:
        """Initialize A2A agent session by fetching agent card"""
        try:
            # Increase timeout for slow agents
            async with httpx.AsyncClient(timeout=httpx.Timeout(30.0)) as client:
                # Fetch agent card to understand capabilities
                card_response = await client.get(f"{self.agent_url}/.well-known/agent-card.json")
                if card_response.status_code == 200:
                    self.agent_card = card_response.json()
                    self.initialized = True
                    return self.agent_card
                else:
                    print(f"Failed to get agent card from {self.agent_url}: {card_response.status_code}")
                    return None
        except Exception as e:
            print(f"Error initializing A2A client for {self.agent_url}: {e}")
            return None
    
    async def get_capabilities(self) -> List[Dict[str, Any]]:
        """Get available capabilities from A2A agent"""
        if not self.initialized:
            await self.initialize()
            
        if not self.agent_card:
            return []
            
        # Extract skills/capabilities from agent card
        return self.agent_card.get("skills", [])
    
    async def send_message(self, message: str, session_id: str = None) -> Dict[str, Any]:
        """Send message to A2A agent"""
        if not session_id:
            session_id = self.session_id

        payload = {
            "jsonrpc": "2.0",
            "method": "message/send",
            "params": {
                "message": {
                    "content": message
                },
                "sessionId": session_id
            },
            "id": str(uuid.uuid4())
        }

        headers = {
            "Content-Type": "application/json"
        }

        try:
            # Increase timeout to 60 seconds for slow A2A agents
            async with httpx.AsyncClient(timeout=httpx.Timeout(60.0)) as client:
                response = await client.post(self.agent_url, json=payload, headers=headers)
                result = await self._parse_response(response)

                # Return the full result instead of unwrapping here
                if result and "error" in result:
                    raise Exception(f"A2A Agent Error: {result['error']}")
                else:
                    return result
        except Exception as e:
            print(f"Error sending message to A2A agent {self.agent_url}: {e}")
            raise


def create_custom_agent_function(a2a_client: CustomA2AClient, capability_info: Dict[str, Any]):
    """Create a callable function from A2A agent capability that SK can use"""
    capability_name = capability_info.get("name", "unknown_capability")
    
    async def agent_function(**kwargs) -> str:
        """Callable agent function for Semantic Kernel"""
        try:
            # Format the request message for the A2A agent
            if kwargs:
                # If we have parameters, create a structured message
                message = f"Please help with {capability_name}. Parameters: {json.dumps(kwargs, indent=2)}"
            else:
                # Simple capability invocation
                message = f"Please help with {capability_name}"

            result = await a2a_client.send_message(message)

            # Extract response content - now result is the full response
            if isinstance(result, dict):
                # Check for result.result.message pattern first
                if "result" in result and isinstance(result["result"], dict):
                    inner_result = result["result"]
                    if "message" in inner_result:
                        message_content = inner_result["message"]
                        if isinstance(message_content, dict) and "content" in message_content:
                            return message_content["content"]
                        elif isinstance(message_content, str):
                            return message_content
                    # Also check if inner_result itself is the message
                    elif "content" in inner_result:
                        return inner_result["content"]
                    # Or if inner_result is a string response
                    elif isinstance(inner_result, str):
                        return inner_result

                # Check for direct message.content pattern
                elif "message" in result and isinstance(result["message"], dict) and "content" in result["message"]:
                    return result["message"]["content"]

                # Check if result itself has content
                elif "content" in result:
                    return result["content"]

            # If result is a string, return it directly
            elif isinstance(result, str):
                return result

            # Fallback to JSON representation
            return json.dumps(result, indent=2)

        except Exception as e:
            return f"Error calling A2A agent {capability_name}: {str(e)}"
    
    # Add metadata to the function for SK
    agent_function.__name__ = capability_name.replace(" ", "_").lower()
    agent_function.__doc__ = capability_info.get("description", f"Call A2A agent capability: {capability_name}")
    
    return agent_function


class CustomA2AAgentset:
    """Custom agent set that replaces MCP toolset for A2A agents"""
    
    def __init__(self, agent_url: str):
        self.agent_url = agent_url
        self.client = CustomA2AClient(agent_url)
        self.capabilities = {}
        self._discovered_capabilities = []
    
    async def discover_capabilities(self) -> List[str]:
        """Discover available capabilities from the A2A agent"""
        try:
            capabilities = await self.client.get_capabilities()
            self._discovered_capabilities = capabilities
            
            capability_names = []
            for capability in capabilities:
                capability_name = capability.get("name", "unknown")
                capability_names.append(capability_name)
                
                # Store capability info for later function creation
                self.capabilities[capability_name] = capability
            
            return capability_names
            
        except Exception as e:
            print(f"Error discovering capabilities from {self.agent_url}: {e}")
            return []
    
    async def get_agent_functions(self) -> List:
        """Get all available agent functions for SK"""
        if not self._discovered_capabilities:
            await self.discover_capabilities()
        
        # Return list of callable functions
        agent_functions = []
        for capability_info in self._discovered_capabilities:
            agent_function = create_custom_agent_function(self.client, capability_info)
            agent_functions.append(agent_function)
        
        return agent_functions
    
    def get_agent_function(self, capability_name: str) -> Optional:
        """Get specific agent function by capability name"""
        capability_info = self.capabilities.get(capability_name)
        if capability_info:
            return create_custom_agent_function(self.client, capability_info)
        return None