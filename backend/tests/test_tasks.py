"""
Tests for task management functionality.
"""

import pytest
from httpx import AsyncClient
from sqlmodel.ext.asyncio.session import AsyncSession

from app.models.user import User
from app.models.task import Task
from app.dependencies.auth import create_access_token


@pytest.fixture
async def auth_headers(test_user: User) -> dict:
    """Create authentication headers with JWT token."""
    token = create_access_token({"sub": test_user.id, "email": test_user.email})
    return {"Authorization": f"Bearer {token}"}


@pytest.fixture
async def test_task(test_session: AsyncSession, test_user: User) -> Task:
    """Create a test task in the database."""
    task = Task(
        id="task_test_123",
        user_id=test_user.id,
        title="Test Task",
        description="Test task description",
        completed=False,
    )
    test_session.add(task)
    await test_session.commit()
    await test_session.refresh(task)
    return task


class TestCreateTask:
    """Test POST /api/tasks endpoint."""

    async def test_create_task_success(
        self, client: AsyncClient, auth_headers: dict, test_user: User
    ):
        """Test creating a task with valid data."""
        task_data = {
            "title": "Complete project documentation",
            "description": "Write comprehensive docs for the new feature",
        }

        response = await client.post(
            "/api/tasks",
            json=task_data,
            headers=auth_headers,
        )

        assert response.status_code == 201
        data = response.json()
        assert data["title"] == task_data["title"]
        assert data["description"] == task_data["description"]
        assert data["user_id"] == test_user.id
        assert data["completed"] is False
        assert "id" in data
        assert "created_at" in data
        assert "updated_at" in data

    async def test_create_task_without_description(
        self, client: AsyncClient, auth_headers: dict
    ):
        """Test creating a task without description."""
        task_data = {"title": "Simple task"}

        response = await client.post(
            "/api/tasks",
            json=task_data,
            headers=auth_headers,
        )

        assert response.status_code == 201
        data = response.json()
        assert data["title"] == task_data["title"]
        assert data["description"] is None

    async def test_create_task_unauthorized(self, client: AsyncClient):
        """Test creating a task without authentication."""
        task_data = {"title": "Test task"}

        response = await client.post("/api/tasks", json=task_data)

        assert response.status_code == 403  # HTTPBearer returns 403

    async def test_create_task_invalid_token(self, client: AsyncClient):
        """Test creating a task with invalid token."""
        task_data = {"title": "Test task"}
        headers = {"Authorization": "Bearer invalid_token"}

        response = await client.post("/api/tasks", json=task_data, headers=headers)

        assert response.status_code == 401


class TestTaskValidation:
    """Test task validation rules."""

    async def test_title_required(self, client: AsyncClient, auth_headers: dict):
        """Test that title is required."""
        task_data = {"description": "Description without title"}

        response = await client.post(
            "/api/tasks",
            json=task_data,
            headers=auth_headers,
        )

        assert response.status_code == 422

    async def test_title_not_empty(self, client: AsyncClient, auth_headers: dict):
        """Test that title cannot be empty string."""
        task_data = {"title": "   ", "description": "Test"}

        response = await client.post(
            "/api/tasks",
            json=task_data,
            headers=auth_headers,
        )

        assert response.status_code == 422

    async def test_title_max_length(self, client: AsyncClient, auth_headers: dict):
        """Test that title cannot exceed 200 characters."""
        task_data = {"title": "x" * 201}

        response = await client.post(
            "/api/tasks",
            json=task_data,
            headers=auth_headers,
        )

        assert response.status_code == 422

    async def test_description_max_length(self, client: AsyncClient, auth_headers: dict):
        """Test that description cannot exceed 1000 characters."""
        task_data = {"title": "Test task", "description": "x" * 1001}

        response = await client.post(
            "/api/tasks",
            json=task_data,
            headers=auth_headers,
        )

        assert response.status_code == 422

    async def test_title_trimmed(self, client: AsyncClient, auth_headers: dict):
        """Test that title is trimmed of whitespace."""
        task_data = {"title": "  Test Task  "}

        response = await client.post(
            "/api/tasks",
            json=task_data,
            headers=auth_headers,
        )

        assert response.status_code == 201
        data = response.json()
        assert data["title"] == "Test Task"


