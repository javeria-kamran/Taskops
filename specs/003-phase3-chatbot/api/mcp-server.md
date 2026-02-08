# API Specification: MCP Server

## Overview

**Component**: MCP Server
**Phase**: III - AI Chatbot
**Priority**: P0 (Critical)
**Dependencies**: `mcp-tools` (Phase III), `task-crud-web` (Phase II)

The MCP (Model Context Protocol) Server implements the official MCP SDK to expose task management tools to the OpenAI agent. It provides a standardized interface for AI-driven task operations with stateless execution.

## Architecture

### MCP Server Role

```
OpenAI Agent
    ↓
    calls tools via MCP protocol
    ↓
MCP Server (this component)
    ↓
    validates user context
    ↓
    executes tool handlers
    ↓
Database (SQLModel ORM)
```

### Key Responsibilities

1. **Tool Registration**: Define and register 5 task tools with schemas
2. **Context Injection**: Inject user_id into all tool calls
3. **Tool Execution**: Route tool calls to appropriate handlers
4. **Result Formatting**: Return standardized responses
5. **Error Handling**: Catch and format errors for agent consumption

## MCP Server Setup

### Installation

```bash
# Install Official MCP SDK
pip install mcp
```

### Server Initialization

```python
from mcp import MCPServer, Tool, ToolParameter
from typing import Callable

# Create MCP server instance
mcp_server = MCPServer(name="task-management-tools")

# Register tools
mcp_server.register_tool(
    Tool(
        name="add_task",
        description="Creates a new task for the user",
        parameters=[
            ToolParameter(name="title", type="string", required=True),
            ToolParameter(name="description", type="string", required=False),
        ],
        handler=add_task_handler
    )
)

# ... register other tools

# Start server (usually integrated into FastAPI)
await mcp_server.start()
```

## Tool Handlers

### Handler Signature

All tool handlers follow this pattern:

```python
async def tool_handler(
    parameters: dict,
    context: dict
) -> dict:
    """
    Args:
        parameters: Tool-specific parameters (from agent)
        context: User context (user_id, etc.)

    Returns:
        Standardized response dict with success/error
    """
    pass
```

### 1. add_task Handler

```python
from sqlmodel import Session, select
from app.models.task import Task
from app.database import get_db

async def add_task_handler(parameters: dict, context: dict) -> dict:
    """
    Creates a new task for the authenticated user.

    Parameters:
        - title (str): Task title (1-200 chars)
        - description (str, optional): Task description (max 1000 chars)

    Context:
        - user_id (str): Authenticated user ID

    Returns:
        {
            "success": bool,
            "task": {...} or None,
            "message": str,
            "error": str (if failed)
        }
    """
    try:
        # Extract parameters
        title = parameters.get("title", "").strip()
        description = parameters.get("description")
        user_id = context["user_id"]

        # Validate
        if not title or len(title) < 1:
            return {"success": False, "error": "Title cannot be empty"}
        if len(title) > 200:
            return {"success": False, "error": "Title must be 200 characters or less"}
        if description and len(description) > 1000:
            return {"success": False, "error": "Description must be 1000 characters or less"}

        # Create task
        with next(get_db()) as db:
            task = Task(
                title=title,
                description=description,
                user_id=user_id,
                is_completed=False
            )
            db.add(task)
            db.commit()
            db.refresh(task)

            return {
                "success": True,
                "task": {
                    "id": task.id,
                    "title": task.title,
                    "description": task.description,
                    "is_completed": task.is_completed,
                    "created_at": task.created_at.isoformat(),
                    "updated_at": task.updated_at.isoformat()
                },
                "message": "Task created successfully"
            }

    except Exception as e:
        return {
            "success": False,
            "error": f"Failed to create task: {str(e)}"
        }
```

### 2. list_tasks Handler

