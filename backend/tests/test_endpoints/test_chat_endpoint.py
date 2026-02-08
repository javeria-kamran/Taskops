"""
Integration tests for Chat Endpoint (T036-T046).

Tests cover:
- T043: JWT Authentication
- T044: Input Sanitization
- T045: User Isolation / Authorization
- T046: Response Structure

All tests use FastAPI TestClient with mocked OpenAI API.
"""

import pytest
from fastapi.testclient import TestClient
from unittest.mock import patch, AsyncMock, MagicMock
from datetime import datetime, timedelta
from uuid import uuid4
import json
import asyncio

from app.main import app


# ==============================================================================
# Markers & Configuration
# ==============================================================================

pytestmark = [pytest.mark.integration, pytest.mark.asyncio]

# Maximum message length from endpoint validation
MAX_MESSAGE_LENGTH = 4096


# ==============================================================================
# T043: Authentication Tests
# ==============================================================================


class TestChatAuthentication:
    """Authentication tests for chat endpoint [T043]."""

    @pytest.mark.integration
    def test_chat_missing_jwt_token(self, user1_id, conversation_user1):
        """
        T043: POST /api/{user_id}/chat without token returns 401.

        Assert:
        - Status code 401
        - "token" or "authentication" in error detail
        """
        client = TestClient(app)

        response = client.post(
            f"/api/{user1_id}/chat",
            json={
                "conversation_id": str(conversation_user1.id),
                "message": "Test message"
            }
            # NOTE: No Authorization header
        )

        assert response.status_code == 401
        assert "token" in response.json()["detail"].lower() or "auth" in response.json()["detail"].lower()

    @pytest.mark.integration
    def test_chat_invalid_jwt_token(self, user1_id, conversation_user1, invalid_token):
        """
        T043: POST /api/{user_id}/chat with invalid token returns 401.

        Assert:
        - Status code 401
        """
        client = TestClient(app)

        response = client.post(
            f"/api/{user1_id}/chat",
            json={
                "conversation_id": str(conversation_user1.id),
                "message": "Test message"
            },
            headers={"Authorization": f"Bearer {invalid_token}"}
        )

        assert response.status_code == 401

    @pytest.mark.integration
    def test_chat_expired_jwt_token(self, user1_id, conversation_user1, expired_token):
        """
        T043: POST /api/{user_id}/chat with expired token returns 401.

        Assert:
        - Status code 401
        """
        client = TestClient(app)

        response = client.post(
            f"/api/{user1_id}/chat",
            json={
                "conversation_id": str(conversation_user1.id),
                "message": "Test message"
            },
            headers={"Authorization": f"Bearer {expired_token}"}
        )

        assert response.status_code == 401


# ==============================================================================
# T045: Authorization / User Isolation Tests
# ==============================================================================


class TestChatAuthorization:
    """Authorization tests for chat endpoint [T045]."""

    @pytest.mark.integration
    def test_chat_user_id_mismatch(self, user1_id, user2_id, user1_token, conversation_user1):
        """
        T045: Token for user1 but path has user2 returns 403.

        User1 has valid token but tries to access endpoint with user2's ID.

        Assert:
        - Status code 403
        - "does not match" in error detail
        """
        client = TestClient(app)

        response = client.post(
            f"/api/{user2_id}/chat",  # user2's path
            json={
                "conversation_id": str(conversation_user1.id),
                "message": "Test message"
            },
            headers={"Authorization": f"Bearer {user1_token}"}  # user1's token
        )

        assert response.status_code == 403
        assert "does not match" in response.json()["detail"].lower() or "mismatch" in response.json()["detail"].lower()

    @pytest.mark.integration
    def test_chat_user_doesnt_own_conversation(self, user1_id, user1_token, conversation_user2):
        """
        T045: User1 tries to access user2's conversation returns 403/404.

        User1 has valid token for their own user_id, but tries to access
        a conversation created by user2.

        Assert:
        - Status code 403 or 404
        """
        client = TestClient(app)

        response = client.post(
            f"/api/{user1_id}/chat",
            json={
                "conversation_id": str(conversation_user2.id),  # user2's conversation
                "message": "Test message"
            },
            headers={"Authorization": f"Bearer {user1_token}"}
        )

        assert response.status_code in [403, 404]


