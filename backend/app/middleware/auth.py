"""
Authentication middleware for JWT token verification.
"""

from fastapi import Request, HTTPException, status
from fastapi.responses import JSONResponse
from starlette.middleware.base import BaseHTTPMiddleware
from typing import Callable

from app.dependencies.auth import decode_access_token


class AuthMiddleware(BaseHTTPMiddleware):
    """
    Middleware to verify JWT tokens on protected routes.
    Currently not enforced globally - authentication handled per-route via dependencies.
    """

    async def dispatch(self, request: Request, call_next: Callable):
        """Process request and verify authentication if needed."""

        # Public routes that don't require authentication
        public_routes = [
            "/",
            "/health",
            "/docs",
            "/openapi.json",
            "/redoc",
        ]

        # Skip authentication for public routes
        if request.url.path in public_routes or request.url.path.startswith("/api/auth"):
            return await call_next(request)

        # For protected routes, authentication is handled by route dependencies
        # This middleware is available for future global auth enforcement if needed

        return await call_next(request)


async def auth_exception_handler(request: Request, exc: HTTPException):
    """Handle authentication exceptions with consistent error format."""
    return JSONResponse(
        status_code=exc.status_code,
        content={
            "success": False,
            "error": exc.detail,
            "status_code": exc.status_code,
        },
    )
