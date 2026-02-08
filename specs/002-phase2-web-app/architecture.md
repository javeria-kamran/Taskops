# System Architecture - Phase II Web Application

## Architecture Overview

Phase II uses a **three-tier client-server architecture** with clear separation between presentation (Next.js), business logic (FastAPI), and data (PostgreSQL).

```
┌─────────────────────────────────────────────────────────────┐
│                         Browser                             │
│  ┌───────────────────────────────────────────────────────┐  │
│  │              Next.js 16 Frontend                      │  │
│  │  - React Server Components (default)                  │  │
│  │  - Client Components (interactivity)                  │  │
│  │  - Better Auth (session management)                   │  │
│  │  - API client with JWT tokens                         │  │
│  └───────────────────────────────────────────────────────┘  │
└─────────────────────────────────────────────────────────────┘
                            │
                            │ HTTP/REST + JWT
                            ▼
┌─────────────────────────────────────────────────────────────┐
│                    FastAPI Backend                          │
│  ┌───────────────────────────────────────────────────────┐  │
│  │  ┌──────────────┐  ┌──────────────┐  ┌────────────┐  │  │
│  │  │ JWT Auth     │  │ API Routes   │  │ CORS       │  │  │
│  │  │ Middleware   │→ │ /api/tasks   │  │ Middleware │  │  │
│  │  └──────────────┘  └──────────────┘  └────────────┘  │  │
│  │  ┌──────────────┐  ┌──────────────┐                  │  │
│  │  │ SQLModel     │  │ Pydantic     │                  │  │
│  │  │ Models       │  │ Schemas      │                  │  │
│  │  └──────────────┘  └──────────────┘                  │  │
│  └───────────────────────────────────────────────────────┘  │
└─────────────────────────────────────────────────────────────┘
                            │
                            │ SQL via SQLModel ORM
                            ▼
┌─────────────────────────────────────────────────────────────┐
│              Neon Serverless PostgreSQL                     │
│  ┌───────────────────────────────────────────────────────┐  │
│  │  Tables: users, tasks                                 │  │
│  │  Indexes: user_id, created_at                         │  │
│  │  Constraints: foreign keys, unique email              │  │
│  └───────────────────────────────────────────────────────┘  │
└─────────────────────────────────────────────────────────────┘
```

## Component Details

### Frontend (Next.js 16+)

**Responsibilities**:
- Render UI components
- Handle user interactions
- Manage Better Auth sessions
- Make authenticated API calls
- Display loading and error states

**Key Technologies**:
- **Framework**: Next.js 16 with App Router
- **Language**: TypeScript
- **Styling**: Tailwind CSS
- **Authentication**: Better Auth (client-side session)
- **API Client**: Fetch with JWT injection

**Component Structure**:
```
frontend/
├── app/
│   ├── (auth)/              # Auth routes (signup, signin)
│   │   ├── signup/
│   │   └── signin/
│   ├── (app)/               # Protected app routes
│   │   └── tasks/
│   ├── layout.tsx           # Root layout
│   └── page.tsx             # Landing page
├── components/
│   ├── ui/                  # Reusable UI components
│   │   ├── button.tsx
│   │   ├── input.tsx
│   │   └── card.tsx
│   ├── tasks/               # Task-specific components
│   │   ├── task-list.tsx
│   │   ├── task-item.tsx
│   │   ├── task-form.tsx
│   │   └── task-filters.tsx
│   └── auth/                # Auth components
│       ├── signup-form.tsx
│       └── signin-form.tsx
├── lib/
│   ├── api.ts               # API client with auth
│   ├── auth.ts              # Better Auth config
│   └── utils.ts             # Helper functions
└── types/
    └── task.ts              # TypeScript interfaces
```

**Rendering Strategy**:
- **Server Components** (default): Use for static content, data fetching
- **Client Components**: Use only when needed for:
  - Event handlers (onClick, onChange)
  - State management (useState, useReducer)
  - Effects (useEffect)
  - Browser APIs

