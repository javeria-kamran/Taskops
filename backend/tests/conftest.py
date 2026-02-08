"""
Pytest configuration and fixtures for Todo API tests.

This module provides shared fixtures for testing the Todo application,
including database setup, authentication tokens, and mock data.
"""

import pytest
import pytest_asyncio
from datetime import datetime, timedelta
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker
from unittest.mock import AsyncMock, MagicMock, patch
import uuid
import json

from app.database import Base
from app.chat.middleware.auth import create_access_token
from app.config.settings import settings
from app.chat.services.conversation_service import ConversationService
from app.chat.tools.executor import ToolExecutor


# ==============================================================================
# Database Fixtures
# ==============================================================================

@pytest_asyncio.fixture
async def async_engine():
    """Create an in-memory SQLite database engine for testing."""
    engine = create_async_engine(
        "sqlite+aiosqlite:///:memory:",
        echo=False,
        connect_args={"check_same_thread": False}
    )

    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    yield engine

    await engine.dispose()


@pytest_asyncio.fixture
async def async_session(async_engine):
    """Create an async session factory for the test database."""
    async_session_local = sessionmaker(
        async_engine,
        class_=AsyncSession,
        expire_on_commit=False,
        autocommit=False,
        autoflush=False
    )

    yield async_session_local

    # Cleanup
    await async_engine.dispose()


# ==============================================================================
# User ID Fixtures
# ==============================================================================

@pytest.fixture
def user1_id():
    """Generate a unique user ID for test user 1."""
    return str(uuid.uuid4())


@pytest.fixture
def user2_id():
    """Generate a unique user ID for test user 2."""
    return str(uuid.uuid4())


@pytest.fixture
def user3_id():
    """Generate a unique user ID for test user 3."""
    return str(uuid.uuid4())


# ==============================================================================
# Authentication Token Fixtures
# ==============================================================================

@pytest.fixture
def user1_token(user1_id):
    """Generate a valid access token for test user 1."""
    return create_access_token(
        data={"sub": user1_id, "email": "user1@example.com"},
        expires_delta=timedelta(hours=24)
    )


@pytest.fixture
def user2_token(user2_id):
    """Generate a valid access token for test user 2."""
    return create_access_token(
        data={"sub": user2_id, "email": "user2@example.com"},
        expires_delta=timedelta(hours=24)
    )


@pytest.fixture
def user3_token(user3_id):
    """Generate a valid access token for test user 3."""
    return create_access_token(
        data={"sub": user3_id, "email": "user3@example.com"},
        expires_delta=timedelta(hours=24)
    )


@pytest.fixture
def expired_token(user1_id):
    """Generate an expired access token for testing authentication failures."""
    return create_access_token(
        data={"sub": user1_id, "email": "user1@example.com"},
        expires_delta=timedelta(hours=-1)  # Already expired
    )


@pytest.fixture
def invalid_token():
    """Generate an invalid token for testing authentication failures."""
    return "invalid.token.format"


# ==============================================================================
# Conversation Fixtures
# ==============================================================================

@pytest_asyncio.fixture
async def conversation_user1(async_session, user1_id):
    """Create a test conversation for user 1."""
    async with async_session() as session:
        async with session.begin():
            # Create a conversation using ConversationService
            service = ConversationService(session)
            conversation = await service.create_conversation(
                user_id=user1_id,
                title="Test Conversation 1"
            )
            await session.commit()
            return conversation


@pytest_asyncio.fixture
async def conversation_user2(async_session, user2_id):
    """Create a test conversation for user 2."""
    async with async_session() as session:
        async with session.begin():
            # Create a conversation using ConversationService
            service = ConversationService(session)
            conversation = await service.create_conversation(
                user_id=user2_id,
                title="Test Conversation 2"
            )
            await session.commit()
            return conversation


# ==============================================================================
# Task Fixtures
# ==============================================================================

