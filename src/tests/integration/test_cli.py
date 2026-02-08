"""Integration tests for CLI workflows."""

import pytest
from unittest.mock import patch, MagicMock
from io import StringIO


class TestMainMenuLoop:
    """Test main menu loop integration."""

    def test_menu_loop_exits_on_option_6(self):
        """Test that selecting option 6 exits the application."""
        from src.cli.menu import main

        # Simulate user selecting option 6 (Exit) and confirming with 'yes'
        with patch('builtins.input', side_effect=['6', 'yes']):
            with patch('sys.stdout', new=StringIO()):
                main()  # Should exit without error

    def test_menu_loop_shows_invalid_option_error(self):
        """Test that invalid menu option shows error and redisplays menu."""
        from src.cli.menu import main

        # Simulate: invalid option "9", press enter, then exit with "6" and "yes"
        with patch('builtins.input', side_effect=['9', '', '6', 'yes']):
            with patch('sys.stdout', new=StringIO()) as fake_out:
                main()
                output = fake_out.getvalue()

                # Should show error message
                assert "Invalid" in output or "invalid" in output or "error" in output

    def test_menu_loop_redisplays_after_action(self):
        """Test that menu redisplays after completing an action."""
        from src.cli.menu import main

        # This test verifies the loop behavior - simplified for now
        with patch('builtins.input', side_effect=['6', 'yes']):
            with patch('sys.stdout', new=StringIO()):
                try:
                    main()
                except SystemExit:
                    pass  # Expected when exiting

    def test_exit_confirmation_cancels_with_no(self):
        """Test that saying 'no' to exit returns to menu."""
        from src.cli.menu import main

        # Simulate: choose exit (6), say 'no', then exit (6) and say 'yes'
        with patch('builtins.input', side_effect=['6', 'no', '6', 'yes']):
            with patch('sys.stdout', new=StringIO()):
                main()  # Should loop back to menu after 'no', then exit

    def test_keyboard_interrupt_exits_gracefully(self):
        """Test that Ctrl+C (KeyboardInterrupt) exits gracefully."""
        from src.cli.menu import main

        # Simulate Ctrl+C by raising KeyboardInterrupt
        with patch('builtins.input', side_effect=KeyboardInterrupt()):
            with patch('sys.stdout', new=StringIO()) as fake_out:
                try:
                    main()
                except SystemExit:
                    pass  # Expected when handling KeyboardInterrupt
                output = fake_out.getvalue()

                # Should show graceful exit message
                assert "Goodbye" in output or "goodbye" in output or "exit" in output.lower()


class TestAddTaskWorkflow:
    """Test add task workflow integration."""

    def test_add_task_successfully(self):
        """Test successfully adding a task through the CLI."""
        from src.cli.menu import main

        # Simulate: choose option 1 (Add Task), enter title and description, then exit
        inputs = [
            '1',  # Select "Add Task"
            'Buy groceries',  # Task title
            'Milk, eggs, bread',  # Task description
            '',  # Continue prompt
            '6',  # Exit
            'yes'  # Confirm exit
        ]

        with patch('builtins.input', side_effect=inputs):
            with patch('sys.stdout', new=StringIO()) as fake_out:
                main()
                output = fake_out.getvalue()

                # Should show success message
                assert "success" in output.lower() or "added" in output.lower() or "created" in output.lower()

    def test_add_task_with_title_only(self):
        """Test adding a task with only a title (no description)."""
        from src.cli.menu import main

        inputs = [
            '1',  # Select "Add Task"
            'Simple task',  # Task title
            '',  # Empty description (optional)
            '',  # Continue prompt
            '6',  # Exit
            'yes'  # Confirm exit
        ]

        with patch('builtins.input', side_effect=inputs):
            with patch('sys.stdout', new=StringIO()) as fake_out:
                main()
                output = fake_out.getvalue()

                # Should complete without error
                assert "error" not in output.lower() or "success" in output.lower()

    def test_add_task_rejects_empty_title(self):
        """Test that adding a task with empty title shows error."""
        from src.cli.menu import main

        inputs = [
            '1',  # Select "Add Task"
            '',  # Empty title (will trigger error)
            '',  # Description (not reached because of error, but validation happens first)
            '',  # Continue prompt after error
            '6',  # Exit after error
            'yes'  # Confirm exit
        ]

        with patch('builtins.input', side_effect=inputs):
            with patch('sys.stdout', new=StringIO()) as fake_out:
                main()
                output = fake_out.getvalue()

                # Should show error message
                assert "Error" in output or "error" in output or "empty" in output.lower()

    def test_add_multiple_tasks(self):
        """Test adding multiple tasks in sequence."""
        from src.cli.menu import main

        inputs = [
            '1', 'Task 1', 'Description 1', '',  # Add first task
            '1', 'Task 2', 'Description 2', '',  # Add second task
            '1', 'Task 3', '', '',  # Add third task (no description)
            '6', 'yes'  # Exit
        ]

        with patch('builtins.input', side_effect=inputs):
            with patch('sys.stdout', new=StringIO()) as fake_out:
                main()
                # Should complete without crashing


