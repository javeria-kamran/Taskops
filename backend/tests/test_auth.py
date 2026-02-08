"""
Tests for authentication functionality.
"""

import pytest
from httpx import AsyncClient
from sqlmodel.ext.asyncio.session import AsyncSession
from datetime import datetime, timedelta

from app.dependencies.auth import (
    create_access_token,
    decode_access_token,
    hash_password,
    verify_password,
)
from app.models.user import User


@pytest.fixture
async def test_user(test_session: AsyncSession, test_user_data: dict) -> User:
    """Create a test user in the database."""
    user = User(
        id="test_user_123",
        email=test_user_data["email"],
        name=test_user_data["name"],
        email_verified=False,
    )
    test_session.add(user)
    await test_session.commit()
    await test_session.refresh(user)
    return user


class TestPasswordHashing:
    """Test password hashing and verification."""

    def test_hash_password(self):
        """Test that password hashing works."""
        password = "TestPassword123!"
        hashed = hash_password(password)

        assert hashed != password
        assert len(hashed) > 0
        assert hashed.startswith("$2b$")  # bcrypt prefix

    def test_verify_password_success(self):
        """Test password verification with correct password."""
        password = "TestPassword123!"
        hashed = hash_password(password)

        assert verify_password(password, hashed) is True

    def test_verify_password_failure(self):
        """Test password verification with incorrect password."""
        password = "TestPassword123!"
        wrong_password = "WrongPassword456!"
        hashed = hash_password(password)

        assert verify_password(wrong_password, hashed) is False


class TestJWTTokens:
    """Test JWT token creation and verification."""

    def test_create_access_token(self):
        """Test JWT token creation."""
        data = {"sub": "user_123", "email": "test@example.com"}
        token = create_access_token(data)

        assert token is not None
        assert isinstance(token, str)
        assert len(token) > 0

    def test_create_access_token_with_expiration(self):
        """Test JWT token creation with custom expiration."""
        data = {"sub": "user_123"}
        expires_delta = timedelta(minutes=30)

        token = create_access_token(data, expires_delta=expires_delta)

        assert token is not None
        payload = decode_access_token(token)
        assert payload["sub"] == "user_123"

    def test_decode_access_token_success(self):
        """Test decoding a valid JWT token."""
        data = {"sub": "user_123", "email": "test@example.com"}
        token = create_access_token(data)

        payload = decode_access_token(token)

        assert payload["sub"] == "user_123"
        assert payload["email"] == "test@example.com"
        assert "exp" in payload
        assert "iat" in payload

    def test_decode_access_token_invalid(self):
        """Test decoding an invalid JWT token."""
        from fastapi import HTTPException

        invalid_token = "invalid.token.here"

        with pytest.raises(HTTPException) as exc_info:
            decode_access_token(invalid_token)

        assert exc_info.value.status_code == 401
        assert "Could not validate credentials" in exc_info.value.detail

    def test_decode_expired_token(self):
        """Test decoding an expired JWT token."""
        from fastapi import HTTPException

        data = {"sub": "user_123"}
        # Create token that expired 1 hour ago
        expires_delta = timedelta(hours=-1)
        token = create_access_token(data, expires_delta=expires_delta)

        with pytest.raises(HTTPException) as exc_info:
            decode_access_token(token)

        assert exc_info.value.status_code == 401


class TestUserAuthentication:
    """Test user authentication flow."""

    async def test_get_current_user_with_valid_token(
        self, client: AsyncClient, test_user: User
    ):
        """Test getting current user with valid JWT token."""
        # Create token for test user
        token = create_access_token({"sub": test_user.id, "email": test_user.email})

        # Note: This test will be completed when we add protected endpoints
        # For now, we're testing the token creation and user existence
        assert token is not None
        assert test_user.id is not None

    async def test_get_current_user_with_invalid_token(self, client: AsyncClient):
        """Test getting current user with invalid JWT token."""
        # This will be tested via protected endpoint once implemented
        pass

    async def test_get_current_user_user_not_found(self):
        """Test getting current user when user doesn't exist in database."""
        # Create token for non-existent user
        token = create_access_token({"sub": "nonexistent_user_id"})

        # Decoding should work but database lookup should fail
        payload = decode_access_token(token)
        assert payload["sub"] == "nonexistent_user_id"
        # Full test requires protected endpoint
