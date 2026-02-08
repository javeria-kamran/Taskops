# REST API Endpoints Specification

## Overview

Complete specification for all REST API endpoints in the Phase II web application.

**Base URL**: `http://localhost:8000` (development)
**API Prefix**: `/api`
**Authentication**: JWT Bearer token (except auth endpoints)
**Content-Type**: `application/json`

## Authentication

All endpoints except authentication routes require a valid JWT token in the `Authorization` header:

```
Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...
```

Missing or invalid tokens return **401 Unauthorized**.

## Endpoints Summary

### Authentication Endpoints (Better Auth)
| Method | Endpoint | Auth Required | Description |
|--------|----------|---------------|-------------|
| POST | `/api/auth/signup` | No | Create new user account |
| POST | `/api/auth/signin` | No | Sign in existing user |
| POST | `/api/auth/signout` | Yes | Sign out current user |
| GET | `/api/auth/session` | Yes | Get current session |

### Task Endpoints
| Method | Endpoint | Auth Required | Description |
|--------|----------|---------------|-------------|
| GET | `/api/tasks` | Yes | List all tasks for current user |
| POST | `/api/tasks` | Yes | Create a new task |
| GET | `/api/tasks/{id}` | Yes | Get single task by ID |
| PUT | `/api/tasks/{id}` | Yes | Update task title/description |
| PATCH | `/api/tasks/{id}/complete` | Yes | Toggle task completion status |
| DELETE | `/api/tasks/{id}` | Yes | Delete a task |

---

## Authentication Endpoints

### POST /api/auth/signup

Create a new user account.

**Request**:
```json
{
  "email": "user@example.com",
  "password": "securepass123",
  "name": "John Doe"  // optional
}
```

**Response** (201 Created):
```json
{
  "user": {
    "id": "user_clp1234567890",
    "email": "user@example.com",
    "name": "John Doe",
    "emailVerified": false,
    "image": null,
    "createdAt": "2024-12-28T10:00:00.000Z",
    "updatedAt": "2024-12-28T10:00:00.000Z"
  },
  "session": {
    "token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
    "expiresAt": "2025-01-04T10:00:00.000Z"
  }
}
```

**Errors**:
- **400 Bad Request**: Invalid input (missing fields, weak password)
- **409 Conflict**: Email already in use

**Validation**:
- `email`: required, valid email format, max 255 chars
- `password`: required, min 8 chars, max 100 chars
- `name`: optional, max 100 chars

---

### POST /api/auth/signin

Sign in an existing user.

**Request**:
```json
{
  "email": "user@example.com",
  "password": "securepass123"
}
```

**Response** (200 OK):
```json
{
  "user": {
    "id": "user_clp1234567890",
    "email": "user@example.com",
    "name": "John Doe",
    "emailVerified": false,
    "image": null,
    "createdAt": "2024-12-28T10:00:00.000Z",
    "updatedAt": "2024-12-28T10:00:00.000Z"
  },
  "session": {
    "token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
    "expiresAt": "2025-01-04T10:00:00.000Z"
  }
}
```

**Errors**:
- **400 Bad Request**: Missing email or password
- **401 Unauthorized**: Invalid credentials

**Validation**:
- `email`: required, valid email format
- `password`: required

---

### POST /api/auth/signout

Sign out the current user and invalidate session.

**Headers**:
```
Authorization: Bearer eyJhbGc...
```

**Request**: Empty body

**Response** (200 OK):
```json
{
  "success": true
}
```

**Errors**:
- **401 Unauthorized**: Invalid or missing token

---

### GET /api/auth/session

Get current user session information.

**Headers**:
```
Authorization: Bearer eyJhbGc...
```

**Response** (200 OK):
```json
{
  "user": {
    "id": "user_clp1234567890",
    "email": "user@example.com",
    "name": "John Doe",
    "emailVerified": false,
    "image": null
  },
  "session": {
    "expiresAt": "2025-01-04T10:00:00.000Z"
  }
}
```

**Errors**:
- **401 Unauthorized**: Invalid or expired token

---

## Task Endpoints

### GET /api/tasks

List all tasks for the authenticated user.

**Headers**:
```
Authorization: Bearer eyJhbGc...
```

**Query Parameters**: None (Basic Level)

