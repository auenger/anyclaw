---
description: 'Development agent that automates the complete feature development workflow from start to completion.'
---

# Agent: dev-agent

Development agent that automates the complete feature development process: start → implement → verify → complete.

## Role

dev-agent is the "developer" role, transforming requirements into code by orchestrating multiple skills:

```
Requirement → Analysis → Implementation → Verification → Completion
```

## Capabilities

### Skills to Call

```yaml
skills:
  - new-feature
  - start-feature
  - implement-feature
  - verify-feature
  - complete-feature
  - list-features
  - block-feature
  - unblock-feature
```

### File Operations

```yaml
read:
  - feature-workflow/config.yaml
  - feature-workflow/queue.yaml
  - features/**/spec.md
  - features/**/task.md
  - features/**/checklist.md
  - All code files in worktree

write:
  - feature-workflow/queue.yaml
  - features/**/spec.md
  - features/**/task.md
  - features/**/checklist.md
  - All code files in worktree
```

## Modes

### Mode 1: Full Development

Create and develop feature from description:

```
/dev-feature "User authentication feature"

→ Automatically:
  1. new-feature (create)
  2. start-feature (setup)
  3. implement-feature (code)
  4. verify-feature (check)
  5. complete-feature (finish)
```

### Mode 2: Continue Development

Continue from existing feature:

```
/dev-feature feat-auth

→ Check status then:
  - If pending: start → implement → verify → complete
  - If active: implement → verify → complete
  - If blocked: prompt to unblock
```

### Mode 3: Interactive

Ask for confirmation at each stage:

```
/dev-feature feat-auth --interactive

→ Ask before each stage:
  "About to implement. Continue? (y/n)"
  "Implementation done. Verify? (y/n)"
  ...
```

## Execution Flow

```
┌─────────────────────────────────────────────────────────────────┐
│                      dev-agent Main Flow                         │
└─────────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────────┐
│ Step 1: Parse Input                                              │
│ - If description: create new feature                            │
│ - If feature ID: find existing feature                          │
│ - Determine mode                                                 │
└─────────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────────┐
│ Step 2: Check Status                                             │
│ - Read queue.yaml                                                │
│ - Check feature status                                           │
│ - Determine starting stage                                       │
│                                                                  │
│ Status mapping:                                                  │
│   pending  → start from start-feature                           │
│   active   → start from implement-feature                       │
│   blocked  → prompt user, exit                                  │
│   done     → notify complete, exit                              │
└─────────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────────┐
│ Step 3: Execute Stages                                           │
│                                                                  │
│   ┌─────────────────┐                                          │
│   │ start-feature   │  (if needed)                             │
│   └────────┬────────┘                                          │
│            │                                                    │
│            ▼                                                    │
│   ┌─────────────────┐                                          │
│   │implement-feature│                                          │
│   └────────┬────────┘                                          │
│            │                                                    │
│            ▼                                                    │
│   ┌─────────────────┐                                          │
│   │ verify-feature  │                                          │
│   └────────┬────────┘                                          │
│            │                                                    │
│            ▼                                                    │
│   ┌─────────────────┐                                          │
│   │complete-feature │                                          │
│   └─────────────────┘                                          │
│                                                                  │
└─────────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────────┐
│ Step 4: Handle Errors                                            │
│ - If stage fails: pause and report                              │
│ - Provide fix suggestions                                        │
│ - Wait for user instruction                                      │
│                                                                  │
│ Recovery: Fix and rerun from interruption point                 │
└─────────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────────┐
│ Step 5: Report Completion                                        │
│ - Summarize results                                              │
│ - Show file changes                                              │
│ - Show next pending feature                                      │
└─────────────────────────────────────────────────────────────────┘
```

## Command Options

| Option | Description |
|--------|-------------|
| `--mode=auto` | Auto-execute all stages (default) |
| `--mode=interactive` | Ask confirmation at each stage |
| `--mode=step` | Execute one stage then stop |
| `--start-from=<stage>` | Start from specific stage |
| `--skip-verify` | Skip verification stage |
| `--no-auto-complete` | Don't auto-complete after verify |
| `--resume` | Resume from last interruption |

## Output

### Full Success

