# Feature: User Authentication (Phase II)

## Overview

**Feature ID**: `authentication`
**Phase**: II - Web Application
**Priority**: P0 (Critical)
**Dependencies**: None (foundational feature)

Implement user signup, signin, and session management using Better Auth with JWT tokens for API authentication.

## User Stories

### 1. User Signup
**As a** new user
**I want to** create an account with email and password
**So that** I can start managing my tasks

**Acceptance Criteria**:
- ✅ User can access signup page
- ✅ Email field is required and validated
- ✅ Password field is required (minimum 8 characters)
- ✅ Password confirmation field matches password
- ✅ Email must be unique (no duplicate accounts)
- ✅ Account is created in database
- ✅ User is automatically signed in after signup
- ✅ User is redirected to tasks page
- ✅ User sees success message

### 2. User Signin
**As a** registered user
**I want to** sign in with my email and password
**So that** I can access my tasks

**Acceptance Criteria**:
- ✅ User can access signin page
- ✅ Email and password fields required
- ✅ Credentials are validated
- ✅ Session is created on successful signin
- ✅ JWT token is issued
- ✅ User is redirected to tasks page
- ✅ Error shown for invalid credentials
- ✅ Error shown for unverified email (if applicable)

### 3. User Signout
**As a** signed-in user
**I want to** sign out of my account
**So that** I can keep my data secure

**Acceptance Criteria**:
- ✅ User can click signout button
- ✅ Session is destroyed
- ✅ JWT token is invalidated
- ✅ User is redirected to signin page
- ✅ Protected pages are inaccessible after signout

### 4. Session Persistence
**As a** signed-in user
**I want to** stay signed in across browser sessions
**So that** I don't have to sign in every time

**Acceptance Criteria**:
- ✅ Session persists after browser close (optional "Remember me")
- ✅ Session expires after 7 days of inactivity
- ✅ User is automatically signed in on page load if valid session exists
- ✅ User is redirected to signin if session expired

### 5. Protected Routes
**As a** visitor (not signed in)
**I want to** be redirected to signin when accessing protected pages
**So that** I know I need to sign in first

**Acceptance Criteria**:
- ✅ `/tasks` page requires authentication
- ✅ Unauthenticated users redirected to `/signin`
- ✅ After signin, user redirected to originally requested page
- ✅ API requests without token receive 401 Unauthorized

## Functional Requirements

### User Entity
```typescript
interface User {
  id: string              // Auto-generated UUID
  email: string           // Unique, required
  name?: string           // Optional display name
  emailVerified: boolean  // Default: false
  image?: string          // Profile picture URL (optional)
  createdAt: Date         // Auto-generated
  updatedAt: Date         // Auto-updated
}
```

**Note**: Password hash is managed internally by Better Auth, not exposed in User object.

### Authentication Flow

**Signup Flow**:
```
1. User fills signup form (email, password, confirm password)
2. Frontend validates:
   - Email format valid
   - Password >= 8 characters
   - Passwords match
3. Frontend calls Better Auth signup endpoint
4. Better Auth:
   - Hashes password (bcrypt)
   - Creates user in database
   - Creates session
   - Issues JWT token
5. Frontend stores token
6. Redirect to /tasks
```

**Signin Flow**:
```
1. User fills signin form (email, password)
2. Frontend validates:
   - Email format valid
   - Password not empty
3. Frontend calls Better Auth signin endpoint
4. Better Auth:
   - Finds user by email
   - Verifies password hash
   - Creates session
   - Issues JWT token
5. Frontend stores token
6. Redirect to /tasks (or originally requested page)
```

**API Request Flow**:
```
1. Frontend makes API request
2. Frontend attaches JWT token to Authorization header
3. Backend middleware extracts token
4. Backend verifies token signature using BETTER_AUTH_SECRET
5. Backend extracts user_id from token payload
6. Backend passes user_id to route handler
7. Route handler filters data by user_id
8. Response sent back to frontend
```

### Validation Rules

**Email**:
- ✅ Required
- ✅ Valid email format (regex: `^[^\s@]+@[^\s@]+\.[^\s@]+$`)
- ✅ Unique (checked at database level)
- ✅ Case-insensitive (normalize to lowercase)
- ✅ Maximum 255 characters

**Password**:
- ✅ Required
- ✅ Minimum 8 characters
- ✅ Maximum 100 characters
- ❌ No complexity requirements in Basic Level (can be all letters)

**Name** (optional):
- ✅ Optional
- ✅ Maximum 100 characters
- ✅ Can contain letters, numbers, spaces

