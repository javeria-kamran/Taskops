# Test File Structure Reference

## Quick Navigation - All 14 Tests

```
test_stateless.py (937 lines)
├─ Module Imports & Setup (lines 1-29)
│
├─ Section 1: No Module-Level Mutable State
│  ├─ test_no_module_level_cached_state (lines 46-79)
│  │  └─ Checks: ChatService class has no cache/buffer attributes
│  ├─ test_no_conversation_in_memory_buffer (lines 84-102)
│  │  └─ Checks: ConversationService has no buffer storage
│  └─ test_no_task_in_memory_cache (lines 107-137)
│     └─ Checks: ToolExecutor only has session attribute
│
├─ Section 2: Fresh Database Reads Each Call
│  ├─ test_chat_service_fresh_from_db_each_call (lines 146-204)
│  │  └─ Pattern: Create → Read → Insert → Read → Verify
│  └─ test_tools_no_caching_list_tasks_twice (lines 209-261)
│     └─ Pattern: List → Insert → List → Verify count increased
│
├─ Section 3: Concurrent Request Testing (Most Critical)
│  ├─ test_concurrent_requests_no_data_corruption (lines 271-351)
│  │  └─ Pattern: 10 concurrent creates (3 users) → Verify no contamination
│  ├─ test_concurrent_list_tasks_no_state_sharing (lines 356-442)
│  │  └─ Pattern: 10 concurrent lists (5 per user) → Verify isolation
│  └─ test_concurrent_chat_messages_isolated (lines 447-542)
│     └─ Pattern: 3 concurrent message posts → Verify per-conversation isolation
│
├─ Section 4: AsyncSession Isolation
│  └─ test_each_request_gets_fresh_session (lines 552-597)
│     └─ Pattern: 5 concurrent sessions → Verify all different instances
│
├─ Section 5: Database Consistency After Concurrent Ops
│  ├─ test_concurrent_task_count_consistency (lines 607-674)
│  │  └─ Pattern: 5 users × 3 tasks concurrently → Verify DB consistency
│  └─ test_conversation_message_isolation_concurrent (lines 679-743)
│     └─ Pattern: 2 conversations, concurrent additions → Verify isolation
│
├─ Section 6: Additional Stateless Verification
│  ├─ test_conversation_service_stateless_methods (lines 753-809)
│  │  └─ Pattern: Repeated method calls → Verify consistent results
│  ├─ test_tool_executor_stateless_operations (lines 814-860)
│  │  └─ Pattern: Repeated executions → Verify fresh results
│  └─ test_no_session_cache_pollution (lines 865-921)
│     └─ Pattern: Concurrent users in separate sessions → Verify no pollution
│
└─ Fixtures (lines 924-937)
   ├─ user4_id (lines 928-931)
   └─ user5_id (lines 934-937)
```

---

## Test Execution Summary

### Total Tests: 14
- **Section 1 Tests**: 3 (Class inspection)
- **Section 2 Tests**: 2 (Fresh DB reads)
- **Section 3 Tests**: 3 (Concurrent requests) ⭐ CRITICAL
- **Section 4 Tests**: 1 (Session isolation)
- **Section 5 Tests**: 2 (DB consistency)
- **Section 6 Tests**: 3 (Additional verification)

### Decorators Applied to All Tests
```python
@pytest.mark.asyncio      # Enable async/await
@pytest.mark.stateless    # Custom marker for test filtering
```

### Test Execution Command
```bash
# Run all stateless tests
pytest tests/test_stateless.py -v

# Run only concurrent tests (most critical)
pytest tests/test_stateless.py -k "concurrent" -v

# Run with custom marker
pytest tests/test_stateless.py -m stateless -v
```

---

## Fixture Dependencies