@pytest_asyncio.fixture
async def task1_user1(async_session, user1_id, conversation_user1):
    """Create a test task for user 1."""
    async with async_session() as session:
        executor = ToolExecutor(session=session)

        # Create a task using ToolExecutor
        task = await executor.execute(
            tool_name="create_task",
            tool_input={
                "user_id": user1_id,
                "conversation_id": conversation_user1.id if hasattr(conversation_user1, 'id') else str(uuid.uuid4()),
                "title": "Test Task 1",
                "description": "Description for test task 1",
                "due_date": (datetime.now() + timedelta(days=1)).isoformat(),
                "priority": "high"
            }
        )
        await session.commit()
        return task


@pytest_asyncio.fixture
async def task2_user1(async_session, user1_id, conversation_user1):
    """Create a second test task for user 1."""
    async with async_session() as session:
        executor = ToolExecutor(session=session)

        # Create a task using ToolExecutor
        task = await executor.execute(
            tool_name="create_task",
            tool_input={
                "user_id": user1_id,
                "conversation_id": conversation_user1.id if hasattr(conversation_user1, 'id') else str(uuid.uuid4()),
                "title": "Test Task 2",
                "description": "Description for test task 2",
                "due_date": (datetime.now() + timedelta(days=2)).isoformat(),
                "priority": "medium"
            }
        )
        await session.commit()
        return task


@pytest_asyncio.fixture
async def task1_user2(async_session, user2_id, conversation_user2):
    """Create a test task for user 2."""
    async with async_session() as session:
        executor = ToolExecutor(session=session)

        # Create a task using ToolExecutor
        task = await executor.execute(
            tool_name="create_task",
            tool_input={
                "user_id": user2_id,
                "conversation_id": conversation_user2.id if hasattr(conversation_user2, 'id') else str(uuid.uuid4()),
                "title": "Test Task for User 2",
                "description": "Description for test task user 2",
                "due_date": (datetime.now() + timedelta(days=3)).isoformat(),
                "priority": "low"
            }
        )
        await session.commit()
        return task


# ==============================================================================
# OpenAI Mock Fixtures
# ==============================================================================

@pytest.fixture
def mock_openai_response():
    """Create a mock OpenAI response without tool calls."""
    return {
        "id": "chatcmpl-test123",
        "object": "chat.completion",
        "created": int(datetime.now().timestamp()),
        "model": "gpt-4",
        "choices": [
            {
                "index": 0,
                "message": {
                    "role": "assistant",
                    "content": "This is a test response from OpenAI."
                },
                "finish_reason": "stop"
            }
        ],
        "usage": {
            "prompt_tokens": 10,
            "completion_tokens": 15,
            "total_tokens": 25
        }
    }


@pytest.fixture
def mock_openai_with_tool_call():
    """Create a mock OpenAI response with a tool call."""
    return {
        "id": "chatcmpl-test456",
        "object": "chat.completion",
        "created": int(datetime.now().timestamp()),
        "model": "gpt-4",
        "choices": [
            {
                "index": 0,
                "message": {
                    "role": "assistant",
                    "content": None,
                    "tool_calls": [
                        {
                            "id": "call_test123",
                            "type": "function",
                            "function": {
                                "name": "create_task",
                                "arguments": json.dumps({
                                    "title": "AI Generated Task",
                                    "description": "Task created by AI",
                                    "priority": "high"
                                })
                            }
                        }
                    ]
                },
                "finish_reason": "tool_calls"
            }
        ],
        "usage": {
            "prompt_tokens": 20,
            "completion_tokens": 30,
            "total_tokens": 50
        }
    }


# ==============================================================================
# Helper Fixtures for HTTP Client
# ==============================================================================

@pytest.fixture
def auth_headers(user1_token):
    """Create authorization headers with a valid token."""
    return {"Authorization": f"Bearer {user1_token}"}


@pytest.fixture
def auth_headers_user2(user2_token):
    """Create authorization headers for user 2."""
    return {"Authorization": f"Bearer {user2_token}"}


@pytest.fixture
def invalid_auth_headers(invalid_token):
    """Create authorization headers with an invalid token."""
    return {"Authorization": f"Bearer {invalid_token}"}


@pytest.fixture
def expired_auth_headers(expired_token):
    """Create authorization headers with an expired token."""
    return {"Authorization": f"Bearer {expired_token}"}
