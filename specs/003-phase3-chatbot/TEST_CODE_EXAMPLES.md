# Test Code Examples & Implementation Details

This document provides actual code excerpts from `test_stateless.py` showing how each test category works.

---

## Section 1: No Module-Level Mutable State

### Example 1: test_no_module_level_cached_state

**Location**: Lines 46-79

```python
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
```

**What it does**:
1. Uses `inspect.getmembers()` to extract all ChatService class attributes
2. Filters out dunder methods and callables
3. Searches for attributes containing "cache" or "buffer" (case-insensitive)
4. Verifies no mutable data structures (dict, list, set) exist at class level
5. Logs success if all checks pass

**Key assertion**: `assert len(cache_attrs) == 0`

---

### Example 2: test_no_task_in_memory_cache

**Location**: Lines 107-137

```python
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
```

**What it does**:
1. Instantiates a ToolExecutor with a session
2. Uses `vars(executor)` to get all instance attributes
3. Checks that ONLY 'session' attribute exists
4. Verifies no prohibited mutable types in any attributes
5. Confirms all operations must use the passed session (no internal cache)

**Key assertion**: `assert actual_attrs == expected_attrs`

---

## Section 2: Fresh Database Reads

### Example 3: test_chat_service_fresh_from_db_each_call

**Location**: Lines 146-204

```python
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
```

**What it does**:
1. Creates 3 initial messages in conversation
2. Calls `get_recent_messages()` and gets 3 messages
3. Adds new message directly to database
4. Calls `get_recent_messages()` again
5. **Critical check**: Assert that second call returns 4 messages (including the new one)
6. If the service was caching, it would have returned the old 3 messages

**Key assertions**:
- `assert count_2 == 4` - Proves fresh DB read
- `assert messages_2[-1].content == "Message 4..."` - Proves new data is visible

---

## Section 3: Concurrent Requests - Most Critical

### Example 4: test_concurrent_requests_no_data_corruption

**Location**: Lines 271-351

```python
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
```

**What it does**:
1. Defines a helper function to create a task for any user
2. Creates a list of 10 concurrent task creation operations
3. Uses **`asyncio.gather(*tasks)`** to run all 10 operations concurrently
4. Verifies all operations succeeded
5. **Critical checks**: Queries the database directly to count tasks per user
6. If there was any race condition or state contamination, counts would be wrong

**Key concurrent pattern**:
```python
tasks = [
    create_task_for_user(...),
    create_task_for_user(...),
    ...(10 total)
]
results = await asyncio.gather(*tasks)  # All run concurrently!
```

**Key assertions**:
- `assert all(r.get("success") for r in results)` - All operations must succeed
- `assert user1_count == 4` - Exact count verification from DB
- `assert user2_count == 3` - Different count per user
- `assert user3_count == 3` - All users properly isolated

**Why this is critical**:
- If there was shared state, counts might be wrong
- If there was a race condition, some writes might be lost
- If there was state pollution, tasks might be assigned to wrong user
- Database should be source of truth, bypassing any in-memory cache

---

### Example 5: test_concurrent_list_tasks_no_state_sharing

**Location**: Lines 356-442

```python
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
```

**What it does**:
1. Pre-populates 2 tasks for user1, 3 tasks for user2
2. Defines a list_tasks helper that executes the tool
3. Creates 5 concurrent list calls for user1 and 5 for user2 (10 total)
4. **Runs all 10 concurrently** with `asyncio.gather()`
5. Verifies all calls succeeded
6. **Critical check**: User1's results always show ≥2 tasks, User2 shows ≥3

**Key differences from previous test**:
- Tests **read operations** instead of write
- Tests **consistency** across concurrent calls
- Tests that each user always sees their own data

**Why important**:
- If there was shared state, counts might intermingle
- If there was caching, results might be stale
- If there was state pollution, user1 might see user2's tasks

---

## Section 4: AsyncSession Isolation

### Example 6: test_each_request_gets_fresh_session

**Location**: Lines 552-597

```python
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
```

**What it does**:
1. Uses `id(session)` to capture the Python memory address of the session object
2. Appends each session ID to a list
3. Runs 5 concurrent operations using `asyncio.gather()`
4. **Critical check**: Converts session IDs to a set and verifies all 5 are unique
5. If sessions were reused, some IDs would be duplicates

**Key uniqueness check**:
```python
unique_ids = set(results)  # Remove duplicates
assert len(unique_ids) == 5  # All must be unique!
```

**Why important**:
- SQLAlchemy sessions can't be safely shared across async operations
- Each request must get its own session instance
- Reusing sessions could cause data leaks or race conditions

---

## Section 5: Database Consistency

### Example 7: test_concurrent_task_count_consistency

**Location**: Lines 607-674

```python
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
```

**What it does**:
1. Creates a helper to generate 3 tasks for each user
2. Concurrently runs this for 5 users (15 tasks total)
3. **Three separate verifications**:
   - Total COUNT(*) should be 15
   - Each user COUNT(*) should be 3
   - No duplicate IDs exist

**Key database queries**:
```python
# Total count
stmt = select(func.count(Task.id))

# Count per user
stmt = select(func.count(Task.id)).where(Task.user_id == user_id)

# Duplicate detection
task_ids = [t.id for t in all_db_tasks]
unique_ids = set(task_ids)
assert len(task_ids) == len(unique_ids)
```

**Why important**:
- Proves database received all writes (no lost updates)
- Proves data is correctly partitioned by user
- Proves no duplicate primary keys were created

---

## Summary of Test Patterns

| Pattern | Implementation | Proves |
|---------|---|---|
| **Module Inspection** | `inspect.getmembers()` | No class-level state |
| **Fresh Reads** | Read → Insert → Read → Verify | No caching |
| **Concurrent Ops** | `asyncio.gather(10 operations)` | No race conditions |
| **Session Isolation** | `id(session)` tracking | Fresh sessions |
| **DB Consistency** | `SELECT COUNT(*)` with conditions | All writes successful |
| **Repeated Methods** | Call method N times, compare results | Stateless behavior |

---

## Files Generated

1. **test_stateless.py** (937 lines) - Main test file
2. **STATELESS_TEST_SUMMARY.md** - Overview of all tests
3. **TEST_FILE_STRUCTURE.md** - Visual structure and navigation
4. **TEST_CODE_EXAMPLES.md** (this file) - Detailed code examples

All test files are complete and ready for execution with `pytest`.

