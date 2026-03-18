# Feature Workflow 文档

> 基于 Git Worktree 的 AI 辅助开发工作流

版本: 1.0.0
更新日期: 2026-03-03

---

## 目录

1. [概述](#概述)
2. [Worktree + Feature 的核心优势](#worktree--feature-的核心优势)
3. [工作流程](#工作流程)
4. [冲突处理机制](#冲突处理机制)
5. [安装与配置](#安装与配置)
6. [命令参考](#命令参考)
7. [最佳实践](#最佳实践)

---

## 概述

Feature Workflow 是一套基于 Git Worktree 机制的需求驱动开发工作流，专为 AI 辅助编程场景设计。它将每个需求隔离在独立的 worktree 中开发，通过规范化的流程管理从需求创建到归档的完整生命周期。

### 核心理念

```
一个 Feature = 一个 Worktree = 一个独立开发环境
```

### 技术栈

- **Git Worktree**: 分支隔离
- **YAML 配置**: 工作流配置
- **Markdown 文档**: 需求/任务/检查清单
- **Playwright**: E2E 测试验证
- **Git Tag**: 归档追溯

---

## Worktree + Feature 的核心优势

### 什么是 Git Worktree？

Git Worktree 允许你在同一个仓库下同时检出多个分支到不同的目录：

```
OA_Tool/                    # 主仓库 (main 分支)
├── src/
├── package.json
└── feature-workflow/

OA_Tool-feat-auth/          # Worktree 1 (feature/auth 分支)
├── src/
└── package.json

OA_Tool-feat-dashboard/     # Worktree 2 (feature/dashboard 分支)
├── src/
└── package.json
```

### 优势一：开发环境完全隔离

**传统方式的问题：**
```
# 切换分支会丢失当前工作进度
git checkout feature/auth
# 代码被覆盖，需要 stash 或 commit
```

**Worktree 方式：**
```
# 每个需求独立目录，互不干扰
cd OA_Tool-feat-auth      # 开发认证功能
cd OA_Tool-feat-dashboard  # 开发仪表盘功能
# 无需切换分支，两个功能可同时开发
```

**收益：**
- 不会因为切换分支丢失工作进度
- 每个 feature 可以独立运行/测试
- 支持真正的并行开发

### 优势二：AI 上下文隔离

**问题场景：**
当 AI 同时处理多个需求时，代码变更会相互干扰，导致：
- 代码覆盖
- 逻辑冲突
- 难以追踪每个需求的变更

**Worktree 解决方案：**
```
Feature A 的 AI Agent → OA_Tool-feat-auth/
Feature B 的 AI Agent → OA_Tool-feat-dashboard/

# 每个 AI Agent 只在自己的目录工作
# 上下文完全隔离，不会互相干扰
```

**收益：**
- AI 可以并行处理多个需求
- 每个需求的代码变更清晰可追溯
- 减少人为错误

### 优势三：独立测试验证

```
OA_Tool-feat-auth/
├── src/
└── e2e/
    └── auth.spec.ts      # 只测试认证功能

OA_Tool-feat-dashboard/
├── src/
└── e2e/
    └── dashboard.spec.ts # 只测试仪表盘功能
```

**收益：**
- 测试环境独立
- 证据收集互不干扰
- Playwright traces 隔离存储

### 优势四：安全的合并策略

```
传统方式:
main ← feature (直接 merge，冲突在 main 分支解决)

Worktree + Rebase 方式:
feature → rebase onto main → 解决冲突 → fast-forward merge
         (冲突在 feature 分支解决)
```

**收益：**
- main 分支始终保持干净
- 冲突解决在 feature 分支内完成
- 解决后可重新验证

### 优势五：完整的追溯能力

每个完成的 feature 都会：
1. 创建 Git Tag（如 `feat-auth-20260303`）
2. 保留完整的验证证据
3. 归档所有文档

```
features/archive/done-feat-auth-20260303/
├── spec.md                    # 需求规格
├── task.md                    # 任务列表
├── checklist.md               # 完成检查
├── evidence/                  # 验证证据
│   ├── verification-report.md
│   ├── screenshots/
│   └── traces/
└── archive-meta.yaml          # 元数据
```

**收益：**
- 任何时间点都可以回溯
- Tag 可恢复完整代码
- 证据可重新查看

### 对比总结

| 特性 | 传统分支切换 | Worktree 方式 |
|------|-------------|---------------|
| 并行开发 | ❌ 不支持 | ✅ 支持 |
| 环境隔离 | ❌ 共享目录 | ✅ 独立目录 |
| AI 上下文 | ❌ 易混淆 | ✅ 完全隔离 |
| 测试隔离 | ❌ 相互影响 | ✅ 独立运行 |
| 冲突解决 | ⚠️ main 分支 | ✅ feature 分支 |
| 进度保存 | ⚠️ 需要 stash | ✅ 天然支持 |
| 追溯能力 | ⚠️ 需要额外配置 | ✅ 自动归档 |

---

## 工作流程

### 完整生命周期

```
┌─────────────────────────────────────────────────────────────────────┐
│                     Feature Workflow 生命周期                        │
├─────────────────────────────────────────────────────────────────────┤
│                                                                     │
│  /new-feature                                                       │
│  ────────────────                                                   │
│  输入: 需求描述                                                      │
│  输出: features/pending-feat-xxx/                                   │
│        ├── spec.md        (需求规格 + Gherkin 场景)                  │
│        ├── task.md        (任务分解)                                │
│        └── checklist.md   (完成检查清单)                            │
│                                                                     │
│         │                                                           │
│         ▼                                                           │
│                                                                     │
│  /start-feature feat-xxx                                            │
│  ─────────────────────────                                          │
│  动作:                                                              │
│    1. 拉取最新 main: git pull origin main                           │
│    2. 创建分支: git checkout -b feature/xxx                         │
│    3. 创建 worktree: git worktree add ../OA_Tool-feat-xxx           │
│    4. 移动目录: pending → active                                    │
│  输出:                                                              │
│    - 分支: feature/xxx                                              │
│    - Worktree: ../OA_Tool-feat-xxx/                                 │
│                                                                     │
│         │                                                           │
│         ▼                                                           │
│                                                                     │
│  /implement-feature feat-xxx                                        │
│  ──────────────────────────                                         │
│  动作: 在 worktree 中实现代码                                        │
│  输出: 更新 task.md 中的任务状态                                     │
│                                                                     │
│         │                                                           │
│         ▼                                                           │
│                                                                     │
│  /verify-feature feat-xxx                                           │
│  ─────────────────────────                                          │
│  动作:                                                              │
│    1. 检查任务完成情况                                               │
│    2. 运行单元测试                                                   │
│    3. 运行 E2E 测试 (Playwright)                                    │
│    4. 验证 Gherkin 场景                                              │
│    5. 收集证据 (screenshots, traces)                                │
│    6. 更新 checklist.md                                             │
│  输出: features/active-feat-xxx/evidence/                           │
│                                                                     │
│         │                                                           │
│         ▼                                                           │
│                                                                     │
│  /complete-feature feat-xxx                                         │
│  ──────────────────────────                                         │
│  动作:                                                              │
│    1. Commit 代码                                                    │
│    2. Rebase 到最新 main                                            │
│    3. [如有冲突] 解决冲突 → 重新验证                                  │
│    4. Fast-forward merge                                            │
│    5. 创建 Archive Tag                                              │
│    6. 清理 worktree 和分支                                           │
│    7. 归档文档                                                       │
│  输出: features/archive/done-feat-xxx/                              │
│        Tag: feat-xxx-YYYYMMDD                                       │
│                                                                     │
└─────────────────────────────────────────────────────────────────────┘
```

### 并行开发示意

```
时间线 ──────────────────────────────────────────────────────────────►

T1: /start-feature feat-auth
    └─ main (A) → feature/auth → worktree: OA_Tool-feat-auth/

T2: /start-feature feat-dashboard  (并行)
    └─ main (A) → feature/dashboard → worktree: OA_Tool-feat-dashboard/

T3-T5: 两个 feature 同时开发，互不干扰
    OA_Tool-feat-auth/     ← 开发认证功能
    OA_Tool-feat-dashboard/ ← 开发仪表盘功能

T6: /complete-feature feat-auth
    └─ rebase → merge → main (B)
    └─ cleanup worktree

T7: /complete-feature feat-dashboard
    └─ rebase onto main (B) → 可能冲突，在 worktree 中解决
    └─ merge → main (C)
    └─ cleanup worktree
```

---

## 冲突处理机制

### 冲突产生的原因

在 Worktree 模式下，冲突主要发生在以下场景：

```
时间 ──────────────────────────────────────────────────────────────►

T1: 创建 feat-auth worktree    (基于 main commit A)
T2: 创建 feat-dashboard worktree (基于 main commit A)

T3: feat-auth 开发中... 修改 auth.ts
T4: feat-dashboard 开发中... 也修改 auth.ts

T5: feat-auth 完成，合并到 main → main 变成 commit B
    (auth.ts 已被 feat-auth 修改)

T6: feat-dashboard 完成，尝试合并
    ↓
    feat-dashboard 基于 A 开发
    main 现在是 B
    auth.ts 在两个分支都被修改
    ↓
    冲突！
```

### 冲突检测：Rebase 策略

我们使用 **Rebase + Fast-forward Merge** 策略，而非直接 Merge：

```
【传统 Merge 方式】

main ──── merge feature ──── 可能冲突在这里
              ↑
         冲突时 main 分支变脏


【Rebase 方式】

main ──── (干净) ──── fast-forward merge (无冲突)
              ↑
feature → rebase onto main
              ↑
         冲突在这里解决，在 feature 分支内
```

### 完整的冲突处理流程

```
┌─────────────────────────────────────────────────────────────────────┐
│                    冲突处理流程                                       │
├─────────────────────────────────────────────────────────────────────┤
│                                                                     │
│  Step 1: 执行 Rebase                                                │
│  ────────────────────                                               │
│  git checkout feature/dashboard                                     │
│  git rebase main                                                    │
│                                                                     │
│         │                                                           │
│         ▼                                                           │
│                                                                     │
│  Step 2: 检测冲突                                                   │
│  ────────────────────                                               │
│  如果有冲突:                                                         │
│                                                                     │
│  ┌─────────────────────────────────────────────────────────────┐   │
│  │ ❌ Rebase 冲突检测到                                          │   │
│  │                                                               │   │
│  │ 冲突文件:                                                      │   │
│  │   - src/auth/auth.ts                                          │   │
│  │   - src/utils/helpers.ts                                      │   │
│  │                                                               │   │
│  │ 解决步骤:                                                      │   │
│  │   1. cd ../OA_Tool-feat-dashboard   ← 在 worktree 中解决       │   │
│  │   2. 打开冲突文件，解决 <<<< 标记                              │   │
│  │   3. git add .                                                │   │
│  │   4. git rebase --continue                                    │   │
│  │   5. /verify-feature feat-dashboard  ← 重新验证               │   │
│  │   6. /complete-feature feat-dashboard --resume               │   │
│  │                                                               │   │
│  │ 💡 冲突在当前 feature 内解决，不影响其他 feature               │   │
│  └─────────────────────────────────────────────────────────────┘   │
│                                                                     │
│         │                                                           │
│         ▼                                                           │
│                                                                     │
│  Step 3: 在 Worktree 中解决冲突                                     │
│  ────────────────────────────────                                   │
│  cd ../OA_Tool-feat-dashboard                                       │
│                                                                     │
│  # 打开冲突文件，手动解决 <<<< ==== >>>> 标记                        │
│  vim src/auth/auth.ts                                               │
│                                                                     │
│  # 标记为已解决                                                      │
│  git add .                                                          │
│                                                                     │
│  # 继续 rebase                                                       │
│  git rebase --continue                                              │
│                                                                     │
│         │                                                           │
│         ▼                                                           │
│                                                                     │
│  Step 4: 重新验证 (关键步骤！)                                      │
│  ──────────────────────────────                                     │
│  # 冲突解决可能影响功能，必须重新验证                                 │
│  /verify-feature feat-dashboard                                     │
│                                                                     │
│  # 验证通过后继续完成                                                │
│  /complete-feature feat-dashboard --resume                          │
│                                                                     │
│         │                                                           │
│         ▼                                                           │
│                                                                     │
│  Step 5: Fast-forward Merge                                         │
│  ──────────────────────────                                         │
│  git checkout main                                                  │
│  git merge feature/dashboard   # Fast-forward，无冲突               │
│                                                                     │
│         │                                                           │
│         ▼                                                           │
│                                                                     │
│  Step 6: 记录冲突信息                                               │
│  ──────────────────────                                             │
│  在 archive-log.yaml 中记录:                                        │
│                                                                     │
│  conflicts:                                                         │
│    had_conflict: true                                               │
│    conflict_files:                                                  │
│      - src/auth/auth.ts                                             │
│      - src/utils/helpers.ts                                         │
│    resolved_at: 2026-03-03T15:30:00Z                                │
│    re_verified: true                                                │
│                                                                     │
└─────────────────────────────────────────────────────────────────────┘
```

### 冲突处理的核心原则

```
┌─────────────────────────────────────────────────────────────────────┐
│                      冲突处理三原则                                   │
├─────────────────────────────────────────────────────────────────────┤
│                                                                     │
│  1️⃣ 隔离原则                                                        │
│  ─────────────                                                      │
│  冲突在 feature 分支内解决，不影响 main 和其他 feature               │
│                                                                     │
│  2️⃣ 验证原则                                                        │
│  ─────────────                                                      │
│  冲突解决后必须重新验证，确保功能正确                                 │
│                                                                     │
│  3️⃣ 追溯原则                                                        │
│  ─────────────                                                      │
│  所有冲突信息记录在案，便于回溯分析                                   │
│                                                                     │
└─────────────────────────────────────────────────────────────────────┘
```

### 冲突预防策略

虽然我们有完善的冲突处理机制，但预防胜于治疗：

```
┌─────────────────────────────────────────────────────────────────────┐
│                      冲突预防策略                                     │
├─────────────────────────────────────────────────────────────────────┤
│                                                                     │
│  策略 1: 合并前 Pull                                                │
│  ────────────────────                                               │
│  在 start-feature 和 complete-feature 时都先 pull 最新 main         │
│                                                                     │
│  git pull origin main  # 获取最新代码                               │
│                                                                     │
│  策略 2: 串行开发相同模块                                            │
│  ────────────────────────────                                       │
│  如果多个 feature 需要修改同一文件，设置依赖关系串行执行               │
│                                                                     │
│  /new-feature feat-auth-login --depends-on=feat-auth-register       │
│                                                                     │
│  策略 3: 需求拆分时考虑文件边界                                      │
│  ────────────────────────────────                                   │
│  在 new-feature 阶段分析预估修改的文件，避免重叠                      │
│                                                                     │
│  spec.md:                                                           │
│    affected_files:                                                  │
│      - src/auth/                                                    │
│      - src/models/user.ts                                           │
│                                                                     │
└─────────────────────────────────────────────────────────────────────┘
```

### 冲突处理 vs 传统方式对比

| 方面 | 传统 Merge | Rebase + Worktree |
|------|-----------|-------------------|
| 冲突位置 | main 分支 | feature 分支 |
| 解决环境 | 主仓库 | 独立 worktree |
| 影响范围 | 可能影响其他开发 | 完全隔离 |
| 验证时机 | 可选 | 强制重新验证 |
| 历史记录 | 有 merge commit | 线性历史 |
| 回滚难度 | 较难 | 容易 (可 abort) |
| 追溯能力 | 无记录 | 自动记录冲突信息 |

---

## 安装与配置

### 快速安装

```bash
# 解压
tar -xzf feature-workflow-v1.0.0.tar.gz

# 安装
cd feature-workflow
./dist/install.sh /path/to/your/project
```

### 配置说明

编辑 `feature-workflow/config.yaml`:

```yaml
# 项目信息
project:
  name: Your-Project
  main_branch: main          # 主分支名
  repo_path: .               # 仓库路径 (monorepo 用)
  tech_stack: react-vite     # 技术栈

# Git 设置
git:
  remote: origin             # 远程仓库名
  auto_push: false           # 自动推送 main
  merge_strategy: "--no-ff"  # 合并策略
  push_tags: true            # 推送 tag

# 并行控制
parallelism:
  max_concurrent: 2          # 最大并行 feature 数

# 命名规则
naming:
  feature_prefix: feat       # feat-xxx
  branch_prefix: feature     # feature/xxx
  worktree_prefix: Project   # ../Project-feat-xxx
```

---

## 命令参考

### /new-feature

创建新需求

```
/new-feature <需求描述>

示例:
/new-feature 用户登录 - 实现用户名密码登录、OAuth 登录
```

### /start-feature

开始开发需求

```
/start-feature <feature-id>

示例:
/start-feature feat-user-login
```

### /implement-feature

实现需求代码

```
/implement-feature <feature-id> [--task=<index>]

示例:
/implement-feature feat-user-login
/implement-feature feat-user-login --task=2
```

### /verify-feature

验证需求完成

```
/verify-feature <feature-id>

示例:
/verify-feature feat-user-login
```

### /complete-feature

完成并归档需求

```
/complete-feature <feature-id> [options]

选项:
  --message=<msg>     自定义提交信息
  --skip-checklist    跳过检查清单验证
  --no-merge          只提交，不合并
  --keep-branch       保留分支
  --resume            冲突解决后继续

示例:
/complete-feature feat-user-login
/complete-feature feat-user-login --resume
```

### /list-features

列出所有需求

```
/list-features
```

---

## 最佳实践

### 1. 需求粒度控制

```
✅ 好的需求粒度:
- feat-user-login      (用户登录)
- feat-user-logout     (用户登出)
- feat-password-reset  (密码重置)

❌ 过大的需求:
- feat-user-auth       (包含登录、登出、注册、密码重置...)

建议: 3个以上用户价值点时自动拆分
```

### 2. 并行开发控制

```
# 串行开发 (避免冲突)
feat-auth-register → feat-auth-login → feat-auth-logout

# 并行开发 (独立模块)
feat-auth-login      ┐
feat-dashboard       ├─ 同时开发
feat-settings        ┘
```

### 3. 验证先行

```
# 正确流程
/verify-feature feat-xxx    # 先验证
/complete-feature feat-xxx  # 后完成

# 错误流程
/complete-feature feat-xxx  # 直接完成，跳过验证
```

### 4. 冲突处理规范

```
1. 发现冲突 → 在 worktree 中解决
2. 解决完成 → git rebase --continue
3. 必须 → /verify-feature 重新验证
4. 验证通过 → /complete-feature --resume
5. 记录 → 冲突信息自动记录到 archive-log.yaml
```

### 5. 归档追溯

```bash
# 查看历史归档
cat features/archive/archive-log.yaml

# 从 tag 恢复代码
git checkout -b feature/auth-restored feat-auth-20260303

# 查看验证证据
npx playwright show-trace features/archive/done-feat-auth/evidence/traces/
```

---

## 附录

### 目录结构总览

```
project/
├── .claude/commands/feature-workflow/
│   ├── skills/
│   │   ├── new-feature.md
│   │   ├── start-feature.md
│   │   ├── implement-feature.md
│   │   ├── verify-feature.md
│   │   ├── complete-feature.md
│   │   ├── list-features.md
│   │   ├── block-feature.md
│   │   ├── unblock-feature.md
│   │   ├── cleanup-features.md
│   │   └── feature-config.md
│   ├── workflows/
│   │   ├── feature-lifecycle.md
│   │   └── auto-schedule.md
│   └── agents/
│       ├── feature-manager.md
│       └── dev-agent.md
│
├── feature-workflow/
│   ├── config.yaml
│   ├── queue.yaml
│   ├── templates/
│   │   ├── spec.md
│   │   ├── task.md
│   │   ├── checklist.md
│   │   └── project-context.md
│   └── features/
│       ├── active-feat-xxx/
│       │   ├── spec.md
│       │   ├── task.md
│       │   ├── checklist.md
│       │   └── evidence/
│       ├── pending-feat-yyy/
│       └── archive/
│           ├── done-feat-zzz/
│           └── archive-log.yaml
│
└── project-context.md

# Worktrees (在项目外部)
../Project-feat-xxx/
../Project-feat-yyy/
```

### 版本历史

| 版本 | 日期 | 说明 |
|------|------|------|
| 1.0.0 | 2026-03-03 | 初始版本 |

---

## 联系与反馈

如有问题或建议，请在项目中提出 Issue。
