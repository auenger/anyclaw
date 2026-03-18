---
description: 'Create a new feature request through interactive dialogue, generate documentation, and add to queue.'
---

# Skill: new-feature

Create a new feature request. You will collect requirements through dialogue, analyze complexity, potentially split into multiple features, generate documentation, and add to the development queue.

## Execution Steps

### Step 0: Load Project Context

Before creating any feature, load the project context to understand the codebase.

**Context Loading Priority:**

```
1. Check project-context.md
   ├── Exists → Read and load ✅
   └── Not found ↓

2. Check CLAUDE.md
   ├── Exists → Read and offer to convert to project-context.md
   └── Not found ↓

3. Trigger Quick Explore
   ├── Scan project structure, tech stack, code patterns
   └── Generate project-context.md
```

**Step 0.1: Check for project-context.md**

Look for file at:
- `{project-root}/project-context.md`
- `{project-root}/docs/project-context.md`

If found:
```
📚 Project Context Loaded

Source: project-context.md
Last Updated: {date}
Version: {version}

Key Info:
- Tech Stack: {main_technologies}
- Critical Rules: {number} rules loaded
- Recent Changes: {last_3_features}

Proceeding with feature creation...
```

**Step 0.2: Fallback to CLAUDE.md**

If project-context.md not found, check for:
- `{project-root}/CLAUDE.md`
- `{project-root}/.claude/CLAUDE.md`

If found:
```
📚 Found CLAUDE.md instead of project-context.md

Loaded context from CLAUDE.md.
💡 Tip: Consider creating project-context.md for better AI context management.

Proceeding with feature creation...
```

**Step 0.3: Generate Project Context (if neither found)**

If no context file exists, perform quick project exploration:

```
🔍 No project context found. Generating...

Analyzing:
├── package.json / requirements.txt / Cargo.toml
├── Configuration files (tsconfig, vite, webpack, etc.)
├── Directory structure
├── Code patterns (naming, organization)
└── Testing setup

Generating project-context.md...
✅ project-context.md created
```

**Quick Explore checks:**

1. **Tech Stack Discovery:**
   - Read package.json/requirements.txt for dependencies
   - Check config files (tsconfig.json, vite.config.ts, etc.)
   - Identify framework and language versions

2. **Directory Structure:**
   - List main directories
   - Identify code organization patterns

3. **Code Patterns:**
   - Scan a few files for naming conventions
   - Identify import patterns
   - Note any obvious rules

4. **Generate Minimal Context:**
   ```markdown
   ---
   last_updated: {date}
   version: 1
   features_completed: 0
   generated: true
   ---

   # Project Context: {project_name}

   > Auto-generated context. Review and update as needed.

   ## Technology Stack

   | Category | Technology | Version |
   |----------|-----------|---------|
   | {category} | {tech} | {version} |

   ## Directory Structure

   {main_directories}

   ## Critical Rules

   _To be documented as features are completed._

   ## Recent Changes

   _No features completed yet._
   ```

**Context loaded successfully → Continue to Step 1**

---

### Step 1: Collect Information

If the user provided a description, extract the following:
- **name**: Feature name (short, e.g., "User Authentication")
- **description**: Detailed description of what needs to be built
- **priority**: 1-100 (default: 50, higher = more urgent)
- **dependencies**: List of other feature IDs this depends on (optional)

If information is incomplete, ask the user:

```
Please provide the following information:

1. Feature name (short description, e.g., "User Authentication")
2. Detailed description (what problem does this solve?)
3. Priority (1-100, higher = more urgent, default 50)
4. Dependencies? (other feature IDs, if any)
```

### Step 2: AI Analysis - Identify User Value Points & Generate Scenarios

Analyze the feature description to:
1. Identify independent user value points
2. Generate Gherkin format acceptance scenarios for each value point

**Analysis Process:**
1. Parse the description for distinct capabilities
2. Identify what users can accomplish with each capability
3. Look for natural boundaries (different user goals, different workflows)
4. Consider technical independence (can each part work standalone?)
5. **Generate Gherkin scenarios** for each user value point

**User Value Point Definition:**
A user value point is a distinct capability that:
- Enables users to accomplish something meaningful
- Can be delivered and tested independently
- Has clear acceptance criteria

**Gherkin Scenario Generation Rules:**
- Each user value point should have 1-3 scenarios
- Include happy path (正常流程) and error cases (异常情况)
- Use Given-When-Then format
- Be specific and testable
- For frontend features: include UI interaction steps

**Example Analysis:**

Input: "User authentication system with registration, login, and permission management"

