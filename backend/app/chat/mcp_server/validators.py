"""
T016: Tool Input Validation

Validates tool inputs against JSON schemas defined in tools.py.
Ensures all inputs match schema constraints before execution.

Constraints:
- user_id: UUID format (validated by auth layer)
- task_id: UUID format
- title: non-empty string, max 200 chars
- description: max 1024 chars
- priority: enum (low, medium, high)
- due_date: ISO 8601 datetime
- status: enum (pending, completed, all)
- limit: 1-100
- offset: non-negative integer
"""

import json
from datetime import datetime
from typing import Any, Optional
from uuid import UUID
import logging

logger = logging.getLogger(__name__)


class ValidationError(Exception):
    """Raised when tool input validation fails"""

    def __init__(self, message: str, error_code: str = "VALIDATION_ERROR"):
        self.message = message
        self.error_code = error_code
        super().__init__(message)


def validate_add_task_input(tool_input: dict[str, Any]) -> dict[str, Any]:
    """
    Validate add_task tool input.

    Required: title
    Optional: description, priority, due_date

    Returns:
        Validated and normalized input
    """
    # Required field
    if "title" not in tool_input:
        raise ValidationError("title is required for add_task")

    title = tool_input.get("title", "").strip()
    if not title:
        raise ValidationError("title cannot be empty")
    if len(title) > 200:
        raise ValidationError("title must be <= 200 characters")

    # Optional description
    description = tool_input.get("description", "").strip() if "description" in tool_input else None
    if description and len(description) > 1024:
        raise ValidationError("description must be <= 1024 characters")

    # Optional priority
    priority = tool_input.get("priority", "medium")
    if priority not in ["low", "medium", "high"]:
        raise ValidationError(f"priority must be low/medium/high, got {priority}")

    # Optional due_date
    due_date = None
    if "due_date" in tool_input:
        try:
            due_date = datetime.fromisoformat(tool_input["due_date"].replace("Z", "+00:00"))
        except (ValueError, AttributeError):
            raise ValidationError(f"due_date must be valid ISO 8601 datetime")

    return {
        "title": title,
        "description": description or None,
        "priority": priority,
        "due_date": due_date
    }


def validate_list_tasks_input(tool_input: dict[str, Any]) -> dict[str, Any]:
    """
    Validate list_tasks tool input.

    Optional: status, limit, offset

    Returns:
        Validated and normalized input
    """
    status = tool_input.get("status", "all")
    if status not in ["pending", "completed", "all"]:
        raise ValidationError(f"status must be pending/completed/all, got {status}")

    limit = tool_input.get("limit", 50)
    try:
        limit = int(limit)
        if limit < 1 or limit > 100:
            raise ValidationError("limit must be 1-100")
    except (ValueError, TypeError):
        raise ValidationError("limit must be integer")

    offset = tool_input.get("offset", 0)
    try:
        offset = int(offset)
        if offset < 0:
            raise ValidationError("offset must be >= 0")
    except (ValueError, TypeError):
        raise ValidationError("offset must be non-negative integer")

    return {
        "status": status,
        "limit": limit,
        "offset": offset
    }


def validate_complete_task_input(tool_input: dict[str, Any]) -> dict[str, Any]:
    """
    Validate complete_task tool input.

    Required: task_id (UUID)

    Returns:
        Validated input
    """
    if "task_id" not in tool_input:
        raise ValidationError("task_id is required for complete_task")

    task_id = tool_input["task_id"]
    try:
        UUID(task_id)  # Validate UUID format
    except (ValueError, AttributeError, TypeError):
        raise ValidationError(f"task_id must be valid UUID, got {task_id}")

    return {"task_id": task_id}


def validate_delete_task_input(tool_input: dict[str, Any]) -> dict[str, Any]:
    """
    Validate delete_task tool input.

    Required: task_id (UUID)

    Returns:
        Validated input
    """
    if "task_id" not in tool_input:
        raise ValidationError("task_id is required for delete_task")

    task_id = tool_input["task_id"]
    try:
        UUID(task_id)  # Validate UUID format
    except (ValueError, AttributeError, TypeError):
        raise ValidationError(f"task_id must be valid UUID, got {task_id}")

    return {"task_id": task_id}


def validate_update_task_input(tool_input: dict[str, Any]) -> dict[str, Any]:
    """
    Validate update_task tool input.

    Required: task_id (UUID)
    Optional: title, description, priority, due_date

    Returns:
        Validated input
    """
    if "task_id" not in tool_input:
        raise ValidationError("task_id is required for update_task")

    task_id = tool_input["task_id"]
    try:
        UUID(task_id)  # Validate UUID format
    except (ValueError, AttributeError, TypeError):
        raise ValidationError(f"task_id must be valid UUID, got {task_id}")

    # Optional fields (same validation as add_task)
    result = {"task_id": task_id}

    if "title" in tool_input:
        title = tool_input.get("title", "").strip()
        if not title:
            raise ValidationError("title cannot be empty")
        if len(title) > 200:
            raise ValidationError("title must be <= 200 characters")
        result["title"] = title

    if "description" in tool_input:
        description = tool_input.get("description", "").strip()
        if description and len(description) > 1024:
            raise ValidationError("description must be <= 1024 characters")
        result["description"] = description or None

    if "priority" in tool_input:
        priority = tool_input["priority"]
        if priority not in ["low", "medium", "high"]:
            raise ValidationError(f"priority must be low/medium/high, got {priority}")
        result["priority"] = priority

    if "due_date" in tool_input:
        try:
            due_date = datetime.fromisoformat(tool_input["due_date"].replace("Z", "+00:00"))
            result["due_date"] = due_date
        except (ValueError, AttributeError):
            raise ValidationError(f"due_date must be valid ISO 8601 datetime")

    return result


# Validator registry mapping tool names to validator functions
_VALIDATORS = {
    "add_task": validate_add_task_input,
    "list_tasks": validate_list_tasks_input,
    "complete_task": validate_complete_task_input,
    "delete_task": validate_delete_task_input,
    "update_task": validate_update_task_input,
}


def validate_tool_input(tool_name: str, tool_input: dict[str, Any]) -> dict[str, Any]:
    """
    Validate tool input against schema.

    Args:
        tool_name: Name of tool
        tool_input: Input dict to validate

    Returns:
        Validated and normalized input

    Raises:
        ValidationError: If input invalid
        KeyError: If tool not found
    """
    if tool_name not in _VALIDATORS:
        raise KeyError(f"Unknown tool: {tool_name}")

    return _VALIDATORS[tool_name](tool_input)
