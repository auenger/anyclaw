---
description: 'Verify feature completion by checking tasks, running tests, and validating Gherkin acceptance scenarios. For frontend features, use Playwright MCP (preferred) or npx playwright test (fallback) with trace and screenshot evidence.'
---

# Skill: verify-feature

Verify that a feature is complete by checking tasks, running tests, and validating Gherkin acceptance scenarios.

**For frontend features:**
- **Method A (Preferred)**: Use Playwright MCP for real-time browser interaction
- **Method B (Fallback)**: Use `npx playwright test` with auto-generated E2E tests

Both methods capture:
- Screenshots for visual evidence
- Trace files for debugging
- HTML reports for review

## Usage

```
/verify-feature <feature-id>
```

## Pre-flight Checks

- Feature must be in `queue.yaml` active list
- Feature directory exists at `features/active-{id}/`

## Execution Steps

### Step 1: Check Task Completion

Read `features/active-{id}/task.md`:
- Count total tasks
- Count completed tasks (checked boxes)
- List incomplete tasks

```
📋 Task Status: 4/5 complete

Incomplete:
  - [ ] Write unit tests
```

### Step 2: Run Code Quality Checks

In the worktree:
```bash
cd {worktree_path}

# Check for common issues
# - Lint errors (if configured)
# - Type errors (if TypeScript)
# - Obvious code smells
```

### Step 3: Run Unit/Integration Tests

If tests exist:
```bash
npm test  # or appropriate test command
```

Record results:
- Tests run
- Tests passed
- Tests failed

### Step 4: Detect Feature Type

Determine if this feature requires frontend testing:

#### 4.1 Detection Criteria

Check for frontend indicators:
```yaml
frontend_indicators:
  - spec.md contains "UI/交互验收点" section
  - spec.md Gherkin scenarios mention page interactions
  - Component files exist (*.tsx, *.vue, *.svelte, *.jsx)
  - Page/Route files exist (pages/, routes/, app/)
  - spec.md has "页面" or "界面" or "按钮" keywords
```

#### 4.2 Feature Type Result

```
📊 Feature Type Detection:

Type: frontend | backend | fullstack

Frontend Indicators:
  - UI验收点: Yes
  - Component files: 3 found
  - Gherkin scenarios with UI: 4

Decision: Will use Playwright MCP for scenario validation
```

### Step 5: Validate Gherkin Acceptance Scenarios

Read `features/active-{id}/spec.md` and extract all Gherkin scenarios.

#### 5.1 For Backend/Non-UI Features: Code Analysis

Analyze the implementation code to verify:
- All Given conditions can be satisfied
- All When actions are implemented
- All Then expectations are met

#### 5.2 For Frontend Features: Playwright Testing

**IMPORTANT: Determine testing method first!**

##### 5.2.1 Check Playwright MCP Availability

Before starting, check if Playwright MCP tools are available:
- Look for tools like `playwright_navigate`, `playwright_click`, `playwright_fill`
- If available → Use **Method A: Playwright MCP**
- If NOT available → Use **Method B: npx playwright test**

##### 5.2.2 Method A: Playwright MCP (Preferred when available)

**Prerequisites:**
- Playwright MCP must be available
- Dev server must be running (or start automatically)

**Evidence Directory:**
```
features/active-{feature-id}/
└── evidence/                    # 所有证据保存在这里
    ├── verification-report.md   # 验证报告
    ├── screenshots/             # 截图
    │   ├── scenario-1-step-1.png
    │   └── scenario-2-step-1.png
    └── traces/                  # Trace 文件
        ├── trace-scenario-1.zip
        └── trace-scenario-2.zip
```

**Execution Process:**

For each Gherkin scenario:

1. **Parse Scenario Steps**
```gherkin
Scenario: 用户登录成功
  Given 用户在登录页面
  When 用户输入用户名 "testuser" 和密码 "password123"
  And 点击登录按钮
  Then 页面跳转到首页
  And 显示欢迎信息 "Welcome, testuser"
```

2. **Execute via Playwright MCP**

