"""
Chat data models (Phase III)

[FROM TASKS]: T007-T008 - Database model definitions
[FROM SPEC]: speckit.specify §FR2

Models:
- Conversation: Persists user conversations
- Message: Stores individual messages in conversations
"""

from .conversation import Conversation
from .message import Message

__all__ = ["Conversation", "Message"]
