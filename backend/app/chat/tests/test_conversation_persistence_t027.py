"""
T027: Test Scenario - Conversation Persistence

Minimal functional verification of T024-T026:
1. Create conversation
2. Append messages
3. Retrieve messages in correct order

This is NOT a comprehensive test suite.
Comprehensive tests in Phase 10 (T053-T060).
"""

import pytest
from uuid import UUID
from sqlalchemy.ext.asyncio import AsyncSession

from app.chat.services.conversation_service import ConversationService
from app.chat.models import Conversation, Message


@pytest.mark.asyncio
async def test_conversation_persistence_flow(session: AsyncSession):
    """
    T027: Test scenario for conversation persistence.

    Flow:
    1. User creates conversation
    2. User sends message
    3. User closes chat, reopens
    4. Previous messages visible (retrieved in order)
    """
    user_id = "test-user-123"

    # T024: Create conversation
    conv_id = await ConversationService.create_conversation(
        session,
        user_id=user_id,
        title="Test Conversation"
    )

    assert isinstance(conv_id, UUID)
    assert conv_id is not None
    print(f"[T024] ✓ Created conversation: {conv_id}")

    # T026: Append first user message
    msg1 = await ConversationService.append_message(
        session,
        conversation_id=conv_id,
        user_id=user_id,
        role="user",
        content="What are my tasks?
"
    )

    assert msg1.id is not None
    assert msg1.role == "user"
    assert msg1.content == "What are my tasks?"
    assert msg1.conversation_id == conv_id
    print(f"[T026] ✓ Appended user message: {msg1.id}")

    # T026: Append assistant response
    msg2 = await ConversationService.append_message(
        session,
        conversation_id=conv_id,
        user_id=user_id,
        role="assistant",
        content="You have 3 tasks pending",
        tool_calls={"add_task": []}
    )

    assert msg2.id is not None
    assert msg2.role == "assistant"
    assert msg2.tool_calls is not None
    print(f"[T026] ✓ Appended assistant message: {msg2.id}")

    # T026: Append second user message
    msg3 = await ConversationService.append_message(
        session,
        conversation_id=conv_id,
        user_id=user_id,
        role="user",
        content="Add a new task: buy groceries"
    )

    assert msg3.id is not None
    print(f"[T026] ✓ Appended user message: {msg3.id}")

    # T025: Retrieve messages (simulate "reopening" conversation)
    # Messages should be in chronological order (oldest first)
    messages = await ConversationService.get_recent_messages(
        session,
        conversation_id=conv_id,
        user_id=user_id,
        limit=50
    )

    # Validate retrieval
    assert len(messages) == 3
    assert messages[0].content == "What are my tasks?"
    assert messages[1].content == "You have 3 tasks pending"
    assert messages[2].content == "Add a new task: buy groceries"

    # Validate ordering (created_at ascending)
    assert messages[0].created_at <= messages[1].created_at
    assert messages[1].created_at <= messages[2].created_at

    print(f"[T025] ✓ Retrieved {len(messages)} messages in correct order")

    # T025: Test user isolation (different user can't see messages)
    other_user_id = "other-user-456"
    messages_other = await ConversationService.get_recent_messages(
        session,
        conversation_id=conv_id,
        user_id=other_user_id,
        limit=50
    )

    assert len(messages_other) == 0
    print(f"[T025] ✓ User isolation verified (other user sees 0 messages)")

    # T024: Verify conversation ownership
    conv = await ConversationService.get_conversation(
        session,
        conversation_id=conv_id,
        user_id=user_id
    )
    assert conv is not None
    assert conv.user_id == user_id

    conv_other = await ConversationService.get_conversation(
        session,
        conversation_id=conv_id,
        user_id=other_user_id
    )
    assert conv_other is None
    print(f"[T024] ✓ Conversation ownership verified")

    print("\n[T027] ✓ All conversation persistence tests passed!")
    print("Flow: create → append (3x) → retrieve ordered → verify isolation")
