# Tasks: Phase II Web Application

**Input**: Design documents from `/specs/002-phase2-web-app/`
**Prerequisites**: plan.md, overview.md, architecture.md, features/, api/, database/, ui/

**Tests**: Tests are included as this is a production-grade application requiring >80% coverage per constitution

**Organization**: Tasks are grouped by user story to enable independent implementation and testing of each story

## Format: `[ID] [P?] [Story] Description`

- **[P]**: Can run in parallel (different files, no dependencies)
- **[Story]**: Which user story this task belongs to (e.g., US1, US2, US3)
- Include exact file paths in descriptions

## Path Conventions

- **Backend**: `backend/app/`, `backend/tests/`
- **Frontend**: `frontend/app/`, `frontend/components/`, `frontend/__tests__/`
- **Root**: `docker-compose.yml`, `.env.example`

---

## Phase 1: Setup (Shared Infrastructure)

**Purpose**: Project initialization and basic structure

- [x] T001 Create backend directory structure per plan.md (app/, tests/, alembic/)
- [x] T002 Create frontend directory structure per plan.md (app/, components/, lib/, types/)
- [x] T003 Initialize Python project with UV in backend/ directory
- [x] T004 [P] Create backend/requirements.txt with FastAPI, SQLModel, Alembic, python-jose, passlib, asyncpg
- [x] T005 [P] Create backend/requirements-dev.txt with pytest, pytest-cov, pytest-asyncio, httpx
- [x] T006 [P] Initialize Next.js project in frontend/ with TypeScript and Tailwind CSS
- [x] T007 [P] Add Better Auth and required dependencies to frontend/package.json
- [x] T008 Create root .env.example with all required environment variables
- [x] T009 Create backend/.env.example with DATABASE_URL, BETTER_AUTH_SECRET, ALLOWED_ORIGINS
- [x] T010 Create frontend/.env.local.example with BETTER_AUTH_SECRET, DATABASE_URL, NEXT_PUBLIC_API_URL
- [x] T011 [P] Create backend/Dockerfile for FastAPI container
- [x] T012 [P] Create frontend/Dockerfile for Next.js container
- [x] T013 Create docker-compose.yml for development environment (frontend + backend services)
- [x] T014 [P] Create docker-compose.prod.yml for production environment
- [x] T015 [P] Configure ESLint and Prettier for frontend in frontend/.eslintrc.json
- [x] T016 [P] Configure Python linting (ruff/black) for backend in backend/pyproject.toml

**Checkpoint**: Project structure and configuration files ready

---

## Phase 2: Foundational (Blocking Prerequisites)

**Purpose**: Core infrastructure that MUST be complete before ANY user story can be implemented

**⚠️ CRITICAL**: No user story work can begin until this phase is complete

- [x] T017 Setup SQLModel database connection in backend/app/database.py with async PostgreSQL
- [x] T018 Create backend/app/config.py for environment variable management using pydantic BaseSettings
- [x] T019 Initialize Alembic in backend/alembic/ for database migrations
- [x] T020 Configure Alembic env.py to use SQLModel metadata and async engine
- [x] T021 Create FastAPI app instance in backend/app/main.py with CORS middleware
- [x] T022 Configure CORS middleware in backend/app/middleware/cors.py using ALLOWED_ORIGINS
- [x] T023 Create base response schemas in backend/app/schemas/__init__.py (ErrorResponse, SuccessResponse)
- [x] T024 Create backend/app/dependencies/__init__.py for dependency injection utilities
- [x] T025 Setup pytest configuration in backend/tests/conftest.py with async fixtures
- [x] T026 Create test database session fixture in backend/tests/conftest.py
- [x] T027 Setup Next.js root layout in frontend/app/layout.tsx with Tailwind CSS
- [x] T028 Create frontend/lib/utils.ts with common utility functions (cn, formatDate, etc.)
- [x] T029 [P] Create base UI components in frontend/components/ui/ (button.tsx, input.tsx, card.tsx, dialog.tsx)
- [x] T030 Create frontend/types/__init__.ts for shared TypeScript types
- [x] T031 Create error boundary component in frontend/app/error.tsx
- [x] T032 Create loading component in frontend/app/loading.tsx

**Checkpoint**: Foundation ready - user story implementation can now begin in parallel

---

## Phase 3: User Story 1 - User Authentication (Priority: P0) 🎯 FOUNDATIONAL

