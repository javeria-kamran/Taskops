# API Specification: Chat Endpoint

## Overview

**Endpoint**: `POST /api/chat`
**Phase**: III - AI Chatbot
**Priority**: P0 (Critical)
**Dependencies**: `authentication` (Phase II), `mcp-tools` (Phase III)

The chat endpoint provides a stateless conversational interface for task management. It receives user messages, orchestrates AI agent responses using MCP tools, and persists conversation history to the database.

## Endpoint Details

### POST /api/chat

**Purpose**: Process a chat message and return AI agent's response

**Authentication**: Required (JWT Bearer token)

**Request Headers**:
```http
POST /api/chat HTTP/1.1
Host: api.example.com
Content-Type: application/json
Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...
```

### Request Body

**Schema**:
```json
{
  "type": "object",
  "properties": {
    "message": {
      "type": "string",
      "description": "User's message text",
      "minLength": 1,
      "maxLength": 2000
    },
    "conversation_id": {
      "type": "string",
      "description": "Optional conversation ID to continue existing conversation",
      "format": "uuid"
    }
  },
  "required": ["message"]
}
```

**Example (New Conversation)**:
```json
{
  "message": "Add task to buy groceries"
}
```

**Example (Continue Conversation)**:
```json
{
  "conversation_id": "550e8400-e29b-41d4-a716-446655440000",
  "message": "Mark the groceries task as done"
}
```

### Response Body

**Success Response (200 OK)**:
```json
{
  "conversation_id": "550e8400-e29b-41d4-a716-446655440000",
  "message": {
    "role": "assistant",
    "content": "✅ I've created a new task: 'Buy groceries' (Task #15)",
    "created_at": "2024-12-28T10:30:00Z"
  },
  "tools_used": ["add_task"],
  "metadata": {
    "message_count": 2,
    "processing_time_ms": 1234
  }
}
```

**Error Response (400 Bad Request)**:
```json
{
  "detail": "Message cannot be empty"
}
```

**Error Response (401 Unauthorized)**:
```json
{
  "detail": "Not authenticated"
}
```

**Error Response (404 Not Found)**:
```json
{
  "detail": "Conversation not found or you don't have permission to access it"
}
```

**Error Response (500 Internal Server Error)**:
```json
{
  "detail": "An error occurred while processing your request"
}
```

## Request Flow

### Step-by-Step Processing

1. **Receive Request**
   - Parse JSON body
   - Extract JWT token from Authorization header

2. **Authenticate User**
   - Validate JWT token
   - Extract `user_id` from token
   - Reject if token invalid or expired

3. **Validate Input**
   - Check message is not empty
   - Check message length <= 2000 chars
   - If conversation_id provided, verify it exists and belongs to user

4. **Load/Create Conversation**
   - If `conversation_id` provided: Load existing conversation
   - If not provided: Create new conversation with UUID
   - Filter by `user_id` to ensure user isolation

5. **Fetch Conversation History**
   - Query messages table for this conversation
   - Order by created_at ascending
   - Build message array for agent

6. **Store User Message**
   - Insert user message into messages table
   - Link to conversation_id and user_id

7. **Build Agent Context**
   - Construct message array with history + new message
   - Format: `[{role: "user", content: "..."}, {role: "assistant", content: "..."}, ...]`

8. **Run OpenAI Agent**
   - Pass messages to OpenAI Agents SDK
   - Agent has access to MCP tools
   - Agent orchestrates tool calls and generates response

9. **Store Assistant Response**
   - Insert assistant message into messages table
   - Include tool calls metadata if any

10. **Return Response**
    - Return conversation_id, assistant message, metadata
    - Server is now stateless (no session stored)

## Example Interactions

### Example 1: Create Task

**Request**:
```json
POST /api/chat
Authorization: Bearer <jwt_token>

{
  "message": "Add task to buy groceries"
}
```

**Internal Processing**:
1. User authenticated → user_id = "user_123"
2. New conversation created → conversation_id = "550e8400..."
3. User message stored
4. Agent invoked with message history
5. Agent calls MCP tool: `add_task(title="Buy groceries")`
6. Agent generates response
7. Assistant message stored

**Response**:
```json
{
  "conversation_id": "550e8400-e29b-41d4-a716-446655440000",
  "message": {
    "role": "assistant",
    "content": "✅ I've created a new task: 'Buy groceries' (Task #15)",
    "created_at": "2024-12-28T10:30:00Z"
  },
  "tools_used": ["add_task"],
  "metadata": {
    "message_count": 2,
    "processing_time_ms": 1200
  }
}
```

### Example 2: List Tasks

**Request**:
```json
POST /api/chat
Authorization: Bearer <jwt_token>

{
  "conversation_id": "550e8400-e29b-41d4-a716-446655440000",
  "message": "Show me all my tasks"
}
```