Output:
```
📊 User Value Points Identified:

1. User Registration - Users can create new accounts
2. User Login - Users can access the system
3. Permission Management - Users can control access permissions

📝 Gherkin Scenarios Generated:

## Value Point 1: User Registration

### Scenario: Successful Registration
Given 用户在注册页面
When 用户输入有效的用户名 "testuser" 和密码 "Test123!"
And 点击注册按钮
Then 账户创建成功
And 显示欢迎信息

### Scenario: Duplicate Username
Given 用户在注册页面
And 用户名 "testuser" 已存在
When 用户输入用户名 "testuser" 和密码 "Test123!"
And 点击注册按钮
Then 显示错误提示 "用户名已存在"

## Value Point 2: User Login

### Scenario: Successful Login
Given 用户在登录页面
And 用户 "testuser" 已注册
When 用户输入正确的用户名和密码
And 点击登录按钮
Then 跳转到首页
And 显示用户信息

### Scenario: Wrong Password
Given 用户在登录页面
When 用户输入正确的用户名和错误的密码
And 点击登录按钮
Then 显示错误提示 "密码错误"
And 用户仍在登录页面

## Value Point 3: Permission Management

### Scenario: Admin Assigns Permission
Given 管理员在权限管理页面
And 用户 "testuser" 存在
When 管理员给 "testuser" 分配 "editor" 角色
Then "testuser" 获得 editor 权限
And 显示操作成功

Analysis: This feature contains 3 independent user value points.
```

### Step 3: Size Assessment and Split Decision

Based on the number of user value points, assess the feature size:

**Size Thresholds:**
| Value Points | Size | Action |
|--------------|------|--------|
| 1 | Small | Create directly |
| 2 | Medium | Create directly (optional split suggestion) |
| 3+ | Large | **Recommend split** |

**Split Decision Logic:**

If value points ≥ 3:
```
⚠️ Large Feature Detected

This feature contains {N} independent user value points.
To prevent AI context overflow during implementation, we recommend splitting.

Proposed split:
┌─────────────────────────────────────────────────────────────┐
│ Original: {original_name}                                   │
├─────────────────────────────────────────────────────────────┤
│ Split into:                                                  │
│                                                              │
│ 1. {id-1} - {value_point_1}                                │
│ 2. {id-2} - {value_point_2}                                │
│ 3. {id-3} - {value_point_3}                                │
│    ...                                                       │
└─────────────────────────────────────────────────────────────┘

Dependencies will be set automatically:
- First feature: no dependencies
- Subsequent features: depend on previous ones

[Y] Confirm split and create {N} features
[N] Keep as single feature (may affect AI coding quality)
[E] I want to define my own split
```

If value points = 2:
```
📋 Medium Feature Detected

This feature contains 2 related user value points.
You can keep it as one feature or split into two.

[K] Keep as single feature
[S] Split into 2 features
```

If value points = 1:
- Proceed directly to Step 4

### Step 4: Generate Feature ID(s)

#### For Single Feature:

Generate a slug from the feature name:
- Convert to lowercase
- Replace spaces with hyphens
- Remove special characters
- Example: "User Authentication" → "user-auth" → ID: "feat-user-auth"

ID format: `{prefix}-{slug}` (prefix from config, default "feat")

#### For Split Features:

Generate IDs for each sub-feature:
- Base slug from original feature name
- Suffix from each value point
- Example:
  - "User Authentication" + "Login" → "feat-auth-login"
  - "User Authentication" + "Register" → "feat-auth-register"

### Step 5: Check for Conflicts

For each feature ID to be created:

Check if the ID already exists:
1. Check `features/pending-{id}/` directory
2. Check `features/active-{id}/` directory
3. Check `features/archive/done-{id}/` directory
4. Check `feature-workflow/queue.yaml`

If conflict exists, suggest a new ID like `feat-auth-2`.

### Step 6: Create Feature Directory and Files

#### For Single Feature:

Create directory: `features/pending-{id}/`

Create three files using templates from `feature-workflow/templates/`:

**spec.md:**
```markdown
# Feature: {id} {name}

## Basic Information
- **ID**: {id}
- **Name**: {name}
- **Priority**: {priority}
- **Size**: {S|M|L}
- **Dependencies**: {dependencies}
- **Parent**: {parent_id or null}
- **Children**: {child_ids or empty}
- **Created**: {timestamp}

## Description
{user-provided description}

## User Value Points
{ai_generated_value_points}

## Context Analysis
### Reference Code
<!-- List existing files to reference or modify -->

### Related Documents
<!-- List related design docs, API docs -->

### Related Features
<!-- List related completed features -->

## Technical Solution
<!-- To be filled during implementation -->

## Acceptance Criteria (Gherkin)

### User Story
作为 {role}，我希望 {goal}，以便 {value}

### Scenarios

#### Scenario 1: {scenario_name}
```gherkin
Given {precondition}
When {action}
Then {expected_result}
```

{more_ai_generated_scenarios}

### UI/Interaction Checkpoints (if frontend)
- [ ] Page layout correct
- [ ] Interaction flow smooth
- [ ] Error messages friendly
- [ ] Responsive design

### General Checklist
- [ ] Feature fully implemented
- [ ] Self-tested
- [ ] No obvious bugs
```

