"""Unit tests for Task model."""

import pytest
from datetime import datetime
from src.models.task import Task


class TestTaskCreation:
    """Test Task model creation and validation."""

    def test_create_task_with_required_fields(self):
        """Test creating a task with required fields only."""
        task = Task(id=1, title="Test task")

        assert task.id == 1
        assert task.title == "Test task"
        assert task.description == ""
        assert task.completed is False
        assert isinstance(task.created_at, datetime)

    def test_create_task_with_all_fields(self):
        """Test creating a task with all fields."""
        now = datetime.now()
        task = Task(
            id=1,
            title="Test task",
            description="Test description",
            completed=True,
            created_at=now
        )

        assert task.id == 1
        assert task.title == "Test task"
        assert task.description == "Test description"
        assert task.completed is True
        assert task.created_at == now

    def test_task_auto_created_at(self):
        """Test that created_at is auto-generated if not provided."""
        before = datetime.now()
        task = Task(id=1, title="Test")
        after = datetime.now()

        assert before <= task.created_at <= after

    def test_task_strips_title_whitespace(self):
        """Test that title whitespace is stripped during creation."""
        task = Task(id=1, title="  Task with spaces  ")

        assert task.title == "Task with spaces"

    def test_task_rejects_empty_title(self):
        """Test that empty title raises ValueError."""
        with pytest.raises(ValueError, match="Title cannot be empty"):
            Task(id=1, title="")

        with pytest.raises(ValueError, match="Title cannot be empty"):
            Task(id=1, title="   ")

    def test_task_rejects_long_title(self):
        """Test that title over 200 characters raises ValueError."""
        long_title = "x" * 201

        with pytest.raises(ValueError, match="Title must be 200 characters or less"):
            Task(id=1, title=long_title)

    def test_task_accepts_max_length_title(self):
        """Test that title with exactly 200 characters is accepted."""
        max_title = "x" * 200
        task = Task(id=1, title=max_title)

        assert len(task.title) == 200

    def test_task_rejects_long_description(self):
        """Test that description over 1000 characters raises ValueError."""
        long_description = "x" * 1001

        with pytest.raises(ValueError, match="Description must be 1000 characters or less"):
            Task(id=1, title="Valid", description=long_description)

    def test_task_accepts_max_length_description(self):
        """Test that description with exactly 1000 characters is accepted."""
        max_description = "x" * 1000
        task = Task(id=1, title="Valid", description=max_description)

        assert len(task.description) == 1000

    def test_task_accepts_empty_description(self):
        """Test that empty description is accepted."""
        task = Task(id=1, title="Valid", description="")

        assert task.description == ""


class TestTaskRepresentation:
    """Test Task string representation."""

    def test_task_str_representation(self):
        """Test that Task has a meaningful string representation."""
        task = Task(id=1, title="Test task", description="Description")

        # Task should have some string representation
        str_repr = str(task)
        assert str_repr is not None
        assert len(str_repr) > 0
