# Feature: MCP Tools for Task Management

## Overview

**Feature ID**: `mcp-tools`
**Phase**: III - AI Chatbot
**Priority**: P0 (Critical)
**Dependencies**: `task-crud-web` (Phase II), `authentication` (Phase II)

Define the five MCP (Model Context Protocol) tools that expose task CRUD operations to the OpenAI agent, following the Official MCP SDK patterns.

## MCP Tool Overview

MCP tools are stateless, standardized functions that the AI agent can call to interact with the application. Each tool:
- Has a clear schema with typed parameters
- Returns structured results
- Has no side effects beyond database writes
- Is isolated from other tools
- Validates user permissions

## Tool Definitions

### 1. add_task

**Purpose**: Create a new task for the authenticated user

**Schema**:
```json
{
  "name": "add_task",
  "description": "Creates a new task for the user",
  "parameters": {
    "type": "object",
    "properties": {
      "title": {
        "type": "string",
        "description": "The task title (1-200 characters)",
        "minLength": 1,
        "maxLength": 200
      },
      "description": {
        "type": "string",
        "description": "Optional detailed description of the task (max 1000 characters)",
        "maxLength": 1000
      }
    },
    "required": ["title"]
  }
}
```

**Input Example**:
```json
{
  "title": "Buy groceries",
  "description": "Milk, bread, eggs, and vegetables"
}
```

**Success Response**:
```json
{
  "success": true,
  "task": {
    "id": 15,
    "title": "Buy groceries",
    "description": "Milk, bread, eggs, and vegetables",
    "is_completed": false,
    "created_at": "2024-12-28T10:30:00Z",
    "updated_at": "2024-12-28T10:30:00Z"
  },
  "message": "Task created successfully"
}
```

**Error Response**:
```json
{
  "success": false,
  "error": "Title must be between 1 and 200 characters"
}
```

**Implementation Notes**:
- Extract `user_id` from context (JWT token)
- Validate title length (1-200 chars)
- Validate description length if provided (max 1000 chars)
- Set `is_completed` to false by default
- Return full task object with timestamps

### 2. list_tasks

**Purpose**: Retrieve tasks for the authenticated user with optional filtering

**Schema**:
```json
{
  "name": "list_tasks",
  "description": "Lists tasks for the user, optionally filtered by status",
  "parameters": {
    "type": "object",
    "properties": {
      "status": {
        "type": "string",
        "enum": ["all", "pending", "completed"],
        "description": "Filter tasks by completion status",
        "default": "all"
      }
    },
    "required": []
  }
}
```

**Input Example**:
```json
{
  "status": "pending"
}
```

**Success Response**:
```json
{
  "success": true,
  "tasks": [
    {
      "id": 15,
      "title": "Buy groceries",
      "description": "Milk, bread, eggs",
      "is_completed": false,
      "created_at": "2024-12-28T10:30:00Z",
      "updated_at": "2024-12-28T10:30:00Z"
    },
    {
      "id": 16,
      "title": "Call mom",
      "description": null,
      "is_completed": false,
      "created_at": "2024-12-28T11:00:00Z",
      "updated_at": "2024-12-28T11:00:00Z"
    }
  ],
  "count": 2,
  "filter": "pending"
}
```

**Empty Response**:
```json
{
  "success": true,
  "tasks": [],
  "count": 0,
  "filter": "all"
}
```

**Implementation Notes**:
- Extract `user_id` from context
- Filter by `user_id` to ensure user isolation
- If `status == "pending"`: filter `is_completed == false`
- If `status == "completed"`: filter `is_completed == true`
- If `status == "all"`: return all tasks
- Order by `created_at` descending (newest first)
- Return count of tasks

### 3. complete_task

**Purpose**: Mark a task as completed

**Schema**:
```json
{
  "name": "complete_task",
  "description": "Marks a task as completed",
  "parameters": {
    "type": "object",
    "properties": {
      "task_id": {
        "type": "integer",
        "description": "The ID of the task to complete"
      }
    },
    "required": ["task_id"]
  }
}
```

**Input Example**:
```json
{
  "task_id": 15
}
```

**Success Response**:
```json
{
  "success": true,
  "task": {
    "id": 15,
    "title": "Buy groceries",
    "description": "Milk, bread, eggs",
    "is_completed": true,
    "created_at": "2024-12-28T10:30:00Z",
    "updated_at": "2024-12-28T12:00:00Z"
  },
  "message": "Task marked as completed"
}
```

**Error Response (Task Not Found)**:
```json
{
  "success": false,
  "error": "Task not found or you don't have permission to access it"
}
```

**Error Response (Already Completed)**:
```json
{
  "success": false,
  "error": "Task is already completed"
}
```

