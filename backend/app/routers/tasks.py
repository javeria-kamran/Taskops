from fastapi import APIRouter, Depends, HTTPException, status
from sqlmodel.ext.asyncio.session import AsyncSession
from sqlmodel import select
from typing import List
import uuid

from app.database import get_session
from app.models.user import User
from app.models.task import Task
from app.schemas.task import TaskCreate, TaskUpdate, TaskResponse
from app.dependencies.auth import get_current_user

router = APIRouter(prefix="/api/tasks", tags=["Tasks"])


@router.post("", status_code=status.HTTP_201_CREATED)
async def create_task(
    task_data: TaskCreate,
    current_user: User = Depends(get_current_user),
    session: AsyncSession = Depends(get_session),
):
    """Create a new task for the authenticated user."""
    task_id = f"task_{uuid.uuid4().hex[:12]}"

    new_task = Task(
        id=task_id,
        user_id=current_user.id,
        title=task_data.title,
        description=task_data.description,
        completed=False,
    )

    session.add(new_task)
    await session.commit()
    await session.refresh(new_task)

    return TaskResponse.model_validate(new_task)


@router.get("", response_model=List[TaskResponse])
async def get_tasks(
    current_user: User = Depends(get_current_user),
    session: AsyncSession = Depends(get_session),
    completed: bool | None = None,
):
    """Get all tasks for the authenticated user."""
    statement = select(Task).where(Task.user_id == current_user.id)

    if completed is not None:
        statement = statement.where(Task.completed == completed)

    statement = statement.order_by(Task.created_at.desc())

    result = await session.execute(statement)
    tasks = result.scalars().all()

    return [TaskResponse.model_validate(task) for task in tasks]


@router.get("/{task_id}", response_model=TaskResponse)
async def get_task(
    task_id: str,
    current_user: User = Depends(get_current_user),
    session: AsyncSession = Depends(get_session),
):
    """Get a specific task by ID."""
    statement = select(Task).where(Task.id == task_id, Task.user_id == current_user.id)
    result = await session.execute(statement)
    task = result.scalar_one_or_none()

    if not task:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Task not found",
        )

    return TaskResponse.model_validate(task)


@router.put("/{task_id}", response_model=TaskResponse)
async def update_task(
    task_id: str,
    task_data: TaskUpdate,
    current_user: User = Depends(get_current_user),
    session: AsyncSession = Depends(get_session),
):
    """Update a task."""
    statement = select(Task).where(Task.id == task_id, Task.user_id == current_user.id)
    result = await session.execute(statement)
    task = result.scalar_one_or_none()

    if not task:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Task not found",
        )

    if task_data.title is not None:
        task.title = task_data.title
    if task_data.description is not None:
        task.description = task_data.description
    if task_data.completed is not None:
        task.completed = task_data.completed

    from datetime import datetime
    task.updated_at = datetime.utcnow()

    session.add(task)
    await session.commit()
    await session.refresh(task)

    return TaskResponse.model_validate(task)


@router.delete("/{task_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_task(
    task_id: str,
    current_user: User = Depends(get_current_user),
    session: AsyncSession = Depends(get_session),
):
    """Delete a task."""
    statement = select(Task).where(Task.id == task_id, Task.user_id == current_user.id)
    result = await session.execute(statement)
    task = result.scalar_one_or_none()

    if not task:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Task not found",
        )

    await session.delete(task)
    await session.commit()

    return None