### Backend (FastAPI)

**Responsibilities**:
- Validate JWT tokens
- Enforce user isolation
- Execute business logic
- Manage database transactions
- Return JSON responses

**Key Technologies**:
- **Framework**: FastAPI
- **Language**: Python 3.13+
- **ORM**: SQLModel
- **Validation**: Pydantic (built into FastAPI)
- **Testing**: pytest

**Project Structure**:
```
backend/
├── app/
│   ├── main.py              # FastAPI app entry
│   ├── config.py            # Settings (from env)
│   ├── database.py          # DB connection
│   ├── models/
│   │   ├── __init__.py
│   │   ├── user.py          # User SQLModel
│   │   └── task.py          # Task SQLModel
│   ├── schemas/
│   │   ├── __init__.py
│   │   ├── user.py          # User Pydantic schemas
│   │   └── task.py          # Task Pydantic schemas
│   ├── routes/
│   │   ├── __init__.py
│   │   └── tasks.py         # Task CRUD endpoints
│   ├── middleware/
│   │   ├── __init__.py
│   │   ├── auth.py          # JWT verification
│   │   └── cors.py          # CORS setup
│   └── dependencies/
│       ├── __init__.py
│       └── auth.py          # Auth dependency injection
├── tests/
│   ├── test_tasks.py
│   └── test_auth.py
├── requirements.txt         # Production deps
└── requirements-dev.txt     # Dev deps (pytest, etc.)
```

**Layered Architecture**:
1. **Routes** (`routes/tasks.py`): HTTP request/response handling
2. **Schemas** (`schemas/task.py`): Request/response validation
3. **Models** (`models/task.py`): Database entities
4. **Database** (`database.py`): Connection and session management

### Database (Neon PostgreSQL)

**Responsibilities**:
- Store user accounts
- Store tasks with user relationships
- Enforce data integrity
- Provide fast queries via indexes

**Schema Design**:
```sql
-- users table (managed by Better Auth via migrations)
CREATE TABLE users (
    id VARCHAR(255) PRIMARY KEY,
    email VARCHAR(255) UNIQUE NOT NULL,
    name VARCHAR(255),
    email_verified BOOLEAN DEFAULT FALSE,
    image TEXT,
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW()
);

-- tasks table
CREATE TABLE tasks (
    id SERIAL PRIMARY KEY,
    user_id VARCHAR(255) NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    title VARCHAR(200) NOT NULL,
    description TEXT,
    completed BOOLEAN DEFAULT FALSE,
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW()
);

-- Indexes for performance
CREATE INDEX idx_tasks_user_id ON tasks(user_id);
CREATE INDEX idx_tasks_completed ON tasks(completed);
CREATE INDEX idx_tasks_created_at ON tasks(created_at DESC);
```

**Connection**:
- **Pooling**: SQLModel with asyncpg
- **Connection String**: From `DATABASE_URL` environment variable
- **SSL**: Required by Neon

## Authentication Flow

### Better Auth + JWT Integration

**Why JWT?**
- Better Auth is a JavaScript library (runs in Next.js)
- FastAPI is a separate Python service
- JWT tokens allow stateless authentication across services

### Authentication Sequence