class TestUserIsolation:
    """Test user isolation for tasks."""

    async def test_task_has_user_id(
        self, client: AsyncClient, auth_headers: dict, test_user: User
    ):
        """Test that created task has correct user_id."""
        task_data = {"title": "User's task"}

        response = await client.post(
            "/api/tasks",
            json=task_data,
            headers=auth_headers,
        )

        assert response.status_code == 201
        data = response.json()
        assert data["user_id"] == test_user.id

    async def test_different_users_different_tasks(
        self, client: AsyncClient, test_session: AsyncSession, test_user_data: dict
    ):
        """Test that different users create separate tasks."""
        # Create second user
        user2 = User(
            id="user_test_456",
            email="user2@example.com",
            name="User Two",
            email_verified=False,
        )
        test_session.add(user2)
        await test_session.commit()
        await test_session.refresh(user2)

        # Create tokens for both users
        token1 = create_access_token({"sub": "test_user_123", "email": test_user_data["email"]})
        token2 = create_access_token({"sub": user2.id, "email": user2.email})

        headers1 = {"Authorization": f"Bearer {token1}"}
        headers2 = {"Authorization": f"Bearer {token2}"}

        # Create task for user 1
        response1 = await client.post(
            "/api/tasks",
            json={"title": "User 1 task"},
            headers=headers1,
        )

        # Create task for user 2
        response2 = await client.post(
            "/api/tasks",
            json={"title": "User 2 task"},
            headers=headers2,
        )

        assert response1.status_code == 201
        assert response2.status_code == 201

        data1 = response1.json()
        data2 = response2.json()

        # Verify different user_ids
        assert data1["user_id"] == "test_user_123"
        assert data2["user_id"] == user2.id
        assert data1["user_id"] != data2["user_id"]


class TestGetTasks:
    """Test GET /api/tasks endpoint."""

    async def test_get_all_tasks(
        self, client: AsyncClient, auth_headers: dict, test_user: User
    ):
        """Test fetching all tasks for authenticated user."""
        # Create multiple tasks
        tasks_data = [
            {"title": "Task 1", "description": "First task"},
            {"title": "Task 2", "description": "Second task"},
            {"title": "Task 3"},
        ]

        for task_data in tasks_data:
            await client.post("/api/tasks", json=task_data, headers=auth_headers)

        # Fetch all tasks
        response = await client.get("/api/tasks", headers=auth_headers)

        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)
        assert len(data) == 3

        # Verify all tasks belong to the user
        for task in data:
            assert task["user_id"] == test_user.id

    async def test_get_tasks_empty(self, client: AsyncClient, auth_headers: dict):
        """Test fetching tasks when user has no tasks."""
        response = await client.get("/api/tasks", headers=auth_headers)

        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)
        assert len(data) == 0

    async def test_get_tasks_unauthorized(self, client: AsyncClient):
        """Test fetching tasks without authentication."""
        response = await client.get("/api/tasks")

        assert response.status_code == 403

    async def test_get_tasks_with_completed_filter(
        self, client: AsyncClient, auth_headers: dict
    ):
        """Test filtering tasks by completion status."""
        # Create tasks with different completion status
        await client.post(
            "/api/tasks",
            json={"title": "Incomplete task"},
            headers=auth_headers,
        )

        # Create and complete a task
        response = await client.post(
            "/api/tasks",
            json={"title": "Complete task"},
            headers=auth_headers,
        )
        task_id = response.json()["id"]
        await client.put(
            f"/api/tasks/{task_id}",
            json={"completed": True},
            headers=auth_headers,
        )

        # Fetch only incomplete tasks
        response = await client.get("/api/tasks?completed=false", headers=auth_headers)
        assert response.status_code == 200
        incomplete_tasks = response.json()
        assert len(incomplete_tasks) == 1
        assert incomplete_tasks[0]["completed"] is False

        # Fetch only completed tasks
        response = await client.get("/api/tasks?completed=true", headers=auth_headers)
        assert response.status_code == 200
        completed_tasks = response.json()
        assert len(completed_tasks) == 1
        assert completed_tasks[0]["completed"] is True


