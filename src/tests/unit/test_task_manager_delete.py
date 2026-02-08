"""Unit tests for delete_task functionality in TaskManager."""

import pytest
from src.services.task_manager import TaskManager
from src.lib.exceptions import TaskNotFoundError


class TestDeleteTask:
    """Test delete_task method."""

    def test_delete_task_removes_from_list(self):
        """Test that deleted task is removed from task list."""
        manager = TaskManager()
        task = manager.add_task("Test task")

        manager.delete_task(task.id)

        tasks = manager.get_all_tasks()
        assert len(tasks) == 0

    def test_delete_task_returns_deleted_task(self):
        """Test that delete returns the deleted task."""
        manager = TaskManager()
        task = manager.add_task("Test task", "Test description")

        deleted = manager.delete_task(task.id)

        assert deleted.id == task.id
        assert deleted.title == task.title
        assert deleted.description == task.description

    def test_delete_task_with_invalid_id(self):
        """Test deleting non-existent task raises error."""
        manager = TaskManager()

        with pytest.raises(TaskNotFoundError, match="Task #999 not found"):
            manager.delete_task(999)

    def test_delete_task_from_multiple(self):
        """Test deleting specific task from multiple tasks."""
        manager = TaskManager()
        task1 = manager.add_task("Task 1")
        task2 = manager.add_task("Task 2")
        task3 = manager.add_task("Task 3")

        manager.delete_task(task2.id)

        tasks = manager.get_all_tasks()
        assert len(tasks) == 2
        assert tasks[0].title == "Task 1"
        assert tasks[1].title == "Task 3"

    def test_delete_task_ids_not_reused(self):
        """Test that deleted task IDs are not reused."""
        manager = TaskManager()
        task1 = manager.add_task("Task 1")
        manager.delete_task(task1.id)

        task2 = manager.add_task("Task 2")

        assert task2.id != task1.id
        assert task2.id > task1.id

    def test_delete_all_tasks(self):
        """Test deleting all tasks results in empty list."""
        manager = TaskManager()
        manager.add_task("Task 1")
        manager.add_task("Task 2")
        manager.add_task("Task 3")

        all_tasks = manager.get_all_tasks()
        for task in all_tasks:
            manager.delete_task(task.id)

        assert len(manager.get_all_tasks()) == 0

    def test_delete_cannot_retrieve_deleted_task(self):
        """Test that deleted task cannot be retrieved."""
        manager = TaskManager()
        task = manager.add_task("Task to delete")

        manager.delete_task(task.id)

        with pytest.raises(TaskNotFoundError):
            manager.get_task(task.id)
