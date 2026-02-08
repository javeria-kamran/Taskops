"""
T043: JWT Authentication Middleware

Extracts and validates JWT tokens from request headers.
Validates token signature and expiration.
Passes authenticated user_id to request context.

Security:
- Validates JWT signature
- Checks token expiration
- Returns 401 on invalid/missing token
- Extracts user_id claim
"""

import logging
from typing import Optional
from fastapi import HTTPException, status, Depends
from fastapi.security import HTTPBearer
import jwt
from datetime import datetime

from app.config import settings

logger = logging.getLogger(__name__)

security = HTTPBearer(auto_error=False)


class InvalidTokenError(Exception):
    """Invalid JWT token."""
    pass


class ExpiredTokenError(Exception):
    """Token has expired."""
    pass


class MissingTokenError(Exception):
    """Token missing from request."""
    pass


async def verify_jwt_token(credentials = None) -> str:
    """
    Verify JWT token and extract user_id claim.

    Args:
        credentials: HTTPAuthenticationCredentials from header

    Returns:
        str: user_id extracted from token

    Raises:
        HTTPException: 401 if token is invalid/expired/missing
    """
    if not credentials:
        logger.warning("[T043] Missing authentication token")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Missing authentication token",
            headers={"WWW-Authenticate": "Bearer"}
        )

    token = credentials.credentials

    try:
        # Decode and validate JWT
        payload = jwt.decode(
            token,
            settings.better_auth_secret,
            algorithms=[settings.jwt_algorithm]
        )

        user_id = payload.get("sub")  # 'sub' is standard JWT claim for subject (user)
        if not user_id:
            logger.warning("[T043] Token missing 'sub' (user_id) claim")
            raise InvalidTokenError("Token missing user_id claim")

        logger.debug(f"[T043] Token validated for user {user_id}")
        return user_id

    except jwt.ExpiredSignatureError:
        logger.warning("[T043] Token expired")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token has expired",
            headers={"WWW-Authenticate": "Bearer"}
        )

    except jwt.InvalidSignatureError:
        logger.error("[T043] Invalid token signature")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid token signature",
            headers={"WWW-Authenticate": "Bearer"}
        )

    except jwt.InvalidTokenError as e:
        logger.error(f"[T043] Invalid token: {e}")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid token",
            headers={"WWW-Authenticate": "Bearer"}
        )

    except Exception as e:
        logger.error(f"[T043] Token validation error: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Authentication failed",
            headers={"WWW-Authenticate": "Bearer"}
        )


async def get_authenticated_user_id(credentials = Depends(security)) -> str:
    """
    FastAPI dependency for extracting authenticated user_id.

    Usage in endpoint:
        @router.get("/protected")
        async def protected_endpoint(user_id: str = Depends(get_authenticated_user_id)):
            # user_id is now authenticated

    Args:
        credentials: HTTPBearer credentials from header

    Returns:
        str: Authenticated user_id

    Raises:
        HTTPException: 401 if not authenticated
    """
    return await verify_jwt_token(credentials)


def create_access_token(user_id: str, expires_in_hours: int = 24) -> str:
    """
    Create JWT access token for user.

    Args:
        user_id: User UUID to encode
        expires_in_hours: Token expiration time in hours

    Returns:
        str: JWT token

    Note:
        This is for testing/development.
        In production, tokens should be issued by auth service.
    """
    from datetime import timedelta

    payload = {
        "sub": user_id,  # 'sub' is standard claim for subject
        "iat": datetime.utcnow(),
        "exp": datetime.utcnow() + timedelta(hours=expires_in_hours)
    }

    token = jwt.encode(
        payload,
        settings.better_auth_secret,
        algorithm=settings.jwt_algorithm
    )

    logger.debug(f"[T043] Created access token for user {user_id}")
    return token
