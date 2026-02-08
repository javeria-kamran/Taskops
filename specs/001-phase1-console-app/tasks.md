# Tasks: Phase I Console Todo Application

**Input**: Design documents from `/specs/001-phase1-console-app/`
**Prerequisites**: plan.md, spec.md, data-model.md, contracts/cli-interface.md, research.md

**Tests**: Test tasks are included as this is a deliverable requirement (FR-019: >80% test coverage, SC-007)

**Organization**: Tasks are grouped by user story to enable independent implementation and testing of each story.

## Format: `[ID] [P?] [Story] Description`

- **[P]**: Can run in parallel (different files, no dependencies)
- **[Story]**: Which user story this task belongs to (e.g., US1, US2, US3, US4, US5)
- Include exact file paths in descriptions

## Path Conventions

- **Single project**: `src/`, `tests/` at repository root
- Phase I follows single project structure per plan.md

---

## Phase 1: Setup (Shared Infrastructure)

**Purpose**: Project initialization and basic Python structure

- [x] T001 Create project directory structure (src/, tests/, src/models/, src/services/, src/cli/, src/lib/)
- [x] T002 Initialize UV project with pyproject.toml for Python 3.13+
- [x] T003 [P] Create .gitignore file with Python patterns (__pycache__/, *.pyc, .venv/, etc.)
- [x] T004 [P] Add pytest and pytest-cov as dev dependencies via UV
- [x] T005 [P] Create README.md with project overview and setup instructions
- [x] T006 [P] Create all __init__.py files for Python packages (src/, src/models/, src/services/, src/cli/, src/lib/, tests/, tests/unit/, tests/integration/)

---

## Phase 2: Foundational (Blocking Prerequisites)

**Purpose**: Core infrastructure that MUST be complete before ANY user story can be implemented

**⚠️ CRITICAL**: No user story work can begin until this phase is complete

- [x] T007 Create Task model class with validation in src/models/task.py
- [x] T008 Create custom exception classes (ValidationError, TaskNotFoundError) in src/lib/exceptions.py
- [x] T009 Create input validators module in src/lib/validators.py
- [x] T010 Create TaskManager service class with in-memory storage in src/services/task_manager.py

**Checkpoint**: ✅ Foundation ready - user story implementation can now begin in parallel

---

## Phase 3: User Story 5 - Navigate Console Menu (Priority: P1) 🎯 MVP Part 1

**Goal**: Provide clear console menu with numbered options for navigation

**Independent Test**: Can be fully tested by launching the app and verifying all menu options are displayed, numbered, and respond correctly to user input. Delivers usability.

**Why First**: Menu navigation is the gateway to all functionality. Without a working menu, no other features can be accessed. This is a P1 dependency for all other user stories.

### Tests for User Story 5

> **NOTE: Write these tests FIRST, ensure they FAIL before implementation**

- [ ] T011 [P] [US5] Unit test for menu display in tests/unit/test_menu.py
- [ ] T012 [P] [US5] Unit test for menu input validation in tests/unit/test_menu.py
- [ ] T013 [P] [US5] Integration test for main menu loop in tests/integration/test_cli.py

### Implementation for User Story 5

- [ ] T014 [US5] Implement main menu display function in src/cli/menu.py
- [ ] T015 [US5] Implement menu input handler and validation in src/cli/menu.py
- [ ] T016 [US5] Implement main application loop with menu redisplay in src/cli/menu.py
- [ ] T017 [US5] Implement graceful exit handler (option 6) with confirmation in src/cli/menu.py
- [ ] T018 [US5] Implement Ctrl+C (KeyboardInterrupt) handler in src/cli/menu.py

**Checkpoint**: At this point, User Story 5 (menu navigation) should be fully functional and testable independently

---

## Phase 4: User Story 1 - Create and View Tasks (Priority: P1) 🎯 MVP Part 2

**Goal**: Allow users to create new tasks and view their task list

**Independent Test**: Can be fully tested by launching the console app, adding a task with a title and description, and confirming it appears in the task list. Delivers immediate value as users can start tracking their todos.

**Why Second**: This is the foundational capability - without the ability to create and view tasks, the todo application has no value. This represents the absolute minimum viable product along with menu navigation.

