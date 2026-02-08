"""
MCP Server Implementation (Phase III)

[FROM TASKS]: T019 - MCP Server Startup
[FROM TASKS]: T035-T041 - Tool Implementation
[FROM SPEC]: speckit.specify §FR3

MCPServer:
- Initializes MCP protocol (stdio transport)
- Registers tools with JSON schemas
- Executes tool calls
- Handles errors gracefully

Tools (MVP):
- add_task: Create new task
- list_tasks: List tasks with optional filtering

Future Tools:
- complete_task: Mark task complete
- delete_task: Delete task
- update_task: Update task fields
"""

import logging
import json
from typing import Any, Dict, List, Optional, Callable
from abc import ABC, abstractmethod

logger = logging.getLogger(__name__)


class ToolSchema:
    """JSON Schema definition for a tool"""

    def __init__(
        self,
        name: str,
        description: str,
        input_schema: Dict[str, Any],
        handler: Callable
    ):
        self.name = name
        self.description = description
        self.input_schema = input_schema
        self.handler = handler

    def to_dict(self) -> Dict[str, Any]:
        """Convert to MCP tool definition"""
        return {
            "name": self.name,
            "description": self.description,
            "inputSchema": self.input_schema
        }


class MCPServer:
    """
    MCP Server for task management tools.

    [FROM SPEC]: speckit.specify §FR3
    [FROM PLAN]: Phase 3 - MCP Tool Layer

    Manages tool registration and execution.
    """

    def __init__(self):
        """Initialize MCP server"""
        self.tools: Dict[str, ToolSchema] = {}
        self.initialized = False
        logger.info("MCPServer instance created")

    async def initialize(self):
        """
        Initialize MCP server on startup.

        [FROM TASKS]: T019 - MCP Server Startup Integration

        Registers all available tools with schemas.
        """
        logger.info("Initializing MCP Server...")

        # Register MVP tools (Phase III MVP scope)
        self._register_add_task_tool()
        self._register_list_tasks_tool()

        # Register placeholder for future tools
        self._register_placeholder_tools()

        self.initialized = True
        logger.info(f"MCP Server initialized with {len(self.tools)} tools")

    async def shutdown(self):
        """Shutdown MCP server gracefully"""
        logger.info("Shutting down MCP Server...")
        self.initialized = False

    def _register_add_task_tool(self):
        """
        Register add_task tool.

        [FROM TASKS]: T036 - Implement MCP Tool: add_task
        [FROM SPEC]: speckit.specify §FR3
        """
        schema = {
            "type": "object",
            "properties": {
                "user_id": {
                    "type": "string",
                    "description": "UUID of user"
                },
                "title": {
                    "type": "string",
                    "description": "Task title (1-256 chars)",
                    "minLength": 1,
                    "maxLength": 256
                },
                "description": {
                    "type": "string",
                    "description": "Optional task description",
                    "maxLength": 2048
                }
            },
            "required": ["user_id", "title"]
        }

        tool = ToolSchema(
            name="add_task",
            description="Create a new todo task",
            input_schema=schema,
            handler=self._execute_add_task
        )

        self.tools["add_task"] = tool
        logger.debug("Registered tool: add_task")

    def _register_list_tasks_tool(self):
        """
        Register list_tasks tool.

        [FROM TASKS]: T037 - Implement MCP Tool: list_tasks
        [FROM SPEC]: speckit.specify §FR3
        """
        schema = {
            "type": "object",
            "properties": {
                "user_id": {
                    "type": "string",
                    "description": "UUID of user"
                },
                "status": {
                    "type": "string",
                    "description": "Filter by status: all, pending, completed",
                    "enum": ["all", "pending", "completed"],
                    "default": "all"
                },
                "limit": {
                    "type": "integer",
                    "description": "Max tasks to return (1-100)",
                    "minimum": 1,
                    "maximum": 100,
                    "default": 50
                }
            },
            "required": ["user_id"]
        }

        tool = ToolSchema(
            name="list_tasks",
            description="List user's tasks with optional filtering",
            input_schema=schema,
            handler=self._execute_list_tasks
        )

        self.tools["list_tasks"] = tool
        logger.debug("Registered tool: list_tasks")

    def _register_placeholder_tools(self):
        """Register placeholder tools for future implementation"""

        # complete_task (future)
        # delete_task (future)
        # update_task (future)
        #
        # These will be implemented in:
        # T038 - Implement MCP Tool: complete_task
        # T039 - Implement MCP Tool: delete_task
        # T040 - Implement MCP Tool: update_task

        logger.debug("Placeholder tools registered (complete_task, delete_task, update_task)")

    async def _execute_add_task(self, **kwargs) -> Dict[str, Any]:
        """
        Execute add_task tool.

        [FROM TASKS]: T036
        [FROM SPEC]: FR3 - add_task tool

        Implementation to be completed in T036.
        Placeholder returns success structure.
        """
        logger.debug(f"Executing add_task: {kwargs}")

        # TODO: T036 - Implement actual tool logic
        return {
            "success": True,
            "task_id": "placeholder-id",
            "title": kwargs.get("title", ""),
            "description": kwargs.get("description", ""),
            "created_at": "2026-02-08T00:00:00Z"
        }

    async def _execute_list_tasks(self, **kwargs) -> Dict[str, Any]:
        """
        Execute list_tasks tool.

        [FROM TASKS]: T037
        [FROM SPEC]: FR3 - list_tasks tool

        Implementation to be completed in T037.
        Placeholder returns empty list structure.
        """
        logger.debug(f"Executing list_tasks: {kwargs}")

        # TODO: T037 - Implement actual tool logic
        return {
            "tasks": [],
            "total": 0,
            "status_filter": kwargs.get("status", "all")
        }

    def get_tools(self) -> List[Dict[str, Any]]:
        """Get all registered tools as MCP definitions"""
        return [tool.to_dict() for tool in self.tools.values()]

    async def execute_tool(
        self,
        tool_name: str,
        tool_input: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Execute a registered tool.

        [FROM SPEC]: FR3 - Tool Invocation

        Args:
            tool_name: Name of tool to execute
            tool_input: Input parameters

        Returns:
            Tool response

        Raises:
            ValueError: If tool not found or input invalid
        """
        if tool_name not in self.tools:
            logger.error(f"Tool not found: {tool_name}")
            raise ValueError(f"Tool '{tool_name}' not found")

        tool = self.tools[tool_name]

        try:
            # TODO: Add input validation against schema
            result = await tool.handler(**tool_input)
            logger.debug(f"Tool {tool_name} executed successfully")
            return result
        except Exception as e:
            logger.error(f"Tool {tool_name} execution failed: {e}")
            return {
                "success": False,
                "error": str(e)
            }