```
┌─────────┐                    ┌──────────┐                 ┌─────────┐
│ Browser │                    │ Next.js  │                 │ FastAPI │
└────┬────┘                    └────┬─────┘                 └────┬────┘
     │                              │                            │
     │ 1. POST /api/auth/signup     │                            │
     ├─────────────────────────────>│                            │
     │                              │                            │
     │                              │ 2. Create user in DB       │
     │                              │ 3. Create session          │
     │                              │ 4. Issue JWT token         │
     │                              │                            │
     │ 5. Return token + user       │                            │
     │<─────────────────────────────┤                            │
     │                              │                            │
     │ 6. Store token in memory     │                            │
     │                              │                            │
     │ 7. GET /api/tasks            │                            │
     │    Authorization: Bearer JWT │                            │
     ├─────────────────────────────>│                            │
     │                              │                            │
     │                              │ 8. Proxy to FastAPI        │
     │                              │    with JWT in header      │
     │                              ├───────────────────────────>│
     │                              │                            │
     │                              │                            │ 9. Verify JWT
     │                              │                            │ 10. Extract user_id
     │                              │                            │ 11. Query tasks
     │                              │                            │     WHERE user_id = ?
     │                              │                            │
     │                              │ 12. Return tasks           │
     │                              │<───────────────────────────┤
     │                              │                            │
     │ 13. Return tasks to browser  │                            │
     │<─────────────────────────────┤                            │
     │                              │                            │
```

### JWT Token Structure

**Claims (payload)**:
```json
{
  "sub": "user_abc123",          // Subject (user ID)
  "email": "user@example.com",
  "iat": 1703001600,              // Issued at
  "exp": 1703606400               // Expires (7 days)
}
```

**Shared Secret**:
- Environment variable: `BETTER_AUTH_SECRET`
- Must be identical in Next.js and FastAPI
- Used for signing (Next.js) and verifying (FastAPI)

### Security Implementation

**Frontend (Better Auth)**:
```typescript
// lib/auth.ts
import { betterAuth } from "better-auth"

export const auth = betterAuth({
  database: /* Neon connection */,
  jwt: {
    enabled: true,
    secret: process.env.BETTER_AUTH_SECRET,
    expiresIn: "7d"
  }
})
```

**Backend (FastAPI)**:
```python
# middleware/auth.py
from fastapi import HTTPException, Security
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
import jwt

security = HTTPBearer()

async def verify_token(credentials: HTTPAuthorizationCredentials = Security(security)):
    token = credentials.credentials
    try:
        payload = jwt.decode(token, settings.BETTER_AUTH_SECRET, algorithms=["HS256"])
        return payload["sub"]  # Return user_id
    except jwt.ExpiredSignatureError:
        raise HTTPException(status_code=401, detail="Token expired")
    except jwt.InvalidTokenError:
        raise HTTPException(status_code=401, detail="Invalid token")
```

## API Communication

### Request Flow

**Authenticated Request**:
```typescript
// Frontend: lib/api.ts
async function getTasks() {
  const session = await auth.getSession()
  const response = await fetch(`${API_URL}/api/tasks`, {
    headers: {
      'Authorization': `Bearer ${session.token}`,
      'Content-Type': 'application/json'
    }
  })
  return response.json()
}
```

**Backend Handling**:
```python
# Backend: routes/tasks.py
@router.get("/api/tasks")
async def get_tasks(
    user_id: str = Depends(verify_token),
    session: AsyncSession = Depends(get_session)
):
    tasks = await session.exec(
        select(Task).where(Task.user_id == user_id)
    )
    return tasks.all()
```

### User Isolation

**Every API endpoint**:
1. Extracts JWT from `Authorization` header
2. Verifies signature using `BETTER_AUTH_SECRET`
3. Decodes to get `user_id`
4. Filters database queries by `user_id`

**Example**:
```python
# ✅ Correct: user can only see their own tasks
tasks = await session.exec(
    select(Task).where(Task.user_id == user_id)
)

# ❌ Wrong: would expose all users' tasks
tasks = await session.exec(select(Task))
```

## Data Flow

### Create Task Example

```
User types task → Frontend Form (Client Component)
                       ↓
                  Validation (Zod schema)
                       ↓
                  POST /api/tasks with JWT
                       ↓
                  FastAPI receives request
                       ↓
                  JWT middleware extracts user_id
                       ↓
                  Route handler receives user_id
                       ↓
                  Pydantic validates request body
                       ↓
                  SQLModel creates Task instance
                       ↓
                  SQLModel inserts to database
                       ↓
                  Return created task
                       ↓
                  Frontend updates UI
```

