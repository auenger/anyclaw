# Feature Workflow 实现方案

## 架构概览

```
┌─────────────────────────────────────────────────────────────────┐
│                        用户交互层                                │
│   /new-feature  /implement-feature  /complete-feature  ...      │
└─────────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────────┐
│                      Agent 层                                   │
│   feature-manager (主控) | dev-agent (开发自动化)               │
└─────────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────────┐
│                      Workflow 层                                │
│   feature-lifecycle (完整流程) | auto-schedule (自动调度)       │
└─────────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────────┐
│                       Skill 层 (10个)                           │
│   new | start | implement | verify | complete | list |         │
│   block | unblock | config | cleanup                            │
└─────────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────────┐
│                      数据层                                     │
│   config.yaml | queue.yaml | features/archive/archive-log.yaml │
└─────────────────────────────────────────────────────────────────┘
```

---

## 1. Skill 清单 (10个)

### 1.1 核心 Skills (P0)

| Skill 名称 | 触发命令 | 功能描述 |
|-----------|---------|---------|
| `new-feature` | `/new-feature` | 创建新需求（对话 → 文档 → 队列） |
| `start-feature` | `/start-feature <id>` | 启动开发（创建分支 + worktree） |
| `implement-feature` | `/implement-feature <id>` | 实现代码（spec → task → 代码） |
| `verify-feature` | `/verify-feature <id>` | 验证完成（checklist 检查） |
| `complete-feature` | `/complete-feature <id>` | 完成需求（提交→合并→tag→归档） |
| `list-features` | `/list-features` | 查看所有需求状态 |

### 1.2 管理 Skills (P1)

| Skill 名称 | 触发命令 | 功能描述 |
|-----------|---------|---------|
| `block-feature` | `/block-feature <id>` | 阻塞某个需求 |
| `unblock-feature` | `/unblock-feature <id>` | 解除阻塞 |
| `feature-config` | `/feature-config` | 修改配置 |
| `cleanup-features` | `/cleanup-features` | 清理无效 worktree |

---

## 2. Workflow 清单 (2个)

| Workflow | 触发命令 | 描述 |
|----------|----------|------|
| `feature-lifecycle` | `/feature-lifecycle` | 完整生命周期管理（交互式） |
| `auto-schedule` | 自动触发 | 自动调度待处理需求 |

---

## 3. Agent 清单 (2个)

| Agent | 描述 |
|-------|------|
| `feature-manager` | 主控 Agent：整体调度、状态监控、异常处理 |
| `dev-agent` | 开发 Agent：自动执行 start→implement→verify→complete |

---

## 4. 完整开发流程

```
┌─────────────────────────────────────────────────────────────────┐
│                      一个需求的完整生命周期                      │
└─────────────────────────────────────────────────────────────────┘

  用户输入
      │
      ▼
  ┌─────────────┐
  │ new-feature │     对话确认 → 生成文档 → 加入队列
  └──────┬──────┘
         │
         ▼
  ┌─────────────┐
  │start-feature│     创建分支 → 创建 worktree
  └──────┬──────┘
         │
         ▼
  ┌──────────────┐
  │implement-feat│     读取 spec → 分析 task → 实现代码
  └──────┬───────┘
         │
         ▼
  ┌─────────────┐
  │verify-feature│    执行 checklist → 运行测试 → 验证验收标准
  └──────┬──────┘
         │
         ▼
  ┌─────────────┐
  │complete-feat│     提交 → 合并 → 创建 tag → 删除 worktree/分支 → 归档
  └─────────────┘
         │
         ▼
    自动调度下一个
```

---

## 5. 归档策略

完成需求时执行：

| 操作 | 说明 |
|------|------|
| 创建 Tag | 格式: feat-auth-20260302，可追溯历史 |
| 删除 Worktree | 释放磁盘空间 |
| 删除 Branch | 保持仓库整洁（可通过 tag 恢复） |
| 更新 spec.md | 添加合并记录和统计 |
| 更新 archive-log.yaml | 记录归档信息 |

---

## 6. 文件依赖关系

```
feature-workflow/
├── config.yaml          ← 所有 Skills 读取
├── queue.yaml           ← 核心状态，所有 Skills 读写
└── templates/
    ├── spec.md          ← new-feature 使用
    ├── task.md          ← new-feature 使用
    └── checklist.md     ← new-feature 创建, verify/complete 检查

features/
├── pending-{id}/        ← new-feature 创建
├── active-{id}/         ← start-feature 重命名
└── archive/
    ├── archive-log.yaml ← complete-feature 写入
    └── done-{id}/       ← complete-feature 归档
```

---

## 7. 实现优先级

### Phase 1: 核心 Skills (MVP)

```
[ ] new-feature        - 创建需求
[ ] start-feature      - 启动开发
[ ] implement-feature  - 实现代码
[ ] verify-feature     - 验证完成
[ ] complete-feature   - 完成需求（含 tag 归档）
[ ] list-features      - 查看状态
```

### Phase 2: 管理 Skills

```
[ ] block-feature      - 阻塞需求
[ ] unblock-feature    - 解除阻塞
[ ] feature-config     - 修改配置
[ ] cleanup-features   - 清理
```

### Phase 3: Workflows

```
[ ] feature-lifecycle  - 完整生命周期
[ ] auto-schedule      - 自动调度
```

### Phase 4: Agents

```
[ ] feature-manager    - 主控 Agent
[ ] dev-agent          - 开发 Agent（自动化流程）
```

---

## 8. 使用方式

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

---

## 9. 下一步行动

1. **选择实现方式**
   - 作为 Claude Code 的 Skill 文件
   - 作为 BMAD 的 Workflow
   - 混合方式

2. **创建第一个 Skill**
   - 建议从 `new-feature` 开始

3. **测试流程**
   - 创建测试需求
   - 验证完整流程（含 tag 归档）

4. **实现 dev-agent**
   - 编排 Skills 实现自动化
