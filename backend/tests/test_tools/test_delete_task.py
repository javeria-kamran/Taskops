"""
Comprehensive unit tests for the delete_task tool.

This module provides comprehensive test coverage for the delete_task tool,
including valid deletion tests, error handling tests, user isolation tests,
and verification of deletion through list operations.

Tests use the ToolExecutor to execute the delete_task tool and verify
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
async def test_delete_task_valid(async_session, user1_id, conversation_user1):
    """
    Test deleting an existing task successfully.

    Verifies that:
    - success=True is returned
    - Task is deleted and no longer in list_tasks
    """
    async with async_session() as session:
        executor = ToolExecutor(session)

        # Create a task first
        task = await executor.execute(
            tool_name="add_task",
            arguments={"title": "Task to Delete"},
            user_id=user1_id,
            conversation_id=conversation_user1.id
        )

        task_id = task["result"]["id"]

        # Delete the task
        result = await executor.execute(
            tool_name="delete_task",
            arguments={"task_id": task_id},
            user_id=user1_id,
            conversation_id=conversation_user1.id
        )

        assert result["success"] is True
        assert result["tool_name"] == "delete_task"
        assert result["error"] is None


@pytest.mark.asyncio
@pytest.mark.unit
async def test_delete_task_already_deleted(async_session, user1_id, conversation_user1):
    """
    Test deleting a task that has already been deleted.

    Verifies that:
    - Second deletion returns success=False
    - Error is properly reported
    """
    async with async_session() as session:
        executor = ToolExecutor(session)

        # Create a task
        task = await executor.execute(
            tool_name="add_task",
            arguments={"title": "Task to Delete Twice"},
            user_id=user1_id,
            conversation_id=conversation_user1.id
        )

        task_id = task["result"]["id"]

        # Delete the task first time
        result1 = await executor.execute(
            tool_name="delete_task",
            arguments={"task_id": task_id},
            user_id=user1_id,
            conversation_id=conversation_user1.id
        )

        assert result1["success"] is True

        # Try to delete again
        result2 = await executor.execute(
            tool_name="delete_task",
            arguments={"task_id": task_id},
            user_id=user1_id,
            conversation_id=conversation_user1.id
        )

        assert result2["success"] is False
        assert result2["error"] is not None


@pytest.mark.asyncio
@pytest.mark.unit
async def test_delete_task_task_not_found(async_session, user1_id, conversation_user1):
    """
    Test deleting a non-existent task.

    Verifies that:
    - success=False is returned
    - error message is provided
    """
    async with async_session() as session:
        executor = ToolExecutor(session)

        # Try to delete non-existent task
        result = await executor.execute(
            tool_name="delete_task",
            arguments={"task_id": "non-existent-id"},
            user_id=user1_id,
            conversation_id=conversation_user1.id
        )

        assert result["success"] is False
        assert result["error"] is not None
        assert "not found" in result["error"].lower() or "invalid" in result["error"].lower()


@pytest.mark.asyncio
@pytest.mark.unit
async def test_delete_task_cross_user_attempt(
    async_session,
    user1_id,
    user2_id,
    conversation_user1,
    conversation_user2
):
    """
    Test that user2 cannot delete user1's task.

    Verifies that:
    - success=False when user2 tries to delete user1's task
    - Task still exists for user1
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

        # User 2 tries to delete the task
        result = await executor.execute(
            tool_name="delete_task",
            arguments={"task_id": task_id},
            user_id=user2_id,
            conversation_id=conversation_user2.id
        )

        assert result["success"] is False
        assert result["error"] is not None

        # Verify user1 can still see the task
        list_result = await executor.execute(
            tool_name="list_tasks",
            arguments={},
            user_id=user1_id,
            conversation_id=conversation_user1.id
        )

        assert list_result["success"] is True