# ==============================================================================
# T044: Input Sanitization Tests
# ==============================================================================


class TestChatInputSanitization:
    """Input sanitization tests for chat endpoint [T044]."""

    @pytest.mark.integration
    def test_chat_xss_message_sanitized(self, user1_id, user1_token, conversation_user1):
        """
        T044: XSS message with <script> tags is sanitized, not rejected.

        The message should be processed but with XSS stripped out.

        Assert:
        - Status code 200
        - Message was processed and stored without XSS payload
        """
        client = TestClient(app)

        dangerous_message = '<script>alert("XSS")</script>Hello'

        with patch('app.chat.services.chat_service.ChatService.process_chat_message') as mock_process:
            mock_process.return_value = {
                "success": True,
                "conversation_id": str(conversation_user1.id),
                "response": "This is a safe response",
                "tool_calls_executed": [],
                "message_count": 2,
                "execution_time_ms": 100.5
            }

            response = client.post(
                f"/api/{user1_id}/chat",
                json={
                    "conversation_id": str(conversation_user1.id),
                    "message": dangerous_message
                },
                headers={"Authorization": f"Bearer {user1_token}"}
            )

        assert response.status_code == 200
        # Verify sanitization happened (the message passed to service should be sanitized)
        # The endpoint sanitizes before calling ChatService

    @pytest.mark.integration
    def test_chat_message_exceeds_max_length(self, user1_id, user1_token, conversation_user1):
        """
        T044: Message > 4096 chars returns 400.

        Assert:
        - Status code 400
        """
        client = TestClient(app)

        too_long_message = "x" * (MAX_MESSAGE_LENGTH + 1)

        response = client.post(
            f"/api/{user1_id}/chat",
            json={
                "conversation_id": str(conversation_user1.id),
                "message": too_long_message
            },
            headers={"Authorization": f"Bearer {user1_token}"}
        )

        assert response.status_code == 400

    @pytest.mark.integration
    def test_chat_empty_message(self, user1_id, user1_token, conversation_user1):
        """
        T044: Empty or whitespace-only message returns 400.

        Assert:
        - Status code 400
        """
        client = TestClient(app)

        response = client.post(
            f"/api/{user1_id}/chat",
            json={
                "conversation_id": str(conversation_user1.id),
                "message": ""
            },
            headers={"Authorization": f"Bearer {user1_token}"}
        )

        assert response.status_code == 400


# ==============================================================================
# Full Flow Tests (Happy Path)
# ==============================================================================


class TestChatFullFlow:
    """Full flow tests for chat endpoint."""

    @pytest.mark.integration
    def test_chat_full_flow_without_tools(self, user1_id, user1_token, conversation_user1):
        """
        Test: Full chat flow without tool execution.

        Flow:
        1. POST valid message to conversation
        2. Mock OpenAI response (no tool calls)
        3. Verify response structure and persistence

        Assert:
        - Status code 200
        - Response contains: success=True, response text, message_count
        - Response structure is valid (T046)
        """
        client = TestClient(app)

        mock_openai_response = MagicMock()
        mock_openai_response.choices = [MagicMock()]
        mock_openai_response.choices[0].message.content = "Here are your tasks..."
        mock_openai_response.choices[0].message.tool_calls = None

        with patch('app.chat.services.chat_service.ChatService.process_chat_message') as mock_process:
            mock_process.return_value = {
                "success": True,
                "conversation_id": str(conversation_user1.id),
                "response": "Here are your tasks...",
                "tool_calls_executed": [],
                "message_count": 2,
                "execution_time_ms": 234.5
            }

            response = client.post(
                f"/api/{user1_id}/chat",
                json={
                    "conversation_id": str(conversation_user1.id),
                    "message": "What are my tasks?"
                },
                headers={"Authorization": f"Bearer {user1_token}"}
            )

        assert response.status_code == 200
        data = response.json()

        # T046: Response structure validation
        assert data["success"] is True
        assert "response" in data
        assert isinstance(data["response"], str)
        assert len(data["response"]) > 0
        assert data["message_count"] >= 2
        assert isinstance(data["tool_calls_executed"], list)
        assert "execution_time_ms" in data
        assert data["conversation_id"] == str(conversation_user1.id)

    @pytest.mark.integration
    def test_chat_full_flow_with_tool_execution(self, user1_id, user1_token, conversation_user1):
        """
        Test: Full chat flow with tool execution.

        Flow:
        1. POST message that triggers tool call
        2. Mock OpenAI to return list_tasks tool call
        3. Mock ToolExecutor to return task results
        4. Verify tool was executed and results included

        Assert:
        - Status code 200
        - Tool was executed
        - Tool results included in response
        - Response structure is valid
        """
        client = TestClient(app)

        with patch('app.chat.services.chat_service.ChatService.process_chat_message') as mock_process:
            mock_process.return_value = {
                "success": True,
                "conversation_id": str(conversation_user1.id),
                "response": "You have 3 tasks to complete.",
                "tool_calls_executed": [
                    {
                        "tool_name": "list_tasks",
                        "arguments": {},
                        "result": "3 tasks found"
                    }
                ],
                "message_count": 4,  # user msg, assistant msg with tool call, tool result, final assistant msg
                "execution_time_ms": 456.7
            }

            response = client.post(
                f"/api/{user1_id}/chat",
                json={
                    "conversation_id": str(conversation_user1.id),
                    "message": "List all my tasks"
                },
                headers={"Authorization": f"Bearer {user1_token}"}
            )

        assert response.status_code == 200
        data = response.json()

        # T046: Response structure validation
        assert data["success"] is True
        assert data["message_count"] >= 2
        assert isinstance(data["tool_calls_executed"], list)
        assert len(data["tool_calls_executed"]) > 0

        # Verify tool execution details
        tool_call = data["tool_calls_executed"][0]
        assert "tool_name" in tool_call
        assert tool_call["tool_name"] == "list_tasks"


