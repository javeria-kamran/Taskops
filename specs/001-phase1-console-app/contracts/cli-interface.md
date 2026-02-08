# CLI Interface Contract: Phase I Console Todo Application

**Feature**: Phase I Console Todo Application
**Date**: December 27, 2025
**Status**: Complete
**Contract Type**: Console User Interface

## Overview

This contract defines the console interface behavior for the Phase I Todo Application. It specifies the exact user interactions, menu structure, input/output formats, and error handling for all 5 Basic Level operations.

---

## Main Menu

### Display Format

```
====================================
           Todo Application
====================================

1. Add Task
2. View Tasks
3. Update Task
4. Delete Task
5. Mark Task as Complete/Incomplete
6. Exit

Enter your choice (1-6):
```

### Behavior

**Initial Display**:
- Shows immediately on application startup (FR-001)
- Startup time must be <2 seconds (SC-008)

**Re-Display**:
- After every operation completes (FR-010)
- After invalid option entered (User Story 5, acceptance scenario 3)
- Loop continues until user selects option 6 (Exit)

**Input Validation**:
- Accept only integers 1-6
- Non-numeric input → Error message + redisplay menu
- Out of range (0, 7, etc.) → Error message + redisplay menu

**Error Message Format**:
```
Invalid option. Please enter a number between 1 and 6.

[Menu redisplays]
```

---

## Operation 1: Add Task

### User Flow

**From Main Menu**: User selects option 1

**Step 1 - Title Input**:
```
Enter task title (1-200 characters):
```

**Step 2 - Description Input**:
```
Enter task description (optional, max 1000 characters):
```

**Step 3 - Confirmation**:
```
✓ Task #[ID] added successfully!
  Title: [USER_TITLE]
  Description: [USER_DESCRIPTION or "None"]
  Status: Pending

Press Enter to continue...
```

**Return**: Main menu

### Input Validation

**Title Validation** (FR-002, FR-013):
- **Empty Input**: Error → "Error: Title cannot be empty."
- **Whitespace Only**: Error → "Error: Title cannot be empty."
- **Too Long (>200 chars)**: Error → "Error: Title must be 200 characters or less."
- **Valid Input**: Accept and proceed

**Description Validation** (FR-002, FR-014):
- **Empty Input**: Accept as empty description (optional field)
- **Too Long (>1000 chars)**: Error → "Error: Description must be 1000 characters or less."
- **Valid Input**: Accept and proceed

### Error Handling

**Validation Error Flow**:
```
Enter task title (1-200 characters):
> [USER_INPUT_TOO_LONG]

Error: Title must be 200 characters or less.

Enter task title (1-200 characters):
> [USER_INPUT_VALID]

[Proceeds to description input]
```

**Retry Mechanism**:
- Invalid input → Display error → Re-prompt for same field
- User can retry indefinitely until valid input provided
- No option to cancel (user can provide minimal valid input to proceed, then delete task)

### Examples

**Example 1: Minimal Valid Task**
```
Enter your choice (1-6): 1

Enter task title (1-200 characters):
> Buy milk

Enter task description (optional, max 1000 characters):
>

✓ Task #1 added successfully!
  Title: Buy milk
  Description: None
  Status: Pending

Press Enter to continue...
```

**Example 2: Full Task with Description**
```
Enter your choice (1-6): 1

Enter task title (1-200 characters):
> Complete Phase I console app

Enter task description (optional, max 1000 characters):
> Build in-memory Python console application with 5 Basic Level CRUD operations for task management.

✓ Task #2 added successfully!
  Title: Complete Phase I console app
  Description: Build in-memory Python console application with 5 Basic Level CRUD operations for task management.
  Status: Pending

Press Enter to continue...
```

**Example 3: Validation Error**
```
Enter your choice (1-6): 1

Enter task title (1-200 characters):
>

Error: Title cannot be empty.

Enter task title (1-200 characters):
> Call mom

Enter task description (optional, max 1000 characters):
>

✓ Task #3 added successfully!
  Title: Call mom
  Description: None
  Status: Pending

Press Enter to continue...
```

---

## Operation 2: View Tasks

### User Flow

**From Main Menu**: User selects option 2

**Display All Tasks**:
```
====================================
           All Tasks
====================================

Task #1: [✓] Buy milk
         Created: 2025-12-27 14:30:00
         Description: None

Task #2: [ ] Complete Phase I console app
         Created: 2025-12-27 14:31:15
         Description: Build in-memory Python console application...

Task #3: [ ] Call mom
         Created: 2025-12-27 14:32:00
         Description: None

====================================
Total: 3 tasks (1 completed, 2 pending)

Press Enter to continue...
```