**Goal**: Enable users to sign up, sign in, and manage sessions with Better Auth and JWT tokens

**Independent Test**: User can sign up with email/password, sign in to receive JWT, and access protected routes

### Tests for User Story 1 (Backend)

> **NOTE: Write these tests FIRST, ensure they FAIL before implementation**

- [ ] T033 [P] [US1] Create backend/tests/test_auth.py with fixture for test user creation
- [ ] T034 [P] [US1] Write test for JWT token generation in backend/tests/test_auth.py
- [ ] T035 [P] [US1] Write test for JWT token verification in backend/tests/test_auth.py
- [ ] T036 [P] [US1] Write test for invalid token handling in backend/tests/test_auth.py

### Implementation for User Story 1 (Backend)

- [ ] T037 [US1] Create User SQLModel in backend/app/models/user.py (id, email, name, emailVerified, createdAt, updatedAt)
- [ ] T038 [US1] Create Alembic migration for users table in backend/alembic/versions/001_create_users_table.py
- [ ] T039 [US1] Run migration to create users table in Neon database
- [ ] T040 [US1] Create UserCreate schema in backend/app/schemas/user.py (email, password validation)
- [ ] T041 [US1] Create UserResponse schema in backend/app/schemas/user.py (excludes password)
- [ ] T042 [US1] Implement JWT token creation function in backend/app/dependencies/auth.py using python-jose
- [ ] T043 [US1] Implement JWT token verification function in backend/app/dependencies/auth.py
- [ ] T044 [US1] Create get_current_user dependency in backend/app/dependencies/auth.py for route protection
- [ ] T045 [US1] Implement auth middleware in backend/app/middleware/auth.py for JWT verification
- [ ] T046 [US1] Add auth middleware to FastAPI app in backend/app/main.py

### Implementation for User Story 1 (Frontend)

- [ ] T047 [P] [US1] Configure Better Auth in frontend/lib/auth.ts with JWT settings and database connection
- [ ] T048 [P] [US1] Create Better Auth API route handler in frontend/app/api/auth/[...all]/route.ts
- [ ] T049 [P] [US1] Create User TypeScript interface in frontend/types/user.ts
- [ ] T050 [P] [US1] Create signup form component in frontend/components/auth/signup-form.tsx
- [ ] T051 [P] [US1] Create signin form component in frontend/components/auth/signin-form.tsx
- [ ] T052 [US1] Create signup page in frontend/app/(auth)/signup/page.tsx
- [ ] T053 [US1] Create signin page in frontend/app/(auth)/signin/page.tsx
- [ ] T054 [US1] Create auth guard component in frontend/components/auth/auth-guard.tsx for protected routes
- [ ] T055 [US1] Create protected app layout in frontend/app/(app)/layout.tsx with auth guard
- [ ] T056 [US1] Add signout functionality to app layout navigation in frontend/app/(app)/layout.tsx

### Tests for User Story 1 (Frontend)

- [ ] T057 [P] [US1] Write signup form test in frontend/__tests__/components/signup-form.test.tsx
- [ ] T058 [P] [US1] Write signin form test in frontend/__tests__/components/signin-form.test.tsx
- [ ] T059 [P] [US1] Write auth guard test in frontend/__tests__/components/auth-guard.test.tsx

**Checkpoint**: At this point, authentication should be fully functional - users can sign up, sign in, and access protected routes

---

## Phase 4: User Story 2 - Create Task (Priority: P1) 🎯 MVP Core

**Goal**: Authenticated users can create new tasks with title and optional description

**Independent Test**: After signing in, user can fill task form, submit, and see task appear in database

### Tests for User Story 2 (Backend)

- [ ] T060 [P] [US2] Write POST /api/tasks endpoint test in backend/tests/test_tasks.py
- [ ] T061 [P] [US2] Write task validation test (title required, length limits) in backend/tests/test_tasks.py
- [ ] T062 [P] [US2] Write user isolation test (task has user_id) in backend/tests/test_tasks.py

### Implementation for User Story 2 (Backend)

- [ ] T063 [US2] Create Task SQLModel in backend/app/models/task.py (id, userId, title, description, completed, createdAt, updatedAt)
- [ ] T064 [US2] Create Alembic migration for tasks table in backend/alembic/versions/002_create_tasks_table.py with FK to users
- [ ] T065 [US2] Run migration to create tasks table in Neon database
- [ ] T066 [US2] Create TaskCreate schema in backend/app/schemas/task.py with validation (title 1-200 chars, description max 1000)
- [ ] T067 [US2] Create TaskResponse schema in backend/app/schemas/task.py
- [ ] T068 [US2] Implement POST /api/tasks endpoint in backend/app/routes/tasks.py with user_id injection
- [ ] T069 [US2] Add tasks router to FastAPI app in backend/app/main.py

