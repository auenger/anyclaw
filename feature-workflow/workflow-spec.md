# Feature Workflow 详细规范

## 1. 数据结构

### 1.1 config.yaml

```yaml
project:
  name: string                        # 项目名称
  main_branch: string                 # 主分支名称， 默认 main
  repo_path: string                   # Git仓库子目录（可选,用于monorepo)

parallelism:
  max_concurrent: number              # 最大并行开发数，默认 2

workflow:
  auto_start: boolean                 # 完成后自动启动下一个
  require_checklist: boolean          # 完成前需要完成 checklist

  # 需求切分配置
  splitting:
    enabled: true                     # 启用需求切分功能
    threshold: 3                      # 3个以上用户价值点触发切分
    auto_dependencies: true           # 自动设置子需求依赖关系
    force_split: false                # 是否强制切分（默认false）
    suggest_split: true               # 是否建议切分（默认true）

  # 验收配置
  verification:
    enabled: true                     # 启用验收功能
    require_pass: false               # 是否要求验收通过才能完成
    playwright_mcp: true              # 启用 Playwright MCP 前端测试
    save_evidence: true               # 保存验收证据（截图、trace）
    dev_server:
      auto_start: true                # 自动启动开发服务器
      port: 3000                      # 开发服务器端口
      command: "npm run dev"          # 启动命令

completion:
  archive:
    create_tag: boolean               # 创建归档 tag
    tag_format: string                # tag 格式， 默认 "{id}-{date}"
    tag_date_format: string           # 日期格式, 默认 "%Y%m%d"
  cleanup:
    delete_worktree: boolean          # 删除 worktree
    delete_branch: boolean            # 删除分支（已通过 tag 归档）
  record:
    update_spec: boolean              # 更新 spec.md 添加合并记录
    update_archive_log: boolean       # 更新 archive-log.yaml
    preserve_evidence: boolean        # 归档时保留验收证据

naming:
  feature_prefix: string              # 需求 ID 前缀， 默认 feat
  branch_prefix: string               # 分支前缀， 默认 feature
  worktree_prefix: string             # worktree 前缀， 默认项目名

paths:
  features_dir: string                # 需求目录
  archive_dir: string                 # 归档目录
  worktree_base: string               # worktree 父目录
  repo_path: string                   # Git 仓库相对路径（可选)
  evidence_dir: string                # 验收证据目录，默认 evidence

git:
  auto_push: boolean                  # 是否自动推送
  merge_strategy: string              # 合并策略, 默认 "--no-ff"
  push_tags: boolean                  # 是否自动推送 tag
```

### 1.2 queue.yaml
meta:
  last_updated: datetime              # 最后更新时间
  version: number                     # 版本号

active:                               # 正在开发
  - id: string                        # 需求 ID (feat-xxx)
    name: string                      # 需求名称
    priority: number                  # 优先级 (0-100)
    size: string                      # 规模: S/M/L
    parent: string|null            # 父需求ID（如果是子需求）
    children: string[]               # 子需求ID列表（如果有）
    dependencies: string[]             # 依赖的其他需求 ID
    branch: string                    # 分支名
    worktree: string                  # worktree 路径
    started: datetime                 # 开始时间

pending:                              # 等待中
  - id: string
    name: string
    priority: number
    size: string                      # 规模: S/M/L
    parent: string|null            # 父需求id
    children: string[]               # 子需求id列表
    dependencies: string[]             # 依赖的其他需求
    created: datetime                 # 创建时间

blocked:                              # 阻塞中
  - id: string
    name: string
    reason: string                    # 阻塞原因
    size: string                      # 规模: S/M/L
    parent: string|null
 children: string[]
    dependencies: string[]
    created: datetime
```

### 1.3 archive-log.yaml
位置: `features/archive/archive-log.yaml`
```yaml
meta:
  last_updated: datetime
  total_archived: number