class TestUserIsolationForGetTasks:
    """Test user isolation when fetching tasks."""

    async def test_user_sees_only_own_tasks(
        self, client: AsyncClient, test_session: AsyncSession, test_user: User
    ):
        """Test that users only see their own tasks."""
        # Create second user
        user2 = User(
            id="user_test_789",
            email="user3@example.com",
            name="User Three",
            email_verified=False,
        )
        test_session.add(user2)
        await test_session.commit()

        # Create tokens
        token1 = create_access_token({"sub": test_user.id, "email": test_user.email})
        token2 = create_access_token({"sub": user2.id, "email": user2.email})

        headers1 = {"Authorization": f"Bearer {token1}"}
        headers2 = {"Authorization": f"Bearer {token2}"}

        # User 1 creates tasks
        await client.post("/api/tasks", json={"title": "User 1 task 1"}, headers=headers1)
        await client.post("/api/tasks", json={"title": "User 1 task 2"}, headers=headers1)

        # User 2 creates tasks
        await client.post("/api/tasks", json={"title": "User 2 task 1"}, headers=headers2)

        # User 1 fetches tasks
        response1 = await client.get("/api/tasks", headers=headers1)
        tasks1 = response1.json()

        # User 2 fetches tasks
        response2 = await client.get("/api/tasks", headers=headers2)
        tasks2 = response2.json()

        # Verify isolation
        assert len(tasks1) == 2
        assert len(tasks2) == 1
        assert all(task["user_id"] == test_user.id for task in tasks1)
        assert all(task["user_id"] == user2.id for task in tasks2)


class TestTaskOrdering:
    """Test task ordering by creation date."""

    async def test_tasks_ordered_by_created_at_desc(
        self, client: AsyncClient, auth_headers: dict
    ):
        """Test that tasks are returned in descending order by creation date."""
        import asyncio

        # Create tasks with small delays to ensure different timestamps
        task1_response = await client.post(
            "/api/tasks",
            json={"title": "First task"},
            headers=auth_headers,
        )
        task1_id = task1_response.json()["id"]

        await asyncio.sleep(0.1)  # Small delay

        task2_response = await client.post(
            "/api/tasks",
            json={"title": "Second task"},
            headers=auth_headers,
        )
        task2_id = task2_response.json()["id"]

        await asyncio.sleep(0.1)  # Small delay

        task3_response = await client.post(
            "/api/tasks",
            json={"title": "Third task"},
            headers=auth_headers,
        )
        task3_id = task3_response.json()["id"]

        # Fetch all tasks
        response = await client.get("/api/tasks", headers=auth_headers)
        tasks = response.json()

        # Verify order (newest first)
        assert tasks[0]["id"] == task3_id
        assert tasks[1]["id"] == task2_id
        assert tasks[2]["id"] == task1_id

        # Verify timestamps are in descending order
        assert tasks[0]["created_at"] >= tasks[1]["created_at"]
        assert tasks[1]["created_at"] >= tasks[2]["created_at"]