**Internal Processing**:
1. Load conversation history (2 messages from previous turn)
2. Store new user message (history now has 3 messages)
3. Agent invoked with full history
4. Agent calls MCP tool: `list_tasks(status="all")`
5. Agent formats task list in response

**Response**:
```json
{
  "conversation_id": "550e8400-e29b-41d4-a716-446655440000",
  "message": {
    "role": "assistant",
    "content": "You have 1 task:\n1. Buy groceries (pending)",
    "created_at": "2024-12-28T10:31:00Z"
  },
  "tools_used": ["list_tasks"],
  "metadata": {
    "message_count": 4,
    "processing_time_ms": 980
  }
}
```

### Example 3: Multi-Turn Context

**Turn 1**:
```json
User: "Add task to buy groceries"
Assistant: "✅ I've created a new task: 'Buy groceries' (Task #15)"
```

**Turn 2**:
```json
User: "Mark it as done"  // Context: "it" refers to task from Turn 1
Assistant: "✅ Marked 'Buy groceries' as complete!"
```

Agent uses conversation history to understand "it" refers to the groceries task.

## Database Operations

### Conversation Lookup/Creation

```sql
-- If conversation_id provided, verify ownership
SELECT * FROM conversations
WHERE id = $conversation_id AND user_id = $user_id;

-- If not provided, create new
INSERT INTO conversations (id, user_id, created_at)
VALUES (uuid_generate_v4(), $user_id, NOW())
RETURNING *;
```

### Fetch Message History

```sql
SELECT role, content, created_at, metadata
FROM messages
WHERE conversation_id = $conversation_id
ORDER BY created_at ASC;
```

### Store User Message

```sql
INSERT INTO messages (id, conversation_id, role, content, created_at)
VALUES (uuid_generate_v4(), $conversation_id, 'user', $message, NOW());
```

### Store Assistant Message

```sql
INSERT INTO messages (id, conversation_id, role, content, metadata, created_at)
VALUES (
  uuid_generate_v4(),
  $conversation_id,
  'assistant',
  $response_content,
  $tools_used_json,
  NOW()
);
```

## Agent Integration

### Message Format for Agent

```python
messages = [
    {"role": "user", "content": "Add task to buy groceries"},
    {"role": "assistant", "content": "✅ I've created a new task..."},
    {"role": "user", "content": "Show me all my tasks"},
]
```

### Agent Context Injection

The agent needs access to `user_id` for MCP tool calls:

```python
# Example agent invocation
agent_response = await agent.run(
    messages=messages,
    tools=mcp_tools,
    context={"user_id": user_id}  # Injected into all tool calls
)
```

### Tool Call Handling

When agent calls a tool:

```python
# Agent decides to call add_task
tool_call = {
    "tool": "add_task",
    "parameters": {
        "title": "Buy groceries",
        "description": None
    }
}

# MCP server executes tool with user context
result = await mcp_server.execute_tool(
    tool_name="add_task",
    parameters=tool_call["parameters"],
    context={"user_id": user_id}
)

# Result returned to agent
# Agent uses result to generate response
```

## Error Handling

### Validation Errors

**Empty Message**:
```python
if not message or len(message.strip()) == 0:
    raise HTTPException(status_code=400, detail="Message cannot be empty")
```

**Message Too Long**:
```python
if len(message) > 2000:
    raise HTTPException(status_code=400, detail="Message exceeds maximum length of 2000 characters")
```

### Authentication Errors

**Missing Token**:
```python
if not authorization_header:
    raise HTTPException(status_code=401, detail="Not authenticated")
```

**Invalid Token**:
```python
try:
    payload = jwt.decode(token, SECRET_KEY, algorithms=["HS256"])
except JWTError:
    raise HTTPException(status_code=401, detail="Invalid authentication token")
```

### Conversation Errors

**Conversation Not Found**:
```python
conversation = db.query(Conversation).filter(
    Conversation.id == conversation_id,
    Conversation.user_id == user_id
).first()

if not conversation:
    raise HTTPException(
        status_code=404,
        detail="Conversation not found or you don't have permission to access it"
    )
```

### Agent Errors

**Agent Processing Failed**:
```python
try:
    response = await agent.run(messages, tools, context)
except Exception as e:
    logger.error(f"Agent error: {e}")
    raise HTTPException(
        status_code=500,
        detail="An error occurred while processing your request"
    )
```

## Performance Considerations

### Response Time Targets

- **Database queries**: <50ms
- **Agent processing**: <1500ms
- **Total response time**: <2000ms (2 seconds)

### Optimization Strategies

1. **Database Connection Pooling**
   - Reuse connections across requests
   - Set pool size based on expected load

2. **Message History Limit**
   - Load last 50 messages only (configurable)
   - Prevents large conversation slowdowns

3. **Async/Await**
   - Use async database queries
   - Use async agent invocation

4. **Caching**
   - Cache user authentication results (short TTL)
   - Cache conversation metadata

### Example Implementation (FastAPI)

