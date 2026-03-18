---
description: 'List all features with their status, priority, and filter options.'
---

# Skill: list-features

List all features in the workflow with their status, priority, and other details. Supports filtering and sorting.

## When to use this skill

Use this skill when the user wants to see the current state of all features or find specific features.

## Parameters

- `--status=<status>`: Filter by status (pending, active, blocked, done)
- `--sort=<field>`: Sort by field (priority, name, created, size)
- `--format=<format>`: Output format (table, json, detailed)

## Execution Steps

### Step 1: Load Queue Data

Read `feature-workflow/queue.yaml`:
- pending list
- active list
- blocked list

Read `feature-workflow/archive-log.yaml`:
- completed features

### Step 2: Apply Filters

Apply status filter if provided:
- `--status=pending`: Show only pending features
- `--status=active`: Show only active features
- `--status=blocked`: Show only blocked features
- `--status=done`: Show only completed features

### Step 3: Sort Results

Sort by specified field (default: priority):
- `priority`: Sort by priority (high to low)
- `name`: Sort alphabetically
- `created`: Sort by creation date
- `size`: Sort by size (S, M, L)

### Step 4: Format Output

Format results according to --format parameter:
- `table`: ASCII table format
- `json`: JSON format
- `detailed`: Full details for each feature

## Output

### Table Format (default)

```
┌─────────────────────────────────────────────────────────────────┐
│                    Feature Queue Summary                         │
├─────────────────────────────────────────────────────────────────┤
│                                                                  │
│  Pending (5):                                                    │
│  ┌──────────────┬─────────────┬──────────┬──────────┬────────┐  │
│  │ ID           │ Name        │ Priority │ Size     │ Deps   │  │
│  ├──────────────┼─────────────┼──────────┼──────────┼────────┤  │
│  │ feat-auth    │ Auth        │ 80       │ L        │ -      │  │
│  │ feat-db      │ Database    │ 70       │ M        │ -      │  │
│  └──────────────┴─────────────┴──────────┴──────────┴────────┘  │
│                                                                  │
│  Active (2):                                                     │
│  ┌──────────────┬─────────────┬──────────┬──────────┬────────┐  │
│  │ ID           │ Name        │ Priority │ Progress │ Branch │  │
│  ├──────────────┼─────────────┼──────────┼──────────┼────────┤  │
│  │ feat-api     │ API Layer   │ 90       │ 3/5      │ api    │  │
│  │ feat-ui      │ UI Update   │ 60       │ 1/4      │ ui     │  │
│  └──────────────┴─────────────┴──────────┴──────────┴────────┘  │
│                                                                  │
│  Blocked (1):                                                    │
│  ┌──────────────┬─────────────┬──────────┬────────────────────┐ │
│  │ ID           │ Name        │ Priority │ Blocked Reason     │ │
│  ├──────────────┼─────────────┼──────────┼────────────────────┤ │
│  │ feat-upload  │ Upload      │ 50       │ Waiting for storage│ │
│  └──────────────┴─────────────┴──────────┴────────────────────┘ │
│                                                                  │
│  Statistics:                                                     │
│  Total: 18                                                       │
│  Pending: 5 | Active: 2 | Blocked: 1 | Done: 10                  │
│  Parallel usage: 2/3 (max_concurrent)                            │
└─────────────────────────────────────────────────────────────────┘
```

### JSON Format

```json
{
  "pending": [
    {
      "id": "feat-auth",
      "name": "Auth",
      "priority": 80,
      "size": "L",
      "dependencies": []
    }
  ],
  "active": [
    {
      "id": "feat-api",
      "name": "API Layer",
      "priority": 90,
      "progress": "3/5",
      "branch": "api"
    }
  ],
  "blocked": [
    {
      "id": "feat-upload",
      "name": "Upload",
      "priority": 50,
      "reason": "Waiting for storage"
    }
  ],
  "statistics": {
    "total": 18,
    "pending": 5,
    "active": 2,
    "blocked": 1,
    "done": 10,
    "parallel_usage": "2/3"
  }
}
```

### Detailed Format

Show full details for each feature including:
- Basic info (id, name, priority, size)
- Dependencies
- Parent/children relationships
- Creation date
- For active features: branch, worktree, progress
- For blocked features: block reason

## Error Handling

| Error | Description | Solution |
|-------|-------------|----------|
| QUEUE_NOT_FOUND | queue.yaml not found | Initialize feature workflow first |
| INVALID_STATUS | Invalid status filter | Use valid status value |
| ARCHIVE_ERROR | Cannot read archive-log | Check archive-log.yaml |
