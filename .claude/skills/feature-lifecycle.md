---
description: 'Interactive workflow for complete feature lifecycle management from planning to completion.'
---

# Skill: feature-lifecycle

Interactive workflow that guides you through the complete feature lifecycle from planning to completion.

## When to use this skill

Use this skill when you want a guided, interactive experience for developing a feature from start to finish.

## Parameters

- `--next`: Skip to next stage
- `--status`: View current status
- `--restart`: Restart current stage
- `--abort`: Abort workflow

## Workflow Stages

```
┌─────────────────────────────────────────────────────────────────┐
│                    Feature Lifecycle                             │
└─────────────────────────────────────────────────────────────────┘

  ┌─────────┐     ┌─────────┐     ┌─────────┐     ┌─────────┐
  │Planning │ ──▶ │  Dev    │ ──▶ │ Review  │ ──▶ │  Done   │
  │         │     │         │     │         │     │         │
  │new-feat │     │start    │     │(manual) │     │complete │
  └─────────┘     └─────────┘     └─────────┘     └─────────┘
```

## Stage Details

### Stage 1: Planning

**Goal**: Create feature and generate documentation

**Calls**: `new-feature`

**Interaction**:
```
Agent: Welcome to Feature Lifecycle Workflow

       Describe the feature you want to build:

User: User authentication with login, register, logout

Agent: Please provide details:

       1. Name (default: User authentication)
       2. Detailed description
       3. Priority (1-100, default 50)
       4. Dependencies

User: Name: User Auth
     Description: Complete auth system
     Priority: 80

Agent: Confirm creating feat-user-auth?
       (y/n/e=edit)

User: y

Agent: ✅ Feature created!

       Directory: features/pending-feat-user-auth
       Documents: spec.md, task.md, checklist.md

       Start development now? (y/n)
```

### Stage 2: Development

**Goal**: Set up development environment

**Calls**: `start-feature`

**Interaction**:
```
Agent: 🚀 Starting development

       Checking parallel limit... ✅
       Creating branch feature/user-auth... ✅
       Creating worktree... ✅

       Development environment ready!

       Switch directory:
         cd ../AnyClaw-feat-user-auth

       View tasks:
         cat features/active-feat-user-auth/task.md

       When done, run:
         /feature-lifecycle --next
```

**Manual Phase**:
- Develop in worktree
- Update spec.md with technical solution
- Complete tasks in task.md
- Check items in checklist.md

### Stage 3: Review

**Goal**: Review code and documentation

**Interaction**:
```
Agent: 📋 Development Review

       Checklist Status:
       ✅ All tasks completed
       ✅ Code self-tested
       ⚠️ Unit tests not written
       ✅ Code style OK

       Git Status:
       - Files changed: 12
       - New files: 5
       - Deleted: 1

       Commit message:
       feat(feat-user-auth): User authentication

       Continue to complete? (y/n/edit)
```

**Options**:
- `y`: Proceed to completion
- `n`: Return to development
- `edit`: Modify commit message

### Stage 4: Done

**Goal**: Commit, merge, archive

**Calls**: `complete-feature`

**Interaction**:
```
Agent: 🎉 Completing feature

       Committing code... ✅
       Merging to main... ✅
       Cleaning up worktree... ✅
       Archiving docs... ✅

       ┌───────────────────────────────────────────────┐
       │ Completion Report                               │
       ├───────────────────────────────────────────────┤
       │ Feature: feat-user-auth (User Auth)            │
       │ Duration: 2h 30m                                │
       │ Commits: 5                                      │
       │ Files changed: 18                               │
       └───────────────────────────────────────────────┘

       Next: feat-dashboard (priority 80)
       Auto-start? (y/n)
```

## State Persistence

Workflow state saved in `.workflow-state.yaml`:

```yaml
workflow: feature-lifecycle
feature_id: feat-user-auth
current_stage: development
started: 2026-03-02T10:00:00
stages:
  planning:
    status: completed
    completed_at: 2026-03-02T10:05:00
  development:
    status: in_progress
    started_at: 2026-03-02T10:05:00
  review:
    status: pending
  done:
    status: pending
```

## Status Output

```
/feature-lifecycle --status

┌───────────────────────────────────────────────┐
│ Feature Lifecycle Status                       │
├───────────────────────────────────────────────┤
│ Feature: feat-user-auth                        │
│ Current Stage: development                     │
│                                                │
│ ✅ planning (completed 2h ago)                │
│ 🔄 development (in progress)                  │
│ ⏳ review (pending)                           │
│ ⏳ done (pending)                             │
└───────────────────────────────────────────────┘
```

## Recovery

| Scenario | Recovery |
|----------|----------|
| Interrupted | Run `/feature-lifecycle --status` |
| Stage failed | Fix issue, run `/feature-lifecycle --restart` |
| Want to abort | Run `/feature-lifecycle --abort` |

## Examples

```
/feature-lifecycle
→ Start full interactive workflow

/feature-lifecycle --stage=development
→ Start at development stage

/feature-lifecycle --status
→ Check current progress

/feature-lifecycle --next
→ Skip to next stage
```
