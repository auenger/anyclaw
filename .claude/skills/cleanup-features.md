---
description: 'Clean up old or completed feature data and manage disk space.'
---

# Skill: cleanup-features

Clean up old feature data, archived features, and manage disk space used by the feature workflow system.

## When to use this skill

Use this skill when the user wants to clean up old feature data, free up disk space, or manage archived features.

## Parameters

- `--older-than=<days>`: Clean features older than specified days
- `--keep-last=<n>`: Keep only the last N completed features
- `--dry-run`: Show what would be deleted without actually deleting
- `--confirm`: Skip confirmation prompt

## Execution Steps

### Step 1: Scan Feature Data

Scan for cleanable data:
- `features/archive/done-*` directories
- Old worktrees in parent directory
- Archived data in `archive-log.yaml`

### Step 2: Calculate Size

Calculate disk space usage:
- Size of each archived feature
- Total size of all archived features
- Size of old worktrees

### Step 3: Apply Filters

Apply filters based on parameters:
- `--older-than`: Only features older than N days
- `--keep-last`: Keep only the last N features
- Combined: Keep last N that are newer than threshold

### Step 4: Preview Deletions

Show what will be deleted:
- List of features to be removed
- Total size to be freed
- Confirmation prompt (unless --confirm)

### Step 5: Execute Cleanup

If confirmed:
1. Remove archived feature directories
2. Remove old worktrees
3. Update archive-log.yaml
4. Update queue.yaml metadata

## Output

### Dry Run Output

```
🧹 Feature Cleanup Preview

Scanned features: 15
Matching filters: 8

Features to be removed:
  ┌──────────────┬─────────────┬──────────┬────────────┐
  │ ID           │ Completed   │ Size     │ Age        │
  ├──────────────┼─────────────┼──────────┼────────────┤
  │ feat-old-1   │ 2024-01-15  │ 2.3 MB   │ 60 days    │
  │ feat-old-2   │ 2024-02-01  │ 1.8 MB   │ 45 days    │
  │ feat-old-3   │ 2024-02-10  │ 3.1 MB   │ 35 days    │
  └──────────────┴─────────────┴──────────┴────────────┘

Total space to be freed: 7.2 MB

Worktrees to be removed:
  - ../OA_Tool-feat-old-1 (2.3 MB)
  - ../OA_Tool-feat-old-2 (1.8 MB)

Total worktree space: 4.1 MB

Grand total: 11.3 MB

This is a dry run. No changes will be made.
Use --confirm to actually delete these features.
```

### Confirmed Cleanup Output

```
🧹 Cleaning Up Features...

Removing archived features:
  ✓ feat-old-1 removed
  ✓ feat-old-2 removed
  ✓ feat-old-3 removed

Removing worktrees:
  ✓ ../OA_Tool-feat-old-1 removed
  ✓ ../OA_Tool-feat-old-2 removed

Updating records:
  ✓ archive-log.yaml updated
  ✓ queue.yaml updated

Cleanup Complete!

Space freed: 11.3 MB
Features removed: 3
Worktrees removed: 2

Remaining features: 12 (last 30 days)
```

## Error Handling

| Error | Description | Solution |
|-------|-------------|----------|
| NO_FEATURES | No features match criteria | Adjust filters |
| WORKTREE_ERROR | Cannot remove worktree | Remove manually |
| ARCHIVE_ERROR | Cannot update archive-log | Check permissions |
| ACTIVE_FEATURE | Attempted to clean active feature | Skip active features |

## Safety Features

1. **Never delete active features**
2. **Never delete pending features**
3. **Always show preview unless --confirm**
4. **Keep minimum of 5 most recent features**
5. **Backup archive-log before cleanup**

## Examples

```
/feature-cleanup --dry-run --older-than=30

/feature-cleanup --confirm --older-than=60

/feature-cleanup --confirm --keep-last=20

/feature-cleanup --confirm --keep-last=10 --older-than=30
```
