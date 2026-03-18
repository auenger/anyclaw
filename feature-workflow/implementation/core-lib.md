# Feature Workflow Core Library

Shared utilities and functions for all feature-workflow skills.

## Configuration

### Default Config Path
`feature-workflow/config.yaml`

### Config Structure
```yaml
project:
  name: string                    # Project name
  main_branch: string             # Main branch name (default: main)

parallelism:
  max_concurrent: number          # Max parallel development (default: 2)

workflow:
  auto_start: boolean             # Auto-start after completion
  require_checklist: boolean      # Require checklist before completion

completion:
  archive:
    create_tag: boolean           # Create archive tag
    tag_format: string            # Tag format (default: "{id}-{date}")
    tag_date_format: string       # Date format (default: "%Y%m%d")
  cleanup:
    delete_worktree: boolean      # Delete worktree
    delete_branch: boolean        # Delete branch
  record:
    update_spec: boolean          # Update spec.md
    update_archive_log: boolean   # Update archive-log.yaml

naming:
  feature_prefix: string          # Feature ID prefix (default: feat)
  branch_prefix: string           # Branch prefix (default: feature)
  worktree_prefix: string         # Worktree prefix (default: project name)

paths:
  features_dir: string            # Features directory
  archive_dir: string             # Archive directory
  worktree_base: string           # Worktree parent directory

git:
  auto_push: boolean              # Auto push main
  merge_strategy: string          # Merge strategy (default: --no-ff)
  push_tags: boolean              # Auto push tags
```

## File Paths

| File | Path | Purpose |
|------|------|---------|
| config.yaml | feature-workflow/ | Project configuration |
| queue.yaml | feature-workflow/ | Feature queue |
| archive-log.yaml | features/archive/ | Archive log |
| templates/ | feature-workflow/ | Document templates |

## Queue Structure

```yaml
meta:
  last_updated: datetime
  version: number

active:                           # In development
  - id: string
    name: string
    priority: number
    branch: string
    worktree: string
    started: datetime

pending:                          # Waiting
  - id: string
    name: string
    priority: number
    created: datetime

blocked:                          # Blocked
  - id: string
    name: string
    reason: string
    created: datetime
```

## Utility Functions

### Generate Slug
Convert feature name to URL-safe slug:
```
"User Authentication" → "user-auth"
"API v2 Integration" → "api-v2-integration"
```

Rules:
1. Convert to lowercase
2. Replace spaces with hyphens
3. Remove special characters
4. Limit length to 30 chars

### Generate Feature ID
```
{prefix}-{slug}
Example: feat-user-auth
```

### Generate Tag Name
```
{id}-{date}
Example: feat-user-auth-20260302
```

### Calculate Duration
```
started: 2026-03-02T09:00:00
now: 2026-03-02T11:30:00
duration: "2h 30m"
```

### Format Relative Time
```
2h ago, 3d ago, just now
```

## Error Codes

| Code | Description |
|------|-------------|
| ID_CONFLICT | Feature ID already exists |
| NOT_FOUND | Feature not found |
| NOT_ACTIVE | Feature not in active list |
| LIMIT_EXCEEDED | Parallel limit reached |
| DEPENDENCY_ERROR | Dependencies not satisfied |
| WORKTREE_NOT_FOUND | Worktree doesn't exist |
| BRANCH_EXISTS | Branch already exists |
| MERGE_CONFLICT | Merge conflict occurred |
| TAG_EXISTS | Tag already exists |
| NOTHING_TO_COMMIT | No changes to commit |
| GIT_ERROR | Git operation failed |
| QUEUE_ERROR | Queue update failed |
| CONFIG_ERROR | Config read/write failed |

## Git Commands Reference

### Create Branch
```bash
git checkout main
git checkout -b feature/{slug}
```

### Create Worktree
```bash
git worktree add ../{project}-{slug} feature/{slug}
```

### Commit
```bash
git add .
git commit -m "feat({id}): {name}"
```

### Merge
```bash
git checkout main
git merge feature/{slug} --no-ff
```

### Create Tag
```bash
git tag -a {tag_name} -m "Archive: {name}"
```

### Cleanup
```bash
git worktree remove {path}
git branch -d {branch}
```

### Restore from Tag
```bash
git checkout -b feature/{slug}-restored {tag_name}
```

## Checklist Parsing

Parse markdown checklist:
```markdown
- [ ] Incomplete item
- [x] Complete item
```

Count complete/incomplete items.

## Task Parsing

Parse markdown task list:
```markdown
### 1. Category
- [ ] Task 1
- [x] Task 2
```

Extract task status and categories.
