"""
CORS middleware configuration.
Handles Cross-Origin Resource Sharing for frontend-backend communication.
"""

from fastapi.middleware.cors import CORSMiddleware
from fastapi import FastAPI

from app.config import settings


def configure_cors(app: FastAPI) -> None:
    """
    Configure CORS middleware for the application.

    Args:
        app: FastAPI application instance
    """
    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.cors_origins,
        allow_credentials=True,
        allow_methods=["GET", "POST", "PUT", "PATCH", "DELETE", "OPTIONS"],
        allow_headers=[
            "Content-Type",
            "Authorization",
            "Accept",
            "Origin",
            "X-Requested-With",
        ],
        expose_headers=["Content-Range", "X-Content-Range"],
        max_age=600,  # Cache preflight requests for 10 minutes
    )
