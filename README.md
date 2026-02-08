# Naz Todo - Agentic Todo Application

An evolving todo application that progresses through five phases, from a simple console app to a cloud-native AI-powered task management system. Built entirely through spec-driven development with Claude Code and Spec-Kit Plus.

## Current Status

| Phase | Status | Description |
|-------|--------|-------------|
| **Phase I** | ✅ COMPLETED | Console application with in-memory storage |
| **Phase II** | ✅ COMPLETED | Full-stack web app with PostgreSQL & auth |
| **Phase III** | 📋 PLANNED | AI chatbot with MCP tools |
| Phase IV | 🔮 FUTURE | Kubernetes deployment |
| Phase V | 🔮 FUTURE | Cloud-native with Kafka & Dapr |

## Quick Start

### Phase I: Console Application (COMPLETED)

```bash
# Install dependencies
uv venv && source .venv/bin/activate  # or .venv\Scripts\activate on Windows
uv pip install -e ".[dev]"

# Run application
python -m src.cli.menu

# Run tests
pytest --cov=src --cov-report=html
```

### Phase II & III: Web Application (Setup)

```bash
# Run setup script to create directory structure
# On Windows:
setup-structure.bat

# On macOS/Linux:
chmod +x setup-structure.sh && ./setup-structure.sh

# Configure environment
cp .env.example .env
# Edit .env with your database credentials and secrets

# Start with Docker Compose
docker-compose up

# Access:
# - Frontend: http://localhost:3000
# - Backend API: http://localhost:8000
# - API Docs: http://localhost:8000/docs
```

See [DEPLOYMENT.md](./DEPLOYMENT.md) for detailed setup instructions.

---

## Project Overview

### Phase I: Console Application ✅

**Status**: Completed
**Interface**: Text-based CLI
**Storage**: In-memory (volatile)
**Users**: Single user

**Features**:
- ✅ Create tasks with title and description
- ✅ View all tasks
- ✅ Update task details
- ✅ Delete tasks with confirmation
- ✅ Toggle task completion status
- ✅ >80% test coverage

**Tech Stack**:
- Python 3.13+
- UV package manager
- pytest for testing
- Standard library only (no external dependencies)

### Phase II: Web Application ✅

**Status**: Completed
**Interface**: Responsive web UI
**Storage**: Neon PostgreSQL
**Users**: Multi-user with authentication

**Features**:
- ✅ All Phase I features via web interface
- ✅ User signup/signin with Better Auth
- ✅ JWT token-based authentication
- ✅ User-specific task isolation
- ✅ Mobile-responsive design
- ✅ RESTful API
- ✅ Real-time task updates
- ✅ Task filtering (All/Active/Completed)
- ✅ Security headers and hardening
- ✅ Comprehensive test coverage

**Tech Stack**:
- **Frontend**: Next.js 16+, TypeScript, Tailwind CSS, Better Auth
- **Backend**: FastAPI, SQLModel, Pydantic, pytest
- **Database**: Neon Serverless PostgreSQL
- **Infrastructure**: Docker, Docker Compose

### Phase III: AI Chatbot 📋

**Status**: Planned (Specs Complete)
**Interface**: Web UI + Natural Language Chat
**Storage**: PostgreSQL (extended)
**AI**: OpenAI Agents with MCP tools

**Features**:
- All Phase II features (preserved)
- Conversational task management
- Natural language understanding
- MCP (Model Context Protocol) server with 5 tools
- Stateless chat architecture
- Conversation history persistence
- Dual interface (Web UI + Chat)

**Tech Stack** (additions):
- **AI**: OpenAI Agents SDK, GPT-4 Turbo
- **MCP**: Official MCP SDK
- **Chat UI**: OpenAI ChatKit
- **New Tables**: conversations, messages

**Natural Language Examples**:
```
User: "Add a task to buy groceries"
AI:   "I've created a new task: 'Buy groceries'. Task ID is 15."

User: "What do I need to do today?"
AI:   "You have 3 pending tasks: 1) Buy groceries, 2) Call mom, 3) Finish report"

User: "Mark task 1 as done"
AI:   "Great! I've marked 'Buy groceries' as completed."
```

---

## Architecture

### Unified Project Structure

