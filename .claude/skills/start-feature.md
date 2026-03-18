---
description: 'Start development on a feature - create branch and worktree.'
---

# Skill: start-feature

Start development on a feature by creating a Git branch and worktree. Supports parent/child feature relationships and dependency chains.

## When to use this skill

Use this skill when the user wants to start development on a pending feature.

## Execution Steps

### Step 1: Pre-flight Checks

**Check 1: Feature exists**
- Find the feature in `queue.yaml` pending list
- If not found, return NOT_FOUND error
- If found in blocked list, return BLOCKED error

**Check 2: Parallelism limit**
- Read `config.yaml` max_concurrent
- Count active features in `queue.yaml`
- If `active.count >= max_concurrent`: return LIMIT_EXCEEDED error

**Check 3: Dependencies satisfied**
- Check feature's dependencies field
- Verify all dependencies are completed (in archive-log.yaml)
- If unsatisfied dependencies, return DEPENDENCY_ERROR

**Check 4: Parent feature status (for child features)**
- If feature has a parent, check if parent is active or completed
- If parent is pending/blocked: return PENDING_DEPENDENCY error

**Check 5: Child features status (for parent features)**
- If feature has children, check status of children
- If any children are active, return CHILD_ACTIVE error

### Step 2: Get Feature Info

Read from `queue.yaml` pending list:
- name, priority, dependencies, parent, children, size

### Step 3: Rename Directory

```bash
mv features/pending-{id} features/active-{id}
```

### Step 4: Create Git Branch

**Get Config Values** from `config.yaml`:
- project.main_branch (default: "main")
- git.remote (default: "origin")

**Create Branch:**
```bash
git checkout {main_branch}
git pull {remote} {main_branch}
git checkout -b feature/{slug}
```

Branch name format: `{branch_prefix}/{slug}`

### Step 5: Create Worktree

```bash
git checkout {main_branch}
git worktree add ../{project}-{slug} feature/{slug}
```

Worktree path: `{worktree_base}/{worktree_prefix}-{slug}`

### Step 6: Update Queue

Update `feature-workflow/queue.yaml`:
- Remove from pending list
- Add to active list with branch and worktree info

## Output

```
🚀 feature {id} started!

branch: feature/{slug}
worktree: ../{project}-{slug}
size: {size}
parent: {parent or "none"}
children: {children or "none"}

start developing:
  cd ../{project}-{slug}

view tasks:
  cat features/active-{id}/task.md
```

## Error Handling

| Error | Description | Solution |
|-------|-------------|----------|
| NOT_FOUND | Feature not in pending list | Check id, use list-features |
| BLOCKED | Feature is blocked | Check reason, use unblock-feature |
| LIMIT_EXCEEDED | Parallel limit reached | Complete active features or increase limit |
| DEPENDENCY_ERROR | Dependencies not satisfied | Complete dependent features first |
| PENDING_DEPENDENCY | Parent feature not started | Start parent feature first |
| CHILD_ACTIVE | Child features still active | Wait for children to complete |
| BRANCH_EXISTS | Branch already exists | Delete old branch or use different name |
| WORKTREE_ERROR | Worktree creation failed | Check path permissions |
