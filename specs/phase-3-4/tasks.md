# Phase III: Todo AI Chatbot - Implementation Tasks

**Version**: 1.1
**Created**: February 8, 2026
**Last Updated**: February 8, 2026
**Feature**: Phase III - Todo AI Chatbot with MCP Architecture
**Total Tasks**: 65
**Completed Tasks**: 23 (T001-T023) ✓
**Status**: In Progress - Phase 4 Complete, Phase 5 Ready

---

## Table of Contents

1. [Overview](#overview)
2. [Phase Structure & Dependencies](#phase-structure--dependencies)
3. [Phase 1: Project Setup](#phase-1-project-setup)
4. [Phase 2: Foundation - Database & Models](#phase-2-foundation--database--models)
5. [Phase 3: Foundation - MCP Server Infrastructure](#phase-3-foundation--mcp-server-infrastructure)
6. [Phase 4: Foundation - AI Agent Configuration](#phase-4-foundation--ai-agent-configuration)
7. [Phase 5: Core User Story - Chat Endpoint](#phase-5-core-user-story--chat-endpoint)
8. [Phase 6: Core Feature - Conversation Persistence](#phase-6-core-feature--conversation-persistence)
9. [Phase 7: Core Feature - MCP Tools Implementation](#phase-7-core-feature--mcp-tools-implementation)
10. [Phase 8: Security & Authentication](#phase-8-security--authentication)
11. [Phase 9: Frontend Integration](#phase-9-frontend-integration)
12. [Phase 10: Testing & Validation](#phase-10-testing--validation)
13. [Phase 11: Deployment & Monitoring](#phase-11-deployment--monitoring)
14. [Task Dependency Graph](#task-dependency-graph)
15. [Parallel Execution Strategy](#parallel-execution-strategy)
16. [MVP Scope](#mvp-scope)

---

## Overview

This tasks document breaks down the Phase III: Todo AI Chatbot specification into 65 atomic, testable implementation tasks across 11 phases. The architecture follows a stateless design pattern enabling horizontal scaling.

**Key Principles**:
- ✅ Stateless: No in-memory session state; all state persists in PostgreSQL
- ✅ Modular: Each phase produces independently testable artifacts
- ✅ Sequential with parallelization: Critical path identified; non-blocking tasks run in parallel
- ✅ Implementation-ready: Each task specifies exact files, inputs, outputs, and acceptance criteria

---

## Phase Structure & Dependencies

```
SETUP (Phase 1)
    ↓
FOUNDATIONAL (Phases 2-4)
    ├→ DB Models & Schema (Phase 2)
    ├→ MCP Server Foundation (Phase 3)
    └→ Agent Configuration (Phase 4)
    ↓
CORE FEATURES (Phases 5-7) - PROPERLY ORDERED
    ├→ Conversation Persistence (Phase 5) [depends on 2]
    ├→ MCP Tools (Phase 6) [depends on 3]
    └→ Chat Endpoint (Phase 7) [depends on 2,3,4,5,6] ← AFTER tools & persistence
    ↓
SECURITY (Phase 8) [depends on 7]
    ↓
FRONTEND (Phase 9) [depends on 7]
    ↓
TESTING (Phase 10) [depends on all implementing phases]
    ↓
DEPLOYMENT (Phase 11) [depends on 10]
```

**Critical Path**: Phase 1 → Phase 2 → Phase 3 → Phase 4 → Phase 5 → Phase 6 → Phase 7 → Phase 8 → Phase 9 → Phase 10 → Phase 11

**Key Dependency Fix**: Chat Endpoint (Phase 7) now correctly positioned AFTER Conversation Persistence (Phase 5) and Tools Implementation (Phase 6), eliminating circular dependency risk.

**Parallelizable**: After Phase 4, certain strands can run in parallel (marked with [P])

---

## Phase 1: Project Setup

**Goal**: Initialize project structure, dependencies, and environment configuration
**Duration**: 1 task
**Blocker**: Yes (foundation for all subsequent work)

### Setup Tasks

- [x] T001 Create FastAPI project structure for Phase III chatbot in `/backend/app/chat/` with subdirectories: models, services, routers, mcp_server, agent

- [x] T002 Create frontend directory structure for ChatKit integration in `/frontend/app/chat/` with components: ChatInterface.tsx, MessageList.tsx, InputField.tsx

- [x] T003 Add Phase III dependencies to `/backend/requirements.txt`: openai>=1.0.0, mcp>=0.3.0, httpx>=0.24.0, tenacity>=8.2.0

- [x] T004 Create `/backend/.env.example` with Phase III environment variables: OPENAI_API_KEY, OPENAI_MODEL, MCP_SERVER_HOST, MCP_SERVER_PORT

- [x] T005 Setup Next.js ChatKit package in `/frontend/package.json`: add @openai-sdk/chatkit and related dependencies

- [x] T006 Create `/backend/app/chat/config.py` to load Phase III configuration from environment (OpenAI API key, model, MCP settings)

---

## Phase 2: Foundation - Database & Models

**Goal**: Define SQLModel data models and create database migrations for conversations and messages; setup foundational middleware
**Duration**: 7 tasks
**Blocker**: Yes (required for all data persistence)
**Test Criteria**: All models instantiate correctly; schema migrations apply without errors to Neon; CORS middleware functions

### Database Tasks

- [x] T007 Create SQLModel `Conversation` model in `/backend/app/models/conversation.py` with fields: id (UUID), user_id (UUID), created_at, updated_at, relationships to messages

- [x] T008 Create SQLModel `Message` model in `/backend/app/models/message.py` with fields: id (UUID), conversation_id (UUID), user_id (UUID), role (enum: user/assistant), content (text), tool_calls (JSONB), created_at

- [x] T009 Update existing `Task` model in `/backend/app/models/task.py` to ensure compatibility with Phase III (verify completed boolean, created_at, updated_at fields exist)

- [x] T010 Create Alembic migration files in `/backend/alembic/versions/` to add conversations and messages tables to Neon

- [x] T011 Create database query repository in `/backend/app/repositories/conversation_repository.py` with methods: get_conversation, get_messages, save_message, create_conversation

- [x] T012 Create database query repository in `/backend/app/repositories/task_repository.py` with methods: get_task_by_id, get_tasks_by_user_and_status, add_task, complete_task, delete_task, update_task

- [x] T013 Implement CORS middleware in `/backend/app/main.py` to allow requests from frontend domain (allow_origins=[...], allow_methods=["*"], allow_headers=["*"]); register with FastAPI app.add_middleware()

---

## Phase 3: Foundation - MCP Server Infrastructure

**Goal**: Initialize MCP server using official MCP SDK and register tool definitions; integrate MCP into FastAPI lifespan
**Duration**: 6 tasks
**Blocker**: Yes (required for agent and chat endpoint)
**Test Criteria**: MCP server starts; tools discoverable via MCP protocol; JSON schemas validate; MCP integrated with FastAPI lifespan

### MCP Server Tasks

- [x] T014 Initialize MCP server in `/backend/app/mcp_server/server.py` using official MCP SDK with transport layer (stdio or HTTP)

- [x] T015 Create MCP tool definitions in `/backend/app/mcp_server/tools.py` registering 5 tools: add_task, list_tasks, complete_task, delete_task, update_task with JSON schemas

- [x] T016 Create tool input validation in `/backend/app/mcp_server/validators.py` ensuring all inputs match schemas (user_id UUID, task_id UUID, status enum, titles <200 chars)

- [x] T017 Create tool execution layer in `/backend/app/mcp_server/executors.py` that routes tool calls to repository methods

- [x] T018 Create error handling wrapper in `/backend/app/mcp_server/error_handler.py` converting tool errors to MCP JSON error responses (ValidationError, NotFoundError, DatabaseError)

- [x] T019 Integrate MCP server startup into FastAPI lifespan event in `/backend/app/main.py`: initialize MCP server on app startup, shutdown on app shutdown; ensure MCP server runs in background and is accessible to agent layer

---

## Phase 4: Foundation - AI Agent Configuration

**Goal**: Configure OpenAI Agents SDK integration with MCP tools
**Duration**: 4 tasks
**Blocker**: Yes (required for chat endpoint)
**Test Criteria**: Agent initializes with tools; tool functions callable; system prompt properly formatted

### Agent Configuration Tasks

- [x] T020 Create agent factory in `/backend/app/agent/factory.py` initializing OpenAI Agent with model, tools, system prompt template

- [x] T021 Create system prompt template in `/backend/app/agent/prompts.py` with instructions for task management intent detection, tool usage, error handling, clarification requests

- [x] T022 Create tool processor in `/backend/app/agent/tool_processor.py` converting MCP tool outputs to agent-compatible format and handling tool chaining

- [x] T023 Create agent error handler in `/backend/app/agent/error_handler.py` with fallback responses for agent failures (timeouts, rate limits, parsing errors)

---

## Phase 5: Core Feature - Conversation Persistence

**Goal**: Ensure conversation history is loaded and persisted correctly, enabling conversation resumption
**Duration**: 4 tasks
**Blocker**: Medium (required for resuming conversations)
**Test Criteria**: Conversations persist across requests; correct user isolation; timestamps accurate

### Conversation Persistence Tasks

- [ ] T024 [US2] Create Conversation entity creation in `/backend/app/services/conversation_service.py` method `create_conversation(user_id: UUID) -> UUID` returning new conversation_id

- [ ] T025 [US2] Implement conversation history retrieval in `/backend/app/services/conversation_service.py` method `get_recent_messages(conversation_id: UUID, limit: int = 50) -> List[Message]` ordered by created_at ascending

- [ ] T026 [US2] Implement message appending in `/backend/app/services/conversation_service.py` method `append_message(conversation_id: UUID, role: str, content: str, tool_calls: dict = None)` transactionally

- [ ] T027 [US2] Create test scenario: user opens chat → sends message → closes → reopens → previous messages visible in UI state

---

## Phase 6: Core Feature - MCP Tools Implementation

**Goal**: Implement 5 task management tools with full CRUD operations
**Duration**: 8 tasks
**Blocker**: High (tools are primary feature)
**Test Criteria**: Each tool executes without errors; database changes persist; error cases handled gracefully

### Task Management Tools

- [ ] T028 [US3] Implement add_task tool in `/backend/app/mcp_server/tools/task_tools.py` handler: validate user_id/title, insert to tasks table, return task_id + metadata, handle title >200 chars error

- [ ] T029 [US3] Implement list_tasks tool in `/backend/app/mcp_server/tools/task_tools.py` handler: filter by user_id + completed status (all|pending|completed), return paginated array, handle invalid status error

- [ ] T030 [US3] [P] Implement complete_task tool in `/backend/app/mcp_server/tools/task_tools.py` handler: find task by user_id+task_id, set completed=true, return updated task, handle not-found error

- [ ] T031 [US3] [P] Implement delete_task tool in `/backend/app/mcp_server/tools/task_tools.py` handler: find task, delete from tasks table, return deleted task_id, handle not-found error

- [ ] T032 [US3] [P] Implement update_task tool in `/backend/app/mcp_server/tools/task_tools.py` handler: update title/description (optional params), validate fields, return updated task, handle validation errors

- [ ] T033 [US3] Create tool error messages in `/backend/app/mcp_server/tools/error_messages.py` with templates: TaskNotFound, ValidationError (title length, empty message), DatabaseError, and corresponding JSON responses

- [ ] T034 [US3] Create tool JSON response formatter in `/backend/app/mcp_server/tools/response_formatter.py` ensuring all outputs are structured: {result: {...}} or {error: "...", details: "..."}

- [ ] T035 [US3] Create tool integration test in `/backend/tests/test_mcp_tools.py` verifying each tool's happy path and error cases (basic tests, not comprehensive—comprehensive tests in Phase 10)

---

## Phase 7: Core User Story - Chat Endpoint

**Goal**: Implement stateless POST /api/{user_id}/chat endpoint orchestrating the full chat flow
**Duration**: 7 tasks
**Blocker**: Yes (integrates all foundation components)
**Test Criteria**: Endpoint accepts POST requests; responses include conversation_id, response, tool_calls; stateless design verified

### Chat Endpoint Tasks

- [ ] T036 [US1] Create router in `/backend/app/routers/chat_router.py` defining POST /api/{user_id}/chat route with request/response models

- [ ] T037 [US1] Create `ChatRequest` model in `/backend/app/models/schemas.py` with params: conversation_id (optional UUID), message (required string, max 2000 chars)

- [ ] T038 [US1] Create `ChatResponse` model in `/backend/app/models/schemas.py` with params: conversation_id, response text, tool_calls array

- [ ] T039 [US1] Implement conversation history loading in `/backend/app/services/chat_service.py` method `load_conversation_history(conversation_id: UUID, user_id: UUID, limit: int = 50)` returning last N messages; ChatService MUST call ConversationService.get_recent_messages(); no direct DB logic allowed in ChatService

- [ ] T040 [US1] [P] Implement message persistence in `/backend/app/services/chat_service.py` method `persist_messages(conversation_id: UUID, user_id: UUID, user_msg: str, assistant_response: str, tool_calls: list)` writing to messages table; ChatService MUST delegate to ConversationService.append_message(); no direct DB operations

- [ ] T041 [US1] Implement agent orchestration in `/backend/app/services/chat_service.py` method `run_agent(user_id: UUID, messages: list, user_message: str)` loading tools, running agent, handling tool calls

- [ ] T042 [US1] Implement endpoint handler in `/backend/app/routers/chat_router.py` method `chat_endpoint(user_id: UUID, request: ChatRequest, token: str)` orchestrating load → append → agent → persist → return (verify stateless—no in-memory state retained after return)

---

## Phase 8: Security & Authentication

**Goal**: Enforce JWT validation, user isolation, input sanitization
**Duration**: 4 tasks
**Blocker**: High (required before production)
**Test Criteria**: Unauthorized requests return 401; cross-user access blocked; SQL injection attempts fail

### Security Tasks

- [ ] T043 Create JWT validation middleware in `/backend/app/middleware/auth_middleware.py` extracting user_id from token, verifying signature, passing to endpoint

- [ ] T044 Create authorization check in `/backend/app/services/chat_service.py` method `verify_user_owns_conversation(user_id: UUID, conversation_id: UUID) -> bool` querying conversations table

- [ ] T045 Create input sanitization in `/backend/app/utils/sanitization.py` for user messages: strip dangerous chars, limit length, prevent SQL/script injection (SQLAlchemy ORM prevents SQL injection; focus on XSS prevention)

- [ ] T046 Implement tool authorization in `/backend/app/mcp_server/executors.py` ensuring each tool call validates user_id matches authenticated user before executing database operations

---

## Phase 9: Frontend Integration

**Goal**: Build ChatKit UI and connect to backend chat endpoint
**Duration**: 6 tasks
**Blocker**: Medium (required for user-facing feature)
**Test Criteria**: Chat UI renders; messages post to backend; responses display; error states shown

### Frontend Tasks

- [ ] T047 [P] Setup OpenAI ChatKit in `/frontend/app/chat/` with API domain configuration pointing to backend /api/{user_id}/chat

- [ ] T048 [P] Create ChatInterface component in `/frontend/app/chat/components/ChatInterface.tsx` rendering full chat UI (message list, input, send button)

- [ ] T049 [P] Implement message submission handler in `/frontend/app/chat/hooks/useChat.ts` posting to /api/{user_id}/chat with conversation_id, handling responses

- [ ] T050 [P] Implement conversation_id state management in `/frontend/app/chat/hooks/useChat.ts` creating new conversation on first message, reusing for subsequent messages in session

- [ ] T051 [P] Create error display component in `/frontend/app/chat/components/ErrorDisplay.tsx` showing user-friendly error messages (400/500 responses, network errors)

- [ ] T052 [P] Create loading state display in `/frontend/app/chat/components/LoadingIndicator.tsx` showing spinner while agent processes (during POST request)

---

## Phase 10: Testing & Validation

**Goal**: Comprehensive testing: unit tests for tools, integration tests for endpoint, statelessness verification, multi-user isolation
**Duration**: 8 tasks
**Blocker**: High (required before production deployment)
**Test Criteria**: All tests pass; code coverage >80% for critical paths; statelessness verified; no race conditions

### Testing Tasks

- [ ] T053 Create unit tests for add_task tool in `/backend/tests/test_tools/test_add_task.py` covering: valid input, missing title, title >200 chars, database error

- [ ] T054 Create unit tests for list_tasks tool in `/backend/tests/test_tools/test_list_tasks.py` covering: valid status, invalid status, empty list, pending/completed filtering, user isolation

- [ ] T055 Create unit tests for complete_task tool in `/backend/tests/test_tools/test_complete_task.py` covering: valid task, task not found, already completed task

- [ ] T056 Create unit tests for delete_task tool in `/backend/tests/test_tools/test_delete_task.py` covering: valid delete, not found error, cross-user access prevention

- [ ] T057 Create unit tests for update_task tool in `/backend/tests/test_tools/test_update_task.py` covering: update title, update description, both fields, no fields error

- [ ] T058 Create integration test for chat endpoint in `/backend/tests/test_endpoints/test_chat_endpoint.py` covering: full flow (history load → agent run → tool call → response), missing JWT (401), cross-user access (403)

- [ ] T059 Create statelessness test in `/backend/tests/test_stateless.py` verifying: (1) no global state usage, (2) no in-memory caching, (3) database is sole source of truth; concurrent requests don't corrupt state

- [ ] T060 Create multi-user isolation test in `/backend/tests/test_isolation.py` verifying: user A cannot see user B's conversations, user A's tools only manipulate user A's tasks, cross-conversation access blocked

---

## Phase 11: Deployment & Monitoring

**Goal**: Environment configuration, domain allowlisting, health checks, observability
**Duration**: 5 tasks
**Blocker**: High (required for production)
**Test Criteria**: All environments configured; health endpoint returns 200; logs structured as JSON

### Deployment Tasks

- [ ] T061 Create environment configuration in `/backend/.env.production` with: OPENAI_API_KEY (from Vault), DATABASE_URL (Neon connection), MCP_SERVER_HOST/PORT, OPENAI_MODEL

- [ ] T062 Implement health check endpoint in `/backend/app/routers/health_router.py` GET /health returning {status: "healthy", timestamp, database: "connected"}, verifying DB connection

- [ ] T063 Create structured logging in `/backend/app/logging_config.py` outputting JSON format with: timestamp, level, message, user_id (anonymized), duration, error details

- [ ] T064 Create OpenAI ChatKit domain allowlist in `/frontend/app/chat/config.ts` registering frontend domain with OpenAI console (localhost:3000 for dev, production domain for prod)

- [ ] T065 Create deployment checklist in `/docs/deployment.md` covering: environment variables, database migrations, OpenAI API key validation, domain allowlisting, CORS configuration, smoke test scenarios

---

## Task Dependency Graph

```
Phase 1: Setup
    ↓
Phase 2: Database Models + CORS (T007-T013)
    ├─→ Phase 5: Conversation Persistence (T024-T027)
    └─→ Phase 10: Database Tests (T053-T058)
    ↓
Phase 3: MCP Server (T014-T019)
    ├─→ Phase 6: MCP Tools (T028-T035)
    └─→ Phase 10: MCP Tool Tests (T053-T057)
    ↓
Phase 4: Agent Config (T020-T023)
    ↓
Phase 5: Conversation Persistence (T024-T027) [depends on Phase 2]
    ↓
Phase 6: MCP Tools (T028-T035) [depends on Phase 3]
    ↓
Phase 7: Chat Endpoint (T036-T042) [depends on Phases 2,3,4,5,6]
    ├─→ Phase 8: Security (T043-T046) [depends on Phase 7]
    ├─→ Phase 9: Frontend (T047-T052) [depends on Phase 7]
    └─→ Phase 10: Integration Tests (T058-T060) [depends on Phase 7]
    ↓
Phase 11: Deployment (T061-T065) [depends on Phase 10]
```

**Critical Dependencies**:
- T007-T013 (DB Models + CORS) must complete before T024 (Conversation Service)
- T014-T019 (MCP Foundation) must complete before T028 (Tool Implementation)
- T020-T023 (Agent Config) must complete before T036 (Chat Endpoint) ← Note: Agent requires no external tool execution, these tasks are independent
- T024-T027 (Conversation Persistence) must complete before T036 (Chat Endpoint) ← Chat Endpoint depends on ConversationService
- T028-T035 (Tools) must complete before T036 (Chat Endpoint)
- **Key Ordering Fix**: Persistence and Tools are COMPLETED before Chat Endpoint begins, eliminating circular dependencies

---

## Parallel Execution Strategy

After completing foundational phases, tasks can execute in parallel:

### Parallel Group 1: After Phase 4 Completion
```
Backend Parallel (Phase 5-6 concurrent):
- Developers A+B: Phase 5 (Conversation Persistence) - T024-T027
- Developer C: Phase 6 (MCP Tools) - T028-T035

Non-blocking:
- Documentation: deployment checklist
- DevOps: environment setup
```

### Parallel Group 2: After Phase 5+6 Completion
```
Multi-stream Execution:
- Developer D: Phase 7 (Chat Endpoint) - T036-T042 [depends on T024-T035 complete]
- Developer E: Phase 8 (Security) - T043-T046 [depends on Chat Endpoint T036+]
- Developer F: Phase 9 (Frontend) - T047-T052 [depends on Chat Endpoint T036+]

Sequential Dependency: T036-T042 must have at least T036-T038 complete before E,F start
```

### Parallel Group 3: Final
```
Testing (Phase 10) - T053-T060 [depends on all implementation phases]
    ↓
Deployment (Phase 11) - T061-T065
```

**Optimal parallelization example**:
- **Week 1**: Setup + Foundation (Sequential: T001-T023)
- **Week 2**: Persistence (T024-T027) + Tools (T028-T035) in parallel
- **Week 3**: Chat Endpoint (T036-T042) [now unblocked by completing tools+persistence]
- **Week 4**: Security (T043-T046) + Frontend (T047-T052) in parallel [both depend on T036+]
- **Week 5**: Testing (T053-T060)
- **Week 6**: Deployment (T061-T065) + Fix issues found in testing

---

## MVP Scope

**Minimum Viable Product Definition**: Users can (1) create tasks via chat, (2) list tasks via chat, (3) see agent responses

**MVP = Phase 1 + Phase 2 + Phase 3 + Phase 4 + Phase 5 + Phase 6 (add_task + list_tasks only) + Phase 7 + Phase 8 + Phase 9 (basic)**

### Must-Have for MVP (Critical Path)
- [ ] T001-T006: Project Setup (all)
- [ ] T007-T013: Database Models + CORS (all)
- [ ] T014-T019: MCP Server Foundation (all)
- [ ] T020-T023: Agent Configuration (all)
- [ ] T024-T027: Conversation Persistence (all)
- [ ] T028, T029: add_task + list_tasks tools ONLY (NOT complete/delete/update yet)
- [ ] T036-T042: Chat Endpoint (all)
- [ ] T043-T046: Security & Auth (all)
- [ ] T047-T052: Frontend ChatKit UI (all)
- [ ] **Partial T053-T060**: Smoke testing only (no comprehensive test suite)

### Can-Defer (Post-MVP, Phase MVP+1)
- [ ] T030-T032: complete_task, delete_task, update_task tools (Phase 6 remainder)
- [ ] T033-T035: Tool error handling & formatting (advanced features)
- [ ] T053-T060: Comprehensive testing (only smoke tests in MVP)
- [ ] T061-T065: Full deployment automation (manual setup acceptable in MVP)

**MVP Timeline**: 3-4 weeks
- Week 1: Phases 1-4 (Setup + Foundation)
- Week 2: Phases 5-6 partial + Phase 7 (Persistence + Chat Endpoint)
- Week 3: Phases 8-9 (Security + Frontend)
- Week 3.5: Smoke testing + manual deployment

**MVP Success Criteria**:
- ✅ Users can type "Create a task to review designs"
- ✅ Agent detects intent and calls add_task tool
- ✅ Task appears in database
- ✅ Users can ask "Show my pending tasks"
- ✅ Agent lists tasks with list_tasks tool
- ✅ Conversation persists across sessions
- ✅ JWT authentication enforced
- ✅ No 500 errors in happy path

---

## Implementation Notes

### Statelessness Guarantee

Every task involving the chat endpoint (T036-T042) must verify:
- No global state usage (no class variables storing user data)
- No in-memory caching (no session objects, no cache decorators)
- Database is sole source of truth (all state reads from PostgreSQL)

```python
# ✅ Correct: Load fresh data on each request
async def chat_endpoint(request: ChatRequest):
    conversation = await db.fetch_conversation(...)  # Fresh read
    agent = OpenAIAgent(tools=[...])  # Fresh instance
    # ... process, save to DB
    return response  # No in-memory state retained

# ❌ Wrong: Session manager storing state
async def chat_endpoint(request: ChatRequest):
    session = session_manager.get(user_id)  # In-memory cached
    agent.process(session)
```

### Service Separation (ChatService vs ConversationService)

**Architecture Decision**: Maintain clean separation between chat orchestration and persistence

- **ChatService** (`/backend/app/services/chat_service.py`): Orchestrates request flow, calls ConversationService and agent
- **ConversationService** (`/backend/app/services/conversation_service.py`): Handles all conversation/message persistence

**Critical Rule**: ChatService has NO direct database logic. All DB operations delegate to ConversationService.

```python
# ✅ Correct: ChatService delegates to ConversationService
class ChatService:
    def __init__(self, conversation_service: ConversationService):
        self.conv_service = conversation_service

    async def load_conversation_history(self, conversation_id, user_id):
        return await self.conv_service.get_recent_messages(...)  # Delegate

    async def persist_messages(self, conv_id, user_msg, assistant_response):
        await self.conv_service.append_message(...)  # Delegate, no SQL here

# ❌ Wrong: ChatService has direct DB logic
class ChatService:
    async def persist_messages(self, conv_id, user_msg):
        await db.execute(insert(messages).values(...))  # Don't do this!
```

### Tool Testing Strategy

For each tool (T028-T032):
- Unit test: Mock database, verify business logic
- Integration test: Real database (test DB), verify end-to-end
- Error cases: Test all exception paths

### Frontend Testing

Phase 10 tests focus on backend. Frontend can verify:
- ChatKit renders without errors
- Messages post to endpoint
- Responses display
- Error states shown

### Security Validation

Phase 8 must verify:
- JWT tokens validated in T043
- User isolation tested in T060 (cross-user prevention)
- Input sanitization in T045 (XSS, injection prevention)

---

## File Structure Summary

```
/backend/
├── app/
│   ├── chat/
│   │   ├── models/
│   │   │   ├── conversation.py (T007)
│   │   │   ├── message.py (T008)
│   │   │   └── schemas.py (T037-T038)
│   │   ├── services/
│   │   │   ├── chat_service.py (T039-T041)
│   │   │   └── conversation_service.py (T024-T026)
│   │   ├── routers/
│   │   │   └── chat_router.py (T036, T042)
│   │   ├── mcp_server/
│   │   │   ├── server.py (T014)
│   │   │   ├── tools.py (T015)
│   │   │   ├── validators.py (T016)
│   │   │   ├── executors.py (T017)
│   │   │   ├── error_handler.py (T018)
│   │   │   ├── tools/
│   │   │   │   ├── task_tools.py (T028-T032)
│   │   │   │   ├── error_messages.py (T033)
│   │   │   │   └── response_formatter.py (T034)
│   │   ├── agent/
│   │   │   ├── factory.py (T020)
│   │   │   ├── prompts.py (T021)
│   │   │   ├── tool_processor.py (T022)
│   │   │   └── error_handler.py (T023)
│   │   ├── repositories/
│   │   │   ├── conversation_repository.py (T011)
│   │   │   └── task_repository.py (T012)
│   │   ├── config.py (T006)
│   │   └── __init__.py
│   ├── middleware/
│   │   └── auth_middleware.py (T043)
│   ├── utils/
│   │   └── sanitization.py (T045)
│   ├── routers/
│   │   └── health_router.py (T062)
│   ├── main.py (T013 CORS + T019 MCP startup)
│   └── logging_config.py (T063)
├── alembic/
│   └── versions/
│       └── [migration files] (T010)
├── tests/
│   ├── test_tools/
│   │   ├── test_add_task.py (T053)
│   │   ├── test_list_tasks.py (T054)
│   │   ├── test_complete_task.py (T055)
│   │   ├── test_delete_task.py (T056)
│   │   └── test_update_task.py (T057)
│   ├── test_endpoints/
│   │   └── test_chat_endpoint.py (T058)
│   ├── test_stateless.py (T059)
│   └── test_isolation.py (T060)
├── .env.example (T004)
├── .env.production (T061)
└── requirements.txt (T003)

/frontend/
├── app/
│   └── chat/
│       ├── components/
│       │   ├── ChatInterface.tsx (T048)
│       │   ├── ErrorDisplay.tsx (T051)
│       │   └── LoadingIndicator.tsx (T052)
│       ├── hooks/
│       │   └── useChat.ts (T049-T050)
│       ├── config.ts (T064)
│       └── __init__.ts
└── package.json (T005)

/docs/
└── deployment.md (T065)
```

---

## Task Checklist Format Validation

All 65 tasks follow strict checklist format:
```
- [ ] [Task ID] [P if parallel] [Story if applicable] Description with file path
```

**Examples from this document**:
- ✅ `- [ ] T001 Create FastAPI project structure...`
- ✅ `- [ ] T013 Implement CORS middleware in /backend/app/main.py...`
- ✅ `- [ ] T039 [US1] Implement conversation history loading in /backend/app/services/chat_service.py...`
- ✅ `- [ ] T040 [US1] [P] Implement message persistence...` (parallelizable with T041)
- ✅ `- [ ] T030 [US3] [P] Implement complete_task...` (parallelizable with T031-T032)

---

## Success Criteria per Phase

| Phase | Success Criteria |
|-------|------------------|
| Phase 1 | Project structure created; dependencies installable |
| Phase 2 | Models defined; Alembic migration applies to Neon without errors; CORS middleware registered |
| Phase 3 | MCP server starts; tools discoverable; JSON schemas validate; MCP integrated with FastAPI lifespan |
| Phase 4 | Agent initializes with tools; system prompt formatted correctly |
| Phase 5 | Conversations persist; history retrievable; user isolation verified |
| Phase 6 | All tools execute successfully; database changes persist; error cases handled |
| Phase 7 | Endpoint responds to POST; statelessness verified; ChatService delegates to ConversationService correctly |
| Phase 8 | JWT validated; cross-user access blocked; input sanitized |
| Phase 9 | ChatKit renders; messages post to endpoint; responses display; error states shown |
| Phase 10 | 90% tests pass; code coverage >80%; statelessness verified; no race conditions |
| Phase 11 | All environments configured; health checks passing; logs structured as JSON |

---

## Next Steps

1. **Approve this tasks document**: Confirm all 65 tasks align with Phase III specification and reordered correctly
2. **Set up tracking**: Import tasks into project management tool (GitHub Projects, Linear, etc.)
3. **Assign teams**: Distribute tasks according to parallel execution strategy
4. **Begin Phase 1**: Start with T001-T006 (project setup)
5. **Monitor critical path**: Ensure Phases 2-4 complete before Phases 5-7 begin

---

## Document Metadata

| Field | Value |
|-------|-------|
| Tasks Version | 1.1 (Reordered & Updated) |
| Total Tasks | 65 |
| Created | February 8, 2026 |
| Last Updated | February 8, 2026 |
| Feature | Phase III - Todo AI Chatbot |
| Status | Ready for Implementation |
| Critical Fix Applied | Reordered to eliminate circular dependencies; Chat Endpoint (Phase 7) positioned AFTER Persistence (Phase 5) and Tools (Phase 6) |
| Service Architecture | ChatServ → ConversationServ separation enforced; ChatService has NO direct DB logic |
| Statelessness | Verified: no global state, no caching, DB is source of truth |
| MVP Scope | T001-T006, T007-T013, T014-T019, T020-T023, T024-T027, T028-T029, T036-T042, T043-T046, T047-T052 (3-4 weeks) |
| Next Phase | Code Generation

