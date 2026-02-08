# Data Model: Phase I Console Todo Application

**Feature**: Phase I Console Todo Application
**Date**: December 27, 2025
**Status**: Complete

## Overview

This document defines the data model for the Phase I Console Todo Application. The model consists of a single entity (Task) with embedded validation rules. The design supports in-memory storage and is structured to facilitate easy migration to database persistence in Phase II.

---

## Entities

### Task

Represents a single todo item with title, description, completion status, and metadata.

**Purpose**: Core data entity representing a user's task or todo item.

**Lifecycle**: Created → (Updated)* → (Completed/Uncompleted)* → (Updated)* → Deleted

**Storage**: In-memory list maintained by TaskManager service

#### Attributes

| Attribute | Type | Required | Default | Constraints | Description |
|-----------|------|----------|---------|-------------|-------------|
| `id` | `int` | Yes (auto-assigned) | Auto-increment | Positive integer, unique | Unique identifier for the task |
| `title` | `str` | Yes | None | 1-200 characters | Short description of the task |
| `description` | `str` | No | `""` (empty string) | 0-1000 characters | Detailed description or notes |
| `completed` | `bool` | Yes | `False` | True or False | Whether the task is completed |
| `created_at` | `datetime` | Yes (auto-assigned) | Current timestamp | Valid datetime | When the task was created |

#### Validation Rules

**Title Validation** (FR-002, FR-013):
- **Required**: Must not be empty or None
- **Minimum Length**: 1 character (after stripping whitespace)
- **Maximum Length**: 200 characters
- **Error Message**: "Title is required and must be 1-200 characters"
- **Validation Point**: Model initialization, update operations

**Description Validation** (FR-002, FR-014):
- **Optional**: Can be empty string or None (converts to empty string)
- **Maximum Length**: 1000 characters
- **Error Message**: "Description cannot exceed 1000 characters"
- **Validation Point**: Model initialization, update operations

**ID Validation** (FR-003):
- **Auto-Generated**: Assigned by TaskManager on creation, not user-provided
- **Unique**: Enforced by TaskManager (sequential counter)
- **Immutable**: Once assigned, ID never changes
- **Positive Integer**: Must be >= 1

**Completed Validation** (FR-008):
- **Boolean Only**: Must be exactly `True` or `False`
- **Default**: `False` for new tasks
- **Toggleable**: Can be changed from False → True or True → False

**Created At Validation**:
- **Auto-Generated**: Set to current timestamp on creation
- **Immutable**: Never changes after creation
- **Timezone-Aware**: Use UTC timezone for consistency (if applicable)

#### Validation Examples

**Valid Task Creation**:
```python
# Minimum valid task
Task(id=1, title="Buy milk")
# Attributes: id=1, title="Buy milk", description="", completed=False, created_at=<now>

# Complete valid task
Task(id=2, title="Complete project", description="Finish Phase I console app", completed=False)
# Attributes: id=2, title="Complete project", description="Finish Phase I...", completed=False, created_at=<now>

# Task with maximum length title (200 chars)
Task(id=3, title="x" * 200)
# Valid - exactly 200 characters

# Task with maximum length description (1000 chars)
Task(id=4, title="Long description task", description="y" * 1000)
# Valid - exactly 1000 characters
```

**Invalid Task Creation (Validation Errors)**:
```python
# Empty title
Task(id=1, title="")
# ❌ ValidationError: "Title is required and must be 1-200 characters"

# Title too long (201 chars)
Task(id=1, title="x" * 201)
# ❌ ValidationError: "Title is required and must be 1-200 characters"

# Description too long (1001 chars)
Task(id=1, title="Valid title", description="z" * 1001)
# ❌ ValidationError: "Description cannot exceed 1000 characters"

# Whitespace-only title
Task(id=1, title="   ")
# ❌ ValidationError: "Title is required and must be 1-200 characters"
# (after stripping whitespace, title is empty)
```

#### State Transitions

Tasks have two primary states related to completion:

**Pending State** (`completed = False`):
- Initial state for all new tasks
- Indicates task is not yet done
- User can update title/description, mark as complete, or delete

**Completed State** (`completed = True`):
- Task has been marked as done
- User can mark as incomplete (toggle back), update, or delete
- Completion does not prevent further modifications

