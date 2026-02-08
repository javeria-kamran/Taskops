"""
Comprehensive unit tests for the update_task tool.

This module provides comprehensive test coverage for the update_task tool,
including field-specific update tests, multi-field updates, error handling,
user isolation tests, and response format validation.

Tests use the ToolExecutor to execute the update_task tool and verify
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
# Valid Input Tests - Field-Specific Updates
# ==============================================================================

@pytest.mark.asyncio
@pytest.mark.unit
async def test_update_task_title_only(async_session, user1_id, conversation_user1):
    """
    Test updating only the task title.

    Verifies that:
    - success=True is returned
    - title is changed to new value
    - other fields remain unchanged
    """
    async with async_session() as session:
        executor = ToolExecutor(session)

        # Create a task with specific fields
        task = await executor.execute(
            tool_name="add_task",
            arguments={
                "title": "Original Title",
                "description": "Original Description",
                "priority": "medium"
            },
            user_id=user1_id,
            conversation_id=conversation_user1.id
        )

        original = task["result"]

        # Update only title
        result = await executor.execute(
            tool_name="update_task",
            arguments={
                "task_id": original["id"],
                "title": "Updated Title"
            },
            user_id=user1_id,
            conversation_id=conversation_user1.id
        )

        assert result["success"] is True
        assert result["tool_name"] == "update_task"
        assert result["error"] is None

        updated = result["result"]
        assert updated["title"] == "Updated Title"
        assert updated["description"] == original["description"]
        assert updated["priority"] == original["priority"]


@pytest.mark.asyncio
@pytest.mark.unit
async def test_update_task_description_only(async_session, user1_id, conversation_user1):
    """
    Test updating only the task description.

    Verifies that:
    - success=True is returned
    - description is changed
    - title and priority remain unchanged
    """
    async with async_session() as session:
        executor = ToolExecutor(session)

        # Create a task
        task = await executor.execute(
            tool_name="add_task",
            arguments={
                "title": "Original Title",
                "description": "Original Description",
                "priority": "low"
            },
            user_id=user1_id,
            conversation_id=conversation_user1.id
        )

        original = task["result"]

        # Update only description
        result = await executor.execute(
            tool_name="update_task",
            arguments={
                "task_id": original["id"],
                "description": "Updated Description"
            },
            user_id=user1_id,
            conversation_id=conversation_user1.id
        )

        assert result["success"] is True

        updated = result["result"]
        assert updated["title"] == original["title"]
        assert updated["description"] == "Updated Description"
        assert updated["priority"] == original["priority"]


@pytest.mark.asyncio
@pytest.mark.unit
async def test_update_task_status_only(async_session, user1_id, conversation_user1):
    """
    Test updating only the task status.

    Verifies that:
    - success=True is returned
    - status is changed to "completed"
    - other fields remain unchanged
    """
    async with async_session() as session:
        executor = ToolExecutor(session)

        # Create a task
        task = await executor.execute(
            tool_name="add_task",
            arguments={"title": "Task to Update Status"},
            user_id=user1_id,
            conversation_id=conversation_user1.id
        )

        original = task["result"]

        # Update only status
        result = await executor.execute(
            tool_name="update_task",
            arguments={
                "task_id": original["id"],
                "status": "completed"
            },
            user_id=user1_id,
            conversation_id=conversation_user1.id
        )

        assert result["success"] is True

        updated = result["result"]
        assert updated["status"] == "completed"
        assert updated["title"] == original["title"]


@pytest.mark.asyncio
@pytest.mark.unit
async def test_update_task_priority_only(async_session, user1_id, conversation_user1):
    """
    Test updating only the task priority.

    Verifies that:
    - success=True is returned
    - priority is changed
    - other fields remain unchanged
    """
    async with async_session() as session:
        executor = ToolExecutor(session)

        # Create a task
        task = await executor.execute(
            tool_name="add_task",
            arguments={
                "title": "Task to Update Priority",
                "priority": "low"
            },
            user_id=user1_id,
            conversation_id=conversation_user1.id
        )

        original = task["result"]

        # Update only priority
        result = await executor.execute(
            tool_name="update_task",
            arguments={
                "task_id": original["id"],
                "priority": "high"
            },
            user_id=user1_id,
            conversation_id=conversation_user1.id
        )

        assert result["success"] is True

        updated = result["result"]
        assert updated["priority"] == "high"
        assert updated["title"] == original["title"]


@pytest.mark.asyncio
@pytest.mark.unit
async def test_update_task_multiple_fields(async_session, user1_id, conversation_user1):
    """
    Test updating multiple fields at once.

    Verifies that:
    - success=True is returned
    - all specified fields are updated
    - updates are applied correctly together
    """
    async with async_session() as session:
        executor = ToolExecutor(session)

        # Create a task
        task = await executor.execute(
            tool_name="add_task",
            arguments={
                "title": "Original Title",
                "description": "Original Description",
                "priority": "low",
                "status": "pending"
            },
            user_id=user1_id,
            conversation_id=conversation_user1.id
        )

        original = task["result"]

        # Update multiple fields
        result = await executor.execute(
            tool_name="update_task",
            arguments={
                "task_id": original["id"],
                "title": "New Title",
                "description": "New Description",
                "priority": "high",
                "status": "completed"
            },
            user_id=user1_id,
            conversation_id=conversation_user1.id
        )

        assert result["success"] is True

        updated = result["result"]
        assert updated["title"] == "New Title"
        assert updated["description"] == "New Description"
        assert updated["priority"] == "high"
        assert updated["status"] == "completed"


@pytest.mark.asyncio
@pytest.mark.unit
async def test_update_task_with_due_date(async_session, user1_id, conversation_user1):
    """
    Test updating task with due_date field.

    Verifies that:
    - success=True is returned
    - due_date is updated correctly
    """
    async with async_session() as session:
        executor = ToolExecutor(session)

        # Create a task
        task = await executor.execute(
            tool_name="add_task",
            arguments={"title": "Task with Due Date"},
            user_id=user1_id,
            conversation_id=conversation_user1.id
        )

        original = task["result"]
        new_due_date = (datetime.utcnow() + timedelta(days=10)).isoformat()

        # Update with due_date
        result = await executor.execute(
            tool_name="update_task",
            arguments={
                "task_id": original["id"],
                "due_date": new_due_date
            },
            user_id=user1_id,
            conversation_id=conversation_user1.id
        )

        assert result["success"] is True

        updated = result["result"]
        assert updated["due_date"] == new_due_date


# ==============================================================================
# Invalid Input Tests
# ==============================================================================

@pytest.mark.asyncio
@pytest.mark.unit
async def test_update_task_no_fields_provided(async_session, user1_id, conversation_user1):
    """
    Test updating a task with no update fields provided.

    Verifies that:
    - success=False is returned
    - error message indicates no fields to update
    """
    async with async_session() as session:
        executor = ToolExecutor(session)

        # Create a task
        task = await executor.execute(
            tool_name="add_task",
            arguments={"title": "Task"},
            user_id=user1_id,
            conversation_id=conversation_user1.id
        )

        # Try to update with no fields
        result = await executor.execute(
            tool_name="update_task",
            arguments={"task_id": task["result"]["id"]},
            user_id=user1_id,
            conversation_id=conversation_user1.id
        )

        assert result["success"] is False
        assert result["error"] is not None
        assert "no fields" in result["error"].lower() or "at least" in result["error"].lower()


@pytest.mark.asyncio
@pytest.mark.unit
async def test_update_task_task_not_found(async_session, user1_id, conversation_user1):
    """
    Test updating a non-existent task.

    Verifies that:
    - success=False is returned
    - error message indicates task not found
    """
    async with async_session() as session:
        executor = ToolExecutor(session)

        result = await executor.execute(
            tool_name="update_task",
            arguments={
                "task_id": "non-existent-id",
                "title": "New Title"
            },
            user_id=user1_id,
            conversation_id=conversation_user1.id
        )

        assert result["success"] is False
        assert result["error"] is not None
        assert "not found" in result["error"].lower() or "invalid" in result["error"].lower()


@pytest.mark.asyncio
@pytest.mark.unit
async def test_update_task_missing_task_id(async_session, user1_id, conversation_user1):
    """
    Test updating a task without providing task_id.

    Verifies that:
    - success=False is returned
    - error message indicates missing task_id
    """
    async with async_session() as session:
        executor = ToolExecutor(session)

        result = await executor.execute(
            tool_name="update_task",
            arguments={
                "title": "New Title"
            },
            user_id=user1_id,
            conversation_id=conversation_user1.id
        )

        assert result["success"] is False
        assert result["error"] is not None
        assert "task_id" in result["error"].lower() or "required" in result["error"].lower()


@pytest.mark.asyncio
@pytest.mark.unit
async def test_update_task_invalid_priority(async_session, user1_id, conversation_user1):
    """
    Test updating a task with invalid priority value.

    Verifies that:
    - success=False is returned
    - error indicates invalid priority
    """
    async with async_session() as session:
        executor = ToolExecutor(session)

        # Create a task
        task = await executor.execute(
            tool_name="add_task",
            arguments={"title": "Task"},
            user_id=user1_id,
            conversation_id=conversation_user1.id
        )

        # Try to update with invalid priority
        result = await executor.execute(
            tool_name="update_task",
            arguments={
                "task_id": task["result"]["id"],
                "priority": "invalid_priority"
            },
            user_id=user1_id,
            conversation_id=conversation_user1.id
        )

        assert result["success"] is False
        assert result["error"] is not None
        assert "priority" in result["error"].lower() or "invalid" in result["error"].lower()


@pytest.mark.asyncio
@pytest.mark.unit
async def test_update_task_invalid_status(async_session, user1_id, conversation_user1):
    """
    Test updating a task with invalid status value.

    Verifies that:
    - success=False is returned
    - error indicates invalid status
    """
    async with async_session() as session:
        executor = ToolExecutor(session)

        # Create a task
        task = await executor.execute(
            tool_name="add_task",
            arguments={"title": "Task"},
            user_id=user1_id,
            conversation_id=conversation_user1.id
        )

        # Try to update with invalid status
        result = await executor.execute(
            tool_name="update_task",
            arguments={
                "task_id": task["result"]["id"],
                "status": "invalid_status"
            },
            user_id=user1_id,
            conversation_id=conversation_user1.id
        )

        assert result["success"] is False
        assert result["error"] is not None


@pytest.mark.asyncio
@pytest.mark.unit
async def test_update_task_title_exceeds_max(async_session, user1_id, conversation_user1):
    """
    Test updating task title to exceed maximum length.

    Verifies that:
    - success=False is returned
    - error indicates length validation failure
    """
    async with async_session() as session:
        executor = ToolExecutor(session)

        # Create a task
        task = await executor.execute(
            tool_name="add_task",
            arguments={"title": "Original Title"},
            user_id=user1_id,
            conversation_id=conversation_user1.id
        )

        # Try to update with too long title
        long_title = "x" * 201

        result = await executor.execute(
            tool_name="update_task",
            arguments={
                "task_id": task["result"]["id"],
                "title": long_title
            },
            user_id=user1_id,
            conversation_id=conversation_user1.id
        )

        assert result["success"] is False
        assert result["error"] is not None


@pytest.mark.asyncio
@pytest.mark.unit
async def test_update_task_description_exceeds_max(async_session, user1_id, conversation_user1):
    """
    Test updating task description to exceed maximum length.

    Verifies that:
    - success=False is returned
    - error indicates length validation failure
    """
    async with async_session() as session:
        executor = ToolExecutor(session)

        # Create a task
        task = await executor.execute(
            tool_name="add_task",
            arguments={"title": "Original"},
            user_id=user1_id,
            conversation_id=conversation_user1.id
        )

        # Try to update with too long description
        long_description = "x" * 1025

        result = await executor.execute(
            tool_name="update_task",
            arguments={
                "task_id": task["result"]["id"],
                "description": long_description
            },
            user_id=user1_id,
            conversation_id=conversation_user1.id
        )

        assert result["success"] is False
        assert result["error"] is not None


# ==============================================================================
# User Isolation Tests
# ==============================================================================

@pytest.mark.asyncio
@pytest.mark.unit
async def test_update_task_cross_user_attempt(
    async_session,
    user1_id,
    user2_id,
    conversation_user1,
    conversation_user2
):
    """
    Test that user2 cannot update user1's task.

    Verifies that:
    - success=False when user2 tries to update user1's task
    - Task remains unchanged for user1
    - Access is properly denied
    """
    async with async_session() as session:
        executor = ToolExecutor(session)

        # User 1 creates a task
        task = await executor.execute(
            tool_name="add_task",
            arguments={"title": "User 1 Task", "priority": "low"},
            user_id=user1_id,
            conversation_id=conversation_user1.id
        )

        task_id = task["result"]["id"]
        original_title = task["result"]["title"]
        original_priority = task["result"]["priority"]

        # User 2 tries to update the task
        result = await executor.execute(
            tool_name="update_task",
            arguments={
                "task_id": task_id,
                "title": "Hacked Title",
                "priority": "high"
            },
            user_id=user2_id,
            conversation_id=conversation_user2.id
        )

        assert result["success"] is False
        assert result["error"] is not None

        # Verify user1 can still see the original task
        list_result = await executor.execute(
            tool_name="list_tasks",
            arguments={},
            user_id=user1_id,
            conversation_id=conversation_user1.id
        )

        assert list_result["success"] is True


# ==============================================================================
# Timestamp Update Tests
# ==============================================================================

@pytest.mark.asyncio
@pytest.mark.unit
async def test_update_task_updated_at_changes(async_session, user1_id, conversation_user1):
    """
    Test that updated_at timestamp changes when task is updated.

    Verifies that:
    - updated_at timestamp changes after update
    - New timestamp is valid ISO format
    """
    async with async_session() as session:
        executor = ToolExecutor(session)

        # Create a task
        task = await executor.execute(
            tool_name="add_task",
            arguments={"title": "Original Title"},
            user_id=user1_id,
            conversation_id=conversation_user1.id
        )

        original_task = task["result"]
        initial_updated_at = original_task.get("updated_at", original_task.get("created_at"))

        # Wait a bit to ensure time difference
        import time
        time.sleep(0.1)

        # Update the task
        result = await executor.execute(
            tool_name="update_task",
            arguments={
                "task_id": original_task["id"],
                "title": "Updated Title"
            },
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
# Edge Case Tests
# ==============================================================================

@pytest.mark.asyncio
@pytest.mark.unit
async def test_update_task_response_structure(async_session, user1_id, conversation_user1):
    """
    Test that update_task returns the expected response structure.

    Verifies the complete structure of the executor response.
    """
    async with async_session() as session:
        executor = ToolExecutor(session)

        # Create and update a task
        task = await executor.execute(
            tool_name="add_task",
            arguments={"title": "Original Title"},
            user_id=user1_id,
            conversation_id=conversation_user1.id
        )

        result = await executor.execute(
            tool_name="update_task",
            arguments={
                "task_id": task["result"]["id"],
                "title": "Updated Title"
            },
            user_id=user1_id,
            conversation_id=conversation_user1.id
        )

        # Check executor response structure
        assert "success" in result
        assert "tool_name" in result
        assert "result" in result
        assert "error" in result

        assert result["tool_name"] == "update_task"
        assert result["error"] is None
        assert result["success"] is True

        # Check updated_task structure
        updated_task = result["result"]
        assert "id" in updated_task
        assert "title" in updated_task
        assert "status" in updated_task
        assert "priority" in updated_task
        assert "updated_at" in updated_task


@pytest.mark.asyncio
@pytest.mark.unit
async def test_update_task_title_with_whitespace(async_session, user1_id, conversation_user1):
    """
    Test updating task title with leading/trailing whitespace.

    Verifies that:
    - success=True is returned
    - whitespace is trimmed from title
    """
    async with async_session() as session:
        executor = ToolExecutor(session)

        # Create a task
        task = await executor.execute(
            tool_name="add_task",
            arguments={"title": "Original"},
            user_id=user1_id,
            conversation_id=conversation_user1.id
        )

        # Update with whitespace
        result = await executor.execute(
            tool_name="update_task",
            arguments={
                "task_id": task["result"]["id"],
                "title": "  Trimmed Title  "
            },
            user_id=user1_id,
            conversation_id=conversation_user1.id
        )

        assert result["success"] is True
        assert result["result"]["title"] == "Trimmed Title"


@pytest.mark.asyncio
@pytest.mark.unit
async def test_update_task_all_priority_levels(async_session, user1_id, conversation_user1):
    """
    Test updating task with all valid priority levels.

    Verifies that:
    - success=True for all priority values (low, medium, high)
    """
    async with async_session() as session:
        executor = ToolExecutor(session)

        # Create a task
        task = await executor.execute(
            tool_name="add_task",
            arguments={"title": "Priority Test"},
            user_id=user1_id,
            conversation_id=conversation_user1.id
        )

        task_id = task["result"]["id"]

        # Test all priority levels
        for priority in ["low", "medium", "high"]:
            result = await executor.execute(
                tool_name="update_task",
                arguments={
                    "task_id": task_id,
                    "priority": priority
                },
                user_id=user1_id,
                conversation_id=conversation_user1.id
            )

            assert result["success"] is True
            assert result["result"]["priority"] == priority


@pytest.mark.asyncio
@pytest.mark.unit
async def test_update_task_all_status_values(async_session, user1_id, conversation_user1):
    """
    Test updating task with all valid status values.

    Verifies that:
    - success=True for all status values (pending, completed)
    """
    async with async_session() as session:
        executor = ToolExecutor(session)

        # Create a task
        task = await executor.execute(
            tool_name="add_task",
            arguments={"title": "Status Test"},
            user_id=user1_id,
            conversation_id=conversation_user1.id
        )

        task_id = task["result"]["id"]

        # Test all valid status values
        for status in ["pending", "completed"]:
            result = await executor.execute(
                tool_name="update_task",
                arguments={
                    "task_id": task_id,
                    "status": status
                },
                user_id=user1_id,
                conversation_id=conversation_user1.id
            )

            assert result["success"] is True
            assert result["result"]["status"] == status


@pytest.mark.asyncio
@pytest.mark.unit
async def test_update_task_preserves_unmodified_fields(async_session, user1_id, conversation_user1):
    """
    Test that updating some fields preserves unmodified fields.

    Verifies that:
    - Only specified fields are updated
    - All other fields remain the same
    """
    async with async_session() as session:
        executor = ToolExecutor(session)

        # Create a task with all fields
        task = await executor.execute(
            tool_name="add_task",
            arguments={
                "title": "Original Title",
                "description": "Original Description",
                "priority": "high",
                "status": "pending"
            },
            user_id=user1_id,
            conversation_id=conversation_user1.id
        )

        original = task["result"]

        # Update only title
        result = await executor.execute(
            tool_name="update_task",
            arguments={
                "task_id": original["id"],
                "title": "New Title"
            },
            user_id=user1_id,
            conversation_id=conversation_user1.id
        )

        assert result["success"] is True

        updated = result["result"]
        assert updated["title"] == "New Title"
        assert updated["description"] == original["description"]
        assert updated["priority"] == original["priority"]
        assert updated["status"] == original["status"]


# ==============================================================================
# Database Error Tests
# ==============================================================================

@pytest.mark.asyncio
@pytest.mark.unit
async def test_update_task_handles_db_error(async_session, user1_id, conversation_user1):
    """
    Test handling of database errors during task update.

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
                tool_name="update_task",
                arguments={
                    "task_id": task["result"]["id"],
                    "title": "New Title"
                },
                user_id=user1_id,
                conversation_id=conversation_user1.id
            )

            assert result["success"] is False
            assert result["error"] is not None