**task.md:**
```markdown
# Tasks: {id}

## Task Breakdown

### 1. Module/Component
- [ ] Task item 1
- [ ] Task item 2

### 2. API Endpoints
- [ ] Endpoint 1
- [ ] Endpoint 2

### 3. Frontend Pages
- [ ] Page 1
- [ ] Page 2

### 4. Other
- [ ] Other tasks

---

## Progress Log

| Date | Progress | Notes |
|------|----------|-------|
|      |          |       |
```

**checklist.md:**
```markdown
# Checklist: {id}

## Completion Checklist

### Development
- [ ] All tasks completed (see task.md)
- [ ] Code self-tested
- [ ] Edge cases handled

### Code Quality
- [ ] Code style follows conventions
- [ ] No obvious code smells
- [ ] Necessary comments added

### Testing
- [ ] Unit tests written (if needed)
- [ ] Tests passing

### Documentation
- [ ] spec.md technical solution filled
- [ ] Related docs updated

### Commit Ready
- [ ] Changes staged
- [ ] Commit message ready
```

#### For Split Features:

Create directories for each sub-feature: `features/pending-{sub-id}/`

For each sub-feature, create the same three files with:
- **Size**: "S" (each sub-feature should be small)
- **Parent**: The original feature ID (if this is a sub-feature)
- **Children**: Empty (unless further split)
- **Dependencies**: Previous sub-features in the split chain

### Step 7: Update Queue

Read `feature-workflow/queue.yaml` and add feature(s) to pending list:

#### For Single Feature:

```yaml
pending:
  - id: {id}
    name: {name}
    priority: {priority}
    size: {S|M|L}
    parent: null
    children: []
    dependencies: {dependencies}
    created: {timestamp}
```

#### For Split Features:

```yaml
pending:
  - id: {id}-1
    name: {sub_name_1}
    priority: {priority}
    size: S
    parent: {original_id}
    children: []
    dependencies: {original_dependencies}
    created: {timestamp}

  - id: {id}-2
    name: {sub_name_2}
    priority: {priority}
    size: S
    parent: {original_id}
    children: []
    dependencies: [{id}-1]  # depends on first
    created: {timestamp}

  # ... more sub-features
```

Also create a parent entry to track the group:

```yaml
pending:
  - id: {original_id}
    name: {original_name}
    priority: {priority}
    size: L
    parent: null
    children: [{id}-1, {id}-2, ...]
    dependencies: {original_dependencies}
    created: {timestamp}
    split: true  # marks this as a split group header
```

Sort pending list by priority (descending).

Update `meta.last_updated`.

### Step 8: Check Auto-Start

Read `feature-workflow/config.yaml`:
- If `workflow.auto_start: true` AND `active.count < max_concurrent`:
  - For split features: Start the first sub-feature (no dependencies)
  - For single feature: Start this feature
  - Return status: `started`
- Else:
  - Return status: `pending`

## Output

### Single Feature Output:
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

# If auto-started:
🚀 Development started automatically!
Worktree: ../OA_Tool-{slug}
Switch: cd ../OA_Tool-{slug}
```

### Split Features Output:
```
✅ Features created successfully!

Original: {original_name} (split into {N} features)

┌─────────────────────────────────────────────────────────────┐
│ #  │ ID                │ Name                  │ Dependencies │
├─────────────────────────────────────────────────────────────┤
│ 1  │ {id}-1           │ {name_1}              │ -             │
│ 2  │ {id}-2           │ {name_2}              │ {id}-1         │
│ 3  │ {id}-3           │ {name_3}              │ {id}-2         │
└─────────────────────────────────────────────────────────────┘

Directories:
- features/pending-{id}-1
- features/pending-{id}-2
- features/pending-{id}-3

Status: pending (waiting for development)

💡 Tip: Features will be developed in dependency order.
   Complete each feature before starting the next.

# If auto-started:
🚀 First feature started automatically!
Worktree: ../OA_Tool-{slug}-1
Switch: cd ../OA_Tool-{slug}-1
```

## Error Handling

| Error | Description | Solution |
|-------|-------------|----------|
| ID_CONFLICT | ID already exists | Use different name or accept suggested ID |
| QUEUE_ERROR | Failed to update queue | Check queue.yaml permissions |
| TEMPLATE_ERROR | Template processing failed | Check templates directory |
| PERMISSION_ERROR | Cannot create directory | Check filesystem permissions |
| SPLIT_ABORTED | User aborted split | Create as single feature with warning |

## Notes

1. **User value first** - Always split by user value, not technical layers
2. **Dependency chain** - Sub-features depend on previous ones in sequence
3. **Context protection** - Splitting prevents AI context overflow
4. **Parent tracking** - Parent feature tracks all children for visibility