**Return**: Main menu

### Empty List Display

**No Tasks Exist** (FR-012):
```
====================================
           All Tasks
====================================

No tasks found.

Press Enter to continue...
```

### Display Format Rules

**Status Indicator**:
- Completed task: `[✓]` before title
- Pending task: `[ ]` before title

**Description Display**:
- If description is empty: Show `"None"`
- If description is long (>50 chars): Show first 50 chars + `"..."`
- Full description visible (no truncation required in Phase I)

**Timestamp Format**:
- `YYYY-MM-DD HH:MM:SS` (24-hour format)
- Example: `2025-12-27 14:30:00`

**Summary Line**:
- Show total count
- Show count of completed and pending tasks
- Format: `"Total: [N] tasks ([X] completed, [Y] pending)"`

### Performance

**Performance Requirement** (SC-002):
- Display time for 100 tasks: <1 second
- Instant display for typical usage (<20 tasks)

---

## Operation 3: Update Task

### User Flow

**From Main Menu**: User selects option 3

**Step 1 - Task Selection**:
```
Enter task ID to update:
```

**Step 2 - Current Task Display**:
```
Current Task:
  Title: [CURRENT_TITLE]
  Description: [CURRENT_DESCRIPTION]

Enter new title (press Enter to keep current):
```

**Step 3 - Title Update**:
- If user presses Enter (empty input): Keep current title
- If user enters text: Validate and update title

**Step 4 - Description Update**:
```
Enter new description (press Enter to keep current):
```
- If user presses Enter (empty input): Keep current description
- If user enters text: Validate and update description

**Step 5 - Confirmation**:
```
✓ Task #[ID] updated successfully!
  New Title: [UPDATED_TITLE]
  New Description: [UPDATED_DESCRIPTION or "None"]

Press Enter to continue...
```

**Return**: Main menu

### Input Validation

**Task ID Validation** (FR-015):
- **Non-numeric**: Error → "Error: Please enter a valid task ID number."
- **Task Not Found**: Error → "Error: Task #[ID] not found."
- **Valid ID**: Proceed to update prompts

**Title Update Validation**:
- **Empty Input (Enter only)**: Keep current title (no error)
- **Whitespace Only**: Error → "Error: Title cannot be empty."
- **Too Long (>200 chars)**: Error → "Error: Title must be 200 characters or less."
- **Valid Input**: Update title

**Description Update Validation**:
- **Empty Input (Enter only)**: Keep current description (no error)
- **Too Long (>1000 chars)**: Error → "Error: Description must be 1000 characters or less."
- **Valid Input**: Update description

### Examples

**Example 1: Update Title Only**
```
Enter your choice (1-6): 3

Enter task ID to update: 1

Current Task:
  Title: Buy milk
  Description: None

Enter new title (press Enter to keep current):
> Buy milk and eggs

Enter new description (press Enter to keep current):
>

✓ Task #1 updated successfully!
  New Title: Buy milk and eggs
  New Description: None

Press Enter to continue...
```

**Example 2: Update Description Only**
```
Enter your choice (1-6): 3

Enter task ID to update: 2

Current Task:
  Title: Complete Phase I console app
  Description: Build in-memory Python console application...

Enter new title (press Enter to keep current):
>

Enter new description (press Enter to keep current):
> Build Python 3.13+ console app with UV package manager, pytest testing, and >80% coverage.

✓ Task #2 updated successfully!
  New Title: Complete Phase I console app
  New Description: Build Python 3.13+ console app with UV package manager, pytest testing, and >80% coverage.

Press Enter to continue...
```

**Example 3: Task Not Found**
```
Enter your choice (1-6): 3

Enter task ID to update: 999

Error: Task #999 not found.

Press Enter to continue...
[Returns to main menu]
```

---

## Operation 4: Delete Task

### User Flow

**From Main Menu**: User selects option 4

**Step 1 - Task Selection**:
```
Enter task ID to delete:
```

**Step 2 - Confirmation**:
```
Are you sure you want to delete this task?
  Task #[ID]: [TITLE]
Enter 'yes' to confirm or 'no' to cancel:
```

**Step 3a - Confirmed Deletion**:
```
✓ Task #[ID] deleted successfully.

Press Enter to continue...
```

**Step 3b - Cancelled Deletion**:
```
Deletion cancelled.

Press Enter to continue...
```

