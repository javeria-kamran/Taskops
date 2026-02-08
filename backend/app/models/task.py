"""
Task model for database.

T009: Verify and update Task model for Phase III compatibility
- Add priority field (high, medium, low)
- Add due_date field (optional)
- Ensure created_at and updated_at are present
- Ensure completed boolean field exists
"""

from datetime import datetime
from typing import Optional
from sqlmodel import Field, SQLModel


class Task(SQLModel, table=True):
    """
    Task model representing a user's todo item.

    T009: Enhanced with Phase III fields for MCP tool integration.

    Attributes:
        id: Unique task identifier
        user_id: Foreign key to user who owns this task
        title: Task title (required, 1-200 characters)
        description: Optional task description (max 1000 characters)
        completed: Whether task is completed
        priority: Task priority level (high, medium, low)
        due_date: Optional due date for task
        created_at: Timestamp when task was created (UTC, indexed)
        updated_at: Timestamp when task was last updated
    """

    __tablename__ = "tasks"

    # Primary key
    id: Optional[str] = Field(default=None, primary_key=True)

    # Foreign key - user ownership
    user_id: str = Field(
        foreign_key="users.id",
        index=True,
        nullable=False,
        description="User who owns this task"
    )

    # Task content
    title: str = Field(
        min_length=1,
        max_length=200,
        nullable=False,
        description="Task title"
    )

    description: Optional[str] = Field(
        default=None,
        max_length=1000,
        nullable=True,
        description="Task description"
    )

    # Task status
    completed: bool = Field(
        default=False,
        nullable=False,
        description="Whether task is completed"
    )

    # Task metadata
    priority: str = Field(
        default="medium",
        max_length=20,
        nullable=False,
        description="Task priority: high, medium, low"
    )

    due_date: Optional[datetime] = Field(
        default=None,
        nullable=True,
        description="Optional due date for task"
    )

    # Timestamps (UTC)
    created_at: datetime = Field(
        default_factory=datetime.utcnow,
        nullable=False,
        index=True,
        description="Task creation timestamp"
    )

    updated_at: datetime = Field(
        default_factory=datetime.utcnow,
        nullable=False,
        description="Task last update timestamp"
    )
