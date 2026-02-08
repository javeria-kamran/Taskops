"""
Message Model - Phase III
T008: Create Message SQLModel for message persistence

Stores individual messages within conversations.
Supports user and assistant messages with tool call tracking.

Fields:
- id: UUID primary key
- conversation_id: FK to Conversation (cascade delete)
- user_id: Message author (for isolation)
- role: 'user' or 'assistant'
- content: Message text (max 4096 chars)
- tool_calls: Optional JSONB array of tool invocations
- tokens_used: Optional token count
- created_at: Creation timestamp (UTC, indexed)

Constraints:
- role must be 'user' or 'assistant'
- content max 4096 characters
- Immutable after creation (no updates)

Indexes:
- conversation_id: For history loading
- user_id: For user isolation verification
- created_at: For ordering messages chronologically
"""

from datetime import datetime
from typing import Optional, TYPE_CHECKING
from uuid import UUID, uuid4
from sqlmodel import SQLModel, Field, Relationship, Column
from sqlalchemy import CheckConstraint, JSON, String

if TYPE_CHECKING:
    from app.chat.models.conversation import Conversation


class MessageBase(SQLModel):
    """Base message schema for API requests"""

    conversation_id: UUID = Field(
        foreign_key="conversations.id",
        index=True,
        description="UUID of parent conversation"
    )
    user_id: str = Field(
        index=True,
        description="UUID of message author (for user isolation)"
    )
    role: str = Field(
        description="'user' or 'assistant'"
    )
    content: str = Field(
        description="Message text",
        max_length=4096
    )
    tool_calls: Optional[dict] = Field(
        default=None,
        description="Tool calls executed by agent (JSONB)"
    )
    tokens_used: Optional[int] = Field(
        default=None,
        description="Token count for this message"
    )


class Message(MessageBase, table=True):
    """
    Message table model.

    T008: Message persistence for chat history.
    Supports multi-turn conversations with tool tracking.
    User isolation: Every message tied to user_id.
    Immutable: No updates after creation.
    """

    __tablename__ = "messages"

    # Primary key (UUID)
    id: UUID = Field(
        default_factory=uuid4,
        primary_key=True,
        description="Unique message identifier"
    )

    # Foreign key - conversation relationship
    conversation_id: UUID = Field(
        foreign_key="conversations.id",
        index=True,
        description="Parent conversation ID"
    )

    # User isolation
    user_id: str = Field(
        index=True,
        description="Message author (for user isolation)"
    )

    # Message content
    role: str = Field(
        sa_column=Column(
            "role",
            String,
            CheckConstraint("role IN ('user', 'assistant')")
        ),
        description="Message role: 'user' or 'assistant'"
    )

    content: str = Field(
        max_length=4096,
        description="Message text content"
    )

    # Tool tracking
    tool_calls: Optional[dict] = Field(
        default=None,
        sa_column=Column("tool_calls", JSON),
        description="Tool calls executed by agent (stored as JSONB)"
    )

    tokens_used: Optional[int] = Field(
        default=None,
        description="Token count for this message"
    )

    # Timestamp (indexed for history ordering)
    created_at: datetime = Field(
        default_factory=datetime.utcnow,
        index=True,
        description="Message creation timestamp (UTC)"
    )

    # Relationship
    conversation: "Conversation" = Relationship(
        back_populates="messages"
    )

    class Config:
        """Pydantic configuration."""
        json_encoders = {UUID: str}


class MessageRead(MessageBase):
    """Schema for reading message from API"""

    id: UUID
    created_at: datetime

    class Config:
        """Pydantic configuration."""
        json_encoders = {UUID: str}
