"""
T028: Tool Registry

Centralized registry of task management tools with JSON schemas.
Used by AgentFactory to inject available tools into OpenAI agent.

Tools:
1. add_task - Create a new task
2. list_tasks - Show user's tasks
3. complete_task - Mark task as done
4. delete_task - Remove a task
5. update_task - Modify task details
"""

import logging

logger = logging.getLogger(__name__)


def get_tool_schemas() -> dict[str, dict]:
    """
    Get all tool JSON schemas for OpenAI agent.

    Returns:
        Dict mapping tool_name -> OpenAI tool schema
    """
    return {
        "add_task": {
            "name": "add_task",
            "description": "Create a new task with title and optional description",
            "parameters": {
                "type": "object",
                "properties": {
                    "title": {
                        "type": "string",
                        "description": "Task title (required, max 200 chars)",
                        "maxLength": 200
                    },
                    "description": {
                        "type": "string",
                        "description": "Task description (optional, max 1024 chars)",
                        "maxLength": 1024
                    },
                    "priority": {
                        "type": "string",
                        "enum": ["low", "medium", "high"],
                        "description": "Task priority (default: medium)"
                    },
                    "due_date": {
                        "type": "string",
                        "description": "Due date in ISO format (optional)"
                    }
                },
                "required": ["title"]
            }
        },

        "list_tasks": {
            "name": "list_tasks",
            "description": "List user's tasks with optional filters",
            "parameters": {
                "type": "object",
                "properties": {
                    "status": {
                        "type": "string",
                        "enum": ["all", "pending", "completed"],
                        "description": "Filter by status (default: all)"
                    },
                    "priority": {
                        "type": "string",
                        "enum": ["low", "medium", "high"],
                        "description": "Filter by priority (optional)"
                    },
                    "limit": {
                        "type": "integer",
                        "description": "Max tasks to return (default: 20, max: 100)",
                        "minimum": 1,
                        "maximum": 100
                    }
                },
                "required": []
            }
        },

        "complete_task": {
            "name": "complete_task",
            "description": "Mark a task as completed",
            "parameters": {
                "type": "object",
                "properties": {
                    "task_id": {
                        "type": "string",
                        "description": "UUID of task to complete"
                    }
                },
                "required": ["task_id"]
            }
        },

        "delete_task": {
            "name": "delete_task",
            "description": "Delete a task permanently",
            "parameters": {
                "type": "object",
                "properties": {
                    "task_id": {
                        "type": "string",
                        "description": "UUID of task to delete"
                    }
                },
                "required": ["task_id"]
            }
        },

        "update_task": {
            "name": "update_task",
            "description": "Update task details (title, description, priority, or due_date)",
            "parameters": {
                "type": "object",
                "properties": {
                    "task_id": {
                        "type": "string",
                        "description": "UUID of task to update"
                    },
                    "title": {
                        "type": "string",
                        "description": "New task title (optional, max 200 chars)",
                        "maxLength": 200
                    },
                    "description": {
                        "type": "string",
                        "description": "New description (optional, max 1024 chars)",
                        "maxLength": 1024
                    },
                    "priority": {
                        "type": "string",
                        "enum": ["low", "medium", "high"],
                        "description": "New priority (optional)"
                    },
                    "due_date": {
                        "type": "string",
                        "description": "New due date in ISO format (optional)"
                    }
                },
                "required": ["task_id"]
            }
        }
    }


def get_tool_names() -> list[str]:
    """
    Get list of available tool names.

    Returns:
        List of tool names
    """
    return list(get_tool_schemas().keys())


def validate_tool_name(tool_name: str) -> bool:
    """
    Check if tool name is valid.

    Args:
        tool_name: Name to validate

    Returns:
        True if tool is registered
    """
    return tool_name in get_tool_schemas()


def get_tool_schema(tool_name: str) -> dict:
    """
    Get schema for a specific tool.

    Args:
        tool_name: Name of tool

    Returns:
        Tool schema dict

    Raises:
        KeyError: If tool not found
    """
    schemas = get_tool_schemas()
    if tool_name not in schemas:
        raise KeyError(f"Tool '{tool_name}' not found. Available: {list(schemas.keys())}")
    return schemas[tool_name]
