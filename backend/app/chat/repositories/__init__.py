"""
Database Repository Layer for Chat Module
T024-T027: Conversation Persistence Service - Repository Pattern

Provides abstraction layer for database operations (CRUD).
Separates data access logic from service/business logic.
No business logic - only database queries.
"""

from typing import Optional, List
from uuid import UUID
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy.orm import selectinload

from app.chat.models.conversation import Conversation
from app.chat.models.message import Message


class ConversationRepository:
    """
    T024: Repository for Conversation CRUD operations.
    Handles all database interactions for conversations.
    """

    def __init__(self, session: AsyncSession):
        """Initialize repository with database session."""
        self.session = session

    async def create_conversation(
        self,
        user_id: str,
        title: Optional[str] = None
    ) -> Conversation:
        """
        T024: Create new conversation.

        Args:
            user_id: UUID of conversation owner
            title: Optional conversation title

        Returns:
            Created Conversation object
        """
        conversation = Conversation(
            user_id=user_id,
            title=title or "New Conversation"
        )
        self.session.add(conversation)
        await self.session.flush()
        return conversation

    async def get_conversation(self, conversation_id: str, user_id: str) -> Optional[Conversation]:
        """
        T025: Retrieve conversation by ID (with user isolation).

        Args:
            conversation_id: Conversation ID
            user_id: User ID (for isolation)

        Returns:
            Conversation or None
        """
        stmt = select(Conversation).where(
            (Conversation.id == conversation_id) &
            (Conversation.user_id == user_id)
        ).options(selectinload(Conversation.messages))

        result = await self.session.execute(stmt)
        return result.scalars().first()

    async def get_user_conversations(
        self,
        user_id: str,
        limit: int = 10,
        offset: int = 0
    ) -> List[Conversation]:
        """
        Get all conversations for a user.

        Args:
            user_id: User ID
            limit: Max conversations to return
            offset: Pagination offset

        Returns:
            List of conversations
        """
        stmt = (
            select(Conversation)
            .where(Conversation.user_id == user_id)
            .order_by(Conversation.updated_at.desc())
            .limit(limit)
            .offset(offset)
        )

        result = await self.session.execute(stmt)
        return result.scalars().all()

    async def update_conversation(
        self,
        conversation_id: str,
        user_id: str,
        title: Optional[str] = None
    ) -> Optional[Conversation]:
        """
        Update conversation metadata.

        Args:
            conversation_id: Conversation ID
            user_id: User ID (for isolation)
            title: New title

        Returns:
            Updated conversation or None
        """
        conversation = await self.get_conversation(conversation_id, user_id)
        if not conversation:
            return None

        if title:
            conversation.title = title

        conversation.updated_at = __import__('datetime').datetime.utcnow()
        await self.session.flush()
        return conversation

    async def delete_conversation(self, conversation_id: str, user_id: str) -> bool:
        """
        T026: Delete conversation (cascades to messages).

        Args:
            conversation_id: Conversation ID
            user_id: User ID (for isolation)

        Returns:
            True if deleted, False if not found
        """
        conversation = await self.get_conversation(conversation_id, user_id)
        if not conversation:
            return False

        await self.session.delete(conversation)
        await self.session.flush()
        return True


class MessageRepository:
    """
    T025-T026: Repository for Message CRUD operations.
    Handles all database interactions for messages.
    """

    def __init__(self, session: AsyncSession):
        """Initialize repository with database session."""
        self.session = session

    async def create_message(
        self,
        conversation_id: str,
        user_id: str,
        role: str,
        content: str,
        tool_calls: Optional[dict] = None
    ) -> Message:
        """
        T026: Create new message in conversation.

        Args:
            conversation_id: Parent conversation ID
            user_id: Message author ID
            role: 'user' or 'assistant'
            content: Message text
            tool_calls: Optional tool invocation data

        Returns:
            Created Message object
        """
        message = Message(
            conversation_id=conversation_id,
            user_id=user_id,
            role=role,
            content=content,
            tool_calls=tool_calls
        )
        self.session.add(message)
        await self.session.flush()
        return message

    async def get_conversation_messages(
        self,
        conversation_id: str,
        user_id: str,
        limit: int = 50
    ) -> List[Message]:
        """
        T025: Get recent messages from conversation (stateless context loading).

        Loads last N messages for agent context (prevents token explosion).
        User isolation verified via conversation ownership check.

        Args:
            conversation_id: Conversation ID
            user_id: User ID (for isolation)
            limit: Max messages to return (default: 50)

        Returns:
            List of messages ordered by creation time
        """
        # First verify user owns this conversation
        conv_stmt = select(Conversation).where(
            (Conversation.id == conversation_id) &
            (Conversation.user_id == user_id)
        )
        conv_result = await self.session.execute(conv_stmt)
        if not conv_result.scalars().first():
            return []  # User doesn't own this conversation

        # Load messages ordered by creation (oldest first for context)
        stmt = (
            select(Message)
            .where(Message.conversation_id == conversation_id)
            .order_by(Message.created_at.asc())
            .limit(limit)
        )

        result = await self.session.execute(stmt)
        return result.scalars().all()

    async def get_message(self, message_id: str, user_id: str) -> Optional[Message]:
        """
        Get single message by ID (with user isolation).

        Args:
            message_id: Message ID
            user_id: User ID (for isolation)

        Returns:
            Message or None
        """
        stmt = select(Message).where(
            (Message.id == message_id) &
            (Message.user_id == user_id)
        )

        result = await self.session.execute(stmt)
        return result.scalars().first()

    async def delete_message(self, message_id: str, user_id: str) -> bool:
        """
        Delete message (soft delete via marking, or hard delete).

        Args:
            message_id: Message ID
            user_id: User ID (for isolation)

        Returns:
            True if deleted, False if not found
        """
        message = await self.get_message(message_id, user_id)
        if not message:
            return False

        await self.session.delete(message)
        await self.session.flush()
        return True
