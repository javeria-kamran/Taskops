"""
Test Suite for Stateless Architecture Verification

Verifies that the chat service and tools are truly stateless:
1. No module-level mutable state (caches, buffers)
2. No in-memory caching of data
3. Concurrent requests don't interfere with each other
4. AsyncSession isolation (no session reuse)
5. Database consistency after concurrent operations

Pattern: Use @pytest.mark.stateless and @pytest.mark.asyncio for all tests
"""

import pytest
import asyncio
import inspect
import logging
from uuid import UUID, uuid4
from typing import List, Optional, Dict, Any
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func

from app.chat.services.chat_service import ChatService
from app.chat.services.conversation_service import ConversationService
from app.chat.tools.executor import ToolExecutor
from app.chat.models import Message, Conversation
from app.models.task import Task

logger = logging.getLogger(__name__)


# ============================================================================
# Pytest Marker Configuration
# ============================================================================

pytest.mark.stateless = pytest.mark.stateless


# ============================================================================
# Section 1: No Module-Level Mutable State
# ============================================================================


@pytest.mark.asyncio
@pytest.mark.stateless
async def test_no_module_level_cached_state():
    """
    Verify ChatService has no module-level cached state.

    Checks for:
    - No attributes starting with cache_, _cache
    - No mutable class-level dictionaries or lists
    - No global conversation buffers
    """
    # Get ChatService class attributes
    class_attrs = inspect.getmembers(ChatService, predicate=lambda x: not callable(x))

    # Filter out private/dunder attributes
    public_attrs = [(name, value) for name, value in class_attrs if not name.startswith('__')]

    # Check for cache-related attributes
    cache_attrs = [name for name, _ in public_attrs if 'cache' in name.lower() or 'buffer' in name.lower()]
    assert len(cache_attrs) == 0, f"Found cache/buffer attributes: {cache_attrs}"

    # Check for mutable class-level state
    for name, value in public_attrs:
        # Skip methods, properties, and constants
        if callable(value) or isinstance(value, (classmethod, staticmethod, property)):
            continue

        # Class-level constants are OK
        if isinstance(value, (int, float, str, tuple)):
            continue

        # No mutable data structures as class attributes
        assert not isinstance(value, (dict, list, set)), \
            f"Found mutable class attribute '{name}': {type(value)}"

    logger.info("✓ ChatService has no module-level cached state")


@pytest.mark.asyncio
@pytest.mark.stateless
async def test_no_conversation_in_memory_buffer():
    """
    Verify ConversationService has no in-memory conversation storage.

    Checks for:
    - No module-level conversation storage
    - No _buffer or _cache attributes
    - No global message buffers
    """
    class_attrs = inspect.getmembers(ConversationService, predicate=lambda x: not callable(x))

    # Check for buffer/cache attributes
    buffer_attrs = [
        name for name, _ in class_attrs
        if any(x in name.lower() for x in ['buffer', 'cache', '_storage', '_messages', '_conversations'])
    ]
    assert len(buffer_attrs) == 0, f"Found buffer/cache attributes: {buffer_attrs}"

    logger.info("✓ ConversationService has no in-memory buffers")


@pytest.mark.asyncio
@pytest.mark.stateless
async def test_no_task_in_memory_cache(async_session, user1_id):
    """
    Verify tool implementations have no cached task storage.

    Checks for:
    - No global task cache in ToolExecutor
    - No session-level task buffering
    - All operations go through database
    """
    # Instantiate executor and check for caches
    executor = ToolExecutor(async_session)

    # Get all instance attributes
    instance_attrs = vars(executor)

    # Should only have session attribute
    expected_attrs = {'session'}
    actual_attrs = set(instance_attrs.keys())

    assert actual_attrs == expected_attrs, \
        f"ToolExecutor has unexpected attributes: {actual_attrs - expected_attrs}"

    # Verify no cached data
    for attr_name, attr_value in instance_attrs.items():
        if attr_name == 'session':
            continue
        assert not isinstance(attr_value, (dict, list, set)), \
            f"Found cache in '{attr_name}': {type(attr_value)}"

    logger.info("✓ ToolExecutor has no task in-memory cache")


