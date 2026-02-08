"""
T023: Agent Error Handler

Handles agent failures with appropriate fallback responses.

Error scenarios:
- Timeouts: Agent took too long
- Rate limits: OpenAI API rate limited
- Parsing errors: Invalid response from agent
- Tool not found: Referenced tool doesn't exist
- Invalid tool input: Tool validation failed
- Database errors: Persistence failed
- Unknown errors: Unexpected failure

Each error type has a fallback response for the user.
"""

import logging
from typing import Optional, Any
from enum import Enum

logger = logging.getLogger(__name__)


class AgentErrorType(Enum):
    """Types of agent errors"""
    TIMEOUT = "timeout"
    RATE_LIMIT = "rate_limit"
    PARSING_ERROR = "parsing_error"
    TOOL_NOT_FOUND = "tool_not_found"
    VALIDATION_ERROR = "validation_error"
    DATABASE_ERROR = "database_error"
    PERMISSION_ERROR = "permission_error"
    UNKNOWN = "unknown"


class AgentError(Exception):
    """Base class for agent errors"""

    def __init__(
        self,
        error_type: AgentErrorType,
        message: str,
        details: Optional[str] = None,
        original_exception: Optional[Exception] = None
    ):
        self.error_type = error_type
        self.message = message
        self.details = details
        self.original_exception = original_exception
        super().__init__(message)


class AgentErrorHandler:
    """Handles agent errors and provides user-friendly responses."""

    # Timeout constant
    DEFAULT_TIMEOUT_SECONDS = 4.0

    @staticmethod
    def handle_timeout(timeout_seconds: float) -> dict[str, Any]:
        """
        Handle agent timeout.

        Response: Apologize, suggest alternatives, offer manual input.
        """
        logger.warning(f"Agent timeout after {timeout_seconds}s")
        return {
            "success": False,
            "error_type": "timeout",
            "response": (
                "I'm taking a bit longer than usual to process your request. "
                "Could you try again, or would you like to:"
                "\n1. Ask for a list of your tasks"
                "\n2. Tell me the task number you want to manage"
                "\n3. Try a simpler request"
            ),
            "fallback": True
        }

    @staticmethod
    def handle_rate_limit() -> dict[str, Any]:
        """
        Handle API rate limiting.

        Response: Apologize, ask user to wait, offer alternatives.
        """
        logger.warning("OpenAI API rate limit reached")
        return {
            "success": False,
            "error_type": "rate_limit",
            "response": (
                "I've hit a temporary limit on my API usage. "
                "I'll be back to normal in a moment. "
                "Please try your request again in 10-30 seconds."
            ),
            "fallback": True
        }

    @staticmethod
    def handle_parsing_error(raw_response: Optional[str] = None) -> dict[str, Any]:
        """
        Handle agent response parsing failure.

        Response: Acknowledge issue, ask for clarification.
        """
        logger.error(f"Failed to parse agent response: {raw_response}")
        return {
            "success": False,
            "error_type": "parsing_error",
            "response": (
                "I had trouble understanding my own response. "
                "Could you rephrase your request? "
                "For example: 'add task', 'show my tasks', or 'mark task complete'"
            ),
            "fallback": True
        }

    @staticmethod
    def handle_tool_not_found(tool_name: str) -> dict[str, Any]:
        """
        Handle unknown tool reference.

        Response: Explain available tools.
        """
        logger.error(f"Tool not found: {tool_name}")
        return {
            "success": False,
            "error_type": "tool_not_found",
            "response": (
                "I tried to use an unavailable tool. "
                "Here's what I can do:"
                "\n• Add new tasks"
                "\n• Show your tasks"
                "\n• Mark tasks as complete"
                "\n• Delete tasks"
                "\n• Update task details"
                "\n\nWhat would you like to do?"
            ),
            "fallback": True
        }

    @staticmethod
    def handle_validation_error(validation_message: str) -> dict[str, Any]:
        """
        Handle tool input validation failure.

        Response: Explain what went wrong, ask for correction.
        """
        logger.warning(f"Validation error: {validation_message}")
        return {
            "success": False,
            "error_type": "validation_error",
            "response": (
                f"I couldn't validate your request: {validation_message}\n\n"
                "Please check:\n"
                "• Task titles must be under 200 characters\n"
                "• Descriptions must be under 1024 characters\n"
                "• Dates should be in standard format\n\n"
                "Can you rephrase that?"
            ),
            "fallback": True
        }

    @staticmethod
    def handle_database_error(operation: str = "operation") -> dict[str, Any]:
        """
        Handle database/persistence failures.

        Response: Apologize, suggest alternatives, log for investigation.
        """
        logger.error(f"Database error during {operation}")
        return {
            "success": False,
            "error_type": "database_error",
            "response": (
                f"I had trouble saving your {operation}. "
                "This might be temporary. Please try again in a moment. "
                "If the problem persists, please contact support."
            ),
            "fallback": True
        }

    @staticmethod
    def handle_permission_error(resource: str = "resource") -> dict[str, Any]:
        """
        Handle permission/authorization errors.

        Response: Explain access denied, don't leak details.
        """
        logger.warning(f"Permission denied for {resource}")
        return {
            "success": False,
            "error_type": "permission_error",
            "response": (
                f"I don't have permission to access that {resource}. "
                "Please make sure you're using the correct task ID or contact support."
            ),
            "fallback": True
        }

    @staticmethod
    def handle_unknown_error(
        exception: Optional[Exception] = None,
        context: Optional[str] = None
    ) -> dict[str, Any]:
        """
        Handle unexpected/unknown errors.

        Response: Generic apology, suggest basic actions, log details.
        """
        error_msg = str(exception) if exception else "Unknown error"
        logger.error(
            f"Unexpected agent error: {error_msg}",
            extra={"context": context, "exception": exception},
            exc_info=exception
        )
        return {
            "success": False,
            "error_type": "unknown",
            "response": (
                "I encountered an unexpected issue. "
                "I've logged this for investigation. "
                "Please try your request again, or contact support if it continues."
            ),
            "fallback": True
        }


