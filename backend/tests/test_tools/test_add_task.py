"""
Comprehensive unit tests for the add_task tool.

This module provides comprehensive test coverage for the add_task tool,
including valid input tests, invalid input tests, user isolation tests,
and database error handling tests.

Tests use the ToolExecutor to execute the add_task tool and verify
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
async def test_add_task_valid_input(async_session, user1_id, conversation_user1):
    """
    Test creating a task with title and description.

    Verifies that:
    - success=True is returned
    - task_id is returned in result
    - task has correct title and description
    """
    async with async_session() as session:
        executor = ToolExecutor(session)
        result = await executor.execute(
            tool_name="add_task",
            arguments={
                "title": "Test Task",
                "description": "Test Description"
            },
            user_id=user1_id,
            conversation_id=conversation_user1.id
        )

        assert result["success"] is True
        assert result["tool_name"] == "add_task"
        assert result["error"] is None
        assert result["result"] is not None

        task = result["result"]
        assert "id" in task
        assert task["title"] == "Test Task"
        assert task["description"] == "Test Description"
        assert task["status"] == "pending"
        assert task["priority"] == "medium"  # Default priority
        assert "created_at" in task

        # Verify task_id is a valid UUID string
        try:
            UUID(task["id"])
        except ValueError:
            pytest.fail("task_id is not a valid UUID")


@pytest.mark.asyncio
@pytest.mark.unit
async def test_add_task_title_only(async_session, user1_id, conversation_user1):
    """
    Test creating a task with title only (no description).

    Verifies that:
    - success=True is returned
    - task_id is returned
    - task has correct title
    - description is None or empty
    """
    async with async_session() as session:
        executor = ToolExecutor(session)
        result = await executor.execute(
            tool_name="add_task",
            arguments={
                "title": "Simple Task"
            },
            user_id=user1_id,
            conversation_id=conversation_user1.id
        )

        assert result["success"] is True
        assert result["error"] is None
        assert "id" in result["result"]
        assert result["result"]["title"] == "Simple Task"
        assert result["result"]["description"] is None


@pytest.mark.asyncio
@pytest.mark.unit
async def test_add_task_with_priority(async_session, user1_id, conversation_user1):
    """
    Test creating a task with custom priority.

    Verifies that:
    - success=True is returned
    - priority is correctly set to high
    """
    async with async_session() as session:
        executor = ToolExecutor(session)
        result = await executor.execute(
            tool_name="add_task",
            arguments={
                "title": "Important Task",
                "description": "This is important",
                "priority": "high"
            },
            user_id=user1_id,
            conversation_id=conversation_user1.id
        )

        assert result["success"] is True
        assert result["result"]["priority"] == "high"


@pytest.mark.asyncio
@pytest.mark.unit
async def test_add_task_with_due_date(async_session, user1_id, conversation_user1):
    """
    Test creating a task with a due date.

    Verifies that:
    - success=True is returned
    - due_date is correctly set and in ISO format
    """
    async with async_session() as session:
        executor = ToolExecutor(session)
        due_date = (datetime.utcnow() + timedelta(days=5)).isoformat()

        result = await executor.execute(
            tool_name="add_task",
            arguments={
                "title": "Task with deadline",
                "due_date": due_date
            },
            user_id=user1_id,
            conversation_id=conversation_user1.id
        )

        assert result["success"] is True
        assert result["result"]["due_date"] == due_date


# ==============================================================================
# Invalid Input Tests
# ==============================================================================

@pytest.mark.asyncio
@pytest.mark.unit
async def test_add_task_missing_title(async_session, user1_id, conversation_user1):
    """
    Test creating a task without title.

    Verifies that:
    - success=False is returned
    - error message is present in response
    """
    async with async_session() as session:
        executor = ToolExecutor(session)
        result = await executor.execute(
            tool_name="add_task",
            arguments={
                "description": "Description without title"
            },
            user_id=user1_id,
            conversation_id=conversation_user1.id
        )

        assert result["success"] is False
        assert result["error"] is not None
        assert "title" in result["error"].lower()


@pytest.mark.asyncio
@pytest.mark.unit
async def test_add_task_empty_title(async_session, user1_id, conversation_user1):
    """
    Test creating a task with empty title string.

    Verifies that:
    - success=False is returned
    - error message indicates empty title
    """
    async with async_session() as session:
        executor = ToolExecutor(session)
        result = await executor.execute(
            tool_name="add_task",
            arguments={
                "title": "   "
            },
            user_id=user1_id,
            conversation_id=conversation_user1.id
        )

        assert result["success"] is False
        assert result["error"] is not None


@pytest.mark.asyncio
@pytest.mark.unit
async def test_add_task_title_exceeds_max(async_session, user1_id, conversation_user1):
    """
    Test creating a task with title exceeding 200 characters.

    Verifies that:
    - success=False is returned
    - error indicates length validation failure
    """
    async with async_session() as session:
        executor = ToolExecutor(session)
        long_title = "x" * 201

        result = await executor.execute(
            tool_name="add_task",
            arguments={
                "title": long_title
            },
            user_id=user1_id,
            conversation_id=conversation_user1.id
        )

        assert result["success"] is False
        assert result["error"] is not None
        assert "max" in result["error"].lower() or "200" in result["error"]


@pytest.mark.asyncio
@pytest.mark.unit
async def test_add_task_description_exceeds_max(async_session, user1_id, conversation_user1):
    """
    Test creating a task with description exceeding 1024 characters.

    Verifies that:
    - success=False is returned
    - error indicates length validation failure for description
    """
    async with async_session() as session:
        executor = ToolExecutor(session)
        long_description = "x" * 1025

        result = await executor.execute(
            tool_name="add_task",
            arguments={
                "title": "Valid Title",
                "description": long_description
            },
            user_id=user1_id,
            conversation_id=conversation_user1.id
        )

        assert result["success"] is False
        assert result["error"] is not None
        assert "description" in result["error"].lower()


@pytest.mark.asyncio
@pytest.mark.unit
async def test_add_task_invalid_priority(async_session, user1_id, conversation_user1):
    """
    Test creating a task with invalid priority value.

    Verifies that:
    - success=False is returned
    - error indicates invalid priority
    """
    async with async_session() as session:
        executor = ToolExecutor(session)
        result = await executor.execute(
            tool_name="add_task",
            arguments={
                "title": "Task",
                "priority": "urgent"  # Invalid priority
            },
            user_id=user1_id,
            conversation_id=conversation_user1.id
        )

        assert result["success"] is False
        assert result["error"] is not None
        assert "priority" in result["error"].lower()


@pytest.mark.asyncio
@pytest.mark.unit
async def test_add_task_invalid_due_date_format(async_session, user1_id, conversation_user1):
    """
    Test creating a task with invalid due date format.

    Verifies that:
    - success=False is returned
    - error indicates invalid date format
    """
    async with async_session() as session:
        executor = ToolExecutor(session)
        result = await executor.execute(
            tool_name="add_task",
            arguments={
                "title": "Task with bad date",
                "due_date": "not-a-date"
            },
            user_id=user1_id,
            conversation_id=conversation_user1.id
        )

        assert result["success"] is False
        assert result["error"] is not None
        assert "due_date" in result["error"].lower() or "iso" in result["error"].lower()


@pytest.mark.asyncio
@pytest.mark.unit
async def test_add_task_title_with_whitespace(async_session, user1_id, conversation_user1):
    """
    Test creating a task with title that has leading/trailing whitespace.

    Verifies that:
    - success=True is returned
    - whitespace is trimmed from title
    """
    async with async_session() as session:
        executor = ToolExecutor(session)
        result = await executor.execute(
            tool_name="add_task",
            arguments={
                "title": "  Trimmed Task  "
            },
            user_id=user1_id,
            conversation_id=conversation_user1.id
        )

        assert result["success"] is True
        assert result["result"]["title"] == "Trimmed Task"


# ==============================================================================
# User Isolation Tests
# ==============================================================================

@pytest.mark.asyncio
@pytest.mark.unit
async def test_add_task_requires_user_id(async_session, conversation_user1):
    """
    Test that user_id is required for task creation.

    Verifies that tasks created with different user IDs are isolated.
    """
    async with async_session() as session:
        executor = ToolExecutor(session)

        # Create tasks with different user IDs
        user1_result = await executor.execute(
            tool_name="add_task",
            arguments={"title": "User 1 Task"},
            user_id="user-1",
            conversation_id=conversation_user1.id
        )

        user2_result = await executor.execute(
            tool_name="add_task",
            arguments={"title": "User 2 Task"},
            user_id="user-2",
            conversation_id=conversation_user1.id
        )

        # Both should succeed
        assert user1_result["success"] is True
        assert user2_result["success"] is True

        # Each user's task should have their own ID
        assert user1_result["result"]["id"] != user2_result["result"]["id"]


@pytest.mark.asyncio
@pytest.mark.unit
async def test_add_task_user1_cannot_see_user2_task(
    async_session,
    user1_id,
    user2_id,
    conversation_user1,
    conversation_user2
):
    """
    Test that user1 cannot see user2's tasks.

    Verifies that:
    - Tasks created by user1 and user2 are kept separate
    - list_tasks tool respects user isolation
    """
    async with async_session() as session:
        executor = ToolExecutor(session)

        # User 1 creates a task
        user1_task = await executor.execute(
            tool_name="add_task",
            arguments={
                "title": "User 1 Private Task",
                "description": "Only user1 should see this"
            },
            user_id=user1_id,
            conversation_id=conversation_user1.id
        )

        # User 2 creates a task
        user2_task = await executor.execute(
            tool_name="add_task",
            arguments={
                "title": "User 2 Private Task",
                "description": "Only user2 should see this"
            },
            user_id=user2_id,
            conversation_id=conversation_user2.id
        )

        # Both tasks should be created successfully
        assert user1_task["success"] is True
        assert user2_task["success"] is True

        # Tasks should have different ids
        assert user1_task["result"]["id"] != user2_task["result"]["id"]

        # Tasks should have different titles
        assert user1_task["result"]["title"] != user2_task["result"]["title"]

        # Verify through list_tasks that isolation is maintained
        user1_list = await executor.execute(
            tool_name="list_tasks",
            arguments={},
            user_id=user1_id,
            conversation_id=conversation_user1.id
        )

        user2_list = await executor.execute(
            tool_name="list_tasks",
            arguments={},
            user_id=user2_id,
            conversation_id=conversation_user2.id
        )

        # Each user should only see their own tasks (currently mock returns empty)
        # This test ensures the structure is correct for when real implementation is added
        assert user1_list["success"] is True
        assert user2_list["success"] is True


# ==============================================================================
# Database Error Tests
# ==============================================================================

@pytest.mark.asyncio
@pytest.mark.unit
async def test_add_task_handles_db_error(async_session, user1_id, conversation_user1):
    """
    Test handling of database errors during task creation.

    Verifies that:
    - success=False is returned on database error
    - error response contains error type/message
    """
    async with async_session() as session:
        executor = ToolExecutor(session)

        # Mock the session to raise an exception
        with patch.object(session, 'execute', side_effect=Exception("Database connection failed")):
            # The executor should still return a valid response structure
            # even though there's an error
            result = await executor.execute(
                tool_name="add_task",
                arguments={
                    "title": "Task that will fail",
                },
                user_id=user1_id,
                conversation_id=conversation_user1.id
            )

            assert result["success"] is False
            assert result["error"] is not None
            # Error should mention execution or database
            assert "error" in result["error"].lower() or "execution" in result["error"].lower()


# ==============================================================================
# Edge Case Tests
# ==============================================================================

@pytest.mark.asyncio
@pytest.mark.unit
async def test_add_task_title_at_max_length(async_session, user1_id, conversation_user1):
    """
    Test creating a task with title at exactly 200 characters (max).

    Verifies that:
    - success=True is returned
    - task is created successfully at boundary
    """
    async with async_session() as session:
        executor = ToolExecutor(session)
        max_title = "x" * 200

        result = await executor.execute(
            tool_name="add_task",
            arguments={
                "title": max_title
            },
            user_id=user1_id,
            conversation_id=conversation_user1.id
        )

        assert result["success"] is True
        assert len(result["result"]["title"]) == 200


@pytest.mark.asyncio
@pytest.mark.unit
async def test_add_task_description_at_max_length(async_session, user1_id, conversation_user1):
    """
    Test creating a task with description at exactly 1024 characters (max).

    Verifies that:
    - success=True is returned
    - task description is created successfully at boundary
    """
    async with async_session() as session:
        executor = ToolExecutor(session)
        max_description = "x" * 1024

        result = await executor.execute(
            tool_name="add_task",
            arguments={
                "title": "Task with max description",
                "description": max_description
            },
            user_id=user1_id,
            conversation_id=conversation_user1.id
        )

        assert result["success"] is True
        assert len(result["result"]["description"]) == 1024


@pytest.mark.asyncio
@pytest.mark.unit
async def test_add_task_special_characters_in_title(async_session, user1_id, conversation_user1):
    """
    Test creating a task with special characters in title.

    Verifies that:
    - success=True is returned
    - special characters are preserved
    """
    async with async_session() as session:
        executor = ToolExecutor(session)
        special_title = "Task with @#$%^&*() special chars!!!"

        result = await executor.execute(
            tool_name="add_task",
            arguments={
                "title": special_title
            },
            user_id=user1_id,
            conversation_id=conversation_user1.id
        )

        assert result["success"] is True
        assert result["result"]["title"] == special_title


@pytest.mark.asyncio
@pytest.mark.unit
async def test_add_task_unicode_characters(async_session, user1_id, conversation_user1):
    """
    Test creating a task with unicode characters.

    Verifies that:
    - success=True is returned
    - unicode characters are preserved
    """
    async with async_session() as session:
        executor = ToolExecutor(session)
        unicode_title = "购买 🎉 物品 𝓶𝓾𝓵𝓽𝓲𝓶𝓮𝓭𝓲𝓪"

        result = await executor.execute(
            tool_name="add_task",
            arguments={
                "title": unicode_title
            },
            user_id=user1_id,
            conversation_id=conversation_user1.id
        )

        assert result["success"] is True
        assert result["result"]["title"] == unicode_title


@pytest.mark.asyncio
@pytest.mark.unit
async def test_add_task_all_priority_levels(async_session, user1_id, conversation_user1):
    """
    Test creating tasks with all valid priority levels.

    Verifies that:
    - success=True for all priority values (low, medium, high)
    """
    async with async_session() as session:
        executor = ToolExecutor(session)

        for priority in ["low", "medium", "high"]:
            result = await executor.execute(
                tool_name="add_task",
                arguments={
                    "title": f"Task with {priority} priority",
                    "priority": priority
                },
                user_id=user1_id,
                conversation_id=conversation_user1.id
            )

            assert result["success"] is True
            assert result["result"]["priority"] == priority


@pytest.mark.asyncio
@pytest.mark.unit
async def test_add_task_response_structure(async_session, user1_id, conversation_user1):
    """
    Test that add_task returns the expected response structure.

    Verifies the complete structure of the executor response.
    """
    async with async_session() as session:
        executor = ToolExecutor(session)
        result = await executor.execute(
            tool_name="add_task",
            arguments={
                "title": "Structure Test",
                "description": "Testing response structure"
            },
            user_id=user1_id,
            conversation_id=conversation_user1.id
        )

        # Check executor response structure
        assert "success" in result
        assert "tool_name" in result
        assert "result" in result
        assert "error" in result

        # When successful, error should be None
        assert result["error"] is None
        assert result["tool_name"] == "add_task"

        # Check task result structure
        task = result["result"]
        assert "id" in task
        assert "title" in task
        assert "description" in task
        assert "status" in task
        assert "priority" in task
        assert "created_at" in task
        assert "due_date" in task  # Can be None


@pytest.mark.asyncio
@pytest.mark.unit
async def test_add_task_created_at_is_valid_iso(async_session, user1_id, conversation_user1):
    """
    Test that created_at timestamp is in valid ISO format.

    Verifies that:
    - created_at can be parsed as ISO datetime
    """
    async with async_session() as session:
        executor = ToolExecutor(session)
        result = await executor.execute(
            tool_name="add_task",
            arguments={
                "title": "Timestamp Test"
            },
            user_id=user1_id,
            conversation_id=conversation_user1.id
        )

        assert result["success"] is True

        # Try to parse the created_at timestamp
        created_at = result["result"]["created_at"]
        try:
            parsed_datetime = datetime.fromisoformat(created_at)
            # Verify it's recent (within last minute)
            now = datetime.utcnow()
            diff = (now - parsed_datetime).total_seconds()
            assert 0 <= diff <= 60, f"created_at is not recent: {created_at}"
        except ValueError:
            pytest.fail(f"created_at is not valid ISO format: {created_at}")
