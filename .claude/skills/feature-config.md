---
description: 'Manage feature workflow configuration settings.'
---

# Skill: feature-config

Manage and view feature workflow configuration settings. Use this skill to check or modify workflow behavior.

## When to use this skill

Use this skill when the user wants to view or modify feature workflow configuration.

## Parameters

- `--show`: Show current configuration
- `--set=<key=value>`: Set a configuration value
- `--reset`: Reset to default configuration

## Execution Steps

### Step 1: Load Configuration

Read `feature-workflow/config.yaml`

### Step 2: Display or Modify

**If --show:**
Display all configuration values with descriptions

**If --set:**
- Validate the key
- Validate the value
- Update configuration
- Save changes

**If --reset:**
- Restore default configuration
- Save changes

### Step 3: Update Related Files

If configuration changes affect:
- Queue structure → Update queue.yaml
- Template paths → Verify templates exist
- Git settings → Verify git configuration

## Configuration Options

| Key | Type | Default | Description |
|-----|------|---------|-------------|
| `project.name` | string | - | Project name |
| `project.main_branch` | string | "main" | Main branch name |
| `git.remote` | string | "origin" | Git remote name |
| `git.branch_prefix` | string | "feature" | Branch name prefix |
| `workflow.auto_start` | boolean | false | Auto-start features |
| `workflow.max_concurrent` | number | 3 | Max active features |
| `worktree.base` | string | ".." | Worktree base path |
| `worktree.prefix` | string | project name | Worktree prefix |
| `feature.id_prefix` | string | "feat" | Feature ID prefix |
| `feature.default_priority` | number | 50 | Default priority |

## Output

### Show Configuration

```
┌─────────────────────────────────────────────────────────────────┐
│                    Feature Workflow Configuration                 │
├─────────────────────────────────────────────────────────────────┤
│                                                                  │
│  Project:                                                        │
│    name: OA_Tool                                                │
│    main_branch: main                                            │
│                                                                  │
│  Git:                                                            │
│    remote: origin                                               │
│    branch_prefix: feature                                       │
│                                                                  │
│  Workflow:                                                       │
│    auto_start: false                                           │
│    max_concurrent: 3                                            │
│                                                                  │
│  Worktree:                                                       │
│    base: ..                                                    │
│    prefix: OA_Tool                                              │
│                                                                  │
│  Feature:                                                        │
│    id_prefix: feat                                              │
│    default_priority: 50                                         │
│                                                                  │
└─────────────────────────────────────────────────────────────────┘
```

### Set Configuration

```
✅ Configuration Updated

Key: workflow.max_concurrent
Old value: 3
New value: 5

This change allows more parallel feature development.
```

## Error Handling

| Error | Description | Solution |
|-------|-------------|----------|
| CONFIG_NOT_FOUND | config.yaml not found | Initialize workflow first |
| INVALID_KEY | Configuration key doesn't exist | Check key name |
| INVALID_VALUE | Value type or range invalid | Check value format |
| SAVE_FAILED | Cannot save configuration | Check file permissions |

## Examples

```
/feature-config --show

/feature-config --set=workflow.max_concurrent=5

/feature-config --set=workflow.auto_start=true

/feature-config --set=feature.default_priority=70

/feature-config --reset
```
