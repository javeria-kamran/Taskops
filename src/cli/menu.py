"""Main menu and navigation for console todo application.

This module provides the main menu interface and application loop.
"""

import sys
from src.services.task_manager import TaskManager
from src.lib.exceptions import ValidationError, TaskNotFoundError
from src.cli.handlers import (
    handle_add_task,
    handle_view_tasks,
    handle_update_task,
    handle_delete_task,
    handle_mark_complete
)


# Global task manager instance
task_manager = TaskManager()


def display_menu():
    """Display the main menu with all available options."""
    print("\n" + "=" * 40)
    print("        Todo Application")
    print("=" * 40)
    print("\n1. Add Task")
    print("2. View Tasks")
    print("3. Update Task")
    print("4. Delete Task")
    print("5. Mark Task as Complete/Incomplete")
    print("6. Exit")
    print()


def validate_menu_choice(choice: str) -> int:
    """Validate menu choice input.

    Args:
        choice: User input string

    Returns:
        Validated choice as integer (1-6)

    Raises:
        ValueError: If choice is not a valid number between 1 and 6
    """
    try:
        choice_int = int(choice)
        if choice_int < 1 or choice_int > 6:
            raise ValueError("Choice must be between 1 and 6")
        return choice_int
    except ValueError:
        raise ValueError("Invalid option. Please enter a number between 1 and 6.")


def handle_exit() -> bool:
    """Handle exit option with confirmation.

    Returns:
        True if user confirms exit, False otherwise
    """
    print("\nAre you sure you want to exit? All data will be lost. (yes/no): ", end="")
    confirmation = input().strip().lower()

    if confirmation == "yes":
        print("\nThank you for using Todo Application!")
        print("Goodbye!\n")
        return True
    return False


def main():
    """Main application loop with menu navigation."""
    try:
        while True:
            display_menu()
            print("Enter your choice (1-6): ", end="")

            try:
                choice_str = input()
                choice = validate_menu_choice(choice_str)

                if choice == 1:
                    # Add Task
                    handle_add_task(task_manager)
                    input("\nPress Enter to continue...")

                elif choice == 2:
                    # View Tasks
                    handle_view_tasks(task_manager)
                    input("\nPress Enter to continue...")

                elif choice == 3:
                    # Update Task
                    handle_update_task(task_manager)
                    input("\nPress Enter to continue...")

                elif choice == 4:
                    # Delete Task
                    handle_delete_task(task_manager)
                    input("\nPress Enter to continue...")

                elif choice == 5:
                    # Mark Complete
                    handle_mark_complete(task_manager)
                    input("\nPress Enter to continue...")

                elif choice == 6:
                    # Exit
                    if handle_exit():
                        break

            except ValueError as e:
                print(f"\n{e}")
                input("\nPress Enter to continue...")

    except KeyboardInterrupt:
        # Handle Ctrl+C gracefully
        print("\n\nApplication interrupted by user.")
        print("Goodbye!\n")
        sys.exit(0)


if __name__ == "__main__":
    main()
