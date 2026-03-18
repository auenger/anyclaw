# Feature Workflow 安装指南

基于 Git Worktree 的 AI 辅助开发工作流，## 快速安装

```bash
# 方法 1: 使用安装脚本
./install.sh /path/to/your/project

# 方法 2: 手动安装
cp -r feature-workflow /path/to/your/project/
cp -r .claude /path/to/your/project/.claude/
```

## 目录结构

安装后的目录结构：

```
your-project/
├── .claude/
│   └── commands/
│       └── feature-workflow/
│           ├── skills/
│           │   ├── new-feature.md
│           │   ├── start-feature.md
│           │   ├── implement-feature.md
│           │   ├── verify-feature.md
│           │   ├── complete-feature.md
│           │   └── list-features.md
│           ├── workflows/
│           │   └── feature-lifecycle.md
│           └── agents/
│               ├── feature-manager.md
│               └── dev-agent.md
├── feature-workflow/
│   ├── config.yaml           # 工作流配置
│   ├── config.yaml.example   # 配置示例
│   ├── queue.yaml            # 需求队列
│   ├── templates/            # 模板文件
│   │   ├── spec.md
│   │   ├── task.md
│   │   └── checklist.md
│   └── features/             # 需求目录
│       ├── active/           # 进行中的需求
│       ├── pending/          # 待开发的需求
│       └── archive/          # 已完成的需求
└── project-context.md        # 项目上下文 (可选)
```

## 配置

编辑 `feature-workflow/config.yaml`：

```yaml
project:
  name: Your-Project-Name
  main_branch: main          # 主分支名
  repo_path: .               # 仓库路径 (monorepo 用)
  tech_stack: react-vite     # 技术栈

git:
  remote: origin             # 远程仓库名
  auto_push: false           # 自动推送
  merge_strategy: "--no-ff"  # 合并策略
  push_tags: true            # 推送标签

parallelism:
  max_concurrent: 2          # 最大并行数
```

## 使用方法

### 创建新需求

```
/new-feature 用户登录功能 - 实现用户登录、登出功能
```

### 开始开发

```
/start-feature feat-user-login
```

### 实现代码

```
/implement-feature feat-user-login
```

### 验证功能

```
/verify-feature feat-user-login
```

### 完成需求

```
/complete-feature feat-user-login
```

### 查看所有需求

```
/list-features
```

## 工作流程

```
┌─────────────────────────────────────────────────────────────────┐
│                    Feature Workflow                               │
├─────────────────────────────────────────────────────────────────┤
│                                                                 │
│  /new-feature     →  创建需求 (spec.md, task.md, checklist.md)   │
│        ↓                                                        │
│  /start-feature   →  创建 worktree + branch, 开始开发              │
│        ↓                                                        │
│  /implement-feature →  在 worktree 中实现代码                       │
│        ↓                                                        │
│  /verify-feature  →  运行测试，收集证据 (screenshots, traces)       │
│        ↓                                                        │
│  /complete-feature →  rebase, merge, archive, cleanup              │
│                                                                 │
└─────────────────────────────────────────────────────────────────┘
```

## Worktree 模式

Feature Workflow 使用 Git Worktree 实现并行开发：

```
main-project/           # 主仓库 (main 分支)
├── src/
└── feature-workflow/

../main-project-feat-auth/    # worktree (feature/auth 分支)
├── src/
└── ...开发中的代码...

../main-project-feat-dashboard/  # worktree (feature/dashboard 分支)
├── src/
└── ...开发中的代码...
```

## 归档结构

完成的需求会被归档：

```
features/archive/
└── done-feat-auth-20260303/
    ├── spec.md              # 需求规格
    ├── task.md              # 任务列表
    ├── checklist.md         # 完成检查
    ├── evidence/            # 验证证据
    │   ├── verification-report.md
    │   ├── test-results.json      # 测试结果
    │   ├── playwright-report/     # HTML 测试报告
    │   ├── e2e-tests/             # ⭐ E2E 测试脚本 (随 feature 归档)
    │   │   └── feat-auth.spec.ts
    │   ├── screenshots/
    │   └── traces/
    └── archive-meta.yaml    # 归档元数据
```

**重要**: E2E 测试脚本会随 feature 一起归档，方便后续追溯和复用。

## 标签恢复

所有完成的需求都会创建 Git 标签：

```bash
# 查看标签
git tag -l "feat-*"

# 从标签恢复分支
git checkout -b feature/auth-restored feat-auth-20260303
```

## 依赖要求

- Git >= 2.17 (worktree 支持)
- Claude Code CLI
- Node.js >= 16 (可选，用于 Playwright 测试)

## 版本历史

| 版本 | 日期 | 说明 |
|------|------|------|
| 1.0.0 | 2026-03-03 | 初始版本 |

## 许可证

MIT License
