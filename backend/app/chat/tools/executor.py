"""
T029-T032: Tool Executor

Routes tool calls to task management functions.
Handles argument validation, error handling, and result formatting.
All operations user-isolated and session-safe.

Tool Execution Flow:
1. Receive tool call with user_id and session
2. Validate tool exists
3. Validate arguments against schema
4. Execute tool function
5. Return structured result
"""

import logging
from typing import Any, Optional
from uuid import UUID
from datetime import datetime
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

logger = logging.getLogger(__name__)


class ToolExecutionError(Exception):
    """Base exception for tool execution errors."""
    pass


class ToolNotFoundError(ToolExecutionError):
    """Tool not found in registry."""
    pass


class ToolValidationError(ToolExecutionError):
    """Tool arguments failed validation."""
    pass


class ToolExecutor:
    """Executes task management tools with user isolation."""

    def __init__(self, session: AsyncSession):
        """
        Initialize executor with database session.

        Args:
            session: AsyncSession for database operations
        """
        self.session = session

    async def execute(
        self,
        tool_name: str,
        arguments: dict[str, Any],
        user_id: str,
        conversation_id: UUID
    ) -> dict[str, Any]:
        """
        Execute a tool call.

        Args:
            tool_name: Name of tool to execute
            arguments: Tool arguments dict
            user_id: User ID for isolation
            conversation_id: Conversation ID for logging

        Returns:
            {
                "success": bool,
                "tool_name": str,
                "result": Any,
                "error": Optional[str]
            }
        """
        try:
            logger.info(f"[T032] Executing tool '{tool_name}' for user {user_id}")

            if tool_name == "add_task":
                result = await self._execute_add_task(arguments, user_id)
            elif tool_name == "list_tasks":
                result = await self._execute_list_tasks(arguments, user_id)
            elif tool_name == "complete_task":
                result = await self._execute_complete_task(arguments, user_id)
            elif tool_name == "delete_task":
                result = await self._execute_delete_task(arguments, user_id)
            elif tool_name == "update_task":
                result = await self._execute_update_task(arguments, user_id)
            else:
                raise ToolNotFoundError(f"Unknown tool: {tool_name}")

            logger.info(f"[T032] Tool '{tool_name}' executed successfully")
            return {
                "success": True,
                "tool_name": tool_name,
                "result": result,
                "error": None
            }

        except ToolValidationError as e:
            logger.warning(f"[T032] Validation error for {tool_name}: {e}")
            return {
                "success": False,
                "tool_name": tool_name,
                "result": None,
                "error": f"Validation error: {str(e)}"
            }

        except ToolNotFoundError as e:
            logger.error(f"[T032] Tool not found: {e}")
            return {
                "success": False,
                "tool_name": tool_name,
                "result": None,
                "error": str(e)
            }

        except Exception as e:
            logger.error(f"[T032] Tool execution failed: {e}", exc_info=True)
            return {
                "success": False,
                "tool_name": tool_name,
                "result": None,
                "error": f"Execution error: {str(e)}"
            }

    async def _execute_add_task(self, args: dict, user_id: str) -> dict:
        """
        Execute add_task tool.

        Args:
            args: {title, description?, priority?, due_date?}
            user_id: User ID

        Returns:
            {id, title, status, ...}
        """
        # Validate required arguments
        if not isinstance(args.get("title"), str) or not args["title"].strip():
            raise ToolValidationError("title is required and must be a non-empty string")

        title = args["title"].strip()
        if len(title) > 200:
            raise ToolValidationError("title must be max 200 characters")

        description = args.get("description", "").strip()
        if description and len(description) > 1024:
            raise ToolValidationError("description must be max 1024 characters")

        priority = args.get("priority", "medium")
        if priority not in ("low", "medium", "high"):
            raise ToolValidationError("priority must be low, medium, or high")

        due_date = args.get("due_date")
        if due_date:
            try:
                datetime.fromisoformat(due_date)
            except ValueError:
                raise ToolValidationError("due_date must be in ISO format (YYYY-MM-DD or ISO8601)")

        # TODO: Phase 9+ - Import Task model and TaskRepository
        # For now, return mock result
        from uuid import uuid4

        task_id = uuid4()
        logger.debug(
            f"[T029] Created task {task_id} for user {user_id}: "
            f"'{title}' (priority={priority})"
        )

        return {
            "id": str(task_id),
            "title": title,
            "description": description or None,
            "status": "pending",
            "priority": priority,
            "due_date": due_date,
            "created_at": datetime.utcnow().isoformat()
        }

    async def _execute_list_tasks(self, args: dict, user_id: str) -> dict:
        """
        Execute list_tasks tool.

        Args:
            args: {status?, priority?, limit?}
            user_id: User ID

        Returns:
            {count, tasks: [{id, title, status, ...}]}
        """
        status = args.get("status", "all")
        if status not in ("all", "pending", "completed"):
            raise ToolValidationError("status must be all, pending, or completed")

        priority = args.get("priority")
        if priority and priority not in ("low", "medium", "high"):
            raise ToolValidationError("priority must be low, medium, or high")

        limit = args.get("limit", 20)
        if not isinstance(limit, int) or limit < 1 or limit > 100:
            raise ToolValidationError("limit must be between 1 and 100")

        logger.debug(
            f"[T030] Listing tasks for user {user_id}: "
            f"status={status}, priority={priority}, limit={limit}"
        )

        # TODO: Phase 9+ - Import Task model and TaskRepository
        # For now, return mock result
        return {
            "count": 0,
            "tasks": [],
            "status_filter": status,
            "priority_filter": priority
        }

    async def _execute_complete_task(self, args: dict, user_id: str) -> dict:
        """
        Execute complete_task tool.

        Args:
            args: {task_id}
            user_id: User ID

        Returns:
            {id, title, status}
        """
        task_id = args.get("task_id")
        if not task_id:
            raise ToolValidationError("task_id is required")

        try:
            UUID(task_id)
        except ValueError:
            raise ToolValidationError(f"task_id must be a valid UUID")

        logger.debug(f"[T031] Completing task {task_id} for user {user_id}")

        # TODO: Phase 9+ - Import Task model and TaskRepository
        # For now, return mock result
        return {
            "id": task_id,
            "status": "completed",
            "completed_at": datetime.utcnow().isoformat()
        }

    async def _execute_delete_task(self, args: dict, user_id: str) -> dict:
        """
        Execute delete_task tool.

        Args:
            args: {task_id}
            user_id: User ID

        Returns:
            {id, deleted: true}
        """
        task_id = args.get("task_id")
        if not task_id:
            raise ToolValidationError("task_id is required")

        try:
            UUID(task_id)
        except ValueError:
            raise ToolValidationError("task_id must be a valid UUID")

        logger.debug(f"[T032] Deleting task {task_id} for user {user_id}")

        # TODO: Phase 9+ - Import Task model and TaskRepository
        # For now, return mock result
        return {
            "id": task_id,
            "deleted": True,
            "deleted_at": datetime.utcnow().isoformat()
        }

    async def _execute_update_task(self, args: dict, user_id: str) -> dict:
        """
        Execute update_task tool.

        Args:
            args: {task_id, title?, description?, priority?, due_date?}
            user_id: User ID

        Returns:
            {id, title, status, ...}
        """
        task_id = args.get("task_id")
        if not task_id:
            raise ToolValidationError("task_id is required")

        try:
            UUID(task_id)
        except ValueError:
            raise ToolValidationError("task_id must be a valid UUID")

        # Validate optional fields
        title = args.get("title")
        if title is not None:
            if not isinstance(title, str) or not title.strip():
                raise ToolValidationError("title must be a non-empty string")
            if len(title) > 200:
                raise ToolValidationError("title must be max 200 characters")

        description = args.get("description")
        if description is not None:
            if not isinstance(description, str):
                raise ToolValidationError("description must be a string")
            if len(description) > 1024:
                raise ToolValidationError("description must be max 1024 characters")

        priority = args.get("priority")
        if priority is not None and priority not in ("low", "medium", "high"):
            raise ToolValidationError("priority must be low, medium, or high")

        due_date = args.get("due_date")
        if due_date is not None:
            try:
                datetime.fromisoformat(due_date)
            except ValueError:
                raise ToolValidationError("due_date must be in ISO format")

        logger.debug(f"[T032] Updating task {task_id} for user {user_id}")

        # TODO: Phase 9+ - Import Task model and TaskRepository
        # For now, return mock result
        return {
            "id": task_id,
            "title": title or "Task",
            "priority": priority or "medium",
            "updated_at": datetime.utcnow().isoformat()
        }
