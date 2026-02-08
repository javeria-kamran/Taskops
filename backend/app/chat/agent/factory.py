"""
T020: Agent Factory

Initializes OpenAI Agent with:
1. OpenAI model configuration
2. Tool registration from MCP server
3. System prompt template (T021)

Creates agent instance ready for tool calling and task management.
"""

import logging
from typing import Optional, Any
from openai import AsyncOpenAI

from app.chat.config import ChatConfig
from app.chat.mcp_server.tools import get_tool_definitions
from app.chat.agent.prompts import get_system_prompt, get_system_prompt_with_context

logger = logging.getLogger(__name__)


class AgentFactory:
    """Factory for creating configured OpenAI Agents."""

    def __init__(self, settings: ChatConfig):
        """
        Initialize agent factory with configuration.

        Args:
            settings: ChatSettings instance with OpenAI API key and model
        """
        self.settings = settings
        self.client = AsyncOpenAI(api_key=settings.openai_api_key)
        self.model = settings.openai_model
        self.tools = get_tool_definitions()
        self.tool_list = list(self.tools.keys())

    def create_agent(
        self,
        user_context: Optional[dict[str, Any]] = None,
        system_prompt_override: Optional[str] = None
    ) -> dict[str, Any]:
        """
        Create a configured agent.

        This returns the agent configuration (not an agent instance).
        The actual agent execution happens via OpenAI API calls.

        Args:
            user_context: Optional dict with user-specific context
                - user_id: User's unique ID
                - task_count: Total tasks for user
                - recent_tasks: Tasks created in last 24h
            system_prompt_override: Use custom system prompt instead of generated

        Returns:
            {
                "model": str,
                "system_prompt": str,
                "tools": [tool_definitions...],
                "tool_names": [str...]
            }
        """
        # Generate system prompt
        if system_prompt_override:
            system_prompt = system_prompt_override
        else:
            system_prompt = get_system_prompt_with_context(
                self.tool_list,
                user_context or {}
            )

        # Convert tool definitions to OpenAI format
        openai_tools = self._convert_tools_to_openai_format()

        agent_config = {
            "model": self.model,
            "system_prompt": system_prompt,
            "tools": openai_tools,
            "tool_names": self.tool_list,
            "client": self.client,  # Store client for later use
        }

        logger.info(f"Agent created with {len(openai_tools)} tools for model {self.model}")
        return agent_config

    def _convert_tools_to_openai_format(self) -> list[dict[str, Any]]:
        """
        Convert MCP tool definitions to OpenAI function call format.

        OpenAI format:
        {
            "type": "function",
            "function": {
                "name": "tool_name",
                "description": "Tool description",
                "parameters": {
                    "type": "object",
                    "properties": {...},
                    "required": [...]
                }
            }
        }

        Returns:
            List of tool definitions in OpenAI format
        """
        openai_tools = []

        for tool_name, tool_schema in self.tools.items():
            openai_tool = {
                "type": "function",
                "function": {
                    "name": tool_schema["name"],
                    "description": tool_schema["description"],
                    "parameters": tool_schema["inputSchema"]
                }
            }
            openai_tools.append(openai_tool)

        return openai_tools

    async def validate_tools(self) -> bool:
        """
        Validate that all tools are properly registered.

        Checks:
        - Tool definitions exist
        - Each tool has name, description, inputSchema
        - inputSchema is valid JSON Schema

        Returns:
            True if validation passes

        Raises:
            Exception: If validation fails
        """
        if not self.tools:
            raise Exception("No tools registered in agent")

        for tool_name, tool_schema in self.tools.items():
            if not tool_schema.get("name"):
                raise Exception(f"Tool {tool_name} missing name")
            if not tool_schema.get("description"):
                raise Exception(f"Tool {tool_name} missing description")
            if not tool_schema.get("inputSchema"):
                raise Exception(f"Tool {tool_name} missing inputSchema")

        logger.info(f"Tools validation passed: {len(self.tools)} tools ready")
        return True


# Global agent factory instance
_agent_factory: Optional[AgentFactory] = None


def initialize_agent_factory(settings: ChatConfig) -> AgentFactory:
    """
    Initialize the global agent factory.

    Called during application startup.

    Args:
        settings: ChatSettings instance

    Returns:
        Initialized AgentFactory
    """
    global _agent_factory
    _agent_factory = AgentFactory(settings)
    return _agent_factory


def get_agent_factory() -> AgentFactory:
    """
    Get the global agent factory instance.

    Returns:
        AgentFactory instance

    Raises:
        RuntimeError: If factory not initialized
    """
    if not _agent_factory:
        raise RuntimeError("Agent factory not initialized. Call initialize_agent_factory() first.")
    return _agent_factory


async def create_configured_agent(
    user_context: Optional[dict[str, Any]] = None,
    system_prompt_override: Optional[str] = None
) -> dict[str, Any]:
    """
    Create a configured agent using global factory.

    Args:
        user_context: Optional user-specific context
        system_prompt_override: Optional custom system prompt

    Returns:
        Agent configuration dict

    Raises:
        RuntimeError: If factory not initialized
    """
    factory = get_agent_factory()
    await factory.validate_tools()
    return factory.create_agent(user_context, system_prompt_override)
