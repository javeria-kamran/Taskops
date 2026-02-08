"""
Agent Module (Phase III)

[FROM TASKS]: T020-T023 - Agent Layer Configuration
[FROM SPEC]: speckit.specify §FR4

Agent configuration and orchestration for AI-powered task management.
OpenAI Agents SDK integration with MCP tools and error handling.

Structure:
- factory.py: Agent initialization with tools and system prompt
- prompts.py: System prompt engineering templates
- tool_processor.py: MCP tool output formatting and chaining
- error_handler.py: Error handling with fallback responses
"""

from app.chat.agent.factory import (
    AgentFactory,
    initialize_agent_factory,
    get_agent_factory,
    create_configured_agent
)
from app.chat.agent.prompts import (
    get_system_prompt,
    get_system_prompt_with_context
)
from app.chat.agent.tool_processor import (
    ToolProcessor,
    ToolExecutionResult,
    initialize_tool_processor,
    get_tool_processor
)
from app.chat.agent.error_handler import (
    AgentError,
    AgentErrorType,
    AgentErrorHandler,
    handle_agent_error
)

__all__ = [
    # Factory
    "AgentFactory",
    "initialize_agent_factory",
    "get_agent_factory",
    "create_configured_agent",
    # Prompts
    "get_system_prompt",
    "get_system_prompt_with_context",
    # Tool Processor
    "ToolProcessor",
    "ToolExecutionResult",
    "initialize_tool_processor",
    "get_tool_processor",
    # Error Handling
    "AgentError",
    "AgentErrorType",
    "AgentErrorHandler",
    "handle_agent_error"
]
