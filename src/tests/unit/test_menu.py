"""Unit tests for menu module."""

import pytest
from unittest.mock import patch, MagicMock
from io import StringIO


class TestMenuDisplay:
    """Test menu display functionality."""

    def test_display_menu_shows_all_options(self):
        """Test that menu displays all 6 options."""
        from src.cli.menu import display_menu

        with patch('sys.stdout', new=StringIO()) as fake_out:
            display_menu()
            output = fake_out.getvalue()

            # Check for all menu options
            assert "1. Add Task" in output or "1) Add Task" in output
            assert "2. View Tasks" in output or "2) View Tasks" in output
            assert "3. Update Task" in output or "3) Update Task" in output
            assert "4. Delete Task" in output or "4) Delete Task" in output
            assert "5. Mark" in output and "Complete" in output
            assert "6. Exit" in output or "6) Exit" in output

    def test_display_menu_shows_title(self):
        """Test that menu displays application title."""
        from src.cli.menu import display_menu

        with patch('sys.stdout', new=StringIO()) as fake_out:
            display_menu()
            output = fake_out.getvalue()

            # Check for title/header
            assert "Todo" in output or "TODO" in output or "Menu" in output


class TestMenuInputValidation:
    """Test menu input validation."""

    def test_validate_menu_choice_accepts_valid_numbers(self):
        """Test that valid menu choices (1-6) are accepted."""
        from src.cli.menu import validate_menu_choice

        for choice in ["1", "2", "3", "4", "5", "6"]:
            result = validate_menu_choice(choice)
            assert result in [1, 2, 3, 4, 5, 6]

    def test_validate_menu_choice_rejects_invalid_numbers(self):
        """Test that invalid numbers are rejected."""
        from src.cli.menu import validate_menu_choice

        invalid_choices = ["0", "7", "10", "-1", "99"]
        for choice in invalid_choices:
            with pytest.raises((ValueError, Exception)):
                validate_menu_choice(choice)

    def test_validate_menu_choice_rejects_non_numeric(self):
        """Test that non-numeric input is rejected."""
        from src.cli.menu import validate_menu_choice

        invalid_choices = ["abc", "one", "", " ", "1.5", "1a"]
        for choice in invalid_choices:
            with pytest.raises((ValueError, Exception)):
                validate_menu_choice(choice)
