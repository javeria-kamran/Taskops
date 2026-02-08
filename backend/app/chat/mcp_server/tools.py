"""
T015: MCP Tool Definitions

Defines 5 task management tools with JSON schemas for validation and discovery.

Tools:
1. add_task: Create new task
2. list_tasks: Get user tasks with optional status filter
3. complete_task: Mark task complete
4. delete_task: Remove task
5. update_task: Modify task fields

Each tool has:
- name: Tool identifier
- description: Human-readable description
- inputSchema: JSON Schema for validation (user_id, task_id, status, etc.)
"""

from typing import Any


# Tool definitions dictionary
_TOOL_DEFINITIONS = {
    "add_task": {
        "name": "add_task",
        "description": "Create a new task for the user",
        "inputSchema": {
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
                    "description": "Task priority (optional, default: 'medium')"
                },
                "due_date": {
                    "type": "string",
                    "format": "date-time",
                    "description": "Due date in ISO 8601 format (optional)"
                }
            },
            "required": ["title"]
        }
    },
    "list_tasks": {
        "name": "list_tasks",
        "description": "Get user's tasks with optional status filter",
        "inputSchema": {
            "type": "object",
            "properties": {
                "status": {
                    "type": "string",
                    "enum": ["pending", "completed", "all"],
                    "description": "Filter by status (optional, default: 'all')"
                },
                "limit": {
                    "type": "integer",
                    "description": "Max results (optional, default: 50, max: 100)",
                    "maximum": 100
                },
                "offset": {
                    "type": "integer",
                    "description": "Pagination offset (optional, default: 0)"
                }
            }
        }
    },
    "complete_task": {
        "name": "complete_task",
        "description": "Mark a task as completed",
        "inputSchema": {
            "type": "object",
            "properties": {
                "task_id": {
                    "type": "string",
                    "format": "uuid",
                    "description": "Task ID (required)"
                }
            },
            "required": ["task_id"]
        }
    },
    "delete_task": {
        "name": "delete_task",
        "description": "Delete a task",
        "inputSchema": {
            "type": "object",
            "properties": {
                "task_id": {
                    "type": "string",
                    "format": "uuid",
                    "description": "Task ID (required)"
                }
            },
            "required": ["task_id"]
        }
    },
    "update_task": {
        "name": "update_task",
        "description": "Update task fields (title, description, priority, due_date)",
        "inputSchema": {
            "type": "object",
            "properties": {
                "task_id": {
                    "type": "string",
                    "format": "uuid",
                    "description": "Task ID (required)"
                },
                "title": {
                    "type": "string",
                    "description": "New title (optional, max 200 chars)",
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
                    "format": "date-time",
                    "description": "New due date in ISO 8601 format (optional)"
                }
            },
            "required": ["task_id"]
        }
    }
}


def register_tools() -> dict[str, dict[str, Any]]:
    """
    Register all tool definitions with MCP server.

    Returns:
        Dictionary mapping tool_name -> tool_schema
        Used by server.py to attach handlers to MCP protocol
    """
    return _TOOL_DEFINITIONS.copy()


def get_tool_definitions() -> dict[str, dict[str, Any]]:
    """
    Get all tool definitions for agent discovery.

    Returns:
        Complete tool schemas for OpenAI Agents SDK integration
    """
    return _TOOL_DEFINITIONS.copy()


def get_tool_schema(tool_name: str) -> dict[str, Any]:
    """
    Get schema for specific tool.

    Args:
        tool_name: Name of tool (e.g., 'add_task')

    Returns:
        Tool schema dict

    Raises:
        KeyError: If tool not found
    """
    return _TOOL_DEFINITIONS[tool_name].copy()


def validate_tool_name(tool_name: str) -> bool:
    """Check if tool name is valid and registered"""
    return tool_name in _TOOL_DEFINITIONS