**Return**: Main menu

### Input Validation

**Task ID Validation** (FR-015):
- **Non-numeric**: Error → "Error: Please enter a valid task ID number."
- **Task Not Found**: Error → "Error: Task #[ID] not found."
- **Valid ID**: Proceed to confirmation

**Confirmation Validation**:
- **"yes" (case-insensitive)**: Proceed with deletion
- **"no" (case-insensitive)**: Cancel deletion
- **Any other input**: Treat as "no" and cancel

### Examples

**Example 1: Successful Deletion**
```
Enter your choice (1-6): 4

Enter task ID to delete: 3

Are you sure you want to delete this task?
  Task #3: Call mom
Enter 'yes' to confirm or 'no' to cancel: yes

✓ Task #3 deleted successfully.

Press Enter to continue...
```

**Example 2: Cancelled Deletion**
```
Enter your choice (1-6): 4

Enter task ID to delete: 1

Are you sure you want to delete this task?
  Task #1: Buy milk and eggs
Enter 'yes' to confirm or 'no' to cancel: no

Deletion cancelled.

Press Enter to continue...
```

**Example 3: Task Not Found**
```
Enter your choice (1-6): 4

Enter task ID to delete: 999

Error: Task #999 not found.

Press Enter to continue...
[Returns to main menu]
```

---

## Operation 5: Mark Task as Complete/Incomplete

### User Flow

**From Main Menu**: User selects option 5

**Step 1 - Task Selection**:
```
Enter task ID to toggle completion:
```

**Step 2a - Mark as Complete** (if currently pending):
```
✓ Task #[ID] marked as complete!
  Title: [TITLE]
  Status: Completed

Press Enter to continue...
```

**Step 2b - Mark as Incomplete** (if currently completed):
```
✓ Task #[ID] marked as incomplete.
  Title: [TITLE]
  Status: Pending

Press Enter to continue...
```

**Return**: Main menu

### Input Validation

**Task ID Validation** (FR-015):
- **Non-numeric**: Error → "Error: Please enter a valid task ID number."
- **Task Not Found**: Error → "Error: Task #[ID] not found."
- **Valid ID**: Toggle completion status

### Behavior

**Toggle Logic** (FR-008):
- If task.completed is `False` → Set to `True` (mark complete)
- If task.completed is `True` → Set to `False` (mark incomplete)
- No confirmation required (toggle is non-destructive)

### Examples

**Example 1: Mark Pending Task as Complete**
```
Enter your choice (1-6): 5

Enter task ID to toggle completion: 1

✓ Task #1 marked as complete!
  Title: Buy milk and eggs
  Status: Completed

Press Enter to continue...
```

**Example 2: Mark Completed Task as Incomplete**
```
Enter your choice (1-6): 5

Enter task ID to toggle completion: 1

✓ Task #1 marked as incomplete.
  Title: Buy milk and eggs
  Status: Pending

Press Enter to continue...
```

**Example 3: Task Not Found**
```
Enter your choice (1-6): 5

Enter task ID to toggle completion: 999

Error: Task #999 not found.

Press Enter to continue...
[Returns to main menu]
```

---

## Operation 6: Exit

### User Flow

**From Main Menu**: User selects option 6

**Exit Confirmation**:
```
Are you sure you want to exit? All data will be lost. (yes/no):
```

**Confirmed Exit**:
```
Thank you for using Todo Application!
Goodbye!

[Application terminates]
```

**Cancelled Exit**:
```
[Returns to main menu]
```

### Input Validation

**Confirmation Validation**:
- **"yes" (case-insensitive)**: Exit application
- **"no" (case-insensitive)**: Return to main menu
- **Any other input**: Treat as "no" and return to main menu

### Graceful Termination

**Expected Behavior** (FR-011):
- Clean exit with exit code 0
- No error messages or stack traces
- All resources properly released (though minimal in console app)

**Data Loss Warning**:
- Remind user that in-memory data will be lost (expected Phase I behavior)
- This is not an error, it's a known limitation of Phase I

### Examples

**Example 1: Confirmed Exit**
```
Enter your choice (1-6): 6

Are you sure you want to exit? All data will be lost. (yes/no): yes

Thank you for using Todo Application!
Goodbye!
```

**Example 2: Cancelled Exit**
```
Enter your choice (1-6): 6

Are you sure you want to exit? All data will be lost. (yes/no): no

[Main menu redisplays]
```

---

## Error Handling

### Standard Error Message Format

