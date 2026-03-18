---
description: 'Block a feature from being automatically scheduled.'
---

# Skill: block-feature

Block a feature from being automatically scheduled. Use when waiting for dependencies or external factors.

## Usage

```
/block-feature <feature-id> [reason]
```

Parameters:
- `feature-id`: The feature ID (required)
- `reason`: Why it's being blocked (optional, default: "Manually blocked")

## Pre-flight Checks

- Feature must be in `pending` or `blocked` list
- Cannot block `active` features

## Execution Steps

### Step 1: Check Feature Status

Find the feature in `queue.yaml`:
- If in `active`: Return error (cannot block active features)
- If already in `blocked`: Update the reason
- If in `pending`: Proceed to block

### Step 2: Update Queue

Move from `pending` to `blocked` in `queue.yaml`:

```yaml
blocked:
  - id: {id}
    name: {name}
    reason: "{reason}"
    created: {original_created}
```

Update `meta.last_updated`.

## Output

### Success

```
🔒 Feature feat-report blocked

Reason: Waiting for API to be ready

Unblock: /unblock-feature feat-report
```

### Error - Cannot Block Active

```
❌ Cannot block active feature feat-auth

The feature is currently in development.
Complete or abandon it first:
  /complete-feature feat-auth
```

## Error Codes

| Code | Description | Solution |
|------|-------------|----------|
| NOT_FOUND | Feature doesn't exist | Check ID |
| CANNOT_BLOCK_ACTIVE | Feature is active | Complete or abandon first |
| ALREADY_BLOCKED | Already blocked | Reason updated |

## Examples

```
/block-feature feat-report Waiting for third-party API
→ 🔒 Feature feat-report blocked (reason: Waiting for third-party API)

/block-feature feat-dashboard
→ 🔒 Feature feat-dashboard blocked (reason: Manually blocked)
```