```yaml
status: success
feature:
  id: feat-auth
  name: User Authentication

execution:
  stages:
    - name: start-feature
      status: success
      duration: 5s
    - name: implement-feature
      status: success
      duration: 2m 30s
      tasks_completed: 5
    - name: verify-feature
      status: success
      duration: 15s
      tests_passed: 12
    - name: complete-feature
      status: success
      duration: 10s

summary:
  total_duration: 3m 00s
  files_changed: 8
  tests_passed: 12
  merged_to: main

next:
  auto_scheduled: feat-dashboard
```

### Partial Failure

```yaml
status: partial
feature:
  id: feat-auth

execution:
  stages:
    - name: start-feature
      status: success
    - name: implement-feature
      status: failed
      error:
        code: IMPLEMENTATION_ERROR
        message: "Task 3 failed: service not found"
      completed_tasks: 2
      failed_task: 3

  current_stage: implement-feature
  can_resume: true

message: |
  ⚠️ Development interrupted

  Failed at: implement-feature
  Reason: Task 3 failed

  Completed: 2/5 tasks

  Suggestion:
  Fix and run: /dev-feature feat-auth --resume
```

### Interactive Mode

```
User: /dev-feature feat-auth --interactive

Agent: 📋 Checking status...
       feat-auth: pending

       ┌───────────────────────────────────────────┐
       │ Stage 1/4: start-feature                   │
       ├───────────────────────────────────────────┤
       │ Will execute:                              │
       │ - Create branch feature/auth               │
       │ - Create worktree ../OA_Tool-feat-auth     │
       └───────────────────────────────────────────┘

       Continue? (y/n/skip)

User: y

Agent: ✅ start-feature complete

       ┌───────────────────────────────────────────┐
       │ Stage 2/4: implement-feature               │
       ├───────────────────────────────────────────┤
       │ Will implement:                            │
       │ 1. Create User model                       │
       │ 2. Register API                            │
       │ 3. Login API                               │
       │ 4. Logout API                              │
       │ 5. Auth middleware                         │
       └───────────────────────────────────────────┘

       Continue? (y/n/skip)

User: y

Agent: 🔨 Implementing...
       [1/5] ✅ [2/5] ✅ [3/5] ✅ [4/5] ✅ [5/5] ✅

       ✅ implement-feature complete
       ...
```

## Decision Logic

### Determine Starting Stage

```python
def determine_start_stage(feature):
    if feature.status == "pending":
        return "start"
    elif feature.status == "active":
        if all_tasks_completed(feature):
            if verification_passed(feature):
                return "complete"
            else:
                return "verify"
        else:
            return "implement"
    elif feature.status == "blocked":
        return None  # Need to unblock first
    else:
        return None  # Already done
```

### Handle Error

```python
def handle_error(stage, error):
    if error.recoverable:
        report_error(error)
        suggest_fix(error)
        wait_for_user_action()
    else:
        report_error(error)
        suggest_manual_fix(error)
        save_state()
        exit()
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

## Examples

### From Description

```
User: /dev-feature "User auth with login, register, logout"

Agent: 📋 Creating feature...
       ✅ feat-auth created

       🚀 Starting development...
       ✅ Environment ready

       🔨 Implementing...
       ✅ Code complete

       🔍 Verifying...
       ✅ Verification passed

       📦 Completing...
       ✅ Merged to main

       🎉 Done! Total: 3m 30s
```

### Continue Development

```
User: /dev-feature feat-auth

Agent: 📋 Checking status...
       feat-auth: active (2/5 tasks done)

       🔨 Continuing...
       ✅ Code complete (5/5)

       🔍 Verifying...
       ✅ Passed

       🎉 Done!
```

### Resume After Error

```
User: /dev-feature feat-auth --resume

Agent: 📋 Found previous run
       Last stage: implement-feature (failed at task 3)

       🔨 Resuming from task 3...
       ✅ Complete

       🔍 Verifying...
       ✅ Passed

       🎉 Done!
```

## Notes

1. **Interruptible** - Can stop at any stage, resume later
2. **Progress preserved** - Failed runs save state
3. **Manual intervention** - Can pause, edit, continue
4. **Works with feature-manager** - Can be called by master agent
