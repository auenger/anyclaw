---
description: 'Automatically schedule and start features based on priority and dependencies.'
---

# Skill: auto-schedule

Automatically schedule and start features based on priority, dependencies, and parallel development limits.

## When to use this skill

Use this skill when you want to automatically start features that are ready for development, optimizing the workflow throughput.

## Parameters

- `--dry-run`: Show what would be scheduled without actually starting
- `--max=<n>`: Override max_concurrent for this run
- `--force`: Start features even at parallel limit
- `--priority-threshold=<n>`: Only start features above this priority

## Execution Steps

### Step 1: Load Configuration

Read `feature-workflow/config.yaml`:
- `workflow.max_concurrent`
- `workflow.auto_start`
- Other relevant settings

### Step 2: Analyze Pending Features

For each pending feature:
- Check dependencies are satisfied
- Check priority threshold
- Calculate priority score
- Identify parent/child relationships

### Step 3: Determine Capacity

Calculate available capacity:
```python
active_count = len(queue.yaml['active'])
max_concurrent = config['workflow']['max_concurrent']
available = max_concurrent - active_count
```

### Step 4: Select Features to Start

Sort pending features by:
1. Priority (high to low)
2. Creation date (older first)
3. Dependency order (prerequisites first)

Select top N features where N = available capacity

### Step 5: Validate Selection

For each selected feature:
- Verify dependencies are completed
- Check parent/child constraints
- Validate no conflicts

### Step 6: Execute or Preview

If `--dry-run`:
- Show what would be started
- Show expected completion order
- Show resource utilization

If not `--dry-run`:
- Call `start-feature` for each selected feature
- Update queue.yaml
- Report results

## Output

### Dry Run Output

```
📊 Auto-Schedule Preview

Current status:
  Active features: 2/3
  Available capacity: 1

Pending features analyzed: 8
Ready to start: 3

Recommended start order:
  ┌─────────────────────────────────────────────────────────────┐
  │ #  │ ID           │ Priority │ Dependencies │ Score        │
  ├─────────────────────────────────────────────────────────────┤
  │ 1  │ feat-api     │ 90       │ ✅          │ 90 (highest) │
  │ 2  │ feat-auth    │ 85       │ ✅          │ 85           │
  │ 3  │ feat-ui      │ 70       │ ⚠️  feat-db │ 70 (blocked) │
  └─────────────────────────────────────────────────────────────┘

Will start: feat-api (highest priority, dependencies met)

Expected completion order:
  1. feat-api (2h est.)
  2. feat-auth (3h est.)
  3. feat-db → feat-ui (4h est.)

This is a dry run. Use without --dry-run to actually start features.
```

### Execution Output

```
🚀 Auto-Scheduling Features...

Current capacity: 1/3 slots available

Starting features:
  ✓ feat-api (priority 90)
    Branch: feature/api created
    Worktree: ../AnyClaw-feat-api created

Updated queue:
  Active: 3/3 (at capacity)
  Pending: 7 remaining

Next auto-schedule:
  Recommended: When feat-api completes (~2h)
  Next to start: feat-auth (priority 85)

Auto-schedule complete! 1 feature started.
```

## Scheduling Algorithm

```
score = priority + dependency_bonus + age_bonus

Where:
  priority = user-defined priority (1-100)
  dependency_bonus = +10 if unblocks other features
  age_bonus = +1 per week since creation (max +5)
```

## Error Handling

| Error | Description | Solution |
|-------|-------------|----------|
| NO_CAPACITY | No slots available | Wait or increase max_concurrent |
| DEPENDENCY_UNSATISFIED | Dependencies not met | Complete dependencies first |
| START_FAILED | Feature start failed | Check feature details |
| PARALLEL_LIMIT | Would exceed limit | Use --force or wait |

## Examples

```
# Preview what would be scheduled
/auto-schedule --dry-run

# Schedule normally
/auto-schedule

# Override max_concurrent
/auto-schedule --max=5

# Only high priority features
/auto-schedule --priority-threshold=80

# Force start even at limit
/auto-schedule --force
```

## Notes

1. **Respects dependencies** - Never starts features with unsatisfied dependencies
2. **Priority-based** - Higher priority features start first
3. **Parent/child aware** - Handles split feature relationships
4. **Resource-aware** - Respects max_concurrent limit
5. **Safe mode** - Default uses --dry-run for preview
