---
description: 'Create a new feature request through interactive dialogue, generate documentation, and add to queue.'
---

# Skill: new-feature

Create a new feature request. You will collect requirements through dialogue, analyze complexity, potentially split into multiple features, generate documentation, and add to the development queue.

## When to use this skill

Use this skill when the user wants to create a new feature request or start working on a new feature.

## Execution Steps

### Step 0: Load Project Context

Before creating any feature, load the project context to understand the codebase.

**Context Loading Priority:**

1. Check project-context.md - if exists, read and load
2. Check CLAUDE.md - if exists, read and offer to convert to project-context.md
3. Trigger Quick Explore - scan project structure, tech stack, code patterns, generate project-context.md

### Step 1: Collect Information

Collect the following information from the user:
- **name**: Feature name (short, e.g., "User Authentication")
- **description**: Detailed description of what needs to be built
- **priority**: 1-100 (default: 50, higher = more urgent)
- **dependencies**: List of other feature IDs this depends on (optional)

### Step 2: AI Analysis - Identify User Value Points & Generate Scenarios

Analyze the feature description to:
1. Identify independent user value points
2. Generate Gherkin format acceptance scenarios for each value point

**User Value Point Definition:**
A user value point is a distinct capability that enables users to accomplish something meaningful, can be delivered and tested independently, and has clear acceptance criteria.

### Step 3: Size Assessment and Split Decision

Based on the number of user value points, assess the feature size:

| Value Points | Size | Action |
|--------------|------|--------|
| 1 | Small | Create directly |
| 2 | Medium | Create directly (optional split suggestion) |
| 3+ | Large | Recommend split |

If value points ≥ 3, recommend splitting the feature to prevent AI context overflow during implementation.

### Step 4: Generate Feature ID(s)

Generate a slug from the feature name for single features, or generate IDs for each sub-feature for split features.

ID format: `{prefix}-{slug}` (prefix from config, default "feat")

### Step 5: Check for Conflicts

Check if the ID already exists in:
- features/pending-{id}/
- features/active-{id}/
- features/archive/done-{id}/
- feature-workflow/queue.yaml

### Step 6: Create Feature Directory and Files

Create directory: `features/pending-{id}/`

Create three files:
- **spec.md**: Requirements specification with user value points and Gherkin scenarios
- **task.md**: Task breakdown
- **checklist.md**: Completion checklist

### Step 7: Update Queue

Add feature(s) to `feature-workflow/queue.yaml` pending list, sorted by priority (descending).

### Step 8: Check Auto-Start

Read `feature-workflow/config.yaml` - if `workflow.auto_start: true` AND `active.count < max_concurrent`, start the first feature automatically.

## Output

```
✅ Feature created successfully!

ID: {id}
Size: {S|M|L}
Directory: features/pending-{id}

Documents:
- spec.md      Requirements specification
- task.md      Task breakdown
- checklist.md Completion checklist

Status: pending (waiting for development)
```

## Error Handling

| Error | Description | Solution |
|-------|-------------|----------|
| ID_CONFLICT | ID already exists | Use different name or accept suggested ID |
| QUEUE_ERROR | Failed to update queue | Check queue.yaml permissions |
| TEMPLATE_ERROR | Template processing failed | Check templates directory |
| PERMISSION_ERROR | Cannot create directory | Check filesystem permissions |
