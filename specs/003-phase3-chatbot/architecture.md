# System Architecture - Phase III AI Chatbot with MCP

## Architecture Overview

Phase III extends the Phase II architecture with a **stateless chat endpoint** that uses **MCP (Model Context Protocol)** tools via **OpenAI Agents SDK** to provide conversational task management.

```
┌──────────────────────────────────────────────────────────────────────┐
│                            Browser                                    │
│  ┌────────────────────────────────────────────────────────────────┐  │
│  │                 OpenAI ChatKit UI                              │  │
│  │  - Chat interface component                                    │  │
│  │  - Message history display                                     │  │
│  │  - User input field                                            │  │
│  │  - Loading indicators                                          │  │
│  └────────────────────────────────────────────────────────────────┘  │
└──────────────────────────────────────────────────────────────────────┘
                                 │
                                 │ POST /api/chat + JWT
                                 ▼
┌──────────────────────────────────────────────────────────────────────┐
│                         FastAPI Backend                               │
│  ┌────────────────────────────────────────────────────────────────┐  │
│  │                    Chat Endpoint                               │  │
│  │  POST /api/chat                                                │  │
│  │  1. Verify JWT → get user_id                                  │  │
│  │  2. Fetch conversation history from DB                        │  │
│  │  3. Store user message in DB                                  │  │
│  │  4. Build message array for agent                             │  │
│  │  5. Run OpenAI Agent with MCP tools                           │  │
│  │  6. Store assistant response in DB                            │  │
│  │  7. Return response to client                                 │  │
│  └──────────────────┬─────────────────────────────────────────────┘  │
│                     │                                                 │
│                     │ Agent calls MCP tools                          │
│                     ▼                                                 │
│  ┌────────────────────────────────────────────────────────────────┐  │
│  │                     MCP Server                                 │  │
│  │  (Official MCP SDK)                                            │  │
│  │                                                                │  │
│  │  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐        │  │
│  │  │  add_task    │  │  list_tasks  │  │ complete_task│        │  │
│  │  │              │  │              │  │              │        │  │
│  │  └──────────────┘  └──────────────┘  └──────────────┘        │  │
│  │                                                                │  │
│  │  ┌──────────────┐  ┌──────────────┐                          │  │
│  │  │ update_task  │  │ delete_task  │                          │  │
│  │  │              │  │              │                          │  │
│  │  └──────────────┘  └──────────────┘                          │  │
│  │                                                                │  │
│  │  Each tool is stateless - reads/writes DB directly            │  │
│  └──────────────────┬─────────────────────────────────────────────┘  │
└─────────────────────┼────────────────────────────────────────────────┘
                      │
                      │ SQL via SQLModel ORM
                      ▼
┌──────────────────────────────────────────────────────────────────────┐
│                   Neon Serverless PostgreSQL                          │
│  ┌────────────────────────────────────────────────────────────────┐  │
│  │  Existing Tables (Phase II):                                   │  │
│  │  - users                                                       │  │
│  │  - sessions                                                    │  │
│  │  - accounts                                                    │  │
│  │  - tasks                                                       │  │
│  │                                                                │  │
│  │  New Tables (Phase III):                                       │  │
│  │  - conversations (chat sessions)                               │  │
│  │  - messages (chat history)                                     │  │
│  └────────────────────────────────────────────────────────────────┘  │
└──────────────────────────────────────────────────────────────────────┘
```

## Component Details

### Frontend (OpenAI ChatKit)

**Responsibilities**:
- Render chat interface
- Send user messages to /api/chat
- Display AI responses
- Handle loading states
- Maintain JWT authentication

**Key Technologies**:
- **Chat UI**: OpenAI ChatKit
- **Framework**: Next.js 16+ (existing)
- **Auth**: Better Auth (existing)
- **Language**: TypeScript