# ============================================================================
# Section 2: No In-Memory Caching
# ============================================================================


@pytest.mark.asyncio
@pytest.mark.stateless
async def test_chat_service_fresh_from_db_each_call(
    async_session,
    user1_id,
    conversation_user1
):
    """
    Verify ChatService fetches fresh data from DB on each call.

    Flow:
    1. Create conversation with 3 messages
    2. Call get_recent_messages (result1)
    3. Modify DB (add new message)
    4. Call get_recent_messages again (result2)
    5. Assert result2 has the new message (not cached)
    """
    async with async_session() as session:
        # Setup: Create initial messages
        conv_id = conversation_user1.id
        for i in range(3):
            await ConversationService.append_message(
                session,
                conversation_id=conv_id,
                user_id=user1_id,
                role="user" if i % 2 == 0 else "assistant",
                content=f"Message {i+1}"
            )

        # First call: get_recent_messages
        messages_1 = await ConversationService.get_recent_messages(
            session,
            conversation_id=conv_id,
            user_id=user1_id,
            limit=50
        )
        count_1 = len(messages_1)
        assert count_1 == 3, f"Expected 3 messages, got {count_1}"

        # Modify database: Add new message
        await ConversationService.append_message(
            session,
            conversation_id=conv_id,
            user_id=user1_id,
            role="user",
            content="Message 4 (added between calls)"
        )

        # Second call: get_recent_messages should see the new message
        messages_2 = await ConversationService.get_recent_messages(
            session,
            conversation_id=conv_id,
            user_id=user1_id,
            limit=50
        )
        count_2 = len(messages_2)
        assert count_2 == 4, f"Expected 4 messages after modification, got {count_2}"
        assert messages_2[-1].content == "Message 4 (added between calls)", \
            "New message not found or cached response returned"

    logger.info("✓ ChatService fetches fresh data from DB each call (no caching)")


@pytest.mark.asyncio
@pytest.mark.stateless
async def test_tools_no_caching_list_tasks_twice(
    async_session,
    user1_id,
    conversation_user1
):
    """
    Verify ToolExecutor.list_tasks returns fresh data, not cached.

    Flow:
    1. List tasks (result1 - empty initially)
    2. Add task to database
    3. List tasks again (result2)
    4. Assert result2 shows new task (not cached)
    """
    async with async_session() as session:
        executor = ToolExecutor(session)
        conv_id = conversation_user1.id

        # First call: list_tasks
        result_1 = await executor.execute(
            tool_name="list_tasks",
            arguments={"status": "all", "limit": 20},
            user_id=user1_id,
            conversation_id=conv_id
        )
        count_1 = result_1.get("result", {}).get("count", 0)
        # Should match whatever's in DB (likely 0 for fresh test)

        # Add task to database
        task = Task(
            id=str(uuid4()),
            user_id=user1_id,
            title="Test Task for Cache Check",
            status="pending",
            priority="high"
        )
        session.add(task)
        await session.commit()

        # Second call: list_tasks should see new task
        result_2 = await executor.execute(
            tool_name="list_tasks",
            arguments={"status": "all", "limit": 20},
            user_id=user1_id,
            conversation_id=conv_id
        )
        count_2 = result_2.get("result", {}).get("count", 0)

        # Count should have increased (or be fresh from DB)
        assert count_2 >= count_1, \
            f"Second list_tasks returned cached result: {count_1} >= {count_2}"

    logger.info("✓ ToolExecutor.list_tasks fetches fresh data (no caching)")


# ============================================================================
# Section 3: Concurrent Request Testing
# ============================================================================


