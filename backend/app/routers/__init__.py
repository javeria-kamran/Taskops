"""
API routers for the backend application.
"""

from app.routers.auth import router as auth_router
from app.routers.tasks import router as tasks_router

__all__ = ["auth_router", "tasks_router"]
