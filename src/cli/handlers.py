"""CLI handlers for user interactions.

This module provides handler functions for each menu option.
"""

from src.services.task_manager import TaskManager
from src.lib.exceptions import ValidationError, TaskNotFoundError


def handle_add_task(task_manager: TaskManager) -> None:
    """Handle adding a new task.

    Prompts user for title and description, then creates the task.

    Args:
        task_manager: TaskManager instance to add task to
    """
    print("\n=== Add New Task ===")
    print("\nEnter task title: ", end="")
    title = input()

    print("Enter task description (optional): ", end="")
    description = input()

    try:
        task = task_manager.add_task(title, description)
        print(f"\n✓ Task added successfully!")
        print(f"  ID: #{task.id}")
        print(f"  Title: {task.title}")
        if task.description:
            print(f"  Description: {task.description}")
    except ValidationError as e:
        print(f"\n✗ Error: {e}")


def handle_view_tasks(task_manager: TaskManager) -> None:
    """Handle viewing all tasks.

    Displays a formatted list of all tasks with their details.

    Args:
        task_manager: TaskManager instance to retrieve tasks from
    """
    print("\n=== All Tasks ===\n")

    tasks = task_manager.get_all_tasks()

    if not tasks:
        print("No tasks found. Your list is empty!")
        print("\nTip: Use option 1 to add your first task.")
        return

    # Display header
    print(f"Total tasks: {len(tasks)}\n")
    print("-" * 60)

    # Display each task
    for task in tasks:
        # Status indicator
        status = "✓" if task.completed else "☐"

        # Format output
        print(f"{status} Task #{task.id}: {task.title}")

        if task.description:
            print(f"  Description: {task.description}")

        print(f"  Status: {'Completed' if task.completed else 'Incomplete'}")
        print(f"  Created: {task.created_at.strftime('%Y-%m-%d %H:%M:%S')}")
        print("-" * 60)

    # Summary
    completed_count = sum(1 for t in tasks if t.completed)
    incomplete_count = len(tasks) - completed_count
    print(f"\nSummary: {completed_count} completed, {incomplete_count} incomplete")


def handle_update_task(task_manager: TaskManager) -> None:
    """Handle updating a task.

    Prompts user for task ID and new values, then updates the task.

    Args:
        task_manager: TaskManager instance to update task in
    """
    from src.lib.validators import validate_task_id

    print("\n=== Update Task ===")

    # Show current tasks
    tasks = task_manager.get_all_tasks()
    if not tasks:
        print("\nNo tasks available. Add a task first!")
        return

    print("\nCurrent tasks:")
    for task in tasks:
        status = "✓" if task.completed else "☐"
        print(f"  {status} #{task.id}: {task.title}")

    print("\nEnter task ID to update: ", end="")
    task_id_input = input()

    try:
        task_id = validate_task_id(task_id_input)
        task = task_manager.get_task(task_id)

        print(f"\nCurrent title: {task.title}")
        print("Enter new title (or press Enter to keep current): ", end="")
        new_title = input()

        print(f"\nCurrent description: {task.description or '(none)'}")
        print("Enter new description (or press Enter to keep current): ", end="")
        new_description = input()

        # Only update if user provided new values
        title_update = new_title if new_title.strip() else None
        desc_update = new_description if new_description else None

        if title_update is None and desc_update is None:
            print("\n No changes made.")
            return

        updated_task = task_manager.update_task(
            task_id,
            title=title_update,
            description=desc_update
        )

        print(f"\n✓ Task #{updated_task.id} updated successfully!")
        print(f"  Title: {updated_task.title}")
        if updated_task.description:
            print(f"  Description: {updated_task.description}")

    except (ValidationError, TaskNotFoundError) as e:
        print(f"\n✗ Error: {e}")


def handle_delete_task(task_manager: TaskManager) -> None:
    """Handle deleting a task.

    Prompts user for task ID and confirmation, then deletes the task.

    Args:
        task_manager: TaskManager instance to delete task from
    """
    from src.lib.validators import validate_task_id

    print("\n=== Delete Task ===")

    # Show current tasks
    tasks = task_manager.get_all_tasks()
    if not tasks:
        print("\nNo tasks available.")
        return

    print("\nCurrent tasks:")
    for task in tasks:
        status = "✓" if task.completed else "☐"
        print(f"  {status} #{task.id}: {task.title}")

    print("\nEnter task ID to delete: ", end="")
    task_id_input = input()

    try:
        task_id = validate_task_id(task_id_input)
        task = task_manager.get_task(task_id)

        # Confirmation
        print(f"\n⚠ Are you sure you want to delete this task?")
        print(f"  #{task.id}: {task.title}")
        print("  This action cannot be undone!")
        print("\nType 'yes' to confirm: ", end="")
        confirmation = input().strip().lower()

        if confirmation == "yes":
            deleted_task = task_manager.delete_task(task_id)
            print(f"\n✓ Task #{deleted_task.id} deleted successfully!")
            print(f"  Deleted: {deleted_task.title}")
        else:
            print("\n Deletion cancelled.")

    except (ValidationError, TaskNotFoundError) as e:
        print(f"\n✗ Error: {e}")


def handle_mark_complete(task_manager: TaskManager) -> None:
    """Handle marking a task as complete or incomplete.

    Prompts user for task ID, then toggles completion status.

    Args:
        task_manager: TaskManager instance to update task in
    """
    from src.lib.validators import validate_task_id

    print("\n=== Mark Task Complete/Incomplete ===")

    # Show current tasks first
    tasks = task_manager.get_all_tasks()
    if not tasks:
        print("\nNo tasks available. Add a task first!")
        return

    print("\nCurrent tasks:")
    for task in tasks:
        status = "✓" if task.completed else "☐"
        print(f"  {status} #{task.id}: {task.title}")

    print("\nEnter task ID to toggle completion: ", end="")
    task_id_input = input()

    try:
        task_id = validate_task_id(task_id_input)
        task = task_manager.toggle_complete(task_id)

        status_text = "complete" if task.completed else "incomplete"
        print(f"\n✓ Task #{task.id} marked as {status_text}!")
        print(f"  Title: {task.title}")
        print(f"  Status: {'Completed' if task.completed else 'Incomplete'}")
    except (ValidationError, TaskNotFoundError) as e:
        print(f"\n✗ Error: {e}")
