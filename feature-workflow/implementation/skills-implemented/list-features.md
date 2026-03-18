---
description: 'List all features with their current status - active, pending, blocked, and archived.'
---

# Skill: list-features

List all features with their current status - active, pending, blocked, and archived.

 Use `/list-features` or `/list-features --verbose` for more details.

 Use `/list-features --json` for machine-readable output.

## Quick Display

 just the status summary.

```
┌─────────────────────────────────────────────────────────────────┐
│ Feature Status                                                  │
├─────────────────────────────────────────────────────────────────┤
│ Active: 0/2                                                │
│ Pending: 0                                                 │
│ Blocked: 0                                                 │
│ Archived: 2                                                 │
└─────────────────────────────────────────────────────────────────┘
```

## Execution Steps

### Step 1: Read Configuration

Read `feature-workflow/config.yaml`:
- max_concurrent

- workflow.auto_start

- workflow.require_checklist

### Step 2: Read queue
Read `feature-workflow/queue.yaml`:
- active features
- pending features
- blocked features

- Check for parent/children relationships

### Step 3: Read archive log
Read `features/archive/archive-log.yaml`:
- count archived features

### Step 4: Calculate duration
For active features:
- Calculate time since started
- Format as human-readable (e.g., "2h ago", "3d ago")
### Step 5: Format output

```
┌─────────────────────────────────────────────────────────────────┐
│ Feature Status                                                  │
├─────────────────────────────────────────────────────────────────┤
│ Active (1/2):                                                   │
│   ● feat-auth       [90]  started: 2h ago                       │
│     Branch: feature/auth                                        │
│     Worktree: ../OA_Tool-feat-auth                              │
│                                                                 │
│ Pending:                                                        │
│   ○ feat-dashboard  [80]  created: 1d ago                       │
│   ○ feat-report     [70]  created: 3h ago                        │
│                                                                 │
│ Blocked:                                                        │
│   ⊘ feat-export     reason: depends on feat-auth                │
│                                                                 │
│ Archived: 2                                                     │
└─────────────────────────────────────────────────────────────────┘

```

### Enhanced display (with --verbose)

```
┌─────────────────────────────────────────────────────────────────┐
│ Feature Status (Detailed)                                 │
├─────────────────────────────────────────────────────────────────┤
│ Active (1/2):                                                   │
│   ● feat-auth       [90]  started: 2h ago                       │
│     Size: M                                                  │
│     Parent: null                                                │
│     Children: []                                                │
│     Dependencies: []                                              │
│     Branch: feature/auth                                        │
│     Worktree: ../OA_Tool-feat-auth                              │
│                                                                 │
│ Pending:                                                        │
│   ○ feat-dashboard  [80]  created: 1d ago                       │
│     Size: S                                                  │
│     Parent: null                                                │
│     Children: []                                                │
│     Dependencies: []                                              │
│                                                                 │
│ Split Group: feat-user-system (3 features)             │
│   ├─ feat-user-login      [80]  created: 1d ago                      │
│   │  Size: S | Parent: feat-user-system | Children: []             │
│   │  Dependencies: []                                        │
│   ├─ feat-user-register   [80]  created: 1d ago                      │
│   │  Size: S | Parent: feat-user-system | Children: []             │
│   │  Dependencies: [feat-user-login]                               │
│   └─ feat-user-permissions [80]  created: 1d ago                     │
│      Size: S | Parent: feat-user-system | Children: []             │
│      Dependencies: [feat-user-register]                                │
│                                                                 │
│ Blocked:                                                        │
│   ⊘ feat-export     reason: depends on feat-auth                │
│                                                                 │
│ Archived: 2                                                     │
└─────────────────────────────────────────────────────────────────┘
```

### JSON output (with --json)

```json
{
  "active": [
    {
      "id": "feat-auth",
      "name": "User Authentication",
      "priority": 90,
      "branch": "feature/auth",
      "worktree": "../OA_Tool-feat-auth",
      "started": "2026-03-02T09:00:00",
      "duration": "2h"
    }
  ],
  "pending": [
    {
      "id": "feat-dashboard",
      "name": "Dashboard",
      "priority": 80,
      "size": "S",
      "created": "2026-03-01T14:00:00"
    }
  ],
  "blocked": [
    {
      "id": "feat-export",
      "name": "Export Feature",
      "reason": "depends on feat-auth",
      "created": "2026-03-01T10:00:00"
    }
  ],
  "archived_count": 2,
  "capacity": {
    "used": 1,
    "max": 2
  }
}
```

## Error handling

| Error | Description | Solution |
|-------|-------------|----------|
| CONFIG_not_found | config.yaml missing | Check feature-workflow directory |
| queue_not_found | queue.yaml missing | Check feature-workflow directory |
| parse_error | YAML parsing failed | Check file format |