### Security Requirements

**Password Storage**:
- ✅ Passwords hashed using bcrypt (handled by Better Auth)
- ✅ Minimum 10 salt rounds
- ✅ Never store plaintext passwords
- ✅ Never log passwords

**Session Management**:
- ✅ Sessions stored in database (managed by Better Auth)
- ✅ Session tokens cryptographically random
- ✅ Session expiry configurable (default: 7 days)
- ✅ Refresh token rotation (Better Auth handles)

**JWT Tokens**:
- ✅ Signed with HS256 algorithm
- ✅ Secret key minimum 32 characters
- ✅ Include user_id in payload
- ✅ Set expiration time (7 days)
- ✅ Cannot be tampered with (signature verification)

**CORS**:
- ✅ Backend only accepts requests from frontend origin
- ✅ Credentials allowed for cookie-based auth
- ✅ Preflight requests handled

## UI/UX Requirements

### Signup Page

**Layout**:
```
┌──────────────────────────────────────┐
│                                       │
│         [Logo] Naz Todo              │
│                                       │
│      Create Your Account             │
│                                       │
│  Email                                │
│  [_____________________________]      │
│                                       │
│  Password                             │
│  [_____________________________]      │
│                                       │
│  Confirm Password                     │
│  [_____________________________]      │
│                                       │
│       [Sign Up] button                │
│                                       │
│  Already have an account?             │
│  Sign in                              │
│                                       │
└──────────────────────────────────────┘
```

**Field Requirements**:
- Email: type="email", autocomplete="email"
- Password: type="password", autocomplete="new-password"
- Confirm Password: type="password", autocomplete="new-password"
- Submit button disabled while loading

**Validation Messages**:
- "Email is required"
- "Invalid email format"
- "Password must be at least 8 characters"
- "Passwords do not match"
- "Email already in use" (from backend)

### Signin Page

**Layout**:
```
┌──────────────────────────────────────┐
│                                       │
│         [Logo] Naz Todo              │
│                                       │
│      Welcome Back                    │
│                                       │
│  Email                                │
│  [_____________________________]      │
│                                       │
│  Password                             │
│  [_____________________________]      │
│                                       │
│  [ ] Remember me                     │
│                                       │
│       [Sign In] button                │
│                                       │
│  Don't have an account?               │
│  Sign up                              │
│                                       │
└──────────────────────────────────────┘
```

**Field Requirements**:
- Email: type="email", autocomplete="email"
- Password: type="password", autocomplete="current-password"
- Remember me: checkbox (extends session duration)

**Validation Messages**:
- "Email is required"
- "Password is required"
- "Invalid email or password" (generic for security)

### Navigation Bar (Authenticated)

```
┌─────────────────────────────────────────────┐
│ [Logo] Naz Todo          [user@email.com] ▼ │
└─────────────────────────────────────────────┘
                                     │
                         ┌───────────▼──────────┐
                         │ Sign Out             │
                         └──────────────────────┘
```

**Elements**:
- Logo/app name (links to /tasks)
- User email or name
- Dropdown with "Sign Out" option

### Visual States

**Form States**:
1. **Default**: Fields empty, button enabled
2. **Loading**: Spinner on button, fields disabled
3. **Error**: Red border on invalid fields, error text below
4. **Success**: Green checkmark, redirect after 1 second

**Authentication States**:
1. **Unauthenticated**: Show signin/signup pages
2. **Authenticated**: Show tasks page with nav bar
3. **Loading**: Show loading spinner while checking session
4. **Error**: Show error message if auth check fails

## Better Auth Configuration

### Frontend Setup

**Installation**:
```bash
npm install better-auth
```

**Configuration** (`lib/auth.ts`):
```typescript
import { betterAuth } from "better-auth"
import { Pool } from "@neondatabase/serverless"

const pool = new Pool({ connectionString: process.env.DATABASE_URL })

export const auth = betterAuth({
  database: pool,

  // Email + Password authentication
  emailAndPassword: {
    enabled: true,
    minPasswordLength: 8,
    requireEmailVerification: false, // Disabled for Basic Level
  },

  // JWT configuration
  jwt: {
    enabled: true,
    secret: process.env.BETTER_AUTH_SECRET!,
    expiresIn: "7d",
  },

  // Session configuration
  session: {
    expiresIn: 60 * 60 * 24 * 7, // 7 days
    updateAge: 60 * 60 * 24, // Update every 24 hours
  },

  // URLs
  baseURL: process.env.BETTER_AUTH_URL!,
})
```

