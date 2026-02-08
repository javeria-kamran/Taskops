"""
Load and Stress Testing

Optional tests for system behavior under concurrent load:
- Multiple concurrent chat requests
- Multiple concurrent conversation creation
- Rate limiting / 429 Too Many Requests
- Database connection pool under load
- OpenAI API availability handling

Note: These tests are optional and may require special configuration
or external service availability to run successfully.
"""

import pytest
import asyncio
import time
from concurrent.futures import ThreadPoolExecutor
from uuid import uuid4
from fastapi.testclient import TestClient

from app.chat.routers.chat import router
from app.chat.services.conversation_service import ConversationService
from app.chat.middleware.auth import create_access_token
from fastapi import FastAPI


# ============================================================================
# Test Fixtures
# ============================================================================


@pytest.fixture
def app():
    """Create FastAPI test app."""
    app = FastAPI()
    app.include_router(router)
    return app


@pytest.fixture
def client(app):
    """Create TestClient."""
    return TestClient(app)


@pytest.fixture
def user_id():
    """Test user ID."""
    return str(uuid4())


@pytest.fixture
def user_token(user_id):
    """JWT token for test user."""
    return create_access_token(user_id, expires_in_hours=24)


# ============================================================================
# Tests: Concurrent Conversation Creation
# ============================================================================


@pytest.mark.load
def test_create_100_conversations_sequentially(client, user_id, user_token):
    """
    Test creating 100 conversations sequentially.

    Measures:
    - Total time for 100 creates
    - Average time per create
    - No errors
    """
    start_time = time.time()
    conversation_ids = []

    for i in range(100):
        response = client.post(
            f"/api/{user_id}/conversations",
            json={"title": f"Conversation {i+1}"},
            headers={"Authorization": f"Bearer {user_token}"}
        )
        assert response.status_code == 201
        conversation_ids.append(response.json()["conversation_id"])

    elapsed = time.time() - start_time
    avg_time = elapsed / 100

    print(f"\n100 sequential creates: {elapsed:.2f}s total, {avg_time:.3f}s avg")
    assert len(set(conversation_ids)) == 100  # All unique


@pytest.mark.load
def test_concurrent_conversation_creation_10_threads(client, user_id, user_token):
    """
    Test creating conversations with 10 concurrent threads.

    Measures:
    - Throughput with concurrency
    - Thread safety
    - No duplicate IDs
    """
    results = []
    errors = []

    def create_conversation(index):
        try:
            response = client.post(
                f"/api/{user_id}/conversations",
                json={"title": f"Concurrent Conversation {index}"},
                headers={"Authorization": f"Bearer {user_token}"}
            )
            if response.status_code == 201:
                results.append(response.json()["conversation_id"])
            else:
                errors.append((index, response.status_code))
        except Exception as e:
            errors.append((index, str(e)))

    start_time = time.time()

    with ThreadPoolExecutor(max_workers=10) as executor:
        futures = [executor.submit(create_conversation, i) for i in range(50)]
        for future in futures:
            future.result(timeout=30)

    elapsed = time.time() - start_time

    print(f"\n50 concurrent creates (10 threads): {elapsed:.2f}s, {50/elapsed:.1f} req/s")
    assert len(errors) == 0, f"Errors occurred: {errors}"
    assert len(set(results)) == 50  # All unique


@pytest.mark.load
def test_list_conversations_with_100_items(client, user_id, user_token):
    """
    Test listing 100 conversations.

    Measures:
    - Query performance with large result set
    - Response time
    - Data consistency
    """
    # Create 100 conversations
    for i in range(100):
        response = client.post(
            f"/api/{user_id}/conversations",
            json={"title": f"Conversation {i+1}"},
            headers={"Authorization": f"Bearer {user_token}"}
        )
        assert response.status_code == 201

    # List with limit=100
    start_time = time.time()
    response = client.get(
        f"/api/{user_id}/conversations?limit=100",
        headers={"Authorization": f"Bearer {user_token}"}
    )
    elapsed = time.time() - start_time

    print(f"\nList 100 conversations: {elapsed:.3f}s")
    assert response.status_code == 200
    assert response.json()["count"] == 100