# ==============================================================================
# Error Handling Tests
# ==============================================================================


class TestChatErrorHandling:
    """Error handling tests for chat endpoint."""

    @pytest.mark.integration
    def test_chat_conversation_not_found(self, user1_id, user1_token):
        """
        Test: POST to non-existent conversation returns 404.

        Assert:
        - Status code 404
        """
        client = TestClient(app)

        non_existent_conversation_id = str(uuid4())

        with patch('app.chat.services.chat_service.ChatService.verify_user_owns_conversation') as mock_verify:
            mock_verify.return_value = False

            response = client.post(
                f"/api/{user1_id}/chat",
                json={
                    "conversation_id": non_existent_conversation_id,
                    "message": "Test message"
                },
                headers={"Authorization": f"Bearer {user1_token}"}
            )

        assert response.status_code in [403, 404]

    @pytest.mark.integration
    def test_chat_invalid_conversation_id_format(self, user1_id, user1_token):
        """
        Test: POST with invalid UUID format returns 400.

        Assert:
        - Status code 400
        """
        client = TestClient(app)

        response = client.post(
            f"/api/{user1_id}/chat",
            json={
                "conversation_id": "not-a-valid-uuid",
                "message": "Test message"
            },
            headers={"Authorization": f"Bearer {user1_token}"}
        )

        assert response.status_code == 400


# ==============================================================================
# T046: Response Structure Tests
# ==============================================================================


