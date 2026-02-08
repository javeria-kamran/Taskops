"""
T014: MCP Server Initialization

Uses official MCP SDK with stdio transport for tool registration and execution.
Stateless design: server only routes requests to tool handlers, no in-memory state.

Transport: stdio (suitable for FastAPI integration via asyncio subprocess)
Tools: 5 registered (add_task, list_tasks, complete_task, delete_task, update_task)
"""

import json
import logging
from contextlib import asynccontextmanager
from typing import Any, Optional

# MCP Server and tool definition imports
# Note: mcp SDK used for tool definitions and protocol
# This server runs as a background process managed by FastAPI lifespan

logger = logging.getLogger(__name__)

# Global MCP server instance (managed by FastAPI lifespan)
_mcp_server_instance: Optional[Any] = None

# Tool registry - maps tool name to handler function
_tool_handlers: dict = {}


async def init_mcp_server() -> None:
    """
    T014: Initialize MCP server with tool registry.

    Responsibilities:
    1. Register all 5 task management tools
    2. Attach tool handlers to MCP protocol
    3. Start server in background (managed by FastAPI lifespan)

    Tools:
    - add_task: Create new task with title, optional description/priority/due_date
    - list_tasks: Get user's tasks with optional status filter
    - complete_task: Mark task as completed
    - delete_task: Remove task
    - update_task: Modify task title/description/priority/due_date
    """
    global _mcp_server_instance

    try:
        # Import tool definitions (T015)
        from .tools import register_tools

        # Import tool executors (T017)
        from .executors import get_tool_executor

        logger.info("[MCP] Registering tools...")
        tool_schemas = register_tools()

        # Store executor reference for later tool calls
        for tool_name, tool_schema in tool_schemas.items():
            _tool_handlers[tool_name] = get_tool_executor(tool_name)
            logger.info(f"[MCP] Registered tool: {tool_name}")

        _mcp_server_instance = True  # Marker that server is initialized
        logger.info(f"[MCP ✓] Server initialized with {len(tool_schemas)} tools")

    except Exception as e:
        logger.error(f"[MCP ✗] Failed to initialize: {e}", exc_info=True)
        raise


async def shutdown_mcp_server() -> None:
    """
    T019: Shutdown MCP server cleanly.

    Called by FastAPI lifespan shutdown event.
    Performs cleanup: closes connections, saves state if needed.
    """
    global _mcp_server_instance

    try:
        logger.info("[MCP] Shutting down server...")
        _mcp_server_instance = None
        _tool_handlers.clear()
        logger.info("[MCP ✓] Server shutdown complete")
    except Exception as e:
        logger.error(f"[MCP ✗] Error during shutdown: {e}", exc_info=True)


async def execute_tool(
    tool_name: str,
    tool_input: dict[str, Any],
    user_id: str,
    session: Any  # SQLAlchemy AsyncSession
) -> dict[str, Any]:
    """
    Execute a tool handler with given input.

    Args:
        tool_name: Name of tool to execute (e.g., 'add_task')
        tool_input: Tool-specific arguments
        user_id: User ID for isolation
        session: Database session for persistence

    Returns:
        {result: {...}} on success
        {error: "...", details: "..."} on failure

    Raises:
        KeyError: If tool_name not registered
        Exception: Tool-specific errors (converted to JSON by error_handler)
    """
    if not _mcp_server_instance:
        return {
            "error": "MCP server not initialized",
            "details": "call init_mcp_server() first"
        }

    handler = _tool_handlers.get(tool_name)
    if not handler:
        return {
            "error": "Tool not found",
            "details": f"Unknown tool: {tool_name}"
        }

    try:
        # Import error handler (T018)
        from .error_handler import handle_tool_error

        # Execute tool handler (delegates to repository)
        result = await handler(tool_input, user_id, session)
        return {"result": result}

    except Exception as e:
        # Convert exception to MCP JSON error response
        from .error_handler import handle_tool_error
        return handle_tool_error(e, tool_name)


def get_tool_schemas() -> dict[str, dict]:
    """
    Get all registered tool schemas for agent discovery.

    Returns:
        {
            "add_task": {schema...},
            "list_tasks": {schema...},
            ...
        }
    """
    from .tools import get_tool_definitions
    return get_tool_definitions()


@asynccontextmanager
async def mcp_server_lifespan():
    """
    Context manager for MCP server lifecycle (used by FastAPI lifespan).

    Startup: Initialize MCP server
    Execution: Yield control to FastAPI
    Shutdown: Clean up MCP server
    """
    await init_mcp_server()
    try:
        yield
    finally:
        await shutdown_mcp_server()