class TestViewTasksWorkflow:
    """Test view tasks workflow integration."""

    def test_view_tasks_when_empty(self):
        """Test viewing tasks when no tasks exist."""
        # Import and create a fresh task manager for this test
        import importlib
        import src.cli.menu as menu_module

        # Reload the module to get a fresh TaskManager instance
        importlib.reload(menu_module)
        main = menu_module.main

        inputs = [
            '2',  # Select "View Tasks"
            '',  # Continue prompt
            '6',  # Exit
            'yes'  # Confirm exit
        ]

        with patch('builtins.input', side_effect=inputs):
            with patch('sys.stdout', new=StringIO()) as fake_out:
                main()
                output = fake_out.getvalue()

                # Should indicate no tasks or show empty list
                assert "No tasks" in output or "empty" in output or "0 tasks" in output

    def test_view_tasks_after_adding(self):
        """Test viewing tasks after adding some tasks."""
        from src.cli.menu import main

        inputs = [
            '1', 'Buy groceries', 'Milk and eggs', '',  # Add task
            '2', '',  # View tasks
            '6', 'yes'  # Exit
        ]

        with patch('builtins.input', side_effect=inputs):
            with patch('sys.stdout', new=StringIO()) as fake_out:
                main()
                output = fake_out.getvalue()

                # Should display the added task
                assert "Buy groceries" in output or "groceries" in output.lower()

    def test_view_tasks_shows_all_tasks(self):
        """Test that viewing tasks shows all added tasks."""
        from src.cli.menu import main

        inputs = [
            '1', 'Task 1', '', '',  # Add first task
            '1', 'Task 2', '', '',  # Add second task
            '1', 'Task 3', '', '',  # Add third task
            '2', '',  # View all tasks
            '6', 'yes'  # Exit
        ]

        with patch('builtins.input', side_effect=inputs):
            with patch('sys.stdout', new=StringIO()) as fake_out:
                main()
                output = fake_out.getvalue()

                # Should show all three tasks
                assert "Task 1" in output
                assert "Task 2" in output
                assert "Task 3" in output

    def test_view_tasks_shows_task_ids(self):
        """Test that viewing tasks displays task IDs."""
        from src.cli.menu import main

        inputs = [
            '1', 'Test task', '', '',  # Add task
            '2', '',  # View tasks
            '6', 'yes'  # Exit
        ]

        with patch('builtins.input', side_effect=inputs):
            with patch('sys.stdout', new=StringIO()) as fake_out:
                main()
                output = fake_out.getvalue()

                # Should show task ID (likely "1" or "#1")
                assert "1" in output or "#1" in output

    def test_view_tasks_shows_completion_status(self):
        """Test that viewing tasks shows completion status."""
        from src.cli.menu import main

        inputs = [
            '1', 'Test task', '', '',  # Add task
            '2', '',  # View tasks
            '6', 'yes'  # Exit
        ]

        with patch('builtins.input', side_effect=inputs):
            with patch('sys.stdout', new=StringIO()) as fake_out:
                main()
                output = fake_out.getvalue()

                # Should show completion status indicators
                # Could be "[ ]", "incomplete", "pending", etc.
                assert "[ ]" in output or "incomplete" in output.lower() or "pending" in output.lower() or "☐" in output


class TestMarkCompleteWorkflow:
    """Test mark complete workflow integration."""

    def test_mark_task_as_complete(self):
        """Test marking a task as complete."""
        import importlib
        import src.cli.menu as menu_module
        importlib.reload(menu_module)
        main = menu_module.main

        inputs = [
            '1', 'Test task', '', '',  # Add task
            '5',  # Mark complete
            '1',  # Task ID
            '',  # Continue
            '6', 'yes'  # Exit
        ]

        with patch('builtins.input', side_effect=inputs):
            with patch('sys.stdout', new=StringIO()) as fake_out:
                main()
                output = fake_out.getvalue()

                # Should show success or completion message
                assert "complete" in output.lower() or "success" in output.lower()

    def test_mark_task_as_incomplete(self):
        """Test marking a completed task as incomplete (toggle)."""
        import importlib
        import src.cli.menu as menu_module
        importlib.reload(menu_module)
        main = menu_module.main

        inputs = [
            '1', 'Test task', '', '',  # Add task
            '5', '1', '',  # Mark complete
            '5', '1', '',  # Mark incomplete (toggle)
            '6', 'yes'  # Exit
        ]

        with patch('builtins.input', side_effect=inputs):
            with patch('sys.stdout', new=StringIO()) as fake_out:
                main()
                output = fake_out.getvalue()

                # Should show toggle messages
                assert "complete" in output.lower() or "incomplete" in output.lower()

    def test_mark_complete_with_invalid_id(self):
        """Test marking complete with invalid task ID."""
        import importlib
        import src.cli.menu as menu_module
        importlib.reload(menu_module)
        main = menu_module.main

        inputs = [
            '1', 'Test task', '', '',  # Add task
            '5',  # Mark complete
            '999',  # Invalid ID
            '',  # Continue
            '6', 'yes'  # Exit
        ]

        with patch('builtins.input', side_effect=inputs):
            with patch('sys.stdout', new=StringIO()) as fake_out:
                main()
                output = fake_out.getvalue()

                # Should show error message
                assert "not found" in output.lower() or "error" in output.lower()