### Implementation for User Story 2 (Frontend)

- [ ] T070 [P] [US2] Create Task TypeScript interface in frontend/types/task.ts
- [ ] T071 [P] [US2] Create API client function for task creation in frontend/lib/api.ts
- [ ] T072 [P] [US2] Create task form component in frontend/components/tasks/task-form.tsx with validation
- [ ] T073 [US2] Create new task page in frontend/app/(app)/tasks/new/page.tsx

### Tests for User Story 2 (Frontend)

- [ ] T074 [P] [US2] Write task form validation test in frontend/__tests__/components/task-form.test.tsx
- [ ] T075 [P] [US2] Write task creation flow test in frontend/__tests__/components/task-form.test.tsx

**Checkpoint**: Users can successfully create tasks that are persisted to database with user isolation

---

## Phase 5: User Story 3 - View Tasks (Priority: P1) 🎯 MVP Core

**Goal**: Authenticated users can view a list of all their tasks (not other users' tasks)

**Independent Test**: User sees only their own tasks ordered by creation date, with empty state if no tasks

### Tests for User Story 3 (Backend)

- [ ] T076 [P] [US3] Write GET /api/tasks endpoint test in backend/tests/test_tasks.py
- [ ] T077 [P] [US3] Write user isolation test (can't see other users' tasks) in backend/tests/test_tasks.py
- [ ] T078 [P] [US3] Write task ordering test (newest first) in backend/tests/test_tasks.py

### Implementation for User Story 3 (Backend)

- [ ] T079 [US3] Implement GET /api/tasks endpoint in backend/app/routes/tasks.py filtered by user_id
- [ ] T080 [US3] Add query ordering by created_at DESC in GET /api/tasks endpoint

### Implementation for User Story 3 (Frontend)

- [ ] T081 [P] [US3] Create API client function for fetching tasks in frontend/lib/api.ts
- [ ] T082 [P] [US3] Create task item component in frontend/components/tasks/task-item.tsx
- [ ] T083 [P] [US3] Create task list component in frontend/components/tasks/task-list.tsx
- [ ] T084 [US3] Create tasks page in frontend/app/(app)/tasks/page.tsx with loading and empty states

### Tests for User Story 3 (Frontend)

- [ ] T085 [P] [US3] Write task list rendering test in frontend/__tests__/components/task-list.test.tsx
- [ ] T086 [P] [US3] Write empty state test in frontend/__tests__/components/task-list.test.tsx

**Checkpoint**: Users can view all their tasks in a responsive list with proper empty states

---

## Phase 6: User Story 4 - Update Task (Priority: P2)

**Goal**: Authenticated users can edit task title and description

**Independent Test**: User clicks edit on a task, modifies title/description, saves, and sees changes persist

### Tests for User Story 4 (Backend)

- [ ] T087 [P] [US4] Write PUT /api/tasks/{id} endpoint test in backend/tests/test_tasks.py
- [ ] T088 [P] [US4] Write test for updating non-existent task (404) in backend/tests/test_tasks.py
- [ ] T089 [P] [US4] Write test for updating other user's task (403 Forbidden) in backend/tests/test_tasks.py

### Implementation for User Story 4 (Backend)

- [ ] T090 [US4] Create TaskUpdate schema in backend/app/schemas/task.py (optional title and description)
- [ ] T091 [US4] Implement PUT /api/tasks/{id} endpoint in backend/app/routes/tasks.py with user_id check
- [ ] T092 [US4] Implement GET /api/tasks/{id} endpoint in backend/app/routes/tasks.py for single task retrieval

### Implementation for User Story 4 (Frontend)

- [ ] T093 [P] [US4] Create API client functions for task update and single task fetch in frontend/lib/api.ts
- [ ] T094 [P] [US4] Add edit mode to task form component in frontend/components/tasks/task-form.tsx
- [ ] T095 [US4] Create task edit page in frontend/app/(app)/tasks/[id]/page.tsx
- [ ] T096 [US4] Add edit button to task item component in frontend/components/tasks/task-item.tsx

### Tests for User Story 4 (Frontend)

- [ ] T097 [P] [US4] Write task edit form test in frontend/__tests__/components/task-form.test.tsx
- [ ] T098 [P] [US4] Write task update flow test in frontend/__tests__/components/task-form.test.tsx

**Checkpoint**: Users can successfully edit and update their tasks

---

## Phase 7: User Story 5 - Toggle Task Completion (Priority: P2)

**Goal**: Authenticated users can mark tasks as complete or incomplete

**Independent Test**: User clicks checkbox on task, status changes and persists across page reloads

### Tests for User Story 5 (Backend)

- [ ] T099 [P] [US5] Write PATCH /api/tasks/{id}/complete endpoint test in backend/tests/test_tasks.py
- [ ] T100 [P] [US5] Write test for toggling completion multiple times in backend/tests/test_tasks.py

### Implementation for User Story 5 (Backend)

- [ ] T101 [US5] Implement PATCH /api/tasks/{id}/complete endpoint in backend/app/routes/tasks.py
- [ ] T102 [US5] Add optimistic locking (updatedAt check) to prevent race conditions

### Implementation for User Story 5 (Frontend)

- [ ] T103 [P] [US5] Create API client function for toggling completion in frontend/lib/api.ts
- [ ] T104 [P] [US5] Add checkbox with completion handler to task item component in frontend/components/tasks/task-item.tsx
- [ ] T105 [US5] Add visual indication (strikethrough) for completed tasks in frontend/components/tasks/task-item.tsx
- [ ] T106 [US5] Implement optimistic UI update (update UI before API confirms) in task list component

### Tests for User Story 5 (Frontend)

- [ ] T107 [P] [US5] Write completion toggle test in frontend/__tests__/components/task-item.test.tsx
- [ ] T108 [P] [US5] Write visual state test (strikethrough) in frontend/__tests__/components/task-item.test.tsx

**Checkpoint**: Users can toggle task completion with immediate visual feedback

---

## Phase 8: User Story 6 - Delete Task (Priority: P3)

**Goal**: Authenticated users can delete tasks with confirmation

**Independent Test**: User clicks delete, sees confirmation dialog, confirms, and task is permanently removed

### Tests for User Story 6 (Backend)

- [ ] T109 [P] [US6] Write DELETE /api/tasks/{id} endpoint test in backend/tests/test_tasks.py
- [ ] T110 [P] [US6] Write test for deleting non-existent task (404) in backend/tests/test_tasks.py
- [ ] T111 [P] [US6] Write test for deleting other user's task (403 Forbidden) in backend/tests/test_tasks.py

### Implementation for User Story 6 (Backend)

- [ ] T112 [US6] Implement DELETE /api/tasks/{id} endpoint in backend/app/routes/tasks.py with user_id check

### Implementation for User Story 6 (Frontend)

- [ ] T113 [P] [US6] Create API client function for task deletion in frontend/lib/api.ts
- [ ] T114 [P] [US6] Create confirmation dialog component in frontend/components/ui/confirm-dialog.tsx
- [ ] T115 [US6] Add delete button with confirmation to task item component in frontend/components/tasks/task-item.tsx
- [ ] T116 [US6] Implement optimistic UI removal in task list component

### Tests for User Story 6 (Frontend)

- [ ] T117 [P] [US6] Write delete confirmation dialog test in frontend/__tests__/components/task-item.test.tsx
- [ ] T118 [P] [US6] Write task deletion flow test in frontend/__tests__/components/task-item.test.tsx

**Checkpoint**: All 5 Basic Level CRUD operations are complete and tested

---

## Phase 9: Polish & Cross-Cutting Concerns

**Purpose**: Improvements that affect multiple user stories and production readiness

### Error Handling & User Feedback

- [ ] T119 [P] Create toast notification system in frontend/components/ui/toast.tsx
- [ ] T120 [P] Add error handling to all API client functions in frontend/lib/api.ts
- [ ] T121 Add success/error toasts to all task operations (create, update, delete, toggle)
- [ ] T122 [P] Implement backend error response standardization in backend/app/middleware/error_handler.py
- [ ] T123 Add custom error handler to FastAPI app in backend/app/main.py

### Loading States & UX

- [ ] T124 [P] Add loading spinners to all async operations in task components
- [ ] T125 [P] Add skeleton loaders to task list in frontend/components/tasks/task-list.tsx
- [ ] T126 Add disabled states to forms during submission
- [ ] T127 [P] Implement form reset after successful operations

### Security Hardening

- [ ] T128 [P] Add rate limiting to auth endpoints in backend/app/middleware/rate_limit.py
- [ ] T129 [P] Add CSRF protection to all state-changing endpoints
- [ ] T130 Implement request ID tracking for debugging in backend/app/middleware/request_id.py
- [ ] T131 [P] Add security headers (HSTS, X-Frame-Options) in backend/app/middleware/security.py

### Performance Optimization

- [ ] T132 [P] Add database indexes for user_id, completed, created_at in migration
- [ ] T133 [P] Implement connection pooling configuration in backend/app/database.py
- [ ] T134 Add pagination to GET /api/tasks endpoint in backend/app/routes/tasks.py
- [ ] T135 [P] Implement frontend caching for task list using SWR or React Query

### Documentation & Testing

- [ ] T136 [P] Create API documentation using FastAPI automatic docs at /docs
- [ ] T137 [P] Write backend README.md with setup instructions in backend/
- [ ] T138 [P] Write frontend README.md with setup instructions in frontend/
- [ ] T139 [P] Create quickstart.md in specs/002-phase2-web-app/ with end-to-end setup guide
- [ ] T140 Run full test suite and verify >80% coverage for backend
- [ ] T141 [P] Add E2E tests using Playwright for critical user journeys in frontend/e2e/
- [ ] T142 Create deployment guide in specs/002-phase2-web-app/deployment.md

### Code Quality

- [ ] T143 [P] Run ESLint and fix all frontend linting errors
- [ ] T144 [P] Run Python linting (ruff/black) and fix all backend errors
- [ ] T145 [P] Add TypeScript strict mode checks and fix type errors
- [ ] T146 Code review and refactoring for consistency across all components
- [ ] T147 [P] Add logging to all backend operations using Python logging module
- [ ] T148 [P] Add error tracking integration (Sentry) in backend and frontend

---

## Dependencies & Execution Order

### Phase Dependencies

- **Setup (Phase 1)**: No dependencies - can start immediately
- **Foundational (Phase 2)**: Depends on Setup completion - BLOCKS all user stories
- **User Story 1 (Phase 3)**: Depends on Foundational - BLOCKS task features (provides authentication)
- **User Stories 2-6 (Phases 4-8)**: All depend on User Story 1 (authentication) completion
  - Can proceed in priority order: US2 → US3 → US5 → US4 → US6
  - Or in parallel if multiple developers (recommended: US2+US3 first as MVP core)
- **Polish (Phase 9)**: Depends on all user stories being complete

### User Story Dependencies

- **User Story 1 (Authentication)**: No dependencies after Foundational - CRITICAL PATH
- **User Story 2 (Create Task)**: Depends on US1 (auth) - MVP requirement
- **User Story 3 (View Tasks)**: Depends on US1 (auth) - MVP requirement
- **User Story 4 (Update Task)**: Depends on US1 (auth), US2 (tasks exist), US3 (can see tasks)
- **User Story 5 (Toggle Completion)**: Depends on US1 (auth), US3 (can see tasks)
- **User Story 6 (Delete Task)**: Depends on US1 (auth), US3 (can see tasks)

### Critical Path for MVP

```
Setup → Foundational → US1 (Auth) → US2 (Create) + US3 (View) → MVP READY
```

### Within Each User Story

- Tests MUST be written and FAIL before implementation
- Backend models before routes
- Backend routes before frontend API client
- Frontend API client before UI components
- Core implementation before polish/optimization

### Parallel Opportunities

#### Phase 1 (Setup)
- T004-T016: All setup tasks can run in parallel (different files)

#### Phase 2 (Foundational)
- T029: UI components can be built in parallel
- Backend config (T017-T026) and Frontend base (T027-T032) can proceed in parallel teams

#### User Story 1 (Authentication)
- T033-T036: All auth tests in parallel
- T047-T051: Frontend auth components in parallel
- T057-T059: Frontend auth tests in parallel

#### User Story 2 (Create Task)
- T060-T062: Backend tests in parallel
- T070-T072: Frontend components in parallel
- T074-T075: Frontend tests in parallel

#### User Story 3 (View Tasks)
- T076-T078: Backend tests in parallel
- T081-T083: Frontend components in parallel
- T085-T086: Frontend tests in parallel

#### User Story 4 (Update Task)
- T087-T089: Backend tests in parallel
- T093-T094: Frontend functions in parallel
- T097-T098: Frontend tests in parallel

#### User Story 5 (Toggle Completion)
- T099-T100: Backend tests in parallel
- T103-T105: Frontend implementation in parallel
- T107-T108: Frontend tests in parallel

#### User Story 6 (Delete Task)
- T109-T111: Backend tests in parallel
- T113-T114: Frontend components in parallel
- T117-T118: Frontend tests in parallel

#### Phase 9 (Polish)
- Most polish tasks (T119-T148) can run in parallel as they affect different files/concerns

---

## Parallel Example: MVP Core (US2 + US3)

```bash
# After US1 (Auth) completes, launch both Create and View in parallel:

# Developer A: User Story 2 (Create Task)
Task: "Write POST /api/tasks endpoint test"
Task: "Create Task SQLModel"
Task: "Implement POST /api/tasks endpoint"
Task: "Create task form component"

# Developer B: User Story 3 (View Tasks)
Task: "Write GET /api/tasks endpoint test"
Task: "Implement GET /api/tasks endpoint"
Task: "Create task list component"
Task: "Create tasks page"

# Both complete independently, integrate for full MVP
```

---

## Implementation Strategy

### MVP First (Authentication + Create + View)

1. Complete Phase 1: Setup
2. Complete Phase 2: Foundational (CRITICAL - blocks all stories)
3. Complete Phase 3: User Story 1 (Authentication) - BLOCKS task features
4. **PARALLEL or SEQUENTIAL**:
   - Complete Phase 4: User Story 2 (Create Task)
   - Complete Phase 5: User Story 3 (View Tasks)
5. **STOP and VALIDATE**: Test end-to-end MVP flow
6. Deploy/demo MVP

**MVP Deliverable**: Users can sign up, sign in, create tasks, and view their task list

### Incremental Delivery (Remaining CRUD Operations)

1. Add Phase 7: User Story 5 (Toggle Completion) → Deploy/Demo
2. Add Phase 6: User Story 4 (Update Task) → Deploy/Demo
3. Add Phase 8: User Story 6 (Delete Task) → Deploy/Demo
4. Complete Phase 9: Polish → Final deployment

### Parallel Team Strategy

With 2-3 developers:

1. **Team Setup + Foundational** (everyone together): Phases 1-2
2. **Critical Path** (everyone together): Phase 3 (US1 - Authentication)
3. **MVP Core** (parallel):
   - Developer A: Phase 4 (US2 - Create Task)
   - Developer B: Phase 5 (US3 - View Tasks)
4. **Remaining CRUD** (parallel):
   - Developer A: Phase 7 (US5 - Toggle) + Phase 6 (US4 - Update)
   - Developer B: Phase 8 (US6 - Delete) + start Polish
5. **Polish** (parallel): Phase 9 tasks distributed

---

## Task Summary

- **Total Tasks**: 148
- **Setup Phase**: 16 tasks
- **Foundational Phase**: 16 tasks
- **User Story 1 (Authentication)**: 27 tasks
- **User Story 2 (Create Task)**: 16 tasks
- **User Story 3 (View Tasks)**: 11 tasks
- **User Story 4 (Update Task)**: 12 tasks
- **User Story 5 (Toggle Completion)**: 10 tasks
- **User Story 6 (Delete Task)**: 10 tasks
- **Polish Phase**: 30 tasks

**Parallel Opportunities**: ~80 tasks can be executed in parallel across phases (marked with [P])

**MVP Scope**: Phases 1-5 (86 tasks) = Authentication + Create + View tasks

**Critical Path**: Setup → Foundational → Authentication → Create/View (MVP)

---

## Notes

- [P] tasks = different files, no dependencies - can run in parallel
- [Story] label maps task to specific user story for traceability
- Each user story should be independently completable and testable
- All backend tests must be written BEFORE implementation (TDD approach)
- Verify all tests fail initially, then pass after implementation
- Commit after each task or logical group of related tasks
- Stop at any checkpoint to validate story works independently
- Follow constitution mandates: >80% test coverage, no manual coding, spec-driven development
- Use Docker Compose for development: `docker-compose up`
- Avoid: vague tasks, same file conflicts, cross-story dependencies that break independence

---

**Generated**: December 28, 2024
**By**: Claude Code (Sonnet 4.5)
**Status**: Ready for implementation
