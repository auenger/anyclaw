---
last_updated: '{{date}}'
version: 1
features_completed: 0
---

# Project Context: {{project_name}}

> This file contains critical rules and patterns that AI agents must follow when implementing code. Keep it concise and focused on non-obvious details.

---

## Technology Stack

| Category | Technology | Version | Notes |
|----------|-----------|---------|-------|
| Frontend | {{frontend_tech}} | {{version}} | {{notes}} |
| Backend | {{backend_tech}} | {{version}} | {{notes}} |
| Database | {{database_tech}} | {{version}} | {{notes}} |
| Testing | {{testing_tech}} | {{version}} | {{notes}} |

## Directory Structure

```
{{project_name}}/
├── src/
│   ├── components/     # Shared components
│   ├── pages/          # Page routes
│   ├── services/       # API services
│   ├── hooks/          # Custom hooks
│   └── utils/          # Utility functions
├── tests/
├── docs/
└── feature-workflow/
```

## Critical Rules

### Must Follow

- Rule 1: {{critical_rule_1}}
- Rule 2: {{critical_rule_2}}

### Must Avoid

- Anti-pattern 1: {{anti_pattern_1}}
- Anti-pattern 2: {{anti_pattern_2}}

## Code Patterns

### Naming Conventions

- Files: {{file_naming_pattern}}
- Components: {{component_naming_pattern}}
- Functions: {{function_naming_pattern}}

### Import Patterns

```javascript
// Preferred import style
import { Component } from '@/components'
```

### Error Handling

```javascript
// Standard error handling pattern
try {
  // operation
} catch (error) {
  // handle error
}
```

## Testing Patterns

### Unit Tests

- Test file location: `__tests__/` or `.test.ts`
- Naming: `{{module}}.test.ts`

### E2E Tests

- Framework: Playwright
- Location: `e2e/` or `tests/e2e/`

## Recent Changes

| Date | Feature | Impact |
|------|---------|--------|
| {{date}} | {{feature_id}} | {{impact_description}} |

## Update Log

- {{date}}: Initial project context created
