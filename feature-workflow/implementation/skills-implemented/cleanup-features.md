---
description: 'Clean up orphaned worktrees and fix inconsistent state.'
---

# Skill: cleanup-features

Detect and clean up orphaned worktrees, missing references, and inconsistent state.

## Usage

```
/cleanup-features              # Check and prompt for cleanup
/cleanup-features --auto       # Automatically clean up
/cleanup-features --dry-run    # Show what would be cleaned
```

## What It Checks

1. **Orphaned Worktrees**: Worktrees that exist but aren't in queue.yaml
2. **Missing Worktrees**: Worktrees recorded in queue.yaml but don't exist
3. **Orphaned Directories**: Feature directories not in queue.yaml
4. **Missing Directories**: Features in queue.yaml but directory doesn't exist

## Execution Steps

### Step 1: Collect Information

```bash
# Get recorded worktrees from queue.yaml
# Get actual worktrees: git worktree list
# Scan features/ directory
```

### Step 2: Detect Anomalies

Compare recorded vs actual:
- `orphaned_worktrees` = actual - recorded
- `missing_worktrees` = recorded - actual
- `orphaned_dirs` = actual dirs - recorded
- `missing_dirs` = recorded - actual dirs

### Step 3: Display Results

If no issues:
```
┌─────────────────────────────────────────────────────────────────┐
│ Cleanup Check                                                    │
├─────────────────────────────────────────────────────────────────┤
│ ✅ Everything is clean                                          │
│                                                                 │
│ Worktrees: 1 recorded / 1 actual                                │
│ Directories: 3 recorded / 3 actual                              │
└─────────────────────────────────────────────────────────────────┘
```

If issues found:
```
┌─────────────────────────────────────────────────────────────────┐
│ Cleanup Check                                                    │
├─────────────────────────────────────────────────────────────────┤
│ ⚠️ Found issues                                                 │
│                                                                 │
│ Orphaned Worktrees (1):                                         │
│   ../OA_Tool-feat-old (not in queue)                            │
│                                                                 │
│ Missing Worktrees (1):                                          │
│   feat-dashboard: recorded but doesn't exist                    │
│                                                                 │
│ Orphaned Directories (1):                                       │
│   active-feat-obsolete (not in queue)                           │
└─────────────────────────────────────────────────────────────────┘

Actions:
1. [Delete] orphaned worktree: ../OA_Tool-feat-old
2. [Fix] feat-dashboard: remove worktree reference
3. [Archive] orphaned directory: active-feat-obsolete

Execute? (all/1,2,3/none):
```

### Step 4: Execute Cleanup

Based on user selection, perform cleanup actions.

## Cleanup Actions

| Issue | Action Options |
|-------|---------------|
| Orphaned worktree | Delete / Keep and add to queue |
| Missing worktree | Remove from queue / Mark for repair |
| Orphaned pending-* | Archive / Delete / Add to queue |
| Orphaned active-* | Archive / Delete / Check worktree |

## Output

### Dry Run

```
🔍 Dry Run - Actions that would be executed:

[DELETE] git worktree remove ../OA_Tool-feat-old
[UPDATE] queue.yaml: remove feat-dashboard worktree reference
[MOVE] active-feat-obsolete → archive/

Run without --dry-run to execute.
```

### Cleanup Complete

```
✅ Cleanup complete

- Deleted 1 orphaned worktree
- Fixed 1 missing worktree reference
- Archived 1 orphaned directory
```

## Error Codes

| Code | Description |
|------|-------------|
| GIT_ERROR | Git operation failed |
| PERMISSION_ERROR | Cannot delete files |

## Examples

```
/cleanup-features
→ Check and prompt for cleanup

/cleanup-features --dry-run
→ Show what would be cleaned without doing it

/cleanup-features --auto
→ Automatically clean up all issues
```

## Notes

1. Always use --dry-run first to preview changes
2. Deletion is irreversible
3. Run /list-features after cleanup to verify state
