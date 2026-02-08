# Todo AI Chatbot - Project Structure (Evaluation-Ready)

## Root Directory Organization

Clean, minimal root directory following best practices:

```
/Todo-hackathon/
├── backend/                          [FastAPI server + Python modules]
├── frontend/                         [Next.js 14 + React application]
├── specs/                            [All specification documents]
├── .env                              [Local environment (not versioned)]
├── .env.example                      [Environment template]
├── docker-compose.yml                [Development Docker setup]
├── docker-compose.prod.yml           [Production Docker setup]
├── README.md                         [Project overview]
├── ARCHITECTURE.md                   [System architecture]
├── CLAUDE.md                         [Claude Code instructions]
├── AGENTS.md                         [AI agents documentation]
├── pyproject.toml                    [Project metadata]
├── uv.lock                           [UV package manager lock]
└── PROJECT_STRUCTURE.md              [This file - directory guide]
```

---

## Specifications Directory (`/specs`)

### Structure
```
specs/
├── 001-phase1-console-app/           [Python console app with in-memory database]
│   ├── spec.md
│   ├── tasks.md                      [18 implementation tasks]
│   ├── plan.md
│   └── (supporting docs)
│
├── 002-phase2-web-app/               [FastAPI backend + web frontend]
│   ├── spec.md
│   ├── tasks.md                      [25 implementation tasks]
│   ├── plan.md
│   ├── api/                          [REST API specifications]
│   ├── database/                     [Database schema]
│   ├── features/                     [Feature specifications]
│   └── ui/                           [UI/UX specifications]
│
├── phase-3/                          [✓ ACTIVE: AI Chatbot with MCP]
│   ├── spec.md                       [Phase III specification]
│   ├── specification.md              [Full specification document]
│   ├── tasks.md                      [65 implementation tasks (T001-T065)]
│   ├── plan.md                       [Architecture & implementation plan]
│   ├── architecture.md               [System architecture]
│   ├── overview.md                   [Executive summary]
│   ├── IMPLEMENTATION-GUIDE.md       [Step-by-step guide]
│   ├── PHASE_III_DELIVERABLES.md     [Phase 1 deliverables]
│   ├── PHASE_III_BACKEND_SCAFFOLD.md [Backend setup]
│   ├── PHASE_III_BACKEND_COMPLETE.md [Backend completion]
│   ├── PHASE_II_COMPLETION.md        [Phase 2 foundation]
│   ├── PHASE-TRANSITION-GUIDE.md     [Schema migration guide]
│   ├── BACKEND_DIRECTORY_STRUCTURE.md [Backend file structure]
│   ├── api/                          [API specifications]
│   │   ├── chat-endpoint.md          [POST /api/{user_id}/chat]
│   │   └── mcp-server.md             [MCP protocol spec]
│   ├── database/                     [Database design]
│   │   └── schema.md                 [Conversation & Message tables]
│   ├── features/                     [Feature specifications]
│   │   ├── chatbot.md                [AI chatbot behavior]
│   │   └── mcp-tools.md              [Task management tools]
│   ├── ui/                           [UI/UX design]
│   │   └── chatkit-integration.md    [ChatKit component integration]
│   └── checklists/                   [Validation & quality checks]
│       └── requirements.md
│
├── agent/                            [Agent research & design]
│   └── (future: OpenAI Agents documentation)
│
└── mcp/                              [MCP research & design]
    └── (future: Model Context Protocol documentation)
```

---

## Backend Directory (`/backend`)