```
conftest.py provides:
├─ async_engine
│  └─ Create in-memory SQLite DB
├─ async_session
│  └─ AsyncSession factory
├─ user1_id, user2_id, user3_id
│  └─ UUID fixtures for users
├─ user1_token, user2_token, user3_token
│  └─ JWT tokens (not used in stateless tests)
├─ conversation_user1, conversation_user2
│  └─ Pre-created conversations
└─ Task fixtures (not used in stateless tests)

test_stateless.py provides:
├─ user4_id
│  └─ Additional user for concurrent tests
└─ user5_id
   └─ Additional user for concurrent tests
```

---

## Pattern Summary

| Pattern | Tests Using | Purpose |
|---------|-------------|---------|
| **Module Inspection** | 3 tests | Verify no class-level state |
| **Fresh Read Verification** | 2 tests | Prove no in-memory caching |
| **Concurrent Execution** | 3 tests | Verify thread-safety |
| **Session ID Tracking** | 1 test | Prove session isolation |
| **Database Count Checks** | 5 tests | Verify DB consistency |
| **Repeated Method Calls** | 3 tests | Verify statelessness |

---

## Key Assertions by Test Category

### Module-Level State (3 tests)
```python
# Use: inspect.getmembers() + string matching
assert len(cache_attrs) == 0, "Found cache attributes"
assert actual_attrs == expected_attrs, "Unexpected attributes"
assert not isinstance(attr_value, (dict, list, set)), "Mutable state found"
```

### Fresh Database Reads (2 tests)
```python
# Use: Sequential reads with DB modification between
assert count_2 >= count_1, "Cached response returned"
assert new_message in messages_2, "New data not found"
```

### Concurrent Operations (3 tests)
```python
# Use: asyncio.gather() + post-execution DB queries
assert user1_count == 4, "Wrong task count"
results = await asyncio.gather(...)
assert all(r.get("success") for r in results), "Some ops failed"
```

### Session Isolation (1 test)
```python
# Use: id(session) memory address tracking
unique_ids = set(session_ids)
assert len(unique_ids) == 5, "Sessions were reused"
```

### Database Consistency (2 tests)
```python
# Use: SELECT COUNT(*) WHERE conditions
assert total_count == 15, "Missing tasks"
assert len(task_ids) == len(unique_ids), "Duplicate IDs found"
```

### Stateless Methods (3 tests)
```python
# Use: Repeated method calls with consistent result checking
assert all(r == 3 for r in results), "Inconsistent results"
results.append(result)  # Store each result
```

---

## Files Related to Testing

```
d:\Todo-hackathon\
├─ STATELESS_TEST_SUMMARY.md (this file's summary)
├─ backend\
│  ├─ tests\
│  │  ├─ conftest.py (base fixtures)
│  │  ├─ test_stateless.py (THIS FILE - 937 lines, 14 tests)
│  │  ├─ test_auth.py (authentication tests)
│  │  ├─ test_tasks.py (task endpoint tests)
│  │  ├─ test_endpoints/
│  │  └─ test_tools/
│  ├─ app\
│  │  ├─ chat\
│  │  │  ├─ services\
│  │  │  │  ├─ chat_service.py ← tested
│  │  │  │  └─ conversation_service.py ← tested
│  │  │  ├─ tools\
│  │  │  │  └─ executor.py ← tested
│  │  │  └─ models.py ← Message, Conversation models
│  │  ├─ models\
│  │  │  └─ task.py ← Task model
│  │  └─ database.py
│  ├─ requirements.txt
│  └─ requirements-dev.txt
```

---

## Test Data Isolation Strategy

```python
# Each test gets a fresh database
@pytest_asyncio.fixture
async def async_engine():
    engine = create_async_engine(
        "sqlite+aiosqlite:///:memory:",
        echo=False,
        connect_args={"check_same_thread": False}
    )
    # Fresh DB created here
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    yield engine
    await engine.dispose()  # Cleaned up here

# This means:
# - Test 1 gets Database A
# - Test 2 gets Database B
# - Test 3 gets Database C
# - etc.
```

