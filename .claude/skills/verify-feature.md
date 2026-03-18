---
description: 'Verify implemented feature by checking tasks, running tests, and validating against acceptance criteria.'
---

# Skill: verify-feature

Verify the implemented feature by checking completion status, running tests, and validating against acceptance criteria.

## When to use this skill

Use this skill when the user wants to verify that an implemented feature meets all requirements.

## Parameters

- `feature-id`: The feature ID to verify (required)

## Execution Steps

### Step 1: Load Feature Context

Read the feature documents:
- `features/active-{id}/spec.md` - Acceptance criteria
- `features/active-{id}/task.md` - Task list
- `features/active-{id}/checklist.md` - Completion checklist

### Step 2: Check Task Completion

Verify all tasks in `task.md` are completed:
- Check each checkbox
- Verify task notes
- Identify incomplete tasks

### Step 3: Verify Acceptance Criteria

Review Gherkin scenarios in `spec.md`:
- Parse each scenario
- Verify implementation meets criteria
- Test scenarios if possible

### Step 4: Run Tests

Execute available tests:
- Unit tests
- Integration tests
- Manual testing for UI features

### Step 5: Code Quality Check

Review:
- Code style compliance
- Error handling
- Edge cases
- Documentation

### Step 6: Generate Report

Output verification results with:
- Completion status
- Test results
- Issues found (if any)
- Recommendations

## Output

```
📋 Feature Verification Report: {id}

Completion Status:
  Tasks: ✅ 5/5 completed
  Tests: ✅ 12/12 passed
  Checklist: ✅ All items checked

Acceptance Criteria:
  ✅ User registration works
  ✅ User login works
  ✅ User logout works
  ⚠️ Permission tracking incomplete

Issues Found:
  - Permission tracking not fully implemented

Recommendations:
  - Complete permission tracking before completing feature

Overall: ⚠️ Minor issues found

Options:
  [1] Fix issues and re-verify
  [2] Proceed to complete-feature (will note issues)
  [3] Exit and fix manually
```

## Error Handling

| Error | Description | Solution |
|-------|-------------|----------|
| NOT_ACTIVE | Feature not in active list | Check feature status |
| NO_TASKS | No tasks defined | Add tasks to task.md |
| TESTS_FAILED | Tests are failing | Review and fix failing tests |
| CRITERIA_NOT_MET | Acceptance criteria not met | Implement missing functionality |

## Exit Codes

| Code | Meaning |
|------|---------|
| 0 | Verification passed |
| 1 | Minor issues found |
| 2 | Major issues found |
| 3 | Critical failures |