```
backend/
├── app/
│   ├── models/                       [SQLModel definitions]
│   │   ├── user.py                   [User model (Phase II)]
│   │   ├── task.py                   [Task model (T009)]
│   │   └── __init__.py
│   │
│   ├── chat/                         [Phase III Chat Module]
│   │   ├── __init__.py
│   │   ├── config.py                 [Configuration (T006)]
│   │   │
│   │   ├── models/
│   │   │   ├── conversation.py       [Conversation model (T007)]
│   │   │   ├── message.py            [Message model (T008)]
│   │   │   ├── schemas.py            [API schemas (T037-T038)]
│   │   │   └── __init__.py
│   │   │
│   │   ├── repositories/             [Repository pattern (T011-T012)]
│   │   │   ├── conversation_repository.py  [Conversation CRUD]
│   │   │   ├── task_repository.py         [Task CRUD]
│   │   │   └── __init__.py
│   │   │
│   │   ├── services/
│   │   │   ├── conversation_service.py    [Persistence (T024-T027)]
│   │   │   ├── chat_service.py            [Orchestration (T036-T042)]
│   │   │   └── __init__.py
│   │   │
│   │   ├── routers/
│   │   │   ├── __init__.py           [Chat endpoints (T051-T052)]
│   │   │   └── (future: more routers)
│   │   │
│   │   ├── agent/
│   │   │   └── __init__.py           [OpenAI Agents (T048-T050)]
│   │   │
│   │   └── mcp_server/
│   │       ├── server.py             [MCP server (T014-T019)]
│   │       ├── tools/                [Tool definitions (T028-T032)]
│   │       └── __init__.py
│   │
│   ├── routers/                      [Phase II endpoints]
│   │   ├── auth_router.py            [Authentication]
│   │   ├── tasks_router.py           [Task CRUD]
│   │   └── __init__.py
│   │
│   ├── middleware/
│   │   ├── security.py               [Security headers middleware]
│   │   └── __init__.py
│   │
│   ├── main.py                       [FastAPI app entry (T013, T019)]
│   ├── config.py                     [App configuration]
│   ├── database.py                   [Database connection]
│   ├── dependencies.py               [Dependency injection]
│   └── __init__.py
│
├── alembic/                          [Database migrations]
│   ├── versions/
│   │   ├── 001_create_users_table.py
│   │   ├── 002_create_tasks_table.py
│   │   ├── 003_create_conversations_table.py  [T010]
│   │   ├── 004_create_messages_table.py       [T010]
│   │   └── 005_enhance_tasks_table.py         [T010]
│   ├── env.py
│   ├── script.py.mako
│   └── alembic.ini
│
├── tests/                            [Unit & integration tests]
│   ├── test_chat_service.py
│   ├── test_repositories.py
│   ├── test_endpoints.py
│   └── __init__.py
│
├── requirements.txt                  [Python dependencies (T001-T006)]
├── requirements-dev.txt              [Development dependencies]
├── .env.example                      [Environment template]
├── pyproject.toml                    [Project metadata]
├── Dockerfile                        [Container build]
├── test_db_connection.py             [DB test utility]
└── README.md                         [Backend README]
```

---

## Frontend Directory (`/frontend`)

```
frontend/
├── app/
│   ├── chat/                         [Phase III Chat interface]
│   │   ├── page.tsx                  [Chat page]
│   │   ├── layout.tsx                [Chat layout]
│   │   └── (future: sub-routes)
│   │
│   ├── tasks/                        [Phase II Task management]
│   │   ├── page.tsx
│   │   ├── layout.tsx
│   │   └── (sub-routes)
│   │
│   ├── auth/                         [Authentication pages]
│   │   ├── login/page.tsx
│   │   ├── register/page.tsx
│   │   └── callback/page.tsx
│   │
│   ├── page.tsx                      [Landing page]
│   ├── layout.tsx                    [Root layout]
│   └── globals.css
│
├── components/                       [Reusable components]
│   ├── chat/                         [Chat components]
│   │   ├── ChatMessages.tsx
│   │   ├── ChatInput.tsx
│   │   └── ConversationList.tsx
│   │
│   ├── tasks/                        [Task components]
│   │   ├── TaskList.tsx
│   │   ├── TaskForm.tsx
│   │   └── TaskItem.tsx
│   │
│   └── common/                       [Shared components]
│       ├── Header.tsx
│       ├── Sidebar.tsx
│       └── Footer.tsx
│
├── hooks/                            [React hooks]
│   ├── useChat.ts
│   ├── useTasks.ts
│   └── useAuth.ts
│
├── lib/                              [Utilities]
│   ├── api.ts                        [API client]
│   ├── auth.ts                       [Auth utilities]
│   ├── types.ts                      [TypeScript types]
│   └── utils.ts                      [Helper functions]
│
├── public/                           [Static assets]
│   ├── images/
│   ├── icons/
│   └── ...
│
├── styles/                           [Global styles]
│   └── (CSS modules)
│
├── .env.example                      [Environment template]
├── package.json                      [Node dependencies]
├── tsconfig.json                     [TypeScript config]
├── next.config.js                    [Next.js config]
├── Dockerfile                        [Container build]
└── README.md                         [Frontend README]
```