class TestUpdateTask:
    """Test PUT /api/tasks/{id} endpoint."""

    async def test_update_task_success(
        self, client: AsyncClient, auth_headers: dict, test_task: Task
    ):
        """Test updating a task with valid data."""
        update_data = {
            "title": "Updated Task Title",
            "description": "Updated task description",
        }

        response = await client.put(
            f"/api/tasks/{test_task.id}",
            json=update_data,
            headers=auth_headers,
        )

        assert response.status_code == 200
        data = response.json()
        assert data["id"] == test_task.id
        assert data["title"] == update_data["title"]
        assert data["description"] == update_data["description"]
        assert data["completed"] == test_task.completed
        assert data["updated_at"] > test_task.updated_at.isoformat()

    async def test_update_task_partial(
        self, client: AsyncClient, auth_headers: dict, test_task: Task
    ):
        """Test updating only title."""
        update_data = {"title": "Only Title Updated"}

        response = await client.put(
            f"/api/tasks/{test_task.id}",
            json=update_data,
            headers=auth_headers,
        )

        assert response.status_code == 200
        data = response.json()
        assert data["title"] == update_data["title"]
        assert data["description"] == test_task.description  # Unchanged

    async def test_update_task_completion(
        self, client: AsyncClient, auth_headers: dict, test_task: Task
    ):
        """Test toggling task completion."""
        update_data = {"completed": True}

        response = await client.put(
            f"/api/tasks/{test_task.id}",
            json=update_data,
            headers=auth_headers,
        )

        assert response.status_code == 200
        data = response.json()
        assert data["completed"] is True

    async def test_update_nonexistent_task(
        self, client: AsyncClient, auth_headers: dict
    ):
        """Test updating a task that doesn't exist."""
        update_data = {"title": "Updated Title"}

        response = await client.put(
            "/api/tasks/nonexistent_id",
            json=update_data,
            headers=auth_headers,
        )

        assert response.status_code == 404
        data = response.json()
        assert "not found" in data["detail"].lower()

    async def test_update_other_users_task(
        self, client: AsyncClient, test_session: AsyncSession, test_task: Task
    ):
        """Test that users cannot update other users' tasks."""
        # Create second user
        user2 = User(
            id="user_test_999",
            email="user4@example.com",
            name="User Four",
            email_verified=False,
        )
        test_session.add(user2)
        await test_session.commit()

        # Create token for user 2
        token2 = create_access_token({"sub": user2.id, "email": user2.email})
        headers2 = {"Authorization": f"Bearer {token2}"}

        # Try to update user 1's task with user 2's credentials
        update_data = {"title": "Hacked Title"}

        response = await client.put(
            f"/api/tasks/{test_task.id}",
            json=update_data,
            headers=headers2,
        )

        assert response.status_code == 404  # Task not found for this user

    async def test_update_task_validation(
        self, client: AsyncClient, auth_headers: dict, test_task: Task
    ):
        """Test task update validation."""
        # Empty title
        response = await client.put(
            f"/api/tasks/{test_task.id}",
            json={"title": "   "},
            headers=auth_headers,
        )
        assert response.status_code == 422

        # Title too long
        response = await client.put(
            f"/api/tasks/{test_task.id}",
            json={"title": "x" * 201},
            headers=auth_headers,
        )
        assert response.status_code == 422

        # Description too long
        response = await client.put(
            f"/api/tasks/{test_task.id}",
            json={"description": "x" * 1001},
            headers=auth_headers,
        )
        assert response.status_code == 422

    async def test_update_task_unauthorized(self, client: AsyncClient, test_task: Task):
        """Test updating task without authentication."""
        response = await client.put(
            f"/api/tasks/{test_task.id}",
            json={"title": "Updated"},
        )

        assert response.status_code == 403


class TestGetSingleTask:
    """Test GET /api/tasks/{id} endpoint."""

    async def test_get_task_by_id(
        self, client: AsyncClient, auth_headers: dict, test_task: Task
    ):
        """Test fetching a specific task by ID."""
        response = await client.get(f"/api/tasks/{test_task.id}", headers=auth_headers)

        assert response.status_code == 200
        data = response.json()
        assert data["id"] == test_task.id
        assert data["title"] == test_task.title
        assert data["description"] == test_task.description

    async def test_get_nonexistent_task(
        self, client: AsyncClient, auth_headers: dict
    ):
        """Test fetching a task that doesn't exist."""
        response = await client.get("/api/tasks/nonexistent_id", headers=auth_headers)

        assert response.status_code == 404

    async def test_get_other_users_task(
        self, client: AsyncClient, test_session: AsyncSession, test_task: Task
    ):
        """Test that users cannot access other users' tasks."""
        # Create second user
        user2 = User(
            id="user_test_888",
            email="user5@example.com",
            name="User Five",
            email_verified=False,
        )
        test_session.add(user2)
        await test_session.commit()

        # Create token for user 2
        token2 = create_access_token({"sub": user2.id, "email": user2.email})
        headers2 = {"Authorization": f"Bearer {token2}"}

        # Try to access user 1's task with user 2's credentials
        response = await client.get(f"/api/tasks/{test_task.id}", headers=headers2)

        assert response.status_code == 404  # Task not found for this user
