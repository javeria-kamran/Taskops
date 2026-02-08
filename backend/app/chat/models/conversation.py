"""
Conversation Model - Phase III
T007: Create Conversation SQLModel for chat persistence

Represents a conversation session between user and AI.
Groups messages into logical chat sessions.

Fields:
- id: UUID primary key
- user_id: Foreign key to user (for isolation)
- title: Conversation title/summary
- created_at: Creation timestamp (UTC)
- updated_at: Last message timestamp (UTC)

Relationships:
- messages: One-to-many relationship to Message model (cascade delete)

Indexes:
- user_id: For fast lookup of user's conversations
- updated_at: For sorting by recency
"""

from datetime import datetime
from typing import Optional, List, TYPE_CHECKING
from uuid import UUID, uuid4
from sqlmodel import SQLModel, Field, Relationship

if TYPE_CHECKING:
    from app.chat.models.message import Message


class ConversationBase(SQLModel):
    """Base conversation schema for API requests"""

    title: Optional[str] = Field(default=None, max_length=256)
    user_id: str = Field(index=True, description="UUID of conversation owner")


class Conversation(ConversationBase, table=True):
    """
    Conversation table model.

    T007: Conversation persistence for multi-turn chats.
    Groups messages into logical sessions.
    User isolation: Every conversation tied to user_id.
    """

    __tablename__ = "conversations"

    # Primary key (UUID)
    id: UUID = Field(
        default_factory=uuid4,
        primary_key=True,
        nullable=False,
        description="Unique conversation identifier"
    )

    # Foreign key - user isolation
    user_id: str = Field(
        foreign_key="users.id",
        nullable=False,
        index=True,
        description="User who owns this conversation"
    )

    # Metadata
    title: str = Field(
        default="New Conversation",
        min_length=1,
        max_length=256,
        nullable=False,
        description="Conversation summary/title"
    )

    # Timestamps (UTC)
    created_at: datetime = Field(
        default_factory=datetime.utcnow,
        nullable=False,
        description="Conversation creation timestamp"
    )

    updated_at: datetime = Field(
        default_factory=datetime.utcnow,
        nullable=False,
        index=True,
        description="Last activity timestamp (updates on new message)"
    )

    # Relationships
    messages: List["Message"] = Relationship(
        back_populates="conversation",
        cascade_delete=True
    )

    class Config:
        """Pydantic configuration."""
        json_encoders = {UUID: str}


class ConversationRead(ConversationBase):
    """Schema for reading conversation from API"""

    id: UUID
    created_at: datetime
    updated_at: datetime

    class Config:
        """Pydantic configuration."""
        json_encoders = {UUID: str}
