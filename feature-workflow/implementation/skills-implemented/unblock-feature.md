---
description: 'Unblock a feature and return it to the pending queue.'
---

# Skill: unblock-feature

Unblock a feature and return it to the pending queue for scheduling.

## Usage

```
/unblock-feature <feature-id>
```

## Pre-flight Checks

- Feature must be in `blocked` list in `queue.yaml`

## Execution Steps

### Step 1: Check Feature Status

Find the feature in `queue.yaml` `blocked` list.
If not found, return error.

### Step 2: Update Queue

Move from `blocked` to `pending` in `queue.yaml`:
- Remove from `blocked`
- Add to `pending` with original priority
- Sort `pending` by priority (descending)

Update `meta.last_updated`.

### Step 3: Check Auto-Start

If `config.yaml` `workflow.auto_start: true`:
- Check if there's an available slot
- If this feature is highest priority: call `start-feature`

## Output

### Success - Pending

```
🔓 Feature feat-report unblocked

Status: pending (waiting to be scheduled)

Position in queue: #2 (priority 70)
```

### Success - Auto-Started

```
🔓 Feature feat-report unblocked

🚀 Auto-started! (highest priority, slot available)
cd ../OA_Tool-feat-report
```

### Error

```
❌ Feature feat-report is not blocked

Use /list-features to see current status.
```

## Error Codes

| Code | Description |
|------|-------------|
| NOT_FOUND | Feature doesn't exist |
| NOT_BLOCKED | Feature is not in blocked list |

## Examples

```
/unblock-feature feat-report
→ 🔓 Feature feat-report unblocked, status: pending

/unblock-feature feat-report  (when auto-start triggers)
→ 🔓 Feature feat-report unblocked, 🚀 Auto-started!
```
