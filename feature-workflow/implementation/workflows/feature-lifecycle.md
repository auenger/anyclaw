# Workflow: feature-lifecycle

## 元信息

| 属性 | 值 |
|------|-----|
| 名称 | feature-lifecycle |
| 触发命令 | `/feature-lifecycle` |
| 类型 | 交互式工作流 |
| 描述 | 完整的需求生命周期管理 |

## 功能描述

编排完整的需求生命周期，从创建到完成，包含多个阶段和技能调用。

## 阶段定义

```
┌─────────────────────────────────────────────────────────────────┐
│                        需求生命周期                              │
└─────────────────────────────────────────────────────────────────┘

  ┌─────────┐     ┌─────────┐     ┌─────────┐     ┌─────────┐
  │ Planning │ ──▶ │  Dev    │ ──▶ │ Review  │ ──▶ │  Done   │
  │  规划    │     │  开发    │     │  评审    │     │  完成    │
  └─────────┘     └─────────┘     └─────────┘     └─────────┘
       │               │               │               │
       ▼               ▼               ▼               ▼
   new-feature    start-feature   (手动评审)    complete-feature
   对话收集        创建分支                     提交合并
   生成文档        创建worktree                 归档清理
```

## 阶段详情

### 阶段 1: Planning（规划）

**目标**: 创建需求并生成文档

**技能调用**:
- `new-feature`

**用户交互**:
```
Agent: 欢迎使用需求生命周期工作流

       请描述你要开发的功能:

用户: 用户认证功能，包括登录、注册、登出

Agent: 请提供以下信息:

       1. 需求名称 (默认: 用户认证功能)
       2. 详细描述
       3. 优先级 (1-100, 默认 50)
       4. 依赖关系

用户: 名称: 用户认证
     描述: 实现完整的用户认证系统
     优先级: 80
     依赖: 无

Agent: 确认创建需求 feat-auth？

       - 名称: 用户认证
       - 优先级: 80
       - 依赖: 无

       (y/n/e=编辑)

用户: y

Agent: ✅ 需求已创建

       目录: features/pending-feat-auth
       文档: spec.md, task.md, checklist.md

       是否立即开始开发？(y/n)
```

**输出**:
- 需求 ID
- 需求目录和文档
- 队列状态

---

### 阶段 2: Development（开发）

**目标**: 启动开发环境

**技能调用**:
- `start-feature`

**用户交互**:
```
Agent: 🚀 启动开发环境

       检查并行限制... ✅
       创建分支 feature/auth... ✅
       创建 worktree... ✅

       开发环境已就绪！

       切换目录:
         cd ../OA_Tool-feat-auth

       查看任务:
         cat features/active-feat-auth/task.md

       开发完成后运行:
         /feature-lifecycle --next

       或直接完成:
         /complete-feature feat-auth
```

**手动阶段**:
- 用户在 worktree 中开发
- 更新 spec.md 的技术方案
- 完成 task.md 中的任务
- 勾选 checklist.md 中的检查项

---

### 阶段 3: Review（评审）

**目标**: 评审代码和文档

**用户交互**:
```
Agent: 📋 开发完成检查

       Checklist 状态:
       ✅ 所有任务已完成
       ✅ 代码已自测
       ⚠️ 单元测试未完成
       ✅ 代码风格符合规范

       Git 状态:
       - 变更文件: 12
       - 新增文件: 5
       - 删除文件: 1

       提交信息预览:
       feat(feat-auth): 用户认证功能

       是否继续完成？(y/n/edit)
```

**可选操作**:
- `edit`: 修改提交信息
- `skip`: 跳过未完成的 checklist
- `back`: 返回继续开发

---

### 阶段 4: Done（完成）

**目标**: 提交、合并、归档

**技能调用**:
- `complete-feature`

**用户交互**:
```
Agent: 🎉 完成需求

       提交代码... ✅
       合并到 main... ✅
       清理 worktree... ✅
       归档文档... ✅

       ┌───────────────────────────────────────────────┐
       │ 完成报告                                       │
       ├───────────────────────────────────────────────┤
       │ 需求: feat-auth (用户认证)                    │
       │ 开发时长: 2h 30m                              │
       │ 提交数: 5                                     │
       │ 变更文件: 18                                  │
       └───────────────────────────────────────────────┘

       下一个需求: feat-dashboard (优先级 80)
       是否自动启动？(y/n)
```

---

## 命令选项

| 选项 | 描述 |
|------|------|
| `--next` | 跳到下一阶段 |
| `--restart` | 重新开始当前阶段 |
| `--abort` | 中止工作流 |
| `--status` | 查看当前状态 |

## 状态持久化

工作流状态保存在 `.workflow-state.yaml`:

```yaml
workflow: feature-lifecycle
feature_id: feat-auth
current_stage: development
started: 2026-03-02T10:00:00
stages:
  planning:
    status: completed
    completed_at: 2026-03-02T10:05:00
  development:
    status: in_progress
    started_at: 2026-03-02T10:05:00
  review:
    status: pending
  done:
    status: pending
```

## 错误恢复

| 场景 | 恢复方式 |
|------|----------|
| 中途中断 | 重新执行 `/feature-lifecycle --status` 查看状态 |
| 阶段失败 | 修复后执行 `/feature-lifecycle --restart` |
| 想要放弃 | 执行 `/feature-lifecycle --abort` |

## 示例用法

### 完整流程

```
用户: /feature-lifecycle

Agent: 欢迎使用需求生命周期工作流...
       (引导完成所有阶段)

Agent: 🎉 需求 feat-auth 已完成！
```

### 从特定阶段开始

```
用户: /feature-lifecycle --stage=development

Agent: 当前需求: feat-auth
       启动开发环境...
```

### 查看状态

```
用户: /feature-lifecycle --status

Agent:
┌───────────────────────────────────────────────┐
│ Feature Lifecycle Status                       │
├───────────────────────────────────────────────┤
│ 需求: feat-auth                                │
│ 当前阶段: development                          │
│                                                │
│ ✅ planning (completed 2h ago)                │
│ 🔄 development (in progress)                  │
│ ⏳ review (pending)                           │
│ ⏳ done (pending)                             │
└───────────────────────────────────────────────┘
```

## 与单独 Skill 的关系

| 操作 | 使用 Skill | 使用 Workflow |
|------|-----------|---------------|
| 快速创建需求 | `/new-feature` | - |
| 快速完成需求 | `/complete-feature` | - |
| 完整引导流程 | - | `/feature-lifecycle` |
| 查看状态 | `/list-features` | `/feature-lifecycle --status` |

Workflow 更适合新手或需要引导的场景，Skill 更适合熟练用户的快速操作。