**API Route** (`app/api/auth/[...all]/route.ts`):
```typescript
import { auth } from "@/lib/auth"

export const { GET, POST } = auth.handler
```

### Backend Setup

**JWT Verification** (`middleware/auth.py`):
```python
from fastapi import HTTPException, Security
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
import jwt
from app.config import settings

security = HTTPBearer()

async def verify_token(
    credentials: HTTPAuthorizationCredentials = Security(security)
) -> str:
    """
    Verify JWT token and return user_id.

    Raises:
        HTTPException: If token is invalid or expired

    Returns:
        str: User ID from token payload
    """
    token = credentials.credentials

    try:
        payload = jwt.decode(
            token,
            settings.BETTER_AUTH_SECRET,
            algorithms=["HS256"]
        )
        user_id: str = payload.get("sub")
        if user_id is None:
            raise HTTPException(status_code=401, detail="Invalid token")
        return user_id

    except jwt.ExpiredSignatureError:
        raise HTTPException(status_code=401, detail="Token expired")

    except jwt.InvalidTokenError:
        raise HTTPException(status_code=401, detail="Invalid token")
```

**Dependency Injection** (`routes/tasks.py`):
```python
from fastapi import APIRouter, Depends
from app.middleware.auth import verify_token

router = APIRouter()

@router.get("/api/tasks")
async def get_tasks(user_id: str = Depends(verify_token)):
    # user_id is automatically extracted from JWT
    # Route handler can now filter by user_id
    pass
```

## API Integration

### Authentication Endpoints (Better Auth)

| Method | Endpoint | Purpose |
|--------|----------|---------|
| POST | `/api/auth/signup` | Create new user account |
| POST | `/api/auth/signin` | Sign in existing user |
| POST | `/api/auth/signout` | Sign out current user |
| GET | `/api/auth/session` | Get current session |

### Protected API Endpoints

All task endpoints require JWT token:
- GET `/api/tasks`
- POST `/api/tasks`
- GET `/api/tasks/{id}`
- PUT `/api/tasks/{id}`
- PATCH `/api/tasks/{id}/complete`
- DELETE `/api/tasks/{id}`

### Request/Response Examples

**Signup**:
```typescript
// Request
POST /api/auth/signup
Content-Type: application/json

{
  "email": "user@example.com",
  "password": "securepass123",
  "name": "John Doe"
}

// Response (200 OK)
{
  "user": {
    "id": "user_abc123",
    "email": "user@example.com",
    "name": "John Doe",
    "emailVerified": false,
    "createdAt": "2024-12-28T10:00:00Z"
  },
  "session": {
    "token": "eyJhbGciOiJIUzI1NiIs...",
    "expiresAt": "2025-01-04T10:00:00Z"
  }
}
```

**Signin**:
```typescript
// Request
POST /api/auth/signin
Content-Type: application/json

{
  "email": "user@example.com",
  "password": "securepass123"
}

// Response (200 OK)
{
  "user": {
    "id": "user_abc123",
    "email": "user@example.com",
    "name": "John Doe"
  },
  "session": {
    "token": "eyJhbGciOiJIUzI1NiIs...",
    "expiresAt": "2025-01-04T10:00:00Z"
  }
}
```

**Signout**:
```typescript
// Request
POST /api/auth/signout
Authorization: Bearer eyJhbGc...

// Response (200 OK)
{
  "success": true
}
```

**Session Check**:
```typescript
// Request
GET /api/auth/session
Authorization: Bearer eyJhbGc...

// Response (200 OK)
{
  "user": {
    "id": "user_abc123",
    "email": "user@example.com",
    "name": "John Doe"
  }
}

// Response (401 Unauthorized) - no valid session
{
  "detail": "Not authenticated"
}
```

### Error Responses

**Duplicate Email (409 Conflict)**:
```json
{
  "detail": "Email already in use"
}
```

**Invalid Credentials (401 Unauthorized)**:
```json
{
  "detail": "Invalid email or password"
}
```

**Weak Password (400 Bad Request)**:
```json
{
  "detail": "Password must be at least 8 characters"
}
```

## Environment Variables

### Frontend (.env.local)
```bash
# Better Auth
BETTER_AUTH_SECRET=your-secret-key-minimum-32-characters-long
BETTER_AUTH_URL=http://localhost:3000

# Database (for Better Auth user management)
DATABASE_URL=postgresql://user:pass@ep-xxx.neon.tech/neondb?sslmode=require

# Backend API
NEXT_PUBLIC_API_URL=http://localhost:8000
```