Use Playwright MCP tools to execute each step:

```
Step: Given 用户在登录页面
  Action: Navigate to /login
  Tool: playwright_navigate
  Screenshot: features/active-{id}/evidence/screenshots/scenario-1-step-1.png

Step: When 用户输入用户名 "testuser" 和密码 "password123"
  Action: Fill form fields
  Tool: playwright_fill, playwright_click
  Screenshot: features/active-{id}/evidence/screenshots/scenario-1-step-2.png
```

3. **Collect Evidence**
- Save screenshots to `features/active-{id}/evidence/screenshots/`
- Save trace file to `features/active-{id}/evidence/traces/`

##### 5.2.3 Method B: npx playwright test (Fallback)

**When to use:** Playwright MCP tools are NOT available

**Evidence Directory Structure:**
```
features/active-{feature-id}/
└── evidence/                    # 所有证据保存在这里
    ├── verification-report.md   # 验证报告
    ├── test-results.json        # JSON 测试结果
    ├── playwright-report/       # HTML 报告
    ├── e2e-tests/               # ⭐ E2E 测试脚本 (跟随 feature 归档)
    │   └── {feature-id}.spec.ts
    ├── screenshots/             # 截图
    │   ├── Scenario-1-Register-success-chromium.png
    │   └── Scenario-2-Login-success-chromium.png
    └── traces/                  # Trace 文件
        ├── Scenario-1-Register-success.zip
        └── Scenario-2-Login-success.zip
```

**IMPORTANT**: E2E 测试脚本必须复制到 feature 的 evidence 目录，以便随 feature 一起归档！

**Step 1: Create Evidence Directories**

```bash
# 在 feature 目录下创建 evidence 目录结构
mkdir -p features/active-{feature-id}/evidence/{screenshots,traces,playwright-report,e2e-tests}
```

**Step 2: Check/Create Playwright Config**

Check if `playwright.config.ts` exists. If not, create it:

```typescript
// playwright.config.ts
import { defineConfig, devices } from '@playwright/test';

export default defineConfig({
  testDir: './e2e',
  reporter: [
    ['html', { outputFolder: 'features/active-{feature-id}/evidence/playwright-report' }],
    ['json', { outputFile: 'features/active-{feature-id}/evidence/test-results.json' }]
  ],
  use: {
    baseURL: 'http://localhost:5173',
    trace: 'on',
    screenshot: 'on',
    video: 'retain-on-failure',
  },
  projects: [
    { name: 'chromium', use: { ...devices['Desktop Chrome'] } },
  ],
  webServer: {
    command: 'npm run dev',
    url: 'http://localhost:5173',
    reuseExistingServer: true,
  },
});
```

**Step 3: Generate E2E Tests from Gherkin**

For each Gherkin scenario in `spec.md`, generate a Playwright test:

```typescript
// e2e/{feature-id}.spec.ts
import { test, expect } from '@playwright/test';

test('Scenario: 用户登录成功', async ({ page }) => {
  // Given 用户在登录页面
  await page.goto('/login');

  // When 用户输入用户名 "testuser" 和密码 "password123"
  await page.fill('input#username', 'testuser');
  await page.fill('input#password', 'password123');

  // And 点击登录按钮
  await page.click('button[type="submit"]');

  // Then 页面跳转到首页
  await page.waitForURL('**/');
  await expect(page).toHaveURL(/.*\/$/);

  // And 显示欢迎信息
  await expect(page.locator('.welcome')).toContainText('testuser');
});
```

**Step 4: Run Playwright Tests**

**IMPORTANT: 动态指定报告输出路径，不依赖 playwright.config.ts 的硬编码路径！**

