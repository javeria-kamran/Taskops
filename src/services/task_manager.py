"""Task management service for todo application.

This module provides the business logic layer for CRUD operations on tasks.
"""

from typing import List, Optional
from src.models.task import Task
from src.lib.exceptions import TaskNotFoundError, ValidationError
from src.lib.validators import validate_title, validate_description


class TaskManager:
    """Service class for managing tasks with in-memory storage.

    Attributes:
        tasks: List of all tasks
        next_id: Counter for generating unique task IDs
    """

    def __init__(self):
        """Initialize TaskManager with empty task list."""
        self.tasks: List[Task] = []
        self.next_id: int = 1

    def add_task(self, title: str, description: str = "") -> Task:
        """Create and add a new task.

        Args:
            title: Task title (1-200 characters, required)
            description: Task description (max 1000 characters, optional)

        Returns:
            The created Task object

        Raises:
            ValidationError: If title or description violate constraints
        """
        # Validate inputs
        validated_title = validate_title(title)
        validated_description = validate_description(description)

        # Create task with auto-generated ID
        task = Task(
            id=self.next_id,
            title=validated_title,
            description=validated_description,
            completed=False
        )

        # Add to list and increment ID counter
        self.tasks.append(task)
        self.next_id += 1

        return task

    def get_all_tasks(self) -> List[Task]:
        """Retrieve all tasks.

        Returns:
            List of all tasks (may be empty)
        """
        return self.tasks.copy()

    def get_task(self, task_id: int) -> Task:
        """Retrieve a specific task by ID.

        Args:
            task_id: The task ID to find

        Returns:
            The Task object

        Raises:
            TaskNotFoundError: If task with given ID doesn't exist
        """
        for task in self.tasks:
            if task.id == task_id:
                return task
        raise TaskNotFoundError(f"Task #{task_id} not found")

    def update_task(self, task_id: int, title: Optional[str] = None,
                   description: Optional[str] = None) -> Task:
        """Update an existing task's title and/or description.

        Args:
            task_id: The task ID to update
            title: New title (if provided, cannot be empty)
            description: New description (if provided)

        Returns:
            The updated Task object

        Raises:
            TaskNotFoundError: If task with given ID doesn't exist
            ValidationError: If new title or description violate constraints
        """
        task = self.get_task(task_id)

        # Update title if provided
        if title is not None:
            validated_title = validate_title(title)
            task.title = validated_title

        # Update description if provided
        if description is not None:
            validated_description = validate_description(description)
            task.description = validated_description

        return task

    def delete_task(self, task_id: int) -> Task:
        """Delete a task by ID.

        Args:
            task_id: The task ID to delete

        Returns:
            The deleted Task object

        Raises:
            TaskNotFoundError: If task with given ID doesn't exist
        """
        task = self.get_task(task_id)
        self.tasks.remove(task)
        return task

    def toggle_complete(self, task_id: int) -> Task:
        """Toggle task completion status (pending ↔ completed).

        Args:
            task_id: The task ID to toggle

        Returns:
            The updated Task object

        Raises:
            TaskNotFoundError: If task with given ID doesn't exist
        """
        task = self.get_task(task_id)
        task.completed = not task.completed
        return task

    def get_task_count(self) -> dict:
        """Get task count statistics.

        Returns:
            Dictionary with total, completed, and pending counts
        """
        total = len(self.tasks)
        completed = sum(1 for task in self.tasks if task.completed)
        pending = total - completed

        return {
            "total": total,
            "completed": completed,
            "pending": pending
        }