**Component Structure**:
```
frontend/app/(app)/chat/
├── page.tsx                 # Chat page with ChatKit
├── layout.tsx               # Chat layout
└── components/
    └── chat-interface.tsx   # ChatKit wrapper component
```

**ChatKit Integration**:
```typescript
import { ChatKit } from '@openai/chatkit'

<ChatKit
  apiEndpoint="/api/chat"
  authToken={jwtToken}
  onMessage={handleMessage}
  domainKey={process.env.NEXT_PUBLIC_OPENAI_DOMAIN_KEY}
/>
```

---

### Backend (FastAPI + OpenAI Agents + MCP)

**Responsibilities**:
- Authenticate requests (JWT)
- Manage conversations in database
- Orchestrate AI agent with MCP tools
- Store all messages
- Maintain stateless architecture

**Key Technologies**:
- **Framework**: FastAPI (existing)
- **AI**: OpenAI Agents SDK
- **MCP**: Official MCP SDK
- **ORM**: SQLModel (existing)
- **Language**: Python 3.13+

**Project Structure**:
```
backend/
├── app/
│   ├── routes/
│   │   ├── tasks.py          # Phase II REST endpoints (still available)
│   │   └── chat.py           # NEW: Chat endpoint
│   ├── mcp/
│   │   ├── __init__.py
│   │   ├── server.py         # NEW: MCP server setup
│   │   └── tools.py          # NEW: MCP tool definitions
│   ├── agents/
│   │   ├── __init__.py
│   │   └── task_agent.py     # NEW: OpenAI agent logic
│   ├── models/
│   │   ├── task.py           # Existing
│   │   ├── conversation.py   # NEW
│   │   └── message.py        # NEW
│   └── ...
```

---

### Chat Endpoint Architecture

**Route**: `POST /api/chat`

**Request Flow**:
```
1. Receive HTTP POST /api/chat
   ├─ Headers: Authorization: Bearer <JWT>
   ├─ Body: { message: "...", conversation_id?: 123 }

2. Verify JWT token → extract user_id

3. Fetch conversation history from database
   ├─ If conversation_id provided: load existing conversation
   ├─ Else: create new conversation
   ├─ Query: SELECT * FROM messages WHERE conversation_id = ? ORDER BY created_at

4. Store user message in database
   ├─ INSERT INTO messages (conversation_id, role='user', content=message)

5. Build message array for OpenAI Agent
   ├─ Convert DB messages to OpenAI format
   ├─ Format: [{"role": "user", "content": "..."}, ...]

6. Run OpenAI Agent with MCP tools
   ├─ Agent analyzes user message
   ├─ Agent decides which MCP tool(s) to call
   ├─ Agent calls tool(s) via MCP server
   ├─ Tools execute (read/write database)
   ├─ Agent generates natural language response

7. Store assistant response in database
   ├─ INSERT INTO messages (conversation_id, role='assistant', content=response)

8. Return response to client
   └─ { conversation_id: 123, response: "...", tool_calls: [...] }
```

**Stateless Architecture**:
- Server holds **NO state** between requests
- Each request is independent
- All state stored in database
- Server can restart without losing conversations
- Any server instance can handle any request

---

### MCP Server Architecture

**Purpose**: Provide standardized tools for AI agent to manage tasks

**MCP Tools** (5 tools matching CRUD operations):
1. `add_task` - Create a new task
2. `list_tasks` - Retrieve tasks with optional filtering
3. `complete_task` - Mark task as complete
4. `update_task` - Modify task title/description
5. `delete_task` - Remove a task

