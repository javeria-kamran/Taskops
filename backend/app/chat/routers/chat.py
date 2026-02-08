"""
T036-T046: Chat API Endpoints with Security & Authentication

FastAPI router for chat operations:
- POST /api/{user_id}/chat - Process chat message with agentic loop
- POST /api/{user_id}/conversations - Create new conversation
- GET /api/{user_id}/conversations - List user's conversations

All endpoints:
- Require JWT authentication via Bearer token
- User_id matched between token claim and path parameter
- Input sanitization on all user messages
- Authorization checks via ChatService
- Call ChatService methods (which delegate to ConversationService)
- Return structured JSON responses
- Map exceptions to appropriate HTTP status codes

Security features:
- T043: JWT authentication middleware
- T045: User ownership verification
- T044: Input sanitization (XSS prevention)
- T046: Response models with type validation

No direct database logic in endpoints - all through ChatService.
"""

import logging
from typing import Optional
from uuid import UUID
from fastapi import APIRouter, Depends, HTTPException, Path, Body, status
from fastapi.security import HTTPBearer, HTTPCredentials
from pydantic import BaseModel, Field
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_session
from app.chat.services.chat_service import ChatService
from app.chat.middleware.auth import get_authenticated_user_id
from app.chat.utils.sanitization import (
    sanitize_message,
    sanitize_conversation_title,
    SanitizationError
)

logger = logging.getLogger(__name__)

# Create router with authentication
router = APIRouter(prefix="/api", tags=["chat"])
security = HTTPBearer(auto_error=False)


# ============================================================================
# Request/Response Models
# ============================================================================


class ChatMessageRequest(BaseModel):
    """Request for processing a chat message."""

    conversation_id: str = Field(
        ...,
        description="UUID of conversation to continue",
        example="550e8400-e29b-41d4-a716-446655440001"
    )
    message: str = Field(
        ...,
        min_length=1,
        max_length=4096,
        description="User message",
        example="What are my tasks?"
    )


class CreateConversationRequest(BaseModel):
    """Request for creating a new conversation."""

    title: Optional[str] = Field(
        None,
        max_length=200,
        description="Conversation title",
        example="Project Planning"
    )


class ChatMessageResponse(BaseModel):
    """Response for chat message processing."""

    success: bool
    conversation_id: str
    response: str
    tool_calls_executed: list
    message_count: int
    execution_time_ms: float
    error: Optional[str] = None


class CreateConversationResponse(BaseModel):
    """Response for conversation creation."""

    success: bool
    conversation_id: str
    title: str
    error: Optional[str] = None


class ConversationSummary(BaseModel):
    """Summary of a conversation."""

    id: str
    title: str
    created_at: str
    updated_at: str


class ListConversationsResponse(BaseModel):
    """Response for listing conversations."""

    success: bool
    conversations: list[ConversationSummary]
    count: int
    error: Optional[str] = None


# ============================================================================
# Endpoints
# ============================================================================


