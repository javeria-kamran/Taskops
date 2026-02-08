# Phase 10 Test Execution Quick Reference

## Quick Start

```bash
cd backend

# Run all Phase 10 tests
pytest tests/test_tools/ tests/test_endpoints/ tests/test_stateless.py tests/test_isolation.py -v

# Run with coverage
pytest tests/ --cov=app.chat --cov=app.models --cov-report=html -v

# Run specific category
pytest tests/ -m unit -v              # Unit tests only
pytest tests/ -m integration -v       # Integration tests
pytest tests/ -m stateless -v         # Statelessness tests
pytest tests/ -m isolation -v         # Isolation tests
```

## Test Files & Coverage

### Unit Tests (T053-T057)
```bash
pytest tests/test_tools/ -v

# Individual tool tests
pytest tests/test_tools/test_add_task.py -v        # 25 tests
pytest tests/test_tools/test_list_tasks.py -v      # 29 tests
pytest tests/test_tools/test_complete_task.py -v   # 13 tests
pytest tests/test_tools/test_delete_task.py -v     # 15 tests
pytest tests/test_tools/test_update_task.py -v     # 22 tests
```

### Integration Tests (T058)
```bash
pytest tests/test_endpoints/test_chat_endpoint.py -v  # 26 tests
```

### Statelessness (T059)
```bash
pytest tests/test_stateless.py -v  # 14 tests
```

### Multi-User Isolation (T060)
```bash
pytest tests/test_isolation.py -v  # 22 tests
```

## Fixture Reference

### User IDs
- `user1_id` - First test user (UUID)
- `user2_id` - Second test user (UUID)
- `user3_id` - Third test user (UUID)

### JWT Tokens
- `user1_token` - Valid 24-hour token for user1
- `user2_token` - Valid 24-hour token for user2
- `user3_token` - Valid 24-hour token for user3
- `expired_token` - Expired token (1 hour ago)
- `invalid_token` - Invalid token format

### Conversations
- `conversation_user1` - Conversation owned by user1
- `conversation_user2` - Conversation owned by user2

### Tasks
- `task1_user1` - Task created by user1
- `task2_user1` - Second task created by user1
- `task1_user2` - Task created by user2

### Database
- `async_session` - AsyncSession factory for tests
- `async_engine` - In-memory SQLite engine

### Mocks
- `mock_openai_response` - LLM response without tool calls
- `mock_openai_with_tool_call` - LLM response with tool execution

### HTTP Headers
- `auth_headers` - Authorization header for user1
- `auth_headers_user2` - Authorization header for user2
- `invalid_auth_headers` - Invalid auth header
- `expired_auth_headers` - Expired auth header

## Example Test Pattern

```python
import pytest
from app.chat.tools.executor import ToolExecutor

@pytest.mark.asyncio
@pytest.mark.unit
async def test_add_task_valid_input(async_session, user1_id, conversation_user1):
    executor = ToolExecutor(async_session)

    result = await executor.execute(
        tool_name="add_task",
        arguments={
            "title": "Test Task",
            "description": "Test Description",
            "priority": "high"
        },
        user_id=user1_id,
        conversation_id=conversation_user1
    )

    assert result["success"] is True
    assert "task_id" in result
    assert result["task"]["user_id"] == user1_id
    assert result["task"]["status"] == "pending"
```

## Coverage Report

Generate HTML coverage report:
```bash
pytest tests/ --cov=app.chat --cov=app.models --cov-report=html

# Open report
open htmlcov/index.html
```

## Test Markers

Available pytest markers:
- `@pytest.mark.unit` - Unit tests
- `@pytest.mark.integration` - Integration tests
- `@pytest.mark.stateless` - Statelessness verification
- `@pytest.mark.isolation` - Multi-user isolation

## Debugging Tips

### Run single test with output
```bash
pytest tests/test_tools/test_add_task.py::test_add_task_valid_input -v -s
```

### Run with print statements visible
```bash
pytest tests/ -v -s
```

### Run with detailed logging
```bash
pytest tests/ -v --log-cli-level=DEBUG
```

### Run and stop on first failure
```bash
pytest tests/ -x -v
```

## Expected Results

All tests should pass with:
- ✅ 100+ test cases
- ✅ >80% code coverage
- ✅ No cross-user contamination
- ✅ Stateless operation verified
- ✅ Concurrent operation safety

## Continuous Integration

For CI/CD pipeline:
```bash
# Run all tests with coverage threshold
pytest tests/ \
  --cov=app.chat \
  --cov=app.models \
  --cov-fail-under=80 \
  --tb=short \
  -v
```

## Troubleshooting

### Import errors
```bash
# Ensure app is in PYTHONPATH
cd backend
export PYTHONPATH=$PWD:$PYTHONPATH
pytest tests/
```

### Async event loop errors
```bash
# Install pytest-asyncio
pip install pytest-asyncio
```

### Database errors
```bash
# Verify SQLite+asyncio support
pip install aiosqlite
pip install sqlalchemy[asyncio]
```

## Performance

Typical test execution times:
- Unit tests (104 tests): ~15-20 seconds
- Integration tests (26 tests): ~10-15 seconds
- Statelessness (14 tests): ~8-12 seconds (concurrent)
- Isolation (22 tests): ~10-15 seconds
- **Total**: ~50-60 seconds for all tests

## Database Details

All tests use in-memory SQLite:
- **Engine**: `sqlite+aiosqlite:///:memory:`
- **Isolation**: Each test gets fresh database
- **Cleanup**: Automatic after each test
- **Transactions**: Rollback after test completion
- **Performance**: ~1000x faster than file-based DB