**Implementation Notes**:
- Extract `user_id` from context
- Verify task exists AND belongs to user (user isolation)
- Check if already completed (optional - could be idempotent)
- Set `is_completed = true`
- Update `updated_at` timestamp
- Return updated task object

### 4. update_task

**Purpose**: Update task title and/or description

**Schema**:
```json
{
  "name": "update_task",
  "description": "Updates a task's title and/or description",
  "parameters": {
    "type": "object",
    "properties": {
      "task_id": {
        "type": "integer",
        "description": "The ID of the task to update"
      },
      "title": {
        "type": "string",
        "description": "New task title (1-200 characters)",
        "minLength": 1,
        "maxLength": 200
      },
      "description": {
        "type": "string",
        "description": "New task description (max 1000 characters, null to clear)",
        "maxLength": 1000
      }
    },
    "required": ["task_id"]
  }
}
```

**Input Example (Update Title)**:
```json
{
  "task_id": 15,
  "title": "Buy groceries and snacks"
}
```

**Input Example (Update Both)**:
```json
{
  "task_id": 15,
  "title": "Buy groceries and snacks",
  "description": "Milk, bread, eggs, chips, and cookies"
}
```

**Success Response**:
```json
{
  "success": true,
  "task": {
    "id": 15,
    "title": "Buy groceries and snacks",
    "description": "Milk, bread, eggs, chips, and cookies",
    "is_completed": false,
    "created_at": "2024-12-28T10:30:00Z",
    "updated_at": "2024-12-28T13:00:00Z"
  },
  "message": "Task updated successfully",
  "updated_fields": ["title", "description"]
}
```

**Error Response**:
```json
{
  "success": false,
  "error": "Task not found or you don't have permission to access it"
}
```

**Implementation Notes**:
- Extract `user_id` from context
- Verify task exists AND belongs to user
- At least one of `title` or `description` must be provided
- Validate title length if provided (1-200 chars)
- Validate description length if provided (max 1000 chars)
- Only update fields that are provided
- Update `updated_at` timestamp
- Return which fields were updated

### 5. delete_task

**Purpose**: Permanently delete a task

**Schema**:
```json
{
  "name": "delete_task",
  "description": "Deletes a task permanently",
  "parameters": {
    "type": "object",
    "properties": {
      "task_id": {
        "type": "integer",
        "description": "The ID of the task to delete"
      }
    },
    "required": ["task_id"]
  }
}
```

**Input Example**:
```json
{
  "task_id": 15
}
```

**Success Response**:
```json
{
  "success": true,
  "task": {
    "id": 15,
    "title": "Buy groceries",
    "description": "Milk, bread, eggs",
    "is_completed": false,
    "created_at": "2024-12-28T10:30:00Z",
    "updated_at": "2024-12-28T10:30:00Z"
  },
  "message": "Task deleted successfully"
}
```

**Error Response**:
```json
{
  "success": false,
  "error": "Task not found or you don't have permission to access it"
}
```

**Implementation Notes**:
- Extract `user_id` from context
- Verify task exists AND belongs to user
- Store task details before deletion (for response)
- Permanently delete from database
- Return deleted task details for confirmation

## MCP Tool Context

### User Context Injection

All MCP tools receive user context automatically:

```python
# Example context structure
{
  "user_id": "user_abc123",
  "email": "user@example.com",
  "authenticated": true
}
```

The MCP server extracts this from the JWT token before calling tools.

### Stateless Tool Design

**Key Principle**: Tools do NOT maintain state between calls.

```python
# ✅ GOOD: Stateless tool
def add_task(title: str, description: str | None, user_id: str) -> dict:
    # Read from database
    # Create task
    # Write to database
    # Return result
    pass

# ❌ BAD: Stateful tool (DO NOT DO THIS)
class TaskTool:
    def __init__(self):
        self.tasks = []  # State stored in memory!

    def add_task(self, title: str):
        self.tasks.append(title)  # Will be lost after request!
```

### Database Access Pattern

All tools follow this pattern:

1. Receive parameters + user context
2. Open database session
3. Verify user permissions
4. Execute operation
5. Commit changes
6. Close session
7. Return structured result

**Example Flow (add_task)**:
```
1. Receive: title="Buy groceries", user_id="user_123"
2. Open DB session
3. Verify user exists (optional)
4. Create task: Task(title=..., user_id=user_123, is_completed=False)
5. Commit to database
6. Close session
7. Return: {success: true, task: {...}}
```

## Tool Registration

Tools are registered with the MCP server:

```python
# Example registration (Official MCP SDK pattern)
from mcp import Tool, ToolParameter, ToolResponse

tools = [
    Tool(
        name="add_task",
        description="Creates a new task for the user",
        parameters=[
            ToolParameter(name="title", type="string", required=True),
            ToolParameter(name="description", type="string", required=False),
        ],
        handler=add_task_handler
    ),
    # ... other tools
]
```