## Error Handling

### Frontend
- **Network Errors**: Show toast notification
- **Validation Errors**: Show inline field errors
- **Auth Errors**: Redirect to signin
- **Server Errors**: Show error page with retry

### Backend
- **Validation Errors**: Return 422 with field details
- **Auth Errors**: Return 401 Unauthorized
- **Not Found**: Return 404 with message
- **Server Errors**: Return 500 with generic message (log details)

## Environment Configuration

### Frontend (.env.local)
```bash
# Better Auth
BETTER_AUTH_SECRET=your-secret-key-min-32-chars
BETTER_AUTH_URL=http://localhost:3000

# Database (for Better Auth user management)
DATABASE_URL=postgresql://user:pass@neon.tech/db?sslmode=require

# Backend API
NEXT_PUBLIC_API_URL=http://localhost:8000
```

### Backend (.env)
```bash
# Database
DATABASE_URL=postgresql://user:pass@neon.tech/db?sslmode=require

# Auth (same secret as frontend!)
BETTER_AUTH_SECRET=your-secret-key-min-32-chars

# CORS
ALLOWED_ORIGINS=http://localhost:3000
```

## Deployment Architecture (Development)

**Docker Compose**:
```yaml
services:
  frontend:
    build: ./frontend
    ports:
      - "3000:3000"
    environment:
      - BETTER_AUTH_SECRET
      - DATABASE_URL
      - NEXT_PUBLIC_API_URL=http://backend:8000
    depends_on:
      - backend

  backend:
    build: ./backend
    ports:
      - "8000:8000"
    environment:
      - DATABASE_URL
      - BETTER_AUTH_SECRET
      - ALLOWED_ORIGINS=http://localhost:3000
```

**No local database container**: Neon is cloud-hosted, no Docker container needed.

## Performance Considerations

### Frontend
- Use Server Components for initial page load (faster)
- Client Components only for interactive parts
- Implement optimistic UI updates
- Cache API responses (SWR or React Query)

### Backend
- Database connection pooling
- Index frequently queried fields
- Use SELECT only needed columns
- Implement pagination for large lists

### Database
- Indexes on `user_id`, `created_at`
- Neon auto-scales connections
- Use prepared statements (SQLModel handles this)

## Security Considerations

### Authentication
- ✅ Passwords hashed by Better Auth (bcrypt)
- ✅ JWT tokens expire (7 days)
- ✅ Tokens verified on every API request
- ✅ User isolation at database query level

### API Security
- ✅ CORS restricted to frontend origin
- ✅ Input validation (Pydantic)
- ✅ SQL injection prevented (SQLModel ORM)
- ✅ HTTPS in production (not phase II scope)

### Database Security
- ✅ Foreign key constraints
- ✅ Cascade deletes (user → tasks)
- ✅ SSL required (Neon enforces)
- ✅ Environment variables for credentials

## Testing Strategy

### Frontend
- **Unit**: Component tests (Jest + React Testing Library)
- **Integration**: User flow tests (Playwright)
- **E2E**: Full signup → task creation flow

### Backend
- **Unit**: Individual functions (pytest)
- **Integration**: API endpoints (pytest + TestClient)
- **Database**: Transactions rollback after tests

### Coverage Target
- Backend: >80%
- Frontend: >60% (focused on critical paths)

## Migration from Phase I

| Phase I | Phase II |
|---------|----------|
| `src/models/task.py` → | `backend/app/models/task.py` (SQLModel version) |
| `src/services/task_manager.py` → | `backend/app/routes/tasks.py` (API routes) |
| `src/cli/menu.py` → | `frontend/app/tasks/page.tsx` (React UI) |
| `tests/unit/` → | `backend/tests/` (pytest) + `frontend/__tests__/` (Jest) |

## Document History

| Version | Date | Changes |
|---------|------|---------|
| 1.0 | 2024-12-28 | Initial architecture specification for Phase II |
