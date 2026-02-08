"""Input validation utilities for todo application.

This module provides validation functions for user inputs.
"""

from src.lib.exceptions import ValidationError


def validate_title(title: str) -> str:
    """Validate task title.

    Args:
        title: Task title to validate

    Returns:
        Stripped and validated title

    Raises:
        ValidationError: If title is empty or exceeds 200 characters
    """
    if not title or not title.strip():
        raise ValidationError("Title cannot be empty")

    title = title.strip()

    if len(title) > 200:
        raise ValidationError("Title must be 200 characters or less")

    return title


def validate_description(description: str) -> str:
    """Validate task description.

    Args:
        description: Task description to validate

    Returns:
        Stripped and validated description (empty string if None)

    Raises:
        ValidationError: If description exceeds 1000 characters
    """
    if description is None:
        return ""

    description = description.strip()

    if len(description) > 1000:
        raise ValidationError("Description must be 1000 characters or less")

    return description


def validate_task_id(task_id_input: str) -> int:
    """Validate and convert task ID input to integer.

    Args:
        task_id_input: User input for task ID

    Returns:
        Validated task ID as integer

    Raises:
        ValidationError: If input is not a valid positive integer
    """
    try:
        task_id = int(task_id_input)
        if task_id <= 0:
            raise ValidationError("Task ID must be a positive number")
        return task_id
    except ValueError:
        raise ValidationError("Please enter a valid task ID number")


def validate_yes_no(input_str: str) -> bool:
    """Validate yes/no confirmation input.

    Args:
        input_str: User input string

    Returns:
        True if input is 'yes' (case-insensitive), False otherwise
    """
    return input_str.strip().lower() == "yes"