### Tests for User Story 1

- [ ] T019 [P] [US1] Unit test for add_task in tests/unit/test_task_manager.py
- [ ] T020 [P] [US1] Unit test for get_all_tasks in tests/unit/test_task_manager.py
- [ ] T021 [P] [US1] Unit test for Task model creation and validation in tests/unit/test_task.py
- [ ] T022 [P] [US1] Unit test for title validation (empty, too long) in tests/unit/test_validators.py
- [ ] T023 [P] [US1] Unit test for description validation (too long) in tests/unit/test_validators.py
- [ ] T024 [US1] Integration test for add task workflow in tests/integration/test_cli.py
- [ ] T025 [US1] Integration test for view tasks workflow in tests/integration/test_cli.py

### Implementation for User Story 1

- [ ] T026 [US1] Implement add_task method in TaskManager (src/services/task_manager.py)
- [ ] T027 [US1] Implement get_all_tasks method in TaskManager (src/services/task_manager.py)
- [ ] T028 [US1] Implement add task handler (option 1) in src/cli/handlers.py
- [ ] T029 [US1] Implement view tasks handler (option 2) in src/cli/handlers.py
- [ ] T030 [US1] Integrate add task handler into main menu in src/cli/menu.py
- [ ] T031 [US1] Integrate view tasks handler into main menu in src/cli/menu.py

**Checkpoint**: At this point, User Stories 5 AND 1 should both work independently (MVP complete!)

---

## Phase 5: User Story 2 - Mark Tasks as Complete (Priority: P2)

**Goal**: Allow users to mark tasks as complete or incomplete to track progress

**Independent Test**: Can be tested by creating a task, marking it as complete, verifying the status changes, and confirming it's visible when viewing tasks. Delivers the value of progress tracking.

### Tests for User Story 2

- [ ] T032 [P] [US2] Unit test for toggle_complete method in tests/unit/test_task_manager.py
- [ ] T033 [P] [US2] Unit test for TaskNotFoundError on invalid ID in tests/unit/test_task_manager.py
- [ ] T034 [US2] Integration test for mark complete workflow in tests/integration/test_cli.py
- [ ] T035 [US2] Integration test for mark incomplete workflow in tests/integration/test_cli.py

### Implementation for User Story 2

- [ ] T036 [US2] Implement toggle_complete method in TaskManager (src/services/task_manager.py)
- [ ] T037 [US2] Implement mark complete handler (option 5) in src/cli/handlers.py
- [ ] T038 [US2] Integrate mark complete handler into main menu in src/cli/menu.py

**Checkpoint**: At this point, User Stories 5, 1, AND 2 should all work independently

---

## Phase 6: User Story 3 - Update Task Details (Priority: P3)

**Goal**: Allow users to update task titles and descriptions to correct mistakes or add details

**Independent Test**: Can be tested by creating a task, modifying its title or description, and verifying the changes persist. Delivers value in task maintenance and flexibility.

### Tests for User Story 3

- [ ] T039 [P] [US3] Unit test for update_task method in tests/unit/test_task_manager.py
- [ ] T040 [P] [US3] Unit test for update with invalid ID in tests/unit/test_task_manager.py
- [ ] T041 [P] [US3] Unit test for update with empty title validation in tests/unit/test_task_manager.py
- [ ] T042 [US3] Integration test for update task workflow in tests/integration/test_cli.py
- [ ] T043 [US3] Integration test for update title only in tests/integration/test_cli.py
- [ ] T044 [US3] Integration test for update description only in tests/integration/test_cli.py

### Implementation for User Story 3

- [ ] T045 [US3] Implement update_task method in TaskManager (src/services/task_manager.py)
- [ ] T046 [US3] Implement update task handler (option 3) in src/cli/handlers.py
- [ ] T047 [US3] Integrate update task handler into main menu in src/cli/menu.py

**Checkpoint**: At this point, User Stories 5, 1, 2, AND 3 should all work independently

---

## Phase 7: User Story 4 - Delete Tasks (Priority: P4)

**Goal**: Allow users to delete tasks that are no longer relevant