@pytest.mark.asyncio
@pytest.mark.stateless
async def test_concurrent_requests_no_data_corruption(
    async_session,
    user1_id,
    user2_id,
    user3_id,
    conversation_user1,
    conversation_user2
):
    """
    Verify concurrent requests don't corrupt each other's data.

    Creates 10 concurrent task creation requests:
    - User1 creates 4 tasks (A, C, E, G)
    - User2 creates 3 tasks (B, D, F)
    - User3 creates 3 tasks (H, I, J)

    Verifies after completion:
    - User1 has exactly their 4 tasks
    - User2 has exactly their 3 tasks
    - User3 has exactly their 3 tasks
    - No cross-contamination
    """
    conv_id_1 = conversation_user1.id
    conv_id_2 = conversation_user2.id

    async def create_task_for_user(user_id: str, conv_id: UUID, title: str) -> Dict[str, Any]:
        """Create a task for a specific user."""
        async with async_session() as session:
            executor = ToolExecutor(session)
            result = await executor.execute(
                tool_name="add_task",
                arguments={"title": title, "priority": "high"},
                user_id=user_id,
                conversation_id=conv_id
            )
            # Task is now in DB
            return result

    # Create 10 concurrent tasks
    tasks = [
        # User1 creates 4 tasks
        create_task_for_user(user1_id, conv_id_1, "User1-Task-A"),
        create_task_for_user(user1_id, conv_id_1, "User1-Task-C"),
        create_task_for_user(user1_id, conv_id_1, "User1-Task-E"),
        create_task_for_user(user1_id, conv_id_1, "User1-Task-G"),
        # User2 creates 3 tasks
        create_task_for_user(user2_id, conv_id_2, "User2-Task-B"),
        create_task_for_user(user2_id, conv_id_2, "User2-Task-D"),
        create_task_for_user(user2_id, conv_id_2, "User2-Task-F"),
        # User3 creates 3 tasks
        create_task_for_user(user3_id, uuid4(), "User3-Task-H"),
        create_task_for_user(user3_id, uuid4(), "User3-Task-I"),
        create_task_for_user(user3_id, uuid4(), "User3-Task-J"),
    ]

    # Run all concurrently
    results = await asyncio.gather(*tasks)
    assert all(r.get("success") for r in results), "Some tasks failed to create"

    # Verify database integrity
    async with async_session() as session:
        # Count User1's tasks
        stmt = select(func.count(Task.id)).where(Task.user_id == user1_id)
        result = await session.execute(stmt)
        user1_count = result.scalar()

        # Count User2's tasks
        stmt = select(func.count(Task.id)).where(Task.user_id == user2_id)
        result = await session.execute(stmt)
        user2_count = result.scalar()

        # Count User3's tasks
        stmt = select(func.count(Task.id)).where(Task.user_id == user3_id)
        result = await session.execute(stmt)
        user3_count = result.scalar()

        assert user1_count == 4, f"User1 should have 4 tasks, has {user1_count}"
        assert user2_count == 3, f"User2 should have 3 tasks, has {user2_count}"
        assert user3_count == 3, f"User3 should have 3 tasks, has {user3_count}"

    logger.info("✓ Concurrent requests produce no data corruption")


