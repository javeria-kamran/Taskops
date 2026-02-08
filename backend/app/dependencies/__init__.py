"""
Dependency injection utilities for FastAPI routes.
"""

from app.database import get_session

__all__ = ["get_session"]