**Independent Test**: Can be tested by creating a task, deleting it, and verifying it no longer appears in the task list. Delivers value in task list hygiene.

### Tests for User Story 4

- [ ] T048 [P] [US4] Unit test for delete_task method in tests/unit/test_task_manager.py
- [ ] T049 [P] [US4] Unit test for delete with invalid ID in tests/unit/test_task_manager.py
- [ ] T050 [P] [US4] Unit test for ID not reused after deletion in tests/unit/test_task_manager.py
- [ ] T051 [US4] Integration test for delete task workflow with confirmation in tests/integration/test_cli.py
- [ ] T052 [US4] Integration test for cancelled deletion in tests/integration/test_cli.py

### Implementation for User Story 4

- [ ] T053 [US4] Implement delete_task method in TaskManager (src/services/task_manager.py)
- [ ] T054 [US4] Implement delete task handler (option 4) with confirmation in src/cli/handlers.py
- [ ] T055 [US4] Integrate delete task handler into main menu in src/cli/menu.py

**Checkpoint**: All user stories (1-5) should now be independently functional - Phase I feature complete!

---

## Phase 8: Polish & Cross-Cutting Concerns

**Purpose**: Improvements that affect multiple user stories and final validation

- [ ] T056 [P] Run pytest with coverage and verify >80% coverage
- [ ] T057 [P] Fix any failing tests or coverage gaps
- [ ] T058 [P] Add docstrings to all public functions and classes
- [ ] T059 [P] Verify all error messages match CLI interface contract
- [ ] T060 [P] Test edge cases (empty title, long title, long description, special characters)
- [ ] T061 [P] Verify performance targets (<2s startup, <1s view 100 tasks)
- [ ] T062 [P] Update README.md with final usage examples and screenshots
- [ ] T063 Validate all acceptance scenarios from spec.md pass
- [ ] T064 Run complete end-to-end manual testing following quickstart.md
- [ ] T065 Create demo script showing all 5 operations
- [ ] T066 Final code review against constitutional principles

---

## Dependencies & Execution Order

### Phase Dependencies

- **Setup (Phase 1)**: No dependencies - can start immediately
- **Foundational (Phase 2)**: Depends on Setup completion - BLOCKS all user stories
- **User Story 5 (Phase 3)**: Depends on Foundational phase - BLOCKS all other user stories (menu required to access features)
- **User Stories 1-4 (Phases 4-7)**: All depend on Foundational + US5 completion
  - User stories can then proceed in parallel (if staffed)
  - Or sequentially in priority order (US1 → US2 → US3 → US4)
- **Polish (Phase 8)**: Depends on all user stories being complete

### User Story Dependencies

- **User Story 5 (P1 - Menu)**: Can start after Foundational (Phase 2) - No dependencies on other stories - **REQUIRED for all other stories**
- **User Story 1 (P1 - Create/View)**: Depends on US5 (needs menu) - No dependencies on US2, US3, US4
- **User Story 2 (P2 - Mark Complete)**: Depends on US5 (needs menu) and US1 (needs tasks to mark) - Can start after US1
- **User Story 3 (P3 - Update)**: Depends on US5 (needs menu) and US1 (needs tasks to update) - Can start after US1
- **User Story 4 (P4 - Delete)**: Depends on US5 (needs menu) and US1 (needs tasks to delete) - Can start after US1

### Within Each User Story

- Tests MUST be written and FAIL before implementation
- TaskManager methods before CLI handlers
- CLI handlers before menu integration
- Story complete before moving to next priority

### Parallel Opportunities

- **Setup (Phase 1)**: T003, T004, T005, T006 can run in parallel
- **Foundational (Phase 2)**: T007, T008, T009 can run in parallel (T010 depends on T007-T009)
- **Tests within each story**: All test tasks marked [P] can run in parallel
- **After US1 complete**: US2, US3, US4 can run in parallel (all depend on US1 for tasks to exist)

---

## Parallel Example: User Story 1