async def handle_agent_error(
    error: Exception,
    timeout_seconds: float = AgentErrorHandler.DEFAULT_TIMEOUT_SECONDS,
    context: Optional[str] = None
) -> dict[str, Any]:
    """
    Handle an agent error and return user-friendly response.

    Args:
        error: Exception raised by agent
        timeout_seconds: Timeout threshold (for comparison)
        context: Optional context about what was being done

    Returns:
        {
            "success": False,
            "error_type": str,
            "response": str,
            "fallback": True
        }
    """
    # Import here to avoid circular imports
    from openai import Timeout, RateLimitError

    if isinstance(error, Timeout):
        return AgentErrorHandler.handle_timeout(timeout_seconds)
    elif isinstance(error, RateLimitError):
        return AgentErrorHandler.handle_rate_limit()
    elif isinstance(error, ValueError):
        # Likely parsing error
        return AgentErrorHandler.handle_parsing_error(str(error))
    elif isinstance(error, KeyError):
        # Tool not found
        return AgentErrorHandler.handle_tool_not_found(str(error))
    elif hasattr(error, "error_code") and error.error_code == "VALIDATION_ERROR":
        return AgentErrorHandler.handle_validation_error(str(error))
    elif "database" in str(error).lower() or "sql" in str(error).lower():
        return AgentErrorHandler.handle_database_error(context or "operation")
    elif hasattr(error, "status_code") and error.status_code == 403:
        return AgentErrorHandler.handle_permission_error()
    else:
        return AgentErrorHandler.handle_unknown_error(error, context)


# Fallback responses for common user intents if agent completely fails

FALLBACK_RESPONSES = {
    "list_tasks": {
        "success": False,
        "response": (
            "I'm having trouble fetching your tasks right now. "
            "Please try again shortly. "
            "I can help you add, complete, delete, or update tasks when the service is available."
        )
    },
    "add_task": {
        "success": False,
        "response": (
            "I'm having trouble creating tasks right now. "
            "Please try again shortly."
        )
    },
    "complete_task": {
        "success": False,
        "response": (
            "I'm having trouble updating tasks right now. "
            "Please try again shortly."
        )
    },
    "help": {
        "success": True,
        "response": (
            "I can help you manage your tasks! Here's what you can ask me to do:\n"
            "• 'Add a task to...' - Create a new task\n"
            "• 'Show my tasks' - List all your tasks\n"
            "• 'Mark task complete' - Mark a task as done\n"
            "• 'Delete task' - Remove a task\n"
            "• 'Update task' - Change task details\n\n"
            "What would you like to do?"
        )
    }
}