archived:
  - id: string
    name: string
    completed: datetime               # 完成时间

    # Git 归档信息
    tag: string                       # 归档 tag
    merge_commit: string              # 合并 commit hash
    merged_to: string                 # 合并到的分支

    # 父子关系（如果是拆分的需求）
    parent: string|null
    children: string[]

    # 清理信息
    branch_deleted: boolean
    branch_name: string               # 原分支名
    worktree_deleted: boolean
    worktree_path: string             # 原 worktree 路径

    # 需求目录
    docs_path: string                 # 归档目录名

    # 验收信息（如果有）
    verification:
      status: passed | warning | failed
      feature_type: frontend | backend | fullstack
      method: code_analysis | playwright_mcp
      scenarios:
        total: number
        passed: number
        failed: number
      evidence_path: string           # 相对于 docs_path
      executed_at: datetime

    # 统计
    stats:
      started: datetime
      duration: string                # 开发时长
      commits: number
      files_changed: number
      additions: number
      deletions: number

    # Checklist 跳过记录（如果有）
    checklist_skipped:
      items: string[]
      reason: string
```

---

## 2. 项目上下文规范

### 2.1 项目上下文文件

**位置**: `{project-root}/project-context.md`

**作用**: 为 AI 提供项目关键信息，确保实现一致性

### 2.2 文件结构

```markdown
---
last_updated: {date}
version: {number}
features_completed: {count}
---

# Project Context: {project_name}

## Technology Stack

| Category | Technology | Version | Notes |
|----------|-----------|---------|-------|
| Frontend | React | 18.2 | Vite + TypeScript |
| Backend | Node.js | 20.x | Express |
| Database | PostgreSQL | 15 | Prisma ORM |

## Critical Rules

### Must Follow
- 规则1: {critical_rule}

### Must Avoid
- 反模式1: {anti_pattern}

## Directory Structure

{project_directory_tree}

## Recent Changes

| Date | Feature | Impact |
|------|---------|--------|
| {date} | {feature_id} | {impact} |

## Update Log

- {date}: {what_was_updated}
```

### 2.3 上下文加载优先级

```
┌─────────────────────────────────────────────────────────────────┐
│                    上下文加载流程                                │
├─────────────────────────────────────────────────────────────────┤
│                                                                 │
│  1. project-context.md                                          │
│     ├── 存在 → 直接加载 ✅                                       │
│     └── 不存在 ↓                                                │
│                                                                 │
│  2. CLAUDE.md                                                    │
│     ├── 存在 → 加载并提示可转换                                   │
│     └── 不存在 ↓                                                │
│                                                                 │
│  3. Quick Explore                                                │
│     ├── 扫描项目结构、技术栈、代码模式                            │
│     └── 生成 project-context.md                                 │
│                                                                 │
└─────────────────────────────────────────────────────────────────┘
```

### 2.4 上下文更新策略

**更新时机**: complete-feature 时

**更新判断**:

```yaml
update_triggers:
  - 新增依赖或版本升级
  - 新的代码模式/约定
  - 新的目录结构
  - 新的测试模式
  - 新发现的 Anti-pattern
```

**增量更新原则**:
- 只更新受影响的部分
- 保持文件精简
- 记录更新日志
- 递增版本号

**跳过更新条件**:
- Feature 仅修改现有代码
- Bug fix 或小增强
- 未引入新模式

### 2.5 Quick Explore 扫描项

当需要生成 project-context.md 时，扫描以下内容：

| 扫描项 | 文件/目录 | 提取信息 |
|--------|----------|---------|
| 依赖 | package.json, requirements.txt | 技术栈、版本 |
| 配置 | tsconfig.json, vite.config.* | 构建配置 |
| 目录 | src/, app/, lib/ | 代码组织 |
| 代码模式 | 随机抽样 3-5 个文件 | 命名、import 风格 |
| 测试 | tests/, __tests__/ | 测试模式 |

---

## 3. 需求切分规范

### 3.1 切分原则

需求切分遵循以下原则（参考 BMAD）：

1. **用户价值优先**: 按用户能完成什么来切分，而非技术层
2. **增量交付**: 每个子需求独立交付价值
3. **无循环依赖**: 子需求2不能依赖子需求3
4. **按需创建**: 数据库/实体按需创建

5. **上下文保护**: 每个子需求保持在 AI 上下文限制内

### 2.2 切分触发条件

当满足以下任一条件时，触发切分建议:

- 用户价值点 ≥ 3 个
- 用户明确请求切分
- AI 判断需求过于复杂

### 2.3 切分流程

```
/new-feature <需求描述>
        ↓
Step 1: 收集需求信息
        ↓
Step 2: AI 分析用户价值点
        ↓
Step 3: 评估需求规模
        ↓
    ┌─────────────────┬─────────────────┐
    │                 │                 │
Small (1个)     Medium (2个)       Large (3+个)
    │                 │                 │
    ▼                 ▼                 ▼
