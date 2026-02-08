"""
MCP Server Module (Phase III)

[FROM TASKS]: T014-T018 - MCP Server Infrastructure
[FROM SPEC]: speckit.specify §FR2

MCP (Model Context Protocol) server for task management tool integration.
Provides 5 core tools: add_task, list_tasks, complete_task, delete_task, update_task

Structure:
- server.py: Core MCP server initialization with stdio transport
- tools.py: Tool definitions with JSON schemas
- validators.py: Tool input validation
- executors.py: Tool execution layer (delegates to repositories)
- error_handler.py: Error handling and MCP JSON responses
"""

from app.chat.mcp_server.server import (
    init_mcp_server,
    shutdown_mcp_server,
    execute_tool,
    get_tool_schemas,
    mcp_server_lifespan
)

__all__ = [
    "init_mcp_server",
    "shutdown_mcp_server",
    "execute_tool",
    "get_tool_schemas",
    "mcp_server_lifespan"
]
