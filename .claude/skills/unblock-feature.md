---
description: 'Unblock a blocked feature, allowing it to be started again.'
---

# Skill: unblock-feature

Unblock a blocked feature, allowing it to be started again. Moves the feature back to the pending list.

## When to use this skill

Use this skill when a blocked feature is ready to be worked on again.

## Parameters

- `feature-id`: The feature ID to unblock (required)

## Execution Steps

### Step 1: Find Feature

Locate the feature in `queue.yaml` blocked list:
- Find feature by ID
- If not found, error
- Check current blocked status

### Step 2: Show Block Information

Display why the feature was blocked:
- Block reason
- Blocked at timestamp
- Blocked by user
- Duration blocked

### Step 3: Verify Dependencies

Check if dependencies are now satisfied:
- Verify all dependencies in archive-log.yaml
- Check if blocking issues are resolved
- Warn if dependencies still not met

### Step 4: Confirm Unblock

Ask user to confirm:
- Show block info
- Show dependency status
- Ask for confirmation

### Step 5: Update Queue

Move feature from blocked to pending list in `queue.yaml`:

```yaml
pending:
  - id: {id}
    name: {name}
    priority: {priority}
    size: {size}
    parent: {parent or null}
    children: {children or []}
    dependencies: {dependencies}
    created: {original_created}
    unblocked_at: {timestamp}
    previous_block: {original_block_reason}
```

### Step 6: Check Auto-Start

Read `config.yaml`:
- If `workflow.auto_start: true` AND `active.count < max_concurrent`
- Offer to start the feature immediately

## Output

```
✅ Feature Unblocked: {id}

Feature: {name}
Was blocked for: {duration}
Original reason: {reason}

Status:
  Dependencies: ✅ Satisfied
  Ready to start: ✅ Yes

Current parallel usage: 1/3

Options:
  [1] Start feature now (/start-feature {id})
  [2] Add to queue and start later
  [3] View feature details
```

## Error Handling

| Error | Description | Solution |
|-------|-------------|----------|
| NOT_FOUND | Feature not in blocked list | Check feature ID |
| NOT_BLOCKED | Feature is not blocked | Check current status |
| DEPENDENCIES_UNSATISFIED | Dependencies not met | Complete dependencies first |

## Examples

```
/unblock-feature feat-upload

Output:
🔓 Feature Unblocked: feat-upload

Feature: File Upload
Was blocked for: 2 weeks
Original reason: "Waiting for storage infrastructure"

Status:
  Dependencies: ✅ All satisfied
  Storage feat-storage: ✅ Completed
  Ready to start: ✅ Yes

Options:
  [1] Start feature now
  [2] Add to queue
```
