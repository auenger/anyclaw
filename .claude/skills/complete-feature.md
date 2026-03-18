---
description: 'Complete a feature by committing code, merging to main, cleaning up, and archiving.'
---

# Skill: complete-feature

Complete a feature by committing changes, merging to main branch, cleaning up worktree, and archiving documentation.

## When to use this skill

Use this skill when the user wants to finish and merge a completed feature.

## Parameters

- `feature-id`: The feature ID to complete (required)
- `--skip-verify`: Skip verification step (use with caution)
- `--keep-worktree`: Keep worktree after completion (for debugging)

## Execution Steps

### Step 1: Pre-flight Checks

- Verify feature is in active list
- Check all tasks are completed (unless --skip-verify)
- Verify tests pass (unless --skip-verify)

### Step 2: Review Changes

Switch to worktree and show:
- Files changed
- New files
- Deleted files
- Diff summary

Ask for confirmation before proceeding.

### Step 3: Commit Changes

In worktree:
```bash
git add .
git commit -m "feat({id}): {commit_message}"
```

Commit message format:
```
feat({id}): {feature_name}

{detailed_description}
```

### Step 4: Merge to Main

Switch to main branch and merge:
```bash
cd {repo_path}
git checkout {main_branch}
git merge feature/{slug} --no-ff
```

### Step 5: Cleanup

**Remove worktree:**
```bash
git worktree remove ../{project}-{slug}
```

**Remove feature branch:**
```bash
git branch -d feature/{slug}
```

**Archive feature:**
```bash
mv features/active-{id} features/archive/done-{id}
```

### Step 6: Update Queue

Update `feature-workflow/queue.yaml`:
- Remove from active list
- Add to archive-log.yaml

### Step 7: Generate Completion Report

Output summary of work done.

## Output

```
🎉 Feature Completed: {id}

Summary:
  Name: {feature_name}
  Duration: {time_from_start}
  Commits: {commit_count}
  Files changed: {file_count}

Git:
  Branch: feature/{slug}
  Merged to: {main_branch}
  Commit: {commit_hash}

Archive:
  Location: features/archive/done-{id}

Next Features:
  - {next_feature_1} (priority: {p1})
  - {next_feature_2} (priority: {p2})

Auto-start next feature? (y/n)
```

## Error Handling

| Error | Description | Solution |
|-------|-------------|----------|
| NOT_ACTIVE | Feature not in active list | Check feature status |
| TASKS_INCOMPLETE | Not all tasks completed | Run implement-feature first |
| TESTS_FAILED | Tests still failing | Fix tests before completing |
| MERGE_CONFLICT | Merge conflict detected | Resolve conflicts manually |
| WORKTREE_BUSY | Worktree has uncommitted changes | Commit or stash changes |

## Rollback Strategy

If completion fails after merge:
- Feature remains completed in queue
- Worktree is kept for inspection
- User can manually clean up

If completion fails before merge:
- Worktree is preserved
- Feature remains active
- User can fix and retry