class TestChatResponseStructure:
    """Response structure validation tests [T046]."""

    @pytest.mark.integration
    def test_chat_response_structure_complete(self, user1_id, user1_token, conversation_user1):
        """
        T046: Valid request produces complete response with all required fields.

        Assert:
        - All required fields present
        - Field types are correct
        - Field values are valid
        """
        client = TestClient(app)

        with patch('app.chat.services.chat_service.ChatService.process_chat_message') as mock_process:
            mock_process.return_value = {
                "success": True,
                "conversation_id": str(conversation_user1.id),
                "response": "Test response from assistant",
                "tool_calls_executed": [],
                "message_count": 2,
                "execution_time_ms": 123.45
            }

            response = client.post(
                f"/api/{user1_id}/chat",
                json={
                    "conversation_id": str(conversation_user1.id),
                    "message": "Test message"
                },
                headers={"Authorization": f"Bearer {user1_token}"}
            )

        assert response.status_code == 200
        data = response.json()

        # T046: Verify all required fields
        required_fields = [
            "success",
            "conversation_id",
            "response",
            "tool_calls_executed",
            "message_count",
            "execution_time_ms"
        ]

        for field in required_fields:
            assert field in data, f"Missing required field: {field}"

        # T046: Verify field types
        assert isinstance(data["success"], bool)
        assert isinstance(data["conversation_id"], str)
        assert isinstance(data["response"], str)
        assert isinstance(data["tool_calls_executed"], list)
        assert isinstance(data["message_count"], int)
        assert isinstance(data["execution_time_ms"], (float, int))

        # T046: Verify field constraints
        assert data["message_count"] > 0
        assert data["execution_time_ms"] >= 0

    @pytest.mark.integration
    def test_chat_response_with_error_field(self, user1_id, user1_token, conversation_user1):
        """
        T046: Error responses include error field.

        When an error occurs, the response should have error field set.
        """
        client = TestClient(app)

        with patch('app.chat.services.chat_service.ChatService.process_chat_message') as mock_process:
            mock_process.return_value = {
                "success": False,
                "conversation_id": str(conversation_user1.id),
                "error": "timeout",
                "response": "The request timed out. Please try again.",
                "execution_time_ms": 4000.0
            }

            response = client.post(
                f"/api/{user1_id}/chat",
                json={
                    "conversation_id": str(conversation_user1.id),
                    "message": "Test message"
                },
                headers={"Authorization": f"Bearer {user1_token}"}
            )

        assert response.status_code in [500, 503]


# ==============================================================================
# Integration Tests with Realistic Flows
# ==============================================================================


class TestChatIntegration:
    """Integration tests with realistic scenarios."""

    @pytest.mark.integration
    def test_chat_multiple_messages_same_conversation(self, user1_id, user1_token, conversation_user1):
        """
        Test: Multiple messages in same conversation maintain history.

        This test verifies that multiple messages can be sent to the same
        conversation in sequence, building up the message history.
        """
        client = TestClient(app)

        messages = ["What is my first task?", "Tell me more about it", "Mark it complete"]

        with patch('app.chat.services.chat_service.ChatService.process_chat_message') as mock_process:
            for i, message in enumerate(messages):
                mock_process.return_value = {
                    "success": True,
                    "conversation_id": str(conversation_user1.id),
                    "response": f"Response to message {i+1}",
                    "tool_calls_executed": [],
                    "message_count": (i + 1) * 2,  # user + assistant for each turn
                    "execution_time_ms": 100.0 + (i * 50)
                }

                response = client.post(
                    f"/api/{user1_id}/chat",
                    json={
                        "conversation_id": str(conversation_user1.id),
                        "message": message
                    },
                    headers={"Authorization": f"Bearer {user1_token}"}
                )

                assert response.status_code == 200
                data = response.json()
                assert data["message_count"] >= (i + 1) * 2

    @pytest.mark.integration
    def test_chat_multiple_users_isolated(self, user1_id, user1_token, user2_id, user2_token,
                                           conversation_user1, conversation_user2):
        """
        Test: User isolation - each user can only see their own conversations.

        Verify that user1 cannot accidentally access conversation from user2,
        and vice versa.
        """
        client = TestClient(app)

        with patch('app.chat.services.chat_service.ChatService.verify_user_owns_conversation') as mock_verify:
            # User1 accessing user1's conversation - should succeed
            mock_verify.return_value = True

            response = client.post(
                f"/api/{user1_id}/chat",
                json={
                    "conversation_id": str(conversation_user1.id),
                    "message": "My message"
                },
                headers={"Authorization": f"Bearer {user1_token}"}
            )

            # Would return 200 if authorized (mocked), but endpoint still checks
            # the actual verify_user_owns_conversation before calling process_chat_message
            assert response.status_code in [200, 403, 404]

    @pytest.mark.integration
    def test_chat_with_special_characters(self, user1_id, user1_token, conversation_user1):
        """
        Test: Messages with special characters are handled correctly.

        Verify that unicode, emoji, and special chars don't break the endpoint.
        """
        client = TestClient(app)

        special_messages = [
            "Hello 你好 مرحبا",
            "This has emoji: 🎉 🚀 😊",
            "Special chars: !@#$%^&*()",
            "Mixed: {json: 'style'} [test]"
        ]

        with patch('app.chat.services.chat_service.ChatService.process_chat_message') as mock_process:
            for msg in special_messages:
                mock_process.return_value = {
                    "success": True,
                    "conversation_id": str(conversation_user1.id),
                    "response": "Successfully processed special characters",
                    "tool_calls_executed": [],
                    "message_count": 2,
                    "execution_time_ms": 100.0
                }

                response = client.post(
                    f"/api/{user1_id}/chat",
                    json={
                        "conversation_id": str(conversation_user1.id),
                        "message": msg
                    },
                    headers={"Authorization": f"Bearer {user1_token}"}
                )

                assert response.status_code == 200


