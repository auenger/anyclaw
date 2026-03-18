---
description: 'Start development on a feature - create branch and worktree.'
---

# Skill: start-feature

Start development on a feature by creating a Git branch and worktree.
 Supports parent/child feature relationships and dependency chains.

## Usage

```
/start-feature <feature-id>
```

## Pre-flight checks

### check 1: Feature exists
- Find the feature in `queue.yaml` pending list
- If not found, return NOT_FOUND error

- if found in blocked list, return BLOCKED error

### Check 2: Parallelism limit
- Read `config.yaml` max_concurrent
- Count active features in `queue.yaml`
- if `active.count >= max_concurrent`: return LIMIT_EXCEEDED error

- Show current active features

### check 3: Dependencies satisfied
- Check feature's dependencies field
- Verify all dependencies are completed (in archive-log.yaml)
- if unsatisfied dependencies:
  - Return DEPENDENCY_ERROR error
  - Show which dependencies are missing

### check 4: Parent feature status (for child features)
- If feature has a parent:
  - check if parent is active or completed
  - if parent is pending/blocked: return PENDING_DEPENDENCY error
  - suggest: "Start parent feature first"

### check 5: Child features status (for parent features)
- if feature has children:
  - check status of children
  - if any children are active:
    - return CHILD_ACTIVE error
    - note: "Cannot start while child features are in development"

## execution steps

### step 1: get feature info
Read from `queue.yaml` pending list:
- name
- priority
- dependencies
- parent
- children
- size

### step 2: rename directory
```bash
mv features/pending-{id} features/active-{id}
```

### step 3: create git branch

**Step 3.1: Get Config Values**

Read from `config.yaml`:
```yaml
project:
  main_branch: main    # Default target branch

git:
  remote: origin       # Remote name
```

```bash
MAIN_BRANCH={config.project.main_branch || "main"}
REMOTE={config.git.remote || "origin"}
```

**Step 3.2: Create Branch**

```bash
cd {repo_path}  # if repo_path configured, switch to repo directory first
git checkout {main_branch}
git pull {remote} {main_branch}  # Pull latest changes first
git checkout -b feature/{slug}
```

branch name format: `{branch_prefix}/{slug}`
- branch_prefix from config (default: "feature")
- slug from id (feat-auth → auth)
- repo_path from config (optional, for monorepo setups)
- main_branch from config (default: "main")

### step 4: create worktree
```bash
# first, switch back to main_branch to create worktree
git checkout {main_branch}
git worktree add ../OA_Tool-{slug} feature/{slug}
```

worktree path: `{worktree_base}/{worktree_prefix}-{slug}`
- worktree_base from config (default: "..")
- worktree_prefix from config (default: project name)

### step 5: update queue
update `feature-workflow/queue.yaml`:
- remove from pending list
- add to active list:

```yaml
active:
  - id: {id}
    name: {name}
    priority: {priority}
    size: {size}
    parent: {parent or null}
    children: {children or []}
    dependencies: {dependencies}
    branch: feature/{slug}
    worktree: ../OA_Tool-{slug}
    started: {timestamp}
```

update `meta.last_updated`.

## output
```
🚀 feature {id} started!

branch: feature/{slug}
worktree: ../OA_Tool-{slug}
size: {size}
parent: {parent or "none"}
children: {children or "none"}

start developing:
  cd ../OA_Tool-{slug}

view tasks:
  cat features/active-{id}/task.md
```

## error handling

| error | description | solution |
|-------|-------------|----------|
| NOT_found | feature not in pending list | check id, use /list-features |
| blocked | feature is blocked | check reason, use /unblock-feature |
| limit_exceeded | parallel limit reached | complete active features or increase limit |
| dependency_error | dependencies not satisfied | complete dependent features first |
| pending_dependency | parent feature not started | start parent feature first |
| child_active | child features still active | wait for children to complete |
| branch_exists | branch already exists | delete old branch or use different name |
| worktree_error | worktree creation failed | check path permissions |
| git_error | git operation failed | check git status |

## rollback strategy

| failure point | rollback action |
|---------------|-----------------|
| step 2 rename failed | no rollback needed |
| step 3 branch failed | no rollback needed |
| step 4 worktree failed | delete branch, rename dir back to pending |
| step 5 queue update failed | delete worktree, delete branch, rename dir |

## notes

1. **dependency chain**: features with dependencies will be started in order
2. **split features**: child features show parent id for tracking
3. **parent tracking**: parent features track all children
4. **repo_path**: for monorepo setups, configure repo_path in config.yaml
