---
description: 'Implement feature code by reading spec, analyzing tasks, and writing code in worktree.'
---

# Skill: implement-feature

Implement the feature by reading specifications, analyzing tasks, and writing code in the worktree.

## Usage

```
/implement-feature <feature-id> [--task=<index>] [--dry-run]
```

Parameters:
- `feature-id`: The feature ID (required)
- `--task=<index>`: Implement only a specific task (optional)
- `--dry-run`: Analyze only, don't implement (optional)

## Pre-flight Checks

- Feature must be in `queue.yaml` active list
- Worktree must exist

## Execution Steps

### Step 1: Read Feature Documents

Read `features/active-{id}/spec.md`:
- Feature description
- Context analysis (reference code, related docs)
- Acceptance criteria

Read `features/active-{id}/task.md`:
- Task list
- Task status (completed/pending)

### Step 2: Analyze Tasks

Parse the task list and:
- Identify task dependencies
- Determine implementation order
- List reference code/docs needed

Output:
```
📋 Analysis Complete

Pending tasks: 4
Suggested order:
  1. Implement registration API
  2. Implement login API
  3. Implement logout API
  4. Add auth middleware

Reference code:
  - src/models/user.ts
  - src/middleware/

Start implementation? (y/n)
```

### Step 3: Confirm Plan

Display implementation plan and ask for confirmation.

Options:
- `y` - Start implementation
- `n` - Cancel
- `edit` - Modify plan

### Step 4: Implement Code

Switch to worktree directory and implement each task:

```
cd {worktree_path}
```

For each task:
1. Implement the code
2. Update `task.md` status (check the checkbox)
3. Add brief notes about implementation

Implementation guidelines:
- Reference existing code style
- Reuse existing components and utilities
- Follow project directory structure
- Add necessary error handling
- Add necessary type definitions

### Step 5: Self-Test

- Run existing tests if available
- Manually verify core functionality
- Check code quality
- Record test results

### Step 6: Generate Report

```
✅ Implementation Complete

Completed tasks: 4/4
Files changed: 5

Testing: 12 passed, 0 failed

Next steps:
  - Run /verify-feature {id} to validate
  - Or run /complete-feature {id} to finish
```

## Output

### Analysis Phase
```yaml
status: analyzed
feature:
  id: feat-auth
  name: User Authentication

analysis:
  total_tasks: 5
  completed: 1
  pending: 4
  suggested_order: [2, 3, 4, 5]
```

### Implementation Phase
```yaml
status: implemented
feature:
  id: feat-auth

implementation:
  completed_tasks:
    - index: 2
      name: Implement registration API
      files:
        - src/api/auth/register.ts (new)
        - src/services/user.ts (modified)
  files_changed:
    new: 3
    modified: 2

testing:
  tests_run: true
  passed: 12
  failed: 0
```

## Error Handling

| Error | Description | Solution |
|-------|-------------|----------|
| NOT_ACTIVE | Feature not in active list | Run /start-feature first |
| WORKTREE_NOT_FOUND | Worktree doesn't exist | Run /start-feature first |
| SPEC_PARSE_ERROR | Cannot parse spec.md | Check document format |
| IMPLEMENTATION_FAILED | Implementation failed | Check details, fix manually |

## Notes

1. **No auto-commit** - Code stays in worktree, not committed
2. **Reference existing code** - Prioritize context mentioned in spec
3. **Keep docs in sync** - Update task.md status during implementation
4. **Resume support** - Can interrupt and continue later