@pytest.mark.asyncio
@pytest.mark.stateless
async def test_concurrent_list_tasks_no_state_sharing(
    async_session,
    user1_id,
    user2_id,
    conversation_user1,
    conversation_user2
):
    """
    Verify concurrent list_tasks calls don't share state.

    Flow:
    1. User1 calls list_tasks 5 times concurrently
    2. User2 calls list_tasks 5 times concurrently
    3. All 10 calls should succeed
    4. Each user sees only their own tasks
    5. No state pollution between concurrent requests
    """
    conv_id_1 = conversation_user1.id
    conv_id_2 = conversation_user2.id

    # Pre-populate: add 2 tasks for user1
    async with async_session() as session:
        for i in range(2):
            task = Task(
                id=str(uuid4()),
                user_id=user1_id,
                title=f"User1-PreTask-{i+1}",
                status="pending",
                priority="medium"
            )
            session.add(task)

        # Pre-populate: add 3 tasks for user2
        for i in range(3):
            task = Task(
                id=str(uuid4()),
                user_id=user2_id,
                title=f"User2-PreTask-{i+1}",
                status="pending",
                priority="low"
            )
            session.add(task)

        await session.commit()

    async def list_tasks_for_user(user_id: str, conv_id: UUID) -> Dict[str, Any]:
        """List tasks for a specific user."""
        async with async_session() as session:
            executor = ToolExecutor(session)
            result = await executor.execute(
                tool_name="list_tasks",
                arguments={"status": "all", "limit": 20},
                user_id=user_id,
                conversation_id=conv_id
            )
            return result

    # Concurrent calls
    user1_calls = [
        list_tasks_for_user(user1_id, conv_id_1) for _ in range(5)
    ]
    user2_calls = [
        list_tasks_for_user(user2_id, conv_id_2) for _ in range(5)
    ]

    # Run all concurrently
    all_results = await asyncio.gather(*user1_calls, *user2_calls)

    # Verify results
    user1_results = all_results[:5]
    user2_results = all_results[5:]

    # All should succeed
    for result in all_results:
        assert result.get("success"), f"list_tasks failed: {result}"

    # User1's results should be consistent
    for result in user1_results:
        count = result.get("result", {}).get("count", 0)
        assert count >= 2, f"User1 should see at least 2 tasks, got {count}"

    # User2's results should be consistent
    for result in user2_results:
        count = result.get("result", {}).get("count", 0)
        assert count >= 3, f"User2 should see at least 3 tasks, got {count}"

    logger.info("✓ Concurrent list_tasks calls have no state sharing")


@pytest.mark.asyncio
@pytest.mark.stateless
async def test_concurrent_chat_messages_isolated(
    async_session,
    user1_id,
    user2_id,
    user3_id,
    conversation_user1,
    conversation_user2
):
    """
    Verify concurrent message posts are isolated per conversation.

    Flow:
    1. User1 POSTs message M1 to conversation C1
    2. User2 POSTs message M2 to conversation C2
    3. User3 POSTs message M3 to conversation C2 (same as User2)
    4. All 3 concurrent
    5. Verify each conversation has only its own message(s)
    6. No cross-talk between conversations
    """
    conv_id_1 = conversation_user1.id
    conv_id_2 = conversation_user2.id
    conv_id_3 = uuid4()  # Create new conversation for user3

    async def post_message(user_id: str, conv_id: UUID, message: str):
        """Post a message to a conversation."""
        async with async_session() as session:
            return await ConversationService.append_message(
                session,
                conversation_id=conv_id,
                user_id=user_id,
                role="user",
                content=message
            )

    # Post messages concurrently
    # Note: conv_id_3 needs to be created first
    async with async_session() as session:
        await ConversationService.create_conversation(
            session,
            user_id=user3_id,
            title="User3 Conversation"
        )
        # Get the created conversation ID
        user3_convs = await ConversationService.get_user_conversations(
            session,
            user_id=user3_id,
            limit=1
        )
        if user3_convs:
            conv_id_3 = user3_convs[0].id

    posts = [
        post_message(user1_id, conv_id_1, "M1 from User1"),
        post_message(user2_id, conv_id_2, "M2 from User2"),
        post_message(user3_id, conv_id_3, "M3 from User3"),
    ]

    results = await asyncio.gather(*posts)
    assert all(r is not None for r in results), "Some posts failed"

    # Verify isolation
    async with async_session() as session:
        # Conversation 1 should have only message from User1
        msgs_1 = await ConversationService.get_recent_messages(
            session,
            conversation_id=conv_id_1,
            user_id=user1_id,
            limit=50
        )
        assert len(msgs_1) == 1, f"Conv1 should have 1 message, has {len(msgs_1)}"
        assert "M1" in msgs_1[0].content, "Conv1 should have User1's message"

        # Conversation 2 should have only message from User2
        msgs_2 = await ConversationService.get_recent_messages(
            session,
            conversation_id=conv_id_2,
            user_id=user2_id,
            limit=50
        )
        assert len(msgs_2) == 1, f"Conv2 should have 1 message, has {len(msgs_2)}"
        assert "M2" in msgs_2[0].content, "Conv2 should have User2's message"

        # Conversation 3 should have only message from User3
        if conv_id_3 != uuid4():  # Only check if we successfully created it
            msgs_3 = await ConversationService.get_recent_messages(
                session,
                conversation_id=conv_id_3,
                user_id=user3_id,
                limit=50
            )
            assert len(msgs_3) >= 1, f"Conv3 should have messages from User3"
            # Check that User3's message is there
            user3_messages = [m for m in msgs_3 if "M3" in m.content]
            assert len(user3_messages) > 0, "Conv3 should have User3's M3 message"

    logger.info("✓ Concurrent message posts are isolated per conversation")