```bash
# Ensure dev server is running
npm run dev &

# ⭐ 方法1: 使用命令行动态指定报告路径 (推荐)
REPORT_DIR="features/active-{feature-id}/evidence"
npx playwright test \
  --trace on \
  --screenshot on \
  --reporter=html,json \
  e2e/{feature-id}.spec.ts

# 移动报告到正确的 feature 目录 (因为 playwright 默认输出到 playwright-report/)
mkdir -p "$REPORT_DIR/playwright-report"
[ -d "playwright-report" ] && mv playwright-report/* "$REPORT_DIR/playwright-report/"
[ -f "test-results.json" ] && mv test-results.json "$REPORT_DIR/"

# ⭐ 方法2: 创建临时配置文件覆盖路径
cat > playwright.config.temp.ts << EOF
import { defineConfig, devices } from '@playwright/test';
export default defineConfig({
  testDir: './e2e',
  reporter: [
    ['html', { outputFolder: 'features/active-{feature-id}/evidence/playwright-report' }],
    ['json', { outputFile: 'features/active-{feature-id}/evidence/test-results.json' }]
  ],
  use: { baseURL: 'http://localhost:5173', trace: 'on', screenshot: 'on' },
});
EOF
npx playwright test --config=playwright.config.temp.ts
rm playwright.config.temp.ts
```

**Step 5: Copy Evidence to Feature Directory**

**IMPORTANT**: 测试脚本必须复制到 feature 的 evidence 目录，以便随 feature 一起归档！

```bash
# Copy E2E test scripts to feature evidence (必须!)
# ⭐ 这一步很重要，确保测试脚本随 feature 归档
cp e2e/{feature-id}.spec.ts features/active-{feature-id}/evidence/e2e-tests/

# Copy trace files to feature evidence
cp test-results/*/trace.zip features/active-{feature-id}/evidence/traces/

# Copy screenshots to feature evidence
cp test-results/*/test-finished-1.png features/active-{feature-id}/evidence/screenshots/

# Rename for clarity (optional)
cd features/active-{feature-id}/evidence/screenshots/
for f in *.png; do
  # Extract scenario name from test-results directory
  mv "$f" "$(echo $f | sed 's/test-finished-1/Scenario-screenshot/')"
done
```

**Step 6: View Results**

```bash
# Open HTML report
npx playwright show-report features/active-{feature-id}/evidence/playwright-report

# View specific trace
npx playwright show-trace features/active-{feature-id}/evidence/traces/Scenario-1.zip
```

##### 5.2.4 Test Execution Summary Template

After running tests (either method), report:

```
📊 Playwright Test Results

Feature: {feature-id}
Method Used: Playwright MCP | npx playwright test

Test Summary:
  Total Scenarios: X
  Passed: X
  Failed: X
  Duration: Xs

Evidence Location:
  📁 features/active-{feature-id}/evidence/
  ├── verification-report.md     # 验证报告
  ├── test-results.json          # JSON 测试结果
  ├── playwright-report/         # HTML 报告
  │   └── index.html
  ├── e2e-tests/                 # ⭐ E2E 测试脚本
  │   └── {feature-id}.spec.ts
  ├── screenshots/               # 截图 (X files)
  │   ├── Scenario-1-xxx.png
  │   └── Scenario-2-xxx.png
  └── traces/                    # Trace 文件 (X files)
      ├── Scenario-1-xxx.zip
      └── Scenario-2-xxx.zip

View Report:
  npx playwright show-report features/active-{feature-id}/evidence/playwright-report

View Trace:
  npx playwright show-trace features/active-{feature-id}/evidence/traces/Scenario-1.zip
```

### Step 6: Save Verification Report

Create verification report at `features/active-{id}/evidence/verification-report.md`:

