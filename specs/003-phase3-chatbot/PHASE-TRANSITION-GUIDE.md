# Phase Transition Guide

This guide helps you transition between phases of the Naz Todo application.

## Table of Contents

1. [Overview](#overview)
2. [Phase I → Phase II Transition](#phase-i--phase-ii-transition)
3. [Phase II → Phase III Transition](#phase-ii--phase-iii-transition)
4. [Business Logic Migration](#business-logic-migration)
5. [Data Migration](#data-migration)

---

## Overview

Taskops application evolves through phases while maintaining backward compatibility and code reusability:

```
Phase I (Console) → Phase II (Web) → Phase III (AI Chat)
   ↓                    ↓                    ↓
Preserved           Extended            Extended
  /src/             + /backend/        + MCP Server
                    + /frontend/       + AI Agent
```

---

## Phase I → Phase II Transition

### What Gets Preserved

1. **Phase I Code**: Entirely preserved in `/src` directory
   - Still runnable: `python -m src.cli.menu`
   - Serves as reference implementation
   - Contains core business logic

2. **Business Logic Patterns**:
   - Task validation rules
   - CRUD operation logic
   - Error handling patterns
   - Test coverage approach (>80%)

3. **Project Philosophy**:
   - Clean architecture (models → services → interface)
   - Spec-driven development
   - Claude Code generation

### What Changes

| Aspect | Phase I | Phase II |
|--------|---------|----------|
| **Interface** | CLI (input/print) | Web UI (React) |
| **Storage** | In-memory dict | PostgreSQL |
| **Users** | Single user | Multi-user with auth |
| **Architecture** | Monolithic | Client-server (REST) |
| **Communication** | Direct function calls | HTTP/JSON API |
| **State** | In-memory (volatile) | Database (persistent) |
| **Deployment** | Local Python script | Docker Compose |

### Migration Steps

#### Step 1: Setup Project Structure

```bash
# Run setup script to create directory structure
# Windows:
setup-structure.bat

# macOS/Linux:
chmod +x setup-structure.sh && ./setup-structure.sh
```

This creates:
- `/backend` - FastAPI application
- `/frontend` - Next.js application
- Configuration files (Dockerfiles, docker-compose.yml)

#### Step 2: Configure Environment

```bash
# Copy environment template
cp .env.example .env

# Edit .env and set:
# - DATABASE_URL (from Neon)
# - BETTER_AUTH_SECRET (generate with: openssl rand -base64 32)
# - NEXT_PUBLIC_API_URL (http://localhost:8000 for dev)
```

#### Step 3: Port Business Logic

**Phase I** (`src/services/task_manager.py`):
```python
class TaskManager:
    def create_task(self, title: str, description: str = None) -> Task:
        # Validation
        if not title or len(title) > 200:
            raise ValidationError("Invalid title")

        # Create in-memory
        task = Task(id=self.next_id, title=title, description=description)
        self.tasks[task.id] = task
        self.next_id += 1
        return task
```

**Phase II** (`backend/app/routes/tasks.py`):
```python
@router.post("/tasks")
async def create_task(
    task_data: TaskCreate,
    user_id: str = Depends(verify_token),
    session: AsyncSession = Depends(get_session)
):
    # Same validation logic
    if not task_data.title or len(task_data.title) > 200:
        raise HTTPException(400, "Invalid title")

    # Create in database
    task = Task(user_id=user_id, **task_data.dict())
    session.add(task)
    await session.commit()
    await session.refresh(task)
    return task
```

**Key Changes**:
- Add `user_id` parameter (from JWT)
- Replace in-memory storage with database session
- Use `HTTPException` instead of custom exceptions
- Add async/await for database operations

#### Step 4: Implement Frontend

Create Next.js components that call the REST API:

**Task List Component** (`frontend/components/tasks/task-list.tsx`):
```typescript
export function TaskList() {
  const [tasks, setTasks] = useState<Task[]>([])

  useEffect(() => {
    fetch(`${API_URL}/api/tasks`, {
      headers: {
        'Authorization': `Bearer ${getJWT()}`
      }
    })
    .then(res => res.json())
    .then(data => setTasks(data))
  }, [])

  return (
    <div>
      {tasks.map(task => (
        <TaskItem key={task.id} task={task} />
      ))}
    </div>
  )
}
```

#### Step 5: Database Migration

```bash
# Inside backend directory
cd backend

# Initialize Alembic
alembic init alembic

# Create initial migration
alembic revision --autogenerate -m "Initial schema"

# Apply migration
alembic upgrade head
```

#### Step 6: Run Phase II

```bash
# Start all services
docker-compose up

# Access:
# Frontend: http://localhost:3000
# Backend: http://localhost:8000/docs
```

### Reusable Code Checklist

- [ ] Port task validation logic from Phase I
- [ ] Adapt CRUD patterns to async/database
- [ ] Maintain >80% test coverage
- [ ] Keep clean architecture (models → routes → services)
- [ ] Reuse error messages and validation rules

---

## Phase II → Phase III Transition

### What Gets Preserved

1. **All Phase II Features**:
   - Web UI at `/tasks` (still functional)
   - REST API endpoints (still available)
   - Authentication system (JWT flow)
   - Database schema (extended, not replaced)
   - User management

2. **Business Logic**:
   - Task CRUD operations
   - User isolation
   - Validation rules

### What Gets Added

| Component | Phase II | Phase III |
|-----------|----------|-----------|
| **Chat Endpoint** | None | POST /api/chat |
| **MCP Server** | None | 5 tools (add, list, etc.) |
| **AI Agent** | None | OpenAI Agents SDK |
| **Chat UI** | None | ChatKit at /chat |
| **Database** | users, tasks | + conversations, messages |

### Migration Steps

#### Step 1: Extend Database Schema

```bash
# Create migration for new tables
cd backend
alembic revision --autogenerate -m "Add conversations and messages"
alembic upgrade head
```

**New Tables**:
```sql
CREATE TABLE conversations (
  id SERIAL PRIMARY KEY,
  user_id VARCHAR(255) REFERENCES users(id),
  created_at TIMESTAMP DEFAULT NOW()
);

CREATE TABLE messages (
  id SERIAL PRIMARY KEY,
  conversation_id INTEGER REFERENCES conversations(id),
  user_id VARCHAR(255) REFERENCES users(id),
  role VARCHAR(20) NOT NULL,
  content TEXT NOT NULL,
  tool_calls JSONB,
  created_at TIMESTAMP DEFAULT NOW()
);
```

#### Step 2: Install AI Dependencies

**Backend** (`backend/requirements.txt`):
```
fastapi==0.104.1
sqlmodel==0.0.14
openai==1.3.0           # NEW
mcp-sdk==1.0.0          # NEW
pydantic==2.5.0
```

**Frontend** (`frontend/package.json`):
```json
{
  "dependencies": {
    "next": "16.0.0",
    "react": "19.0.0",
    "@openai/chatkit": "^1.0.0"  // NEW
  }
}
```

#### Step 3: Implement MCP Server

**Define MCP Tools** (`backend/app/mcp/tools.py`):
```python
from mcp import Tool, Parameter, PropertyType

add_task_tool = Tool(
    name="add_task",
    description="Create a new task for the user",
    parameters={
        "user_id": Parameter(type=PropertyType.STRING, required=True),
        "title": Parameter(type=PropertyType.STRING, required=True),
        "description": Parameter(type=PropertyType.STRING, required=False)
    }
)

# Handler (stateless)
async def add_task_handler(user_id: str, title: str, description: str = None):
    # Reuse Phase II task creation logic
    task = Task(user_id=user_id, title=title, description=description)
    session.add(task)
    await session.commit()
    return {"task_id": task.id, "status": "created"}
```

#### Step 4: Implement Chat Endpoint

**Chat Route** (`backend/app/routes/chat.py`):
```python
@router.post("/chat")
async def chat(
    message: str,
    conversation_id: Optional[int] = None,
    user_id: str = Depends(verify_token),
    session: AsyncSession = Depends(get_session)
):
    # 1. Fetch or create conversation
    if conversation_id:
        conv = await session.get(Conversation, conversation_id)
    else:
        conv = Conversation(user_id=user_id)
        session.add(conv)
        await session.commit()

    # 2. Store user message
    user_msg = Message(
        conversation_id=conv.id,
        user_id=user_id,
        role="user",
        content=message
    )
    session.add(user_msg)
    await session.commit()

    # 3. Build message history
    history = await session.exec(
        select(Message)
        .where(Message.conversation_id == conv.id)
        .order_by(Message.created_at)
    )
    messages = [{"role": m.role, "content": m.content} for m in history]

    # 4. Run OpenAI Agent with MCP tools
    agent_response = await task_agent.process_message(
        user_id=user_id,
        messages=messages,
        mcp_tools=[add_task_tool, list_tasks_tool, ...]
    )

    # 5. Store assistant response
    assistant_msg = Message(
        conversation_id=conv.id,
        user_id=user_id,
        role="assistant",
        content=agent_response
    )
    session.add(assistant_msg)
    await session.commit()

    # 6. Return response
    return {
        "conversation_id": conv.id,
        "response": agent_response
    }
```

#### Step 5: Add ChatKit UI

**Chat Page** (`frontend/app/(app)/chat/page.tsx`):
```typescript
import { ChatKit } from '@openai/chatkit'

export default function ChatPage() {
  const { token } = useAuth()  // JWT from Better Auth

  return (
    <ChatKit
      apiEndpoint="/api/chat"
      authToken={token}
      domainKey={process.env.NEXT_PUBLIC_OPENAI_DOMAIN_KEY}
    />
  )
}
```

#### Step 6: Configure OpenAI

```bash
# Add to .env
OPENAI_API_KEY=sk-proj-your-key-here
NEXT_PUBLIC_OPENAI_DOMAIN_KEY=your-domain-key  # From OpenAI dashboard
```

#### Step 7: Run Phase III

```bash
# Rebuild containers with new dependencies
docker-compose up --build

# Access:
# - Web UI: http://localhost:3000/tasks (Phase II)
# - Chat UI: http://localhost:3000/chat (Phase III)
# - Backend API: http://localhost:8000/docs
```

### Dual Interface Architecture

Phase III provides **two ways** to manage tasks:

1. **Traditional Web UI** (`/tasks`):
   - Form-based task creation
   - List view with edit/delete buttons
   - Same as Phase II

2. **Conversational Chat UI** (`/chat`):
   - Natural language input
   - AI-powered task management
   - MCP tools call same business logic as REST API

**Key Insight**: Both interfaces operate on the same `tasks` table. The chat interface internally uses MCP tools that perform the same operations as REST endpoints.

---

## Business Logic Migration

### Validation Logic (Reusable)

**Phase I** (src/lib/validators.py):
```python
def validate_title(title: str) -> str:
    if not title:
        raise ValueError("Title is required")
    if len(title) > 200:
        raise ValueError("Title too long")
    return title.strip()
```

**Phase II** (backend/app/schemas/task.py):
```python
from pydantic import BaseModel, validator

class TaskCreate(BaseModel):
    title: str
    description: Optional[str] = None

    @validator('title')
    def validate_title(cls, v):
        if not v:
            raise ValueError("Title is required")
        if len(v) > 200:
            raise ValueError("Title too long")
        return v.strip()
```

**Phase III** (backend/app/mcp/tools.py):
```python
async def add_task_handler(user_id: str, title: str, description: str = None):
    # Reuse same validation via Pydantic
    task_data = TaskCreate(title=title, description=description)
    # Pydantic automatically validates
    ...
```

### CRUD Patterns (Portable)

**Pattern**: Extract business logic into separate functions

```python
# backend/app/services/task_service.py (NEW)
class TaskService:
    @staticmethod
    async def create_task(
        session: AsyncSession,
        user_id: str,
        title: str,
        description: Optional[str] = None
    ) -> Task:
        """Reusable task creation logic"""
        # Validation
        task_data = TaskCreate(title=title, description=description)

        # Create task
        task = Task(user_id=user_id, **task_data.dict())
        session.add(task)
        await session.commit()
        await session.refresh(task)

        return task
```

**Usage in REST API** (Phase II):
```python
@router.post("/tasks")
async def create_task(
    task_data: TaskCreate,
    user_id: str = Depends(verify_token),
    session: AsyncSession = Depends(get_session)
):
    return await TaskService.create_task(
        session, user_id, task_data.title, task_data.description
    )
```

**Usage in MCP Tool** (Phase III):
```python
async def add_task_handler(user_id: str, title: str, description: str = None):
    async with get_session() as session:
        task = await TaskService.create_task(
            session, user_id, title, description
        )
        return {"task_id": task.id, "status": "created"}
```

---

## Data Migration

### Phase I → Phase II

**Challenge**: No database in Phase I (in-memory only)

**Solution**: Fresh start with Phase II database schema

**Steps**:
1. Create Neon database
2. Run Alembic migrations to create tables
3. Start with empty database
4. Users create tasks via web UI

**Note**: No data to migrate since Phase I data is volatile.

### Phase II → Phase III

**Challenge**: Add new tables without losing existing data

**Solution**: Alembic migration with backward compatibility

**Migration Script** (`alembic/versions/002_add_conversations.py`):
```python
def upgrade():
    # Add new tables
    op.create_table(
        'conversations',
        sa.Column('id', sa.Integer(), primary_key=True),
        sa.Column('user_id', sa.String(255), nullable=False),
        sa.Column('created_at', sa.TIMESTAMP(), server_default=sa.func.now()),
        sa.ForeignKeyConstraint(['user_id'], ['users.id'], ondelete='CASCADE')
    )

    op.create_table(
        'messages',
        sa.Column('id', sa.Integer(), primary_key=True),
        sa.Column('conversation_id', sa.Integer(), nullable=False),
        sa.Column('user_id', sa.String(255), nullable=False),
        sa.Column('role', sa.String(20), nullable=False),
        sa.Column('content', sa.Text(), nullable=False),
        sa.Column('tool_calls', sa.JSON()),
        sa.Column('created_at', sa.TIMESTAMP(), server_default=sa.func.now()),
        sa.ForeignKeyConstraint(['conversation_id'], ['conversations.id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['user_id'], ['users.id'], ondelete='CASCADE')
    )

    # Create indexes
    op.create_index('idx_conversations_user_id', 'conversations', ['user_id'])
    op.create_index('idx_messages_conversation_id', 'messages', ['conversation_id'])

def downgrade():
    # Rollback changes
    op.drop_table('messages')
    op.drop_table('conversations')
```

**Apply Migration**:
```bash
cd backend
alembic upgrade head
```

**Result**:
- Existing `users` and `tasks` tables untouched
- New `conversations` and `messages` tables added
- Zero downtime (no data loss)

---

## Testing Migration

### Phase I → Phase II

**Port Tests**:

**Phase I Test** (`src/tests/unit/test_task_manager.py`):
```python
def test_create_task():
    manager = TaskManager()
    task = manager.create_task("Buy milk")
    assert task.title == "Buy milk"
    assert task.id == 1
```

**Phase II Test** (`backend/tests/test_tasks.py`):
```python
async def test_create_task(client: AsyncClient, auth_token: str):
    response = await client.post(
        "/api/tasks",
        json={"title": "Buy milk"},
        headers={"Authorization": f"Bearer {auth_token}"}
    )
    assert response.status_code == 201
    data = response.json()
    assert data["title"] == "Buy milk"
    assert "id" in data
```

**Key Changes**:
- Add authentication (JWT token)
- Use HTTP client instead of direct calls
- Test async functions
- Verify JSON responses

### Phase II → Phase III

**New Tests for MCP Tools**:

```python
# backend/tests/test_mcp_tools.py
async def test_add_task_tool():
    result = await add_task_handler(
        user_id="user_123",
        title="Buy groceries",
        description="Milk, eggs, bread"
    )

    assert result["status"] == "created"
    assert "task_id" in result

    # Verify task was created in database
    task = await session.get(Task, result["task_id"])
    assert task.title == "Buy groceries"
    assert task.user_id == "user_123"
```

**New Tests for Chat Endpoint**:

```python
# backend/tests/test_chat.py
async def test_chat_endpoint(client: AsyncClient, auth_token: str):
    response = await client.post(
        "/api/chat",
        json={"message": "Add task to buy groceries"},
        headers={"Authorization": f"Bearer {auth_token}"}
    )

    assert response.status_code == 200
    data = response.json()
    assert "conversation_id" in data
    assert "response" in data
    assert "buy groceries" in data["response"].lower()
```

---

## Rollback Strategy

### Phase II → Phase I

If you need to revert to Phase I:

```bash
# Stop Phase II containers
docker-compose down

# Run Phase I console app
source .venv/bin/activate  # or .venv\Scripts\activate on Windows
python -m src.cli.menu
```

**Note**: Phase I code is never modified, so it always works.

### Phase III → Phase II

If you need to disable AI features:

1. **Keep Phase II Web UI**:
   - Just use `/tasks` instead of `/chat`
   - REST API still works

2. **Remove Phase III Components** (optional):
   ```bash
   # Comment out chat routes in backend
   # Remove ChatKit from frontend
   # Keep database as-is (conversations table unused but harmless)
   ```

3. **Database Rollback** (if needed):
   ```bash
   cd backend
   alembic downgrade -1  # Roll back one migration
   ```

---

## Troubleshooting

### Common Migration Issues

**Issue**: Database migration fails

**Solution**:
```bash
# Check current migration version
alembic current

# Show migration history
alembic history

# Manually fix database, then stamp version
alembic stamp head
```

**Issue**: Phase I validation logic doesn't work in Phase II

**Solution**: Port validation to Pydantic validators in schemas

**Issue**: MCP tools can't access database

**Solution**: Ensure tools receive database session via dependency injection

---

## Summary

### Phase I → Phase II
- ✅ Preserve Phase I code in `/src`
- ✅ Port business logic to FastAPI routes
- ✅ Add SQLModel for database operations
- ✅ Create Next.js frontend
- ✅ Implement JWT authentication

### Phase II → Phase III
- ✅ Keep all Phase II features functional
- ✅ Extend database schema (conversations, messages)
- ✅ Add MCP server with 5 tools
- ✅ Implement stateless chat endpoint
- ✅ Integrate OpenAI Agents SDK
- ✅ Add ChatKit UI

### Key Principles
- **Progressive Enhancement**: Build on previous phases
- **Code Reusability**: Share business logic across interfaces
- **Backward Compatibility**: Previous features keep working
- **Clean Architecture**: Maintain separation of concerns

---

**Generated with Claude Code**
Co-Authored-By: Claude Sonnet 4.5 <noreply@anthropic.com>