**Tool Structure**:
```python
from mcp import Tool, Parameter, PropertyType

add_task_tool = Tool(
    name="add_task",
    description="Create a new task for the user",
    parameters={
        "user_id": Parameter(
            type=PropertyType.STRING,
            description="User ID from JWT",
            required=True
        ),
        "title": Parameter(
            type=PropertyType.STRING,
            description="Task title (1-200 characters)",
            required=True
        ),
        "description": Parameter(
            type=PropertyType.STRING,
            description="Optional task description",
            required=False
        )
    }
)

async def add_task_handler(user_id: str, title: str, description: str = None):
    """
    Stateless handler - reads/writes DB directly
    """
    # Validate inputs
    if not title or len(title) > 200:
        return {"error": "Invalid title"}

    # Create task in database
    task = Task(user_id=user_id, title=title, description=description)
    session.add(task)
    await session.commit()

    # Return result
    return {
        "task_id": task.id,
        "status": "created",
        "title": task.title
    }
```

**Stateless MCP Tools**:
- Each tool call is independent
- Tools receive `user_id` as parameter (from JWT)
- Tools read/write database directly
- Tools don't maintain state between calls
- Tools are pure functions (input → output)

---

### OpenAI Agent Integration

**Agent Role**: Orchestrate MCP tools based on natural language

**Agent Architecture**:
```python
from openai import OpenAI
from mcp import MCPClient

class TaskAgent:
    def __init__(self, mcp_client: MCPClient):
        self.openai = OpenAI()
        self.mcp_client = mcp_client

    async def process_message(
        self,
        user_id: str,
        messages: List[dict],
        mcp_tools: List[Tool]
    ) -> str:
        """
        Process user message with MCP tools
        """
        # Call OpenAI with tools
        response = await self.openai.chat.completions.create(
            model="gpt-4",
            messages=messages,
            tools=mcp_tools,  # MCP tools exposed to agent
            tool_choice="auto"
        )

        # Handle tool calls if any
        if response.tool_calls:
            for tool_call in response.tool_calls:
                # Execute MCP tool
                tool_result = await self.mcp_client.call_tool(
                    name=tool_call.function.name,
                    arguments={
                        "user_id": user_id,
                        **tool_call.function.arguments
                    }
                )

                # Add tool result to messages
                messages.append({
                    "role": "tool",
                    "tool_call_id": tool_call.id,
                    "content": str(tool_result)
                })

            # Get final response from agent
            final_response = await self.openai.chat.completions.create(
                model="gpt-4",
                messages=messages
            )

            return final_response.choices[0].message.content

        # No tool calls, return direct response
        return response.choices[0].message.content
```

**Agent Capabilities**:
- Understands natural language intents
- Maps user requests to MCP tools
- Chains multiple tools in one turn
- Provides friendly confirmations
- Handles errors gracefully

---

### Database Schema (Extended from Phase II)

**New Tables**:

**conversations**:
```sql
CREATE TABLE conversations (
    id SERIAL PRIMARY KEY,
    user_id VARCHAR(255) NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_conversations_user_id ON conversations(user_id);
```

**messages**:
```sql
CREATE TABLE messages (
    id SERIAL PRIMARY KEY,
    conversation_id INTEGER NOT NULL REFERENCES conversations(id) ON DELETE CASCADE,
    user_id VARCHAR(255) NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    role VARCHAR(20) NOT NULL,  -- 'user' or 'assistant'
    content TEXT NOT NULL,
    tool_calls JSONB,  -- Optional: store tool call details
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_messages_conversation_id ON messages(conversation_id);
CREATE INDEX idx_messages_created_at ON messages(created_at);
```

---

## Stateless Request Cycle

### Complete Request Flow