@router.post(
    "/{user_id}/chat",
    response_model=ChatMessageResponse,
    status_code=status.HTTP_200_OK,
    summary="Process Chat Message",
    description="Send a message to the agent in a conversation with full agentic loop",
    responses={
        200: {"description": "Chat processed successfully"},
        400: {"description": "Invalid request"},
        401: {"description": "Unauthorized - missing/invalid token"},
        403: {"description": "Forbidden - user doesn't own conversation"},
        404: {"description": "Conversation not found"},
        500: {"description": "Server error"}
    }
)
async def chat(
    user_id: str = Path(
        ...,
        description="User ID (must match token)",
        example="550e8400-e29b-41d4-a716-446655440000"
    ),
    request: ChatMessageRequest = Body(...),
    session: AsyncSession = Depends(get_session),
    authenticated_user_id: str = Depends(get_authenticated_user_id)
) -> ChatMessageResponse:
    """
    Process a chat message in a conversation with full agentic loop (T036-T046).

    Security:
    - T043: Requires valid JWT token in Authorization header
    - T045: Validates user owns conversation
    - T044: Sanitizes message input (XSS prevention)

    Flow:
    1. Authenticate user via JWT token
    2. Verify path user_id matches token user_id
    3. Sanitize message input
    4. Validate user owns conversation
    5. Append user message to conversation
    6. Load conversation history
    7. Invoke OpenAI agent with tools
    8. Execute any tool calls via ToolExecutor
    9. Persist assistant response
    10. Return response

    Request body:
    ```json
    {
        "conversation_id": "uuid",
        "message": "What are my tasks?"
    }
    ```

    Response:
    ```json
    {
        "success": true,
        "conversation_id": "uuid",
        "response": "You have 5 tasks...",
        "tool_calls_executed": [],
        "message_count": 2,
        "execution_time_ms": 1234.5
    }
    ```
    """
    try:
        # Step 1: T043 - Verify JWT authentication
        logger.debug(f"[T043] JWT authentication successful for user {authenticated_user_id}")

        # Step 2: T045 - Verify path user_id matches authenticated user
        if user_id != authenticated_user_id:
            logger.warning(
                f"[T045] User ID mismatch: path={user_id}, token={authenticated_user_id}"
            )
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="User ID in path does not match authenticated user"
            )

        logger.info(
            f"[T036] Received chat request from authenticated user {user_id} "
            f"in conversation {request.conversation_id}"
        )

        # Step 3: T044 - Sanitize message input
        try:
            sanitized_message = sanitize_message(request.message)
            logger.debug(f"[T044] Message sanitized successfully")
        except SanitizationError as e:
            logger.warning(f"[T044] Sanitization failed: {e}")
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Invalid message: {str(e)}"
            )

        # Step 4: Validate conversation_id is a valid UUID
        try:
            conversation_id = UUID(request.conversation_id)
        except ValueError:
            logger.warning(f"[T037] Invalid conversation ID format: {request.conversation_id}")
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Invalid conversation_id format. Must be a valid UUID."
            )

        # Step 5: T045 - Authorize user owns conversation
        user_owns_conversation = await ChatService.verify_user_owns_conversation(
            session=session,
            conversation_id=conversation_id,
            user_id=user_id
        )

        if not user_owns_conversation:
            logger.warning(
                f"[T045] Authorization failed: user {user_id} does not own conversation {conversation_id}"
            )
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="You don't have access to this conversation"
            )

        logger.debug(f"[T045] Authorization check passed")

        # Step 6-10: Call ChatService (no direct DB access here)
        result = await ChatService.process_chat_message(
            session=session,
            conversation_id=conversation_id,
            user_id=user_id,
            user_message=sanitized_message
        )

        # Check if operation was successful
        if not result.get("success"):
            logger.warning(
                f"[T036] Chat processing failed: {result.get('error', 'unknown')} "
                f"for user {user_id}"
            )

            # Map error types to HTTP status codes
            error_type = result.get("error", "unknown")
            if error_type == "conversation_not_found":
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail="Conversation not found or you don't have access to it"
                )
            elif error_type in ("timeout", "rate_limit", "api_error"):
                raise HTTPException(
                    status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                    detail=result.get("response", "Service temporarily unavailable")
                )
            else:
                raise HTTPException(
                    status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                    detail=result.get("response", "An unexpected error occurred")
                )

        logger.info(f"[T036] Chat processed successfully for user {user_id}")
        return ChatMessageResponse(**result)

    except HTTPException:
        # Re-raise HTTP exceptions
        raise
    except Exception as e:
        logger.error(f"[T036] Unhandled exception in chat endpoint: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="An unexpected error occurred. Please try again."
        )