```
Naz-Todo/
├── specs/                      # Feature specifications (Spec-Kit)
│   ├── 001-phase1-console-app/ # Phase I specs ✅
│   ├── 002-phase2-web-app/     # Phase II specs ✅
│   └── 003-phase3-chatbot/     # Phase III specs ✅
│
├── src/                        # Phase I: Console App (Preserved)
│   ├── models/                 # Task entity
│   ├── services/               # Business logic
│   ├── cli/                    # CLI interface
│   └── tests/                  # Unit & integration tests
│
├── backend/                    # Phase II & III: FastAPI Backend
│   ├── app/
│   │   ├── models/             # SQLModel entities
│   │   ├── schemas/            # Pydantic validation
│   │   ├── routes/             # API endpoints
│   │   ├── middleware/         # Auth & CORS
│   │   ├── mcp/                # MCP server (Phase III)
│   │   └── agents/             # OpenAI agents (Phase III)
│   ├── tests/                  # API tests
│   └── alembic/                # Database migrations
│
├── frontend/                   # Phase II & III: Next.js Frontend
│   ├── app/
│   │   ├── (auth)/             # Signin/signup pages
│   │   ├── (app)/tasks/        # Task management UI (Phase II)
│   │   └── (app)/chat/         # Chatbot UI (Phase III)
│   ├── components/
│   │   ├── tasks/              # Task components
│   │   ├── chat/               # Chat components
│   │   └── ui/                 # Reusable UI
│   └── lib/                    # API client, auth config
│
├── ARCHITECTURE.md             # Complete architecture guide
├── DEPLOYMENT.md               # Deployment instructions
├── CLAUDE.md                   # Development guidelines
├── docker-compose.yml          # Development environment
└── README.md                   # This file
```

See [ARCHITECTURE.md](./ARCHITECTURE.md) for complete architecture details.

---

## Technology Stack Evolution

| Component | Phase I | Phase II | Phase III |
|-----------|---------|----------|-----------|
| **Language** | Python 3.13+ | Python + TypeScript | Python + TypeScript |
| **Frontend** | CLI | Next.js 16+ | Next.js 16+ + ChatKit |
| **Backend** | Direct calls | FastAPI | FastAPI + OpenAI Agents |
| **Database** | In-memory dict | Neon PostgreSQL | Neon PostgreSQL (extended) |
| **Auth** | None | Better Auth + JWT | Better Auth + JWT |
| **AI** | None | None | OpenAI Agents + MCP |
| **Deployment** | Local Python | Docker Compose | Docker Compose |
| **Testing** | pytest | pytest + Jest | pytest + Jest |

---

## API Endpoints

### Phase II: RESTful API

| Method | Endpoint | Description | Auth |
|--------|----------|-------------|------|
| POST | `/api/auth/signup` | Create user account | No |
| POST | `/api/auth/signin` | Login and get JWT | No |
| GET | `/api/tasks` | List all tasks | Yes |
| POST | `/api/tasks` | Create new task | Yes |
| GET | `/api/tasks/{id}` | Get single task | Yes |
| PUT | `/api/tasks/{id}` | Update task | Yes |
| PATCH | `/api/tasks/{id}/complete` | Toggle completion | Yes |
| DELETE | `/api/tasks/{id}` | Delete task | Yes |

### Phase III: Chat API (Addition)

| Method | Endpoint | Description | Auth |
|--------|----------|-------------|------|
| POST | `/api/chat` | Send message to AI agent | Yes |

**MCP Tools** (called by AI agent):
1. `add_task(user_id, title, description?)`
2. `list_tasks(user_id, completed?)`
3. `complete_task(user_id, task_id, completed)`
4. `update_task(user_id, task_id, title?, description?)`
5. `delete_task(user_id, task_id)`

---

## Database Schema

### Phase II: Core Tables

```sql
-- Users (managed by Better Auth)
users (id, email, name, email_verified, created_at, updated_at)

-- Tasks
tasks (
  id, user_id, title, description,
  completed, created_at, updated_at
)
```

### Phase III: Extended Tables

```sql
-- Conversations
conversations (id, user_id, created_at, updated_at)

-- Messages
messages (
  id, conversation_id, user_id, role,
  content, tool_calls, created_at
)
```

---

## Development Workflow

### Spec-Driven Development

All code is generated by Claude Code from specifications:

```
1. Write Specification → /specs/{phase}/
2. Claude Code Analyzes Requirements
3. Generate Implementation Plan → plan.md
4. Break into Atomic Tasks → tasks.md
5. Claude Code Implements Features
6. User Tests & Validates
7. Iterate if Needed
```

**No Manual Coding**: Every line of code comes from specs processed by Claude Code.

### Commands

**Phase I** (Console):
```bash
python -m src.cli.menu          # Run application
pytest --cov=src                # Run tests
```

**Phase II & III** (Web):
```bash
docker-compose up               # Start all services
docker-compose logs -f backend  # View backend logs
docker-compose down             # Stop services

# Local development (without Docker)
cd backend && uvicorn app.main:app --reload
cd frontend && npm run dev
```

---

## Testing

### Phase I: Console App
- **Framework**: pytest
- **Coverage**: >80% achieved
- **Types**: Unit tests, integration tests
- **Location**: `src/tests/`

### Phase II: Web App
- **Backend**: pytest + httpx (API tests)
- **Frontend**: Jest + React Testing Library
- **Coverage Target**: >80%
- **Location**: `backend/tests/`, `frontend/__tests__/`

