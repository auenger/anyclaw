---
description: 'Block a feature with a reason, preventing it from being started.'
---

# Skill: block-feature

Block a pending feature with a specific reason, preventing it from being started until unblocked.

## When to use this skill

Use this skill when a feature needs to be blocked from starting due to dependencies, issues, or strategic reasons.

## Parameters

- `feature-id`: The feature ID to block (required)
- `--reason=<text>`: Reason for blocking (required)

## Execution Steps

### Step 1: Find Feature

Locate the feature in `queue.yaml`:
- Check pending list
- If not found, check active list (warn user)
- If in blocked list, error (already blocked)

### Step 2: Validate Block Reason

Ensure block reason is provided and meaningful:
- Not empty
- Not too vague (e.g., "just because")
- Should be actionable if possible

### Step 3: Update Queue

Move feature from pending to blocked list in `queue.yaml`:

```yaml
blocked:
  - id: {id}
    name: {name}
    priority: {priority}
    size: {size}
    parent: {parent or null}
    children: {children or []}
    dependencies: {dependencies}
    blocked_at: {timestamp}
    blocked_by: {user}
    reason: {reason}
```

### Step 4: Handle Child Features

If feature has children:
- Option 1: Block all children automatically
- Option 2: Warn user but don't block children
- Option 3: Ask user what to do

### Step 5: Update Blocked Features

If any active features depend on this feature:
- Warn user
- Offer to block dependent features
- Or note in dependent features

## Output

```
🚫 Feature Blocked: {id}

Feature: {name}
Reason: {reason}

Blocked at: {timestamp}
Blocked by: {user}

Affected features:
  - feat-child-1 (depends on {id})
  - feat-child-2 (depends on {id})

Options:
  [1] Block dependent features too
  [2] Keep dependent features active
  [3] View dependent feature details
```

## Error Handling

| Error | Description | Solution |
|-------|-------------|----------|
| NOT_FOUND | Feature not found | Check feature ID |
| ALREADY_BLOCKED | Feature already blocked | Check current status |
| ACTIVE_FEATURE | Feature is active | Cannot block active feature |
| NO_REASON | No block reason provided | Provide --reason parameter |

## Examples

```
/block-feature feat-upload --reason "Waiting for storage infrastructure to be completed"

/block-feature feat-auth --reason "Security review pending, waiting for approval from security team"

/block-feature feat-payment --reason "Payment gateway API not yet available, ETA 2 weeks"
```