```python
from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from typing import Optional
import time

router = APIRouter()

class ChatRequest(BaseModel):
    message: str
    conversation_id: Optional[str] = None

class ChatResponse(BaseModel):
    conversation_id: str
    message: dict
    tools_used: list[str]
    metadata: dict

@router.post("/chat", response_model=ChatResponse)
async def chat_endpoint(
    request: ChatRequest,
    user_id: str = Depends(get_current_user_id),
    db: Session = Depends(get_db)
):
    start_time = time.time()

    # Validate input
    if not request.message or len(request.message.strip()) == 0:
        raise HTTPException(status_code=400, detail="Message cannot be empty")
    if len(request.message) > 2000:
        raise HTTPException(status_code=400, detail="Message too long")

    # Load or create conversation
    if request.conversation_id:
        conversation = db.query(Conversation).filter(
            Conversation.id == request.conversation_id,
            Conversation.user_id == user_id
        ).first()
        if not conversation:
            raise HTTPException(status_code=404, detail="Conversation not found")
    else:
        conversation = Conversation(user_id=user_id)
        db.add(conversation)
        db.commit()
        db.refresh(conversation)

    # Fetch message history
    history = db.query(Message).filter(
        Message.conversation_id == conversation.id
    ).order_by(Message.created_at.asc()).limit(50).all()

    # Store user message
    user_message = Message(
        conversation_id=conversation.id,
        role="user",
        content=request.message
    )
    db.add(user_message)
    db.commit()

    # Build message array for agent
    messages = [{"role": m.role, "content": m.content} for m in history]
    messages.append({"role": "user", "content": request.message})

    # Run agent
    agent_response = await run_agent(
        messages=messages,
        user_id=user_id
    )

    # Store assistant message
    assistant_message = Message(
        conversation_id=conversation.id,
        role="assistant",
        content=agent_response.content,
        metadata={"tools_used": agent_response.tools_used}
    )
    db.add(assistant_message)
    db.commit()
    db.refresh(assistant_message)

    # Calculate metrics
    processing_time = int((time.time() - start_time) * 1000)
    message_count = len(messages) + 1

    return ChatResponse(
        conversation_id=str(conversation.id),
        message={
            "role": "assistant",
            "content": agent_response.content,
            "created_at": assistant_message.created_at.isoformat()
        },
        tools_used=agent_response.tools_used,
        metadata={
            "message_count": message_count,
            "processing_time_ms": processing_time
        }
    )
```

## Testing Requirements

### Unit Tests

**Test: Valid request creates conversation**:
```python
async def test_chat_creates_new_conversation():
    response = await client.post(
        "/api/chat",
        headers={"Authorization": f"Bearer {jwt_token}"},
        json={"message": "Hello"}
    )
    assert response.status_code == 200
    assert "conversation_id" in response.json()
```

**Test: Conversation history is loaded**:
```python
async def test_chat_loads_history():
    # First message
    resp1 = await client.post("/api/chat", ...)
    conversation_id = resp1.json()["conversation_id"]

    # Second message (should load first message)
    resp2 = await client.post(
        "/api/chat",
        json={"conversation_id": conversation_id, "message": "Second message"}
    )
    assert resp2.json()["metadata"]["message_count"] == 4  # 2 user + 2 assistant
```

**Test: User isolation enforced**:
```python
async def test_chat_user_isolation():
    # User 1 creates conversation
    resp1 = await client.post("/api/chat", headers=user1_headers, ...)
    conversation_id = resp1.json()["conversation_id"]

    # User 2 tries to access it
    resp2 = await client.post(
        "/api/chat",
        headers=user2_headers,
        json={"conversation_id": conversation_id, "message": "Hello"}
    )
    assert resp2.status_code == 404
```

### Integration Tests

**Test: Full chat workflow**:
```python
async def test_full_chat_workflow():
    # Create task
    resp1 = await client.post("/api/chat", json={"message": "Add task to buy milk"})
    assert "created" in resp1.json()["message"]["content"].lower()

    # List tasks
    resp2 = await client.post(
        "/api/chat",
        json={
            "conversation_id": resp1.json()["conversation_id"],
            "message": "Show me my tasks"
        }
    )
    assert "buy milk" in resp2.json()["message"]["content"].lower()
```

## Security Considerations

### JWT Validation

- Verify signature using SECRET_KEY
- Check expiration time
- Extract user_id from validated token
- Reject if any validation fails

### User Isolation

- ALWAYS filter conversations by user_id
- ALWAYS filter messages through conversation ownership
- Never expose other users' conversations

### Input Sanitization

- Validate message length
- Trim whitespace
- No executable code in messages (handled by OpenAI)

### Rate Limiting

```python
# Example: 20 requests per minute per user
@limiter.limit("20/minute")
async def chat_endpoint(...):
    pass
```

## Document History

| Version | Date | Changes |
|---------|------|---------|
| 1.0 | 2024-12-28 | Initial chat endpoint specification |