---

## Task Reference by Phase

### Phase III Tasks (`specs/phase-3/tasks.md`)

#### Phase 1: Project Setup (T001-T006)
- T001: Project structure
- T002: Dependencies
- T003: Environment variables
- T004: .env.example
- T005: Configuration module
- T006: Settings singleton

#### Phase 2: Database Foundation (T007-T013)
- **T007**: Conversation SQLModel (`backend/app/chat/models/conversation.py`)
- **T008**: Message SQLModel (`backend/app/chat/models/message.py`)
- **T009**: Task model enhancement (`backend/app/models/task.py`)
- **T010**: Alembic migrations (`backend/alembic/versions/003_*.py`, `004_*.py`)
- **T011**: ConversationRepository (`backend/app/chat/repositories/conversation_repository.py`)
- **T012**: TaskRepository (`backend/app/chat/repositories/task_repository.py`)
- **T013**: CORS middleware (`backend/app/main.py`)

#### Phase 3+: Services & Implementation (T014+)
- T014-T019: MCP server infrastructure
- T020-T023: Agent configuration
- T024-T027: Conversation persistence
- T028-T032: MCP tools implementation
- T036-T042: Chat endpoint
- T043-T046: Security & authentication
- T047-T052: Frontend integration
- T053-T060: Testing & validation
- T061-T065: Deployment & monitoring

---

## Important Files for Evaluation

### Documentation
- 📄 `/README.md` - Project overview
- 📄 `/ARCHITECTURE.md` - System architecture
- 📄 `/CLAUDE.md` - Claude Code instructions
- 📄 `/specs/phase-3/spec.md` - Phase III specification
- 📄 `/specs/phase-3/tasks.md` - 65 implementation tasks
- 📄 `/specs/phase-3/plan.md` - Strategic implementation plan

### Backend Code
- 🐍 `/backend/app/main.py` - FastAPI application
- 🐍 `/backend/app/chat/` - Phase III implementation
- 🐍 `/backend/alembic/` - Database migrations
- 📋 `/backend/requirements.txt` - Dependencies

### Frontend Code
- ⚛️ `/frontend/app/` - Next.js application
- ⚛️ `/frontend/components/` - UI components
- 📋 `/frontend/package.json` - Dependencies

---

## Evaluation Checklist

✅ **Directory Structure**
- [ ] Root directory clean & minimal
- [ ] All phase specs in `/specs/`
- [ ] Phase 3 in `/specs/phase-3/`
- [ ] Backend & frontend isolated
- [ ] No scattered documentation

✅ **Documentation**
- [ ] README.md accessible at root
- [ ] ARCHITECTURE.md explains design
- [ ] Phase 3 spec in `/specs/phase-3/spec.md`
- [ ] Tasks in `/specs/phase-3/tasks.md`
- [ ] Plan in `/specs/phase-3/plan.md`

✅ **Implementation**
- [ ] Backend logic intact in `/backend/`
- [ ] Frontend logic intact in `/frontend/`
- [ ] No broken imports
- [ ] Database models with user isolation
- [ ] MCP server scaffolded

✅ **Deployment Ready**
- [ ] Docker compose files present
- [ ] Environment templates available
- [ ] Requirements.txt updated
- [ ] Migrations in alembic/versions/
- [ ] Config management via .env

---

## Running the Project

### Development

**Backend:**
```bash
cd backend
pip install -r requirements.txt
uvicorn app.main:app --reload
```

**Frontend:**
```bash
cd frontend
npm install
npm run dev
```

### Docker

```bash
docker-compose up
```

### Production

```bash
docker-compose -f docker-compose.prod.yml up
```

---

## Documentation Navigation

1. **Start Here**: `/README.md` (5 min read)
2. **Architecture**: `/ARCHITECTURE.md` (15 min read)
3. **Phase 3 Overview**: `/specs/phase-3/overview.md` (10 min read)
4. **Full Spec**: `/specs/phase-3/spec.md` (30 min read)
5. **Implementation Tasks**: `/specs/phase-3/tasks.md` (Reference)
6. **Implementation Plan**: `/specs/phase-3/plan.md` (Strategic overview)

---

**Last Updated**: 2026-02-08
**Status**: ✅ Evaluation-Ready
