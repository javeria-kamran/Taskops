"""
Chat module for Phase III: Todo AI Chatbot

This module contains all chat-related functionality including:
- Message persistence (Conversation, Message models)
- Chat service orchestration
- Conversation management
- Agent coordination

[FROM SPEC]: speckit.specify §FR1-FR5
[FROM PLAN]: plan.md - Phase 4-7
[FROM TASKS]: T007-T008, T029-T032, T045-T050
"""

__all__ = [
    "Conversation",
    "Message",
    "ChatService",
    "ConversationService",
    "chat_router",
]