```python
async def list_tasks_handler(parameters: dict, context: dict) -> dict:
    """
    Lists tasks for the authenticated user with optional filtering.

    Parameters:
        - status (str, optional): "all", "pending", or "completed" (default: "all")

    Context:
        - user_id (str): Authenticated user ID

    Returns:
        {
            "success": bool,
            "tasks": [...],
            "count": int,
            "filter": str,
            "error": str (if failed)
        }
    """
    try:
        status = parameters.get("status", "all")
        user_id = context["user_id"]

        # Validate status
        if status not in ["all", "pending", "completed"]:
            return {"success": False, "error": "Invalid status filter"}

        with next(get_db()) as db:
            # Build query
            query = select(Task).where(Task.user_id == user_id)

            if status == "pending":
                query = query.where(Task.is_completed == False)
            elif status == "completed":
                query = query.where(Task.is_completed == True)

            # Order by created_at descending
            query = query.order_by(Task.created_at.desc())

            # Execute
            tasks = db.exec(query).all()

            return {
                "success": True,
                "tasks": [
                    {
                        "id": task.id,
                        "title": task.title,
                        "description": task.description,
                        "is_completed": task.is_completed,
                        "created_at": task.created_at.isoformat(),
                        "updated_at": task.updated_at.isoformat()
                    }
                    for task in tasks
                ],
                "count": len(tasks),
                "filter": status
            }

    except Exception as e:
        return {
            "success": False,
            "error": f"Failed to list tasks: {str(e)}"
        }
```

### 3. complete_task Handler

```python
async def complete_task_handler(parameters: dict, context: dict) -> dict:
    """
    Marks a task as completed.

    Parameters:
        - task_id (int): ID of task to complete

    Context:
        - user_id (str): Authenticated user ID

    Returns:
        {
            "success": bool,
            "task": {...} or None,
            "message": str,
            "error": str (if failed)
        }
    """
    try:
        task_id = parameters.get("task_id")
        user_id = context["user_id"]

        if not task_id:
            return {"success": False, "error": "task_id is required"}

        with next(get_db()) as db:
            # Find task (with user isolation)
            task = db.exec(
                select(Task).where(
                    Task.id == task_id,
                    Task.user_id == user_id
                )
            ).first()

            if not task:
                return {
                    "success": False,
                    "error": "Task not found or you don't have permission to access it"
                }

            # Check if already completed (optional)
            if task.is_completed:
                return {
                    "success": False,
                    "error": "Task is already completed"
                }

            # Mark as completed
            task.is_completed = True
            db.add(task)
            db.commit()
            db.refresh(task)

            return {
                "success": True,
                "task": {
                    "id": task.id,
                    "title": task.title,
                    "description": task.description,
                    "is_completed": task.is_completed,
                    "created_at": task.created_at.isoformat(),
                    "updated_at": task.updated_at.isoformat()
                },
                "message": "Task marked as completed"
            }

    except Exception as e:
        return {
            "success": False,
            "error": f"Failed to complete task: {str(e)}"
        }
```

### 4. update_task Handler

```python
async def update_task_handler(parameters: dict, context: dict) -> dict:
    """
    Updates a task's title and/or description.

    Parameters:
        - task_id (int): ID of task to update
        - title (str, optional): New title
        - description (str, optional): New description

    Context:
        - user_id (str): Authenticated user ID

    Returns:
        {
            "success": bool,
            "task": {...} or None,
            "message": str,
            "updated_fields": [...],
            "error": str (if failed)
        }
    """
    try:
        task_id = parameters.get("task_id")
        title = parameters.get("title")
        description = parameters.get("description")
        user_id = context["user_id"]

        if not task_id:
            return {"success": False, "error": "task_id is required"}

        # At least one field must be provided
        if title is None and description is None:
            return {"success": False, "error": "At least one of title or description must be provided"}

        # Validate title if provided
        if title is not None:
            title = title.strip()
            if len(title) < 1:
                return {"success": False, "error": "Title cannot be empty"}
            if len(title) > 200:
                return {"success": False, "error": "Title must be 200 characters or less"}

        # Validate description if provided
        if description is not None and len(description) > 1000:
            return {"success": False, "error": "Description must be 1000 characters or less"}

        with next(get_db()) as db:
            # Find task (with user isolation)
            task = db.exec(
                select(Task).where(
                    Task.id == task_id,
                    Task.user_id == user_id
                )
            ).first()

            if not task:
                return {
                    "success": False,
                    "error": "Task not found or you don't have permission to access it"
                }

            # Update fields
            updated_fields = []
            if title is not None:
                task.title = title
                updated_fields.append("title")
            if description is not None:
                task.description = description
                updated_fields.append("description")

            db.add(task)
            db.commit()
            db.refresh(task)

            return {
                "success": True,
                "task": {
                    "id": task.id,
                    "title": task.title,
                    "description": task.description,
                    "is_completed": task.is_completed,
                    "created_at": task.created_at.isoformat(),
                    "updated_at": task.updated_at.isoformat()
                },
                "message": "Task updated successfully",
                "updated_fields": updated_fields
            }

    except Exception as e:
        return {
            "success": False,
            "error": f"Failed to update task: {str(e)}"
        }
```