直接创建      可选切分          建议切分
```

### 2.4 规模评估标准

| 规模 | 用户价值点 | 特征 |
|------|----------|------|
| S (Small) | 1 | 单一功能点，快速完成 |
| M (Medium) | 2 | 几个相关功能点 |
| L (Large) | 3+ | 多个独立功能模块，建议切分 |
### 2.5 正确切分示例
**输入**: "用户认证系统，支持注册、登录、权限管理"
**分析**: 识别到 3 个用户价值点:
1. 用户注册 - 创建新账户
2. 用户登录 - 访问系统
3. 权限管理 - 控制访问权限
**切分结果**:
```
feat-auth-register  → 用户能注册 (独立可交付)
feat-auth-login     → 用户能登录 (依赖 register)
feat-auth-permission → 用户能管理权限 (依赖 login)
```
**错误切分示例** (按技术层，非用户价值):
```
feat-auth-db    → 数据库设计 (无用户价值)❌
feat-auth-api   → API 开发 (无用户价值)❌
feat-auth-ui    → 前端界面 (无用户价值)❌
```
---

## 3. 验收规范

### 3.1 验收场景格式 (Gherkin)

所有 Feature 的 spec.md 必须包含 Gherkin 格式的验收场景：

```markdown
## 验收标准 (Acceptance Criteria)

### 用户故事
作为 [角色]，我希望 [目标]，以便 [价值]

### Gherkin 验收场景

#### 场景 1: [场景名称]
```gherkin
Given [前置条件]
When [用户操作]
Then [预期结果]
```

#### 场景 2: [场景名称] (异常情况)
```gherkin
Given [前置条件]
When [异常操作]
Then [错误处理]
```
```

### 3.2 Feature 类型检测

系统自动检测 Feature 类型：

| 类型 | 检测条件 |
|------|---------|
| **frontend** | 存在组件文件 (*.tsx, *.vue, *.jsx) 或 spec.md 包含 UI/交互关键词 |
| **backend** | 仅包含 API、数据库、服务端代码 |
| **fullstack** | 同时包含前后端代码 |

### 3.3 验收方法

根据 Feature 类型选择验收方法：

| 类型 | 验收方法 | 说明 |
|------|---------|------|
| **backend** | 代码分析 | AI 分析代码逻辑，验证 Gherkin 场景 |
| **frontend** | Playwright MCP | AI 通过 Playwright MCP 执行浏览器测试 |
| **fullstack** | 混合 | 后端用代码分析，前端用 Playwright MCP |

### 3.4 Playwright MCP 验收流程

```
┌─────────────────────────────────────────────────────────────────┐
│                    Playwright MCP 验收流程                        │
├─────────────────────────────────────────────────────────────────┤
│                                                                 │
│  1. 解析 Gherkin 场景                                           │
│     ↓                                                           │
│  2. 启动开发服务器 (如需要)                                       │
│     ↓                                                           │
│  3. For each 场景:                                              │
│     ├── Playwright MCP 执行 Given-When-Then                     │
│     ├── 每步截图保存到 evidence/screenshots/                     │
│     └── 记录执行结果                                             │
│     ↓                                                           │
│  4. 保存 Trace 文件到 evidence/traces/                          │
│     ↓                                                           │
│  5. 生成 verification-report.md                                 │
│                                                                 │
└─────────────────────────────────────────────────────────────────┘
```

### 3.5 验收证据目录结构

```
features/active-{id}/
├── spec.md
├── task.md
├── checklist.md
└── evidence/                          # 验收证据目录
    ├── verification-report.md          # 验收报告
    ├── screenshots/                    # 截图目录
    │   ├── scenario-1-step-1.png
    │   ├── scenario-1-step-2.png
    │   ├── scenario-2-step-1.png
    │   └── scenario-2-failure.png      # 失败截图
    └── traces/                         # Trace 文件目录
        ├── trace-scenario-1.zip
        ├── trace-scenario-2.zip
        └── trace-all.zip               # 完整 trace
```

### 3.6 验收报告格式

`evidence/verification-report.md`:

```markdown
# 验收报告: {feature-id}

**执行时间**: {timestamp}
**执行者**: AI Agent (Playwright MCP)
**Feature 类型**: frontend
**总体状态**: ✅ PASSED / ❌ FAILED

---

## 测试概览

