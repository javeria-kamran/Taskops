"""Custom exception classes for todo application.

This module defines application-specific exceptions for better error handling.
"""


class TodoAppError(Exception):
    """Base exception for all todo application errors."""
    pass


class ValidationError(TodoAppError):
    """Raised when input validation fails.

    Used for:
    - Title too long (>200 chars)
    - Title empty
    - Description too long (>1000 chars)
    - Invalid input types
    """
    pass


class TaskNotFoundError(TodoAppError):
    """Raised when a task ID doesn't exist.

    Used when attempting to:
    - Get a non-existent task
    - Update a non-existent task
    - Delete a non-existent task
    - Toggle completion of a non-existent task
    """
    pass
