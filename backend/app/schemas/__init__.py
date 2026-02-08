"""
Base Pydantic schemas for request/response handling.
"""

from pydantic import BaseModel
from typing import Optional, Any
from datetime import datetime


class SuccessResponse(BaseModel):
    """Standard success response schema."""

    success: bool = True
    message: str
    data: Optional[Any] = None


class ErrorResponse(BaseModel):
    """Standard error response schema."""

    success: bool = False
    error: str
    detail: Optional[str] = None
    status_code: int


class TimestampMixin(BaseModel):
    """Mixin for created_at and updated_at timestamps."""

    created_at: datetime
    updated_at: datetime