```bash
# Launch all tests for User Story 1 together:
Task T019: "Unit test for add_task in tests/unit/test_task_manager.py"
Task T020: "Unit test for get_all_tasks in tests/unit/test_task_manager.py"
Task T021: "Unit test for Task model creation in tests/unit/test_task.py"
Task T022: "Unit test for title validation in tests/unit/test_validators.py"
Task T023: "Unit test for description validation in tests/unit/test_validators.py"
# All these can execute in parallel - different test files

# After tests fail, implement in sequence:
Task T026: "Implement add_task method in TaskManager"
Task T027: "Implement get_all_tasks method in TaskManager"
Task T028: "Implement add task handler in handlers.py"
Task T029: "Implement view tasks handler in handlers.py"
Task T030: "Integrate add task handler into menu"
Task T031: "Integrate view tasks handler into menu"
```

---

## Parallel Example: After Foundational Complete

```bash
# Once Phase 2 (Foundational) is complete, US5 must complete first (menu),
# then US1 must complete (create tasks), then US2, US3, US4 can proceed in parallel:

# After US1 complete, launch in parallel:
Task: "User Story 2 tests and implementation" (Developer A)
Task: "User Story 3 tests and implementation" (Developer B)
Task: "User Story 4 tests and implementation" (Developer C)
```

---

## Implementation Strategy

### MVP First (User Stories 5 + 1 Only)

1. Complete Phase 1: Setup (T001-T006)
2. Complete Phase 2: Foundational (T007-T010) - CRITICAL
3. Complete Phase 3: User Story 5 (T011-T018) - Menu navigation
4. Complete Phase 4: User Story 1 (T019-T031) - Create and view tasks
5. **STOP and VALIDATE**: Test US5 + US1 independently
6. Run tests, verify >80% coverage
7. Demo MVP: Working menu + Add/View tasks

**MVP Deliverable**: Functional console app with menu navigation and ability to create/view tasks

### Incremental Delivery

1. Complete Setup + Foundational → Foundation ready
2. Add User Story 5 (Menu) → Test independently
3. Add User Story 1 (Create/View) → Test independently → **MVP Checkpoint!**
4. Add User Story 2 (Mark Complete) → Test independently
5. Add User Story 3 (Update) → Test independently
6. Add User Story 4 (Delete) → Test independently → **Phase I Complete!**
7. Polish (Phase 8) → Final testing and validation
8. Each story adds value without breaking previous stories

### Parallel Team Strategy

With multiple developers:

1. Team completes Setup + Foundational together (T001-T010)
2. One developer completes User Story 5 (Menu) - Required for all
3. One developer completes User Story 1 (Create/View) - Required for US2, US3, US4
4. Once US1 is done:
   - Developer A: User Story 2 (Mark Complete)
   - Developer B: User Story 3 (Update)
   - Developer C: User Story 4 (Delete)
5. Stories complete and integrate independently

---

## Task Count Summary

- **Phase 1 (Setup)**: 6 tasks (T001-T006)
- **Phase 2 (Foundational)**: 4 tasks (T007-T010)
- **Phase 3 (US5 - Menu)**: 8 tasks (T011-T018)
- **Phase 4 (US1 - Create/View)**: 13 tasks (T019-T031)
- **Phase 5 (US2 - Mark Complete)**: 7 tasks (T032-T038)
- **Phase 6 (US3 - Update)**: 9 tasks (T039-T047)
- **Phase 7 (US4 - Delete)**: 8 tasks (T048-T055)
- **Phase 8 (Polish)**: 11 tasks (T056-T066)

**Total**: 66 tasks

**Test Tasks**: 30 (covering >80% requirement)
**Implementation Tasks**: 36

**Parallel Opportunities**: 20 tasks marked [P] can execute in parallel

---

## Notes

- [P] tasks = different files, no dependencies, can run in parallel
- [Story] label maps task to specific user story for traceability
- Each user story should be independently completable and testable
- Verify tests fail before implementing (TDD approach)
- Commit after each task or logical group
- Stop at any checkpoint to validate story independently
- **US5 (Menu) is a hard dependency** for all other user stories - complete first after Foundational
- **US1 (Create/View) is a dependency** for US2, US3, US4 - need tasks to mark/update/delete
- Run `pytest --cov=src --cov-report=html` after each story to track coverage progress
- Target: >80% coverage minimum (SC-007), aim for 90%+
