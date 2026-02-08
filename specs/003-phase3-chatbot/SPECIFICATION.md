# Phase III: Todo AI Chatbot - Technical Specification

**Version:** 1.0  
**Date:** February 8, 2026  
**Status:** Ready for Implementation  
**Framework:** Spec-Kit Plus + Agentic Dev Stack  

---

## Table of Contents

1. [Executive Summary](#executive-summary)
2. [Constitution (WHY)](#constitution-why--principles--constraints)
3. [Specify (WHAT)](#specify-what--requirements--acceptance-criteria)
4. [Plan (HOW)](#plan-how--architecture--components)
5. [Tasks (BREAKDOWN)](#tasks-breakdown--atomic-work-units)
6. [Appendix](#appendix)

---

## Executive Summary

**Phase III** extends the existing Todo application with an **AI-powered conversational interface** using OpenAI Agents and Model Context Protocol (MCP).

### Objectives
- Enable natural language task management
- Maintain stateless, scalable architecture
- Support multi-turn conversations with persistence
- Implement secure tool execution via MCP
- Ensure seamless integration with existing system

### Key Deliverables
- OpenAI Agent with MCP Server
- Chat API endpoints (`POST /api/{user_id}/chat`)
- ChatKit UI integration (Next.js)
- Conversation history persistence (PostgreSQL)
- Tool execution layer (5 stateless tools)
- Comprehensive error handling
- Production-ready deployment

### Tech Stack
| Layer | Technology | Version |
|-------|-----------|---------|
| Frontend | Next.js + TypeScript | Latest |
| Frontend UI | ChatKit | Latest |
| Backend API | FastAPI | 0.104+ |
| AI Framework | OpenAI Agents SDK | Latest |
| MCP | Official MCP SDK | v1.0+ |
| ORM | SQLModel | 0.0.14+ |
| Database | Neon PostgreSQL | Serverless |
| Auth | Better Auth | Integrated |

---

## Constitution (WHY) — Principles & Constraints

### Core Principles

**P1: Stateless Server Architecture**
- No in-memory conversation state
- All state persisted in PostgreSQL
- Every request is independent and resumable
- Enables horizontal scaling

**P2: Security by Design**
- User context isolation (validate `user_id` on every operation)
- Input validation on all tool parameters
- Rate limiting on chat endpoints
- SQL injection prevention via SQLModel parameterization

**P3: Deterministic Tool Execution**
- MCP tools are pure functions
- Same inputs always produce same outputs
- No side effects beyond database writes
- Idempotent operations where possible

**P4: Natural Language Intent Resolution**
- Agent interprets ambiguous user queries
- Confirms high-risk actions (delete, complete)
- Supports task chaining (find then delete)
- Graceful error messages for clarification

**P5: API-First Design**
- All functionality exposed via REST
- ChatKit UI is reference implementation
- Third-party apps can use Chat API directly
- Structured JSON responses

### Constraints

**C1: Technology Stack Lock**
- OpenAI API (no local LLMs)
- FastAPI only (no Flask, Django)
- PostgreSQL only (no NoSQL)
- MCP v1.0+ (official SDK)

**C2: Stateless Mandate**
- No thread-local storage
- No request caching between calls
- No in-memory conversation buffers
- All context from database

**C3: Data Residency**
- All data in Neon PostgreSQL
- No external conversation storage
- Audit trail maintained
- GDPR-compliant deletion

**C4: Latency Requirements**
- Chat API: < 5 seconds (including OpenAI latency)
- Tool execution: < 1 second per tool
- Database queries: < 100ms

**C5: Scaling Model**
- Horizontal scaling via stateless design
- Connection pooling for PostgreSQL
- Load balancing across API instances
- No session affinity required

---

## Specify (WHAT) — Requirements & Acceptance Criteria

### Functional Requirements

#### FR1: Chat API Endpoint

**Endpoint:** `POST /api/{user_id}/chat`

**Request Schema:**
```json
{
  "conversation_id": "uuid (optional)",
  "message": "string (required, 1-4096 chars)",
  "stream": "boolean (optional, default: false)"
}
```

**Response Schema (Non-Streaming):**
```json
{
  "conversation_id": "uuid",
  "message_id": "uuid",
  "response": "string (assistant message)",
  "tool_calls": [
    {
      "tool_name": "string",
      "tool_id": "string",
      "status": "success|error|pending",
      "result": "object"
    }
  ],
  "tokens": {
    "input": 150,
    "output": 320,
    "total": 470
  }
}
```

**Error Response:**
```json
{
  "error": "string",
  "error_code": "INVALID_REQUEST|RATE_LIMITED|UNAUTHORIZED|SERVER_ERROR",
  "request_id": "uuid"
}
```

**AC1.1:** Endpoint accepts valid conversation_id and returns existing conversation context ✓  
**AC1.2:** Endpoint creates new conversation if conversation_id is null ✓  
**AC1.3:** Response includes all tool calls executed with results ✓  
**AC1.4:** Token counts are accurate and returned ✓  
**AC1.5:** Invalid user_id returns 401 Unauthorized ✓  
**AC1.6:** Rate limit exceeded returns 429 Too Many Requests ✓  

---

#### FR2: Conversation Persistence

**Requirement:** Every user message and assistant response is persisted to PostgreSQL with full traceability.

**Database Tables:**

**conversations**
```sql
CREATE TABLE conversations (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  user_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
  title VARCHAR(255) DEFAULT 'New Conversation',
  created_at TIMESTAMP DEFAULT now(),
  updated_at TIMESTAMP DEFAULT now(),
  FOREIGN KEY (user_id) REFERENCES users(id)
);
```

**messages**
```sql
CREATE TABLE messages (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  conversation_id UUID NOT NULL REFERENCES conversations(id) ON DELETE CASCADE,
  user_id UUID NOT NULL,
  role VARCHAR(10) CHECK (role IN ('user', 'assistant')),
  content TEXT NOT NULL,
  tool_calls JSONB,
  tokens_used INTEGER,
  created_at TIMESTAMP DEFAULT now()
);

CREATE INDEX idx_messages_conversation ON messages(conversation_id);
CREATE INDEX idx_messages_user ON messages(user_id);
```

**AC2.1:** All user messages are stored with timestamp and metadata ✓  
**AC2.2:** All assistant responses are stored with tool_calls and tokens ✓  
**AC2.3:** Conversation history can be retrieved for resumption ✓  
**AC2.4:** Messages are immutable after creation ✓  

---

#### FR3: MCP Tools Implementation

**Tool 1: add_task**

```yaml
Name: add_task
Description: Create a new todo item
InputSchema:
  type: object
  required: [user_id, title]
  properties:
    user_id:
      type: string
      description: UUID of the user
    title:
      type: string
      minLength: 1
      maxLength: 256
      description: Task title
    description:
      type: string
      maxLength: 2048
      description: Optional task description
OutputSchema:
  type: object
  properties:
    success: boolean
    task_id: string
    title: string
    description: string
    created_at: string (ISO 8601)
ErrorCases:
  - InvalidTitle: Empty or > 256 chars
  - Unauthorized: user_id mismatch
```

**AC3.1:** Task created with valid title appears in database ✓  
**AC3.2:** Description is optional and trimmed ✓  
**AC3.3:** Task belongs to correct user ✓  
**AC3.4:** Invalid inputs return structured error ✓  

---

**Tool 2: list_tasks**

```yaml
Name: list_tasks
Description: Retrieve user's tasks with optional filtering
InputSchema:
  type: object
  required: [user_id]
  properties:
    user_id:
      type: string
    status:
      type: string
      enum: [all, pending, completed]
      default: all
    limit:
      type: integer
      minimum: 1
      maximum: 100
      default: 50
OutputSchema:
  type: object
  properties:
    tasks:
      type: array
      items:
        type: object
        properties:
          id: string
          title: string
          description: string
          completed: boolean
          created_at: string
    total: integer
    status_filter: string
ErrorCases:
  - InvalidStatus: status not in enum
  - Unauthorized: user_id mismatch
```

**AC3.5:** Returns all tasks when status=all ✓  
**AC3.6:** Filters correctly for pending and completed ✓  
**AC3.7:** Respects limit parameter ✓  
**AC3.8:** Only returns tasks for authenticated user ✓  

---

**Tool 3: complete_task**

```yaml
Name: complete_task
Description: Mark a task as completed
InputSchema:
  type: object
  required: [user_id, task_id]
  properties:
    user_id: string
    task_id: string (UUID of task to complete)
OutputSchema:
  type: object
  properties:
    success: boolean
    task_id: string
    title: string
    completed: boolean
    completed_at: string (ISO 8601)
ErrorCases:
  - TaskNotFound: task_id doesn't exist
  - Unauthorized: task doesn't belong to user
  - AlreadyCompleted: task already marked complete
```

**AC3.9:** Task marked complete updates database ✓  
**AC3.10:** Cannot complete already-completed task ✓  
**AC3.11:** Returns clear error for missing task ✓  

---

**Tool 4: delete_task**

```yaml
Name: delete_task
Description: Permanently delete a task
InputSchema:
  type: object
  required: [user_id, task_id]
  properties:
    user_id: string
    task_id: string
OutputSchema:
  type: object
  properties:
    success: boolean
    task_id: string
    title: string
    deleted_at: string
ErrorCases:
  - TaskNotFound: task doesn't exist
  - Unauthorized: task doesn't belong to user
  - OperationFailed: database error
```

**AC3.12:** Task is removed from database ✓  
**AC3.13:** Cascading deletes don't affect other users ✓  

---

**Tool 5: update_task**

```yaml
Name: update_task
Description: Update task title or description
InputSchema:
  type: object
  required: [user_id, task_id]
  properties:
    user_id: string
    task_id: string
    title:
      type: string
      maxLength: 256
    description:
      type: string
      maxLength: 2048
OutputSchema:
  type: object
  properties:
    success: boolean
    task_id: string
    title: string
    description: string
    updated_at: string
ErrorCases:
  - TaskNotFound: task doesn't exist
  - Unauthorized: task doesn't belong to user
  - InvalidInput: title or description invalid
```

**AC3.14:** Only provided fields are updated ✓  
**AC3.15:** Timestamps reflect update ✓  

---

#### FR4: Agent Intent Resolution

**Requirement:** OpenAI Agent must accurately interpret natural language and invoke correct tools.

**Supported Intents:**

| User Input | Detected Intent | Tools | Example |
|-----------|-----------------|-------|---------|
| "add a task called..." | CREATE | add_task | "add task: buy milk" |
| "what's on my list" | LIST | list_tasks(status=all) | "what tasks do I have?" |
| "mark X done" | COMPLETE | complete_task | "mark groceries done" |
| "delete X" | DELETE | delete_task | "remove that old task" |
| "update X to..." | UPDATE | update_task | "change X's description" |
| "find tasks with..." | SEARCH | list_tasks + filter | "find unfinished items" |
| "chain: find X then delete" | CHAIN | list_tasks → delete_task | "remove all completed tasks" |
| "what happened to X" | CLARIFY | N/A | "what about my grocery list?" |

**AC4.1:** Agent correctly detects CREATE intent ✓  
**AC4.2:** Agent correctly detects READ intent ✓  
**AC4.3:** Agent correctly detects UPDATE intent ✓  
**AC4.4:** Agent correctly detects DELETE intent ✓  
**AC4.5:** Agent chains multiple tools in sequence ✓  
**AC4.6:** Agent asks clarifying questions when ambiguous ✓  
**AC4.7:** Agent confirms before destructive operations ✓  

---

#### FR5: Multi-Turn Conversations

**Requirement:** Conversations maintain context across multiple turns without in-memory state.

**Conversation Flow Example:**
```
Turn 1:
  User: "I need to buy milk and bread"
  → add_task("milk", "grocery item")
  → add_task("bread", "grocery item")
  Assistant: "I've created two tasks: 'milk' and 'bread'"

Turn 2:
  User: "and add eggs"
  → Loads conversation history from DB
  → Understands context from Turn 1
  → add_task("eggs", "grocery item")
  Assistant: "Added eggs to your grocery list"

Turn 3:
  User: "mark milk done"
  → Finds "milk" task from history
  → complete_task(task_id)
  Assistant: "Marked milk as complete"
```

**AC5.1:** Conversation history is loaded from DB before each request ✓  
**AC5.2:** Agent maintains context across turns (no memory loss) ✓  
**AC5.3:** Conversation can be resumed after server restart ✓  
**AC5.4:** No in-memory buffer is used ✓  

---

#### FR6: Error Handling & Recovery

**Requirement:** System gracefully handles errors with clear user feedback.

**Error Categories:**

| Error | HTTP Status | Recovery |
|-------|------------|----------|
| Invalid conversation_id | 400 | Return new conversation_id |
| User not authenticated | 401 | Redirect to login |
| Rate limited | 429 | Retry after N seconds |
| Task not found | 404 | Suggest similar tasks |
| Database error | 500 | Log and retry (idempotent) |
| OpenAI quota exceeded | 503 | Queue for retry |

**AC6.1:** All errors include structured error responses ✓  
**AC6.2:** No stack traces leak to client ✓  
**AC6.3:** Request IDs enable debugging ✓  
**AC6.4:** Rate limits are enforced per user ✓  
**AC6.5:** Retry logic is implemented with exponential backoff ✓  

---

### Non-Functional Requirements

#### NFR1: Performance
- Chat API response time: < 5 seconds (p95), including OpenAI latency
- Tool execution: < 1 second per tool
- Database query: < 100ms
- Message persistence: < 50ms
- Conversation load: < 200ms

#### NFR2: Reliability
- 99.9% uptime SLA
- Graceful degradation if OpenAI API is unavailable
- Automatic retry with exponential backoff (3 attempts)
- Circuit breaker for external services

#### NFR3: Scalability
- Horizontal scaling via stateless design
- Support 10,000+ concurrent users
- PostgreSQL connection pooling (max 100 connections)
- No shared state between instances
- Load balancing via round-robin

#### NFR4: Security
- All API endpoints require authentication (Bearer token)
- Rate limiting: 100 requests per minute per user
- User context isolation enforced at every layer
- Input validation on all tool parameters
- SQL injection prevention via parameterized queries
- CORS configured for ChatKit domain only

#### NFR5: Maintainability
- TypeScript frontend (strict mode)
- Python backend with type hints (mypy)
- Comprehensive logging (structured JSON)
- Unit tests (>80% coverage)
- Integration tests for MCP tools
- Swagger API documentation

#### NFR6: Auditability
- All tool executions logged with user_id and timestamp
- Conversation history immutable after creation
- Message metadata includes token counts
- Soft deletes for compliance (GDPR)

---

## Plan (HOW) — Architecture & Components

### System Architecture

```
┌─────────────────────────────────────────────────────┐
│           Next.js Frontend (TypeScript)             │
│  ┌──────────────────────────────────────────────┐   │
│  │  ChatKit UI Component                        │   │
│  │  - Message display                           │   │
│  │  - Input field                               │   │
│  │  - Typing indicator                          │   │
│  │  - Tool call visualization                   │   │
│  └──────────────────────────────────────────────┘   │
└─────────────────────────────────────────────────────┘
              ↓ HTTPS (Bearer Token Auth)
┌─────────────────────────────────────────────────────┐
│       FastAPI Backend (Python 3.11+)               │
│  ┌──────────────────────────────────────────────┐   │
│  │  Endpoint: POST /api/{user_id}/chat          │   │
│  └──────────────────────────────────────────────┘   │
│  ┌──────────────────────────────────────────────┐   │
│  │  Middleware Layer                            │   │
│  │  - Authentication (Better Auth)              │   │
│  │  - Rate limiting                             │   │
│  │  - Request logging                           │   │
│  │  - Error handling                            │   │
│  └──────────────────────────────────────────────┘   │
│  ┌──────────────────────────────────────────────┐   │
│  │  Chat Service                                │   │
│  │  - Load conversation history                 │   │
│  │  - Append user message                       │   │
│  │  - Invoke OpenAI Agent                       │   │
│  │  - Execute MCP tools                         │   │
│  │  - Store responses                           │   │
│  └──────────────────────────────────────────────┘   │
│  ┌──────────────────────────────────────────────┐   │
│  │  MCP Server (Local Process)                  │   │
│  │  - add_task                                  │   │
│  │  - list_tasks                                │   │
│  │  - complete_task                             │   │
│  │  - delete_task                               │   │
│  │  - update_task                               │   │
│  └──────────────────────────────────────────────┘   │
└─────────────────────────────────────────────────────┘
              ↓ TCP (stdio/JSON-RPC)
┌─────────────────────────────────────────────────────┐
│           OpenAI Agents SDK                         │
│  - Intent resolution                               │
│  - Tool selection                                  │
│  - Response generation                             │
└─────────────────────────────────────────────────────┘
              ↓ HTTPS (API Key)
┌─────────────────────────────────────────────────────┐
│           OpenAI API (GPT-4 with tools)            │
│  - Processing natural language                     │
│  - Tool calling                                    │
│  - Response streaming                              │
└─────────────────────────────────────────────────────┘
              ↓ SQL (PgBouncer)
┌─────────────────────────────────────────────────────┐
│       Neon PostgreSQL (Serverless)                  │
│  - conversations table                             │
│  - messages table                                  │
│  - tasks table (existing)                          │
│  - users table (existing)                          │
└─────────────────────────────────────────────────────┘
```

---

### Component Breakdown

#### Component 1: FastAPI Server (`backend/app/main.py`)

**Responsibilities:**
- Route incoming HTTP requests
- Authenticate requests via Better Auth
- Apply middleware (CORS, rate limiting, logging)
- Delegate business logic to Chat Service

**File Structure:**
```
backend/
├── app/
│   ├── __init__.py
│   ├── main.py (FastAPI app setup)
│   ├── config.py (environment variables)
│   ├── database.py (SQLAlchemy async engine)
│   ├── middleware/
│   │   ├── __init__.py
│   │   ├── auth.py (Bearer token validation)
│   │   ├── rate_limit.py (per-user rate limiting)
│   │   ├── logging.py (structured JSON logging)
│   │   └── cors.py (ChatKit domain allowlist)
│   ├── models/
│   │   ├── __init__.py
│   │   ├── user.py (existing)
│   │   ├── task.py (existing)
│   │   ├── conversation.py (NEW)
│   │   └── message.py (NEW)
│   ├── schemas/
│   │   ├── __init__.py
│   │   ├── chat.py (ChatRequest, ChatResponse)
│   │   ├── tool.py (ToolCall)
│   │   └── error.py (ErrorResponse)
│   ├── routers/
│   │   ├── __init__.py
│   │   ├── chat.py (POST /api/{user_id}/chat)
│   │   ├── tasks.py (existing)
│   │   └── auth.py (existing)
│   ├── services/
│   │   ├── __init__.py
│   │   ├── chat_service.py (NEW - orchestration)
│   │   └── task_service.py (existing)
│   └── mcp/
│       ├── __init__.py
│       └── server.py (MCP Server implementation)
```

---

#### Component 2: Chat Service (`backend/app/services/chat_service.py`)

**Responsibilities:**
- Load conversation history from PostgreSQL
- Append user message to database
- Invoke OpenAI Agent with MCP tools
- Execute tool calls
- Persist assistant response
- Handle errors and retries

**Key Methods:**
```python
class ChatService:
    async def handle_chat(
        self,
        user_id: str,
        message: str,
        conversation_id: Optional[str] = None
    ) -> ChatResponse:
        # 1. Validate user_id
        # 2. Load/create conversation
        # 3. Load conversation history
        # 4. Append user message
        # 5. Invoke OpenAI Agent
        # 6. Execute tool calls
        # 7. Store assistant response
        # 8. Return response
        pass

    async def get_conversation_history(
        self,
        conversation_id: str
    ) -> List[Message]:
        # Query messages table
        pass

    async def execute_tool(
        self,
        tool_name: str,
        tool_input: dict,
        user_id: str
    ) -> dict:
        # Invoke MCP tool
        pass
```

---

#### Component 3: MCP Server (`backend/app/mcp/server.py`)

**Responsibilities:**
- Implement MCP protocol (stdio transport)
- Expose 5 tools with proper schemas
- Validate inputs
- Execute database operations
- Return structured responses

**Tool Implementation Pattern:**
```python
@mcp_server.tool()
async def add_task(
    user_id: str,
    title: str,
    description: Optional[str] = None
) -> dict:
    """Create a new todo task"""
    # 1. Validate inputs
    # 2. Create Task model
    # 3. Persist to database
    # 4. Return response
    pass
```

---

#### Component 4: Database Models (`backend/app/models/`)

**New Models:**

```python
# models/conversation.py
from sqlmodel import SQLModel, Field
from typing import Optional
from datetime import datetime
import uuid

class Conversation(SQLModel, table=True):
    __tablename__ = "conversations"
    
    id: uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True)
    user_id: uuid.UUID = Field(foreign_key="users.id", index=True)
    title: str = "New Conversation"
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)


# models/message.py
class Message(SQLModel, table=True):
    __tablename__ = "messages"
    
    id: uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True)
    conversation_id: uuid.UUID = Field(
        foreign_key="conversations.id",
        index=True
    )
    user_id: uuid.UUID = Field(index=True)
    role: str = Field(  # "user" or "assistant"
        sa_column=Column(String, CheckConstraint("role IN ('user', 'assistant')"))
    )
    content: str
    tool_calls: Optional[dict] = Field(default=None, sa_column=Column(JSON))
    tokens_used: Optional[int] = None
    created_at: datetime = Field(default_factory=datetime.utcnow)
```

---

#### Component 5: Frontend Chat UI (`frontend/components/chat/`)

**Structure:**
```
frontend/
├── components/
│   └── chat/
│       ├── ChatContainer.tsx (Main component)
│       ├── MessageList.tsx (Display messages)
│       ├── ChatInput.tsx (Input field + send)
│       ├── ToolCallVisualization.tsx (Show tool calls)
│       └── TypingIndicator.tsx (Loading state)
├── lib/
│   ├── chat-api.ts (POST /api/{user_id}/chat wrapper)
│   ├── conversation.ts (Conversation state management)
│   └── types.ts (TypeScript interfaces)
└── pages/
    └── chat/
        ├── [conversationId].tsx (Chat page)
        └── new.tsx (New conversation)
```

---

### Data Flow

#### Request Flow: User Sends Message

```
1. User types message in ChatKit UI
2. ChatInput component calls POST /api/{user_id}/chat
   ├─ Headers: Authorization: Bearer <token>
   └─ Body: { conversation_id, message }

3. FastAPI endpoint /api/{user_id}/chat receives request
   ├─ AuthMiddleware validates Bearer token
   ├─ RateLimitMiddleware checks user quota
   └─ LoggingMiddleware logs request

4. Chat router invokes ChatService.handle_chat()
   ├─ Load conversation_id (or create new)
   ├─ Query messages table for history
   ├─ Append user message to database
   ├─ Invoke OpenAI Agent with MCP tools
   │  └─ Agent calls add_task, list_tasks, etc.
   ├─ Execute MCP tools
   ├─ Store assistant response
   └─ Return ChatResponse

5. Frontend receives response
   ├─ Display assistant message
   ├─ Visualize tool calls
   └─ Append to conversation UI
```

---

#### Tool Execution Flow: Complete Task

```
1. User: "Mark groceries done"

2. ChatService invokes OpenAI Agent with:
   {
     "messages": [...conversation history...],
     "tools": [add_task, list_tasks, complete_task, delete_task, update_task]
   }

3. OpenAI Agent determines:
   - Intent: COMPLETE
   - Tool: complete_task
   - Parameters: { task_id: "abc123" }
   - But task_id is unknown, so Agent chains:
     1. Call list_tasks to find "groceries"
     2. Extract task_id from results
     3. Call complete_task with that task_id

4. ChatService executes MCP tools:
   a) invoke_tool("list_tasks", {user_id, status: "pending"})
      └─ MCP Server queries database
      └─ Returns all pending tasks
   b) Agent identifies "groceries" task_id
   c) invoke_tool("complete_task", {user_id, task_id})
      └─ MCP Server marks task.completed = true
      └─ Returns success response

5. Assistant response:
   "I've marked 'groceries' as complete!"

6. Response persisted to database
7. Returned to frontend
```

---

### Token Flow

```
User requests chat endpoint
    ↓
Better Auth validates Bearer token
    ↓
Token contains user_id (claim: sub)
    ↓
Extract user_id from token
    ↓
Validate user_id matches request parameter
    ↓
If mismatch → Return 403 Forbidden
    ↓
Proceed with chat logic using user_id
    ↓
All MCP tools receive validated user_id
    ↓
Tools enforce user context isolation
```

---

### Conversation State Management

**NO in-memory state:**
- Conversations stored in PostgreSQL
- Each request loads full history from DB
- No session affinity required
- Can be handled by any server instance

**Per-Request State:**
```python
@app.post("/api/{user_id}/chat")
async def chat(
    user_id: str,
    request: ChatRequest,
    session: AsyncSession = Depends(get_db)
):
    # State lives only during this request
    conversation = await load_conversation(
        session, request.conversation_id, user_id
    )
    messages = await load_messages(session, conversation.id)
    
    # Invoke agent (with all context loaded)
    response = await openai_agent.run(
        messages=messages,
        tools=mcp_tools
    )
    
    # Persist and return
    return response
    
    # Everything cleaned up after request ends
```

---

### Error Handling Strategy

**Layer 1: API Validation**
```python
@router.post("/api/{user_id}/chat")
async def chat(user_id: str, request: ChatRequest):
    try:
        # Pydantic validation happens here automatically
        # Invalid schema → 422 Unprocessable Entity
    except ValidationError as e:
        return ErrorResponse(
            error="Invalid request format",
            error_code="INVALID_REQUEST",
            details=e.errors()
        )
```

**Layer 2: Authentication**
```python
@app.middleware("http")
async def auth_middleware(request, call_next):
    try:
        token = extract_bearer_token(request.headers)
        user_id = validate_token(token)
        request.state.user_id = user_id
    except InvalidToken:
        return ErrorResponse(
            error="Unauthorized",
            error_code="UNAUTHORIZED"
        )
```

**Layer 3: Business Logic**
```python
async def handle_chat(user_id, message, conversation_id):
    try:
        conversation = await get_conversation(conversation_id)
        if conversation.user_id != user_id:
            raise PermissionDenied("Not your conversation")
        
        response = await openai_agent.run(...)
        return response
        
    except TaskNotFound:
        return ChatResponse(
            response="I couldn't find that task. Can you be more specific?"
        )
    except Exception as e:
        logger.error(f"Chat error: {e}", extra={request_id: uuid4()})
        return ErrorResponse(
            error="Server error",
            error_code="SERVER_ERROR",
            request_id=str(uuid4())
        )
```

**Layer 4: Tool Execution**
```python
@mcp_server.tool()
async def complete_task(user_id: str, task_id: str):
    try:
        task = await get_task(task_id)
        if task.user_id != user_id:
            raise PermissionDenied()
        if task.completed:
            raise AlreadyCompleted()
        
        task.completed = True
        await save_task(task)
        return {"success": True, "task_id": task_id}
        
    except TaskNotFound:
        return {"success": False, "error": "Task not found"}
    except AlreadyCompleted:
        return {"success": False, "error": "Task already completed"}
```

---

### Stateless Architecture Explanation

**Why Stateless?**
- Enables horizontal scaling
- No session affinity needed
- Fault tolerance (server can crash)
- Easier load balancing
- GDPR compliant (no cached PII)

**How to Achieve Stateless?**
1. Load all context from database per request
2. No in-memory buffers or caches
3. No thread-local conversation state
4. No session cookies (use Bearer tokens)
5. Idempotent operations

**Example: Multi-Server Scenario**
```
Request 1 (Server A):
├─ Load conversation history from DB
├─ Execute tools
└─ Store response

Request 2 (Server B):  ← Different server instance!
├─ Load conversation history from DB (same data!)
├─ Execute tools
└─ Store response

Both servers have access to SAME conversation state
No session affinity required
```

---

## Tasks (BREAKDOWN) — Atomic Work Units

### Phase III Implementation Tasks

#### Task Group 1: Database & Models

**T-001: Create Conversation & Message Tables**
- **Type:** Database Migration
- **Status:** Not Started
- **Preconditions:** Backend environment configured
- **Description:**
  - Create `conversations` table with user_id FK
  - Create `messages` table with conversation_id FK, role enum, JSONB tool_calls
  - Add indexes on (conversation_id), (user_id)
  - Write Alembic migration
- **Expected Output:**
  - Alembic migration file (v003_add_chat_tables.py)
  - Tables queryable and indexed
  - Auto-incrementing creation timestamps
- **Artifacts Modified:**
  - `backend/alembic/versions/003_*.py`
  - `backend/app/models/conversation.py`
  - `backend/app/models/message.py`
- **Effort:** 2 hours
- **Dependencies:** None
- **From Spec:** FR2

---

**T-002: Implement SQLModel Classes**
- **Type:** Code Implementation
- **Status:** Not Started
- **Preconditions:** T-001 complete
- **Description:**
  - Define `Conversation` SQLModel class
  - Define `Message` SQLModel class with role validation
  - Add validators for title max length, content max length
  - Add __repr__ for debugging
- **Expected Output:**
  - Two working SQLModel classes
  - Type-safe fields with validation
  - Relationships defined (cascade deletes)
- **Artifacts Modified:**
  - `backend/app/models/conversation.py`
  - `backend/app/models/message.py`
- **Effort:** 1.5 hours
- **Dependencies:** T-001
- **From Spec:** FR2

---

#### Task Group 2: MCP Tools & Server

**T-003: Implement MCP Server Scaffold**
- **Type:** Code Implementation
- **Status:** Not Started
- **Preconditions:** Backend environment configured
- **Description:**
  - Set up MCP server using official SDK
  - Configure stdio transport
  - Create tool registry structure
  - Implement error handling
- **Expected Output:**
  - MCP server accepting tool calls
  - JSON-RPC protocol working
  - Tool schema validation working
- **Artifacts Modified:**
  - `backend/app/mcp/__init__.py`
  - `backend/app/mcp/server.py`
  - `backend/app/mcp/tools/__init__.py`
- **Effort:** 2 hours
- **Dependencies:** None
- **From Spec:** FR3

---

**T-004: Implement MCP Tool: add_task**
- **Type:** Code Implementation
- **Status:** Not Started
- **Preconditions:** T-003, T-002
- **Description:**
  - Implement `add_task` MCP tool
  - Validate title (1-256 chars)
  - Validate description (max 2048 chars)
  - Enforce user_id ownership
  - Persist to database
  - Return structured response
- **Expected Output:**
  - Tool accepts valid inputs and creates task
  - Tool rejects invalid inputs with error
  - Task appears in database
- **Artifacts Modified:**
  - `backend/app/mcp/tools/task_tools.py`
- **Unit Tests:**
  - test_add_task_valid
  - test_add_task_invalid_title
  - test_add_task_unauthorized
- **Effort:** 2 hours
- **Dependencies:** T-003, T-002
- **From Spec:** FR3

---

**T-005: Implement MCP Tool: list_tasks**
- **Type:** Code Implementation
- **Status:** Not Started
- **Preconditions:** T-003, T-002
- **Description:**
  - Implement `list_tasks` MCP tool
  - Support status filter (all, pending, completed)
  - Support limit parameter
  - Enforce user_id ownership
  - Return paginated results
- **Expected Output:**
  - Filters work correctly
  - Limit respected
  - All/pending/completed states distinguished
- **Artifacts Modified:**
  - `backend/app/mcp/tools/task_tools.py`
- **Unit Tests:**
  - test_list_tasks_all
  - test_list_tasks_pending
  - test_list_tasks_completed
  - test_list_tasks_limit
- **Effort:** 1.5 hours
- **Dependencies:** T-003, T-002
- **From Spec:** FR3

---

**T-006: Implement MCP Tool: complete_task**
- **Type:** Code Implementation
- **Status:** Not Started
- **Preconditions:** T-003, T-002
- **Description:**
  - Implement `complete_task` MCP tool
  - Find task by task_id
  - Enforce user_id ownership
  - Prevent double-completion
  - Update completed timestamp
- **Expected Output:**
  - Task marked complete
  - Cannot re-complete
  - Returns timestamp
- **Artifacts Modified:**
  - `backend/app/mcp/tools/task_tools.py`
- **Unit Tests:**
  - test_complete_task_success
  - test_complete_task_already_completed
  - test_complete_task_unauthorized
  - test_complete_task_not_found
- **Effort:** 1.5 hours
- **Dependencies:** T-003, T-002
- **From Spec:** FR3

---

**T-007: Implement MCP Tool: delete_task**
- **Type:** Code Implementation
- **Status:** Not Started
- **Preconditions:** T-003, T-002
- **Description:**
  - Implement `delete_task` MCP tool
  - Find task by task_id
  - Enforce user_id ownership
  - Hard delete from database
  - Return confirmation
- **Expected Output:**
  - Task removed from database
  - Cannot delete again
  - Clear error messages
- **Artifacts Modified:**
  - `backend/app/mcp/tools/task_tools.py`
- **Unit Tests:**
  - test_delete_task_success
  - test_delete_task_not_found
  - test_delete_task_unauthorized
- **Effort:** 1.5 hours
- **Dependencies:** T-003, T-002
- **From Spec:** FR3

---

**T-008: Implement MCP Tool: update_task**
- **Type:** Code Implementation
- **Status:** Not Started
- **Preconditions:** T-003, T-002
- **Description:**
  - Implement `update_task` MCP tool
  - Accept optional title and description
  - Validate provided fields
  - Enforce user_id ownership
  - Update only provided fields
- **Expected Output:**
  - Partial updates work
  - Validation enforced
  - Timestamps updated
- **Artifacts Modified:**
  - `backend/app/mcp/tools/task_tools.py`
- **Unit Tests:**
  - test_update_task_title
  - test_update_task_description
  - test_update_task_both
  - test_update_task_invalid
- **Effort:** 1.5 hours
- **Dependencies:** T-003, T-002
- **From Spec:** FR3

---

#### Task Group 3: Chat Service & API

**T-009: Implement Chat Service**
- **Type:** Code Implementation
- **Status:** Not Started
- **Preconditions:** T-002, T-008
- **Description:**
  - Create `ChatService` class
  - Implement `handle_chat()` method
  - Load/create conversations
  - Load conversation history
  - Persist user messages and responses
  - Handle MCP tool execution
- **Expected Output:**
  - Chat service accepts requests
  - Conversations created/loaded
  - Messages persisted
  - Tool calls executed
- **Artifacts Modified:**
  - `backend/app/services/chat_service.py`
- **Effort:** 3 hours
- **Dependencies:** T-002, T-008
- **From Spec:** FR1, FR5

---

**T-010: Integrate OpenAI Agents SDK**
- **Type:** Code Implementation
- **Status:** Not Started
- **Preconditions:** T-009, T-003
- **Description:**
  - Install OpenAI Agents SDK
  - Configure API key from environment
  - Instantiate Agent with MCP tools
  - Implement agent invocation with conversation history
  - Handle tool calling and response generation
- **Expected Output:**
  - Agent successfully initialized
  - Agent receives messages and tools
  - Agent calls tools correctly
  - Responses generated
- **Artifacts Modified:**
  - `backend/requirements.txt`
  - `backend/app/services/chat_service.py`
  - `backend/app/config.py`
- **Effort:** 2 hours
- **Dependencies:** T-009, T-003
- **From Spec:** FR4

---

**T-011: Implement Chat API Endpoint**
- **Type:** Code Implementation
- **Status:** Not Started
- **Preconditions:** T-009, T-010
- **Description:**
  - Create `POST /api/{user_id}/chat` endpoint
  - Define request/response schemas
  - Implement auth validation
  - Call ChatService.handle_chat()
  - Return formatted response
  - Handle errors
- **Expected Output:**
  - Endpoint accepts requests
  - Returns per-spec response schema
  - Authentication enforced
  - Errors handled gracefully
- **Artifacts Modified:**
  - `backend/app/routers/chat.py`
  - `backend/app/schemas/chat.py`
  - `backend/app/main.py`
- **Unit Tests:**
  - test_chat_endpoint_valid_request
  - test_chat_endpoint_unauthorized
  - test_chat_endpoint_new_conversation
  - test_chat_endpoint_with_conversation_id
- **Effort:** 2 hours
- **Dependencies:** T-009, T-010
- **From Spec:** FR1

---

**T-012: Implement Rate Limiting Middleware**
- **Type:** Code Implementation
- **Status:** Not Started
- **Preconditions:** None
- **Description:**
  - Create rate limit middleware
  - Track requests per user_id
  - Enforce 100 req/min limit
  - Return 429 when exceeded
  - Log rate limit events
- **Expected Output:**
  - Rate limits enforced
  - 429 responses on breach
  - Requests counted per user
- **Artifacts Modified:**
  - `backend/app/middleware/rate_limit.py`
  - `backend/app/main.py`
- **Effort:** 1.5 hours
- **Dependencies:** None
- **From Spec:** NFR4

---

#### Task Group 4: Frontend Integration

**T-013: Create Chat UI Components**
- **Type:** Code Implementation (React/TypeScript)
- **Status:** Not Started
- **Preconditions:** Existing Next.js frontend
- **Description:**
  - Create ChatContainer.tsx main component
  - Create MessageList.tsx for displaying messages
  - Create ChatInput.tsx for user input
  - Create ToolCallVisualization.tsx
  - Create TypingIndicator.tsx
  - Style with Tailwind CSS
- **Expected Output:**
  - Chat UI renders messages
  - Input field functional
  - Messages styled properly
  - Tool calls visualized
- **Artifacts Modified:**
  - `frontend/components/chat/ChatContainer.tsx`
  - `frontend/components/chat/MessageList.tsx`
  - `frontend/components/chat/ChatInput.tsx`
  - `frontend/components/chat/ToolCallVisualization.tsx`
  - `frontend/components/chat/TypingIndicator.tsx`
- **Effort:** 3 hours
- **Dependencies:** None
- **From Spec:** UI/UX

---

**T-014: Implement Chat API Client**
- **Type:** Code Implementation (TypeScript)
- **Status:** Not Started
- **Preconditions:** T-011
- **Description:**
  - Create chat-api.ts wrapper
  - Implement POST /api/{user_id}/chat call
  - Handle streaming vs non-streaming
  - Type-safe request/response
  - Error handling
- **Expected Output:**
  - API client works
  - Type safety enforced
  - Errors caught and logged
  - Streaming implemented
- **Artifacts Modified:**
  - `frontend/lib/chat-api.ts`
  - `frontend/lib/types.ts`
- **Effort:** 1.5 hours
- **Dependencies:** T-011
- **From Spec:** FR1

---

**T-015: Implement Conversation State Management**
- **Type:** Code Implementation (React Hooks)
- **Status:** Not Started
- **Preconditions:** T-014
- **Description:**
  - Create useConversation hook
  - Manage conversation_id state
  - Manage messages array
  - Implement message sending
  - Handle loading states
  - Error recovery
- **Expected Output:**
  - Conversation state managed
  - Messages displayed correctly
  - Loading states work
  - Errors displayed
- **Artifacts Modified:**
  - `frontend/hooks/useConversation.ts`
  - `frontend/lib/conversation.ts`
- **Effort:** 2 hours
- **Dependencies:** T-014
- **From Spec:** FR5

---

**T-016: Create Chat Pages**
- **Type:** Code Implementation (Next.js)
- **Status:** Not Started
- **Preconditions:** T-015
- **Description:**
  - Create /chat/new page (new conversation)
  - Create /chat/[conversationId] page (resume)
  - Add navigation between pages
  - Add conversation list sidebar
  - Add styling
- **Expected Output:**
  - Pages render
  - Navigation works
  - Conversations loadable
  - Resumable conversations
- **Artifacts Modified:**
  - `frontend/app/(app)/chat/new/page.tsx`
  - `frontend/app/(app)/chat/[conversationId]/page.tsx`
  - `frontend/components/chat/ConversationList.tsx`
- **Effort:** 2 hours
- **Dependencies:** T-015
- **From Spec:** FR1, FR5

---

#### Task Group 5: Testing & Documentation

**T-017: Unit Tests for MCP Tools**
- **Type:** Testing
- **Status:** Not Started
- **Preconditions:** T-004 through T-008
- **Description:**
  - Write pytest tests for each tool
  - Test valid inputs
  - Test invalid inputs
  - Test user context isolation
  - Test error cases
  - Target 90%+ coverage
- **Expected Output:**
  - All tests passing
  - >90% code coverage
  - Clear test names
- **Artifacts Modified:**
  - `backend/tests/test_mcp_tools.py`
- **Effort:** 3 hours
- **Dependencies:** T-004 through T-008
- **From Spec:** NFR5

---

**T-018: Integration Tests for Chat API**
- **Type:** Testing
- **Status:** Not Started
- **Preconditions:** T-011
- **Description:**
  - Test full chat flow end-to-end
  - Test conversation persistence
  - Test authentication
  - Test rate limiting
  - Test error responses
- **Expected Output:**
  - Integration tests passing
  - Full chat flow verified
  - Edge cases covered
- **Artifacts Modified:**
  - `backend/tests/test_chat_api.py`
- **Effort:** 2 hours
- **Dependencies:** T-011
- **From Spec:** NFR5

---

**T-019: Frontend Chat Tests**
- **Type:** Testing (Jest/React Testing Library)
- **Status:** Not Started
- **Preconditions:** T-016
- **Description:**
  - Test ChatContainer component
  - Test MessageList rendering
  - Test ChatInput functionality
  - Test API client calls
  - Mock backend responses
- **Expected Output:**
  - Component tests passing
  - User interactions tested
  - API mocking working
- **Artifacts Modified:**
  - `frontend/__tests__/components/chat/ChatContainer.test.tsx`
  - `frontend/__tests__/lib/chat-api.test.ts`
- **Effort:** 2 hours
- **Dependencies:** T-016
- **From Spec:** NFR5

---

**T-020: API Documentation**
- **Type:** Documentation
- **Status:** Not Started
- **Preconditions:** T-011
- **Description:**
  - Document Chat API endpoint
  - Document request/response schemas
  - Document error codes
  - Document authentication
  - Document rate limiting
  - Add Swagger annotations
- **Expected Output:**
  - Swagger docs complete
  - All endpoints documented
  - Schemas clear
  - Examples provided
- **Artifacts Modified:**
  - `backend/app/routers/chat.py` (docstrings)
  - `README.md` (API reference)
- **Effort:** 1.5 hours
- **Dependencies:** T-011, T-020
- **From Spec:** NFR5

---

**T-021: Deployment Guide**
- **Type:** Documentation
- **Status:** Not Started
- **Preconditions:** All phases complete
- **Description:**
  - Document environment variables needed
  - Document CORS setup (ChatKit domain)
  - Document OpenAI API key setup
  - Document Neon connection
  - Document deployment steps (Docker, K8s)
  - Document scaling recommendations
- **Expected Output:**
  - Comprehensive deployment guide
  - All configuration documented
  - Troubleshooting included
- **Artifacts Modified:**
  - `DEPLOYMENT.md`
  - `docker-compose.prod.yml`
  - `.env.example`
- **Effort:** 2 hours
- **Dependencies:** All tasks
- **From Spec:** NFR3, NFR6

---

### Task Execution Order

```
Phase 1: Database Setup
  ├─ T-001: Create tables
  └─ T-002: Define models

Phase 2: MCP Tools
  ├─ T-003: MCP scaffold
  ├─ T-004-T-008: Individual tools
  └─ T-017: Tool tests

Phase 3: Chat Service
  ├─ T-009: Chat service
  ├─ T-010: OpenAI integration
  ├─ T-011: Chat endpoint
  ├─ T-012: Rate limiting
  ├─ T-018: Integration tests
  └─ T-020: API docs

Phase 4: Frontend
  ├─ T-013: Chat UI components
  ├─ T-014: Chat API client
  ├─ T-015: State management
  ├─ T-016: Chat pages
  ├─ T-019: Frontend tests
  └─ Done!

Phase 5: Documentation & Deployment
  └─ T-021: Deployment guide
```

---

## Appendix

### Appendix A: Security Considerations

#### A1: Authentication & Authorization
- All endpoints require Bearer token from Better Auth
- Token validated via JWT verification
- user_id extracted from token claims
- Request user_id must match token user_id
- Tokens expire after 24 hours

#### A2: Input Validation
- All MCP tool inputs validated against schema
- String lengths enforced (title: 1-256, desc: max 2048)
- Only allowed statuses accepted (all, pending, completed)
- Invalid inputs rejected with 400 Bad Request

#### A3: SQL Injection Prevention
- SQLModel uses parameterized queries
- No string concatenation in queries
- All user input escaped automatically

#### A4: Rate Limiting
- Per-user rate limit: 100 req/min
- Per-IP fallback: 1000 req/min
- Excess requests return 429
- No silent drops (client notified)

#### A5: Data Residency
- All data in PostgreSQL
- No external APIs
- No caching of user data
- Soft deletes for GDPR compliance

#### A6: CORS Configuration
- Allowed domains: api.chatkit.com, localhost:3000 (dev)
- No wildcard allowed
- Credentials handled properly

#### A7: Logging & Audit Trail
- All tool executions logged with timestamp, user_id, tool_name
- No passwords or secrets in logs
- Structured JSON logging
- Request IDs for tracing

---

### Appendix B: Scalability & Deployment

#### B1: Horizontal Scaling
- Stateless design enables multiple instances
- Load balancer (nginx/HAProxy) distributes traffic
- No session affinity needed
- Database connection pooling (PgBouncer)

#### B2: Performance Optimization
- Database indexes on (conversation_id), (user_id)
- Query results cached in Redis (optional)
- OpenAI API calls parallelized where possible
- Connection reuse via async SQLAlchemy

#### B3: Deployment Architecture
```
┌─────────────────────────────────────┐
│       Load Balancer (nginx)         │
├─────────────────────────────────────┤
│ ┌──────────┐  ┌──────────┐  ...     │ ← Multiple instances
│ │ FastAPI  │  │ FastAPI  │         │
│ │ Instance │  │ Instance │         │
│ └──────────┘  └──────────┘         │
├─────────────────────────────────────┤
│ PgBouncer Connection Pool          │
├─────────────────────────────────────┤
│ Neon PostgreSQL (Serverless)       │
└─────────────────────────────────────┘
```

#### B4: Deployment Steps
1. Build Docker images (backend + frontend)
2. Push to container registry
3. Deploy to Kubernetes / Docker Swarm / Heroku
4. Configure environment variables
5. Run database migrations
6. Warm up connections
7. Monitor logs and metrics

#### B5: Scaling Limits
- Neon PostgreSQL: up to 100K connections (with pooling)
- OpenAI API: rate limits per organization
- Memory: stateless (no accumulation)
- CDN for frontend assets: CloudFront / Fastly

---

### Appendix C: Error Reference

| Error Code | HTTP | Description | Recovery |
|-----------|------|-------------|----------|
| INVALID_REQUEST | 400 | Malformed request | Check schema |
| UNAUTHORIZED | 401 | No/invalid Bearer token | Reauth user |
| FORBIDDEN | 403 | User context mismatch | Check user_id |
| NOT_FOUND | 404 | Task/conversation not found | Create new |
| RATE_LIMITED | 429 | Exceeds rate limit | Retry after N sec |
| SERVER_ERROR | 500 | Internal error | Check logs |
| SERVICE_UNAVAILABLE | 503 | OpenAI API down | Queue/retry |

---

### Appendix D: Conversation Example

**User:** "I need to buy milk, eggs, and bread"

**Assistant:** ✓ I'll create three tasks for your shopping list.
1. ✓ Created: "milk"
2. ✓ Created: "eggs"  
3. ✓ Created: "bread"

---

**User:** "what's on my list?"

**Assistant:** Here are your current tasks:
- [ ] milk
- [ ] eggs
- [ ] bread

---

**User:** "mark milk done"

**Assistant:** ✓ I've completed "milk". You now have 2 pending tasks.

---

**User:** "update eggs to 'brown eggs' and add a description"

**Assistant:** I need to clarify - what description would you like for "brown eggs"?

**User:** "from the farm"

**Assistant:** ✓ Updated "eggs" to "brown eggs" with description "from the farm"

---

**User:** "delete everything I've completed"

**Assistant:** I don't see any completed tasks. Would you like me to mark something as done first?

---

### Appendix E: Configuration Variables

```env
# Backend
DATABASE_URL=postgresql+asyncpg://user:pass@neon.tech/dbname
OPENAI_API_KEY=sk-...
OPENAI_MODEL=gpt-4-1106-preview
BETTER_AUTH_SECRET=...
CORS_ALLOWED_ORIGINS=https://app.chatkit.com,http://localhost:3000

# Frontend
NEXT_PUBLIC_API_URL=https://api.example.com
NEXT_PUBLIC_AUTH_URL=https://auth.example.com
```

---

### Appendix F: Folder Structure

```
d:/Todo-hackathon/
├── backend/
│   ├── app/
│   │   ├── main.py
│   │   ├── config.py
│   │   ├── database.py
│   │   ├── middleware/
│   │   │   ├── auth.py
│   │   │   ├── rate_limit.py
│   │   │   └── logging.py
│   │   ├── models/
│   │   │   ├── user.py
│   │   │   ├── task.py
│   │   │   ├── conversation.py (NEW)
│   │   │   └── message.py (NEW)
│   │   ├── schemas/
│   │   │   ├── chat.py (NEW)
│   │   │   └── error.py (NEW)
│   │   ├── routers/
│   │   │   ├── auth.py
│   │   │   ├── tasks.py
│   │   │   └── chat.py (NEW)
│   │   ├── services/
│   │   │   ├── task_service.py
│   │   │   └── chat_service.py (NEW)
│   │   └── mcp/
│   │       ├── server.py (NEW)
│   │       └── tools/
│   │           └── task_tools.py (NEW)
│   ├── tests/
│   │   ├── test_mcp_tools.py (NEW)
│   │   ├── test_chat_api.py (NEW)
│   │   └── conftest.py
│   ├── alembic/
│   │   └── versions/
│   │       └── 003_add_chat_tables.py (NEW)
│   └── requirements.txt
├── frontend/
│   ├── components/
│   │   └── chat/ (NEW)
│   │       ├── ChatContainer.tsx
│   │       ├── MessageList.tsx
│   │       ├── ChatInput.tsx
│   │       ├── ToolCallVisualization.tsx
│   │       └── TypingIndicator.tsx
│   ├── app/
│   │   └── (app)/
│   │       └── chat/ (NEW)
│   │           ├── new/
│   │           │   └── page.tsx
│   │           └── [conversationId]/
│   │               └── page.tsx
│   ├── lib/
│   │   ├── chat-api.ts (NEW)
│   │   └── conversation.ts (NEW)
│   ├── hooks/
│   │   └── useConversation.ts (NEW)
│   └── __tests__/
│       └── chat/ (NEW)
└── specs/
    └── 003-phase3-chatbot/
        ├── SPECIFICATION.md (THIS FILE)
        ├── ARCHITECTURE.md
        ├── API_CONTRACTS.md
        ├── TOOL_SCHEMAS.md
        └── DEPLOYMENT.md
```

---

### Appendix G: Implementation Checklist

#### Phase 1: Database Setup
- [ ] T-001: Create migration
- [ ] T-002: Define SQLModel classes
- [ ] Database verified with schema inspection

#### Phase 2: MCP Tools
- [ ] T-003: MCP server scaffold
- [ ] T-004: add_task tool
- [ ] T-005: list_tasks tool
- [ ] T-006: complete_task tool
- [ ] T-007: delete_task tool
- [ ] T-008: update_task tool
- [ ] T-017: Tool tests passing

#### Phase 3: Chat Service
- [ ] T-009: Chat service implemented
- [ ] T-010: OpenAI integration
- [ ] T-011: API endpoint
- [ ] T-012: Rate limiting
- [ ] T-018: Integration tests passing
- [ ] T-020: API documented

#### Phase 4: Frontend
- [ ] T-013: Chat UI components
- [ ] T-014: Chat API client
- [ ] T-015: State management
- [ ] T-016: Chat pages
- [ ] T-019: Frontend tests passing

#### Phase 5: Deployment
- [ ] T-021: Deployment guide
- [ ] Environment variables configured
- [ ] CORS allowlist set
- [ ] Production deployment tested

---

## Sign-Off

**Specification Status:** ✅ APPROVED FOR IMPLEMENTATION

**Prepared By:** AI Specification Agent  
**Date:** February 8, 2026  
**Version:** 1.0  

**Next Step:** Implement tasks in order (T-001 through T-021)

---

**End of Specification**