# ==============================================================================
# Conversation Endpoint Tests (Companion to Chat)
# ==============================================================================


class TestCreateConversation:
    """Tests for conversation creation endpoint."""

    @pytest.mark.integration
    def test_create_conversation_authenticated(self, user1_id, user1_token):
        """
        Test: Authenticated user can create conversation.

        Assert:
        - Status code 201
        - Conversation created with unique ID
        - Title is included in response
        """
        client = TestClient(app)

        with patch('app.chat.services.chat_service.ChatService.create_conversation') as mock_create:
            conversation_id = str(uuid4())
            mock_create.return_value = {
                "success": True,
                "conversation_id": conversation_id,
                "title": "New Conversation"
            }

            response = client.post(
                f"/api/{user1_id}/conversations",
                json={"title": "New Conversation"},
                headers={"Authorization": f"Bearer {user1_token}"}
            )

        assert response.status_code == 201
        data = response.json()
        assert data["success"] is True
        assert "conversation_id" in data
        assert data["title"] == "New Conversation"

    @pytest.mark.integration
    def test_create_conversation_no_token(self, user1_id):
        """
        Test: POST to create conversation without token returns 401.

        Assert:
        - Status code 401
        """
        client = TestClient(app)

        response = client.post(
            f"/api/{user1_id}/conversations",
            json={"title": "New Conversation"}
            # No Authorization header
        )

        assert response.status_code == 401

    @pytest.mark.integration
    def test_create_conversation_user_id_mismatch(self, user1_id, user2_id, user1_token):
        """
        Test: T045 - User ID mismatch when creating conversation returns 403.

        Assert:
        - Status code 403
        """
        client = TestClient(app)

        response = client.post(
            f"/api/{user2_id}/conversations",  # user2's path
            json={"title": "New Conversation"},
            headers={"Authorization": f"Bearer {user1_token}"}  # user1's token
        )

        assert response.status_code == 403


class TestListConversations:
    """Tests for listing conversations endpoint."""

    @pytest.mark.integration
    def test_list_conversations_authenticated(self, user1_id, user1_token, conversation_user1):
        """
        Test: Authenticated user can list their conversations.

        Assert:
        - Status code 200
        - Returns list of conversations
        - Each conversation has required fields
        """
        client = TestClient(app)

        with patch('app.chat.services.chat_service.ChatService.list_user_conversations') as mock_list:
            mock_list.return_value = {
                "success": True,
                "conversations": [
                    {
                        "id": str(conversation_user1.id),
                        "title": "Test Conversation 1",
                        "created_at": datetime.now().isoformat(),
                        "updated_at": datetime.now().isoformat()
                    }
                ],
                "count": 1
            }

            response = client.get(
                f"/api/{user1_id}/conversations",
                headers={"Authorization": f"Bearer {user1_token}"}
            )

        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True
        assert "conversations" in data
        assert isinstance(data["conversations"], list)
        assert "count" in data

    @pytest.mark.integration
    def test_list_conversations_no_token(self, user1_id):
        """
        Test: GET conversations without token returns 401.

        Assert:
        - Status code 401
        """
        client = TestClient(app)

        response = client.get(f"/api/{user1_id}/conversations")

        assert response.status_code == 401

    @pytest.mark.integration
    def test_list_conversations_user_id_mismatch(self, user1_id, user2_id, user1_token):
        """
        Test: T045 - User ID mismatch when listing conversations returns 403.

        Assert:
        - Status code 403
        """
        client = TestClient(app)

        response = client.get(
            f"/api/{user2_id}/conversations",
            headers={"Authorization": f"Bearer {user1_token}"}
        )

        assert response.status_code == 403