```
┌─────────────────────────────────────────────────────────────────┐
│ 1. User sends message: "Add task to buy groceries"             │
└─────────────────────┬───────────────────────────────────────────┘
                      │
                      ▼
┌─────────────────────────────────────────────────────────────────┐
│ 2. ChatKit sends POST /api/chat                                 │
│    Headers: Authorization: Bearer <JWT>                         │
│    Body: { message: "Add task to buy groceries" }              │
└─────────────────────┬───────────────────────────────────────────┘
                      │
                      ▼
┌─────────────────────────────────────────────────────────────────┐
│ 3. Chat endpoint handler:                                       │
│    a. Verify JWT → user_id = "user_abc123"                     │
│    b. conversation_id not provided → create new conversation   │
│       INSERT INTO conversations (user_id) VALUES ('user_abc123')│
│       → conversation_id = 42                                    │
└─────────────────────┬───────────────────────────────────────────┘
                      │
                      ▼
┌─────────────────────────────────────────────────────────────────┐
│ 4. Fetch conversation history (empty for new conversation)      │
│    SELECT * FROM messages WHERE conversation_id = 42           │
│    → []                                                         │
└─────────────────────┬───────────────────────────────────────────┘
                      │
                      ▼
┌─────────────────────────────────────────────────────────────────┐
│ 5. Store user message in database                               │
│    INSERT INTO messages (conversation_id, role, content)       │
│    VALUES (42, 'user', 'Add task to buy groceries')            │
└─────────────────────┬───────────────────────────────────────────┘
                      │
                      ▼
┌─────────────────────────────────────────────────────────────────┐
│ 6. Build message array for agent                                │
│    messages = [                                                 │
│      {"role": "user", "content": "Add task to buy groceries"}  │
│    ]                                                            │
└─────────────────────┬───────────────────────────────────────────┘
                      │
                      ▼
┌─────────────────────────────────────────────────────────────────┐
│ 7. Run OpenAI Agent                                             │
│    Agent analyzes: "user wants to create a task"               │
│    Agent decides: call add_task tool                            │
│    Agent calls: add_task(user_id="user_abc123",                │
│                          title="Buy groceries")                 │
└─────────────────────┬───────────────────────────────────────────┘
                      │
                      ▼
┌─────────────────────────────────────────────────────────────────┐
│ 8. MCP tool executes (stateless)                                │
│    add_task_handler():                                          │
│      - Validates input                                          │
│      - INSERT INTO tasks (user_id, title)                      │
│        VALUES ('user_abc123', 'Buy groceries')                 │
│      - Returns: {"task_id": 15, "status": "created"}           │
└─────────────────────┬───────────────────────────────────────────┘
                      │
                      ▼
┌─────────────────────────────────────────────────────────────────┐
│ 9. Agent generates response                                     │
│    "I've created a new task: 'Buy groceries'. Task ID is 15."  │
└─────────────────────┬───────────────────────────────────────────┘
                      │
                      ▼
┌─────────────────────────────────────────────────────────────────┐
│ 10. Store assistant response in database                        │
│     INSERT INTO messages (conversation_id, role, content)      │
│     VALUES (42, 'assistant', "I've created a new task...")     │
└─────────────────────┬───────────────────────────────────────────┘
                      │
                      ▼
┌─────────────────────────────────────────────────────────────────┐
│ 11. Return response to client                                   │
│     {                                                           │
│       "conversation_id": 42,                                    │
│       "response": "I've created a new task: 'Buy groceries'...",│
│       "tool_calls": [{"tool": "add_task", "result": {...}}]    │
│     }                                                           │
└─────────────────────┬───────────────────────────────────────────┘
                      │
                      ▼
┌─────────────────────────────────────────────────────────────────┐
│ 12. ChatKit displays response to user                           │
│     Server is now completely stateless - ready for next request │
└─────────────────────────────────────────────────────────────────┘
```

---

## Authentication Flow

**JWT Integration** (Same as Phase II):

```
User logged in (Phase II) → Has JWT token
    │
    ▼
User opens /chat page
    │
    ▼
ChatKit component loads
    │
    ▼
ChatKit sends message with JWT in Authorization header
    │
    ▼
Chat endpoint verifies JWT → extracts user_id
    │
    ▼
All MCP tool calls include user_id
    │
    ▼
MCP tools filter database queries by user_id
```

