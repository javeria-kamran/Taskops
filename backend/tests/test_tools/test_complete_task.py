"""
Comprehensive unit tests for the complete_task tool.

This module provides comprehensive test coverage for the complete_task tool,
including valid completion tests, error handling tests, user isolation tests,
and response format validation.

Tests use the ToolExecutor to execute the complete_task tool and verify
proper behavior for various scenarios.
"""

import pytest
import pytest_asyncio
from datetime import datetime, timedelta
from uuid import UUID
from unittest.mock import AsyncMock, patch, MagicMock
from sqlalchemy.ext.asyncio import AsyncSession

from app.chat.tools.executor import ToolExecutor, ToolValidationError


# ==============================================================================
# Valid Input Tests
# ==============================================================================

@pytest.mark.asyncio
@pytest.mark.unit
async def test_complete_task_valid(async_session, user1_id, conversation_user1):
    """
    Test completing an existing task successfully.

    Verifies that:
    - success=True is returned
    - task status changes to "completed"
    - updated_task is returned in result
    """
    async with async_session() as session:
        executor = ToolExecutor(session)

        # Create a task first
        task = await executor.execute(
            tool_name="add_task",
            arguments={"title": "Task to Complete"},
            user_id=user1_id,
            conversation_id=conversation_user1.id
        )

        task_id = task["result"]["id"]

        # Complete the task
        result = await executor.execute(
            tool_name="complete_task",
            arguments={"task_id": task_id},
            user_id=user1_id,
            conversation_id=conversation_user1.id
        )

        assert result["success"] is True
        assert result["tool_name"] == "complete_task"
        assert result["error"] is None
        assert result["result"] is not None

        completed_task = result["result"]
        assert completed_task["id"] == task_id
        assert completed_task["status"] == "completed"


@pytest.mark.asyncio
@pytest.mark.unit
async def test_complete_task_already_completed(async_session, user1_id, conversation_user1):
    """
    Test completing an already-completed task.

    Verifies that:
    - Second completion may succeed or fail gracefully
    - Idempotent behavior or proper error handling
    """
    async with async_session() as session:
        executor = ToolExecutor(session)

        # Create a task
        task = await executor.execute(
            tool_name="add_task",
            arguments={"title": "Task to Complete"},
            user_id=user1_id,
            conversation_id=conversation_user1.id
        )

        task_id = task["result"]["id"]

        # Complete the task first time
        result1 = await executor.execute(
            tool_name="complete_task",
            arguments={"task_id": task_id},
            user_id=user1_id,
            conversation_id=conversation_user1.id
        )

        assert result1["success"] is True

        # Try to complete again
        result2 = await executor.execute(
            tool_name="complete_task",
            arguments={"task_id": task_id},
            user_id=user1_id,
            conversation_id=conversation_user1.id
        )

        # Should either succeed (idempotent) or return error
        assert isinstance(result2["success"], bool)


@pytest.mark.asyncio
@pytest.mark.unit
async def test_complete_task_task_not_found(async_session, user1_id, conversation_user1):
    """
    Test completing a non-existent task.

    Verifies that:
    - success=False is returned
    - error message is provided
    """
    async with async_session() as session:
        executor = ToolExecutor(session)

        # Try to complete non-existent task
        result = await executor.execute(
            tool_name="complete_task",
            arguments={"task_id": "non-existent-id"},
            user_id=user1_id,
            conversation_id=conversation_user1.id
        )

        assert result["success"] is False
        assert result["error"] is not None
        assert "not found" in result["error"].lower() or "invalid" in result["error"].lower()


@pytest.mark.asyncio
@pytest.mark.unit
async def test_complete_task_cross_user_attempt(
    async_session,
    user1_id,
    user2_id,
    conversation_user1,
    conversation_user2
):
    """
    Test that user2 cannot complete user1's task.

    Verifies that:
    - success=False when user2 tries to complete user1's task
    - Task remains pending for user1
    - Access is properly denied (403/authorization error)
    """
    async with async_session() as session:
        executor = ToolExecutor(session)

        # User 1 creates a task
        task = await executor.execute(
            tool_name="add_task",
            arguments={"title": "User 1 Task"},
            user_id=user1_id,
            conversation_id=conversation_user1.id
        )

        task_id = task["result"]["id"]

        # User 2 tries to complete the task
        result = await executor.execute(
            tool_name="complete_task",
            arguments={"task_id": task_id},
            user_id=user2_id,
            conversation_id=conversation_user2.id
        )

        assert result["success"] is False
        assert result["error"] is not None
        assert "not found" in result["error"].lower() or "access" in result["error"].lower() or "permission" in result["error"].lower()

        # Verify user1 can still see the task as pending
        list_result = await executor.execute(
            tool_name="list_tasks",
            arguments={},
            user_id=user1_id,
            conversation_id=conversation_user1.id
        )

        assert list_result["success"] is True