```markdown
# 验收报告: {feature-id}

**执行时间**: {timestamp}
**执行者**: AI Agent (Playwright MCP)
**总体状态**: ✅ PASSED / ❌ FAILED

---

## 测试概览

| 指标 | 结果 |
|------|------|
| 任务完成 | 5/5 |
| 单元测试 | 12 passed, 0 failed |
| Gherkin 场景 | 5/5 passed |
| 前端测试 | 4 scenarios tested |

---

## Gherkin 场景详情

### 场景 1: 用户登录成功 ✅

**Gherkin:**
```gherkin
Given 用户在登录页面
When 用户输入正确的用户名和密码
Then 页面跳转到首页
```

**执行步骤:**

| 步骤 | 操作 | 截图 | 状态 |
|------|------|------|------|
| Given | 导航到登录页 | ![step1](./screenshots/scenario-1-step-1.png) | ✅ |
| When | 输入凭证 | ![step2](./screenshots/scenario-1-step-2.png) | ✅ |
| Then | 验证跳转 | ![step3](./screenshots/scenario-1-step-3.png) | ✅ |

**Trace 文件**: [trace-scenario-1.zip](./traces/trace-scenario-1.zip)

---

### 场景 2: 密码错误 ❌

**Gherkin:**
```gherkin
Given 用户在登录页面
When 用户输入错误的密码
Then 显示错误提示
```

**失败原因**: 错误提示未显示

**失败截图**: ![failure](./screenshots/scenario-2-failure.png)

**Trace 文件**: [trace-scenario-2.zip](./traces/trace-scenario-2.zip)

---

## 质量检查

- [x] 代码风格符合规范
- [x] 无明显代码异味
- [x] 单元测试覆盖
- [ ] 所有场景通过 (4/5)

---

## 问题列表

| 严重度 | 描述 |
|--------|------|
| High | 场景"密码错误"验证失败 |

---

## 结论

⚠️ 验收未完全通过，请修复上述问题后重新验证。
```

### Step 7: Update Checklist

**IMPORTANT: This step MUST update checklist.md based on verification results.**

Read and update `features/active-{id}/checklist.md`:

**Step 7.1: Mark Completed Items**

Based on verification results, update the following items to `[x]`:

```markdown
### Development
- [x] All tasks completed           ← If task.md shows all tasks done
- [x] Code self-tested              ← After running tests
- [x] Edge cases handled            ← If no edge case failures

### Testing
- [x] Tests passing                 ← If npm test passed
- [x] All Gherkin scenarios validated  ← If all scenarios passed

### Frontend (if applicable)
- [x] Playwright MCP tests executed  ← If Playwright tests ran
- [x] Screenshots captured          ← If evidence/screenshots/ has files
- [x] Traces saved                  ← If evidence/traces/ has files
- [x] Verification report generated ← If evidence/verification-report.md exists

### Code Quality
- [x] Code style follows conventions  ← If lint passed
- [x] No obvious code smells         ← After code review
```

**Step 7.2: Add Verification Record**

Append verification record to checklist.md:

```markdown
---

## Verification Record

**Verified at**: {timestamp}
**Status**: ✅ PASSED / ⚠️ WARNING / ❌ FAILED

### Results Summary
- Tasks: {completed}/{total}
- Unit Tests: {passed} passed, {failed} failed
- Gherkin Scenarios: {passed}/{total} passed

### Evidence
- Report: [verification-report.md](./evidence/verification-report.md)
- Screenshots: {count} files in [screenshots/](./evidence/screenshots/)
- Traces: {count} files in [traces/](./evidence/traces/)

### Issues (if any)
- {issue_1}
- {issue_2}
```

**Step 7.3: Handle Incomplete Items**

If any items remain `[ ]`, add a note explaining why:

```markdown
### Pending Items
- [ ] Unit tests written
  - Reason: No unit tests required for this feature (UI only)
```

### Step 8: Generate Summary Report

