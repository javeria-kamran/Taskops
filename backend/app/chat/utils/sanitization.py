"""
T044: Input Sanitization Utility

Sanitizes user input to prevent XSS, injection attacks.
Validates length limits.
Strips dangerous characters.

Security considerations:
- SQL injection: Handled by SQLAlchemy ORM parameterized queries
- XSS: Prevent malicious HTML/JS in stored messages
- Length limits: Enforce via schema validation
"""

import logging
import re
from typing import Optional

logger = logging.getLogger(__name__)


class SanitizationError(Exception):
    """Input sanitization failed."""
    pass


def sanitize_message(message: str, max_length: int = 4096) -> str:
    """
    Sanitize chat message for safety.

    Removes:
    - Control characters (except newlines, tabs)
    - HTML tags and scripts
    - Excessive whitespace

    Args:
        message: Raw message from user
        max_length: Maximum allowed length (default: 4096)

    Returns:
        str: Sanitized message

    Raises:
        SanitizationError: If message is invalid or too long
    """
    if not message:
        raise SanitizationError("Message cannot be empty")

    if not isinstance(message, str):
        raise SanitizationError("Message must be a string")

    if len(message) > max_length:
        raise SanitizationError(f"Message exceeds max length of {max_length} characters")

    # Strip leading/trailing whitespace
    sanitized = message.strip()

    if not sanitized:
        raise SanitizationError("Message cannot be empty or whitespace only")

    # Remove control characters except newlines and tabs
    sanitized = re.sub(r'[\x00-\x08\x0b\x0c\x0e-\x1f\x7f-\x9f]', '', sanitized)

    # Remove HTML/JavaScript tags (basic prevention)
    # This prevents storing markup that could be exploited on frontend
    sanitized = re.sub(r'<script[^>]*>.*?</script>', '', sanitized, flags=re.IGNORECASE | re.DOTALL)
    sanitized = re.sub(r'<iframe[^>]*>.*?</iframe>', '', sanitized, flags=re.IGNORECASE | re.DOTALL)
    sanitized = re.sub(r'on\w+\s*=\s*["\'][^"\']*["\']', '', sanitized, flags=re.IGNORECASE)

    # Limit consecutive whitespace to max 1 newline and 1 space
    sanitized = re.sub(r' {2,}', ' ', sanitized)  # Multiple spaces → single space
    sanitized = re.sub(r'\t+', ' ', sanitized)    # Tabs → single space
    sanitized = re.sub(r'\n{3,}', '\n\n', sanitized)  # Multiple newlines → max 2

    logger.debug(f"[T044] Sanitized message: {len(message)} → {len(sanitized)} chars")
    return sanitized


def sanitize_conversation_title(title: Optional[str], max_length: int = 200) -> Optional[str]:
    """
    Sanitize conversation title.

    Args:
        title: Raw title from user (can be None)
        max_length: Maximum allowed length

    Returns:
        str or None: Sanitized title, or None if input was None

    Raises:
        SanitizationError: If title is invalid
    """
    if title is None:
        return None

    if not isinstance(title, str):
        raise SanitizationError("Title must be a string")

    if len(title) > max_length:
        raise SanitizationError(f"Title exceeds max length of {max_length} characters")

    # Strip whitespace
    sanitized = title.strip()

    if not sanitized:
        return None

    # Remove control characters
    sanitized = re.sub(r'[\x00-\x08\x0b\x0c\x0e-\x1f\x7f-\x9f]', '', sanitized)

    # Remove HTML tags
    sanitized = re.sub(r'<[^>]+>', '', sanitized)

    # Limit consecutive whitespace
    sanitized = re.sub(r' {2,}', ' ', sanitized)

    logger.debug(f"[T044] Sanitized title: {len(title)} → {len(sanitized)} chars")
    return sanitized


def validate_user_id(user_id: Optional[str]) -> bool:
    """
    Validate user_id format (should be UUID).

    Args:
        user_id: User ID to validate

    Returns:
        bool: True if valid, False otherwise
    """
    if not user_id:
        return False

    import uuid
    try:
        uuid.UUID(user_id)
        return True
    except (ValueError, TypeError):
        return False


def validate_conversation_id(conversation_id: Optional[str]) -> bool:
    """
    Validate conversation_id format (should be UUID).

    Args:
        conversation_id: Conversation ID to validate

    Returns:
        bool: True if valid, False otherwise
    """
    if not conversation_id:
        return False

    import uuid
    try:
        uuid.UUID(conversation_id)
        return True
    except (ValueError, TypeError):
        return False
