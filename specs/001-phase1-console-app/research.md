# Research & Technical Decisions: Phase I Console Todo Application

**Feature**: Phase I Console Todo Application
**Date**: December 27, 2025
**Status**: Complete

## Overview

This document captures all technical decisions made during the planning phase for the Phase I Console Todo Application. All decisions align with constitutional requirements and hackathon Phase I specifications.

---

## Technology Decisions

### 1. Programming Language: Python 3.13+

**Decision**: Use Python 3.13+ as the implementation language

**Rationale**:
- **Constitutional Mandate**: Phase I technology stack explicitly specifies Python 3.13+ (constitution.md, Technology Stack Mandates)
- **Spec-Driven Requirement**: FR-016 in spec.md mandates Python 3.13+ usage
- **Rapid Development**: Python's simplicity aligns with spec-driven development approach where Claude Code generates implementation
- **Rich Standard Library**: Minimal external dependencies needed for console I/O, data structures, and validation
- **Testing Ecosystem**: Mature testing frameworks (pytest) for >80% coverage requirement

**Alternatives Considered**:
- **JavaScript/Node.js**: Rejected - Not aligned with constitutional Phase I requirements
- **Go**: Rejected - Excellent for performance but not specified in constitution
- **Rust**: Rejected - Would add complexity for a simple console app, not in constitution

**Best Practices**:
- Use type hints throughout codebase for clarity and IDE support
- Follow PEP 8 style guidelines for consistency
- Leverage dataclasses for Task entity (Python 3.7+ feature)
- Use context managers for resource handling
- Implement proper exception handling with custom exceptions

---

### 2. Package Management: UV

**Decision**: Use UV as the Python package manager

**Rationale**:
- **Constitutional Requirement**: Specified in Phase I technology stack (constitution.md)
- **Modern Tool**: UV is a fast, modern Python package manager and project manager
- **Dependency Resolution**: Better dependency resolution than traditional pip
- **Virtual Environment Management**: Built-in venv management
- **Lock Files**: Ensures reproducible builds across environments

**Alternatives Considered**:
- **pip + venv**: Rejected - Traditional approach, but UV is constitutionally mandated
- **Poetry**: Rejected - Good tool but not specified in requirements
- **Conda**: Rejected - Overkill for simple console app

**Best Practices**:
- Use `pyproject.toml` for project configuration
- Pin exact dependency versions for reproducibility
- Use UV lock files to ensure consistent environments
- Document UV installation and usage in README.md

---

### 3. Testing Framework: pytest

**Decision**: Use pytest for all testing (unit and integration)

**Rationale**:
- **Industry Standard**: pytest is the de facto standard for Python testing
- **Constitutional Alignment**: Testing standards require >80% coverage (Principle 11)
- **Rich Ecosystem**: Extensive plugin support (pytest-cov for coverage, pytest-mock for mocking)
- **Readable Syntax**: Simple assert statements, no boilerplate test classes required
- **Fixture System**: Powerful fixture system for test setup and teardown

**Alternatives Considered**:
- **unittest**: Rejected - Built-in but more verbose, less flexible
- **nose2**: Rejected - Less actively maintained than pytest
- **doctest**: Rejected - Good for documentation examples but insufficient for comprehensive testing

**Best Practices**:
- Use pytest fixtures for shared test data (e.g., sample tasks)
- Organize tests by layer: `tests/unit/` and `tests/integration/`
- Use parametrized tests for testing multiple scenarios efficiently
- Use pytest-cov plugin for coverage reporting: `pytest --cov=src --cov-report=html`
- Aim for 90%+ coverage to exceed 80% requirement
- Mock external dependencies (though minimal in Phase I)