### Phase III: AI Chatbot
- **MCP Tools**: pytest (isolated tool tests)
- **Chat Endpoint**: pytest (integration tests)
- **E2E**: Full conversation flows
- **Coverage Target**: >80%

---

## Security

### Phase I
- No security layer (single-user, local only)

### Phase II & III
- ✅ JWT authentication (HS256)
- ✅ Passwords hashed (bcrypt via Better Auth)
- ✅ User isolation (all queries filtered by user_id)
- ✅ CORS restricted to frontend origin
- ✅ SQL injection prevention (SQLModel ORM)
- ✅ Input validation (Pydantic schemas)
- ✅ SSL required for database (Neon)
- ✅ Prompt injection prevention (Phase III)

---

## Deployment

### Phase I: Local Execution
```bash
# Just run Python directly
python -m src.cli.menu
```

### Phase II & III: Docker Compose

**Development**:
```bash
docker-compose up
```

**Production** (VPS/Cloud):
```bash
# Configure production environment
cp .env.example .env
# Edit .env with production values

# Deploy with production compose file
docker-compose -f docker-compose.prod.yml up -d
```

See [DEPLOYMENT.md](./DEPLOYMENT.md) for detailed deployment instructions.

---

## Environment Variables

### Phase II
```bash
DATABASE_URL=postgresql://user:pass@ep-xxx.neon.tech/db?sslmode=require
BETTER_AUTH_SECRET=your-secret-key-min-32-chars
NEXT_PUBLIC_API_URL=http://localhost:8000
ALLOWED_ORIGINS=http://localhost:3000
```

### Phase III (additions)
```bash
OPENAI_API_KEY=sk-proj-xxx
NEXT_PUBLIC_OPENAI_DOMAIN_KEY=your-domain-key
```

See `.env.example` for complete template.

---

## Success Criteria

### Phase I ✅
- ✅ All 5 CRUD operations working
- ✅ >80% test coverage achieved
- ✅ Zero crashes in normal operation
- ✅ Clean architecture implemented

### Phase II ✅
- ✅ All features accessible via web UI
- ✅ User authentication working
- ✅ Multi-user isolation enforced
- ✅ >80% backend test coverage
- ✅ Mobile-responsive interface
- ✅ Production-ready with security headers
- ✅ Comprehensive documentation

### Phase III 📋
- Natural language task management
- All 5 MCP tools implemented
- Stateless chat architecture
- Conversation persistence working
- ChatKit integration successful

---

## Project Constraints

### Global Constraints (All Phases)
- **Spec-Driven**: All code generated by Claude Code from specs
- **No Manual Coding**: Everything comes from specifications
- **Test Coverage**: >80% for all business logic
- **Clean Architecture**: Clear separation of concerns

### Phase-Specific Constraints

**Phase I**:
- Python 3.13+ only
- Standard library only (no external deps for core)
- In-memory storage (acceptable for Phase I)

**Phase II**:
- Next.js 16+ (App Router, not Pages Router)
- FastAPI (not Flask/Django)
- SQLModel (not raw SQLAlchemy)
- Neon PostgreSQL (not local Postgres)
- Better Auth (not NextAuth/Clerk)

**Phase III**:
- OpenAI Agents SDK (not custom agent)
- Official MCP SDK (not custom protocol)
- Stateless chat endpoint (no server-side sessions)
- OpenAI ChatKit (for frontend chat UI)

---

## Contributing

This is an educational project for GIAIC Hackathon II. All contributions should follow the spec-driven development approach:

1. Write or update specifications in `/specs`
2. Let Claude Code generate implementation from specs
3. Test thoroughly
4. Submit PR with spec changes and generated code

---

## Documentation

- [ARCHITECTURE.md](./ARCHITECTURE.md) - Complete architecture guide for all phases
- [DEPLOYMENT.md](./DEPLOYMENT.md) - Deployment instructions and environment setup
- [CLAUDE.md](./CLAUDE.md) - Development guidelines for Claude Code
- [AGENTS.md](./AGENTS.md) - Agent specifications
- `/specs` - Detailed feature specifications for each phase

---

## Roadmap

| Phase | Target | Features |
|-------|--------|----------|
| **Phase I** | ✅ Completed | Console CRUD app |
| **Phase II** | ✅ Completed | Web app with auth & database |
| **Phase III** | TBD | AI chatbot with MCP |
| Phase IV | TBD | Kubernetes deployment |
| Phase V | TBD | Cloud-native with Kafka |

---

## License

Educational project for GIAIC Hackathon II.

---

## Acknowledgments

- Built with [Claude Code](https://claude.com/claude-code)
- Spec-Kit Plus for specification management
- GIAIC Hackathon II organizers

---

**Generated with Claude Code**
Co-Authored-By: Claude Sonnet 4.5 <noreply@anthropic.com>