## Error Handling Standards

### User-Facing Errors

All errors should be user-friendly and actionable:

| Error Type | Message Example |
|------------|----------------|
| Task not found | "I couldn't find task #15. Would you like to see your current tasks?" |
| Permission denied | "Task not found or you don't have permission to access it" |
| Validation failed | "Title must be between 1 and 200 characters" |
| Already completed | "Task is already completed" |
| Database error | "I'm having trouble accessing your tasks right now. Please try again." |

### Error Response Format

```json
{
  "success": false,
  "error": "User-friendly error message",
  "error_code": "TASK_NOT_FOUND",  // Optional
  "details": {}  // Optional, for debugging
}
```

## Testing Requirements

### Unit Tests for Each Tool

**Test: add_task**
```python
def test_add_task_success():
    result = add_task(title="Buy groceries", user_id="user_123")
    assert result["success"] == True
    assert result["task"]["title"] == "Buy groceries"
    assert result["task"]["is_completed"] == False

def test_add_task_title_too_long():
    result = add_task(title="x" * 201, user_id="user_123")
    assert result["success"] == False
    assert "200 characters" in result["error"]
```

**Test: list_tasks**
```python
def test_list_tasks_filter_pending():
    # Setup: create 2 pending, 1 completed
    result = list_tasks(status="pending", user_id="user_123")
    assert result["count"] == 2
    assert all(not task["is_completed"] for task in result["tasks"])

def test_list_tasks_user_isolation():
    # User 123 creates task
    add_task(title="Task 1", user_id="user_123")
    # User 456 should not see it
    result = list_tasks(status="all", user_id="user_456")
    assert result["count"] == 0
```

**Test: complete_task**
```python
def test_complete_task_success():
    task = add_task(title="Task", user_id="user_123")["task"]
    result = complete_task(task_id=task["id"], user_id="user_123")
    assert result["success"] == True
    assert result["task"]["is_completed"] == True

def test_complete_task_not_found():
    result = complete_task(task_id=99999, user_id="user_123")
    assert result["success"] == False
    assert "not found" in result["error"].lower()

def test_complete_task_wrong_user():
    task = add_task(title="Task", user_id="user_123")["task"]
    result = complete_task(task_id=task["id"], user_id="user_456")
    assert result["success"] == False
```

**Test: update_task**
```python
def test_update_task_title():
    task = add_task(title="Old title", user_id="user_123")["task"]
    result = update_task(task_id=task["id"], title="New title", user_id="user_123")
    assert result["success"] == True
    assert result["task"]["title"] == "New title"

def test_update_task_description():
    task = add_task(title="Task", user_id="user_123")["task"]
    result = update_task(
        task_id=task["id"],
        description="New description",
        user_id="user_123"
    )
    assert result["task"]["description"] == "New description"
```

**Test: delete_task**
```python
def test_delete_task_success():
    task = add_task(title="Task", user_id="user_123")["task"]
    result = delete_task(task_id=task["id"], user_id="user_123")
    assert result["success"] == True
    # Verify task is gone
    list_result = list_tasks(status="all", user_id="user_123")
    assert list_result["count"] == 0
```

### Integration Tests

**Test: Agent uses tools in sequence**
```python
async def test_agent_workflow():
    # 1. Agent adds task
    response1 = await chat("Add task to buy groceries")
    assert "created" in response1.lower()

    # 2. Agent lists tasks
    response2 = await chat("Show me my tasks")
    assert "buy groceries" in response2.lower()

    # 3. Agent completes task
    response3 = await chat("Mark the groceries task as done")
    assert "complete" in response3.lower()
```

## Performance Requirements

- Tool execution time: <100ms (database operation)
- MCP server response time: <200ms
- Concurrent tool calls: Support 100+ simultaneous requests
- Database connection pooling: Reuse connections

## Security Considerations

### User Isolation

**CRITICAL**: Every tool MUST verify user ownership:

```python
# ✅ SECURE: Check user_id
task = db.query(Task).filter(
    Task.id == task_id,
    Task.user_id == user_id  # REQUIRED
).first()

# ❌ INSECURE: Missing user_id check
task = db.query(Task).filter(Task.id == task_id).first()
```

### Input Validation

- Sanitize all string inputs
- Validate lengths (title, description)
- Validate types (task_id must be integer)
- Prevent SQL injection (use ORM, not raw SQL)

### Authentication

- JWT token validated BEFORE tools are called
- user_id extracted from validated token
- Expired tokens rejected at endpoint level

## Document History

| Version | Date | Changes |
|---------|------|---------|
| 1.0 | 2024-12-28 | Initial MCP tools specification |
