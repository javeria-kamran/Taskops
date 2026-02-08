"""Unit tests for input validators."""

import pytest
from src.lib.validators import (
    validate_title,
    validate_description,
    validate_task_id
)
from src.lib.exceptions import ValidationError


class TestValidateTitle:
    """Test title validation."""

    def test_validate_title_accepts_valid_title(self):
        """Test that valid titles are accepted."""
        result = validate_title("Valid task title")
        assert result == "Valid task title"

    def test_validate_title_strips_whitespace(self):
        """Test that whitespace is stripped from title."""
        result = validate_title("  Title with spaces  ")
        assert result == "Title with spaces"

    def test_validate_title_accepts_max_length(self):
        """Test that title with exactly 200 characters is accepted."""
        max_title = "x" * 200
        result = validate_title(max_title)
        assert len(result) == 200

    def test_validate_title_rejects_empty_string(self):
        """Test that empty string is rejected."""
        with pytest.raises(ValidationError, match="Title cannot be empty"):
            validate_title("")

    def test_validate_title_rejects_whitespace_only(self):
        """Test that whitespace-only string is rejected."""
        with pytest.raises(ValidationError, match="Title cannot be empty"):
            validate_title("   ")

        with pytest.raises(ValidationError, match="Title cannot be empty"):
            validate_title("\t\n")

    def test_validate_title_rejects_too_long(self):
        """Test that title over 200 characters is rejected."""
        long_title = "x" * 201

        with pytest.raises(ValidationError, match="Title must be 200 characters or less"):
            validate_title(long_title)

    def test_validate_title_accepts_special_characters(self):
        """Test that special characters are accepted."""
        result = validate_title("Task #1: Buy groceries @ store!")
        assert result == "Task #1: Buy groceries @ store!"


class TestValidateDescription:
    """Test description validation."""

    def test_validate_description_accepts_valid_description(self):
        """Test that valid descriptions are accepted."""
        result = validate_description("Valid description text")
        assert result == "Valid description text"

    def test_validate_description_strips_whitespace(self):
        """Test that whitespace is stripped from description."""
        result = validate_description("  Description with spaces  ")
        assert result == "Description with spaces"

    def test_validate_description_accepts_empty_string(self):
        """Test that empty string is accepted for description."""
        result = validate_description("")
        assert result == ""

    def test_validate_description_accepts_max_length(self):
        """Test that description with exactly 1000 characters is accepted."""
        max_desc = "x" * 1000
        result = validate_description(max_desc)
        assert len(result) == 1000

    def test_validate_description_rejects_too_long(self):
        """Test that description over 1000 characters is rejected."""
        long_desc = "x" * 1001

        with pytest.raises(ValidationError, match="Description must be 1000 characters or less"):
            validate_description(long_desc)

    def test_validate_description_accepts_multiline(self):
        """Test that multiline descriptions are accepted."""
        multiline = "Line 1\nLine 2\nLine 3"
        result = validate_description(multiline)
        assert result == multiline


class TestValidateTaskId:
    """Test task ID validation."""

    def test_validate_task_id_accepts_valid_id(self):
        """Test that valid task IDs are accepted."""
        assert validate_task_id("1") == 1
        assert validate_task_id("42") == 42
        assert validate_task_id("999") == 999

    def test_validate_task_id_rejects_zero(self):
        """Test that zero is rejected."""
        with pytest.raises(ValidationError, match="Task ID must be a positive number"):
            validate_task_id("0")

    def test_validate_task_id_rejects_negative(self):
        """Test that negative numbers are rejected."""
        with pytest.raises(ValidationError, match="Task ID must be a positive number"):
            validate_task_id("-1")

        with pytest.raises(ValidationError, match="Task ID must be a positive number"):
            validate_task_id("-42")

    def test_validate_task_id_rejects_non_numeric(self):
        """Test that non-numeric input is rejected."""
        with pytest.raises(ValidationError, match="Please enter a valid task ID number"):
            validate_task_id("abc")

        with pytest.raises(ValidationError, match="Please enter a valid task ID number"):
            validate_task_id("one")

    def test_validate_task_id_rejects_decimal(self):
        """Test that decimal numbers are rejected."""
        with pytest.raises(ValidationError, match="Please enter a valid task ID number"):
            validate_task_id("1.5")

        with pytest.raises(ValidationError, match="Please enter a valid task ID number"):
            validate_task_id("3.14")

    def test_validate_task_id_rejects_empty_string(self):
        """Test that empty string is rejected."""
        with pytest.raises(ValidationError, match="Please enter a valid task ID number"):
            validate_task_id("")

    def test_validate_task_id_rejects_whitespace(self):
        """Test that whitespace is rejected."""
        with pytest.raises(ValidationError, match="Please enter a valid task ID number"):
            validate_task_id("   ")
