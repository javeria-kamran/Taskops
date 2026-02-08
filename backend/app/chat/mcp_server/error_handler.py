"""
T018: Tool Error Handling

Converts tool exceptions to MCP JSON error responses.
All tool errors follow standard format:
{
    "error": "ErrorType",
    "details": "Human-readable message"
}

Error types:
- TaskNotFound: Task with given ID not found
- ValidationError: Input validation failed
- DatabaseError: Database operation failed
- NotAuthorizedError: User doesn't own resource
- InternalError: Unexpected error (logging included)
"""

import logging
from typing import Any

logger = logging.getLogger(__name__)


class MCPError(Exception):
    """Base class for MCP errors"""

    def __init__(self, error_type: str, message: str):
        self.error_type = error_type
        self.message = message
        super().__init__(message)


class TaskNotFoundError(MCPError):
    """Task with given ID not found"""

    def __init__(self, task_id: str):
        super().__init__("TaskNotFound", f"Task not found: {task_id}")


class ValidationErrorMCP(MCPError):
    """Input validation failed"""

    def __init__(self, message: str):
        super().__init__("ValidationError", message)


class DatabaseErrorMCP(MCPError):
    """Database operation failed"""

    def __init__(self, message: str):
        super().__init__("DatabaseError", message)


class NotAuthorizedError(MCPError):
    """User doesn't own resource"""

    def __init__(self, resource: str = "resource"):
        super().__init__("NotAuthorized", f"Access denied to {resource}")


def handle_tool_error(exception: Exception, tool_name: str) -> dict[str, Any]:
    """
    Convert exception to MCP JSON error response.

    Args:
        exception: Exception raised during tool execution
        tool_name: Name of tool that failed

    Returns:
        {error: "...", details: "..."}
    """
    error_details = {
        "error": "InternalError",
        "details": "An unexpected error occurred"
    }

    try:
        # Handle our custom MCP errors
        if isinstance(exception, MCPError):
            error_details = {
                "error": exception.error_type,
                "details": exception.message
            }

        # Handle validators.py ValidationError
        elif hasattr(exception, "error_code") and exception.error_code == "VALIDATION_ERROR":
            error_details = {
                "error": "ValidationError",
                "details": str(exception)
            }

        # Handle KeyError (unknown tool)
        elif isinstance(exception, KeyError):
            tool_name = str(exception).strip("'\"")
            error_details = {
                "error": "ToolNotFound",
                "details": f"Unknown tool: {tool_name}"
            }

        # Handle ValueError (e.g., UUID format)
        elif isinstance(exception, ValueError):
            error_details = {
                "error": "ValidationError",
                "details": f"Invalid input: {str(exception)}"
            }

        # Unexpected errors - log for debugging
        else:
            logger.error(
                f"Unexpected error in tool '{tool_name}': {type(exception).__name__}: {exception}",
                exc_info=True
            )
            error_details = {
                "error": "InternalError",
                "details": f"Tool execution failed: {str(exception)}"
            }

    except Exception as e:
        # Safety net - if error handling itself fails
        logger.error(f"Error in error handler: {e}", exc_info=True)
        error_details = {
            "error": "InternalError",
            "details": "Error handler failure"
        }

    return error_details


def format_tool_result(result: Any) -> dict[str, Any]:
    """
    Format successful tool result.

    Args:
        result: Tool result (dict)

    Returns:
        {result: {...}}
    """
    return {"result": result}


def format_tool_error(error_type: str, message: str) -> dict[str, Any]:
    """
    Format error response.

    Args:
        error_type: Error category
        message: Error message

    Returns:
        {error: "...", details: "..."}
    """
    return {
        "error": error_type,
        "details": message
    }
