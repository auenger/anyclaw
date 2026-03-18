# Feature Workflow

基于 Git Worktree 的多需求并行开发工作流。

## 核心理念

- **并行开发**: 支持多个需求同时开发，通过 worktree 物理隔离
- **自动调度**: 根据优先级自动安排开发顺序
- **状态追踪**: 通过 queue.yaml 统一管理需求状态
- **文档驱动**: 每个需求包含 spec/task/checklist 三个文档
- **归档策略**: 完成后创建 tag 归档，删除 worktree 和分支

## 目录结构

```
/OA_Tool/                              ← 主仓库 (main 分支)
├── feature-workflow/                  ← 工作流配置目录
│   ├── config.yaml                    ← 项目配置
│   ├── queue.yaml                     ← 调度队列
│   └── templates/                     ← 文档模板
│
├── features/                          ← 需求目录
│   ├── pending-feat-xxx/              ← 等待中
│   ├── active-feat-xxx/               ← 进行中
│   └── archive/                       ← 归档区
│       ├── archive-log.yaml           ← 归档日志
│       └── done-feat-xxx/             ← 已完成
│
└── src/

/OA_Tool-feat-xxx/                     ← worktree (同级目录)
```

## 命令列表

| 命令 | 说明 |
|------|------|
| `/new-feature` | 创建新需求 |
| `/start-feature <id>` | 启动需求开发 |
| `/implement-feature <id>` | 实现需求代码 |
| `/verify-feature <id>` | 验证需求完成 |
| `/complete-feature <id>` | 完成需求（提交→合并→归档） |
| `/list-features` | 查看所有需求状态 |
| `/block-feature <id>` | 阻塞某个需求 |
| `/unblock-feature <id>` | 解除阻塞 |
| `/feature-config` | 修改配置 |
| `/cleanup-features` | 清理无效的 worktree |

## 完整开发流程

```
/new-feature              创建需求（对话 → 文档 → 队列）
      ↓
/start-feature            启动开发（创建分支 → 创建 worktree）
      ↓
/implement-feature        实现代码（读取 spec → 分析 task → 写代码）
      ↓
/verify-feature           验证功能（执行 checklist → 运行测试）
      ↓
/complete-feature         完成需求（提交 → 合并 → 创建 tag → 归档）
      ↓
自动调度下一个
```

## 状态流转

```
/new-feature → pending-feat-xxx/ → queue.yaml(pending)
                    ↓
/start-feature → active-feat-xxx/ → queue.yaml(active) + worktree
                    ↓
/complete-feature → archive/done-feat-xxx/ → archive-log.yaml + tag
```

## 归档策略

完成后执行：
- ✅ 创建归档 tag (格式: feat-auth-20260302)
- ✅ 删除 worktree（释放空间）
- ✅ 删除分支（可通过 tag 恢复）
- ✅ 更新 spec.md 添加合并记录
- ✅ 更新 archive-log.yaml

## 文件说明

| 文件 | 位置 | 说明 |
|------|------|------|
| config.yaml | feature-workflow/ | 项目配置（并行数、命名规则、归档策略） |
| queue.yaml | feature-workflow/ | 调度队列（活跃和待处理的需求） |
| archive-log.yaml | features/archive/ | 归档日志（已完成需求的摘要和 tag） |
| templates/ | feature-workflow/ | 文档模板（spec.md, task.md, checklist.md） |

## 使用方式

### 方式 1: 逐步调用 Skill

```
/new-feature 用户认证
/start-feature feat-auth
/implement-feature feat-auth
/verify-feature feat-auth
/complete-feature feat-auth
```

### 方式 2: 使用 dev-agent 自动化

```
/dev-feature feat-auth
```

### 方式 3: 使用 workflow 交互引导

```
/feature-lifecycle
```

## 实现状态

### Phase 1: 核心 Skills ✅ 已完成

| Skill | 命令 | 状态 |
|-------|------|------|
| new-feature | `/new-feature` | ✅ 已实现 |
| start-feature | `/start-feature` | ✅ 已实现 |
| implement-feature | `/implement-feature` | ✅ 已实现 |
| verify-feature | `/verify-feature` | ✅ 已实现 |
| complete-feature | `/complete-feature` | ✅ 已实现 |
| list-features | `/list-features` | ✅ 已实现 |

### Phase 2: 管理 Skills ✅ 已完成

| Skill | 命令 | 状态 |
|-------|------|------|
| block-feature | `/block-feature` | ✅ 已实现 |
| unblock-feature | `/unblock-feature` | ✅ 已实现 |
| feature-config | `/feature-config` | ✅ 已实现 |
| cleanup-features | `/cleanup-features` | ✅ 已实现 |

### Phase 3: Workflows ✅ 已完成

| Workflow | 命令 | 状态 |
|----------|------|------|
| feature-lifecycle | `/feature-lifecycle` | ✅ 已实现 |
| auto-schedule | `/auto-schedule` | ✅ 已实现 |

### Phase 4: Agents ✅ 已完成

| Agent | 命令 | 状态 |
|-------|------|------|
| feature-manager | `/feature-manager` | ✅ 已实现 |
| dev-agent | `/dev-agent` | ✅ 已实现 |

## 实现文件位置

```
.claude/commands/feature-workflow/
├── skills/                   ← Skills (10个)
│   ├── new-feature.md
│   ├── start-feature.md
│   ├── implement-feature.md
│   ├── verify-feature.md
│   ├── complete-feature.md
│   ├── list-features.md
│   ├── block-feature.md
│   ├── unblock-feature.md
│   ├── feature-config.md
│   └── cleanup-features.md
├── workflows/                ← Workflows (2个)
│   ├── feature-lifecycle.md
│   └── auto-schedule.md
└── agents/                   ← Agents (2个)
    ├── feature-manager.md
    └── dev-agent.md

feature-workflow/implementation/
├── skills-implemented/       ← Skills 冗余副本
├── workflows-implemented/    ← Workflows 冗余副本
├── agents-implemented/       ← Agents 冗余副本
├── core-lib.md               ← 核心库文档
└── MVP-README.md             ← MVP 说明
```
