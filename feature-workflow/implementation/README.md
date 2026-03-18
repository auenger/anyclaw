# Implementation 目录说明

本目录包含 Feature Workflow 的所有实现文档。

## 目录结构

```
implementation/
├── README.md                 ← 本文件
│
├── skills/                   ← Skill 文档 (10个)
│   ├── new-feature.md        ← P0: 创建需求
│   ├── start-feature.md      ← P0: 启动环境
│   ├── implement-feature.md  ← P0: 实现需求
│   ├── verify-feature.md     ← P0: 验证需求
│   ├── complete-feature.md   ← P0: 完成需求（含 tag 归档）
│   ├── list-features.md      ← P0: 查看状态
│   ├── block-feature.md      ← P1: 阻塞需求
│   ├── unblock-feature.md    ← P1: 解除阻塞
│   ├── feature-config.md     ← P1: 修改配置
│   └── cleanup-features.md   ← P1: 清理
│
├── workflows/                ← Workflow 文档 (2个)
│   ├── feature-lifecycle.md  ← 完整生命周期
│   └── auto-schedule.md      ← 自动调度
│
└── agents/                   ← Agent 文档 (2个)
    ├── feature-manager.md    ← 主控 Agent
    └── dev-agent.md          ← 开发 Agent
```

## 组件清单

### Skills (10个)

#### P0 核心 Skills

| Skill | 触发命令 | 职责 |
|-------|----------|------|
| `new-feature` | `/new-feature` | 创建需求（对话 → 文档 → 队列） |
| `start-feature` | `/start-feature` | 启动环境（分支 → worktree） |
| `implement-feature` | `/implement-feature` | 实现需求（spec → task → 代码） |
| `verify-feature` | `/verify-feature` | 验证需求（checklist 检查） |
| `complete-feature` | `/complete-feature` | 完成需求（提交→合并→tag→归档） |
| `list-features` | `/list-features` | 查看状态 |

#### P1 管理 Skills

| Skill | 触发命令 | 职责 |
|-------|----------|------|
| `block-feature` | `/block-feature` | 阻塞需求 |
| `unblock-feature` | `/unblock-feature` | 解除阻塞 |
| `feature-config` | `/feature-config` | 修改配置 |
| `cleanup-features` | `/cleanup-features` | 清理 |

### Workflows (2个)

| Workflow | 触发命令 | 职责 |
|----------|----------|------|
| `feature-lifecycle` | `/feature-lifecycle` | 完整生命周期管理（交互式） |
| `auto-schedule` | 自动触发 | 自动调度待处理需求 |

### Agents (2个)

| Agent | 职责 |
|-------|------|
| `feature-manager` | 主控 Agent：整体调度、状态监控、用户交互 |
| `dev-agent` | 开发 Agent：需求实现、代码编写、质量验证 |

## 归档策略

完成需求时执行：

| 操作 | 说明 |
|------|------|
| 创建 Tag | 格式: feat-auth-20260302，可追溯历史 |
| 删除 Worktree | 释放磁盘空间 |
| 删除 Branch | 保持仓库整洁（可通过 tag 恢复） |
| 更新 spec.md | 添加合并记录和统计 |
| 更新 archive-log.yaml | 位置: features/archive/archive-log.yaml |

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

## 使用方式

### 方式 1: 逐步调用 Skill（精细控制）

```
/new-feature 用户认证
/start-feature feat-auth
/implement-feature feat-auth
/verify-feature feat-auth
/complete-feature feat-auth
```

### 方式 2: 使用 dev-agent（自动化）

```
/dev-feature feat-auth
```

或从描述开始：

```
/dev-feature "用户认证功能"
```

### 方式 3: 使用 workflow（交互引导）

```
/feature-lifecycle
```

## 实现优先级

### Phase 1: 核心 Skills (MVP) ✅ 已完成

必须先实现，提供基本功能：

- [x] `new-feature` - 创建需求
- [x] `start-feature` - 启动开发
- [x] `implement-feature` - 实现需求
- [x] `verify-feature` - 验证需求
- [x] `complete-feature` - 完成需求（含 tag 归档）
- [x] `list-features` - 查看状态

### Phase 2: 管理 Skills ✅ 已完成

增强管理能力：

- [x] `block-feature` - 阻塞需求
- [x] `unblock-feature` - 解除阻塞
- [x] `feature-config` - 修改配置
- [x] `cleanup-features` - 清理

### Phase 3: Workflows ✅ 已完成

编排和自动化：

- [x] `feature-lifecycle` - 完整生命周期
- [x] `auto-schedule` - 自动调度

### Phase 4: Agents ✅ 已完成

智能化管理：

- [x] `feature-manager` - 主控 Agent
- [x] `dev-agent` - 开发 Agent

## 文档规范

每个 Skill 文档包含以下部分：

1. **元信息** - 名称、触发命令、优先级、依赖
2. **功能描述** - 做什么
3. **输入参数** - 接受什么参数
4. **前置条件** - 执行前需要满足的条件
5. **执行流程** - 怎么做（流程图）
6. **输出** - 返回什么
7. **错误码** - 可能的错误
8. **文件变更** - 会修改哪些文件
9. **示例用法** - 使用示例
10. **注意事项** - 特殊情况

## 关键文件位置

| 文件 | 位置 | 说明 |
|------|------|------|
| config.yaml | feature-workflow/ | 项目配置（并行数、命名规则、归档策略） |
| queue.yaml | feature-workflow/ | 调度队列（活跃和待处理的需求） |
| archive-log.yaml | features/archive/ | 归档日志（已完成需求的摘要和 tag） |
| templates/ | feature-workflow/ | 文档模板（spec.md, task.md, checklist.md） |

## 下一步

1. Review 各文档，确认逻辑正确
2. 选择实现方式（Skill 文件 / BMAD Workflow / 自定义）
3. 从 Phase 1 开始实现
4. 测试验证
