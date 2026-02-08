"""Unit tests for update_task functionality in TaskManager."""

import pytest
from src.services.task_manager import TaskManager
from src.lib.exceptions import ValidationError, TaskNotFoundError


class TestUpdateTask:
    """Test update_task method."""

    def test_update_task_title_only(self):
        """Test updating only the title."""
        manager = TaskManager()
        task = manager.add_task("Original title", "Original description")

        updated = manager.update_task(task.id, title="New title")

        assert updated.title == "New title"
        assert updated.description == "Original description"
        assert updated.id == task.id

    def test_update_task_description_only(self):
        """Test updating only the description."""
        manager = TaskManager()
        task = manager.add_task("Original title", "Original description")

        updated = manager.update_task(task.id, description="New description")

        assert updated.title == "Original title"
        assert updated.description == "New description"

    def test_update_task_both_fields(self):
        """Test updating both title and description."""
        manager = TaskManager()
        task = manager.add_task("Original title", "Original description")

        updated = manager.update_task(task.id, title="New title", description="New description")

        assert updated.title == "New title"
        assert updated.description == "New description"

    def test_update_task_with_invalid_id(self):
        """Test updating non-existent task raises error."""
        manager = TaskManager()

        with pytest.raises(TaskNotFoundError, match="Task #999 not found"):
            manager.update_task(999, title="New title")

    def test_update_task_with_empty_title(self):
        """Test that empty title is rejected."""
        manager = TaskManager()
        task = manager.add_task("Original title")

        with pytest.raises(ValidationError, match="Title cannot be empty"):
            manager.update_task(task.id, title="")

    def test_update_task_preserves_other_fields(self):
        """Test that update preserves completed status and created_at."""
        manager = TaskManager()
        task = manager.add_task("Original title")
        manager.toggle_complete(task.id)

        original_created_at = task.created_at
        original_completed = True

        updated = manager.update_task(task.id, title="New title")

        assert updated.completed == original_completed
        assert updated.created_at == original_created_at

    def test_update_task_none_values_unchanged(self):
        """Test that None values leave fields unchanged."""
        manager = TaskManager()
        task = manager.add_task("Original title", "Original description")

        updated = manager.update_task(task.id, title=None, description=None)

        assert updated.title == "Original title"
        assert updated.description == "Original description"
