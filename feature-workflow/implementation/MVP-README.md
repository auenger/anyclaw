# Feature Workflow MVP

基于 Git Worktree 的多需求并行开发工作流 MVP 版本。

## 快速开始

### 可用命令

| 命令 | 说明 |
|------|------|
| `/new-feature [描述]` | 创建新需求 |
| `/start-feature <id>` | 启动需求开发 |
| `/implement-feature <id>` | 实现需求代码 |
| `/verify-feature <id>` | 验证需求完成 |
| `/complete-feature <id>` | 完成需求（提交→合并→归档） |
| `/list-features` | 查看所有需求状态 |

### 完整开发流程

```
/new-feature 用户认证
      ↓
/start-feature feat-user-auth
      ↓
/implement-feature feat-user-auth
      ↓
/verify-feature feat-user-auth
      ↓
/complete-feature feat-user-auth
```

## 目录结构

```
.claude/commands/feature-workflow/skills/   ← Claude Code Skills
├── new-feature.md
├── start-feature.md
├── implement-feature.md
├── verify-feature.md
├── complete-feature.md
└── list-features.md

feature-workflow/
├── config.yaml              ← 项目配置
├── queue.yaml               ← 调度队列
├── templates/               ← 文档模板
│   ├── spec.md
│   ├── task.md
│   └── checklist.md
└── implementation/
    ├── skills-implemented/  ← Skills 冗余副本
    └── core-lib.md          ← 核心库文档

features/
├── pending-{id}/            ← 等待中
├── active-{id}/             ← 进行中
└── archive/
    ├── archive-log.yaml     ← 归档日志
    └── done-{id}/           ← 已完成
```

## 配置说明

### config.yaml

```yaml
project:
  name: OA_Tool
  main_branch: main

parallelism:
  max_concurrent: 2          # 最大并行开发数

workflow:
  auto_start: true           # 完成后自动启动下一个
  require_checklist: true    # 完成前检查 checklist

completion:
  archive:
    create_tag: true         # 创建归档 tag
  cleanup:
    delete_worktree: true    # 删除 worktree
    delete_branch: true      # 删除分支
```

## 状态流转

```
/new-feature → pending-{id}/ → queue.yaml(pending)
      ↓
/start-feature → active-{id}/ → queue.yaml(active) + worktree
      ↓
/complete-feature → archive/done-{id}/ → archive-log.yaml + tag
```

## 归档策略

完成后执行：
- 创建 Tag (格式: feat-auth-20260302)
- 删除 Worktree（释放空间）
- 删除 Branch（可通过 tag 恢复）
- 更新 spec.md 添加合并记录
- 更新 archive-log.yaml

## 文件清单

### Skills (6个)

| Skill | 触发命令 | 职责 |
|-------|----------|------|
| new-feature | `/new-feature` | 创建需求（对话 → 文档 → 队列） |
| start-feature | `/start-feature` | 启动环境（分支 → worktree） |
| implement-feature | `/implement-feature` | 实现需求（spec → task → 代码） |
| verify-feature | `/verify-feature` | 验证需求（checklist 检查） |
| complete-feature | `/complete-feature` | 完成需求（提交→合并→tag→归档） |
| list-features | `/list-features` | 查看状态 |

### 核心文件

| 文件 | 位置 | 说明 |
|------|------|------|
| config.yaml | feature-workflow/ | 项目配置 |
| queue.yaml | feature-workflow/ | 调度队列 |
| archive-log.yaml | features/archive/ | 归档日志 |
| core-lib.md | implementation/ | 核心库文档 |

## 下一步

1. 测试 MVP 流程
2. 实现 Phase 2 管理 Skills
3. 实现 Phase 3 Workflows
4. 实现 Phase 4 Agents