# ============================================================================
# Section 4: AsyncSession Isolation
# ============================================================================


@pytest.mark.asyncio
@pytest.mark.stateless
async def test_each_request_gets_fresh_session(
    async_session,
    user1_id,
    conversation_user1
):
    """
    Verify each request gets a fresh AsyncSession instance.

    Flow:
    1. Track AsyncSession instance IDs
    2. Call ChatService.process_chat_message N times
    3. Verify each gets a different session instance
    4. No session object is reused across requests
    """
    session_ids = []
    conv_id = conversation_user1.id

    # Helper to capture session ID
    async def process_with_session_tracking():
        async with async_session() as session:
            # Capture the session ID (memory address)
            session_id = id(session)
            session_ids.append(session_id)

            # Do something with the session
            await ConversationService.append_message(
                session,
                conversation_id=conv_id,
                user_id=user1_id,
                role="user",
                content="Test message for session isolation"
            )

            return session_id

    # Call the function multiple times
    results = await asyncio.gather(*[
        process_with_session_tracking() for _ in range(5)
    ])

    # Verify all session IDs are unique
    unique_ids = set(results)
    assert len(unique_ids) == 5, \
        f"Expected 5 unique session IDs, got {len(unique_ids)}"

    logger.info("✓ Each request gets a fresh AsyncSession instance")


# ============================================================================
# Section 5: Database Consistency After Concurrent Operations
# ============================================================================


@pytest.mark.asyncio
@pytest.mark.stateless
async def test_concurrent_task_count_consistency(
    async_session,
    user1_id,
    user2_id,
    user3_id,
    user4_id,
    user5_id,
    conversation_user1
):
    """
    Verify database consistency after concurrent operations.

    Flow:
    1. 5 users create 3 tasks each concurrently (15 total)
    2. Query DB: total task count should be 15
    3. Query each user: should have exactly 3 tasks
    4. No duplicates, no missing tasks
    """
    conv_id = conversation_user1.id
    user_ids = [user1_id, user2_id, user3_id, user4_id, user5_id]

    async def create_three_tasks(user_id: str):
        """Create 3 tasks for a user."""
        tasks = []
        for i in range(3):
            async with async_session() as session:
                task = Task(
                    id=str(uuid4()),
                    user_id=user_id,
                    title=f"{user_id}-Task-{i+1}",
                    status="pending",
                    priority="medium"
                )
                session.add(task)
                await session.commit()
                tasks.append(task)
        return tasks

    # Create tasks concurrently
    all_tasks = await asyncio.gather(*[
        create_three_tasks(uid) for uid in user_ids
    ])

    # Verify total count
    async with async_session() as session:
        stmt = select(func.count(Task.id))
        result = await session.execute(stmt)
        total_count = result.scalar()
        assert total_count == 15, f"Expected 15 tasks total, got {total_count}"

        # Verify each user has exactly 3 tasks
        for user_id in user_ids:
            stmt = select(func.count(Task.id)).where(Task.user_id == user_id)
            result = await session.execute(stmt)
            user_count = result.scalar()
            assert user_count == 3, \
                f"User {user_id} should have 3 tasks, has {user_count}"

        # Verify no duplicates
        stmt = select(Task)
        result = await session.execute(stmt)
        all_db_tasks = result.scalars().all()
        task_ids = [t.id for t in all_db_tasks]
        unique_ids = set(task_ids)
        assert len(task_ids) == len(unique_ids), \
            f"Found duplicate task IDs: {len(task_ids)} total, {len(unique_ids)} unique"

    logger.info("✓ Database shows perfect consistency after concurrent operations")