**User Isolation**:
- All MCP tools receive `user_id` from JWT
- All database queries filtered by `user_id`
- Users can only access their own tasks and conversations
- No cross-user data leakage

---

## Error Handling

### Chat Endpoint Errors

**Authentication Errors** (401):
- Missing JWT
- Invalid JWT
- Expired JWT

**Validation Errors** (400):
- Empty message
- Message too long (>2000 characters)
- Invalid conversation_id

**MCP Tool Errors** (returned to agent):
- Task not found
- Invalid task_id
- Validation failures
- Database errors

**Agent Error Handling**:
```python
try:
    tool_result = await mcp_client.call_tool(...)
except TaskNotFoundError:
    # Agent generates user-friendly response
    return "I couldn't find that task. Could you check the task number?"
except ValidationError as e:
    return f"There was a problem with your request: {e.message}"
```

---

## Performance Considerations

### Latency Targets
- Chat endpoint response: <2 seconds (simple queries)
- Agent + MCP tool execution: <1 second
- Database query (conversation history): <100ms
- Total user-visible latency: <3 seconds

### Optimization Strategies

**Database**:
- Index on `conversation_id` and `created_at`
- Limit conversation history to last 50 messages
- Connection pooling (existing)

**Agent**:
- Use GPT-4-turbo for faster responses
- Streaming responses (future enhancement)
- Cache agent system prompts

**MCP Tools**:
- Reuse database connections
- Batch operations when possible
- Async tool execution

---

## Scalability Benefits

### Stateless Architecture
- **Horizontal Scaling**: Add more server instances behind load balancer
- **No Session Affinity**: Any server can handle any request
- **Resilience**: Server crashes don't lose conversations
- **Simple Deployment**: No sticky sessions or distributed cache needed

### Database-Centric State
- **Single Source of Truth**: All state in database
- **Auditable**: Full conversation history
- **Recoverable**: Can replay conversations
- **Analyzable**: Can analyze user patterns

---

## Security Considerations

### Authentication
- ✅ All chat requests require valid JWT
- ✅ User ID extracted from JWT (not from request body)
- ✅ MCP tools enforce user isolation

### Prompt Injection Prevention
- ✅ User messages treated as data, not instructions
- ✅ System prompts separate from user input
- ✅ MCP tools validate all parameters
- ✅ SQL injection prevented (SQLModel ORM)

### Data Privacy
- ✅ Users can only access their own conversations
- ✅ Conversation history filtered by user_id
- ✅ No cross-user conversation leakage

---

## Testing Strategy

### Unit Tests
- MCP tool functions (isolated)
- Agent message parsing
- Database models (conversations, messages)

### Integration Tests
- Chat endpoint with mock agent
- MCP server with mock tools
- Database persistence

### E2E Tests
- Full conversation flow
- Multi-turn conversations
- Tool chaining
- Error recovery

---

## Monitoring & Logging

### Metrics
- Chat endpoint response time
- MCP tool execution time
- Agent token usage (OpenAI API)
- Conversation length distribution

### Logging
```python
logger.info(f"User {user_id} sent message in conversation {conversation_id}")
logger.info(f"Agent called tool: {tool_name} with params: {params}")
logger.info(f"Tool {tool_name} returned: {result}")
logger.error(f"Error in chat endpoint: {error}")
```

---

## Migration from Phase II

| Phase II | Phase III | Changes |
|----------|-----------|---------|
| REST API at /api/tasks | Still available | No changes |
| Web UI at /tasks | Still available | No changes |
| — | Chat endpoint /api/chat | NEW |
| — | MCP server | NEW |
| — | OpenAI agent | NEW |
| — | conversations table | NEW |
| — | messages table | NEW |
| — | ChatKit UI at /chat | NEW |

**Backward Compatibility**: Phase II features remain fully functional.

---

## Document History

| Version | Date | Changes |
|---------|------|---------|
| 1.0 | 2024-12-28 | Initial Phase III architecture specification |