**Response** (200 OK):
```json
[
  {
    "id": 1,
    "userId": "user_clp1234567890",
    "title": "Buy groceries",
    "description": "Milk, eggs, bread",
    "completed": false,
    "createdAt": "2024-12-28T10:30:00.000Z",
    "updatedAt": "2024-12-28T10:30:00.000Z"
  },
  {
    "id": 2,
    "userId": "user_clp1234567890",
    "title": "Finish homework",
    "description": "Math assignment pages 10-15",
    "completed": true,
    "createdAt": "2024-12-27T14:00:00.000Z",
    "updatedAt": "2024-12-28T09:15:00.000Z"
  }
]
```

**Empty Response** (no tasks):
```json
[]
```

**Errors**:
- **401 Unauthorized**: Invalid or missing token

**Behavior**:
- Returns only tasks where `userId` matches authenticated user
- Ordered by `createdAt` descending (newest first)
- Empty array if user has no tasks

---

### POST /api/tasks

Create a new task for the authenticated user.

**Headers**:
```
Authorization: Bearer eyJhbGc...
Content-Type: application/json
```

**Request**:
```json
{
  "title": "Buy groceries",
  "description": "Milk, eggs, bread"  // optional
}
```

**Response** (201 Created):
```json
{
  "id": 1,
  "userId": "user_clp1234567890",
  "title": "Buy groceries",
  "description": "Milk, eggs, bread",
  "completed": false,
  "createdAt": "2024-12-28T10:30:00.000Z",
  "updatedAt": "2024-12-28T10:30:00.000Z"
}
```

**Errors**:
- **400 Bad Request**: Validation error (see details below)
- **401 Unauthorized**: Invalid or missing token
- **422 Unprocessable Entity**: Validation error with field details

**Validation**:
- `title`: required, min 1 char, max 200 chars, trimmed
- `description`: optional, max 1000 chars, trimmed

**Example Validation Error** (422):
```json
{
  "detail": [
    {
      "loc": ["body", "title"],
      "msg": "ensure this value has at least 1 character",
      "type": "value_error.any_str.min_length"
    }
  ]
}
```

**Behavior**:
- `userId` automatically set from JWT token (user cannot override)
- `completed` defaults to `false`
- `createdAt` and `updatedAt` auto-generated
- `description` can be `null` or empty string

---

### GET /api/tasks/{id}

Get a single task by ID.

**Headers**:
```
Authorization: Bearer eyJhbGc...
```

**Path Parameters**:
- `id` (integer): Task ID

**Response** (200 OK):
```json
{
  "id": 1,
  "userId": "user_clp1234567890",
  "title": "Buy groceries",
  "description": "Milk, eggs, bread",
  "completed": false,
  "createdAt": "2024-12-28T10:30:00.000Z",
  "updatedAt": "2024-12-28T10:30:00.000Z"
}
```

**Errors**:
- **401 Unauthorized**: Invalid or missing token
- **404 Not Found**: Task doesn't exist or doesn't belong to user