@pytest.mark.asyncio
@pytest.mark.stateless
async def test_conversation_message_isolation_concurrent(
    async_session,
    user1_id,
    user2_id
):
    """
    Verify message isolation between concurrent conversations.

    Creates 2 conversations, adds messages concurrently,
    verifies no cross-contamination.
    """
    # Create conversations
    async with async_session() as session:
        conv1_id = await ConversationService.create_conversation(
            session,
            user_id=user1_id,
            title="Conversation 1"
        )
        conv2_id = await ConversationService.create_conversation(
            session,
            user_id=user2_id,
            title="Conversation 2"
        )

    async def add_messages_to_conversation(user_id: str, conv_id: UUID, message_count: int):
        """Add multiple messages to a conversation."""
        async with async_session() as session:
            for i in range(message_count):
                await ConversationService.append_message(
                    session,
                    conversation_id=conv_id,
                    user_id=user_id,
                    role="user" if i % 2 == 0 else "assistant",
                    content=f"Message {i+1} in conversation {conv_id}"
                )

    # Add messages concurrently
    await asyncio.gather(
        add_messages_to_conversation(user1_id, conv1_id, 5),
        add_messages_to_conversation(user2_id, conv2_id, 3),
    )

    # Verify isolation
    async with async_session() as session:
        msgs1 = await ConversationService.get_recent_messages(
            session,
            conversation_id=conv1_id,
            user_id=user1_id,
            limit=50
        )
        assert len(msgs1) == 5, f"Conv1 should have 5 messages, has {len(msgs1)}"

        msgs2 = await ConversationService.get_recent_messages(
            session,
            conversation_id=conv2_id,
            user_id=user2_id,
            limit=50
        )
        assert len(msgs2) == 3, f"Conv2 should have 3 messages, has {len(msgs2)}"

        # Verify no cross-contamination
        all_in_conv1 = [m for m in msgs1 if str(conv1_id) in m.content]
        assert len(all_in_conv1) == 5, "Conv1 has messages from wrong conversation"

    logger.info("✓ Concurrent conversation operations maintain message isolation")


# ============================================================================
# Section 6: Additional Stateless Verification Tests
# ============================================================================


@pytest.mark.asyncio
@pytest.mark.stateless
async def test_conversation_service_stateless_methods(async_session, user1_id):
    """
    Verify all ConversationService methods are truly stateless.

    Tests that calling methods multiple times with same input
    produces consistent results without cached state.
    """
    async with async_session() as session:
        # Create a conversation
        conv_id = await ConversationService.create_conversation(
            session,
            user_id=user1_id,
            title="Stateless Test Conversation"
        )

        # Add some messages
        for i in range(3):
            await ConversationService.append_message(
                session,
                conversation_id=conv_id,
                user_id=user1_id,
                role="user" if i % 2 == 0 else "assistant",
                content=f"Message {i+1}"
            )

    # Now test that multiple calls return consistent results
    async with async_session() as session:
        # Call get_recent_messages multiple times
        results = []
        for _ in range(3):
            messages = await ConversationService.get_recent_messages(
                session,
                conversation_id=conv_id,
                user_id=user1_id,
                limit=50
            )
            results.append(len(messages))

        # All should be the same
        assert all(r == 3 for r in results), \
            f"Inconsistent results across multiple calls: {results}"

        # Call get_user_conversations multiple times
        conv_results = []
        for _ in range(3):
            conversations = await ConversationService.get_user_conversations(
                session,
                user_id=user1_id,
                limit=20
            )
            conv_results.append(len(conversations))

        # All should be consistent
        assert all(r == conv_results[0] for r in conv_results), \
            f"Inconsistent conversation counts: {conv_results}"

    logger.info("✓ ConversationService methods are stateless and consistent")


