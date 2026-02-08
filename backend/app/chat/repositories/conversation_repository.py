"""
Conversation Repository - Phase III
T011: ConversationRepository with CRUD operations

Pure data access layer for Conversation model.
No business logic - only database CRUD operations.

Methods:
- create(user_id, title) → Conversation
- get_by_id(conversation_id, user_id) → Optional[Conversation]
- list_by_user(user_id, limit, offset) → List[Conversation]
- update_title(conversation_id, user_id, title) → Optional[Conversation]
- delete(conversation_id, user_id) → bool

All methods enforce user isolation via user_id parameter.
"""

from typing import Optional, List
from uuid import UUID
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy.orm import selectinload

from app.chat.models.conversation import Conversation


class ConversationRepository:
    """
    T011: Repository for Conversation CRUD operations.

    Pure data access layer - NO business logic.
    All methods are database operations only.
    User isolation enforced via user_id parameter.
    """

    def __init__(self, session: AsyncSession):
        """Initialize repository with database session"""
        self.session = session

    async def create(
        self,
        user_id: str,
        title: Optional[str] = None
    ) -> Conversation:
        """
        Create new conversation.

        Args:
            user_id: User UUID
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

    async def get_by_id(
        self,
        conversation_id: UUID,
        user_id: str
    ) -> Optional[Conversation]:
        """
        Get conversation by ID with user isolation check.

        Args:
            conversation_id: Conversation UUID
            user_id: User UUID (for isolation check)

        Returns:
            Conversation or None if not found or user doesn't own it
        """
        stmt = select(Conversation).where(
            (Conversation.id == conversation_id) &
            (Conversation.user_id == user_id)
        ).options(selectinload(Conversation.messages))

        result = await self.session.execute(stmt)
        return result.scalar_one_or_none()

    async def list_by_user(
        self,
        user_id: str,
        limit: int = 20,
        offset: int = 0
    ) -> List[Conversation]:
        """
        List user's conversations with pagination.

        Args:
            user_id: User UUID
            limit: Max conversations to return
            offset: Pagination offset

        Returns:
            List of Conversation objects (newest first)
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

    async def update_title(
        self,
        conversation_id: UUID,
        user_id: str,
        title: str
    ) -> Optional[Conversation]:
        """
        Update conversation title.

        Args:
            conversation_id: Conversation UUID
            user_id: User UUID (for isolation)
            title: New title

        Returns:
            Updated Conversation or None if not found/not owned
        """
        conversation = await self.get_by_id(conversation_id, user_id)
        if not conversation:
            return None

        conversation.title = title
        self.session.add(conversation)
        await self.session.flush()
        return conversation

    async def delete(
        self,
        conversation_id: UUID,
        user_id: str
    ) -> bool:
        """
        Delete conversation (cascade deletes messages).

        Args:
            conversation_id: Conversation UUID
            user_id: User UUID (for isolation)

        Returns:
            True if deleted, False if not found/not owned
        """
        conversation = await self.get_by_id(conversation_id, user_id)
        if not conversation:
            return False

        await self.session.delete(conversation)
        await self.session.flush()
        return True
