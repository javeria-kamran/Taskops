"""Unit tests for toggle_complete functionality in TaskManager."""

import pytest
from src.services.task_manager import TaskManager
from src.lib.exceptions import TaskNotFoundError


class TestToggleComplete:
    """Test toggle_complete method."""

    def test_toggle_complete_marks_incomplete_as_complete(self):
        """Test toggling an incomplete task to complete."""
        manager = TaskManager()
        task = manager.add_task("Test task")

        assert task.completed is False

        updated_task = manager.toggle_complete(task.id)

        assert updated_task.completed is True
        assert updated_task.id == task.id
        assert updated_task.title == task.title

    def test_toggle_complete_marks_complete_as_incomplete(self):
        """Test toggling a complete task back to incomplete."""
        manager = TaskManager()
        task = manager.add_task("Test task")

        # First toggle to complete
        manager.toggle_complete(task.id)
        # Then toggle back to incomplete
        updated_task = manager.toggle_complete(task.id)

        assert updated_task.completed is False

    def test_toggle_complete_multiple_times(self):
        """Test toggling task status multiple times."""
        manager = TaskManager()
        task = manager.add_task("Test task")

        # Toggle 1: incomplete -> complete
        task1 = manager.toggle_complete(task.id)
        assert task1.completed is True

        # Toggle 2: complete -> incomplete
        task2 = manager.toggle_complete(task.id)
        assert task2.completed is False

        # Toggle 3: incomplete -> complete
        task3 = manager.toggle_complete(task.id)
        assert task3.completed is True

    def test_toggle_complete_with_invalid_id(self):
        """Test that toggling non-existent task raises TaskNotFoundError."""
        manager = TaskManager()

        with pytest.raises(TaskNotFoundError, match="Task #999 not found"):
            manager.toggle_complete(999)

    def test_toggle_complete_preserves_other_fields(self):
        """Test that toggling completion preserves other task fields."""
        manager = TaskManager()
        task = manager.add_task("Test task", "Test description")

        original_id = task.id
        original_title = task.title
        original_description = task.description
        original_created_at = task.created_at

        updated_task = manager.toggle_complete(task.id)

        assert updated_task.id == original_id
        assert updated_task.title == original_title
        assert updated_task.description == original_description
        assert updated_task.created_at == original_created_at
        # Only completed status should change
        assert updated_task.completed is True

    def test_toggle_complete_affects_correct_task(self):
        """Test that toggling affects only the specified task."""
        manager = TaskManager()
        task1 = manager.add_task("Task 1")
        task2 = manager.add_task("Task 2")
        task3 = manager.add_task("Task 3")

        # Toggle only task 2
        manager.toggle_complete(task2.id)

        # Verify only task 2 is completed
        all_tasks = manager.get_all_tasks()
        assert all_tasks[0].completed is False  # Task 1
        assert all_tasks[1].completed is True   # Task 2
        assert all_tasks[2].completed is False  # Task 3