| 指标 | 结果 |
|------|------|
| 任务完成 | 5/5 |
| 单元测试 | 12 passed, 0 failed |
| Gherkin 场景 | 5/5 passed |
| 前端测试 | 5 scenarios tested |

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

## 质量检查

- [x] 代码风格符合规范
- [x] 无明显代码异味
- [x] 单元测试覆盖
- [x] 所有场景通过

---

## 结论

✅ 验收通过，可以完成 Feature。
```

### 3.7 验收状态定义

| 状态 | 条件 |
|------|------|
| **passed** | 所有场景通过，无警告 |
| **warning** | 场景通过，但有 checklist 未完成 |
| **failed** | 有场景失败 |

### 3.8 Playwright MCP 工具参考

| 工具 | 描述 | 示例 |
|------|------|------|
| `playwright_navigate` | 导航到 URL | Navigate to /login |
| `playwright_click` | 点击元素 | Click button "登录" |
| `playwright_fill` | 填充表单 | Fill input "用户名" with "test" |
| `playwright_get_text` | 获取文本 | Get text from ".welcome" |
| `playwright_get_url` | 获取当前 URL | Verify URL contains /home |
| `playwright_screenshot` | 截图 | Save as evidence/step-1.png |
| `playwright_assert` | 断言 | Text equals "Welcome" |
| `playwright_wait` | 等待条件 | Wait for element visible |

---

## 4. 命令详细规范

### 4.1 /new-feature

**输入**: 需求描述（自然语言）

**流程**:
1. 对话确认需求细节
   - 需求名称
   - 需求描述
   - 优先级 (1-100)
   - 依赖关系
2. **AI 分析需求** (新增)
   - 识别独立用户价值点
   - 评估需求规模 (S/M/L)
   - **生成 Gherkin 验收场景** (新增)
3. **规模判断** (新增)
   - 如果 Large: 建议切分
   - 如果用户同意: 执行切分
   - 如果用户拒绝: 创建单个需求（警告）
4. 生成需求 ID
   - 格式: `{prefix}-{slug}`
   - 切分时: `{prefix}-{base}-{suffix}`
5. 检查 ID 冲突
6. 创建需求目录和文件
   - 切分时: 批量创建多个子需求
   - 设置父子关系和依赖关系
7. 更新 queue.yaml
8. 检查自动启动条件

**输出**: 创建成功提示，包含目录路径
- 切分时: 显示所有子需求及其依赖关系

---

### 4.2 /start-feature

**输入**: 需求 ID

**前置条件**:
- 需求存在于 pending 列表
- active.count < max_concurrent
- **依赖检查** (新增)
  - 检查 dependencies 字段
  - 验证所有依赖是否已完成
  - **父需求检查** (新增)
  - 如果有 parent: 检查父需求状态
  - **子需求检查** (新增)
  - 如果有 children: 检查子需求状态

**流程**:
1. 检查并行限制
2. 检查依赖和父子关系
3. 重命名目录
4. 创建分支
5. 创建 worktree
6. 更新 queue.yaml

**输出**: worktree 路径，提示切换目录
- 显示父/子需求关系（如有）

---

### 4.3 /verify-feature

**输入**: 需求 ID

**前置条件**:
- 需求存在于 active 列表

**流程**:
1. 检查任务完成情况
2. 运行代码质量检查
3. 运行单元/集成测试
4. **检测 Feature 类型**
   - frontend / backend / fullstack
5. **验证 Gherkin 场景**
   - Backend: 代码分析
   - Frontend: Playwright MCP 执行
6. **保存验收证据** (如果是前端)
   - 截图
   - Trace 文件
   - 验收报告
7. 更新 checklist.md
8. 生成验收摘要

**输出**: 验收报告
- 通过: 显示证据路径，提示可以完成
- 警告: 显示未完成项，询问是否继续
- 失败: 显示失败原因和截图

---

### 4.4 /complete-feature

**输入**: 需求 ID

**前置条件**:
- 需求存在于 active 列表
- (可选) 验收通过或用户确认跳过

**流程**:
1. 获取 Feature 信息
2. 检查 Checklist
3. 提交代码
4. 合并到 main
5. 创建归档 tag
6. **归档 Feature 目录** (包含 evidence/)
7. **更新 spec.md** (添加验收证据链接)
8. 清理 worktree 和分支
9. 更新 queue.yaml
10. 自动启动下一个

**输出**: 完成报告
- 包含验收状态和证据路径

---

(后续命令规范保持不变，略)