**State Transition Diagram**:
```
[Created]
    ↓
[Pending] ←─→ [Completed]
    ↓             ↓
[Deleted]     [Deleted]
```

**Allowed Transitions**:
- Created → Pending (automatic on creation)
- Pending → Completed (mark as complete, FR-008)
- Completed → Pending (mark as incomplete, FR-008)
- Pending → Deleted (delete task, FR-007)
- Completed → Deleted (delete task, FR-007)
- Pending → Pending (update title/description, FR-006)
- Completed → Completed (update title/description, FR-006)

---

## Relationships

### Phase I: No Relationships

In Phase I, the Task entity has **no relationships** to other entities:
- **Single-User Application**: No User entity exists
- **No Task Hierarchies**: Tasks are independent, no parent/child relationships
- **No Categories/Tags**: Not in Basic Level features scope

### Phase II+: Future Relationships

**User → Task** (One-to-Many):
- Each task will belong to exactly one user (`user_id` foreign key)
- Users can have zero or more tasks
- Enables multi-user support in Phase II web application

**Task → Category** (Many-to-One, Optional):
- Tasks may optionally belong to a category (Intermediate Level feature)
- Categories can have multiple tasks
- Not in Phase I scope

**Task → Tag** (Many-to-Many, Optional):
- Tasks can have multiple tags (Intermediate Level feature)
- Tags can be applied to multiple tasks
- Not in Phase I scope

---

## Invariants

**Invariants** are conditions that must always be true for the data model:

1. **ID Uniqueness**: No two tasks can have the same ID
   - Enforced by: TaskManager's auto-increment counter
   - Violation would indicate: Critical bug in TaskManager

2. **Title Non-Empty**: Every task must have a non-empty title (after trimming)
   - Enforced by: Task validation on creation and update
   - Violation would indicate: Validation bypass

3. **Length Constraints**: Title ≤ 200 chars, Description ≤ 1000 chars
   - Enforced by: Task validation on creation and update
   - Violation would indicate: Validation bypass

4. **Completed Is Boolean**: `completed` field must be exactly `True` or `False`
   - Enforced by: Python type system (bool type)
   - Violation would indicate: Type system bypass (unlikely)

5. **Created Timestamp Immutable**: `created_at` never changes after task creation
   - Enforced by: TaskManager update logic (excludes created_at from updates)
   - Violation would indicate: Incorrect update implementation

6. **ID Immutability**: Task ID never changes after creation
   - Enforced by: TaskManager update logic (excludes id from updates)
   - Violation would indicate: Incorrect update implementation

---

## Edge Cases

### Title Edge Cases

**Whitespace Handling**:
- **Leading/Trailing Whitespace**: Should be stripped before validation
  - Input: `"  Buy milk  "` → Stored as: `"Buy milk"`
- **Whitespace-Only Title**: Invalid after stripping
  - Input: `"    "` → ValidationError (empty after strip)
- **Internal Whitespace**: Preserved
  - Input: `"Buy  milk"` → Stored as: `"Buy  milk"`

**Special Characters**:
- **Allowed**: All Unicode characters, emojis, punctuation
  - Input: `"Buy milk 🥛"` → Valid
  - Input: `"Complete [Project] #1"` → Valid
- **Edge Case**: Emoji length (single emoji may count as multiple chars depending on encoding)
  - Implementation should count Unicode code points, not bytes

**Boundary Values**:
- **1 Character**: Valid (minimum)
  - Input: `"X"` → Valid
- **200 Characters**: Valid (maximum)
  - Input: `"x" * 200` → Valid
- **201 Characters**: Invalid
  - Input: `"x" * 201` → ValidationError

### Description Edge Cases

**Empty Description**:
- **None**: Converted to empty string
  - Input: `None` → Stored as: `""`
- **Empty String**: Valid
  - Input: `""` → Stored as: `""`

**Newlines and Formatting**:
- **Multiline Descriptions**: Allowed (newline characters preserved)
  - Input: `"Line 1\nLine 2"` → Valid
- **Tabs and Special Whitespace**: Preserved
  - Input: `"Item 1:\tDetails"` → Valid

