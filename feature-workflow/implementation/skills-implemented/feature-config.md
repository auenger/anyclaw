---
description: 'View or modify feature workflow configuration.'
---

# Skill: feature-config

View or modify the feature workflow configuration.

## Usage

```
/feature-config                           # View all config
/feature-config <key>                     # View specific key
/feature-config <key>=<value>             # Modify config
```

## Configuration Keys

| Key | Type | Default | Description |
|-----|------|---------|-------------|
| parallelism.max_concurrent | number | 2 | Max parallel features |
| workflow.auto_start | boolean | true | Auto-start next feature |
| workflow.require_checklist | boolean | true | Require checklist before complete |
| naming.feature_prefix | string | feat | Feature ID prefix |
| naming.branch_prefix | string | feature | Git branch prefix |
| naming.worktree_prefix | string | OA_Tool | Worktree directory prefix |
| completion.archive.create_tag | boolean | true | Create archive tag |
| completion.cleanup.delete_worktree | boolean | true | Delete worktree on complete |
| completion.cleanup.delete_branch | boolean | true | Delete branch on complete |
| git.auto_push | boolean | false | Auto-push to remote |
| git.merge_strategy | string | --no-ff | Git merge strategy |

## Execution Steps

### View All Config

Read `feature-workflow/config.yaml` and display formatted output.

### View Single Key

Read config and return the value at the specified path.

### Modify Config

1. Read current config
2. Validate key exists
3. Validate value type matches
4. Update config
5. Write to `config.yaml`
6. If key is `max_concurrent`: trigger auto-schedule check

## Output

### View All

```
┌─────────────────────────────────────────────────────────────────┐
│ Feature Workflow Configuration                                  │
├─────────────────────────────────────────────────────────────────┤
│ parallelism:                                                    │
│   max_concurrent: 2                                             │
│                                                                 │
│ workflow:                                                       │
│   auto_start: true                                              │
│   require_checklist: true                                       │
│                                                                 │
│ naming:                                                         │
│   feature_prefix: feat                                          │
│   branch_prefix: feature                                        │
│   worktree_prefix: OA_Tool                                      │
│                                                                 │
│ git:                                                            │
│   auto_push: false                                              │
│   merge_strategy: --no-ff                                       │
└─────────────────────────────────────────────────────────────────┘
```

### View Single Key

```
max_concurrent = 2
```

### Modify Success

```
✅ Configuration updated

parallelism.max_concurrent: 2 → 3

Checking if more features can be started...
Current active: 1/3
🚀 Auto-starting: feat-dashboard
```

### Validation Error

```
❌ Invalid value

max_concurrent must be a positive integer, got: -1
```

## Error Codes

| Code | Description |
|------|-------------|
| INVALID_KEY | Configuration key doesn't exist |
| INVALID_VALUE | Value type doesn't match or is invalid |
| PERMISSION_ERROR | Cannot write to config file |

## Examples

```
/feature-config
→ Shows all configuration

/feature-config max_concurrent
→ max_concurrent = 2

/feature-config max_concurrent=3
→ ✅ Updated: max_concurrent: 2 → 3

/feature-config auto_start=false
→ ✅ Updated: auto_start: true → false
```