### 5. delete_task Handler

```python
async def delete_task_handler(parameters: dict, context: dict) -> dict:
    """
    Deletes a task permanently.

    Parameters:
        - task_id (int): ID of task to delete

    Context:
        - user_id (str): Authenticated user ID

    Returns:
        {
            "success": bool,
            "task": {...} or None,
            "message": str,
            "error": str (if failed)
        }
    """
    try:
        task_id = parameters.get("task_id")
        user_id = context["user_id"]

        if not task_id:
            return {"success": False, "error": "task_id is required"}

        with next(get_db()) as db:
            # Find task (with user isolation)
            task = db.exec(
                select(Task).where(
                    Task.id == task_id,
                    Task.user_id == user_id
                )
            ).first()

            if not task:
                return {
                    "success": False,
                    "error": "Task not found or you don't have permission to access it"
                }

            # Store task details before deletion
            task_data = {
                "id": task.id,
                "title": task.title,
                "description": task.description,
                "is_completed": task.is_completed,
                "created_at": task.created_at.isoformat(),
                "updated_at": task.updated_at.isoformat()
            }

            # Delete task
            db.delete(task)
            db.commit()

            return {
                "success": True,
                "task": task_data,
                "message": "Task deleted successfully"
            }

    except Exception as e:
        return {
            "success": False,
            "error": f"Failed to delete task: {str(e)}"
        }
```

## Context Management

### User Context Injection

The chat endpoint extracts `user_id` from JWT and passes it to the MCP server:

```python
# In chat endpoint
user_id = get_user_id_from_jwt(token)

# Pass to agent with context
agent_response = await agent.run(
    messages=messages,
    tools=mcp_server.tools,
    context={"user_id": user_id}
)
```

### MCP Server Context Handling

```python
class MCPServer:
    async def execute_tool(self, tool_name: str, parameters: dict, context: dict):
        """Execute a tool with user context."""
        tool = self.tools[tool_name]
        return await tool.handler(parameters, context)
```

## Integration with OpenAI Agent

### Tool Discovery

The agent discovers available tools from the MCP server:

```python
# MCP server exposes tool schemas
tools = mcp_server.get_tool_schemas()

# Example output:
[
    {
        "name": "add_task",
        "description": "Creates a new task for the user",
        "parameters": {
            "type": "object",
            "properties": {
                "title": {"type": "string"},
                "description": {"type": "string"}
            },
            "required": ["title"]
        }
    },
    # ... other tools
]
```

### Tool Invocation Flow

```
1. Agent receives user message: "Add task to buy milk"
2. Agent analyzes intent → decides to call add_task
3. Agent calls: mcp_server.execute_tool("add_task", {"title": "Buy milk"}, context)
4. MCP server routes to add_task_handler
5. Handler creates task in database
6. Handler returns: {"success": true, "task": {...}}
7. Agent uses result to generate response: "✅ Created task 'Buy milk'"
```

## Error Handling

### Tool Handler Errors

All handlers use try-catch to prevent crashes:

```python
try:
    # Tool logic
    return {"success": True, ...}
except ValidationError as e:
    return {"success": False, "error": str(e)}
except DatabaseError as e:
    logger.error(f"Database error in {tool_name}: {e}")
    return {"success": False, "error": "Database error occurred"}
except Exception as e:
    logger.error(f"Unexpected error in {tool_name}: {e}")
    return {"success": False, "error": "An unexpected error occurred"}
```