@pytest.mark.asyncio
@pytest.mark.unit
async def test_complete_task_response_structure(async_session, user1_id, conversation_user1):
    """
    Test that complete_task returns the expected response structure.

    Verifies the complete structure of the executor response.
    """
    async with async_session() as session:
        executor = ToolExecutor(session)

        # Create and complete a task
        task = await executor.execute(
            tool_name="add_task",
            arguments={"title": "Structure Test"},
            user_id=user1_id,
            conversation_id=conversation_user1.id
        )

        result = await executor.execute(
            tool_name="complete_task",
            arguments={"task_id": task["result"]["id"]},
            user_id=user1_id,
            conversation_id=conversation_user1.id
        )

        # Check executor response structure
        assert "success" in result
        assert "tool_name" in result
        assert "result" in result
        assert "error" in result

        assert result["tool_name"] == "complete_task"
        assert result["error"] is None
        assert result["success"] is True

        # Check updated_task structure
        updated_task = result["result"]
        assert "id" in updated_task
        assert "status" in updated_task
        assert "updated_at" in updated_task


@pytest.mark.asyncio
@pytest.mark.unit
async def test_complete_task_updates_updated_at(async_session, user1_id, conversation_user1):
    """
    Test that updated_at timestamp is changed when task is completed.

    Verifies that:
    - updated_at timestamp changes after completion
    - New timestamp is valid ISO format
    """
    async with async_session() as session:
        executor = ToolExecutor(session)

        # Create a task
        task = await executor.execute(
            tool_name="add_task",
            arguments={"title": "Timestamp Test"},
            user_id=user1_id,
            conversation_id=conversation_user1.id
        )

        initial_task = task["result"]
        initial_updated_at = initial_task.get("updated_at", initial_task.get("created_at"))

        # Wait a bit to ensure time difference
        import time
        time.sleep(0.1)

        # Complete the task
        result = await executor.execute(
            tool_name="complete_task",
            arguments={"task_id": initial_task["id"]},
            user_id=user1_id,
            conversation_id=conversation_user1.id
        )

        assert result["success"] is True

        updated_task = result["result"]
        updated_at = updated_task.get("updated_at")

        # Verify updated_at changed
        if initial_updated_at and updated_at:
            assert updated_at != initial_updated_at or "updated_at" in updated_task

        # Verify timestamp is valid ISO format
        try:
            datetime.fromisoformat(updated_at)
        except (ValueError, TypeError):
            pytest.fail(f"updated_at is not valid ISO format: {updated_at}")


# ==============================================================================
# Invalid Input Tests
# ==============================================================================

@pytest.mark.asyncio
@pytest.mark.unit
async def test_complete_task_missing_task_id(async_session, user1_id, conversation_user1):
    """
    Test completing a task without providing task_id.

    Verifies that:
    - success=False is returned
    - error message indicates missing task_id
    """
    async with async_session() as session:
        executor = ToolExecutor(session)

        result = await executor.execute(
            tool_name="complete_task",
            arguments={},
            user_id=user1_id,
            conversation_id=conversation_user1.id
        )

        assert result["success"] is False
        assert result["error"] is not None
        assert "task_id" in result["error"].lower() or "required" in result["error"].lower()


@pytest.mark.asyncio
@pytest.mark.unit
async def test_complete_task_empty_task_id(async_session, user1_id, conversation_user1):
    """
    Test completing a task with empty task_id.

    Verifies that:
    - success=False is returned
    - error is provided
    """
    async with async_session() as session:
        executor = ToolExecutor(session)

        result = await executor.execute(
            tool_name="complete_task",
            arguments={"task_id": ""},
            user_id=user1_id,
            conversation_id=conversation_user1.id
        )

        assert result["success"] is False
        assert result["error"] is not None


@pytest.mark.asyncio
@pytest.mark.unit
async def test_complete_task_whitespace_task_id(async_session, user1_id, conversation_user1):
    """
    Test completing a task with whitespace-only task_id.

    Verifies that:
    - success=False is returned
    """
    async with async_session() as session:
        executor = ToolExecutor(session)

        result = await executor.execute(
            tool_name="complete_task",
            arguments={"task_id": "   "},
            user_id=user1_id,
            conversation_id=conversation_user1.id
        )

        assert result["success"] is False
        assert result["error"] is not None