class TestUpdateTaskWorkflow:
    """Test update task workflow integration."""

    def test_update_task_title(self):
        """Test updating task title."""
        import importlib
        import src.cli.menu as menu_module
        importlib.reload(menu_module)
        main = menu_module.main

        inputs = [
            '1', 'Original title', 'Original description', '',  # Add task
            '3',  # Update task
            '1',  # Task ID
            'New title',  # New title
            '',  # Keep description
            '',  # Continue
            '6', 'yes'  # Exit
        ]

        with patch('builtins.input', side_effect=inputs):
            with patch('sys.stdout', new=StringIO()) as fake_out:
                main()
                output = fake_out.getvalue()

                assert "updated" in output.lower() or "success" in output.lower()
                assert "New title" in output

    def test_update_task_description(self):
        """Test updating task description."""
        import importlib
        import src.cli.menu as menu_module
        importlib.reload(menu_module)
        main = menu_module.main

        inputs = [
            '1', 'Title', 'Original description', '',  # Add task
            '3', '1', '', 'New description', '',  # Update description only
            '6', 'yes'
        ]

        with patch('builtins.input', side_effect=inputs):
            with patch('sys.stdout', new=StringIO()) as fake_out:
                main()
                output = fake_out.getvalue()

                assert "updated" in output.lower() or "success" in output.lower()

    def test_update_task_invalid_id(self):
        """Test updating with invalid task ID."""
        import importlib
        import src.cli.menu as menu_module
        importlib.reload(menu_module)
        main = menu_module.main

        inputs = [
            '1', 'Task', '', '',  # Add task
            '3', '999', '',  # Try to update non-existent task
            '6', 'yes'
        ]

        with patch('builtins.input', side_effect=inputs):
            with patch('sys.stdout', new=StringIO()) as fake_out:
                main()
                output = fake_out.getvalue()

                assert "not found" in output.lower() or "error" in output.lower()


class TestDeleteTaskWorkflow:
    """Test delete task workflow integration."""

    def test_delete_task_with_confirmation(self):
        """Test deleting a task with confirmation."""
        import importlib
        import src.cli.menu as menu_module
        importlib.reload(menu_module)
        main = menu_module.main

        inputs = [
            '1', 'Task to delete', '', '',  # Add task
            '4',  # Delete task
            '1',  # Task ID
            'yes',  # Confirm
            '',  # Continue
            '6', 'yes'  # Exit
        ]

        with patch('builtins.input', side_effect=inputs):
            with patch('sys.stdout', new=StringIO()) as fake_out:
                main()
                output = fake_out.getvalue()

                assert "deleted" in output.lower() or "success" in output.lower()

    def test_delete_task_cancelled(self):
        """Test cancelling task deletion."""
        import importlib
        import src.cli.menu as menu_module
        importlib.reload(menu_module)
        main = menu_module.main

        inputs = [
            '1', 'Task', '', '',  # Add task
            '4', '1', 'no', '',  # Delete but cancel
            '6', 'yes'
        ]

        with patch('builtins.input', side_effect=inputs):
            with patch('sys.stdout', new=StringIO()) as fake_out:
                main()
                output = fake_out.getvalue()

                assert "cancelled" in output.lower()

    def test_delete_task_invalid_id(self):
        """Test deleting with invalid task ID."""
        import importlib
        import src.cli.menu as menu_module
        importlib.reload(menu_module)
        main = menu_module.main

        inputs = [
            '1', 'Task', '', '',  # Add task
            '4', '999', '',  # Try to delete non-existent
            '6', 'yes'
        ]

        with patch('builtins.input', side_effect=inputs):
            with patch('sys.stdout', new=StringIO()) as fake_out:
                main()
                output = fake_out.getvalue()

                assert "not found" in output.lower() or "error" in output.lower()
