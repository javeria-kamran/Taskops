"""
Chat middleware package.

Exports:
- verify_jwt_token: Validate JWT and extract user_id
- get_authenticated_user_id: FastAPI dependency for auth
- create_access_token: Create JWT for testing
"""

from app.chat.middleware.auth import (
    verify_jwt_token,
    get_authenticated_user_id,
    create_access_token,
    InvalidTokenError,
    ExpiredTokenError,
    MissingTokenError
)

__all__ = [
    "verify_jwt_token",
    "get_authenticated_user_id",
    "create_access_token",
    "InvalidTokenError",
    "ExpiredTokenError",
    "MissingTokenError"
]
