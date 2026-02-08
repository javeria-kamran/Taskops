# Naz Todo - Unified Project Architecture (All Phases)

## Executive Summary

This document defines the complete project architecture for the Naz Todo application, spanning three implementation phases from a console application to an AI-powered web application. The architecture is designed to evolve progressively while maintaining clean separation of concerns and code reusability.

## Table of Contents

1. [Architecture Philosophy](#architecture-philosophy)
2. [Phase Overview](#phase-overview)
3. [Unified Project Structure](#unified-project-structure)
4. [Technology Stack Evolution](#technology-stack-evolution)
5. [Data Architecture](#data-architecture)
6. [API Architecture](#api-architecture)
7. [Authentication & Security](#authentication--security)
8. [Deployment Architecture](#deployment-architecture)
9. [Development Workflow](#development-workflow)
10. [Migration Strategy](#migration-strategy)

---

## Architecture Philosophy

### Core Principles

1. **Progressive Enhancement**: Each phase builds upon the previous, preserving working functionality
2. **Clean Architecture**: Clear separation between entities, business logic, and interfaces
3. **Spec-Driven Development**: All code generated from specifications by Claude Code
4. **Code Reusability**: Business logic shared across phases where applicable
5. **Stateless Design**: Scalable, resilient services with database-centric state
6. **User Isolation**: Multi-tenancy with strict data segregation by user_id

### Design Patterns

- **Repository Pattern**: Database abstraction layer (Phase II & III)
- **Dependency Injection**: Modular, testable components
- **Factory Pattern**: Dynamic creation of tasks, conversations
- **Strategy Pattern**: Multiple interfaces (CLI, Web, Chat) for same business logic
- **MVC/MPA**: Separation of models, views, and controllers

---

## Phase Overview

### Phase I: Console Application ✅ COMPLETED
- **Timeline**: Completed
- **Type**: Single-user CLI application
- **Storage**: In-memory (volatile)
- **Interface**: Text-based menu
- **Deployment**: Local Python execution

### Phase II: Web Application 🔜 NEXT
- **Timeline**: In Progress
- **Type**: Multi-user web application
- **Storage**: PostgreSQL (persistent)
- **Interface**: Responsive web UI
- **Deployment**: Docker Compose

### Phase III: AI Chatbot 🔮 PLANNED
- **Timeline**: Planned
- **Type**: AI-powered conversational interface
- **Storage**: PostgreSQL (extended)
- **Interface**: Web UI + Natural Language Chat
- **Deployment**: Docker Compose (extended)

---

## Unified Project Structure

```
Todo-HACKATHON/
│
├── .spec-kit/                          # Spec-Kit configuration
│   └── config.yaml
│
├── .github/                            # GitHub Actions CI/CD
│   └── workflows/
│       ├── phase1-tests.yml            # Phase I CI
│       ├── phase2-tests.yml            # Phase II CI
│       └── phase3-tests.yml            # Phase III CI
│
├── specs/                              # Feature specifications
│   ├── 001-phase1-console-app/         # Phase I specs
│   │   ├── spec.md
│   │   ├── plan.md
│   │   ├── tasks.md
│   │   └── contracts/
│   ├── 002-phase2-web-app/             # Phase II specs
│   │   ├── overview.md
│   │   ├── architecture.md
│   │   ├── features/
│   │   │   ├── task-crud.md
│   │   │   └── authentication.md
│   │   ├── api/
│   │   │   └── rest-endpoints.md
│   │   ├── database/
│   │   │   └── schema.md
│   │   └── ui/
│   │       ├── components.md
│   │       └── pages.md
│   └── 003-phase3-chatbot/             # Phase III specs
│       ├── overview.md
│       ├── architecture.md
│       ├── features/
│       │   ├── chatbot.md
│       │   └── mcp-tools.md
│       ├── api/
│       │   ├── chat-endpoint.md
│       │   └── mcp-server.md
│       ├── database/
│       │   └── schema.md
│       └── ui/
│           └── chatkit-integration.md
│
├── src/                                # Phase I: Console App (Preserved)
│   ├── __init__.py
│   ├── models/
│   │   ├── __init__.py
│   │   └── task.py                     # Task entity (in-memory)
│   ├── services/
│   │   ├── __init__.py
│   │   └── task_manager.py             # Business logic
│   ├── cli/
│   │   ├── __init__.py
│   │   ├── menu.py                     # Console menu
│   │   └── handlers.py                 # CLI handlers
│   ├── lib/
│   │   ├── __init__.py
│   │   ├── exceptions.py
│   │   └── validators.py
│   └── tests/
│       ├── unit/
│       │   ├── test_task.py
│       │   ├── test_task_manager.py
│       │   └── test_validators.py
│       └── integration/
│           └── test_cli.py
│
├── backend/                            # Phase II & III: FastAPI Backend
│   ├── app/
│   │   ├── __init__.py
│   │   ├── main.py                     # FastAPI app entry
│   │   ├── config.py                   # Environment config
│   │   ├── database.py                 # SQLModel connection
│   │   │
│   │   ├── models/                     # SQLModel entities
│   │   │   ├── __init__.py
│   │   │   ├── task.py                 # Phase II: Task model
│   │   │   ├── user.py                 # Phase II: User model (Better Auth)
│   │   │   ├── conversation.py         # Phase III: Conversation model
│   │   │   └── message.py              # Phase III: Message model
│   │   │
│   │   ├── schemas/                    # Pydantic request/response
│   │   │   ├── __init__.py
│   │   │   ├── task.py
│   │   │   ├── user.py
│   │   │   ├── conversation.py         # Phase III
│   │   │   └── message.py              # Phase III
│   │   │
│   │   ├── routes/                     # API endpoints
│   │   │   ├── __init__.py
│   │   │   ├── tasks.py                # Phase II: REST CRUD
│   │   │   └── chat.py                 # Phase III: Chat endpoint
│   │   │
│   │   ├── middleware/                 # Middleware
│   │   │   ├── __init__.py
│   │   │   ├── auth.py                 # JWT verification
│   │   │   └── cors.py                 # CORS config
│   │   │
│   │   ├── dependencies/               # Dependency injection
│   │   │   ├── __init__.py
│   │   │   └── auth.py                 # Auth dependencies
│   │   │
│   │   ├── mcp/                        # Phase III: MCP Server
│   │   │   ├── __init__.py
│   │   │   ├── server.py               # MCP server setup
│   │   │   └── tools.py                # MCP tool definitions
│   │   │
│   │   └── agents/                     # Phase III: AI Agents
│   │       ├── __init__.py
│   │       └── task_agent.py           # OpenAI agent logic
│   │
│   ├── tests/
│   │   ├── __init__.py
│   │   ├── test_tasks.py               # Phase II tests
│   │   ├── test_auth.py                # Phase II tests
│   │   ├── test_chat.py                # Phase III tests
│   │   ├── test_mcp_tools.py           # Phase III tests
│   │   └── conftest.py                 # Shared fixtures
│   │
│   ├── alembic/                        # Database migrations
│   │   ├── versions/
│   │   │   ├── 001_initial_schema.py   # Phase II: users, tasks
│   │   │   └── 002_add_conversations.py # Phase III: conversations, messages
│   │   └── env.py
│   │
│   ├── Dockerfile
│   ├── requirements.txt
│   └── requirements-dev.txt
│
├── frontend/                           # Phase II & III: Next.js Frontend
│   ├── app/
│   │   ├── (auth)/                     # Auth routes (public)
│   │   │   ├── signin/
│   │   │   │   └── page.tsx
│   │   │   └── signup/
│   │   │       └── page.tsx
│   │   │
│   │   ├── (app)/                      # Protected routes
│   │   │   ├── layout.tsx              # App layout with auth check
│   │   │   ├── tasks/                  # Phase II: Task management UI
│   │   │   │   ├── page.tsx            # Task list page
│   │   │   │   ├── [id]/
│   │   │   │   │   └── page.tsx        # Task detail/edit page
│   │   │   │   └── new/
│   │   │   │       └── page.tsx        # Create task page
│   │   │   │
│   │   │   └── chat/                   # Phase III: Chatbot UI
│   │   │       ├── page.tsx            # Chat interface page
│   │   │       └── [conversationId]/
│   │   │           └── page.tsx        # Resume conversation
│   │   │
│   │   ├── api/                        # API routes (if needed)
│   │   │   └── auth/
│   │   │       └── [...all]/
│   │   │           └── route.ts        # Better Auth handler
│   │   │
│   │   ├── layout.tsx                  # Root layout
│   │   └── page.tsx                    # Landing page
│   │
│   ├── components/
│   │   ├── ui/                         # Reusable UI components
│   │   │   ├── button.tsx
│   │   │   ├── input.tsx
│   │   │   ├── card.tsx
│   │   │   ├── dialog.tsx
│   │   │   └── toast.tsx
│   │   │
│   │   ├── tasks/                      # Phase II: Task components
│   │   │   ├── task-list.tsx
│   │   │   ├── task-item.tsx
│   │   │   ├── task-form.tsx
│   │   │   └── task-filters.tsx
│   │   │
│   │   ├── chat/                       # Phase III: Chat components
│   │   │   ├── chat-interface.tsx      # ChatKit wrapper
│   │   │   ├── message-list.tsx
│   │   │   └── conversation-history.tsx
│   │   │
│   │   └── auth/                       # Auth components
│   │       ├── signin-form.tsx
│   │       ├── signup-form.tsx
│   │       └── auth-guard.tsx
│   │
│   ├── lib/
│   │   ├── api.ts                      # API client with JWT
│   │   ├── auth.ts                     # Better Auth config
│   │   └── utils.ts                    # Helper functions
│   │
│   ├── types/
│   │   ├── task.ts                     # TypeScript interfaces
│   │   ├── user.ts
│   │   ├── conversation.ts             # Phase III
│   │   └── message.ts                  # Phase III
│   │
│   ├── __tests__/                      # Jest tests
│   │   ├── components/
│   │   └── lib/
│   │
│   ├── public/                         # Static assets
│   ├── Dockerfile
│   ├── package.json
│   ├── tsconfig.json
│   ├── tailwind.config.ts
│   └── next.config.js
│
├── shared/                             # Shared utilities (optional)
│   └── types/
│       └── task.ts                     # Shared types (if needed)
│
├── docker-compose.yml                  # Development environment
├── docker-compose.prod.yml             # Production environment
│
├── .env.example                        # Environment template
├── .gitignore
├── pyproject.toml                      # Phase I Python config
├── uv.lock
│
├── ARCHITECTURE.md                     # This file
├── README.md                           # Project overview
├── CLAUDE.md                           # Root development guide
└── AGENTS.md                           # Agent specifications
```

---

## Technology Stack Evolution

### Phase I: Console Application

| Layer | Technology | Purpose |
|-------|-----------|---------|
| Language | Python 3.13+ | Core implementation |
| Package Manager | UV | Dependency management |
| Data Storage | In-memory (dict) | Volatile task storage |
| Interface | CLI (input/print) | Text-based interaction |
| Testing | pytest | Unit/integration tests |
| Coverage | pytest-cov | >80% coverage target |

### Phase II: Web Application

| Layer | Technology | Purpose |
|-------|-----------|---------|
| **Frontend** | | |
| Framework | Next.js 16+ | React-based SSR/CSR |
| Language | TypeScript | Type-safe JavaScript |
| Styling | Tailwind CSS | Utility-first CSS |
| Auth Client | Better Auth | Session management |
| API Client | Fetch API | HTTP requests to backend |
| Testing | Jest + React Testing Library | Component tests |
| **Backend** | | |
| Framework | FastAPI | Async Python web framework |
| Language | Python 3.13+ | Core implementation |
| ORM | SQLModel | Type-safe SQL operations |
| Validation | Pydantic | Request/response validation |
| Auth | JWT (HS256) | Stateless authentication |
| Testing | pytest + httpx | API endpoint tests |
| **Database** | | |
| Primary DB | Neon Serverless PostgreSQL | Managed PostgreSQL |
| Migrations | Alembic (via SQLModel) | Schema versioning |
| **Infrastructure** | | |
| Containerization | Docker | Consistent environments |
| Orchestration | Docker Compose | Multi-service management |

### Phase III: AI Chatbot

| Layer | Technology | Purpose |
|-------|-----------|---------|
| **Frontend** (additions) | | |
| Chat UI | OpenAI ChatKit | Conversational interface |
| Domain Allowlist | OpenAI Platform | Security configuration |
| **Backend** (additions) | | |
| AI Framework | OpenAI Agents SDK | Agent orchestration |
| MCP | Official MCP SDK | Tool protocol |
| LLM | GPT-4 Turbo | Natural language processing |
| **Database** (additions) | | |
| New Tables | conversations, messages | Chat history persistence |

---

## Data Architecture

### Phase I: In-Memory Storage

```python
# Simple dictionary storage
class TaskManager:
    def __init__(self):
        self.tasks: Dict[int, Task] = {}
        self.next_id: int = 1
```

**Characteristics**:
- No persistence
- Single user
- No relationships
- Volatilestate (lost on exit)

### Phase II: Relational Database (PostgreSQL)

```sql
-- Entity-Relationship Diagram

┌──────────────────────┐
│       users          │
│──────────────────────│
│ id (PK)              │ VARCHAR(255)
│ email                │ VARCHAR(255) UNIQUE
│ name                 │ VARCHAR(255)
│ email_verified       │ BOOLEAN
│ image                │ TEXT
│ created_at           │ TIMESTAMP
│ updated_at           │ TIMESTAMP
└──────────────┬───────┘
               │ 1
               │
               │ *
┌──────────────▼───────┐
│       tasks          │
│──────────────────────│
│ id (PK)              │ SERIAL
│ user_id (FK)         │ VARCHAR(255) → users.id
│ title                │ VARCHAR(200) NOT NULL
│ description          │ TEXT
│ completed            │ BOOLEAN DEFAULT FALSE
│ created_at           │ TIMESTAMP
│ updated_at           │ TIMESTAMP
└──────────────────────┘
```

**Indexes**:
- `idx_tasks_user_id` on `tasks(user_id)` - for user isolation
- `idx_tasks_completed` on `tasks(completed)` - for filtering
- `idx_tasks_created_at` on `tasks(created_at DESC)` - for sorting

### Phase III: Extended Schema (Conversations)

```sql
-- Extended Entity-Relationship Diagram

┌──────────────────────┐
│       users          │
└──────────────┬───────┘
               │ 1
               │
               ├──────────────┬─────────────────┐
               │ *            │ *               │ *
               │              │                 │
┌──────────────▼───────┐  ┌──▼──────────────┐  │
│       tasks          │  │ conversations   │  │
└──────────────────────┘  │─────────────────│  │
                          │ id (PK)         │  │
                          │ user_id (FK)    │  │
                          │ created_at      │  │
                          │ updated_at      │  │
                          └──────┬──────────┘  │
                                 │ 1           │
                                 │             │
                                 │ *           │
                          ┌──────▼──────────┐  │
                          │    messages     │  │
                          │─────────────────│  │
                          │ id (PK)         │  │
                          │ conversation_id │◄─┘
                          │ user_id (FK)    │
                          │ role            │  ('user' | 'assistant')
                          │ content         │  TEXT
                          │ tool_calls      │  JSONB (optional)
                          │ created_at      │  TIMESTAMP
                          └─────────────────┘
```

**New Indexes (Phase III)**:
- `idx_conversations_user_id` on `conversations(user_id)`
- `idx_messages_conversation_id` on `messages(conversation_id)`
- `idx_messages_created_at` on `messages(created_at)`

---

## API Architecture

### Phase I: Direct Function Calls

```python
# No API - direct service calls
task_manager = TaskManager()
task = task_manager.create_task("Buy groceries", "Milk, eggs, bread")
```

### Phase II: RESTful API

**Base URL**: `http://localhost:8000/api`

**Authentication**: JWT token in `Authorization: Bearer <token>` header

**Endpoints**:

| Method | Endpoint | Description | Auth Required |
|--------|----------|-------------|---------------|
| POST | `/auth/signup` | Create new user account | No |
| POST | `/auth/signin` | Login and get JWT | No |
| GET | `/tasks` | List all tasks (user-specific) | Yes |
| POST | `/tasks` | Create new task | Yes |
| GET | `/tasks/{id}` | Get single task | Yes |
| PUT | `/tasks/{id}` | Update task | Yes |
| PATCH | `/tasks/{id}/complete` | Toggle task completion | Yes |
| DELETE | `/tasks/{id}` | Delete task | Yes |

**Request/Response Examples**:

```json
// POST /api/tasks
{
  "title": "Buy groceries",
  "description": "Milk, eggs, bread"
}

// Response: 201 Created
{
  "id": 15,
  "user_id": "user_abc123",
  "title": "Buy groceries",
  "description": "Milk, eggs, bread",
  "completed": false,
  "created_at": "2024-12-28T10:00:00Z",
  "updated_at": "2024-12-28T10:00:00Z"
}
```

### Phase III: Stateless Chat API (Addition)

**New Endpoint**:

| Method | Endpoint | Description | Auth Required |
|--------|----------|-------------|---------------|
| POST | `/chat` | Send message to AI agent | Yes |

**Request/Response**:

```json
// POST /api/chat
{
  "message": "Add task to buy groceries",
  "conversation_id": 42  // Optional, omit for new conversation
}

// Response: 200 OK
{
  "conversation_id": 42,
  "response": "I've created a new task: 'Buy groceries'. Task ID is 15.",
  "tool_calls": [
    {
      "tool": "add_task",
      "arguments": {"title": "Buy groceries"},
      "result": {"task_id": 15, "status": "created"}
    }
  ]
}
```

**MCP Tools** (called by AI agent):

1. `add_task(user_id, title, description?)`
2. `list_tasks(user_id, completed?)`
3. `complete_task(user_id, task_id, completed)`
4. `update_task(user_id, task_id, title?, description?)`
5. `delete_task(user_id, task_id)`

---

## Authentication & Security

### Phase I: No Authentication
- Single-user application
- No security layer needed

### Phase II: JWT-Based Authentication

**Flow**:

```
1. User signs up → Better Auth creates user in DB
2. User signs in → Better Auth verifies credentials
3. Better Auth issues JWT token (signed with BETTER_AUTH_SECRET)
4. Frontend stores token in memory (or secure httpOnly cookie)
5. Frontend sends token in Authorization header for all API requests
6. Backend verifies token signature and extracts user_id
7. Backend filters all queries by user_id (user isolation)
```

**JWT Claims**:
```json
{
  "sub": "user_abc123",  // User ID
  "email": "user@example.com",
  "iat": 1703001600,     // Issued at
  "exp": 1703606400      // Expires (7 days)
}
```

**Security Measures**:
- ✅ Passwords hashed with bcrypt (handled by Better Auth)
- ✅ JWT tokens signed with HS256
- ✅ Shared secret (`BETTER_AUTH_SECRET`) between Next.js and FastAPI
- ✅ User isolation enforced at database query level
- ✅ CORS restricted to frontend origin
- ✅ SQL injection prevented by SQLModel ORM
- ✅ Input validation via Pydantic schemas

### Phase III: Extended Security

**Additional Measures**:
- ✅ All chat requests authenticated (JWT)
- ✅ MCP tools validate user_id parameter
- ✅ Prompt injection prevention (user messages as data, not instructions)
- ✅ Conversation isolation (users can only access their own chats)

---

## Deployment Architecture

### Phase I: Local Execution

```
Developer Machine
└── Python 3.13+ Runtime
    └── UV Virtual Environment
        └── python -m src.cli.menu
```

### Phase II: Docker Compose (Development)

```
┌─────────────────────────────────────────────────────────┐
│                  Docker Compose Network                  │
│                                                          │
│  ┌──────────────┐         ┌──────────────┐             │
│  │   Frontend   │         │   Backend    │             │
│  │  (Next.js)   │◄───────►│  (FastAPI)   │             │
│  │ Port: 3000   │  HTTP   │ Port: 8000   │             │
│  └──────────────┘         └──────┬───────┘             │
│                                   │                      │
│                                   │ PostgreSQL           │
│                                   │ Connection           │
└───────────────────────────────────┼──────────────────────┘
                                    │
                                    ▼
                        ┌────────────────────┐
                        │   Neon Database    │
                        │   (Cloud-hosted)   │
                        └────────────────────┘
```

**docker-compose.yml**:
```yaml
version: '3.8'

services:
  frontend:
    build: ./frontend
    ports:
      - "3000:3000"
    environment:
      - BETTER_AUTH_SECRET=${BETTER_AUTH_SECRET}
      - DATABASE_URL=${DATABASE_URL}
      - NEXT_PUBLIC_API_URL=http://backend:8000
    depends_on:
      - backend

  backend:
    build: ./backend
    ports:
      - "8000:8000"
    environment:
      - DATABASE_URL=${DATABASE_URL}
      - BETTER_AUTH_SECRET=${BETTER_AUTH_SECRET}
      - ALLOWED_ORIGINS=http://localhost:3000
    command: uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
```

### Phase III: Extended Docker Compose

**No architectural change** - same Docker Compose setup, but:
- Backend container includes OpenAI Agents SDK and MCP SDK
- Additional environment variables:
  - `OPENAI_API_KEY`
  - `NEXT_PUBLIC_OPENAI_DOMAIN_KEY` (for ChatKit)

---

## Development Workflow

### Spec-Driven Development Process

```
┌─────────────────────────────────────────────────────────┐
│ 1. Write Specification                                   │
│    - User stories                                        │
│    - Acceptance criteria                                 │
│    - Technical requirements                              │
│    Location: /specs/{phase}/                            │
└────────────────┬────────────────────────────────────────┘
                 │
                 ▼
┌─────────────────────────────────────────────────────────┐
│ 2. Claude Code Reads Specs                              │
│    - Analyzes requirements                               │
│    - Identifies dependencies                             │
│    - Plans architecture                                  │
└────────────────┬────────────────────────────────────────┘
                 │
                 ▼
┌─────────────────────────────────────────────────────────┐
│ 3. Generate Implementation Plan                          │
│    - Break into tasks                                    │
│    - Define file structure                               │
│    - Identify shared components                          │
│    Location: /specs/{phase}/plan.md                     │
└────────────────┬────────────────────────────────────────┘
                 │
                 ▼
┌─────────────────────────────────────────────────────────┐
│ 4. Claude Code Implements                                │
│    - Generates code from specs                           │
│    - Writes tests (>80% coverage)                        │
│    - Creates documentation                               │
└────────────────┬────────────────────────────────────────┘
                 │
                 ▼
┌─────────────────────────────────────────────────────────┐
│ 5. User Tests & Validates                                │
│    - Verify functionality                                │
│    - Check acceptance criteria                           │
│    - Provide feedback                                    │
└────────────────┬────────────────────────────────────────┘
                 │
                 ▼
┌─────────────────────────────────────────────────────────┐
│ 6. Iterate if Needed                                     │
│    - Update specs based on feedback                      │
│    - Regenerate affected code                            │
│    - Repeat until criteria met                           │
└─────────────────────────────────────────────────────────┘
```

### Commands by Phase

**Phase I**:
```bash
# Development
python -m src.cli.menu

# Testing
pytest --cov=src --cov-report=html
```

**Phase II**:
```bash
# Development
docker-compose up

# Frontend only
cd frontend && npm run dev

# Backend only
cd backend && uvicorn app.main:app --reload

# Testing
cd backend && pytest
cd frontend && npm test
```

**Phase III**:
```bash
# Same as Phase II + chat features
docker-compose up

# Test MCP tools
cd backend && pytest tests/test_mcp_tools.py

# Test chat endpoint
cd backend && pytest tests/test_chat.py
```

---

## Migration Strategy

### Phase I → Phase II Migration

**Business Logic Reuse**:
```python
# Phase I (src/services/task_manager.py)
class TaskManager:
    def create_task(self, title: str, description: str = None) -> Task:
        # Validation logic (reusable)
        # In-memory storage (not reusable)
```

**Port to Phase II** (backend/app/routes/tasks.py):
```python
@router.post("/tasks")
async def create_task(
    task_data: TaskCreate,
    user_id: str = Depends(verify_token),
    session: AsyncSession = Depends(get_session)
):
    # Reuse validation logic from Phase I
    # Replace in-memory storage with SQLModel
    task = Task(user_id=user_id, **task_data.dict())
    session.add(task)
    await session.commit()
    return task
```

**What Gets Preserved**:
- Task validation rules
- Business logic patterns
- Testing approach (>80% coverage)

**What Changes**:
- Storage layer (in-memory → PostgreSQL)
- Interface (CLI → REST API)
- User model (none → multi-user)

### Phase II → Phase III Migration

**What Gets Preserved**:
- Entire Phase II functionality (web UI, REST API)
- Database schema (extended, not replaced)
- Authentication system (JWT flow)

**What Gets Added**:
- Chat endpoint (POST /api/chat)
- MCP server with 5 tools
- OpenAI agent integration
- Conversation/message models
- ChatKit UI component

**Dual Interface Strategy**:
- Users can use **web UI** at `/tasks` (Phase II)
- Users can use **chat UI** at `/chat` (Phase III)
- Both interfaces manage the same `tasks` table
- MCP tools call the same business logic as REST API

---

## Key Design Decisions

### 1. Monorepo vs Multi-Repo
**Decision**: Monorepo

**Rationale**:
- Simplified dependency management
- Easier to share types between frontend/backend
- Unified versioning
- Better for educational/hackathon context

### 2. Stateless vs Stateful Chat
**Decision**: Stateless chat endpoint (Phase III)

**Rationale**:
- Horizontal scalability
- Resilience (survives server restarts)
- Simpler deployment (no session management)
- Database-centric state (single source of truth)

### 3. MCP Tools Architecture
**Decision**: Stateless tools with user_id parameter

**Rationale**:
- Tools are pure functions (input → output)
- No shared state between tool calls
- Easy to test in isolation
- Agent can chain tools in any order

### 4. Database Choice
**Decision**: Neon Serverless PostgreSQL (Phase II+)

**Rationale**:
- Managed service (no ops overhead)
- Auto-scaling connections
- Generous free tier
- Standard PostgreSQL (portable)

### 5. Authentication Library
**Decision**: Better Auth (Next.js) + JWT (FastAPI)

**Rationale**:
- Better Auth handles user management
- JWT enables stateless auth across services
- Shared secret allows token verification
- Compatible with Next.js and FastAPI

---

## Success Metrics

### Phase I ✅
- ✅ All 5 CRUD operations working
- ✅ >80% test coverage achieved
- ✅ Zero crashes in normal operation
- ✅ Clean architecture (models → services → CLI)

### Phase II 🔜
- All Phase I features via web UI
- User signup/signin functional
- JWT authentication working
- User isolation enforced
- >80% backend test coverage
- Mobile-responsive UI

### Phase III 🔮
- Natural language task management working
- All 5 MCP tools implemented
- Conversation persistence functional
- Stateless chat architecture validated
- >80% MCP tool test coverage
- ChatKit integration successful

---

## Document Metadata

| Attribute | Value |
|-----------|-------|
| Version | 1.0 |
| Date | December 28, 2024 |
| Author | Claude Code |
| Status | Living Document |
| Phases Covered | I, II, III |

---

## References

- [Next.js Documentation](https://nextjs.org/docs)
- [FastAPI Documentation](https://fastapi.tiangolo.com/)
- [SQLModel Documentation](https://sqlmodel.tiangolo.com/)
- [Better Auth Documentation](https://www.better-auth.com/docs)
- [OpenAI Agents SDK](https://platform.openai.com/docs/agents)
- [MCP Documentation](https://modelcontextprotocol.io/)
- [Neon Documentation](https://neon.tech/docs)
- [Spec-Kit Plus](https://github.com/specify-kit/specify-kit)

---

**Generated with Claude Code**
Co-Authored-By: Claude Sonnet 4.5 <noreply@anthropic.com>
