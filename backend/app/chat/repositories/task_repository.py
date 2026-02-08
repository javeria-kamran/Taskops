"""
Task Repository - Phase III
T012: TaskRepository with CRUD operations

Pure data access layer for Task model.
No business logic - only database CRUD operations.

Methods:
- create(user_id, title, description, priority, due_date) → Task
- get_by_id(task_id, user_id) → Optional[Task]
- list_by_user(user_id, status, limit, offset) → List[Task]
- update(task_id, user_id, updates) → Optional[Task]
- complete(task_id, user_id) → Optional[Task]
- delete(task_id, user_id) → bool

All methods enforce user isolation via user_id parameter.
"""

from typing import Optional, List, Dict, Any
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from datetime import datetime

from app.models.task import Task


class TaskRepository:
    """
    T012: Repository for Task CRUD operations.

    Pure data access layer - NO business logic.
    All methods are database operations only.
    User isolation enforced via user_id parameter.
    """

    def __init__(self, session: AsyncSession):
        """Initialize repository with database session"""
        self.session = session

    async def create(
        self,
        user_id: str,
        title: str,
        description: Optional[str] = None,
        priority: str = "medium",
        due_date: Optional[datetime] = None
    ) -> Task:
        """
        Create new task.

        Args:
            user_id: User UUID
            title: Task title
            description: Optional task description
            priority: Task priority (high, medium, low)
            due_date: Optional due date

        Returns:
            Created Task object
        """
        task = Task(
            user_id=user_id,
            title=title,
            description=description,
            priority=priority,
            due_date=due_date,
            completed=False
        )
        self.session.add(task)
        await self.session.flush()
        return task

    async def get_by_id(
        self,
        task_id: str,
        user_id: str
    ) -> Optional[Task]:
        """
        Get task by ID with user isolation check.

        Args:
            task_id: Task ID
            user_id: User UUID (for isolation check)

        Returns:
            Task or None if not found or user doesn't own it
        """
        stmt = select(Task).where(
            (Task.id == task_id) &
            (Task.user_id == user_id)
        )

        result = await self.session.execute(stmt)
        return result.scalar_one_or_none()

    async def list_by_user(
        self,
        user_id: str,
        status: Optional[str] = None,
        limit: int = 50,
        offset: int = 0
    ) -> List[Task]:
        """
        List user's tasks with optional status filter.

        Args:
            user_id: User UUID
            status: Optional filter - 'open', 'completed', or None (all)
            limit: Max tasks to return
            offset: Pagination offset

        Returns:
            List of Task objects (sorted by created_at descending)
        """
        stmt = select(Task).where(Task.user_id == user_id)

        # Optional status filter
        if status == "completed":
            stmt = stmt.where(Task.completed == True)
        elif status == "open":
            stmt = stmt.where(Task.completed == False)

        stmt = (
            stmt
            .order_by(Task.created_at.desc())
            .limit(limit)
            .offset(offset)
        )

        result = await self.session.execute(stmt)
        return result.scalars().all()

    async def update(
        self,
        task_id: str,
        user_id: str,
        **updates
    ) -> Optional[Task]:
        """
        Update task fields.

        Args:
            task_id: Task ID
            user_id: User UUID (for isolation)
            **updates: Field updates (title, description, priority, due_date)

        Returns:
            Updated Task or None if not found/not owned
        """
        task = await self.get_by_id(task_id, user_id)
        if not task:
            return None

        # Update allowed fields only
        allowed_fields = {'title', 'description', 'priority', 'due_date'}
        for field, value in updates.items():
            if field in allowed_fields:
                setattr(task, field, value)

        task.updated_at = datetime.utcnow()
        self.session.add(task)
        await self.session.flush()
        return task

    async def complete(
        self,
        task_id: str,
        user_id: str
    ) -> Optional[Task]:
        """
        Mark task as completed.

        Args:
            task_id: Task ID
            user_id: User UUID (for isolation)

        Returns:
            Updated Task or None if not found/not owned
        """
        task = await self.get_by_id(task_id, user_id)
        if not task:
            return None

        task.completed = True
        task.updated_at = datetime.utcnow()
        self.session.add(task)
        await self.session.flush()
        return task

    async def delete(
        self,
        task_id: str,
        user_id: str
    ) -> bool:
        """
        Delete task.

        Args:
            task_id: Task ID
            user_id: User UUID (for isolation)

        Returns:
            True if deleted, False if not found/not owned
        """
        task = await self.get_by_id(task_id, user_id)
        if not task:
            return False

        await self.session.delete(task)
        await self.session.flush()
        return True