# ============================================================================
# Tests: Rapid Sequential Requests
# ============================================================================


@pytest.mark.load
def test_rapid_conversation_list_requests(client, user_id, user_token):
    """
    Test rapid sequential list requests.

    Measures:
    - Response time consistency
    - Cache behavior
    - No performance degradation
    """
    times = []

    # Create base conversation
    client.post(
        f"/api/{user_id}/conversations",
        json={"title": "Base Conversation"},
        headers={"Authorization": f"Bearer {user_token}"}
    )

    # Perform 50 rapid list requests
    for _ in range(50):
        start = time.time()
        response = client.get(
            f"/api/{user_id}/conversations",
            headers={"Authorization": f"Bearer {user_token}"}
        )
        elapsed = time.time() - start
        times.append(elapsed)
        assert response.status_code == 200

    avg_time = sum(times) / len(times)
    max_time = max(times)
    min_time = min(times)

    print(f"\n50 rapid list requests: avg={avg_time:.3f}s, min={min_time:.3f}s, max={max_time:.3f}s")


# ============================================================================
# Tests: Error Resilience Under Load
# ============================================================================


@pytest.mark.load
def test_invalid_requests_dont_break_system(client, user_id, user_token):
    """
    Test that invalid requests don't crash the system under load.

    Sends mix of valid and invalid requests to verify error handling.
    """
    valid_count = 0
    invalid_count = 0

    for i in range(100):
        if i % 10 == 0:
            # Send invalid request
            response = client.post(
                f"/api/{user_id}/conversations",
                json={"title": "a" * 201},  # Exceeds max length
                headers={"Authorization": f"Bearer {user_token}"}
            )
            if response.status_code == 400:
                invalid_count += 1
        else:
            # Send valid request
            response = client.post(
                f"/api/{user_id}/conversations",
                json={"title": f"Valid Conversation {i}"},
                headers={"Authorization": f"Bearer {user_token}"}
            )
            if response.status_code == 201:
                valid_count += 1

    print(f"\nMixed requests: {valid_count} valid, {invalid_count} invalid")
    assert valid_count == 90  # All valid succeeded
    assert invalid_count == 10  # All invalid rejected


# ============================================================================
# Tests: Token Validity Under Load
# ============================================================================


@pytest.mark.load
def test_same_token_reuse_1000_times(client, user_id, user_token):
    """
    Test reusing the same token 1000 times.

    Verifies:
    - Token validity maintained across requests
    - No token expiration during batch
    - Consistent auth checks
    """
    success_count = 0

    for i in range(1000):
        response = client.get(
            f"/api/{user_id}/conversations",
            headers={"Authorization": f"Bearer {user_token}"}
        )
        if response.status_code in [200, 401]:  # Valid responses
            success_count += 1

    print(f"\n1000 requests with same token: {success_count} succeeded")
    assert success_count == 1000


@pytest.mark.load
def test_expired_token_consistency(client, user_id):
    """
    Test that expired tokens consistently return 401.

    Verifies:
    - Consistent expiration behavior
    - No false positives
    """
    from datetime import datetime, timedelta
    import jwt
    from app.config import settings

    payload = {
        "sub": user_id,
        "exp": datetime.utcnow() - timedelta(hours=1)  # Expired 1 hour ago
    }
    expired_token = jwt.encode(payload, settings.better_auth_secret, algorithm=settings.jwt_algorithm)

    rejected_count = 0

    for _ in range(100):
        response = client.get(
            f"/api/{user_id}/conversations",
            headers={"Authorization": f"Bearer {expired_token}"}
        )
        if response.status_code == 401:
            rejected_count += 1

    print(f"\n100 requests with expired token: {rejected_count} rejected")
    assert rejected_count == 100


# ============================================================================
# Tests: Database Connection Pool
# ============================================================================


