"""
Conversation Service (Phase III)

[FROM TASKS]: T024-T027 - Conversation Persistence
[FROM SPEC]: speckit.specify §FR2

Handles conversation and message persistence with pure database operations.
NO agent orchestration logic allowed in this service.

Architecture:
- ConversationService delegates to ConversationRepository & TaskRepository
- All database I/O through repository layer (no direct SQL)
- User isolation enforced at every operation
- Stateless design: no in-memory state, all data from PostgreSQL

Implemented Methods:
- T024: create_conversation(session, user_id) -> UUID
- T025: get_recent_messages(session, conversation_id, user_id, limit=50) -> List[Message]
- T026: append_message(session, conversation_id, user_id, role, content, tool_calls=None) -> Message
- T027: (test scenario verification - see tests/)
"""

import logging
from typing import List, Optional
from datetime import datetime
from uuid import UUID
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select

from app.chat.models import Conversation, Message
from app.chat.repositories.conversation_repository import ConversationRepository

logger = logging.getLogger(__name__)


class ConversationService:
    """
    Pure database service for conversation persistence.

    T024-T027: Conversation Persistence Implementation

    All methods use repository layer for database operations.
    No business logic - pure data persistence.

    Responsibilities:
    - Create conversations
    - Retrieve conversation history
    - Append messages
    - Ensure user isolation

    NOT responsible for:
    - Agent invocation
    - Tool execution
    - Intent detection
    """

    # ========================================================================
    # T024: Create Conversation
    # ========================================================================

    @staticmethod
    async def create_conversation(
        session: AsyncSession,
        user_id: str,
        title: Optional[str] = None
    ) -> UUID:
        """
        T024: Create new conversation and return conversation_id.

        Creates a new conversation record in the database for the given user.
        Returns the UUID of the created conversation.

        Args:
            session: Async database session (from dependency injection)
            user_id: User UUID (owner of conversation)
            title: Optional conversation title (default: "New Conversation")

        Returns:
            UUID: ID of created conversation

        Raises:
            Exception: If database operation fails

        Design:
        - Uses ConversationRepository for persistence
        - UTC timestamps automatically set by model defaults
        - Commits transaction atomically
        - Returns UUID for downstream use (T025, T026)

        Example:
            session: AsyncSession = (from FastAPI dependency)
            user_id = "550e8400-e29b-41d4-a716-446655440000"
            conv_id = await ConversationService.create_conversation(session, user_id)
            # conv_id: UUID
        """
        try:
            repo = ConversationRepository(session)
            conversation = await repo.create(
                user_id=user_id,
                title=title
            )
            # Commit the transaction
            await session.commit()
            logger.info(f"[T024] Created conversation {conversation.id} for user {user_id}")
            return conversation.id

        except Exception as e:
            logger.error(f"[T024] Failed to create conversation: {e}", exc_info=True)
            await session.rollback()
            raise

    # ========================================================================
    # T025: Get Recent Messages
    # ========================================================================

    @staticmethod
    async def get_recent_messages(
        session: AsyncSession,
        conversation_id: UUID,
        user_id: str,
        limit: int = 50
    ) -> List[Message]:
        """
        T025: Retrieve recent messages from conversation (ordered by created_at ASC).

        Loads conversation history for agent context.
        Messages returned in chronological order (oldest first).
        Enforces user isolation - only returns messages if user owns conversation.

        Args:
            session: Async database session
            conversation_id: UUID of conversation
            user_id: UUID of requesting user (for isolation check)
            limit: Max messages to return (default: 50, must be >= 1)

        Returns:
            List[Message]: Messages in conversation (oldest first)
            Empty list if conversation not found or user doesn't own it

        Design:
        - Validates conversation exists and belongs to user
        - Returns empty list on isolation violation (no error)
        - Limits history to prevent token explosion
        - Stateless: fresh load from DB on each call
        - Ordered by created_at ASC for chronological order

        Example:
            messages = await ConversationService.get_recent_messages(
                session,
                conversation_id=UUID("550e8400-e29b-41d4-a716-446655440000"),
                user_id="550e8400-e29b-41d4-a716-446655440001",
                limit=50
            )
            # messages: List[Message] (oldest to newest)
        """
        try:
            # Verify conversation exists and user owns it
            repo = ConversationRepository(session)
            conversation = await repo.get_by_id(conversation_id, user_id)

            if not conversation:
                logger.warning(
                    f"[T025] Conversation {conversation_id} not found or "
                    f"not owned by user {user_id} (isolation check)"
                )
                return []

            # Query messages in chronological order
            query = (
                select(Message)
                .where(
                    (Message.conversation_id == conversation_id) &
                    (Message.user_id == user_id)  # Double-check isolation
                )
                .order_by(Message.created_at.asc())
                .limit(limit)
            )

            result = await session.execute(query)
            messages = result.scalars().all()

            logger.debug(
                f"[T025] Loaded {len(messages)} messages from conversation "
                f"{conversation_id} (limit: {limit})"
            )
            return messages

        except Exception as e:
            logger.error(
                f"[T025] Failed to get conversation history: {e}",
                exc_info=True
            )
            return []

    # ========================================================================
    # T026: Append Message
    # ========================================================================

    @staticmethod
    async def append_message(
        session: AsyncSession,
        conversation_id: UUID,
        user_id: str,
        role: str,
        content: str,
        tool_calls: Optional[dict] = None,
        tokens_used: Optional[int] = None
    ) -> Message:
        """
        T026: Append message to conversation (transaction-safe).

        Persists a new message atomically.
        Updates conversation.updated_at timestamp.
        Validates role and user isolation.

        Args:
            session: Async database session
            conversation_id: UUID of conversation (FK check enforced by DB)
            user_id: UUID of message author
            role: Message role - must be 'user' or 'assistant'
            content: Message text (max 4096 chars, enforced by model)
            tool_calls: Optional JSONB dict of executed tools
            tokens_used: Optional token count

        Returns:
            Message: Created message object with id, created_at populated

        Raises:
            ValueError: If role not in ('user', 'assistant')
            Exception: If database operation fails

        Design:
        - Validates role before persistence (application-level + DB constraint)
        - Creates message atomically
        - Updates conversation.updated_at for recency tracking
        - Commits transaction
        - Returns full Message object (including id, created_at)
        - User isolation enforced at repository level

        Example:
            message = await ConversationService.append_message(
                session,
                conversation_id=conv_id,
                user_id=user_id,
                role="user",
                content="What are my tasks?",
                tool_calls=None
            )
            # message: Message with id, created_at, etc.
        """
        # Validate role
        if role not in ('user', 'assistant'):
            raise ValueError(f"Invalid role '{role}' - must be 'user' or 'assistant'")

        try:
            # Create message - repository handles persistence
            message = Message(
                conversation_id=conversation_id,
                user_id=user_id,
                role=role,
                content=content,
                tool_calls=tool_calls,
                tokens_used=tokens_used
            )

            session.add(message)

            # Update conversation updated_at timestamp
            repo = ConversationRepository(session)
            conversation = await repo.get_by_id(conversation_id, user_id)

            if not conversation:
                logger.error(
                    f"[T026] Conversation {conversation_id} not found for user {user_id} "
                    f"(user isolation check failed)"
                )
                await session.rollback()
                raise ValueError(
                    f"Conversation {conversation_id} not found or not owned by user"
                )

            # Update conversation timestamp
            conversation.updated_at = datetime.utcnow()
            session.add(conversation)

            # Commit atomically
            await session.commit()
            await session.refresh(message)

            logger.info(
                f"[T026] Appended {role} message {message.id} to conversation "
                f"{conversation_id} (user: {user_id})"
            )
            return message

        except ValueError:
            # Re-raise validation errors
            raise
        except Exception as e:
            logger.error(
                f"[T026] Failed to append message to conversation {conversation_id}: {e}",
                exc_info=True
            )
            await session.rollback()
            raise

    # ========================================================================
    # Helper Methods (Used by Chat Service)
    # ========================================================================

    @staticmethod
    async def get_conversation(
        session: AsyncSession,
        conversation_id: UUID,
        user_id: str
    ) -> Optional[Conversation]:
        """
        Get conversation by ID (with user isolation).

        Used to verify conversation exists before operations.

        Args:
            session: Async database session
            conversation_id: UUID of conversation
            user_id: UUID of requesting user (for isolation)

        Returns:
            Conversation or None if not found/not owned
        """
        repo = ConversationRepository(session)
        return await repo.get_by_id(conversation_id, user_id)

    @staticmethod
    async def get_user_conversations(
        session: AsyncSession,
        user_id: str,
        limit: int = 20
    ) -> List[Conversation]:
        """
        Get all conversations for a user (most recent first).

        Used by conversation list endpoint.

        Args:
            session: Async database session
            user_id: UUID of user
            limit: Max conversations to return

        Returns:
            List of user's conversations (newest first)
        """
        repo = ConversationRepository(session)
        return await repo.list_by_user(user_id, limit=limit)

    @staticmethod
    async def update_conversation_title(
        session: AsyncSession,
        conversation_id: UUID,
        user_id: str,
        title: str
    ) -> Optional[Conversation]:
        """
        Update conversation title.

        Used by conversation settings endpoint.

        Args:
            session: Async database session
            conversation_id: UUID of conversation
            user_id: UUID of user (isolation check)
            title: New title

        Returns:
            Updated Conversation or None if not found/not owned
        """
        try:
            repo = ConversationRepository(session)
            conversation = await repo.update_title(conversation_id, user_id, title)
            await session.commit()
            return conversation
        except Exception as e:
            logger.error(f"Failed to update conversation title: {e}")
            await session.rollback()
            raise