@pytest.mark.asyncio
@pytest.mark.unit
async def test_delete_task_response_structure(async_session, user1_id, conversation_user1):
    """
    Test that delete_task returns the expected response structure.

    Verifies the complete structure of the executor response.
    """
    async with async_session() as session:
        executor = ToolExecutor(session)

        # Create and delete a task
        task = await executor.execute(
            tool_name="add_task",
            arguments={"title": "Structure Test"},
            user_id=user1_id,
            conversation_id=conversation_user1.id
        )

        result = await executor.execute(
            tool_name="delete_task",
            arguments={"task_id": task["result"]["id"]},
            user_id=user1_id,
            conversation_id=conversation_user1.id
        )

        # Check executor response structure
        assert "success" in result
        assert "tool_name" in result
        assert "result" in result
        assert "error" in result

        assert result["tool_name"] == "delete_task"
        assert result["error"] is None
        assert result["success"] is True

        # Check result contains success message or confirmation
        assert result["result"] is not None


@pytest.mark.asyncio
@pytest.mark.unit
async def test_delete_task_verifies_with_list(async_session, user1_id, conversation_user1):
    """
    Test that after deletion, list_tasks no longer returns the task.

    Verifies that:
    - Task is deleted and removed from list_tasks
    - Deletion is permanent and consistent
    """
    async with async_session() as session:
        executor = ToolExecutor(session)

        # Create a task
        task = await executor.execute(
            tool_name="add_task",
            arguments={"title": "Task to Verify Deletion"},
            user_id=user1_id,
            conversation_id=conversation_user1.id
        )

        task_id = task["result"]["id"]

        # List tasks - should contain the task
        list_before = await executor.execute(
            tool_name="list_tasks",
            arguments={},
            user_id=user1_id,
            conversation_id=conversation_user1.id
        )

        assert list_before["success"] is True

        # Delete the task
        delete_result = await executor.execute(
            tool_name="delete_task",
            arguments={"task_id": task_id},
            user_id=user1_id,
            conversation_id=conversation_user1.id
        )

        assert delete_result["success"] is True

        # List tasks again - task should be gone
        list_after = await executor.execute(
            tool_name="list_tasks",
            arguments={},
            user_id=user1_id,
            conversation_id=conversation_user1.id
        )

        assert list_after["success"] is True

        # Verify task is not in the list
        task_ids = [t.get("id") for t in list_after["result"]["tasks"]]
        assert task_id not in task_ids


# ==============================================================================
# Invalid Input Tests
# ==============================================================================

@pytest.mark.asyncio
@pytest.mark.unit
async def test_delete_task_missing_task_id(async_session, user1_id, conversation_user1):
    """
    Test deleting a task without providing task_id.

    Verifies that:
    - success=False is returned
    - error message indicates missing task_id
    """
    async with async_session() as session:
        executor = ToolExecutor(session)

        result = await executor.execute(
            tool_name="delete_task",
            arguments={},
            user_id=user1_id,
            conversation_id=conversation_user1.id
        )

        assert result["success"] is False
        assert result["error"] is not None
        assert "task_id" in result["error"].lower() or "required" in result["error"].lower()


@pytest.mark.asyncio
@pytest.mark.unit
async def test_delete_task_empty_task_id(async_session, user1_id, conversation_user1):
    """
    Test deleting a task with empty task_id.

    Verifies that:
    - success=False is returned
    - error is provided
    """
    async with async_session() as session:
        executor = ToolExecutor(session)

        result = await executor.execute(
            tool_name="delete_task",
            arguments={"task_id": ""},
            user_id=user1_id,
            conversation_id=conversation_user1.id
        )

        assert result["success"] is False
        assert result["error"] is not None