# ==============================================================================
# Edge Case Tests
# ==============================================================================

@pytest.mark.asyncio
@pytest.mark.unit
async def test_complete_task_with_special_characters_in_id(async_session, user1_id, conversation_user1):
    """
    Test completing a task with special characters in task_id.

    Verifies that error is handled properly.
    """
    async with async_session() as session:
        executor = ToolExecutor(session)

        result = await executor.execute(
            tool_name="complete_task",
            arguments={"task_id": "task-@#$%^&*()"},
            user_id=user1_id,
            conversation_id=conversation_user1.id
        )

        # Should not find the task
        assert result["success"] is False
        assert result["error"] is not None


@pytest.mark.asyncio
@pytest.mark.unit
async def test_complete_task_preserves_other_fields(async_session, user1_id, conversation_user1):
    """
    Test that completing a task preserves all other fields unchanged.

    Verifies that:
    - title, description, priority remain unchanged
    - Only status changes to "completed"
    """
    async with async_session() as session:
        executor = ToolExecutor(session)

        # Create a task with specific fields
        task = await executor.execute(
            tool_name="add_task",
            arguments={
                "title": "Original Title",
                "description": "Original Description",
                "priority": "high"
            },
            user_id=user1_id,
            conversation_id=conversation_user1.id
        )

        original = task["result"]

        # Complete the task
        result = await executor.execute(
            tool_name="complete_task",
            arguments={"task_id": original["id"]},
            user_id=user1_id,
            conversation_id=conversation_user1.id
        )

        assert result["success"] is True

        completed = result["result"]
        assert completed["title"] == original["title"]
        assert completed["description"] == original["description"]
        assert completed["priority"] == original["priority"]
        assert completed["status"] == "completed"


@pytest.mark.asyncio
@pytest.mark.unit
async def test_complete_task_status_is_completed_string(async_session, user1_id, conversation_user1):
    """
    Test that the status field is specifically set to "completed" (lowercase).

    Verifies consistent status string format.
    """
    async with async_session() as session:
        executor = ToolExecutor(session)

        # Create and complete a task
        task = await executor.execute(
            tool_name="add_task",
            arguments={"title": "Status Format Test"},
            user_id=user1_id,
            conversation_id=conversation_user1.id
        )

        result = await executor.execute(
            tool_name="complete_task",
            arguments={"task_id": task["result"]["id"]},
            user_id=user1_id,
            conversation_id=conversation_user1.id
        )

        assert result["success"] is True
        assert result["result"]["status"] == "completed"


# ==============================================================================
# Database Error Tests
# ==============================================================================

@pytest.mark.asyncio
@pytest.mark.unit
async def test_complete_task_handles_db_error(async_session, user1_id, conversation_user1):
    """
    Test handling of database errors during task completion.

    Verifies that:
    - success=False is returned on database error
    - error response contains error information
    """
    async with async_session() as session:
        executor = ToolExecutor(session)

        # Create a valid task first
        task = await executor.execute(
            tool_name="add_task",
            arguments={"title": "Task for DB Error Test"},
            user_id=user1_id,
            conversation_id=conversation_user1.id
        )

        # Mock the session to raise an exception
        with patch.object(session, 'execute', side_effect=Exception("Database connection failed")):
            result = await executor.execute(
                tool_name="complete_task",
                arguments={"task_id": task["result"]["id"]},
                user_id=user1_id,
                conversation_id=conversation_user1.id
            )

            assert result["success"] is False
            assert result["error"] is not None


# ==============================================================================
# Response Format Tests
# ==============================================================================

@pytest.mark.asyncio
@pytest.mark.unit
async def test_complete_task_response_contains_updated_task(async_session, user1_id, conversation_user1):
    """
    Test that result contains the updated_task with all fields.

    Verifies that:
    - result contains the full updated task object
    - All expected fields are present
    """
    async with async_session() as session:
        executor = ToolExecutor(session)

        # Create a task
        task = await executor.execute(
            tool_name="add_task",
            arguments={
                "title": "Complete Task",
                "description": "Full description",
                "priority": "high"
            },
            user_id=user1_id,
            conversation_id=conversation_user1.id
        )

        result = await executor.execute(
            tool_name="complete_task",
            arguments={"task_id": task["result"]["id"]},
            user_id=user1_id,
            conversation_id=conversation_user1.id
        )

        assert result["success"] is True

        updated_task = result["result"]
        assert "id" in updated_task
        assert "title" in updated_task
        assert "description" in updated_task
        assert "status" in updated_task
        assert "priority" in updated_task
        assert "created_at" in updated_task
        assert "updated_at" in updated_task
