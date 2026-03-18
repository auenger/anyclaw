---
description: 'Manage and orchestrate multiple features, handle dependencies, and optimize development flow.'
---

# Skill: feature-manager

Master agent that manages and orchestrates multiple features, handles dependencies, and optimizes the overall development workflow.

## When to use this skill

Use this skill when you need to manage multiple features, resolve dependencies, or optimize the development workflow.

## Parameters

- `--status`: Show overall workflow status
- `--optimize`: Suggest optimal feature development order
- `--check-dependencies`: Check all feature dependencies
- `--auto-schedule`: Automatically start ready features
- `--report`: Generate workflow report

## Capabilities

### Skills Called

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
  - dev-agent
```

## Execution Modes

### Mode 1: Status Check

Display overall workflow status:
```
/feature-manager --status
```

Shows:
- Current features by status
- Parallel usage
- Blockers and dependencies
- Recommendations

### Mode 2: Dependency Check

Check all feature dependencies:
```
/feature-manager --check-dependencies
```

Shows:
- Dependency graph
- Circular dependencies (errors)
- Missing dependencies
- Satisfied dependencies

### Mode 3: Optimize

Suggest optimal development order:
```
/feature-manager --optimize
```

Analyzes:
- Priority vs dependencies
- Parallel development opportunities
- Critical path
- Bottlenecks

### Mode 4: Auto-Schedule

Automatically start ready features:
```
/feature-manager --auto-schedule
```

Starts features that:
- Have no unsatisfied dependencies
- Fit within parallel limit
- Have highest priority

### Mode 5: Generate Report

Generate comprehensive workflow report:
```
/feature-manager --report
```

Includes:
- Feature statistics
- Time metrics
- Blocker analysis
- Recommendations

## Output

### Status Output

```
┌─────────────────────────────────────────────────────────────────┐
│                    Workflow Status Summary                       │
├─────────────────────────────────────────────────────────────────┤
│                                                                  │
│  Overview:                                                       │
│    Total features: 25                                           │
│    Pending: 8 | Active: 3 | Blocked: 2 | Done: 12               │
│    Parallel usage: 3/3 (at limit)                               │
│                                                                  │
│  Active Features:                                                │
│    ┌──────────────┬──────────┬──────────┬────────────┐          │
│    │ ID           │ Progress │ Time     │ Est. Done  │          │
│    ├──────────────┼──────────┼──────────┼────────────┤          │
│    │ feat-auth    │ 80%      │ 2h 15m   │ 30m        │          │
│    │ feat-db      │ 45%      │ 1h 30m   │ 2h         │          │
│    │ feat-ui      │ 20%      │ 45m      │ 3h         │          │
│    └──────────────┴──────────┴──────────┴────────────┘          │
│                                                                  │
│  Blockers:                                                       │
│    ┌──────────────┬──────────────────────────────────────────┐  │
│    │ feat-upload  │ Waiting for: feat-storage (in progress) │  │
│    │ feat-export  │ Waiting for: feat-api (not started)     │  │
│    └──────────────┴──────────────────────────────────────────┘  │
│                                                                  │
│  Recommendations:                                                │
│    ⚠️  At parallel limit, consider increasing max_concurrent    │
│    💡 Start feat-api first (unblocks feat-export)               │
│    📊 Priority drift detected, review pending features          │
│                                                                  │
└─────────────────────────────────────────────────────────────────┘
```

### Optimize Output

```
📊 Development Order Optimization

Current order analysis:
  Priority: High → Low
  Dependency awareness: Partial

Optimal order suggested:
  ┌─────────────────────────────────────────────────────────────┐
  │ Batch 1 (Can start now - parallel):                         │
  │   1. feat-api (priority 90, unblocks 2 features)            │
  │   2. feat-storage (priority 80, unblocks 1 feature)         │
  │   3. feat-ui-basic (priority 70, no dependencies)           │
  ├─────────────────────────────────────────────────────────────┤
  │ Batch 2 (After Batch 1):                                    │
  │   4. feat-export (depends on feat-api)                      │
  │   5. feat-upload (depends on feat-storage)                  │
  ├─────────────────────────────────────────────────────────────┤
  │ Batch 3 (After Batch 2):                                    │
  │   6. feat-analytics (depends on feat-export)                │
  └─────────────────────────────────────────────────────────────┘

Critical path: feat-api → feat-export → feat-analytics
Est. completion: 2 days (with optimal parallel execution)

Apply optimization? (y/n)
```

## Error Handling

| Error | Description | Solution |
|-------|-------------|----------|
| CIRCULAR_DEPENDENCY | Features depend on each other | Break dependency cycle |
| ORPHAN_FEATURE | Feature with invalid parent | Update parent reference |
| QUEUE_CORRUPT | queue.yaml is corrupted | Restore from backup |

## Examples

```
# Check status
/feature-manager --status

# Optimize workflow
/feature-manager --optimize

# Check dependencies
/feature-manager --check-dependencies

# Auto-schedule ready features
/feature-manager --auto-schedule

# Generate report
/feature-manager --report
```
