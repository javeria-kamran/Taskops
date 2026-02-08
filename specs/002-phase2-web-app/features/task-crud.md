# Feature: Task CRUD Operations (Phase II)

## Overview

**Feature ID**: `task-crud-web`
**Phase**: II - Web Application
**Priority**: P0 (Critical)
**Dependencies**: `authentication` (users must be logged in)

Implement the 5 Basic Level task management operations as a web application with persistent storage and multi-user support.

## User Stories

### 1. Create Task
**As a** logged-in user
**I want to** create a new task with a title and optional description
**So that** I can track things I need to do

**Acceptance Criteria**:
- ✅ User can access task creation form
- ✅ Title field is required (1-200 characters)
- ✅ Description field is optional (max 1000 characters)
- ✅ Form validates input before submission
- ✅ Task is saved to database with `user_id`
- ✅ Task appears in task list immediately after creation
- ✅ User sees success feedback
- ✅ Form clears after successful creation

### 2. View Tasks
**As a** logged-in user
**I want to** see a list of all my tasks
**So that** I can review what I need to do

**Acceptance Criteria**:
- ✅ User sees only their own tasks (not other users' tasks)
- ✅ Each task displays: title, description, completion status, creation date
- ✅ Tasks are ordered by creation date (newest first)
- ✅ Empty state shown when user has no tasks
- ✅ Loading state shown while fetching tasks
- ✅ Error state shown if fetch fails

### 3. Update Task
**As a** logged-in user
**I want to** edit a task's title or description
**So that** I can correct mistakes or add details

**Acceptance Criteria**:
- ✅ User can click/tap to edit any of their tasks
- ✅ Edit form pre-fills with current task data
- ✅ Title field is required (1-200 characters)
- ✅ Description field is optional (max 1000 characters)
- ✅ Changes are saved to database
- ✅ Task list updates immediately after save
- ✅ User can cancel editing without saving
- ✅ User sees success feedback after save

### 4. Delete Task
**As a** logged-in user
**I want to** delete a task I no longer need
**So that** my task list stays clean

**Acceptance Criteria**:
- ✅ User can click/tap delete button on any of their tasks
- ✅ Confirmation dialog appears before deletion
- ✅ User can confirm or cancel deletion
- ✅ Task is removed from database upon confirmation
- ✅ Task disappears from list immediately after deletion
- ✅ User sees success feedback
- ✅ Deletion is permanent (no undo in Basic Level)

### 5. Toggle Task Completion
**As a** logged-in user
**I want to** mark tasks as complete or incomplete
**So that** I can track my progress

**Acceptance Criteria**:
- ✅ User can click/tap checkbox to toggle completion status
- ✅ Completed tasks show visual indication (strikethrough, checkmark)
- ✅ Status change is saved to database immediately
- ✅ UI updates optimistically (no reload needed)
- ✅ User can toggle between complete/incomplete multiple times
- ✅ Status persists across browser sessions

## Functional Requirements

### Task Entity
```typescript
interface Task {
  id: number              // Auto-generated primary key
  userId: string          // Foreign key to users table
  title: string           // Required, 1-200 chars
  description: string     // Optional, max 1000 chars
  completed: boolean      // Default: false
  createdAt: Date         // Auto-generated
  updatedAt: Date         // Auto-updated on changes
}
```

### Validation Rules

**Title**:
- ✅ Required
- ✅ Minimum 1 character
- ✅ Maximum 200 characters
- ✅ No leading/trailing whitespace (auto-trimmed)
- ❌ Cannot be only whitespace

**Description**:
- ✅ Optional
- ✅ Maximum 1000 characters
- ✅ Can be empty string or null
- ✅ No leading/trailing whitespace (auto-trimmed)

**User Isolation**:
- ✅ Every task must belong to a user
- ✅ Users can only see their own tasks
- ✅ Users cannot modify other users' tasks
- ✅ Enforced at both API and database level

### Business Logic

**Create**:
1. Validate JWT token → extract `user_id`
2. Validate title and description
3. Set `completed = false`
4. Set `user_id` from JWT
5. Insert into database
6. Return created task

**Read**:
1. Validate JWT token → extract `user_id`
2. Query tasks WHERE `user_id = current_user`
3. Order by `created_at DESC`
4. Return task list

**Update**:
1. Validate JWT token → extract `user_id`
2. Validate title and description
3. Verify task exists and belongs to current user
4. Update title and/or description
5. Set `updated_at = NOW()`
6. Return updated task

**Delete**:
1. Validate JWT token → extract `user_id`
2. Verify task exists and belongs to current user
3. Delete from database
4. Return success status

**Toggle Completion**:
1. Validate JWT token → extract `user_id`
2. Verify task exists and belongs to current user
3. Toggle `completed` field
4. Set `updated_at = NOW()`
5. Return updated task

## UI/UX Requirements

### Task List Page

**Layout**:
```
┌──────────────────────────────────────────────────┐
│  [Logo]  My Tasks                    [Logout]    │
├──────────────────────────────────────────────────┤
│                                                   │
│  ┌──────────────────────────────────────────┐    │
│  │  Add New Task                            │    │
│  │  Title: [_________________________]      │    │
│  │  Description (optional):                 │    │
│  │  [________________________________]      │    │
│  │                        [Add Task] button │    │
│  └──────────────────────────────────────────┘    │
│                                                   │
│  ┌──────────────────────────────────────────┐    │
│  │ ☐ Buy groceries                    [Edit]│    │
│  │   Get milk, eggs, bread            [Del] │    │
│  │   Created: 2 hours ago                   │    │
│  └──────────────────────────────────────────┘    │
│                                                   │
│  ┌──────────────────────────────────────────┐    │
│  │ ☑ Finish homework                  [Edit]│    │
│  │   Math assignment pages 10-15      [Del] │    │
│  │   Created: 1 day ago                     │    │
│  └──────────────────────────────────────────┘    │
│                                                   │
└──────────────────────────────────────────────────┘
```

**Responsive Behavior**:
- **Desktop** (>768px): Two-column layout (form left, tasks right)
- **Mobile** (<768px): Stacked layout (form top, tasks below)

### Visual States

**Task Item States**:
1. **Incomplete**:
   - Empty checkbox
   - Normal text weight
   - Full opacity

2. **Complete**:
   - Checked checkbox (✓)
   - Strikethrough text
   - Reduced opacity (60%)

3. **Hover** (desktop):
   - Subtle background color
   - Show edit/delete buttons

4. **Loading**:
   - Skeleton loaders for tasks
   - Disabled form during submission

5. **Error**:
   - Red border on form fields
   - Error message below field
   - Toast notification for API errors

### Interactions

**Create Task**:
1. User types in title and description
2. User clicks "Add Task" or presses Enter
3. Form validates input
4. API request sent with loading spinner
5. On success: form clears, task appears at top of list, success toast
6. On error: error message shown, form stays filled

**Edit Task**:
1. User clicks "Edit" button
2. Inline edit form appears OR modal opens
3. User modifies title/description
4. User clicks "Save" or "Cancel"
5. On save: API request sent, task updates in list
6. On cancel: form closes, no changes made

**Delete Task**:
1. User clicks "Delete" button
2. Confirmation dialog appears: "Delete this task? This cannot be undone."
3. User clicks "Confirm" or "Cancel"
4. On confirm: API request sent, task fades out and disappears
5. On cancel: dialog closes, no action taken

**Toggle Completion**:
1. User clicks checkbox
2. Checkbox state changes immediately (optimistic update)
3. API request sent in background
4. On error: revert checkbox state, show error toast

## API Integration

### Endpoints Used

| Method | Endpoint | Purpose |
|--------|----------|---------|
| GET | `/api/tasks` | Fetch all user's tasks |
| POST | `/api/tasks` | Create new task |
| GET | `/api/tasks/{id}` | Get single task (for edit form) |
| PUT | `/api/tasks/{id}` | Update task title/description |
| PATCH | `/api/tasks/{id}/complete` | Toggle completion status |
| DELETE | `/api/tasks/{id}` | Delete task |

### Request/Response Examples

**Create Task**:
```typescript
// Request
POST /api/tasks
Authorization: Bearer eyJhbGc...
Content-Type: application/json

{
  "title": "Buy groceries",
  "description": "Milk, eggs, bread"
}

// Response (201 Created)
{
  "id": 42,
  "userId": "user_abc123",
  "title": "Buy groceries",
  "description": "Milk, eggs, bread",
  "completed": false,
  "createdAt": "2024-12-28T10:30:00Z",
  "updatedAt": "2024-12-28T10:30:00Z"
}
```

**Get Tasks**:
```typescript
// Request
GET /api/tasks
Authorization: Bearer eyJhbGc...

// Response (200 OK)
[
  {
    "id": 42,
    "userId": "user_abc123",
    "title": "Buy groceries",
    "description": "Milk, eggs, bread",
    "completed": false,
    "createdAt": "2024-12-28T10:30:00Z",
    "updatedAt": "2024-12-28T10:30:00Z"
  },
  {
    "id": 41,
    "userId": "user_abc123",
    "title": "Finish homework",
    "description": "Math assignment",
    "completed": true,
    "createdAt": "2024-12-27T14:20:00Z",
    "updatedAt": "2024-12-28T09:15:00Z"
  }
]
```

**Update Task**:
```typescript
// Request
PUT /api/tasks/42
Authorization: Bearer eyJhbGc...
Content-Type: application/json

{
  "title": "Buy groceries and snacks",
  "description": "Milk, eggs, bread, chips"
}

// Response (200 OK)
{
  "id": 42,
  "userId": "user_abc123",
  "title": "Buy groceries and snacks",
  "description": "Milk, eggs, bread, chips",
  "completed": false,
  "createdAt": "2024-12-28T10:30:00Z",
  "updatedAt": "2024-12-28T11:45:00Z"
}
```

**Toggle Completion**:
```typescript
// Request
PATCH /api/tasks/42/complete
Authorization: Bearer eyJhbGc...

// Response (200 OK)
{
  "id": 42,
  "userId": "user_abc123",
  "title": "Buy groceries and snacks",
  "description": "Milk, eggs, bread, chips",
  "completed": true,  // toggled
  "createdAt": "2024-12-28T10:30:00Z",
  "updatedAt": "2024-12-28T12:00:00Z"
}
```

**Delete Task**:
```typescript
// Request
DELETE /api/tasks/42
Authorization: Bearer eyJhbGc...

// Response (204 No Content)
// Empty body
```

### Error Responses

**Validation Error (422)**:
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

**Unauthorized (401)**:
```json
{
  "detail": "Invalid or expired token"
}
```

**Not Found (404)**:
```json
{
  "detail": "Task not found or does not belong to user"
}
```

## Testing Requirements

### Frontend Tests

**Component Tests**:
- Task list renders correctly
- Task form validates input
- Task item shows correct status
- Edit/delete buttons appear on hover

**Integration Tests**:
- Create task flow (form → API → list update)
- Edit task flow (click edit → modify → save)
- Delete task flow (click delete → confirm → removal)
- Toggle completion flow (click checkbox → API → UI update)

### Backend Tests

**Unit Tests**:
- Task validation (title length, description length)
- User isolation (can't access other users' tasks)

**API Tests**:
- GET /api/tasks returns only current user's tasks
- POST /api/tasks creates task with correct user_id
- PUT /api/tasks/{id} updates only if user owns task
- DELETE /api/tasks/{id} deletes only if user owns task
- PATCH /api/tasks/{id}/complete toggles status
- All endpoints return 401 without valid JWT

### E2E Tests

**Critical Paths**:
1. Login → Create task → Verify in list
2. Login → Edit task → Verify changes
3. Login → Delete task → Verify removal
4. Login → Toggle task → Verify status change
5. Login as User A → Create task → Login as User B → Verify task not visible

## Performance Requirements

- Task list loads within 500ms
- Create/update/delete operations complete within 300ms
- UI responds to clicks within 100ms (optimistic updates)
- No page refresh required for any operation

## Accessibility Requirements

- All interactive elements keyboard navigable
- Checkboxes have proper labels
- Form fields have clear labels and error messages
- Screen reader announcements for task creation/deletion
- Color contrast ratio meets WCAG AA (4.5:1)

## Out of Scope (Phase II Basic Level)

The following are NOT included in Basic Level:
- ❌ Task filtering (show all / active / completed)
- ❌ Task sorting (by date, title, status)
- ❌ Task search
- ❌ Task categories or tags
- ❌ Task due dates
- ❌ Task priorities
- ❌ Task sharing between users
- ❌ Bulk operations (delete all, mark all complete)
- ❌ Drag-and-drop reordering
- ❌ Undo/redo

These may be added in future phases or as enhancements.

## Migration from Phase I

### Code Reuse

**Phase I → Phase II Mapping**:

| Phase I | Phase II | Changes |
|---------|----------|---------|
| `src/models/task.py` (dataclass) | `backend/app/models/task.py` (SQLModel) | Add SQLModel fields, relationships |
| `src/services/task_manager.py` (dict storage) | `backend/app/routes/tasks.py` (database) | Replace dict with SQL queries |
| Validation in `src/lib/validators.py` | Pydantic schemas in `backend/app/schemas/task.py` | Port validation logic |
| No user concept | Add `user_id` to all operations | New field, filtering |

### Validation Preservation

Keep these validation rules from Phase I:
- Title length (1-200)
- Description length (max 1000)
- Whitespace trimming

Add these new validations:
- User ownership verification
- JWT token validation

## Success Metrics

- ✅ All 5 CRUD operations functional via web UI
- ✅ User isolation enforced (100% of queries filtered by user_id)
- ✅ >80% test coverage on backend task routes
- ✅ All acceptance criteria passing
- ✅ Zero data leaks between users in testing

## Document History

| Version | Date | Changes |
|---------|------|---------|
| 1.0 | 2024-12-28 | Initial task CRUD specification for Phase II |