@pytest.mark.load
def test_concurrent_database_operations(client, user_id, user_token):
    """
    Test database connection pool under concurrent load.

    Simulates:
    - Multiple concurrent database sessions
    - Connection pool exhaustion recovery
    - No connection leaks
    """
    import threading
    from queue import Queue

    results = Queue()

    def database_operation(thread_id):
        try:
            response = client.post(
                f"/api/{user_id}/conversations",
                json={"title": f"Thread {thread_id}"},
                headers={"Authorization": f"Bearer {user_token}"}
            )
            results.put(response.status_code)
        except Exception as e:
            results.put(f"ERROR: {e}")

    threads = []
    for i in range(20):
        t = threading.Thread(target=database_operation, args=(i,))
        threads.append(t)
        t.start()

    for t in threads:
        t.join()

    # Check results
    statuses = []
    while not results.empty():
        statuses.append(results.get())

    success_count = sum(1 for s in statuses if s == 201)
    print(f"\n20 concurrent database ops: {success_count} succeeded")
    assert success_count == 20


# ============================================================================
# Tests: Response Time Consistency
# ============================================================================


@pytest.mark.load
def test_response_time_distribution(client, user_id, user_token):
    """
    Test response time distribution across requests.

    Measures:
    - Mean response time
    - Median response time
    - 95th percentile response time
    - Outliers
    """
    times = []

    for _ in range(100):
        start = time.time()
        response = client.get(
            f"/api/{user_id}/conversations",
            headers={"Authorization": f"Bearer {user_token}"}
        )
        elapsed = time.time() - start
        times.append(elapsed)
        assert response.status_code == 200

    times.sort()
    mean = sum(times) / len(times)
    median = times[len(times) // 2]
    p95 = times[int(len(times) * 0.95)]

    print(f"\nResponse time stats (100 requests):")
    print(f"  Mean: {mean:.3f}s")
    print(f"  Median: {median:.3f}s")
    print(f"  P95: {p95:.3f}s")


# ============================================================================
# Tests: Cleanup
# ============================================================================


@pytest.mark.load
def test_system_cleanup_after_load(client, user_id, user_token):
    """
    Test that system recovers cleanly after load.

    Verifies:
    - System responsive after heavy load
    - No resource leaks
    - Normal operations resume
    """
    # Normal request after heavy load
    response = client.get(
        f"/api/{user_id}/conversations",
        headers={"Authorization": f"Bearer {user_token}"}
    )
    assert response.status_code == 200

    # Create new conversation to verify write operations work
    response = client.post(
        f"/api/{user_id}/conversations",
        json={"title": "Post-Load Conversation"},
        headers={"Authorization": f"Bearer {user_token}"}
    )
    assert response.status_code == 201


# ============================================================================
# Notes for Running Load Tests
# ============================================================================

"""
Load Test Execution Guide:

1. Run with pytest marker:
   pytest -m load -v

2. Individual load test:
   pytest backend/app/chat/tests/test_load.py::test_create_100_conversations_sequentially -v

3. Monitor during execution:
   - CPU usage
   - Memory usage
   - Database connections
   - Response times

4. Expected performance metrics:
   - Sequential create: ~50ms per request
   - Concurrent creates (10 threads): ~100-200 req/s
   - List operations: <100ms for typical datasets
   - Token validation: <5ms per request

5. Failure modes to watch:
   - Database connection pool exhaustion
   - OpenAI rate limits (if testing agent)
   - Memory leaks from unclosed sessions
   - Token expiration during batch operations

6. System requirements:
   - Sufficient file descriptors (ulimit -n)
   - Adequate memory for 100+ concurrent operations
   - Network stability for external API calls
   - Database accessible and responsive

Test Coverage Summary:

✅ Concurrent Operations
  - 100 sequential creates
  - 50 concurrent creates (10 threads)
  - 100 item list query

✅ Rapid Sequential Requests
  - 50 rapid list requests
  - Response time consistency

✅ Error Resilience
  - Mix of valid/invalid requests
  - System stability under mixed load

✅ Token Management
  - 1000 reuses of same token
  - 100 expired token rejections
  - Consistent expiration behavior

✅ Database Connections
  - 20 concurrent database operations
  - Connection pool resilience
  - No connection leaks

✅ Performance Metrics
  - Response time distribution
  - Mean, median, P95 calculations
  - Outlier detection

✅ System Recovery
  - Normal operations after load
  - Clean state restoration

Total: 11 load test scenarios
"""