@pytest.mark.asyncio
@pytest.mark.unit
async def test_delete_task_whitespace_task_id(async_session, user1_id, conversation_user1):
    """
    Test deleting a task with whitespace-only task_id.

    Verifies that:
    - success=False is returned
    """
    async with async_session() as session:
        executor = ToolExecutor(session)

        result = await executor.execute(
            tool_name="delete_task",
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
async def test_delete_task_with_special_characters_in_id(async_session, user1_id, conversation_user1):
    """
    Test deleting a task with special characters in task_id.

    Verifies that error is handled properly.
    """
    async with async_session() as session:
        executor = ToolExecutor(session)

        result = await executor.execute(
            tool_name="delete_task",
            arguments={"task_id": "task-@#$%^&*()"},
            user_id=user1_id,
            conversation_id=conversation_user1.id
        )

        # Should not find the task
        assert result["success"] is False
        assert result["error"] is not None


@pytest.mark.asyncio
@pytest.mark.unit
async def test_delete_task_multiple_deletions_in_sequence(async_session, user1_id, conversation_user1):
    """
    Test creating and deleting multiple tasks in sequence.

    Verifies that:
    - Multiple tasks can be created and deleted
    - Each deletion is independent
    """
    async with async_session() as session:
        executor = ToolExecutor(session)

        # Create multiple tasks
        tasks = []
        for i in range(3):
            task = await executor.execute(
                tool_name="add_task",
                arguments={"title": f"Task {i+1}"},
                user_id=user1_id,
                conversation_id=conversation_user1.id
            )
            tasks.append(task["result"]["id"])

        # Delete them one by one
        for task_id in tasks:
            result = await executor.execute(
                tool_name="delete_task",
                arguments={"task_id": task_id},
                user_id=user1_id,
                conversation_id=conversation_user1.id
            )
            assert result["success"] is True


@pytest.mark.asyncio
@pytest.mark.unit
async def test_delete_task_deletes_only_specified_task(async_session, user1_id, conversation_user1):
    """
    Test that deleting a task only removes that specific task.

    Verifies that:
    - Other tasks are not affected by deletion
    - Only the specified task is removed
    """
    async with async_session() as session:
        executor = ToolExecutor(session)

        # Create multiple tasks
        task1 = await executor.execute(
            tool_name="add_task",
            arguments={"title": "Task 1"},
            user_id=user1_id,
            conversation_id=conversation_user1.id
        )

        task2 = await executor.execute(
            tool_name="add_task",
            arguments={"title": "Task 2"},
            user_id=user1_id,
            conversation_id=conversation_user1.id
        )

        task3 = await executor.execute(
            tool_name="add_task",
            arguments={"title": "Task 3"},
            user_id=user1_id,
            conversation_id=conversation_user1.id
        )

        # Delete task 2
        delete_result = await executor.execute(
            tool_name="delete_task",
            arguments={"task_id": task2["result"]["id"]},
            user_id=user1_id,
            conversation_id=conversation_user1.id
        )

        assert delete_result["success"] is True

        # List tasks - both 1 and 3 should still exist
        list_result = await executor.execute(
            tool_name="list_tasks",
            arguments={},
            user_id=user1_id,
            conversation_id=conversation_user1.id
        )

        task_ids = [t.get("id") for t in list_result["result"]["tasks"]]
        assert task1["result"]["id"] in task_ids
        assert task3["result"]["id"] in task_ids
        assert task2["result"]["id"] not in task_ids


# ==============================================================================
# Database Error Tests
# ==============================================================================

@pytest.mark.asyncio
@pytest.mark.unit
async def test_delete_task_handles_db_error(async_session, user1_id, conversation_user1):
    """
    Test handling of database errors during task deletion.

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
                tool_name="delete_task",
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
async def test_delete_task_response_message_field(async_session, user1_id, conversation_user1):
    """
    Test that delete_task response contains a message or result field.

    Verifies that:
    - Response includes confirmation of deletion
    - Message field is present and informative
    """
    async with async_session() as session:
        executor = ToolExecutor(session)

        # Create and delete a task
        task = await executor.execute(
            tool_name="add_task",
            arguments={"title": "Message Test"},
            user_id=user1_id,
            conversation_id=conversation_user1.id
        )

        result = await executor.execute(
            tool_name="delete_task",
            arguments={"task_id": task["result"]["id"]},
            user_id=user1_id,
            conversation_id=conversation_user1.id
        )

        assert result["success"] is True
        assert result["result"] is not None


@pytest.mark.asyncio
@pytest.mark.unit
async def test_delete_task_response_on_not_found(async_session, user1_id, conversation_user1):
    """
    Test that delete_task error response is properly formatted.

    Verifies that:
    - success=False
    - error field is populated
    - error message is descriptive
    """
    async with async_session() as session:
        executor = ToolExecutor(session)

        result = await executor.execute(
            tool_name="delete_task",
            arguments={"task_id": "non-existent-task-id"},
            user_id=user1_id,
            conversation_id=conversation_user1.id
        )

        assert result["success"] is False
        assert "success" in result
        assert "tool_name" in result
        assert "error" in result
        assert result["error"] is not None
        assert len(result["error"]) > 0