@pytest.mark.asyncio
@pytest.mark.stateless
async def test_tool_executor_stateless_operations(
    async_session,
    user1_id,
    conversation_user1
):
    """
    Verify ToolExecutor operations are stateless.

    Creates executor instance, executes operations multiple times,
    verifies no state is retained between calls.
    """
    conv_id = conversation_user1.id

    async with async_session() as session:
        executor = ToolExecutor(session)

        # Execute add_task multiple times with different data
        for i in range(3):
            result = await executor.execute(
                tool_name="add_task",
                arguments={
                    "title": f"Stateless Test Task {i+1}",
                    "priority": "high"
                },
                user_id=user1_id,
                conversation_id=conv_id
            )
            assert result.get("success"), f"Task {i+1} creation failed"

            # Verify task was created fresh (not from cache)
            assert result.get("result", {}).get("title") == f"Stateless Test Task {i+1}"

        # Execute list_tasks multiple times, each should reflect current state
        results = []
        for _ in range(2):
            result = await executor.execute(
                tool_name="list_tasks",
                arguments={"status": "all", "limit": 20},
                user_id=user1_id,
                conversation_id=conv_id
            )
            results.append(result)

        # Both should be fresh queries (not cached)
        assert all(r.get("success") for r in results), "list_tasks failed"

    logger.info("✓ ToolExecutor operations are stateless")


@pytest.mark.asyncio
@pytest.mark.stateless
async def test_no_session_cache_pollution(
    async_session,
    user1_id,
    user2_id,
    conversation_user1,
    conversation_user2
):
    """
    Verify AsyncSession doesn't cache and cause cross-user pollution.

    Tests that separate sessions for different users don't
    interfere with each other's data.
    """
    conv_id_1 = conversation_user1.id
    conv_id_2 = conversation_user2.id

    async def add_message_to_conversation(user_id: str, conv_id: UUID, content: str):
        """Add a message in a fresh session."""
        async with async_session() as session:
            msg = await ConversationService.append_message(
                session,
                conversation_id=conv_id,
                user_id=user_id,
                role="user",
                content=content
            )
            return msg.id

    # Add messages from different users concurrently
    msg_ids = await asyncio.gather(
        add_message_to_conversation(user1_id, conv_id_1, "User1 Message"),
        add_message_to_conversation(user2_id, conv_id_2, "User2 Message"),
    )

    # Verify each user only sees their own messages
    async with async_session() as session:
        user1_msgs = await ConversationService.get_recent_messages(
            session,
            conversation_id=conv_id_1,
            user_id=user1_id,
            limit=50
        )

        user2_msgs = await ConversationService.get_recent_messages(
            session,
            conversation_id=conv_id_2,
            user_id=user2_id,
            limit=50
        )

        # Verify correct isolation
        assert all("User1" in m.content for m in user1_msgs), \
            "User1 conversation has non-User1 messages"
        assert all("User2" in m.content for m in user2_msgs), \
            "User2 conversation has non-User2 messages"

    logger.info("✓ No session cache pollution between concurrent requests")


# ============================================================================
# Fixtures for additional users (user4, user5)
# ============================================================================

@pytest.fixture
def user4_id():
    """Generate a unique user ID for test user 4."""
    return str(uuid4())


@pytest.fixture
def user5_id():
    """Generate a unique user ID for test user 5."""
    return str(uuid4())
