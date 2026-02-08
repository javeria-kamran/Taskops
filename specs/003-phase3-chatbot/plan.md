# Phase III: Todo AI Chatbot - Implementation Plan

**Version**: 1.0
**Status**: Ready for Execution
**Created**: February 8, 2026
**Document Type**: Architecture & Implementation Plan

---

## Executive Summary

This document outlines the implementation strategy for Phase III: Todo AI Chatbot, which extends the existing Todo application with conversational task management via OpenAI Agents and the Model Context Protocol (MCP).

**Core Innovation**: A **stateless backend** that processes chat requests independently, loading conversation context from PostgreSQL and persisting changes transactionally—enabling unlimited horizontal scaling without session affinity.

**Timeline**: 8 weeks total (6 weeks critical path + 2 weeks parallel/testing)

**Team Structure**: 5 developers (1 lead architect, 2 backend engineers, 1 frontend engineer, 1 DevOps/QA)

---

## Table of Contents

1. [Architecture Strategy](#architecture-strategy)
2. [Implementation Order & Rationale](#implementation-order--rationale)
3. [Phase Breakdown](#phase-breakdown)
4. [Stateless Architecture Deep Dive](#stateless-architecture-deep-dive)
5. [Tool Invocation & Agent Strategy](#tool-invocation--agent-strategy)
6. [Data Flow Analysis](#data-flow-analysis)
7. [Scalability & Performance](#scalability--performance)
8. [Security Strategy](#security-strategy)
9. [Risk Assessment & Mitigation](#risk-assessment--mitigation)
10. [Success Metrics & Validation](#success-metrics--validation)

---

## Architecture Strategy

### Component Interaction Model

```
┌─────────────────────────────────────────────────────────────────┐
│                     Frontend (Next.js + ChatKit)                │
│                                                                 │
│  ┌──────────────────────────────────────────────────────────┐  │
│  │  OpenAI ChatKit UI                                       │  │
│  │  - Message rendering                                    │  │
│  │  - Input field                                          │  │
│  │  - Loading indicators                                  │  │
│  └──────────────────────────────────────────────────────────┘  │
└─────────────────────────────────────────────────────────────────┘
                              ↓
                    POST /api/{user_id}/chat
                    + JWT Token
                    + {conversation_id?, message}
                              ↓
┌─────────────────────────────────────────────────────────────────┐
│                    FastAPI Backend (Stateless)                  │
│                                                                 │
│  ┌──────────────────────────────────────────────────────────┐  │
│  │ 1. Request Handler (Chat Router)                         │  │
│  │    - Validate JWT → Extract user_id                     │  │
│  │    - Load conversation history from PostgreSQL         │  │
│  │    - Validate user owns conversation                   │  │
│  └──────────────────────────────────────────────────────────┘  │
│                         ↓                                       │
│  ┌──────────────────────────────────────────────────────────┐  │
│  │ 2. Message Processor (Chat Service)                      │  │
│  │    - Append user message to history                    │  │
│  │    - Format messages for OpenAI                        │  │
│  │    - Invoke agent with context                         │  │
│  └──────────────────────────────────────────────────────────┘  │
│                         ↓                                       │
│  ┌──────────────────────────────────────────────────────────┐  │
│  │ 3. AI Agent Orchestrator (OpenAI Agents SDK)            │  │
│  │    - Receives: conversation history, new message       │  │
│  │    - Detects intent from natural language              │  │
│  │    - Routes to appropriate MCP tools                   │  │
│  │    - Executes tool calls sequentially                  │  │
│  │    - Generates response to user                        │  │
│  │    - Returns: response text + tool_calls array         │  │
│  └──────────────────────────────────────────────────────────┘  │
│                         ↓                                       │
│  ┌──────────────────────────────────────────────────────────┐  │
│  │ 4. MCP Tool Server (Official MCP SDK)                   │  │
│  │    - Exposes 5 tools:                                  │  │
│  │      * add_task(title, description)                   │  │
│  │      * list_tasks(status: all|pending|completed)      │  │
│  │      * complete_task(task_id)                         │  │
│  │      * delete_task(task_id)                           │  │
│  │      * update_task(task_id, title?, description?)     │  │
│  │    - Each tool: validates input → queries DB           │  │
│  │    - Returns: structured JSON response                 │  │
│  └──────────────────────────────────────────────────────────┘  │
│                         ↓                                       │
│  ┌──────────────────────────────────────────────────────────┐  │
│  │ 5. Repository Layer (SQLModel ORM)                      │  │
│  │    - Task operations: create, read, update, delete     │  │
│  │    - Conversation management                           │  │
│  │    - Message persistence                               │  │
│  │    - User isolation enforcement                        │  │
│  └──────────────────────────────────────────────────────────┘  │
└─────────────────────────────────────────────────────────────────┘
                              ↓
┌─────────────────────────────────────────────────────────────────┐
│                  Neon PostgreSQL Database                       │
│                                                                 │
│  Tables:                                                        │
│  - conversations (id, user_id, created_at, updated_at)        │
│  - messages (id, conversation_id, user_id, role, content)     │
│  - tasks (id, user_id, title, description, completed)         │
│  - users (id, email, created_at)                              │
│                                                                │
│  Indexes:                                                       │
│  - messages(conversation_id, created_at) → fast history load  │
│  - tasks(user_id, completed) → fast task filtering            │
│  - conversations(user_id, created_at DESC) → list conversations│
└─────────────────────────────────────────────────────────────────┘
```

### Separation of Concerns

| Layer | Responsibility | Technology | Statefulness |
|-------|-----------------|-----------|--------------|
| **Frontend** | Message UI, input, display responses | Next.js + ChatKit | Stateful (client-side) |
| **API Router** | HTTP handling, JWT validation, user routing | FastAPI + Pydantic | **Stateless** |
| **Chat Service** | Orchestration, history loading, agent invocation | Python business logic | **Stateless** |
| **Agent Orchestrator** | Intent detection, tool routing, response generation | OpenAI Agents SDK | **Stateless** (per-request) |
| **MCP Tools** | Database mutations, CRUD operations, validation | MCP SDK + SQLModel | **Stateless** (functions) |
| **Repository** | Database abstraction, query building | SQLModel ORM | **Stateless** (no caching) |
| **Database** | Persistent state, conversation history, task data | Neon PostgreSQL | **Stateful** (source of truth) |

### Key Design Principles

1. **Single Responsibility**: Each layer handles exactly one concern
2. **Dependency Inversion**: High-level modules don't depend on low-level details
3. **Testability**: Each layer independently testable via mocking dependencies
4. **Scalability**: No shared state between request handlers; unlimited horizontal scaling
5. **Auditability**: Full conversation history persisted; every interaction traceable

---

## Implementation Order & Rationale

### Why This Sequence?

```
Database Models (Phase 1)
    ↓
    Why: MCP tools need task queries; conversation persistence needs schema

MCP Tool Layer (Phase 2)
    ↓
    Why: Agent needs tools exposed; tools must be tested independently

AI Agent Configuration (Phase 3)
    ↓
    Why: Chat endpoint needs agent; agent needs tools registered

Stateless Chat Endpoint (Phase 4)
    ↓
    Why: Endpoint orchestrates everything above; frontend depends on this

Frontend Integration (Phase 5)
    ↓
    Why: Frontend consumes API; API must be complete and tested first

Security & Auth (Phase 6)
    ↓
    Why: Applied late to avoid re-work; but before production deployment

Testing & Validation (Phase 7)
    ↓
    Why: Tests all prior work; catches integration issues early

Deployment (Phase 8)
    ↓
    Why: Only deploy tested, validated system
```

### Critical Path Analysis

**Minimum sequence** (no parallelization):
```
Phase 1 (Database) → Phase 2 (MCP) → Phase 3 (Agent) → Phase 4 (Endpoint)
→ Phase 5 (Frontend) → Phase 6 (Security) → Phase 7 (Testing) → Phase 8 (Deploy)
= 8 weeks sequential
```

**With parallelization**:
```
Phase 1 (1 week)
    ↓
Phase 2 + Phase 3 (parallel, 2 weeks)
    ↓
Phase 4 (1 week)
    ↓
Phase 5 + Phase 6 (parallel, 2 weeks)
    ↓
Phase 7 (1 week)
    ↓
Phase 8 (1 week)
= 8 weeks total, but Phase 2 & 3 concurrent, Phase 5 & 6 concurrent
```

**Optimized** (full parallelization):
```
Phase 1 (1 week) - Foundation
    ↓
Phase 2 + 3 + 4 (2 weeks, highly parallel backend work)
    ↓
Phase 5 + 6 (2 weeks, frontend & security parallel)
    ↓
Phase 7 (1 week) - Testing
    ↓
Phase 8 (1 week) - Deployment
= 7 weeks with proper team allocation
```

---

## Phase Breakdown

### Phase 1: Database Foundation

**Duration**: 1 week
**Team**: 1 backend engineer (DB specialist)
**Blocker**: Yes (foundation for all subsequent work)

#### Objectives

- Define SQLModel data models for conversations, messages
- Create Alembic migrations
- Apply migrations to Neon PostgreSQL
- Verify data persists correctly
- Establish DB session management patterns

#### Key Components

| Component | Description | Technology |
|-----------|-------------|-----------|
| Conversation Model | Stores chat session metadata | SQLModel |
| Message Model | Stores user/assistant messages in conversation | SQLModel |
| Task Model | Extends existing Phase II task model | SQLModel |
| Alembic Migration | Version-controlled schema changes | Alembic |
| Repository Layer | Data access abstraction | SQLModel ORM |

#### Dependencies

- Existing Phase II database setup
- Neon PostgreSQL credentials
- SQLModel library (already in requirements)

#### Architecture Decisions

**Decision**: Why store conversations separately from messages?
- **Rationale**: Conversations group messages semantically; enables suspending/resuming chats; allows future features (sharing, archiving)
- **Trade-off**: Additional JOIN on message queries vs. semantic clarity and future extensibility
- **Mitigation**: Index on (conversation_id, created_at) optimizes queries

**Decision**: Why store tool_calls as JSONB in messages?
- **Rationale**: Future auditing, debugging, replay capability
- **Trade-off**: Slightly larger database footprint (~1KB per tool_call)
- **Mitigation**: Archive old messages to cold storage if needed

#### Risks & Mitigation

| Risk | Probability | Impact | Mitigation |
|------|-----------|--------|-----------|
| Neon connectivity issues | Medium | Blocks all work | Fallback to local SQLite for dev (already configured) |
| Schema migration errors | Low | Data corruption | Test migrations in staging first; have rollback plan |
| N+1 query problems | Medium | Performance issues | Use eager loading; proper indexing from start |

#### Definition of Done

- ✅ Conversation model defined with relationships to messages
- ✅ Message model stores role, content, tool_calls
- ✅ Task model verified compatible
- ✅ Alembic migration file created and tested
- ✅ Database schema applied to development Neon instance
- ✅ Repository methods (CRUD) implemented and tested
- ✅ User isolation verified (queries filter by user_id)
- ✅ Performance baseline established (<500ms for history load)

#### Validation Strategy

```sql
-- Verify schema
SELECT * FROM information_schema.tables
WHERE table_name IN ('conversations', 'messages', 'tasks');

-- Verify indexes
SELECT * FROM pg_indexes
WHERE tablename IN ('conversations', 'messages', 'tasks');

-- Test user isolation (query returns only user A's data)
SELECT * FROM messages WHERE conversation_id IN (
  SELECT id FROM conversations WHERE user_id = 'user_a_id'
);
```

---

### Phase 2: MCP Tool Layer

**Duration**: 2 weeks
**Team**: 1 backend engineer (tool specialist)
**Blocker**: Yes (agent depends on tools)
**Parallel**: Can run parallel to Phase 3

#### Objectives

- Initialize MCP server infrastructure
- Define 5 task tools with JSON schemas
- Implement tool handlers: add_task, list_tasks, complete_task, delete_task, update_task
- Create error handling and response formatting
- Validate tools via MCP protocol

#### Key Components

| Component | Description | Scope |
|-----------|-------------|-------|
| MCP Server | Official MCP SDK initialization | Transport layer (stdio/HTTP) |
| Tool Definitions | JSON schemas for each tool | Input/output contracts |
| Tool Handlers | Business logic for each operation | Database mutations via repositories |
| Error Handler | Converts app errors to JSON responses | StandardError, NotFoundError, ValidationError |
| Response Formatter | Structures all responses consistently | {result: {...}} or {error: ..., details: ...} |

#### Tool Specifications Summary

| Tool | Input | Output | Side Effect |
|------|-------|--------|-------------|
| add_task | user_id, title, description | task_id, title, status, created_at | INSERT tasks |
| list_tasks | user_id, status | [tasks array], total count | SELECT (read-only) |
| complete_task | user_id, task_id | updated_task | UPDATE tasks.completed=true |
| delete_task | user_id, task_id | deleted_task_id | DELETE tasks |
| update_task | user_id, task_id, title?, description? | updated_task | UPDATE tasks |

#### Dependencies

- Phase 1: Database models and repositories
- External: Official MCP SDK library

#### Architecture Decisions

**Decision**: Why MCP tools vs. direct REST endpoints?
- **Rationale**: MCP provides standard protocol for agent tool use; separates tool definition from agent logic; enables tool composition
- **Trade-off**: Additional protocol layer vs. direct HTTP
- **Benefit**: Future-proofs for other agents/frameworks

**Decision**: Why stateless tools?
- **Rationale**: Tools execute independently; don't share state between calls; enables parallelization
- **Trade-off**: Validation repeated per call vs. guaranteed correctness
- **Mitigation**: Minimal performance impact (<10ms per call)

**Decision**: Why JSON schemas for tools?
- **Rationale**: Agent understands tool contracts; validates inputs before calling; OpenAI agents SDK standard
- **Trade-off**: Schema duplication (source + OpenAI format) vs. type safety
- **Mitigation**: Generate schemas from Python types via schema_from_model()

#### Risks & Mitigation

| Risk | Probability | Impact | Mitigation |
|------|-----------|--------|-----------|
| Tool performance regression | Medium | Agent timeout (5s limit) | Implement query timeout <500ms; test with realistic data volume |
| Tool error propagation | Low | User confusion | Clear error messages; fallback responses |
| MCP protocol incompatibility | Low | Agent can't call tools | Use official SDK; follow spec strictly |

#### Definition of Done

- ✅ MCP server starts without errors
- ✅ All 5 tools registered and discoverable
- ✅ Tool JSON schemas validate against OpenAI Agents SDK format
- ✅ Each tool happy-path tested (valid input → correct output)
- ✅ Each tool error-path tested (invalid input → appropriate error)
- ✅ Tool execution time <1000ms (p99)
- ✅ User isolation enforced (tool_a can't access user_b's tasks)
- ✅ Response format consistent (all return {result: ...} or {error: ...})

#### Validation Strategy

```python
# Test tool discovery
tools = mcp_server.get_tools()
assert len(tools) == 5
assert {t['name'] for t in tools} == {'add_task', 'list_tasks', 'complete_task', 'delete_task', 'update_task'}

# Test tool execution
result = await tools['add_task'].execute(user_id='x', title='test')
assert 'task_id' in result
assert 'title' in result
assert 'status' in result

# Test error handling
result = await tools['add_task'].execute(user_id='x', title='')  # Empty title
assert result['error'] == 'ValidationError'
```

---

### Phase 3: AI Agent Configuration

**Duration**: 1-2 weeks
**Team**: 1 backend engineer (ML/agent specialist)
**Blocker**: Yes (chat endpoint depends on agent)
**Parallel**: Can run parallel to Phase 2

#### Objectives

- Configure OpenAI Agents SDK
- Register MCP tools with agent
- Define system prompt for task management domain
- Implement intent detection strategies
- Test agent tool invocation and chaining

#### Key Components

| Component | Description | Scope |
|-----------|-------------|-------|
| Agent Factory | OpenAI Agents SDK initialization | Model selection, tool registration, config |
| System Prompt | Domain instructions for agent | Task management behavior, error handling |
| Tool Registry | MCP tools exposed to agent | Tool definitions, schemas, execution paths |
| Tool Processor | Converts tool outputs to agent format | Format tool results for agent consumption |
| Error Handler | Agent-level error handling | Timeout fallbacks, parsing errors, retry logic |

#### System Prompt Strategy

The system prompt shapes agent behavior. Key sections:

```
1. ROLE: "You are a helpful task management assistant..."
2. CAPABILITIES: "You can create, read, update, delete tasks..."
3. INTENT DETECTION: "When users say 'create a task', use add_task..."
4. CLARIFICATION: "If ambiguous, ask which task they mean..."
5. ERROR HANDLING: "If task not found, suggest next steps..."
6. TONE: "Be conversational, concise, friendly..."
```

#### Intent Detection Strategy

| User Input | Detected Intent | Tool(s) | Parameters |
|-----------|-----------------|---------|-----------|
| "Add a task to review mockups" | create | add_task | title=review mockups |
| "Show my pending tasks" | read + filter | list_tasks | status=pending |
| "Mark the design review as done" | find + complete | list_tasks + complete_task | find task, then mark complete |
| "Delete old refactoring task" | find + delete | list_tasks + delete_task | find task, then delete |
| "Create a task and show all" | create + read | add_task + list_tasks | both operations |

**Implementation**: Intent detection is implicit in agent's understanding; agent reads system prompt and decides which tool to call based on user message.

#### Tool Chaining Strategy

Agent chains tools when necessary:
1. **User**: "Complete the Q2 planning task"
2. **Agent**: "I need to find the task first"
3. **Tool Call 1**: `list_tasks(user_id, status='all')` → finds "Q2 planning"
4. **Tool Call 2**: `complete_task(user_id, task_id=xyz)` → marks complete
5. **Response**: "Done! I've marked 'Q2 planning' as complete."

**Implementation**: OpenAI Agents SDK handles chaining automatically; agent sees tool outputs and decides on next steps.

#### Dependencies

- Phase 2: MCP tool definitions
- External: OpenAI Agents SDK, openai API key

#### Architecture Decisions

**Decision**: Use OpenAI Agents SDK vs. function calling directly?
- **Rationale**: Agents SDK handles tool routing, chaining, error recovery; abstracts agent loop
- **Trade-off**: Less control over reasoning process vs. simpler implementation
- **Benefit**: Future model swaps easier (SDK supports multiple models)

**Decision**: System prompt vs. fine-tuned model?
- **Rationale**: System prompt faster to iterate; no training data collection; sufficient for domain
- **Trade-off**: Less precise control vs. faster dev cycle
- **Mitigation**: Monitor agent accuracy; fine-tune if needed post-launch

**Decision**: Fixed system prompt vs. dynamic (per user/context)?
- **Rationale**: Fixed simpler; domain doesn't require personalization
- **Trade-off**: Can't customize behavior per user vs. simpler logic
- **Future**: Enable dynamic prompts later (e.g., user preferences)

#### Risks & Mitigation

| Risk | Probability | Impact | Mitigation |
|------|-----------|--------|-----------|
| Agent confusion on ambiguous input | High | Poor UX | Explicit clarification in system prompt |
| Tool hallucination (agent invents tools) | Low | API errors | Define tools exhaustively; test edge cases |
| Context window explosion | Low | Cost/latency | Limit history to 50 messages |
| Rate limiting (OpenAI API) | Medium | 429 errors | Implement exponential backoff; queue requests |

#### Definition of Done

- ✅ Agent initializes with OpenAI Agents SDK
- ✅ All 5 MCP tools registered with agent
- ✅ System prompt defined and documented
- ✅ Intent detection tested (>95% accuracy on test cases)
- ✅ Tool chaining works (multi-step operations succeed)
- ✅ Error handling tested (agent responds gracefully to errors)
- ✅ Agent latency <3 seconds (p99)
- ✅ Token usage tracked (understand cost per request)

#### Validation Strategy

```python
# Test agent initialization
agent = AgentFactory.create_agent(
    model='gpt-4-turbo',
    tools=mcp_tools,
    system_prompt=SYSTEM_PROMPT
)
assert agent is not None
assert len(agent.tools) == 5

# Test intent detection
response = await agent.run("Create a task to review designs")
assert 'add_task' in response.tool_calls[0]['name']

# Test tool chaining
response = await agent.run("Complete the Q2 planning task")
assert len(response.tool_calls) >= 2
assert response.tool_calls[0]['name'] == 'list_tasks'
assert response.tool_calls[1]['name'] == 'complete_task'

# Test error handling
response = await agent.run("Delete nonexistent task xyz")
assert 'Task not found' in response.text  # Agent explains error
```

---

### Phase 4: Stateless Chat Endpoint

**Duration**: 2 weeks
**Team**: 1 backend engineer (API/endpoint specialist)
**Blocker**: Yes (integrates all prior components)

#### Objectives

- Build `POST /api/{user_id}/chat` endpoint
- Implement stateless request handler
- Integrate conversation history loading
- Orchestrate agent invocation
- Persist messages after agent processing
- Return structured response

#### Key Components

| Component | Description | Flow |
|-----------|-------------|------|
| Chat Router | FastAPI route handler | Receives POST request |
| Request Validator | Validates JWT, conversation_id, message | JWT checked, params validated |
| History Loader | Fetches last 50 messages from DB | SELECT from messages table |
| Message Formatter | Builds OpenAI message array | [{role, content}, ...] |
| Agent Orchestrator | Invokes agent with messages | Passes to agent, gets response |
| Tool Executor | Executes agent's tool calls | MCP tools invoked |
| Response Persister | Saves user and assistant messages | INSERT into messages table |
| Response Builder | Constructs ChatResponse | Formats for frontend |

#### Stateless Request Cycle

```python
async def chat_endpoint(user_id: UUID, request: ChatRequest, token: str):
    # 1. VALIDATE (no state stored)
    user_id_from_token = jwt.decode(token)['sub']
    assert user_id == user_id_from_token  # Verify authorization

    # 2. LOAD (fresh read from DB each request)
    conversation = await db.get_conversation(request.conversation_id, user_id)
    messages = await db.get_messages(conversation.id, limit=50)

    # 3. APPEND (add new message to array)
    messages.append({role: 'user', content: request.message})

    # 4. PROCESS (fresh agent instance, stateless)
    agent = AgentFactory.create_agent(tools=[...])
    response = await agent.run(messages)

    # 5. PERSIST (write to DB)
    await db.save_message(conversation.id, 'user', request.message)
    await db.save_message(conversation.id, 'assistant', response.text, response.tool_calls)

    # 6. RETURN (no state retained in memory)
    return ChatResponse(
        conversation_id=conversation.id,
        response=response.text,
        tool_calls=response.tool_calls
    )
    # Function exits; local variables garbage collected; NO state lingering
```

**Why This Is Stateless**:
- No session objects stored
- No in-memory caches
- No class instance variables retained
- Each request loads fresh data from DB
- Each request creates fresh agent instance
- Result: Can run on any backend instance; restart-safe; scalable

#### Request/Response Contracts

```
Request: {
  conversation_id: UUID (optional),
  message: string (required, 1-2000 chars)
}

Response: {
  conversation_id: UUID,
  response: string,
  tool_calls: [
    {
      tool: string,
      input: object,
      result: object
    }
  ]
}

Errors: {
  400: {error: "ValidationError", details: "..."}
  401: {error: "Unauthorized"}
  403: {error: "AccessDenied"}
  500: {error: "InternalError"}
}
```

#### Dependencies

- Phase 1: Database models
- Phase 2: MCP tool layer
- Phase 3: Agent configuration
- External: FastAPI, Pydantic

#### Architecture Decisions

**Decision**: New conversation creation?
- **Rationale**: If conversation_id omitted, create new; enables fresh conversations without explicit endpoint
- **Trade-off**: Magic behavior vs. convenience
- **Mitigation**: Document clearly; frontend informed

**Decision**: Context window limit (50 messages)?
- **Rationale**: Prevents token explosion; ~2000 tokens/message → ~100K tokens limit keeps cost reasonable
- **Trade-off**: Very long conversations lose oldest context vs. cost control
- **Mitigation**: Archive old conversations; offer "clear history" option

**Decision**: Synchronous endpoint (request-response)?
- **Rationale**: Stateless simplicity; agent completes in <5s; matches client expectations
- **Trade-off**: No long-polling, no WebSocket support vs. simplicity
- **Future**: Async processing if agent latency increases

#### Risks & Mitigation

| Risk | Probability | Impact | Mitigation |
|------|-----------|--------|-----------|
| Agent timeout (>5s) | Medium | 504 Gateway Timeout | Set agent timeout <4s; use faster model |
| Database connection exhaustion | Low | 500 errors | Connection pooling; max_overflow settings |
| Token bloat (high token count) | Low | Cost explosion | Monitor tokens/request; alert if >10K |
| Race conditions (concurrent requests) | Low | Duplicate messages | Database ordering via created_at timestamp |

#### Definition of Done

- ✅ Endpoint accepts POST /api/{user_id}/chat requests
- ✅ JWT validated; unauthorized requests return 401
- ✅ Request validation (message required, <2000 chars)
- ✅ Conversation history loaded correctly (<200ms)
- ✅ Agent invoked with correct context
- ✅ Tool calls executed and results captured
- ✅ Messages persisted to database
- ✅ Response returned with all fields (conversation_id, response, tool_calls)
- ✅ Statelessness verified: no in-memory state retained; request isolated
- ✅ Endpoint latency <5s (p99)

#### Validation Strategy

```python
# Test happy path
response = await client.post(
    '/api/user-123/chat',
    headers={'Authorization': f'Bearer {token}'},
    json={'message': 'Create a task'}
)
assert response.status_code == 200
assert 'conversation_id' in response.json()
assert 'response' in response.json()

# Test statelessness: restart backend, same request succeeds
response1 = await client.post(..., json={'message': 'Show tasks'})
restart_backend()
response2 = await client.post(..., json={'message': 'Show tasks'})
assert response1.json() == response2.json()  # Identical result

# Test user isolation
response = await client.post(
    '/api/user-789/chat',
    headers={'Authorization': f'Bearer user123_token'},  # Wrong user
    json={'message': 'Create task'}
)
assert response.status_code == 403  # Access Denied
```

---

### Phase 5: Frontend Integration

**Duration**: 2 weeks
**Team**: 1 frontend engineer
**Blocker**: Medium (required for user-facing feature)
**Parallel**: Can run parallel to Phase 6 after Phase 4 complete

#### Objectives

- Integrate OpenAI ChatKit UI
- Connect to chat endpoint
- Manage conversation state
- Display agent responses
- Handle errors gracefully

#### Key Components

| Component | Description | Technology |
|-----------|-------------|-----------|
| ChatInterface | Main chat UI component | Next.js + React |
| MessageList | Renders conversation history | CSS Grid/Flex for layout |
| InputField | User message input | HTML textarea + button |
| ChatHook (useChat) | API communication | fetch + state management |
| ErrorBoundary | Error UI handling | React error boundary |
| LoadingState | Agent processing indicator | Spinner/skeleton UI |

#### Frontend Data Flow

```
User Types Message
    ↓
Input Submit Handler (useChat.ts)
    ↓
POST /api/{user_id}/chat
    {conversation_id?, message}
    ↓
Backend Processes (Phase 4)
    ↓
Response: {conversation_id, response, tool_calls}
    ↓
ChatInterface Updates
    - Add user message to message list
    - Add agent response to message list
    - Update conversation_id in state (if new)
    - Show tool calls (optional debug view)
    ↓
User Sees Response
```

#### Conversation State Management

```typescript
// useChat Hook
const [conversation, setConversation] = useState<Conversation | null>(null);
const [messages, setMessages] = useState<Message[]>([]);

// On first message
const handleSendMessage = async (message: string) => {
  const response = await fetch(`/api/${userId}/chat`, {
    method: 'POST',
    body: JSON.stringify({
      conversation_id: conversation?.id || null,  // null = create new
      message
    })
  });

  const data = await response.json();

  // Set conversation_id on first response (if new)
  if (!conversation) {
    setConversation({ id: data.conversation_id });
  }

  // Add messages to state
  setMessages(prev => [
    ...prev,
    { role: 'user', content: message },
    { role: 'assistant', content: data.response }
  ]);
};
```

#### ChatKit Configuration

```typescript
// config.ts
export const CHATKIT_CONFIG = {
  apiUrl: process.env.NEXT_PUBLIC_CHAT_API_URL,  // /api/{user_id}/chat
  domain: process.env.NEXT_PUBLIC_CHATKIT_DOMAIN,  // e.g., app.mydomain.com
  apiKey: process.env.NEXT_PUBLIC_CHATKIT_API_KEY,  // From OpenAI
  theme: 'light'
};
```

#### Dependencies

- Phase 4: Chat endpoint must be complete
- External: @openai-sdk/chatkit, Next.js 14

#### Architecture Decisions

**Decision**: ChatKit vs. custom chat UI?
- **Rationale**: ChatKit provides styled, accessible UI component; reduces dev time
- **Trade-off**: Less customization vs. faster iteration
- **Benefit**: Official OpenAI integration; maintained by OpenAI

**Decision**: Conversation_id in URL vs. state?
- **Rationale**: State (simpler) vs. URL (shareable, bookmarkable)
- **Decision**: State for MVP; URL routing in Phase 2
- **Benefit**: Users can't accidentally share conversations

**Decision**: Show tool_calls to users?
- **Rationale**: Transparency (users see what agent did) vs. clarity (tool info confusing)
- **Decision**: Optional debug panel; default hidden
- **Benefit**: Power users can verify agent behavior

#### Risks & Mitigation

| Risk | Probability | Impact | Mitigation |
|------|-----------|--------|-----------|
| Endpoint latency perceived | High | Poor UX | Loading spinner; set user expectations |
| Network errors (no internet) | Low | Silent failure | Error UI + user explanation |
| Token expiration mid-chat | Medium | 401 during chat | Refresh token automatically; re-authenticate |

#### Definition of Done

- ✅ ChatKit component renders without errors
- ✅ Messages post to /api/{user_id}/chat
- ✅ Responses display in message list
- ✅ Loading indicator shown during agent processing
- ✅ Errors displayed to user (human-readable messages)
- ✅ Conversation_id persisted across messages (same session)
- ✅ New conversation creation works (omit conversation_id)
- ✅ Tool calls displayed (optional debug view)

#### Validation Strategy

```typescript
// Test message submission
await userEvent.type(inputField, 'Create a task');
await userEvent.click(sendButton);
expect(mockFetch).toHaveBeenCalledWith(
  '/api/user-123/chat',
  expect.objectContaining({
    method: 'POST',
    body: expect.stringContaining('Create a task')
  })
);

// Test response rendering
const response = { conversation_id: 'c1', response: 'Done!' };
render(<ChatInterface />);
// ... simulate response ...
expect(screen.getByText('Done!')).toBeInTheDocument();

// Test error handling
mockFetch.mockRejectedValueOnce(new Error('Network error'));
// ... attempt message ...
expect(screen.getByText(/error|offline/i)).toBeInTheDocument();
```

---

### Phase 6: Security & Authentication

**Duration**: 1 week
**Team**: 1 backend engineer (security specialist)
**Blocker**: High (required before production)
**Parallel**: Can run parallel to Phase 5 after Phase 4 complete

#### Objectives

- Enforce JWT authentication
- Implement user isolation
- Sanitize user input
- Prevent tool authorization bypass
- Harden against common attacks

#### Key Components

| Component | Description | Scope |
|-----------|-------------|-------|
| Auth Middleware | JWT validation | Token signature, expiration, claims |
| Authorization Check | Conversation ownership | Verify user owns conversation before processing |
| Input Sanitization | XSS prevention | Escape user messages before storing/displaying |
| Tool Authorization | Tool access control | Ensure tool calls only for authenticated user |
| Rate Limiting | Abuse prevention | Limit requests per user/IP |
| Audit Logging | Compliance | Log all operations with user_id, timestamp |

#### Authentication Flow

```
Frontend Request
    ↓
Authorization: Bearer {jwt_token}
    ↓
Auth Middleware
    1. Extract token from header
    2. Verify signature (secret key)
    3. Check expiration (exp claim)
    4. Extract user_id (sub claim)
    ↓
Pass (token valid)
    ↓
Endpoint Handler receives user_id
    ↓
Check conversation ownership
    conversation = db.get_conversation(conv_id)
    if conversation.user_id != user_id:
        return 403 Forbidden
    ↓
Process request
```

#### User Isolation Strategy

| Layer | Enforcement |
|-------|-------------|
| Database Query | `WHERE user_id = :user_id` in all queries |
| Business Logic | Check user_id before DB operation |
| API Layer | 403 if requesting other user's data |

Example:
```python
# Endpoint
async def chat_endpoint(user_id: UUID, request: ChatRequest, token: str):
    # 1. Verify user matches token
    token_user_id = jwt.decode(token)['sub']
    if token_user_id != user_id:
        raise HTTPException(403, "Access Denied")

    # 2. Load conversation
    conversation = await db.get_conversation(request.conversation_id, user_id)
    if conversation is None:
        raise HTTPException(403, "Conversation not found")
    if conversation.user_id != user_id:
        raise HTTPException(403, "Access Denied")

    # 3. Tool calls auto-isolated (user_id passed to tools)
    result = await tool_add_task(user_id=user_id, ...)
```

#### Input Sanitization Strategy

| Input | Sanitization | Rationale |
|-------|--------------|-----------|
| User message | Escape HTML entities | Prevent XSS on display |
| Task title | Max 200 chars, escape | Prevent XSS + length bomb |
| Task description | Max 2000 chars, escape | Prevent XSS + data bloat |
| IDs (UUIDs) | Validate format | Prevent injection |

```python
from html import escape

def sanitize_user_message(message: str) -> str:
    # Limit length
    if len(message) > 2000:
        raise ValueError("Message too long")

    # Escape HTML entities
    safe_message = escape(message)

    # Remove null bytes
    safe_message = safe_message.replace('\x00', '')

    return safe_message
```

#### Tool Authorization

Each MCP tool validates user_id before execution:
```python
async def add_task(user_id: UUID, title: str, description: str):
    # 1. Validate user_id format (must be UUID)
    assert isinstance(user_id, UUID)

    # 2. Query always includes user_id filter
    existing = await db.count_tasks_for_user(user_id)

    # 3. Insert includes user_id
    task = await db.insert_task(user_id=user_id, title=title, ...)

    return task
```

#### Injection Prevention

**SQL Injection**: Prevented by SQLAlchemy ORM (parameterized queries)
```python
# ✅ Safe (parameterized)
result = await db.execute(
    select(Task).where(Task.user_id == user_id)
)

# ❌ Unsafe (string concatenation) - NEVER DO THIS
query = f"SELECT * FROM tasks WHERE user_id = '{user_id}'"
```

**LogSQL Injection**: No dynamic SQL in logs; use structured logging
```python
logger.info("User action", extra={
    'user_id': str(user_id),
    'action': 'add_task',
    'timestamp': datetime.now()
})
```

#### Rate Limiting Strategy

```python
from slowapi import Limiter
from slowapi.util import get_remote_address

limiter = Limiter(key_func=get_remote_address)

@app.post('/api/{user_id}/chat')
@limiter.limit("30/minute")  # 30 requests per minute per user
async def chat_endpoint(...):
    ...
```

#### Audit Logging

```python
logger.info("Chat request processed", extra={
    'user_id': str(user_id),
    'conversation_id': str(conversation.id),
    'tool_called': tool_name,
    'status': 'success',
    'duration_ms': elapsed_time
})
```

#### Dependencies

- Phase 4: Chat endpoint
- External: PyJWT, python-jose, slowapi

#### Architecture Decisions

**Decision**: JWT vs. session cookies?
- **Rationale**: JWT stateless; works with horizontal scaling; no server-side session state
- **Trade-off**: Token revocation harder vs. stateless benefit
- **Mitigation**: Token expiration time; token blacklist for logout

**Decision**: Rate limit by user vs. by IP?
- **Rationale**: By user (prevent one user overwhelming others) vs. by IP (prevent bot attacks)
- **Decision**: Both (user limit + IP limit)
- **Benefit**: Double protection

#### Risks & Mitigation

| Risk | Probability | Impact | Mitigation |
|------|-----------|--------|-----------|
| JWT token replayed | Low | Unauthorized access | Token expiration + signature verification |
| User ID forgery | Low | Access to other users' data | JWT signature validates token authenticity |
| XSS in frontend | Medium | JavaScript injection | Escape all user input; Content-Security-Policy headers |
| Rate limit bypass | Low | Spam/abuse | Monitor for anomalies; adjust limits |

#### Definition of Done

- ✅ JWT token required for all /api/chat requests
- ✅ Invalid/expired tokens return 401 Unauthorized
- ✅ User isolation verified: user_a cannot access user_b's conversations
- ✅ Tool authorization enforced: tools only callable by authenticated user
- ✅ User input sanitized (XSS, injection prevention)
- ✅ SQL injection prevented (parameterized queries)
- ✅ Rate limiting active (30 req/minute per user)
- ✅ Audit logs record all operations
- ✅ No secrets in logs (API keys, tokens, passwords)

#### Validation Strategy

```python
# Test JWT validation
response = await client.post('/api/user-123/chat', json={...})
assert response.status_code == 401  # No token

response = await client.post(
    '/api/user-123/chat',
    headers={'Authorization': 'Bearer invalid_token'},
    json={...}
)
assert response.status_code == 401  # Invalid token

# Test user isolation
user_a_token = create_jwt_token('user-a')
user_b_conversation = create_conversation('user-b')

response = await client.post(
    '/api/user-a/chat',
    headers={'Authorization': f'Bearer {user_a_token}'},
    json={'conversation_id': str(user_b_conversation.id), 'message': 'hack'}
)
assert response.status_code == 403  # Access Denied

# Test input sanitization
response = await client.post(
    '/api/user-123/chat',
    headers={'Authorization': f'Bearer {token}'},
    json={'message': '<script>alert("xss")</script>'}
)
# Message stored safely; frontend escapes on display
```

---

### Phase 7: Testing & Validation

**Duration**: 1 week
**Team**: 1 QA engineer + backend engineers
**Blocker**: High (required before deployment)

#### Objectives

- Unit test all MCP tools
- Integration test chat endpoint
- Verify stateless architecture
- Verify user isolation
- Load test endpoint

#### Test Categories

| Category | Scope | Count | Duration |
|----------|-------|-------|----------|
| Unit Tests | Individual functions | 20 | 2 days |
| Integration Tests | Endpoint → DB | 10 | 2 days |
| Stateless Tests | Restart resilience | 5 | 1 day |
| User Isolation Tests | Authorization | 8 | 1 day |
| Load Tests | 100 concurrent users | 3 | 1 day |

#### Unit Tests (MCP Tools)

Each tool tested in isolation:

```python
# test_add_task.py
async def test_add_task_success():
    result = await add_task(
        user_id=UUID('123e4567-e89b-12d3-a456-426614174000'),
        title='Test task',
        description='Test description'
    )
    assert result['task_id'] is not None
    assert result['title'] == 'Test task'

async def test_add_task_title_too_long():
    with pytest.raises(ValidationError):
        await add_task(
            user_id=UUID('123e4567-e89b-12d3-a456-426614174000'),
            title='x' * 201,  # > 200 chars
            description=''
        )

async def test_list_tasks_user_isolation():
    user_a_id = UUID('aaa...')
    user_b_id = UUID('bbb...')

    # Create tasks for both users
    await add_task(user_a_id, 'Task A', '')
    await add_task(user_b_id, 'Task B', '')

    # List for user A
    tasks = await list_tasks(user_a_id, status='all')
    assert len(tasks) == 1
    assert tasks[0]['title'] == 'Task A'  # Only user A's task
```

#### Integration Tests (Chat Endpoint)

```python
# test_chat_endpoint.py
async def test_chat_endpoint_full_flow():
    # 1. Send message
    response = await client.post(
        '/api/user-123/chat',
        headers={'Authorization': f'Bearer {token}'},
        json={'message': 'Create a task to test'}
    )

    # 2. Verify response
    assert response.status_code == 200
    data = response.json()
    assert 'conversation_id' in data
    assert 'response' in data
    assert 'tool_calls' in data

    # 3. Verify tool was called
    tool_calls = data['tool_calls']
    assert len(tool_calls) > 0
    assert tool_calls[0]['tool'] == 'add_task'

    # 4. Verify task created in DB
    tasks = await db.get_tasks_for_user('user-123')
    assert len(tasks) > 0
    assert tasks[0]['title'] == 'test'
```

#### Stateless Tests

```python
# test_stateless.py
async def test_same_request_on_different_instances():
    """Verify two backend restarts produce identical results"""

    # Request 1 on instance A
    instance_a = start_backend('instance-a')
    response1 = await instance_a.post('/api/user-123/chat', json={...})
    stop_backend(instance_a)

    # Request 2 on instance B
    instance_b = start_backend('instance-b')
    response2 = await instance_b.post('/api/user-123/chat', json={...})
    stop_backend(instance_b)

    # Verify identical
    assert response1.json() == response2.json()

async def test_no_in_memory_state_leaked():
    """Verify local variables don't persist between requests"""

    # Request A sets something
    response_a = await client.post(..., json={'message': 'Create task A'})

    # Request B from different user
    response_b = await client.post(..., json={'message': 'Create task B'})

    # Verify B doesn't see A's state
    assert 'task A' not in response_b.json()['response']
```

#### Load Test

```python
# test_load.py
async def test_100_concurrent_users():
    """Load test with 100 concurrent users"""

    async def user_workflow(user_id):
        for i in range(5):  # 5 requests per user
            response = await client.post(
                f'/api/{user_id}/chat',
                headers={'Authorization': f'Bearer {get_token(user_id)}'},
                json={'message': f'Task {i}'}
            )
            assert response.status_code == 200

    # Run 100 users in parallel
    tasks = [user_workflow(f'user-{i}') for i in range(100)]
    await asyncio.gather(*tasks)

    # Verify metrics
    assert avg_response_time < 5000  # ms
    assert error_rate < 0.01  # 1%
    assert db_connections < 200  # Connection pool not exhausted
```

#### Acceptance Criteria

- ✅ 100% of unit tests pass
- ✅ 90% of integration tests pass (allow 10% flakiness due to timing)
- ✅ Statelessness verified (same request → same result)
- ✅ User isolation verified (cross-user access blocked)
- ✅ Load test passes (100 concurrent users, <5s response time)
- ✅ No data corruption under load
- ✅ Coverage >80% for critical paths

---

### Phase 8: Deployment

**Duration**: 1 week
**Team**: 1 DevOps engineer + all engineers (support)

#### Objectives

- Configure production environment
- Setup monitoring and logging
- Domain allowlist ChatKit
- Create runbooks for common issues
- Deploy to staging + production

#### Deployment Checklist

**Pre-Deployment**:
- [ ] All tests pass
- [ ] Code reviewed
- [ ] Security audit complete
- [ ] Performance baselines established

**Environment Setup**:
- [ ] Production .env configured
  - OPENAI_API_KEY
  - DATABASE_URL (Neon production)
  - OPENAI_MODEL
  - JWT_SECRET
  - Other configs
- [ ] Database migrations applied to production
- [ ] Health endpoint verified
- [ ] Logging configured (JSON output)

**OpenAI ChatKit**:
- [ ] Frontend domain registered with OpenAI
- [ ] Domain allowlist applied
- [ ] test.com (staging) and app.com (production)

**Monitoring**:
- [ ] Metrics collection active
  - Request latency (p50, p99)
  - Error rate
  - Database query times
  - Agent processing time
- [ ] Alerting configured
  - Latency >5s
  - Error rate >1%
  - Database unavailable
- [ ] Logs aggregated
  - CloudWatch, DataDog, or equivalent
  - JSON format for parsing

**Deployment Steps**:
1. Deploy to staging environment
2. Smoke test: create task, list tasks, complete task
3. Load test: 50 concurrent users
4. Verify no errors in logs
5. Deploy to production
6. Monitor for 24 hours
7. Roll back if issues detected

#### Scaling Configuration

```python
# Connection pooling
DATABASE_POOL_SIZE = 20
DATABASE_MAX_OVERFLOW = 10
# Allows up to 30 simultaneous connections

# API server
WORKERS = 4  # Uvicorn workers
THREADS_PER_WORKER = 2

# Agent timeout
AGENT_TIMEOUT_SECONDS = 4

# Request timeout
REQUEST_TIMEOUT_SECONDS = 30
```

#### Health Check

```python
# GET /health
{
  "status": "healthy",
  "components": {
    "database": "connected",
    "openai_api": "available"
  },
  "timestamp": "2026-02-08T10:30:45Z"
}
```

#### Runbooks

**Issue**: Agent timeout
- [ ] Check OpenAI API status
- [ ] Reduce context window size
- [ ] Switch to faster model

**Issue**: Database slow
- [ ] Check connection pool exhaustion
- [ ] Verify indexes present
- [ ] Check slow query logs

**Issue**: High error rate
- [ ] Check OpenAI API rate limits
- [ ] Verify JWT secret correct
- [ ] Check database connectivity

#### Definition of Done

- ✅ All environments configured
- ✅ Health check passing
- ✅ Monitoring active and alerting working
- ✅ ChatKit domain allowlisted
- ✅ Logs structured and aggregated
- ✅ Runbooks documented
- ✅ Deployment successful
- ✅ 24-hour production monitoring complete (no critical issues)

---

## Stateless Architecture Deep Dive

### The Stateless Guarantee

**Definition**: No data is held in application memory between requests.

**What This Means**:

```python
# ❌ WRONG: Stateful (in-memory storage)
class ChatHandler:
    conversations = {}  # Class variable = shared state

    def handle_request(self, user_id, message):
        # This violates stateless requirement
        if user_id not in self.conversations:
            self.conversations[user_id] = []
        self.conversations[user_id].append(message)

# ✅ CORRECT: Stateless (DB-backed)
async def handle_request(user_id: UUID, message: str):
    # 1. Load from DB
    conversation = await db.get_conversation(user_id)

    # 2. Process
    response = await agent.process(conversation.messages)

    # 3. Save to DB
    await db.save_message(conversation.id, message)
    await db.save_message(conversation.id, response)

    # 4. Return
    return response
    # Variables go out of scope; garbage collected; no lingering state
```

### Why Stateless?

| Benefit | Explanation |
|---------|-------------|
| **Scalability** | No session affinity; load balancer distributes requests freely |
| **Resilience** | Server crash doesn't lose user data; they can reconnect anywhere |
| **Simplicity** | No distributed caching; no session replication; no state sync issues |
| **Cost** | Can shut down idle servers; no need to maintain warm sessions |
| **Testing** | Easier to test; no hidden state to mock |

### Conversation State Lifecycle

```
Request 1: User sends "Create a task"
    ↓
[Load] conversation_id=null → create new conversation → conv_id=ABC123
[Process] agent creates task → tool call add_task
[Save] message(user): "Create a task"
[Save] message(assistant): "Done!"
[Return] {conversation_id: ABC123, response: "Done!", tool_calls: [...]}
    ↓
Frontend stores conversation_id=ABC123 in state

Request 2: User sends "Show tasks" (same conversation)
    ↓
[Load] conversation_id=ABC123 → fetch last 50 messages
[Process] agent lists tasks → tool call list_tasks
[Save] message(user): "Show tasks"
[Save] message(assistant): "You have 1 task: ..."
[Return] {conversation_id: ABC123, response: "You have...", tool_calls: [...]}
    ↓
State unchanged; same conversation continues

Request 3 (Server restarts between Request 2 and 3)
    ↓
[Load] conversation_id=ABC123 → fetch last 50 messages (includes all prior messages)
[Process] agent has full context → responds as if server never restarted
[Save] persist new messages
[Return] response
    ↓
User unaffected by restart; conversation seamless
```

### Distributed Context Diagram

```
Load Balancer
    ├→ [Backend 1] Request A (user-1, conv-abc)
    │   ├ Load from DB
    │   ├ Process agent
    │   └ Save to DB
    │   (state → garbage collected)
    │
    ├→ [Backend 2] Request B (user-1, conv-abc)
    │   ├ Load from DB (gets Request A's changes!)
    │   ├ Process agent
    │   └ Save to DB
    │   (state → garbage collected)
    │
    └→ [Backend 3] Request C (user-2, conv-xyz)
        ├ Load from DB
        ├ Process agent
        └ Save to DB
        (state → garbage collected)

Result: Seamless multi-server operation; no state sync needed
```

### Transaction Safety

PostgreSQL transactions ensure consistency:

```sql
BEGIN TRANSACTION

-- Read-only
SELECT * FROM conversations WHERE id = conv_id AND user_id = user_id;
SELECT * FROM messages WHERE conversation_id = conv_id ORDER BY created_at;

-- Write
INSERT INTO messages (conversation_id, user_id, role, content)
VALUES (conv_id, user_id, 'user', message_text);

INSERT INTO messages (conversation_id, user_id, role, content, tool_calls)
VALUES (conv_id, user_id, 'assistant', response_text, tool_calls_json);

COMMIT TRANSACTION
```

**Guarantee**: All-or-nothing; either both user and assistant messages saved, or neither.

---

## Tool Invocation & Agent Strategy

### Intent Detection Flow

```
User: "Create a task to review designs by Friday"
    ↓
Agent reads message + conversation history + system prompt
    ↓
Agent reasons:
  - "User wants to CREATE a task"
  - "Task title should be: 'review designs by Friday'"
  - "No description provided"
  - "Tool to call: add_task"
    ↓
Agent invokes tool:
  add_task(user_id=..., title="review designs by Friday", description="")
    ↓
Tool executes:
  - Validate params
  - Insert row in tasks table
  - Return: {task_id: "xyz", title: "...", status: "pending"}
    ↓
Agent processes tool output:
  - Sees successful result
  - Generates response: "I've created 'review designs by Friday'. You now have 3 pending tasks."
    ↓
Response returned to user
```

### Tool Chaining Example

```
User: "Complete the Q2 planning task"
    ↓
Agent reasons:
  - "User wants to COMPLETE a task"
  - "Task name: 'Q2 planning'"
  - "Problem: I don't know the task_id; need to find it first"
    ↓
Agent decides to chain tools:
  1. list_tasks(user_id=..., status='all') → find task matching "Q2 planning"
  2. complete_task(user_id=..., task_id=<result from step 1>)
    ↓
Tool 1 executes:
  SELECT * FROM tasks WHERE user_id=... AND completed=false
  → Returns: [{id: 'abc123', title: 'Q2 planning', ...}]
    ↓
Agent processes Tool 1 result:
  - Found matching task with id='abc123'
  - Proceeds to Tool 2
    ↓
Tool 2 executes:
  UPDATE tasks SET completed=true WHERE id='abc123'
  → Returns: {id: 'abc123', title: 'Q2 planning', completed: true, ...}
    ↓
Agent generates response:
  "Done! I've marked 'Q2 planning' as complete. You now have 2 pending tasks."
    ↓
Response with tool_calls showing both operations
```

### Error Handling in Agent

```
User: "Mark the nonexistent task as done"
    ↓
Agent chains:
  1. list_tasks(user_id=..., status='all')
  2. If matching task found → complete_task
     If NOT found → clarify with user
    ↓
Tool 1 executes:
  SELECT * FROM tasks WHERE user_id=...
  → Returns: [] (empty; no matches)
    ↓
Agent sees empty result:
  - Can't find task
  - Doesn't attempt Tool 2
  - Generates clarification response
    ↓
Agent response:
  "I couldn't find a task matching that description. Did you mean:
   1. Q2 planning
   2. Code review
   Or would you like to create a new task?"
    ↓
User clarifies → new request → cycle repeats
```

---

## Data Flow Analysis

### Scenario 1: Adding a Task

**User Action**: Types "Add a task to review design mockups"

**Data Flow**:

```
1. FRONTEND
   User types message → Submit
   POST /api/user123/chat
   {
     "conversation_id": "conv456",
     "message": "Add a task to review design mockups"
   }

2. BACKEND: VALIDATE (Auth Middleware)
   JWT token extracted from Authorization header
   Signature verified ← JWT_SECRET
   user_id extracted from token: user123
   Passed to endpoint

3. BACKEND: LOAD (History Loading)
   Query: SELECT * FROM conversations WHERE id=conv456 AND user_id=user123
   Result: conversation object
   Query: SELECT * FROM messages WHERE conversation_id=conv456 ORDER BY created_at
   Result: [message1, message2, ...message50]

4. BACKEND: APPEND
   messages array + {role: 'user', content: 'Add a task to review design mockups'}
   = [message1, ..., message50, new_user_message]

5. BACKEND: AGENT PROCESSING
   Input to OpenAI Agents SDK:
   {
     "messages": [{role: 'assistant', content: '...'}, {role: 'user', content: 'Add a task...'}],
     "tools": [add_task, list_tasks, complete_task, delete_task, update_task],
     "system_prompt": "You are a task management assistant..."
   }

   Agent reasoning:
   - Detects intent: CREATE task
   - Selects tool: add_task
   - Extracts parameters:
     * user_id: user123
     * title: "review design mockups"
     * description: "" (optional, not provided)

6. BACKEND: TOOL EXECUTION (MCP Server)
   Tool: add_task
   Input: {user_id: 'user123', title: 'review design mockups', description: ''}
   Execution:
     INSERT INTO tasks (id, user_id, title, description, completed, created_at, updated_at)
     VALUES (gen_random_uuid(), 'user123', 'review design mockups', '', false, now(), now())
   Result: {
     task_id: 'task789',
     user_id: 'user123',
     title: 'review design mockups',
     status: 'pending',
     created_at: '2026-02-08T10:30:45Z'
   }

7. BACKEND: AGENT RESPONSE GENERATION
   Agent receives tool_calls result [from #6]
   Agent generates natural language response:
     "I've created a task 'review design mockups'. You now have 3 pending tasks."

8. BACKEND: PERSISTENCE
   Table: messages
   Row 1: INSERT INTO messages (conversation_id, user_id, role, content, created_at)
          VALUES ('conv456', 'user123', 'user', 'Add a task to review design mockups', now())
   Row 2: INSERT INTO messages (conversation_id, user_id, role, content, tool_calls, created_at)
          VALUES ('conv456', 'user123', 'assistant', 'I\'ve created a task...', [tool_calls json], now())

9. BACKEND: RESPONSE ASSEMBLY
   {
     "conversation_id": "conv456",
     "response": "I've created a task 'review design mockups'. You now have 3 pending tasks.",
     "tool_calls": [
       {
         "tool": "add_task",
         "input": {user_id: 'user123', title: 'review design mockups', description: ''},
         "result": {task_id: 'task789', title: 'review design mockups', ...}
       }
     ]
   }

10. FRONTEND: RENDER
    ChatInterface receives response
    Adds messages to state:
      - User message: "Add a task to review design mockups"
      - Assistant message: "I've created a task 'review design mockups'..."
    Renders messages in MessageList
    Shows tool_calls in optional debug view

11. USER SEES
    Message list updated
    Task created (if user navigates to task list)
    Conversation continues
```

**Database State After**:
```sql
-- New row in messages table
id: message_uuid_1
conversation_id: conv456
user_id: user123
role: user
content: Add a task to review design mockups
created_at: 2026-02-08T10:30:45Z

id: message_uuid_2
conversation_id: conv456
user_id: user123
role: assistant
content: I've created a task 'review design mockups'...
tool_calls: [{"tool": "add_task", "input": {...}, "result": {...}}]
created_at: 2026-02-08T10:30:46Z

-- New row in tasks table
id: task789
user_id: user123
title: review design mockups
description: (null)
completed: false
created_at: 2026-02-08T10:30:45Z
updated_at: 2026-02-08T10:30:45Z
```

### Scenario 2: Completing a Task

**User Action**: Types "Mark the design review as done"

**Data Flow** (abbreviated):

```
1. POST /api/user123/chat {"conversation_id":"conv456","message":"Mark the design review as done"}
2. Validate JWT → user_id = user123
3. Load conversation history (last 50 messages from conv456)
4. Agent processes message
   - Detects intent: COMPLETE task
   - Needs task_id; calls list_tasks first
5. Tool call 1: list_tasks(user_id='user123', status='all')
   - Query: SELECT * FROM tasks WHERE user_id='user123'
   - Result: [{id: 'task789', title: 'review design mockups', ...}, {id: 'task790', title: 'design review', ...}]
6. Agent sees multiple matches, asks for clarification OR picks best match "design review"
7. Tool call 2: complete_task(user_id='user123', task_id='task790')
   - Query: UPDATE tasks SET completed=true WHERE id='task790' AND user_id='user123'
   - Result: {id: 'task790', title: 'design review', completed: true, ...}
8. Agent response: "Done! I've marked 'design review' as complete. You now have 2 pending tasks."
9. Persist both user and assistant messages to messages table
10. Return response to frontend
11. Frontend renders conversation update
```

### Scenario 3: Listing Tasks

**User Action**: Types "Show my pending tasks"

**Data Flow**:

```
1. POST /api/user123/chat {"conversation_id":"conv456","message":"Show my pending tasks"}
2. Validate JWT → user_id = user123
3. Load conversation history
4. Agent processes message
   - Detects intent: LIST tasks with FILTER (pending)
   - Calls list_tasks(user_id='user123', status='pending')
5. Tool call: list_tasks
   - Query: SELECT * FROM tasks WHERE user_id='user123' AND completed=false
   - Result: [{id: 'task789', title: 'review design mockups', ...}]
6. Agent formats response: "You have 1 pending task: 1. Review design mockups"
7. Persist messages
8. Return response
9. Frontend renders task list in chat message
```

---

## Scalability & Performance

### Load Balancing Strategy

```
┌─────────────────────┐
│  External LB (AWS)  │
│  (Round-robin)      │
└──────────┬──────────┘
           ├─────┬─────┬─────┐
           ▼     ▼     ▼     ▼
      Pod 1 Pod 2 Pod 3 Pod 4
      :8002 :8002 :8002 :8002

Each pod: independent, stateless
Result: Scale from 1 to N pods without code changes
```

**Scaling Trigger**:
```
CPU > 70% for 5 minutes → Provision new pod
CPU < 20% for 10 minutes → Remove pod
```

### Database Connection Pooling

```python
DATABASE_POOL_SIZE = 20  # Min connections
DATABASE_MAX_OVERFLOW = 10  # Max additional
# Total: 30 connections max per pod

With 4 pods: 4 * 30 = 120 total connections
Neon supports 1000+ connections → No bottleneck
```

### Latency Targets

| Operation | Target | Path |
|-----------|--------|------|
| JWT validation | <10ms | In-process |
| Load conversation history | <200ms | SELECT 50 messages |
| Agent processing | <3000ms | OpenAI API + tool invocation |
| Tool execution | <500ms | Database query |
| Message persistence | <100ms | INSERT into messages table |
| **Total p99** | **<5000ms** | All operations |

### Indexing Strategy

```sql
-- Conversations table
CREATE INDEX idx_conversations_user_id ON conversations(user_id);
CREATE INDEX idx_conversations_user_created ON conversations(user_id, created_at DESC);

-- Messages table (critical for history loading)
CREATE INDEX idx_messages_conversation_id ON messages(conversation_id);
CREATE INDEX idx_messages_conversation_created ON messages(conversation_id, created_at ASC);

-- Tasks table
CREATE INDEX idx_tasks_user_id ON tasks(user_id);
CREATE INDEX idx_tasks_user_completed ON tasks(user_id, completed);  -- For list_tasks filtering
```

**Query Optimization**:
```sql
-- Fast (uses index)
SELECT * FROM messages
WHERE conversation_id = ?
ORDER BY created_at ASC
LIMIT 50;
-- Index: idx_messages_conversation_created
-- Expected: <50ms

-- Slow (no index)
SELECT * FROM messages
WHERE content LIKE '%keyword%'
-- Expected: >5000ms on 1M rows
-- Solution: Add full-text search index if needed
```

### Monitoring Metrics

```
Request Latency: p50, p95, p99
  Target: p99 < 5000ms

Error Rate:
  Target: < 0.5%

Agent Processing Time:
  Monitor: Time spent in OpenAI API
  Alert if: > 4000ms (indicates API slowness)

Tool Execution Time:
  Monitor: Time spent in DB queries
  Alert if: > 1000ms (indicates DB slowness)

Database Connections:
  Monitor: Active connections
  Alert if: > 100 (pool exhaustion imminent)

Token Usage:
  Monitor: Tokens per request
  Alert if: > 10000 (cost spike)
```

---

## Security Strategy

### Threat Model

| Threat | Mitigation | verification |
|--------|-----------|--------------|
| **Unauthorized Access** | JWT token + signature verification | Test: Invalid token → 401 |
| **User Isolation Breach** | All queries filtered by user_id | Test: UserA accessing UserB data → 403 |
| **SQL Injection** | SQLAlchemy ORM parameterized queries | Test: Malicious input in message → escaped |
| **XSS Attack** | HTML entity escaping in frontend | Test: `<script>alert()</script>` → rendered as text |
| **CSRF** | Not applicable (stateless, token-based) | N/A |
| **Token Replay** | Token expiration + signature validation | Test: Expired token → 401 |
| **Rate Limit Bypass** | IP + user-based throttling | Test: 31 reqs in 60s → 429 |
| **Tool Authorization Bypass** | Each tool validates user_id | Test: Tool called for different user → error |

### API Security Headers

```python
@app.middleware("http")
async def add_security_headers(request: Request, call_next):
    response = await call_next(request)
    response.headers["X-Content-Type-Options"] = "nosniff"
    response.headers["X-Frame-Options"] = "DENY"
    response.headers["X-XSS-Protection"] = "1; mode=block"
    response.headers["Strict-Transport-Security"] = "max-age=31536000; includeSubDomains"
    return response
```

### Data Protection

| Data | Protection |
|------|-----------|
| API Keys (OpenAI, secrets) | Environment variables (never in code/logs) |
| Passwords (user auth) | Better Auth handles (Phase II) |
| JWT tokens | Signed with SECRET; not logged |
| User messages | Stored in DB; encrypted at rest (Neon) |
| Conversation history | User-specific queries; no cross-access |

### Compliance

- **Logging**: No sensitive data logged (API keys, tokens); user_id anonymized if possible
- **Retention**: Conversations retained indefinitely (or per user policy)
- **GDPR**: User can request deletion (future: implement account deletion endpoint)
- **Audit Trail**: All operations logged with timestamp + user_id

---

## Risk Assessment & Mitigation

### Technical Risks

| Risk | Probability | Impact | Mitigation | Monitoring |
|------|-----------|--------|-----------|------------|
| **Agent timeout** | Medium | User sees "timeout" error | Agent timeout <4s; model switch if needed | Agent latency metrics |
| **OpenAI API failure** | Low | Chat unavailable | Fallback response; status page | API health checks |
| **DB connection exhaustion** | Low | 500 errors | Connection pooling; max_overflow | Connection count alerts |
| **Token bloat** | Medium | High cost | Limit context to 50 messages; monitor tokens | Token usage metrics |
| **Malicious input** | Medium | Data corruption / XSS | Input validation + HTML escaping | Security testing |
| **Concurrent race condition** | Low | Duplicate messages | DB transaction ordering | Test concurrency |

### Operational Risks

| Risk | Probability | Impact | Mitigation | Monitoring |
|------|-----------|--------|-----------|------------|
| **Deployment failure** | Low | Service down | Blue-green deployment; rollback plan | Canary deploys |
| **Data corruption** | Low | Data loss | Database backups; point-in-time restore | Backup verification |
| **Scaling misconfiguration** | Low | Too few/many pods | Gradual scaling; resource monitoring | Pod status |
| **Key rotation** | Low | Authentication failure | Planned key rotation; zero-downtime swap | Rotation testing |

### Mitigation Strategies

1. **Testing**: 80%+ code coverage; integration tests; load tests
2. **Monitoring**: Real-time alerts on latency, errors, API availability
3. **Redundancy**: Multiple backend pods; database replication (Neon)
4. **Documentation**: Runbooks for common issues; playbooks for escalation
5. **Gradual Rollout**: Canary deployment to 10% of traffic first

---

## Success Metrics & Validation

### Phase Success Criteria

| Phase | Criteria | Validation Method |
|-------|----------|------------------|
| 1 | Schema created; migrations applied | SQL queries verify tables/indexes exist |
| 2 | Tools discoverable; JSON schemas valid | MCP protocol validation |
| 3 | Agent initializes; tools registered | Agent test suite (intent detection) |
| 4 | Endpoint responds; statelessness verified | Load test + restart test |
| 5 | UI renders; messages post to endpoint | E2E tests |
| 6 | JWT validated; user isolation enforced | Authorization tests |
| 7 | 90% tests pass | Test coverage report |
| 8 | Production live; health checks pass | Monitoring dashboard |

### Launch Readiness Checklist

- [ ] **P1 Features**: Create, list, complete tasks via chat ✅
- [ ] **Security**: JWT validated; user isolation enforced ✅
- [ ] **Performance**: p99 latency <5s ✅
- [ ] **Reliability**: 99.5% uptime SLA ✅
- [ ] **Scalability**: Horizontal scaling verified ✅
- [ ] **Testing**: >80% coverage; integration tests pass ✅
- [ ] **Documentation**: Runbooks, deployment guide ✅
- [ ] **Monitoring**: Alerts configured ✅
- [ ] **Compliance**: Logging, audit trail in place ✅

### Post-Launch Metrics (First 30 Days)

- Feature adoption: 10%+ of daily users try chat
- Conversation rate: >50% of chat users complete a task through chat
- User satisfaction: 4+ star rating
- System health: 99.5% uptime; <0.5% error rate
- Cost: Monitor OpenAI token usage; alert if >$X/day

---

## Timeline & Resource Allocation

### 8-Week Schedule

```
Week 1: Phase 1 (Database Foundation)
  - 1 backend engineer
  - Outputs: Schema, migrations, repos ready

Week 2-3: Phases 2-4 (Foundation Architecture)
  - Phase 2 (MCP tools): 1 engineer
  - Phase 3 (Agent config): 1 engineer [parallel]
  - Outputs: Tools registered, agent initialized

Week 4: Phase 4 (Chat Endpoint)
  - 1 backend engineer
  - Depends on: Phases 2, 3 complete
  - Output: /api/chat endpoint working

Week 5-6: Phases 5-6 (Frontend + Security)
  - Phase 5 (Frontend): 1 frontend engineer
  - Phase 6 (Security): 1 backend engineer [parallel]
  - Outputs: ChatKit UI, auth enforced

Week 7: Phase 7 (Testing & Validation)
  - 1 QA engineer + all engineers
  - Outputs: 90% tests pass, coverage >80%

Week 8: Phase 8 (Deployment)
  - 1 DevOps + all engineers
  - Outputs: Production live, monitoring active
```

### Resource Allocation

```
Backend Engineers: 3 (PLC, Tools, Agent)
Frontend Engineers: 1 (ChatKit)
QA/Testing: 1
DevOps: 1 (part-time until Week 8)
Total: 5-6 FTE for 8 weeks
```

### Critical Path

→ → → → → → → →
Phase 1 → Phase 2 → Phase 3 → Phase 4 → Phase 5 → Phase 6 → Phase 7 → Phase 8

Minimum 8 weeks sequential; parallelization saves 1-2 weeks with proper team allocation.

---

## Next Steps

1. **Approval**: Review and approve this plan
2. **Setup**: Create project structure; assign team members
3. **Begin Phase 1**: Database schema design and migration
4. **Weekly Syncs**: Monitor progress; adjust as needed
5. **Phase Reviews**: Validate each phase before proceeding

---

## Document Metadata

| Field | Value |
|-------|-------|
| Plan Version | 1.0 |
| Created | February 8, 2026 |
| Status | Ready for Execution |
| Next Phase | Begin Implementation |
| Architecture | Stateless, Horizontally Scalable |
| Estimated Timeline | 8 weeks, 5-6 FTE |

