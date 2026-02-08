"""
T017: Tool Execution Layer

Routes tool calls to repository methods.
Each executor:
1. Validates input (calls validators.py)
2. Calls appropriate repository method
3. Returns result (error handling done by error_handler.py)

No business logic here - pure delegation to repositories.
Repositories handle user isolation and database operations.
"""

import logging
from typing import Any, Callable
from sqlalchemy.ext.asyncio import AsyncSession

from app.chat.repositories.task_repository import TaskRepository
from app.chat.mcp_server.validators import validate_tool_input, ValidationError

logger = logging.getLogger(__name__)


async def execute_add_task(
    validated_input: dict[str, Any],
    user_id: str,
    session: AsyncSession
) -> dict[str, Any]:
    """Execute add_task tool"""
    repo = TaskRepository(session)
    task = await repo.create(
        user_id=user_id,
        title=validated_input["title"],
        description=validated_input.get("description"),
        priority=validated_input.get("priority", "medium"),
        due_date=validated_input.get("due_date")
    )
    return {
        "task_id": str(task.id),
        "title": task.title,
        "priority": task.priority,
        "status": "pending"
    }


async def execute_list_tasks(
    validated_input: dict[str, Any],
    user_id: str,
    session: AsyncSession
) -> dict[str, Any]:
    """Execute list_tasks tool"""
    repo = TaskRepository(session)

    # Map status filter
    status_filter = None
    if validated_input["status"] == "pending":
        status_filter = False
    elif validated_input["status"] == "completed":
        status_filter = True
    # "all" means status_filter = None

    tasks = await repo.list_by_user(
        user_id=user_id,
        status=status_filter,
        limit=validated_input["limit"],
        offset=validated_input["offset"]
    )

    return {
        "tasks": [
            {
                "task_id": str(task.id),
                "title": task.title,
                "description": task.description,
                "priority": task.priority,
                "status": "completed" if task.completed else "pending",
                "created_at": task.created_at.isoformat() if task.created_at else None
            }
            for task in tasks
        ],
        "count": len(tasks)
    }


async def execute_complete_task(
    validated_input: dict[str, Any],
    user_id: str,
    session: AsyncSession
) -> dict[str, Any]:
    """Execute complete_task tool"""
    repo = TaskRepository(session)
    task = await repo.complete(
        task_id=validated_input["task_id"],
        user_id=user_id
    )

    if not task:
        raise Exception(f"Task not found: {validated_input['task_id']}")

    return {
        "task_id": str(task.id),
        "title": task.title,
        "status": "completed"
    }


async def execute_delete_task(
    validated_input: dict[str, Any],
    user_id: str,
    session: AsyncSession
) -> dict[str, Any]:
    """Execute delete_task tool"""
    repo = TaskRepository(session)
    success = await repo.delete(
        task_id=validated_input["task_id"],
        user_id=user_id
    )

    if not success:
        raise Exception(f"Task not found: {validated_input['task_id']}")

    return {
        "task_id": validated_input["task_id"],
        "status": "deleted"
    }


async def execute_update_task(
    validated_input: dict[str, Any],
    user_id: str,
    session: AsyncSession
) -> dict[str, Any]:
    """Execute update_task tool"""
    repo = TaskRepository(session)

    # Build update dict with only provided fields
    updates = {}
    if "title" in validated_input:
        updates["title"] = validated_input["title"]
    if "description" in validated_input:
        updates["description"] = validated_input["description"]
    if "priority" in validated_input:
        updates["priority"] = validated_input["priority"]
    if "due_date" in validated_input:
        updates["due_date"] = validated_input["due_date"]

    task = await repo.update(
        task_id=validated_input["task_id"],
        user_id=user_id,
        **updates
    )

    if not task:
        raise Exception(f"Task not found: {validated_input['task_id']}")

    return {
        "task_id": str(task.id),
        "title": task.title,
        "priority": task.priority,
        "status": "completed" if task.completed else "pending"
    }


# Executor registry
_EXECUTORS: dict[str, Callable] = {
    "add_task": execute_add_task,
    "list_tasks": execute_list_tasks,
    "complete_task": execute_complete_task,
    "delete_task": execute_delete_task,
    "update_task": execute_update_task,
}


def get_tool_executor(tool_name: str) -> Callable:
    """
    Get executor function for tool.

    Returns:
        Async callable: async def executor(validated_input, user_id, session) -> dict

    Raises:
        KeyError: If tool not found
    """
    return _EXECUTORS[tool_name]


async def execute_tool(
    tool_name: str,
    tool_input: dict[str, Any],
    user_id: str,
    session: AsyncSession
) -> dict[str, Any]:
    """
    Validate and execute tool.

    Args:
        tool_name: Name of tool
        tool_input: Raw input dict
        user_id: User ID for isolation
        session: Database session

    Returns:
        Tool result dict

    Raises:
        ValidationError: If input invalid
        Exception: Tool-specific errors
    """
    # Validate input
    validated = validate_tool_input(tool_name, tool_input)

    # Get executor
    executor = get_tool_executor(tool_name)

    # Execute with user isolation
    return await executor(validated, user_id, session)