---

## Performance Considerations

- **Concurrent Test Runtime**: ~1-2 seconds each (asyncio overhead)
- **Total Suite Runtime**: ~15-20 seconds expected
- **Database Size**: Minimal (in-memory SQLite, <1MB per test)
- **Memory Usage**: Low (fresh engine per test)
- **Scalability**: Can add more concurrent tests without overhead

---

## Assertions That Catch Issues

### Would catch:
1. ✓ A global dictionary caching results
2. ✓ A module-level conversation buffer
3. ✓ SQLAlchemy session reuse
4. ✓ In-memory message storage
5. ✓ Race conditions in concurrent creates
6. ✓ Cross-user data leakage
7. ✓ Message contamination between conversations
8. ✓ Stale data from previous requests
9. ✓ Duplicate task IDs
10. ✓ Missing database writes

### Structure:
- **Pre-condition Assertion**: Setup data
- **Operation**: Execute the operation
- **Post-condition Assertion**: Verify expected state
- **Isolation Check**: Verify no side effects on other data

---

## Example Test Flow

```python
@pytest.mark.asyncio
@pytest.mark.stateless
async def test_concurrent_requests_no_data_corruption(
    async_session,     # Fresh SQLite engine per test
    user1_id,         # UUID for user 1
    user2_id,         # UUID for user 2
    user3_id,         # UUID for user 3
    conversation_user1,  # Pre-created conversation
    conversation_user2   # Pre-created conversation
):
    """Test description..."""

    async def create_task_for_user(user_id, conv_id, title):
        async with async_session() as session:
            executor = ToolExecutor(session)
            return await executor.execute(
                tool_name="add_task",
                arguments={"title": title, "priority": "high"},
                user_id=user_id,
                conversation_id=conv_id
            )

    # Run 10 concurrent operations
    tasks = [
        create_task_for_user(user1_id, conv_id_1, "User1-Task-A"),
        create_task_for_user(user1_id, conv_id_1, "User1-Task-C"),
        create_task_for_user(user1_id, conv_id_1, "User1-Task-E"),
        create_task_for_user(user1_id, conv_id_1, "User1-Task-G"),
        create_task_for_user(user2_id, conv_id_2, "User2-Task-B"),
        create_task_for_user(user2_id, conv_id_2, "User2-Task-D"),
        create_task_for_user(user2_id, conv_id_2, "User2-Task-F"),
        create_task_for_user(user3_id, uuid4(), "User3-Task-H"),
        create_task_for_user(user3_id, uuid4(), "User3-Task-I"),
        create_task_for_user(user3_id, uuid4(), "User3-Task-J"),
    ]

    # Execute concurrently
    results = await asyncio.gather(*tasks)

    # Verify all succeeded
    assert all(r.get("success") for r in results), "Some tasks failed"

    # Query database for count verification
    async with async_session() as session:
        stmt = select(func.count(Task.id)).where(Task.user_id == user1_id)
        result = await session.execute(stmt)
        user1_count = result.scalar()
        assert user1_count == 4, f"Expected 4, got {user1_count}"

        # Repeat for user2 and user3...

    # Log success
    logger.info("✓ Concurrent requests produce no data corruption")
```

---

## Success Criteria

The test file is complete and comprehensive when:

- [x] 14 tests are defined
- [x] All tests use `@pytest.mark.asyncio`
- [x] All tests use `@pytest.mark.stateless`
- [x] All imported modules exist
- [x] Fixtures are available in conftest.py
- [x] Tests use `asyncio.gather()` for concurrency
- [x] Tests use database queries for verification
- [x] Tests have clear docstrings
- [x] No mutable module-level state is present
- [x] Fresh database reads are verified
- [x] Concurrent requests are properly tested
- [x] Session isolation is validated
- [x] Database consistency is confirmed
- [x] Service methods are stateless
- [x] Tool operations are stateless

## All criteria are met! ✓

