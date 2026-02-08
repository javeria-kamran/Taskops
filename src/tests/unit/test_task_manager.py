"""Unit tests for TaskManager service."""

import pytest
from src.services.task_manager import TaskManager
from src.models.task import Task
from src.lib.exceptions import ValidationError, TaskNotFoundError


class TestAddTask:
    """Test add_task method."""

    def test_add_task_with_title_only(self):
        """Test adding a task with only a title."""
        manager = TaskManager()
        task = manager.add_task("Buy groceries")

        assert task.id == 1
        assert task.title == "Buy groceries"
        assert task.description == ""
        assert task.completed is False
        assert len(manager.get_all_tasks()) == 1

    def test_add_task_with_title_and_description(self):
        """Test adding a task with title and description."""
        manager = TaskManager()
        task = manager.add_task("Buy groceries", "Milk, eggs, bread")

        assert task.id == 1
        assert task.title == "Buy groceries"
        assert task.description == "Milk, eggs, bread"
        assert task.completed is False

    def test_add_task_increments_id(self):
        """Test that task IDs increment automatically."""
        manager = TaskManager()
        task1 = manager.add_task("Task 1")
        task2 = manager.add_task("Task 2")
        task3 = manager.add_task("Task 3")

        assert task1.id == 1
        assert task2.id == 2
        assert task3.id == 3

    def test_add_task_strips_whitespace(self):
        """Test that title whitespace is stripped."""
        manager = TaskManager()
        task = manager.add_task("  Task with spaces  ", "  Description  ")

        assert task.title == "Task with spaces"
        assert task.description == "Description"

    def test_add_task_rejects_empty_title(self):
        """Test that empty title is rejected."""
        manager = TaskManager()

        with pytest.raises(ValidationError, match="Title cannot be empty"):
            manager.add_task("")

        with pytest.raises(ValidationError, match="Title cannot be empty"):
            manager.add_task("   ")

    def test_add_task_rejects_long_title(self):
        """Test that title over 200 characters is rejected."""
        manager = TaskManager()
        long_title = "x" * 201

        with pytest.raises(ValidationError, match="Title must be 200 characters or less"):
            manager.add_task(long_title)

    def test_add_task_rejects_long_description(self):
        """Test that description over 1000 characters is rejected."""
        manager = TaskManager()
        long_description = "x" * 1001

        with pytest.raises(ValidationError, match="Description must be 1000 characters or less"):
            manager.add_task("Valid title", long_description)


class TestGetAllTasks:
    """Test get_all_tasks method."""

    def test_get_all_tasks_empty(self):
        """Test getting tasks from empty manager."""
        manager = TaskManager()
        tasks = manager.get_all_tasks()

        assert tasks == []
        assert len(tasks) == 0

    def test_get_all_tasks_returns_all(self):
        """Test that all tasks are returned."""
        manager = TaskManager()
        manager.add_task("Task 1")
        manager.add_task("Task 2")
        manager.add_task("Task 3")

        tasks = manager.get_all_tasks()

        assert len(tasks) == 3
        assert tasks[0].title == "Task 1"
        assert tasks[1].title == "Task 2"
        assert tasks[2].title == "Task 3"

    def test_get_all_tasks_returns_copy(self):
        """Test that returned list is a copy, not reference."""
        manager = TaskManager()
        manager.add_task("Task 1")

        tasks1 = manager.get_all_tasks()
        tasks2 = manager.get_all_tasks()

        # Should be different list objects
        assert tasks1 is not tasks2
        # But contain same data
        assert len(tasks1) == len(tasks2)
        assert tasks1[0].id == tasks2[0].id

    def test_get_all_tasks_preserves_order(self):
        """Test that tasks are returned in creation order."""
        manager = TaskManager()
        task1 = manager.add_task("First")
        task2 = manager.add_task("Second")
        task3 = manager.add_task("Third")

        tasks = manager.get_all_tasks()

        assert tasks[0].id == task1.id
        assert tasks[1].id == task2.id
        assert tasks[2].id == task3.id


class TestGetTask:
    """Test get_task method."""

    def test_get_task_by_id(self):
        """Test retrieving a task by ID."""
        manager = TaskManager()
        created_task = manager.add_task("Test task")

        retrieved_task = manager.get_task(1)

        assert retrieved_task.id == created_task.id
        assert retrieved_task.title == created_task.title

    def test_get_task_not_found(self):
        """Test that getting non-existent task raises error."""
        manager = TaskManager()

        with pytest.raises(TaskNotFoundError, match="Task #99 not found"):
            manager.get_task(99)

    def test_get_task_after_multiple_adds(self):
        """Test retrieving specific task from multiple tasks."""
        manager = TaskManager()
        manager.add_task("Task 1")
        target_task = manager.add_task("Task 2")
        manager.add_task("Task 3")

        retrieved = manager.get_task(2)

        assert retrieved.id == target_task.id
        assert retrieved.title == "Task 2"