**Boundary Values**:
- **1000 Characters**: Valid (maximum)
  - Input: `"x" * 1000` → Valid
- **1001 Characters**: Invalid
  - Input: `"x" * 1001` → ValidationError

### ID Edge Cases

**Auto-Increment Overflow**:
- **Risk**: If task ID reaches maximum integer value
- **Likelihood**: Extremely low (would require 2^31 - 1 task creations)
- **Mitigation**: Python 3's `int` type has arbitrary precision (no practical limit)
- **Handling**: Not a concern for Phase I (in-memory, <1000 tasks expected)

**ID Reuse After Deletion**:
- **Behavior**: IDs are never reused, even after task deletion
  - Delete task #5 → Next task is #6, not #5
- **Rationale**: Prevents confusion, maintains audit trail concept
- **Implementation**: Counter always increments, never decrements

### Completed Toggle Edge Cases

**Rapid Toggle**:
- **Scenario**: User toggles completed status multiple times rapidly
- **Behavior**: Each toggle updates the state correctly
  - Start: `False` → Toggle: `True` → Toggle: `False` → Toggle: `True`
- **No Side Effects**: Toggling has no hidden side effects in Phase I

### Timestamp Edge Cases

**System Clock Changes**:
- **Scenario**: System clock adjusted backward
- **Behavior**: New task might have earlier `created_at` than previous task
- **Impact**: Minimal (tasks are not sorted by created_at in Phase I)
- **Phase II Consideration**: Use database timestamps instead of application timestamps

---

## Derived Data

### Computed Properties (Not Stored)

**Status Display String**:
- **Logic**: `"Completed" if task.completed else "Pending"`
- **Usage**: Display in task list
- **Not Stored**: Derived from `completed` boolean

**Age in Days**:
- **Logic**: `(datetime.now() - task.created_at).days`
- **Usage**: Potential display in task list (not in Phase I spec)
- **Not Stored**: Derived from `created_at` timestamp

**Title Preview** (for future UI):
- **Logic**: `task.title[:50] + "..." if len(task.title) > 50 else task.title`
- **Usage**: Truncated display in compact views
- **Not Stored**: Derived from `title` field

---

## Data Integrity

### Validation Layer Responsibilities