```
┌─────────────────────────────────────────────────────────────────┐
│ Verification Report: feat-auth                                   │
├─────────────────────────────────────────────────────────────────┤
│ Feature Type: Frontend                                           │
│                                                                 │
│ Tasks:        5/5 complete ✅                                    │
│ Unit Tests:   12 passed, 0 failed ✅                             │
│                                                                 │
│ Gherkin Scenarios (Code Analysis): 0                             │
│ Gherkin Scenarios (Playwright MCP): 5                            │
│   ✅ 用户登录成功                                                 │
│   ✅ 用户登出                                                     │
│   ✅ 会话保持                                                     │
│   ❌ 密码错误提示                                                 │
│   ✅ 表单验证                                                     │
│                                                                 │
│ Evidence Saved:                                                  │
│   📁 features/active-feat-auth/evidence/                         │
│   ├── verification-report.md                                     │
│   ├── e2e-tests/ (1 file)                                        │
│   ├── screenshots/ (15 files)                                    │
│   └── traces/ (5 files)                                          │
│                                                                 │
│ Quality:      ⚠️ Issues Found                                    │
│                                                                 │
│ Issues:       1 pending                                          │
│   - [HIGH] 场景"密码错误提示"验证失败                              │
├─────────────────────────────────────────────────────────────────┤
│ Status: ⚠️ PASSED WITH WARNINGS                                  │
└─────────────────────────────────────────────────────────────────┘

View full report: features/active-feat-auth/evidence/verification-report.md
View traces: npx playwright show-trace features/active-feat-auth/evidence/traces/

Ready to complete? (y/n)
```

## Evidence Directory Structure

**IMPORTANT**: All evidence must be saved to the feature-specific evidence directory!

```
features/active-{feature-id}/
├── spec.md                              # Feature 规格文档
├── task.md                              # 任务列表
├── checklist.md                         # 检查清单
└── evidence/                            # ⭐ 验收证据目录 (所有证据在这里)
    ├── verification-report.md           # 验收报告 (必须)
    ├── test-results.json                # JSON 测试结果
    ├── playwright-report/               # HTML 报告目录
    │   └── index.html
    ├── e2e-tests/                       # ⭐ E2E 测试脚本 (随 feature 归档)
    │   └── {feature-id}.spec.ts
    ├── screenshots/                     # 截图目录
    │   ├── Scenario-1-Register-success-chromium.png
    │   ├── Scenario-2-Login-success-chromium.png
    │   └── Scenario-3-Error-case-chromium.png
    └── traces/                          # Trace 文件目录
        ├── Scenario-1-Register-success.zip
        ├── Scenario-2-Login-success.zip
        └── Scenario-3-Error-case.zip
```

### Evidence Files Description

| 文件/目录 | 说明 | 必须 |
|----------|------|------|
| `verification-report.md` | 详细的验收报告，包含每个场景的执行结果 | ✅ 是 |
| `test-results.json` | Playwright JSON 格式的测试结果 | ✅ 是 |
| `playwright-report/` | 交互式 HTML 报告，可用 `npx playwright show-report` 查看 | ✅ 是 |
| `e2e-tests/` | E2E 测试脚本，随 feature 归档保存 | ✅ 是 |
| `screenshots/` | 每个测试场景的截图 | ✅ 是 |
| `traces/` | Playwright Trace Viewer 文件，用于详细调试 | ✅ 是 |

### Archive Integration

When feature is completed, the entire evidence directory is preserved:

```
features/archive/done-{feature-id}/
├── spec.md
├── task.md
├── checklist.md
├── evidence/                          # 验收证据完整保留
│   ├── verification-report.md
│   ├── test-results.json
│   ├── playwright-report/
│   ├── e2e-tests/                     # ⭐ E2E 测试脚本归档
│   │   └── {feature-id}.spec.ts
│   ├── screenshots/
│   └── traces/
└── archive-meta.yaml                  # 包含验收结果摘要
```

## Output

### Success
```yaml
status: passed
feature:
  id: feat-auth
  type: frontend

verification:
  tasks:
    total: 5
    completed: 5
  tests:
    run: true
    passed: 12
    failed: 0
  gherkin_scenarios:
    total: 5
    passed: 5
    failed: 0
    method: playwright_mcp
    details:
      - name: "用户登录成功"
        status: passed
        trace: "evidence/traces/trace-scenario-1.zip"
      - name: "密码错误提示"
        status: passed
        trace: "evidence/traces/trace-scenario-2.zip"

evidence:
  report: features/active-feat-auth/evidence/verification-report.md
  screenshots: features/active-feat-auth/evidence/screenshots/
  traces: features/active-feat-auth/evidence/traces/

quality_check: passed
issues: []

message: |
  ✅ Verification passed!

  All tasks complete, tests passing, all Gherkin scenarios satisfied.
  Evidence saved to: features/active-feat-auth/evidence/

  Ready to complete: /complete-feature feat-auth
```