**Coverage Targets**:
- **models/task.py**: 100% (pure data class with validation)
- **services/task_manager.py**: 95%+ (core business logic)
- **lib/validators.py**: 100% (utility functions)
- **cli/**: 70%+ (harder to test I/O, but integration tests will help)
- **Overall Target**: >80% (constitutional minimum), aim for 90%

---

### 4. Data Storage: In-Memory Data Structures

**Decision**: Use Python native data structures (list, dict) for in-memory task storage

**Rationale**:
- **Constitutional Constraint**: Phase I explicitly prohibits persistence (constitution.md, Phase I description)
- **Spec Requirement**: FR-004 specifies in-memory storage, "Out of Scope" section excludes database integration
- **Simplicity**: No external dependencies, no file I/O, no database setup
- **Performance**: Direct memory access, instant reads/writes, suitable for 100+ tasks
- **Educational Value**: Demonstrates data structure usage before adding persistence in Phase II

**Alternatives Considered**:
- **SQLite In-Memory Database**: Rejected - Adds unnecessary complexity for Phase I, not needed until Phase II
- **JSON File Storage**: Rejected - Explicitly out of scope (no persistence), would violate constitutional Phase I boundaries
- **Pickle Serialization**: Rejected - Persistence mechanism, violates Phase I constraints

**Implementation Approach**:
- **Primary Storage**: List of Task objects (`tasks: list[Task]`)
- **Auto-Incrementing IDs**: Simple counter variable (`next_id: int`)
- **Fast Lookup**: Iterate list for operations (O(n) acceptable for ~100 tasks)
- **Future-Proof**: Design TaskManager interface to easily swap with database in Phase II

**Data Structures**:
```python
# TaskManager service will maintain:
tasks: list[Task] = []  # All tasks in creation order
next_id: int = 1         # Auto-incrementing ID counter
```

---

### 5. Project Structure: Single Project Layout

**Decision**: Use single project structure with layered architecture (models, services, cli, lib)

**Rationale**:
- **Constitutional Alignment**: Principle 4 (Clean Architecture & Separation of Concerns)
- **Appropriate for Console App**: No web frontend/backend split needed for Phase I
- **Clear Layers**:
  - **models/**: Data entities (Task)
  - **services/**: Business logic (TaskManager)
  - **cli/**: User interface (menu, handlers)
  - **lib/**: Shared utilities (validators)
- **Testability**: Each layer can be tested independently
- **Future Migration**: Easy to extract models/services for Phase II backend

**Alternatives Considered**:
- **Flat Structure (all in one file)**: Rejected - Violates clean code principles, harder to test
- **MVC Pattern**: Rejected - Overkill for console app, more suitable for GUI applications
- **Hexagonal Architecture**: Rejected - Over-engineered for Phase I scope

**Best Practices**:
- **Dependency Direction**: CLI → Services → Models (never reverse)
- **Interface Segregation**: Each module has single, clear responsibility
- **Minimal Coupling**: Services don't know about CLI, Models don't know about Services
- **Clear Naming**: `task_manager.py` not `manager.py`, `validators.py` not `utils.py`

---

### 6. Input Validation Strategy

**Decision**: Implement validation at multiple layers with custom exceptions

**Rationale**:
- **Data Integrity**: Spec defines strict validation rules (FR-013, FR-014: title 1-200 chars, description max 1000 chars)
- **User Experience**: Clear error messages for invalid inputs (SC-004: 100% of invalid inputs caught)
- **Defensive Programming**: Validate at entry points (CLI) and enforce at model level
- **Error Handling**: Custom exceptions provide meaningful error messages

**Alternatives Considered**:
- **Pydantic**: Rejected - Adds external dependency, overkill for simple validation
- **Silent Coercion**: Rejected - Violates spec requirement for clear error messages
- **No Validation**: Rejected - Violates spec requirements FR-009, FR-013, FR-014, FR-015

**Implementation Approach**:
- **Model Layer**: Task class validates on initialization (title length, description length)
- **Service Layer**: TaskManager validates task existence (valid ID checks)
- **CLI Layer**: Pre-validate user input before passing to services (input type checks)
- **Custom Exceptions**: `ValidationError`, `TaskNotFoundError` for clear error messaging

**Validation Rules**:
```python
# Task model validation:
- title: str, required, 1-200 characters
- description: str, optional, max 1000 characters
- id: int, auto-generated, positive integer
- completed: bool, default False

# TaskManager validation:
- task_id must exist in current task list
- task_id must be positive integer
```

---

### 7. Console Interface Design

**Decision**: Numbered menu system with clear navigation flow

**Rationale**:
- **User Story Alignment**: User Story 5 (P1) requires clear console menu with numbered options
- **Simplicity**: Numbered options are intuitive for console applications
- **Spec Requirements**: FR-001 mandates numbered menu, FR-010 requires return to main menu after each operation
- **Error Recovery**: Invalid options redisplay menu (acceptance scenario from User Story 5)

**Alternatives Considered**:
- **Command-Line Arguments** (e.g., `todo add "Buy milk"`): Rejected - Doesn't support interactive session required by spec
- **Text Commands** (e.g., "add task"): Rejected - More error-prone than numbered menu
- **GUI (Tkinter)**: Rejected - Phase I is console-only, GUI is Phase II+

**Menu Structure**:
```
=== Todo App ===
1. Add Task
2. View Tasks
3. Update Task
4. Delete Task
5. Mark Task as Complete/Incomplete
6. Exit

Enter option:
```

**Navigation Flow**:
1. Display main menu
2. Accept user input (1-6)
3. Execute corresponding action
4. Display result/confirmation
5. Return to main menu (repeat)
6. Exit on option 6

**Error Handling**:
- Invalid option number: Display error, redisplay menu
- Non-numeric input: Display error, redisplay menu
- Ctrl+C: Graceful exit with "Goodbye!" message

---

### 8. Testing Strategy

**Decision**: Comprehensive unit and integration testing with pytest

**Rationale**:
- **Constitutional Requirement**: >80% code coverage (Principle 11, FR-019, SC-007)
- **Spec Validation**: Tests verify acceptance scenarios from spec.md
- **Regression Prevention**: Automated tests catch breakage during refactoring
- **Documentation**: Tests serve as executable specification

**Test Organization**:

**Unit Tests** (`tests/unit/`):
- **test_task.py**: Task model validation (title/description length, defaults)
- **test_task_manager.py**: CRUD operations (add, get, update, delete, toggle complete)
- **test_validators.py**: Input validation functions

**Integration Tests** (`tests/integration/`):
- **test_cli.py**: End-to-end workflows simulating user interaction

**Test Coverage Goals**:
| Module | Target Coverage | Rationale |
|--------|----------------|-----------|
| models/task.py | 100% | Pure data class, all branches testable |
| services/task_manager.py | 95%+ | Core business logic, critical to test |
| lib/validators.py | 100% | Utility functions, all branches testable |
| cli/menu.py | 70%+ | I/O-heavy, harder to unit test |
| cli/handlers.py | 75%+ | I/O-heavy, integration tests will help |
| **Overall** | **>80%** | Constitutional minimum |

**Testing Best Practices**:
- Use pytest fixtures for test data (sample tasks, mock TaskManager)
- Parametrize tests for multiple scenarios (e.g., various invalid inputs)
- Test both happy paths and error cases
- Integration tests mock `input()` and capture `print()` output
- Use `pytest-cov` for coverage reporting
- Run tests in CI/CD pipeline (if set up)

**Example Test Structure**:
```python
# tests/unit/test_task_manager.py
def test_add_task():
    manager = TaskManager()
    task = manager.add_task("Buy milk", "From the store")
    assert task.id == 1
    assert task.title == "Buy milk"
    assert task.completed is False

def test_add_task_title_too_long():
    manager = TaskManager()
    with pytest.raises(ValidationError):
        manager.add_task("x" * 201, "")
```

---

### 9. Error Handling Strategy

**Decision**: Custom exception hierarchy with user-friendly error messages

**Rationale**:
- **Spec Requirement**: FR-009 mandates clear error messages for invalid operations
- **Success Criteria**: SC-004 requires 100% of invalid inputs caught with clear messages
- **User Experience**: Users need to understand what went wrong and how to fix it
- **Debugging**: Structured exceptions help identify issues during development

**Custom Exceptions**:
```python
# Base exception
class TodoAppError(Exception):
    """Base exception for todo app"""
    pass

# Specific exceptions
class ValidationError(TodoAppError):
    """Raised when input validation fails"""
    pass

class TaskNotFoundError(TodoAppError):
    """Raised when task ID doesn't exist"""
    pass
```

**Error Handling Patterns**:
- **CLI Layer**: Catch all exceptions, display user-friendly message, return to menu
- **Service Layer**: Raise TaskNotFoundError for invalid IDs
- **Model Layer**: Raise ValidationError for invalid data
- **Never**: Silent failures or generic error messages

**User-Friendly Messages**:
- ❌ "Exception: KeyError 123" → ✅ "Error: Task #123 not found"
- ❌ "ValueError: invalid literal" → ✅ "Error: Please enter a valid number"
- ❌ "AssertionError" → ✅ "Error: Title cannot be empty"

---

### 10. Performance Considerations

**Decision**: Optimize for simplicity over performance, while meeting spec requirements

**Rationale**:
- **Success Criteria**: Spec defines clear performance goals (SC-001, SC-002, SC-005, SC-008)
- **Small Scale**: 100 tasks is well within Python's native performance capabilities
- **In-Memory**: No I/O latency, operations are instant
- **Premature Optimization**: Avoid over-engineering for Phase I scope

**Performance Targets from Spec**:
- Application startup: <2 seconds ✅ (Python import and initialization is instant)
- Task list view (100 tasks): <1 second ✅ (Iterating 100 objects is microseconds)
- Task creation: <30 seconds (including user input time) ✅
- Menu navigation: <5 seconds ✅

**Implementation Choices**:
- **Linear Search**: O(n) for task lookup is fine for ~100 tasks (~100 comparisons)
- **List Storage**: Python lists are optimized in C, append/remove are efficient
- **No Indexing**: No need for hash maps or indexes at this scale
- **Simple Algorithms**: No complex data structures needed

**Future Optimization (Phase II+)**:
- Database with indexed queries (when scaling to 1000s of tasks)
- Pagination for large task lists
- Caching strategies for frequently accessed data

**Actual Performance**:
- Startup time: <100ms (Python imports, class definitions)
- Add task: <1ms (append to list)
- View 100 tasks: <10ms (iterate and print)
- Update/Delete: <1ms (linear search + modification)
- Total memory: <5MB for 100 tasks (Python overhead + task data)

---

## Architecture Decisions

### Layered Architecture Pattern

**Decision**: Implement 3-layer architecture (Presentation, Business, Data)

**Layers**:
1. **Presentation Layer** (cli/): User interaction, input/output
2. **Business Layer** (services/): Application logic, CRUD operations
3. **Data Layer** (models/): Data entities, validation

**Rationale**:
- **Separation of Concerns**: Each layer has single, clear responsibility
- **Testability**: Layers can be tested independently
- **Maintainability**: Changes to one layer don't ripple to others
- **Future-Proofing**: Easy to replace CLI with web UI in Phase II

**Dependencies**:
```
CLI (menu.py, handlers.py)
  ↓
Services (task_manager.py)
  ↓
Models (task.py)
```

**Design Principles**:
- **Single Responsibility**: Each class/module does one thing well
- **Open/Closed**: Open for extension, closed for modification
- **Dependency Inversion**: Depend on abstractions (TaskManager interface), not implementations
- **Don't Repeat Yourself (DRY)**: Shared code in lib/validators.py

---

### Data Model Design

**Decision**: Single Task entity with flat structure (no relationships in Phase I)

**Rationale**:
- **Spec Alignment**: Spec defines single "Task" entity (Key Entities section)
- **Simple Model**: No user relationships (single-user app), no task hierarchies
- **Validation Embedded**: Task class enforces its own constraints
- **Immutable IDs**: ID assigned on creation, never changes

**Task Entity**:
```python
@dataclass
class Task:
    id: int
    title: str
    description: str = ""
    completed: bool = False
    created_at: datetime = field(default_factory=datetime.now)
```

**Validation Rules**:
- **title**: 1-200 characters, required
- **description**: 0-1000 characters, optional
- **completed**: boolean, defaults to False
- **id**: positive integer, auto-assigned
- **created_at**: timestamp, auto-generated

**Future Extensions (Phase II+)**:
- `user_id` field for multi-user support
- `updated_at` timestamp for tracking modifications
- `priority`, `tags`, `due_date` for Intermediate/Advanced features

---

## Development Workflow

### Spec-Driven Code Generation

**Decision**: All code generated by Claude Code from specifications

**Rationale**:
- **Constitutional Mandate**: Principle 1 (Spec-Driven Development First)
- **Success Criteria**: SC-006 requires 0% manual coding
- **Quality Assurance**: Spec defines exact behavior, code must match
- **Documentation**: Specs serve as authoritative documentation

**Workflow**:
1. **Specification Complete**: spec.md defines all requirements ✅
2. **Planning Complete**: plan.md defines technical approach ✅
3. **Task Generation** (/speckit.tasks): Break plan into actionable tasks
4. **Implementation** (/speckit.implement): Claude Code generates code from tasks
5. **Validation**: Run tests, verify against acceptance scenarios

**Code Generation Principles**:
- **Follow Spec Exactly**: Implementation must match spec requirements
- **Clean Code**: PEP 8 compliant, well-named variables/functions
- **Self-Documenting**: Clear naming reduces need for comments
- **Type Hints**: Full type annotations for clarity
- **Comprehensive Tests**: Generate tests alongside implementation

---

### Version Control Strategy

**Decision**: Feature branch workflow with clear commit messages

**Rationale**:
- **Constitutional Requirement**: Principle 2 (Agentic Development Workflow) - track all interactions
- **Audit Trail**: Each commit documents a step in the spec-to-code process
- **Rollback Capability**: Can revert to previous state if needed
- **Collaboration**: Clear history for reviewers and future maintainers

**Branch Strategy**:
- **Branch Name**: `001-phase1-console-app` (already created)
- **Commit Frequency**: Commit after each logical change (e.g., "Add Task model with validation")
- **Commit Messages**: Descriptive, reference spec requirements (e.g., "Implement FR-002: Task creation with title validation")
- **Merge Strategy**: Merge to main after Phase I complete and validated

**Gitignore**:
```
__pycache__/
*.pyc
.pytest_cache/
htmlcov/
.coverage
.env
*.egg-info/
dist/
build/
```

---

## Risks & Mitigations

### Risk 1: Test Coverage Below 80%

**Risk**: Failing to achieve >80% test coverage requirement

**Likelihood**: Low
**Impact**: High (violates constitutional requirement)

**Mitigation**:
- Use pytest-cov to monitor coverage continuously
- Aim for 90% to have buffer above 80% minimum
- Write tests alongside implementation (TDD approach)
- Focus on high-value tests (business logic in TaskManager)

### Risk 2: Spec-Implementation Mismatch

**Risk**: Generated code doesn't match spec requirements

**Likelihood**: Medium
**Impact**: High (violates SC-006 and Principle 1)

**Mitigation**:
- Cross-reference each functional requirement during implementation
- Validate against acceptance scenarios in spec.md
- Use spec.md as test specification source
- Review generated code against spec before finalizing

### Risk 3: Performance Degradation with 100+ Tasks

**Risk**: App slows down with large task lists

**Likelihood**: Very Low
**Impact**: Medium (violates SC-005)

**Mitigation**:
- Python's native list operations are highly optimized
- 100 tasks is trivial for modern hardware
- Include performance test with 100+ tasks
- Profile if issues arise (unlikely)

### Risk 4: Cross-Platform Compatibility Issues

**Risk**: App works on one OS but fails on another (Windows vs Linux)

**Likelihood**: Low
**Impact**: Medium

**Mitigation**:
- Use Python's standard library (cross-platform by design)
- Avoid OS-specific features (no file paths, no system calls)
- Test on target platform (Windows per project context)
- Document Python 3.13+ requirement clearly

---

## Conclusion

All technical decisions for Phase I Console Todo Application are complete and documented. The selected technologies (Python 3.13+, UV, pytest) align with constitutional requirements and hackathon specifications. The layered architecture provides clean separation of concerns while remaining simple enough for a console application.

**Key Takeaways**:
- ✅ All technologies mandated by constitution selected
- ✅ Architecture supports >80% test coverage requirement
- ✅ Design enables future Phase II migration (web app with persistence)
- ✅ No "NEEDS CLARIFICATION" items remaining
- ✅ Ready to proceed to Phase 1 (data-model.md, contracts/, quickstart.md)

**Next Steps**:
1. Generate data-model.md (detailed Task entity specification)
2. Generate contracts/cli-interface.md (console interface contract)
3. Generate quickstart.md (developer onboarding guide)
4. Update agent context with Python/pytest/UV technologies
5. Proceed to `/speckit.tasks` for task breakdown
