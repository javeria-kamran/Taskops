"""
MCP Server Module (Phase III)

[FROM TASKS]: T019 - MCP Startup Integration
[FROM TASKS]: T035-T041 - MCP Tools Implementation
[FROM SPEC]: speckit.specify §FR3

MCP Server handles tool registration and invocation:
- add_task
- list_tasks
- complete_task (future)
- delete_task (future)
- update_task (future)

Startup/Shutdown Lifecycle:
- Managed by FastAPI lifespan events in main.py
- Runs as background process
"""

__all__ = ["init_mcp_server", "shutdown_mcp_server", "get_mcp_server"]

# Global MCP server instance
_mcp_server = None


async def init_mcp_server():
    """
    Initialize MCP Server on FastAPI startup.

    [FROM TASKS]: T019 - MCP Server Startup Integration
    [FROM PLAN]: Phase 3 - MCP Server Foundation

    Called from main.py lifespan event.
    """
    global _mcp_server
    from app.mcp_server.server import MCPServer

    _mcp_server = MCPServer()
    await _mcp_server.initialize()
    print("✅ MCP Server initialized")


async def shutdown_mcp_server():
    """
    Shutdown MCP Server on FastAPI shutdown.

    [FROM PLAN]: Graceful shutdown

    Called from main.py lifespan event.
    """
    global _mcp_server
    if _mcp_server:
        await _mcp_server.shutdown()
        print("✅ MCP Server shutdown")


def get_mcp_server():
    """Get current MCP server instance"""
    global _mcp_server
    if not _mcp_server:
        raise RuntimeError("MCP Server not initialized")
    return _mcp_server