### Warnings
```yaml
status: warning
feature:
  id: feat-auth
  type: frontend

verification:
  tasks:
    total: 5
    completed: 4
    incomplete:
      - "Write unit tests"
  tests:
    run: true
    passed: 10
    failed: 0
  gherkin_scenarios:
    total: 5
    passed: 5
    failed: 0
    method: playwright_mcp

evidence:
  report: features/active-feat-auth/evidence/verification-report.md

issues:
  - severity: medium
    description: "Unit tests not written"

message: |
  ⚠️ Verification passed with warnings

  Incomplete items:
  - Unit tests not written

  Evidence saved to: features/active-feat-auth/evidence/

  Continue to complete? (y/n)
```

### Failure
```yaml
status: failed
feature:
  id: feat-auth
  type: frontend

verification:
  tasks:
    incomplete: 2
  tests:
    failed: 3
  gherkin_scenarios:
    total: 5
    passed: 3
    failed: 2
    method: playwright_mcp
    failures:
      - scenario: "密码错误提示"
        reason: "Error message not displayed"
        screenshot: "evidence/screenshots/scenario-2-failure.png"
      - scenario: "会话过期"
        reason: "Redirect not working"
        screenshot: "evidence/screenshots/scenario-4-failure.png"

evidence:
  report: features/active-feat-auth/evidence/verification-report.md
  failure_screenshots:
    - features/active-feat-auth/evidence/screenshots/scenario-2-failure.png
    - features/active-feat-auth/evidence/screenshots/scenario-4-failure.png

issues:
  - severity: high
    description: "3 unit tests failing"
  - severity: high
    description: "2 Gherkin scenarios failed"
  - severity: medium
    description: "Error handling incomplete"

message: |
  ❌ Verification failed

  Issues:
  - 3 unit tests failing
  - 2 Gherkin scenarios failed:
    * 密码错误提示: Error message not displayed
    * 会话过期: Redirect not working

  View failure screenshots in: features/active-feat-auth/evidence/screenshots/
  View traces for debugging: npx playwright show-trace features/active-feat-auth/evidence/traces/

  Fix these issues before completing.
```

## Error Handling

| Error | Description | Solution |
|-------|-------------|----------|
| NOT_ACTIVE | Feature not in active list | Check ID |
| WORKTREE_NOT_FOUND | Worktree missing | Run /start-feature |
| TEST_FAILURE | Unit tests failing | Fix tests first |
| SCENARIO_FAILED | Gherkin scenario not satisfied | Check evidence, fix implementation |
| PLAYWRIGHT_MCP_UNAVAILABLE | Playwright MCP not configured | Fallback to `npx playwright test` |
| PLAYWRIGHT_NOT_INSTALLED | Playwright not in project | Run `npm install -D @playwright/test` |
| DEV_SERVER_NOT_RUNNING | Frontend dev server not running | Auto-start or manual start |
| TRACE_SAVE_FAILED | Failed to save trace file | Check disk space/permissions |
| E2E_TEST_GENERATION_FAILED | Failed to generate test from Gherkin | Manual test creation required |

## Automatic Test Generation

When using Method B (npx playwright test), automatically generate test files from Gherkin scenarios:

### Gherkin to Playwright Mapping

| Gherkin Step | Playwright Code |
|--------------|-----------------|
| `Given 用户在登录页面` | `await page.goto('/login')` |
| `When 用户输入用户名 "xxx"` | `await page.fill('input#username', 'xxx')` |
| `And 点击登录按钮` | `await page.click('button[type="submit"]')` |
| `Then 页面跳转到首页` | `await page.waitForURL('**/')` |
| `And 显示错误提示 "xxx"` | `await expect(page.locator('.error')).toContainText('xxx')` |
| `And localStorage 存储会话` | `await page.evaluate(() => localStorage.getItem('session'))` |

### Common Selectors