### Agent Error Handling

When a tool returns `success: false`, the agent includes the error in its response:

```python
# Tool returns error
{"success": False, "error": "Task not found"}

# Agent response to user
"I'm sorry, I couldn't find that task. Would you like to see your current tasks?"
```

## Testing

### Unit Tests for Handlers

```python
import pytest
from app.mcp.handlers import add_task_handler

@pytest.mark.asyncio
async def test_add_task_success():
    result = await add_task_handler(
        parameters={"title": "Test task"},
        context={"user_id": "user_123"}
    )
    assert result["success"] == True
    assert result["task"]["title"] == "Test task"

@pytest.mark.asyncio
async def test_add_task_title_too_long():
    result = await add_task_handler(
        parameters={"title": "x" * 201},
        context={"user_id": "user_123"}
    )
    assert result["success"] == False
    assert "200 characters" in result["error"]

@pytest.mark.asyncio
async def test_list_tasks_user_isolation():
    # User 1 creates task
    await add_task_handler(
        parameters={"title": "User 1 task"},
        context={"user_id": "user_1"}
    )

    # User 2 lists tasks (should not see User 1's task)
    result = await list_tasks_handler(
        parameters={},
        context={"user_id": "user_2"}
    )
    assert result["count"] == 0
```

### Integration Tests

```python
@pytest.mark.asyncio
async def test_mcp_server_integration():
    # Setup MCP server
    mcp_server = setup_mcp_server()

    # Simulate agent calling add_task
    result = await mcp_server.execute_tool(
        tool_name="add_task",
        parameters={"title": "Integration test task"},
        context={"user_id": "test_user"}
    )

    assert result["success"] == True
    task_id = result["task"]["id"]

    # Simulate agent calling list_tasks
    result = await mcp_server.execute_tool(
        tool_name="list_tasks",
        parameters={"status": "all"},
        context={"user_id": "test_user"}
    )

    assert result["count"] == 1
    assert result["tasks"][0]["id"] == task_id
```

## File Structure

```
backend/
├── app/
│   ├── mcp/
│   │   ├── __init__.py
│   │   ├── server.py          # MCP server setup
│   │   ├── handlers.py        # Tool handlers (5 functions)
│   │   └── schemas.py         # Tool schemas
│   ├── models/
│   │   ├── task.py            # Task model (existing)
│   │   └── ...
│   └── routes/
│       └── chat.py            # Chat endpoint (integrates MCP server)
└── tests/
    ├── test_mcp_handlers.py   # Handler unit tests
    └── test_mcp_integration.py # Integration tests
```

## Performance Considerations

### Database Connection Pooling

```python
# Use connection pool for all handlers
from app.database import engine

# Pool configuration
engine = create_engine(
    DATABASE_URL,
    pool_size=20,
    max_overflow=10,
    pool_pre_ping=True
)
```

### Handler Optimization

- Use async database queries where possible
- Minimize database round trips
- Use indexes on user_id and task_id

### Caching

```python
# Optional: Cache user validation results
from functools import lru_cache

@lru_cache(maxsize=1000)
def validate_user_exists(user_id: str) -> bool:
    # Check if user exists (short TTL)
    pass
```

## Security Considerations

### User Isolation (CRITICAL)

Every handler MUST filter by `user_id`:

```python
# ✅ CORRECT
task = db.query(Task).filter(
    Task.id == task_id,
    Task.user_id == user_id  # REQUIRED
).first()

# ❌ WRONG - Security vulnerability!
task = db.query(Task).filter(Task.id == task_id).first()
```

### Input Validation

- Validate all parameters before database operations
- Sanitize string inputs
- Check parameter types match schema

### SQL Injection Prevention

- Always use ORM (SQLModel) - never raw SQL
- Use parameterized queries if raw SQL is unavoidable

## Document History

| Version | Date | Changes |
|---------|------|---------|
| 1.0 | 2024-12-28 | Initial MCP server specification |