@router.post(
    "/{user_id}/conversations",
    response_model=CreateConversationResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Create Conversation",
    description="Create a new conversation",
    responses={
        201: {"description": "Conversation created successfully"},
        400: {"description": "Invalid request"},
        401: {"description": "Unauthorized - missing/invalid token"},
        403: {"description": "Forbidden - user ID mismatch"},
        500: {"description": "Server error"}
    }
)
async def create_conversation(
    user_id: str = Path(
        ...,
        description="User ID (must match token)",
        example="550e8400-e29b-41d4-a716-446655440000"
    ),
    request: CreateConversationRequest = Body(default_factory=CreateConversationRequest),
    session: AsyncSession = Depends(get_session),
    authenticated_user_id: str = Depends(get_authenticated_user_id)
) -> CreateConversationResponse:
    """
    Create a new conversation (T024 + T043, T045).

    Security:
    - T043: Requires valid JWT token
    - T045: Verifies user ID matches token

    Request body (optional):
    ```json
    {
        "title": "Project Planning"
    }
    ```

    Response:
    ```json
    {
        "success": true,
        "conversation_id": "uuid",
        "title": "Project Planning"
    }
    ```
    """
    try:
        # T043 - Verify authentication
        logger.debug(f"[T043] JWT authentication successful for user {authenticated_user_id}")

        # T045 - Verify path user_id matches authenticated user
        if user_id != authenticated_user_id:
            logger.warning(
                f"[T045] User ID mismatch: path={user_id}, token={authenticated_user_id}"
            )
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="User ID in path does not match authenticated user"
            )

        # T044 - Sanitize title if provided
        sanitized_title = None
        if request.title:
            try:
                sanitized_title = sanitize_conversation_title(request.title)
                logger.debug(f"[T044] Conversation title sanitized")
            except SanitizationError as e:
                logger.warning(f"[T044] Title sanitization failed: {e}")
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail=f"Invalid title: {str(e)}"
                )

        logger.info(f"[T038] Creating conversation for authenticated user {user_id}")

        # Call ChatService
        result = await ChatService.create_conversation(
            session=session,
            user_id=user_id,
            title=sanitized_title
        )

        if not result.get("success"):
            logger.error(f"[T038] Failed to create conversation: {result.get('error')}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to create conversation"
            )

        logger.info(f"[T038] Conversation created: {result.get('conversation_id')}")
        return CreateConversationResponse(**result)

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"[T038] Unhandled exception: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="An unexpected error occurred"
        )


@router.get(
    "/{user_id}/conversations",
    response_model=ListConversationsResponse,
    status_code=status.HTTP_200_OK,
    summary="List Conversations",
    description="List user's conversations",
    responses={
        200: {"description": "Conversations retrieved successfully"},
        401: {"description": "Unauthorized - missing/invalid token"},
        403: {"description": "Forbidden - user ID mismatch"},
        500: {"description": "Server error"}
    }
)
async def list_conversations(
    user_id: str = Path(
        ...,
        description="User ID (must match token)",
        example="550e8400-e29b-41d4-a716-446655440000"
    ),
    limit: int = 20,
    session: AsyncSession = Depends(get_session),
    authenticated_user_id: str = Depends(get_authenticated_user_id)
) -> ListConversationsResponse:
    """
    List user's conversations ordered by most recent first (T025 + T043, T045).

    Security:
    - T043: Requires valid JWT token
    - T045: Verifies user ID matches token

    Query parameters:
    - limit: Max conversations to return (default: 20, max: 100)

    Response:
    ```json
    {
        "success": true,
        "conversations": [
            {
                "id": "uuid",
                "title": "Project Planning",
                "created_at": "2024-01-15T10:30:00Z",
                "updated_at": "2024-01-15T11:45:00Z"
            }
        ],
        "count": 1
    }
    ```
    """
    try:
        # T043 - Verify authentication
        logger.debug(f"[T043] JWT authentication successful for user {authenticated_user_id}")

        # T045 - Verify path user_id matches authenticated user
        if user_id != authenticated_user_id:
            logger.warning(
                f"[T045] User ID mismatch: path={user_id}, token={authenticated_user_id}"
            )
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="User ID in path does not match authenticated user"
            )

        # Validate limit
        if limit < 1 or limit > 100:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="limit must be between 1 and 100"
            )

        logger.info(f"[T025] Listing conversations for authenticated user {user_id} (limit={limit})")

        # Call ChatService
        result = await ChatService.list_user_conversations(
            session=session,
            user_id=user_id,
            limit=limit
        )

        if not result.get("success"):
            logger.error(f"[T025] Failed to list conversations: {result.get('error')}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to retrieve conversations"
            )

        logger.info(f"[T025] Listed {result.get('count')} conversations for authenticated user {user_id}")
        return ListConversationsResponse(**result)

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"[T025] Unhandled exception: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="An unexpected error occurred"
        )