**Behavior**:
- Only returns task if `userId` matches authenticated user
- Returns 404 if task exists but belongs to another user (don't reveal existence)

---

### PUT /api/tasks/{id}

Update a task's title and/or description.

**Headers**:
```
Authorization: Bearer eyJhbGc...
Content-Type: application/json
```

**Path Parameters**:
- `id` (integer): Task ID

**Request**:
```json
{
  "title": "Buy groceries and snacks",
  "description": "Milk, eggs, bread, chips"
}
```

**Response** (200 OK):
```json
{
  "id": 1,
  "userId": "user_clp1234567890",
  "title": "Buy groceries and snacks",
  "description": "Milk, eggs, bread, chips",
  "completed": false,
  "createdAt": "2024-12-28T10:30:00.000Z",
  "updatedAt": "2024-12-28T11:45:00.000Z"
}
```

**Errors**:
- **400 Bad Request**: Validation error
- **401 Unauthorized**: Invalid or missing token
- **404 Not Found**: Task doesn't exist or doesn't belong to user
- **422 Unprocessable Entity**: Validation error with field details

**Validation**:
- `title`: required, min 1 char, max 200 chars, trimmed
- `description`: optional, max 1000 chars, trimmed

**Behavior**:
- Only updates task if `userId` matches authenticated user
- `updatedAt` automatically set to current timestamp
- `completed` status NOT changed (use PATCH endpoint)
- Cannot change `userId` (ignored if provided)

---

### PATCH /api/tasks/{id}/complete

Toggle task completion status.

**Headers**:
```
Authorization: Bearer eyJhbGc...
```

**Path Parameters**:
- `id` (integer): Task ID

**Request**: Empty body (toggle is automatic)

**Response** (200 OK):
```json
{
  "id": 1,
  "userId": "user_clp1234567890",
  "title": "Buy groceries",
  "description": "Milk, eggs, bread",
  "completed": true,  // toggled from false
  "createdAt": "2024-12-28T10:30:00.000Z",
  "updatedAt": "2024-12-28T12:00:00.000Z"
}
```

**Errors**:
- **401 Unauthorized**: Invalid or missing token
- **404 Not Found**: Task doesn't exist or doesn't belong to user

**Behavior**:
- If `completed` was `false`, set to `true`
- If `completed` was `true`, set to `false`
- Only updates task if `userId` matches authenticated user
- `updatedAt` automatically set to current timestamp
- Title and description NOT changed

---

### DELETE /api/tasks/{id}

Delete a task permanently.

**Headers**:
```
Authorization: Bearer eyJhbGc...
```

**Path Parameters**:
- `id` (integer): Task ID

**Request**: Empty body

**Response** (204 No Content):
Empty body (success indicated by status code)

**Errors**:
- **401 Unauthorized**: Invalid or missing token
- **404 Not Found**: Task doesn't exist or doesn't belong to user

**Behavior**:
- Only deletes task if `userId` matches authenticated user
- Deletion is permanent (no soft delete, no undo)
- Returns 204 even if task was already deleted (idempotent)

---

## Error Response Format

All error responses follow this format:

**Simple Error**:
```json
{
  "detail": "Error message here"
}
```

**Validation Error** (422):
```json
{
  "detail": [
    {
      "loc": ["body", "fieldName"],
      "msg": "Human-readable error message",
      "type": "error_type"
    }
  ]
}
```

## HTTP Status Codes

| Code | Meaning | Usage |
|------|---------|-------|
| 200 | OK | Successful GET, PUT, PATCH |
| 201 | Created | Successful POST (resource created) |
| 204 | No Content | Successful DELETE |
| 400 | Bad Request | Invalid input data |
| 401 | Unauthorized | Missing or invalid authentication |
| 404 | Not Found | Resource doesn't exist or user doesn't own it |
| 409 | Conflict | Resource already exists (duplicate email) |
| 422 | Unprocessable Entity | Validation error with details |
| 500 | Internal Server Error | Server-side error |

## CORS Configuration

**Allowed Origins**: `http://localhost:3000` (development)
**Allowed Methods**: `GET, POST, PUT, PATCH, DELETE, OPTIONS`
**Allowed Headers**: `Content-Type, Authorization`
**Allow Credentials**: `true` (for cookies, if used)

**Preflight Request** (OPTIONS):
All endpoints support OPTIONS for CORS preflight.

```
OPTIONS /api/tasks
Origin: http://localhost:3000

Response:
Access-Control-Allow-Origin: http://localhost:3000
Access-Control-Allow-Methods: GET, POST, PUT, PATCH, DELETE
Access-Control-Allow-Headers: Content-Type, Authorization
Access-Control-Max-Age: 86400
```

## Rate Limiting

**Phase II Basic Level**: No rate limiting implemented.

**Future Enhancement**:
- Auth endpoints: 5 requests/minute per IP
- Task endpoints: 100 requests/minute per user

## Pagination

**Phase II Basic Level**: No pagination implemented (all tasks returned).

**Future Enhancement**:
- Query params: `?page=1&limit=20`
- Response headers: `X-Total-Count`, `X-Page`, `X-Per-Page`

## Filtering & Sorting

**Phase II Basic Level**: No filtering or sorting (except default: newest first).

**Future Enhancement**:
- Filter: `?status=completed`, `?status=pending`
- Sort: `?sort=created_at`, `?sort=title`, `?order=asc`

## API Versioning

**Current**: No versioning (breaking changes allowed in Basic Level)

**Future Enhancement**: `/api/v1/tasks`, `/api/v2/tasks`

## Request/Response Headers

### Common Request Headers
```
Authorization: Bearer eyJhbGciOiJIUzI1NiIs...
Content-Type: application/json
Accept: application/json
```

### Common Response Headers
```
Content-Type: application/json
X-Request-ID: abc123def456  // for debugging (future)
```

## Security Considerations

### JWT Token Security
- ✅ Tokens signed with HS256 algorithm
- ✅ Secret key stored in environment variable
- ✅ Tokens expire after 7 days
- ✅ Signature verified on every request
- ✅ User ID extracted from `sub` claim

### User Isolation
- ✅ All task queries filtered by `userId` from JWT
- ✅ Users cannot access other users' tasks
- ✅ 404 returned (not 403) to avoid revealing task existence

### Input Validation
- ✅ All inputs validated with Pydantic
- ✅ SQL injection prevented (SQLModel ORM)
- ✅ XSS prevention (no HTML rendering on backend)
- ✅ Max length limits enforced

### Password Security
- ✅ Passwords hashed with bcrypt (Better Auth)
- ✅ Never returned in API responses
- ✅ Never logged

## Testing Checklist

### Authentication
- [ ] POST /signup creates user and returns token
- [ ] POST /signup rejects duplicate email (409)
- [ ] POST /signup validates email format
- [ ] POST /signup validates password length
- [ ] POST /signin returns token for valid credentials
- [ ] POST /signin rejects invalid credentials (401)
- [ ] GET /session returns user for valid token
- [ ] GET /session rejects invalid token (401)
- [ ] POST /signout invalidates token

### Task CRUD
- [ ] GET /tasks returns only current user's tasks
- [ ] GET /tasks returns empty array for new user
- [ ] POST /tasks creates task with correct userId
- [ ] POST /tasks rejects invalid title (422)
- [ ] POST /tasks accepts missing description
- [ ] GET /tasks/{id} returns task for owner
- [ ] GET /tasks/{id} returns 404 for other user's task
- [ ] PUT /tasks/{id} updates task for owner
- [ ] PUT /tasks/{id} returns 404 for other user's task
- [ ] PATCH /tasks/{id}/complete toggles status
- [ ] DELETE /tasks/{id} deletes task for owner
- [ ] DELETE /tasks/{id} returns 404 for other user's task

### Security
- [ ] All task endpoints reject requests without token (401)
- [ ] All task endpoints reject expired token (401)
- [ ] All task endpoints reject tampered token (401)
- [ ] User A cannot see User B's tasks
- [ ] User A cannot modify User B's tasks
- [ ] User A cannot delete User B's tasks

## API Client Example (Frontend)

```typescript
// lib/api.ts
const API_URL = process.env.NEXT_PUBLIC_API_URL

async function getAuthToken(): Promise<string> {
  const session = await auth.getSession()
  if (!session?.token) {
    throw new Error('Not authenticated')
  }
  return session.token
}

export const api = {
  async getTasks() {
    const token = await getAuthToken()
    const res = await fetch(`${API_URL}/api/tasks`, {
      headers: { 'Authorization': `Bearer ${token}` }
    })
    if (!res.ok) throw new Error('Failed to fetch tasks')
    return res.json()
  },

  async createTask(data: { title: string; description?: string }) {
    const token = await getAuthToken()
    const res = await fetch(`${API_URL}/api/tasks`, {
      method: 'POST',
      headers: {
        'Authorization': `Bearer ${token}`,
        'Content-Type': 'application/json'
      },
      body: JSON.stringify(data)
    })
    if (!res.ok) throw new Error('Failed to create task')
    return res.json()
  },

  async updateTask(id: number, data: { title: string; description?: string }) {
    const token = await getAuthToken()
    const res = await fetch(`${API_URL}/api/tasks/${id}`, {
      method: 'PUT',
      headers: {
        'Authorization': `Bearer ${token}`,
        'Content-Type': 'application/json'
      },
      body: JSON.stringify(data)
    })
    if (!res.ok) throw new Error('Failed to update task')
    return res.json()
  },

  async toggleComplete(id: number) {
    const token = await getAuthToken()
    const res = await fetch(`${API_URL}/api/tasks/${id}/complete`, {
      method: 'PATCH',
      headers: { 'Authorization': `Bearer ${token}` }
    })
    if (!res.ok) throw new Error('Failed to toggle task')
    return res.json()
  },

  async deleteTask(id: number) {
    const token = await getAuthToken()
    const res = await fetch(`${API_URL}/api/tasks/${id}`, {
      method: 'DELETE',
      headers: { 'Authorization': `Bearer ${token}` }
    })
    if (!res.ok) throw new Error('Failed to delete task')
  }
}
```

## Document History

| Version | Date | Changes |
|---------|------|---------|
| 1.0 | 2024-12-28 | Initial REST API specification for Phase II |
