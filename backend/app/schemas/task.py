"""
Pydantic schemas for Task request/response validation.
"""

from pydantic import BaseModel, Field, field_validator
from datetime import datetime
from typing import Optional


class TaskCreate(BaseModel):
    """Schema for creating a new task."""

    title: str = Field(min_length=1, max_length=200)
    description: Optional[str] = Field(default=None, max_length=1000)

    @field_validator("title")
    @classmethod
    def validate_title(cls, v: str) -> str:
        """Validate title is not empty or whitespace only."""
        if not v or not v.strip():
            raise ValueError("Title cannot be empty or whitespace only")
        return v.strip()

    @field_validator("description")
    @classmethod
    def validate_description(cls, v: Optional[str]) -> Optional[str]:
        """Validate description if provided."""
        if v is not None:
            if len(v.strip()) == 0:
                return None  # Convert empty string to None
            if len(v) > 1000:
                raise ValueError("Description cannot exceed 1000 characters")
            return v.strip()
        return v


class TaskUpdate(BaseModel):
    """Schema for updating an existing task."""

    title: Optional[str] = Field(default=None, min_length=1, max_length=200)
    description: Optional[str] = Field(default=None, max_length=1000)
    completed: Optional[bool] = None

    @field_validator("title")
    @classmethod
    def validate_title(cls, v: Optional[str]) -> Optional[str]:
        """Validate title if provided."""
        if v is not None:
            if not v or not v.strip():
                raise ValueError("Title cannot be empty or whitespace only")
            return v.strip()
        return v

    @field_validator("description")
    @classmethod
    def validate_description(cls, v: Optional[str]) -> Optional[str]:
        """Validate description if provided."""
        if v is not None:
            if len(v.strip()) == 0:
                return None
            if len(v) > 1000:
                raise ValueError("Description cannot exceed 1000 characters")
            return v.strip()
        return v


class TaskResponse(BaseModel):
    """Schema for task response (includes all fields)."""

    id: str
    user_id: str
    title: str
    description: Optional[str] = None
    completed: bool
    created_at: datetime
    updated_at: datetime

    model_config = {
        "from_attributes": True,
        "json_schema_extra": {
            "example": {
                "id": "task_abc123",
                "user_id": "user_xyz789",
                "title": "Complete project documentation",
                "description": "Write comprehensive docs for the new feature",
                "completed": False,
                "created_at": "2024-12-28T10:00:00Z",
                "updated_at": "2024-12-28T10:00:00Z",
            }
        },
    }