**All errors follow consistent format**:
```
Error: [Specific error message]

[Appropriate next step or retry prompt]
```

### Error Categories

**Validation Errors**:
- Title too long: `"Error: Title must be 200 characters or less."`
- Title empty: `"Error: Title cannot be empty."`
- Description too long: `"Error: Description must be 1000 characters or less."`

**Not Found Errors** (FR-015):
- Task not found: `"Error: Task #[ID] not found."`

**Input Type Errors**:
- Non-numeric task ID: `"Error: Please enter a valid task ID number."`
- Invalid menu option: `"Invalid option. Please enter a number between 1 and 6."`

### Exception Handling

**Internal Errors** (should not occur in normal operation):
```
An unexpected error occurred. Please try again.
Error details: [exception message]

Press Enter to continue...
[Returns to main menu]
```

**Success Criteria** (SC-010):
- Zero crashes during normal operation (valid inputs through menu system)
- All expected errors caught and handled gracefully

---

## Special Behaviors

### Ctrl+C (Interrupt Signal)

**Expected Behavior**:
```
^C
Application interrupted by user.
Goodbye!

[Application terminates with exit code 130]
```

**Implementation**:
- Catch `KeyboardInterrupt` exception
- Display graceful exit message
- Terminate cleanly (no stack trace shown to user)

### End-of-File (EOF) Input

**Expected Behavior** (e.g., piped input ends):
```
Unexpected end of input.
Goodbye!

[Application terminates with exit code 0]
```

---

## Performance Requirements

**From Success Criteria**:

| Operation | Performance Target | Success Criteria |
|-----------|-------------------|------------------|
| Application Startup | <2 seconds | SC-008 |
| View Tasks (100 tasks) | <1 second | SC-002, SC-005 |
| Add Task | <30 seconds total (including user input) | SC-001 |
| Menu Navigation | <5 seconds between options | SC-009 |
| Any CRUD Operation | Instant (<1 second excluding user input) | Implied by in-memory operations |

---

## Accessibility Considerations

**Plain Text Only**:
- No ANSI color codes (for maximum terminal compatibility)
- Simple ASCII box-drawing or plain text separators
- Compatible with screen readers

**Clear Instructions**:
- Every input prompt clearly states expected format
- Error messages provide actionable feedback
- Success messages confirm what action was taken

**Keyboard Only**:
- No mouse interaction required (console app)
- All operations accessible via number keys and text input

---

## Contract Validation

### How to Test This Contract

**Manual Testing**:
1. Run application and verify main menu displays correctly
2. Test each operation (1-6) with valid inputs
3. Test each operation with invalid inputs (verify error messages)
4. Test edge cases (empty list, long titles, special characters)
5. Test Ctrl+C interrupt handling
6. Verify performance targets are met

**Automated Testing** (`tests/integration/test_cli.py`):
- Mock `input()` function to simulate user input
- Capture `print()` output to verify display format
- Assert on output strings to verify messages match contract
- Test all user flows defined in this contract

### Contract Compliance Checklist

- [ ] Main menu displays with numbered options 1-6
- [ ] Each operation returns to main menu after completion
- [ ] Invalid menu options show error and redisplay menu
- [ ] Add Task validates title (1-200 chars) and description (≤1000 chars)
- [ ] View Tasks displays all tasks with status indicators
- [ ] View Tasks shows "No tasks found" when list is empty
- [ ] Update Task allows keeping current values with Enter key
- [ ] Delete Task requires "yes" confirmation
- [ ] Toggle Completion changes status (Pending ↔ Completed)
- [ ] Exit requires "yes" confirmation and warns about data loss
- [ ] All errors display user-friendly messages (no stack traces)
- [ ] Task Not Found errors display for invalid IDs
- [ ] Ctrl+C exits gracefully with message
- [ ] All operations complete in <1 second (excluding user input time)

---

## Conclusion

This CLI interface contract defines the complete user interaction for the Phase I Console Todo Application. All inputs, outputs, error messages, and behaviors are specified to ensure consistent implementation via Claude Code.

**Key Contract Elements**:
- ✅ Numbered menu with 6 operations
- ✅ Clear input prompts with validation rules
- ✅ Consistent error message format
- ✅ Graceful error handling (no crashes)
- ✅ Confirmation for destructive actions (delete, exit)
- ✅ User-friendly success messages
- ✅ Performance targets specified and achievable
- ✅ Accessibility via plain text output

**Ready for Implementation**: This contract provides sufficient detail for automated code generation via `/speckit.tasks` and `/speckit.implement` commands.