**Task Model (models/task.py)**:
- Validates title length (1-200 chars)
- Validates description length (≤1000 chars)
- Enforces default values (`completed=False`, `description=""`)
- Ensures created_at is set
- **Does NOT**: Validate ID uniqueness (TaskManager's responsibility)

**TaskManager Service (services/task_manager.py)**:
- Assigns unique IDs (auto-increment counter)
- Validates task existence for operations (get, update, delete, toggle)
- Ensures ID uniqueness across all tasks
- Enforces immutability of ID and created_at during updates
- **Delegates**: Title/description validation to Task model

**CLI Layer (cli/handlers.py)**:
- Pre-validates user input types (e.g., task ID is numeric)
- Handles ValidationError and TaskNotFoundError exceptions
- Displays user-friendly error messages
- **Delegates**: Data validation to lower layers

### Consistency Guarantees

**In-Memory Consistency** (Phase I):
- All operations are synchronous and single-threaded
- No concurrency issues (no multi-threading or multi-processing)
- Consistency guaranteed by Python's execution model

**Future Persistence Consistency** (Phase II+):
- Database transactions will ensure atomicity
- Foreign key constraints will enforce relationships (User ← Task)
- Unique constraints will enforce ID uniqueness at database level

---

## Serialization

### Phase I: Not Applicable

Phase I uses in-memory storage with no serialization:
- **No JSON Export**: Not in spec scope
- **No File Persistence**: Explicitly out of scope (FR-004)
- **No Database Serialization**: Phase II requirement

### Phase II+: Future Serialization

**JSON Serialization** (for API responses):
```json
{
  "id": 1,
  "title": "Buy milk",
  "description": "From the grocery store",
  "completed": false,
  "created_at": "2025-12-27T14:30:00Z"
}
```

**Database Serialization** (SQLModel/SQLAlchemy):
```sql
CREATE TABLE tasks (
    id INTEGER PRIMARY KEY,
    user_id VARCHAR NOT NULL,
    title VARCHAR(200) NOT NULL,
    description TEXT,
    completed BOOLEAN DEFAULT FALSE,
    created_at TIMESTAMP NOT NULL,
    updated_at TIMESTAMP
);
```

---

## Testing Considerations

### Unit Test Coverage

**Task Model Tests** (`tests/unit/test_task.py`):
- ✅ Test valid task creation with minimum required fields
- ✅ Test valid task creation with all fields
- ✅ Test title validation (empty, 1 char, 200 chars, 201 chars)
- ✅ Test description validation (empty, 1000 chars, 1001 chars)
- ✅ Test default values (completed=False, description="")
- ✅ Test created_at auto-generation
- ✅ Test whitespace stripping in title
- ✅ Test special characters in title and description
- ✅ Test emoji handling in title

**TaskManager Tests** (`tests/unit/test_task_manager.py`):
- ✅ Test ID auto-increment (task 1, task 2, task 3 have IDs 1, 2, 3)
- ✅ Test ID uniqueness across multiple tasks
- ✅ Test ID immutability during updates
- ✅ Test created_at immutability during updates
- ✅ Test task retrieval by valid ID
- ✅ Test task retrieval by invalid ID (TaskNotFoundError)
- ✅ Test completed toggle (False → True, True → False)
- ✅ Test task deletion removes from list
- ✅ Test ID not reused after deletion

### Integration Test Coverage

**End-to-End Workflow Tests** (`tests/integration/test_cli.py`):
- ✅ Test create → view → update → view → delete workflow
- ✅ Test create → complete → view workflow
- ✅ Test invalid input handling (title too long, task not found)
- ✅ Test multiple tasks interaction (create 10, view all, delete 1, view 9)

---

## Performance Considerations

### Memory Footprint

**Single Task Size** (estimated):
- `id`: 28 bytes (Python int object overhead)
- `title`: ~50-250 bytes (depends on length, avg 100 chars = ~150 bytes)
- `description`: ~0-1050 bytes (depends on length, avg 200 chars = ~250 bytes)
- `completed`: 28 bytes (Python bool object)
- `created_at`: ~50 bytes (datetime object)
- **Total per task**: ~250-500 bytes (average ~350 bytes)

**100 Tasks**:
- Memory: 100 tasks × 350 bytes = 35 KB
- **Negligible**: Well within modern system memory capabilities

**1000 Tasks** (stress test):
- Memory: 1000 tasks × 350 bytes = 350 KB
- **Still negligible**: Python interpreter overhead (~10-50 MB) dominates

### Operation Complexity

**Create Task**: O(1) - Append to list
**View All Tasks**: O(n) - Iterate entire list (n = number of tasks)
**Get Task by ID**: O(n) - Linear search through list
**Update Task**: O(n) - Linear search + modification
**Delete Task**: O(n) - Linear search + removal
**Toggle Completed**: O(n) - Linear search + modification

**Acceptable for Phase I**: For n ≤ 100, O(n) operations are instant (<1ms)

---

## Migration Path to Phase II

### Database Schema

When migrating to Phase II (Neon PostgreSQL with SQLModel):

**Add Fields**:
```python
user_id: str  # Foreign key to users table
updated_at: datetime  # Track last modification
```

**Modify Storage**:
- Replace in-memory list with database table
- Add indexes: `(user_id, completed)`, `(user_id, created_at)`
- Add foreign key constraint: `user_id → users.id` with CASCADE delete

**Preserve Logic**:
- Task validation rules remain identical
- TaskManager interface remains same (implementation changes)
- CLI layer requires no changes (depends on TaskManager interface)

**Backward Compatibility**:
- All Phase I tests should still pass with database backend
- Only add new tests for multi-user scenarios

---

## Conclusion

The Task data model is designed to be simple, well-validated, and easily extensible. It supports all Phase I Basic Level features while maintaining clean architecture and preparing for Phase II database migration.

**Key Design Decisions**:
- ✅ Single entity with embedded validation
- ✅ Clear validation rules enforced at model level
- ✅ Immutable ID and created_at after creation
- ✅ Boolean completed state (no intermediate states)
- ✅ In-memory storage with O(n) operations acceptable for n ≤ 100
- ✅ Clean migration path to database persistence in Phase II
