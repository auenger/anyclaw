---
description: 'Automatically schedule pending features based on priority and dependencies.'
---

# Workflow: auto-schedule

Automatically schedule pending features based on priority, dependencies, and available capacity.

## Usage

```
/auto-schedule              # Run scheduler
/auto-schedule --dry-run    # Preview without executing
```

## Automatic Triggers

Auto-schedule runs automatically when:

| Event | Condition |
|-------|-----------|
| /new-feature completes | auto_start=true and slot available |
| /complete-feature completes | auto_start=true and pending not empty |
| /unblock-feature completes | auto_start=true and slot available |
| /feature-config changes max_concurrent | Increased parallel capacity |

## Scheduling Algorithm

```
function auto_schedule():
  config = read_config()
  queue = read_queue()

  while queue.active.length < config.max_concurrent:

    # 1. Check if pending is empty
    if queue.pending is empty:
      break

    # 2. Get highest priority feature
    candidates = sort_by_priority(queue.pending)
    next = candidates[0]

    # 3. Check dependencies
    if next.dependencies:
      unmet = check_dependencies(next.dependencies)
      if unmet:
        move_to_blocked(next, reason="Dependencies not met: {unmet}")
        continue  # Check next candidate

    # 4. Start the feature
    result = start_feature(next.id)
    if result.success:
      log("Started: {next.id}")
    else:
      log("Failed to start: {result.error}")
      break

  return results
```

## Priority Sorting

1. **Primary**: priority descending (higher = first)
2. **Secondary**: created ascending (older = first)

```
Example:
  feat-a: priority=90, created=2026-03-01  ← First
  feat-b: priority=90, created=2026-03-02
  feat-c: priority=80                       ← Last
```

## Dependency Check

```python
def check_dependencies(dependencies):
  archive = read_archive_log()
  unmet = []

  for dep_id in dependencies:
    if dep_id not in archive.archived:
      unmet.append(dep_id)

  return unmet  # Empty if all satisfied
```

## Execution Steps

### Step 1: Read State

Read:
- `config.yaml` for max_concurrent
- `queue.yaml` for current state
- `archive-log.yaml` for dependency checking

### Step 2: Calculate Available Slots

```
available = max_concurrent - active.count
```

If `available <= 0`: exit (no capacity)

### Step 3: Process Pending Queue

For each pending feature (sorted by priority):
1. Check dependencies
2. If unmet: move to blocked
3. If met: add to start list
4. Stop when start list is full

### Step 4: Start Features

For each feature in start list:
- Call `start-feature`
- Record result

### Step 5: Report Results

Display:
- Started features
- Blocked features
- Remaining in queue

## Output

### Features Started

```
🚀 Auto-schedule complete

Started:
  - feat-dashboard → ../OA_Tool-feat-dashboard

Blocked:
  - feat-export (depends on feat-auth, not complete)

Remaining: 1 (feat-report, priority 70)
```

### No Capacity

```
ℹ️ No available capacity

Active: 2/2 (at limit)

Active features:
  - feat-auth
  - feat-dashboard
```

### Dry Run

```
🔍 Dry Run - Would execute:

[START] feat-dashboard (priority 80)
  → Branch: feature/dashboard
  → Worktree: ../OA_Tool-feat-dashboard

[BLOCK] feat-export
  → Reason: depends on feat-auth (not complete)

Run without --dry-run to execute.
```

## Configuration

```yaml
# config.yaml
parallelism:
  max_concurrent: 2

workflow:
  auto_start: true           # Enable auto-scheduling
  check_dependencies: true   # Check dependencies
  retry_on_failure: false    # Retry failed starts
```

## Examples

### Scenario 1: After Creating Feature

```
User: /new-feature User Auth --priority=90

Agent: ✅ Feature feat-auth created

       Checking auto-schedule...
       Current active: 0/2
       🚀 Auto-starting feat-auth

       cd ../OA_Tool-feat-auth
```

### Scenario 2: After Completing Feature

```
User: /complete-feature feat-auth

Agent: ✅ feat-auth completed

       Checking auto-schedule...
       Current active: 0/2
       Pending: feat-dashboard (80), feat-report (70)
       🚀 Auto-starting feat-dashboard
```

### Scenario 3: Dependency Blocking

```
User: /complete-feature feat-auth

Agent: ✅ feat-auth completed

       Checking auto-schedule...

       Checking feat-export: depends on feat-dashboard (not complete)
       → Moved to blocked

       Checking feat-dashboard: no dependencies
       🚀 Auto-starting feat-dashboard
```

### Scenario 4: At Capacity

```
User: /new-feature Notifications --priority=60

Agent: ✅ Feature feat-notifications created

       Checking auto-schedule...
       Current active: 2/2 (at limit)

       feat-notifications added to queue
       Position: #3 (priority 60)
```

## Notes

1. **Circular dependencies**: Features in a dependency cycle will all be blocked
2. **Priority changes**: Modify priority to affect scheduling order
3. **Manual blocking**: Use /block-feature to prevent auto-scheduling
4. **Config changes**: Changing max_concurrent triggers re-scheduling