```typescript
// Form inputs
'input#username'           // by id
'input[name="password"]'   // by name
'.login-form input'        // by class descendant

// Buttons
'button[type="submit"]'    // submit button
'.login-button'            // by class
'text=登录'                 // by text

// Messages
'.error-message'           // error display
'.success-message'         // success display
'.welcome-text'            // welcome message
```

## Checklist Items

### Development
- [ ] All tasks completed
- [ ] Code self-tested
- [ ] Edge cases handled

### Code Quality
- [ ] Code style follows conventions
- [ ] No obvious code smells
- [ ] Necessary comments added

### Testing
- [ ] Unit tests written (if needed)
- [ ] Tests passing
- [ ] All Gherkin scenarios validated

### Gherkin Scenarios
- [ ] Happy path scenarios pass
- [ ] Error case scenarios pass
- [ ] Edge case scenarios pass

### Frontend (if applicable)
- [ ] Playwright MCP tests executed
- [ ] Screenshots captured
- [ ] Traces saved
- [ ] Verification report generated

### Documentation
- [ ] spec.md technical solution filled
- [ ] Related docs updated

## Playwright MCP Commands Reference

When executing frontend tests, use these Playwright MCP tools:

| Tool | Description | Example |
|------|-------------|---------|
| `playwright_navigate` | Navigate to URL | Navigate to /login |
| `playwright_click` | Click element | Click button "登录" |
| `playwright_fill` | Fill form field | Fill input "用户名" with "testuser" |
| `playwright_get_text` | Get element text | Get text from ".welcome-message" |
| `playwright_get_url` | Get current URL | Verify URL contains /home |
| `playwright_screenshot` | Take screenshot | Save as evidence/step-1.png |
| `playwright_assert` | Assert condition | Text equals "Welcome" |
| `playwright_wait` | Wait for condition | Wait for element visible |

## Viewing Trace Files

To review trace files after verification:

```bash
# View specific trace
npx playwright show-trace features/active-feat-auth/evidence/traces/trace-scenario-1.zip

# View all traces in directory
npx playwright show-trace features/active-feat-auth/evidence/traces/
```

The Trace Viewer provides:
- Timeline of all actions
- Screenshots at each step
- DOM snapshots
- Network requests
- Console logs

## Complete Verification Workflow

```
┌─────────────────────────────────────────────────────────────────┐
│                    VERIFY-FEATURE WORKFLOW                       │
├─────────────────────────────────────────────────────────────────┤
│                                                                 │
│  Step 1: Check Task Completion                                  │
│    └─► Read task.md, count completed vs total                   │
│                                                                 │
│  Step 2: Run Code Quality Checks                                │
│    └─► npm run build, lint check                                │
│                                                                 │
│  Step 3: Run Unit/Integration Tests                             │
│    └─► npm test (if tests exist)                                │
│                                                                 │
│  Step 4: Detect Feature Type                                    │
│    └─► frontend / backend / fullstack?                          │
│                                                                 │
│  Step 5: Validate Gherkin Scenarios                             │
│    │                                                            │
│    ├─► Frontend? ──┬─► Playwright MCP available?                │
│    │               │       ├─► YES: Method A (MCP tools)        │
│    │               │       └─► NO:  Method B (npx playwright)   │
│    │               │                                            │
│    └─► Backend? ────► Code Analysis only                        │
│                                                                 │
│  Step 6: Collect Evidence                                       │
│    └─► screenshots/, traces/, verification-report.md            │
│                                                                 │
│  Step 7: Update Checklist                                       │
│    └─► Mark completed items, note issues                        │
│                                                                 │
│  Step 8: Generate Summary Report                                │
│    └─► Display results, evidence paths                          │
│                                                                 │
└─────────────────────────────────────────────────────────────────┘
```

## Quick Reference

```bash
# Check if Playwright is installed
npx playwright --version

# Run tests with full evidence collection
npx playwright test --trace on --screenshot on --reporter=html,json

# View HTML report
npx playwright show-report

# View trace file
npx playwright show-trace trace.zip
```
