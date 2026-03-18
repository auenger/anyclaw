---
description: 'Development agent that automates the complete feature development workflow from start to completion.'
---

# Skill: dev-agent

Development agent that automates the complete feature development process: start → implement → verify → complete.

## When to use this skill

Use this skill when you want to automate the entire feature development workflow from start to finish.

## Parameters

- `feature-id`: Feature ID to develop (optional if providing description)
- `description`: Feature description (to create new feature)
- `--mode=<mode>`: Execution mode (auto, interactive, step)
- `--start-from=<stage>`: Start from specific stage
- `--skip-verify`: Skip verification stage
- `--resume`: Resume from last interruption

## Execution Modes

### Mode 1: Full Development (auto)

Create and develop feature from description:
```
/dev-agent "User authentication feature"
```

Automatically executes:
1. new-feature (create)
2. start-feature (setup)
3. implement-feature (code)
4. verify-feature (check)
5. complete-feature (finish)

### Mode 2: Continue Development

Continue from existing feature:
```
/dev-agent feat-auth
```

Check status then:
- If pending: start → implement → verify → complete
- If active: implement → verify → complete
- If blocked: prompt to unblock

### Mode 3: Interactive

Ask for confirmation at each stage:
```
/dev-agent feat-auth --mode=interactive
```

## Execution Flow

```
┌─────────────────────────────────────────────────────────────────┐
│                      dev-agent Main Flow                         │
└─────────────────────────────────────────────────────────────────┘
                              │
                              ▼
                    Parse Input & Determine Mode
                              │
                              ▼
                    Check Feature Status
                              │
                              ▼
                    Execute Stages (start → implement → verify → complete)
                              │
                              ▼
                    Handle Errors (pause, report, suggest fix)
                              │
                              ▼
                    Report Completion
```

## State Persistence

Progress saved in `.dev-progress.yaml`:
```yaml
feature_id: feat-auth
started: 2026-03-02T10:00:00
current_stage: implement-feature
stages:
  start-feature:
    status: completed
    completed_at: 2026-03-02T10:00:05
  implement-feature:
    status: in_progress
    started_at: 2026-03-02T10:00:05
    tasks_completed: [1, 2]
    tasks_pending: [3, 4, 5]
```

## Output

### Full Success
```
🎉 Development Complete!

Feature: feat-auth (User Authentication)

Execution:
  ✓ start-feature (5s)
  ✓ implement-feature (2m 30s)
  ✓ verify-feature (15s)
  ✓ complete-feature (10s)

Summary:
  Total: 3m 00s
  Files changed: 8
  Tests passed: 12
  Merged to: main

Next: feat-dashboard (priority 80)
```

### Partial Failure
```
⚠️ Development Interrupted

Feature: feat-auth
Failed at: implement-feature
Reason: Task 3 failed

Completed: 2/5 tasks

Suggestion:
Fix and run: /dev-agent feat-auth --resume
```

## Error Handling

| Error | Description | Solution |
|-------|-------------|----------|
| NOT_FOUND | Feature not found | Check feature ID |
| BLOCKED | Feature is blocked | Unblock first |
| LIMIT_EXCEEDED | Parallel limit reached | Wait or increase limit |
| IMPLEMENTATION_ERROR | Implementation failed | Fix and resume |
| VERIFICATION_FAILED | Tests failed | Fix tests and resume |

## Examples

```
# From description
/dev-agent "User auth with login, register, logout"

# Continue development
/dev-agent feat-auth

# Interactive mode
/dev-agent feat-auth --mode=interactive

# Resume after error
/dev-agent feat-auth --resume
```