### Backend (.env)
```bash
# Database
DATABASE_URL=postgresql://user:pass@ep-xxx.neon.tech/neondb?sslmode=require

# Auth (same secret as frontend!)
BETTER_AUTH_SECRET=your-secret-key-minimum-32-characters-long

# CORS
ALLOWED_ORIGINS=http://localhost:3000
```

**Critical**: `BETTER_AUTH_SECRET` must be identical in both frontend and backend.

## Database Schema

Better Auth automatically creates these tables:

**users**:
```sql
CREATE TABLE users (
    id VARCHAR(255) PRIMARY KEY,
    email VARCHAR(255) UNIQUE NOT NULL,
    email_verified BOOLEAN DEFAULT FALSE,
    name VARCHAR(100),
    image TEXT,
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW()
);

CREATE INDEX idx_users_email ON users(email);
```

**sessions**:
```sql
CREATE TABLE sessions (
    id VARCHAR(255) PRIMARY KEY,
    user_id VARCHAR(255) NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    expires_at TIMESTAMP NOT NULL,
    created_at TIMESTAMP DEFAULT NOW()
);

CREATE INDEX idx_sessions_user_id ON sessions(user_id);
CREATE INDEX idx_sessions_expires_at ON sessions(expires_at);
```

**accounts** (for password storage):
```sql
CREATE TABLE accounts (
    id VARCHAR(255) PRIMARY KEY,
    user_id VARCHAR(255) NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    provider VARCHAR(50) NOT NULL,
    provider_account_id VARCHAR(255) NOT NULL,
    password_hash TEXT,
    created_at TIMESTAMP DEFAULT NOW()
);

CREATE INDEX idx_accounts_user_id ON accounts(user_id);
```

## Testing Requirements

### Frontend Tests

**Component Tests**:
- Signup form validates email format
- Signup form validates password length
- Signup form validates password match
- Signin form submits correct data
- Protected routes redirect to signin when not authenticated
- Nav bar shows user email when authenticated
- Sign out button works

**Integration Tests**:
- Full signup flow (form → API → redirect)
- Full signin flow (form → API → redirect)
- Session persistence (refresh page, still authenticated)
- Token expiry (redirect to signin after expiry)

### Backend Tests

**Unit Tests**:
- JWT token verification works
- JWT token expiry detected
- Invalid JWT rejected

**API Tests**:
- Protected endpoints return 401 without token
- Protected endpoints return 401 with invalid token
- Protected endpoints return 401 with expired token
- Protected endpoints return data with valid token
- User isolation enforced (User A can't access User B's tasks)

### E2E Tests

**Critical Paths**:
1. Signup → Create task → Sign out → Sign in → Verify task still there
2. Signup as User A → Create task → Signup as User B → Verify User A's task not visible
3. Sign in → Close browser → Reopen → Verify still signed in (if "Remember me" checked)
4. Sign in → Wait for token expiry → Verify redirected to signin

## Performance Requirements

- Signup/signin completes within 1 second
- Session check completes within 200ms
- Token verification adds <50ms latency to API requests
- No noticeable delay when navigating between pages (authenticated)

## Accessibility Requirements

- All form fields have labels
- Error messages announced by screen readers
- Keyboard navigation works for all forms
- Focus visible on all interactive elements
- Color not sole indicator of errors (use icons + text)

## Out of Scope (Phase II Basic Level)

The following are NOT included:
- ❌ Email verification
- ❌ Password reset flow
- ❌ OAuth providers (Google, GitHub, etc.)
- ❌ Two-factor authentication (2FA)
- ❌ Account deletion
- ❌ Profile editing
- ❌ Change password
- ❌ Rate limiting on auth endpoints

These may be added in future phases.

## Security Checklist

- ✅ Passwords hashed with bcrypt
- ✅ JWT tokens signed and verified
- ✅ Secrets stored in environment variables
- ✅ CORS properly configured
- ✅ No password in logs
- ✅ Generic error messages (don't reveal if email exists)
- ✅ HTTPS in production (not Phase II scope)
- ✅ SQL injection prevented (ORM parameterized queries)

## Success Metrics

- ✅ Users can sign up successfully
- ✅ Users can sign in successfully
- ✅ Users stay signed in across sessions
- ✅ Users can sign out
- ✅ Protected pages require authentication
- ✅ API requests without token rejected
- ✅ User isolation 100% effective (zero data leaks)
- ✅ Zero security vulnerabilities in auth flow

## Document History

| Version | Date | Changes |
|---------|------|---------|
| 1.0 | 2024-12-28 | Initial authentication specification for Phase II |
