"""
Chat Router (Phase III)

[FROM TASKS]: T051-T052 - Chat Endpoint API
[FROM SPEC]: speckit.specify §FR1

Endpoints:
- POST /api/{user_id}/chat - Chat with agent
- GET /api/{user_id}/conversations - List conversations
"""

import logging
from typing import Optional
from fastapi import APIRouter, Depends, HTTPException, Path, Query
from sqlalchemy.ext.asyncio import AsyncSession

from app.chat.services.chat_service import ChatService
from app.chat.services.conversation_service import ConversationService
from app.database import get_session

logger = logging.getLogger(__name__)

# Initialize router
chat_router = APIRouter(prefix="/api", tags=["chat"])


async def get_chat_service(
    session: AsyncSession = Depends(get_session)
) -> ChatService:
    """Dependency injection for ChatService"""
    return ChatService(ConversationService())


@chat_router.post("/{user_id}/chat")
async def handle_chat(
    user_id: str = Path(..., description="UUID of user"),
    message: str = Query(..., min_length=1, max_length=4096, description="Chat message"),
    conversation_id: Optional[str] = Query(None, description="Optional conversation ID"),
    session: AsyncSession = Depends(get_session),
    chat_service: ChatService = Depends(get_chat_service)
):
    """
    Handle chat message.

    [FROM SPEC]: FR1 - Chat API Endpoint
    [FROM PLAN]: Stateless Request Cycle

    Request:
    {
        "user_id": "uuid",
        "message": "string",
        "conversation_id": "uuid (optional)"
    }

    Response:
    {
        "conversation_id": "uuid",
        "message_id": "uuid",
        "response": "string",
        "tool_calls": [...],
        "tokens": {...}
    }
    """
    try:
        logger.info(f"Chat request: user={user_id}, conversation={conversation_id}")

        result = await chat_service.handle_chat(
            session,
            user_id,
            message,
            conversation_id
        )

        logger.info(f"Chat response: {result['conversation_id']}")
        return result

    except ValueError as e:
        logger.error(f"Chat validation error: {e}")
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        logger.error(f"Chat error: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail="Internal server error")


@chat_router.get("/{user_id}/conversations")
async def list_conversations(
    user_id: str = Path(..., description="UUID of user"),
    limit: int = Query(20, ge=1, le=100, description="Max conversations"),
    session: AsyncSession = Depends(get_session),
    chat_service: ChatService = Depends(get_chat_service)
):
    """
    List user's conversations.

    [FROM SPEC]: FR5 - Multi-Turn Conversations
    """
    try:
        logger.info(f"Listing conversations for user {user_id}")

        conversations = await chat_service.get_conversations(
            session,
            user_id,
            limit
        )

        return {"conversations": conversations}

    except Exception as e:
        logger.error(f"Error listing conversations: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail="Internal server error")
