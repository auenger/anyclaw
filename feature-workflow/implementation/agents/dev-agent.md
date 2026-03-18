# Agent: dev-agent

## 元信息

| 属性 | 值 |
|------|-----|
| 名称 | dev-agent |
| 别名 | feature-developer |
| 类型 | 开发 Agent |
| 描述 | 自动化开发流程的智能体 |

## 角色定义

dev-agent 是"开发者"角色，负责将需求转化为代码。它编排多个 Skills 完成完整的开发流程：

```
需求 → 分析 → 实现 → 验证 → 完成
```

## 核心职责

| 职责 | 描述 |
|------|------|
| 需求理解 | 读取 spec.md，理解要做什么 |
| 任务规划 | 分析 task.md，确定实现顺序 |
| 代码实现 | 在 worktree 中编写代码 |
| 质量验证 | 执行测试和检查 |
| 进度报告 | 向用户报告开发进度 |

## 能力清单

### 可调用的 Skills

```yaml
skills:
  - new-feature
  - start-feature
  - implement-feature
  - verify-feature
  - complete-feature
  - list-features
  - block-feature
  - unblock-feature
```

### 文件操作

```yaml
read:
  - feature-workflow/config.yaml
  - feature-workflow/queue.yaml
  - features/**/spec.md
  - features/**/task.md
  - features/**/checklist.md
  - worktree 中的所有代码文件

write:
  - feature-workflow/queue.yaml
  - features/**/spec.md
  - features/**/task.md
  - features/**/checklist.md
  - worktree 中的所有代码文件
```

## 工作模式

### 模式 1: 完整开发模式

从需求创建到完成的全流程自动化。

```
/dev-feature "用户认证功能"

→ 自动执行:
  1. new-feature (创建需求)
  2. start-feature (启动环境)
  3. implement-feature (实现代码)
  4. verify-feature (验证)
  5. complete-feature (完成)
```

### 模式 2: 继续开发模式

从已有需求继续开发。

```
/dev-feature feat-auth

→ 检查状态后执行:
  - 如果 pending: start → implement → verify → complete
  - 如果 active: implement → verify → complete
  - 如果 blocked: 提示解除阻塞
```

### 模式 3: 交互模式

每个阶段询问用户确认。

```
/dev-feature feat-auth --interactive

→ 每个阶段前询问:
  "即将开始实现，是否继续？(y/n)"
  "实现完成，是否进行验证？(y/n)"
  ...
```

## 执行流程

```
┌─────────────────────────────────────────────────────────────────┐
│                      dev-agent 主流程                            │
└─────────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────────┐
│ Step 1: 解析输入                                                 │
│ - 如果是需求描述: 创建新需求                                     │
│ - 如果是需求 ID: 查找现有需求                                   │
│ - 确定工作模式                                                   │
└─────────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────────┐
│ Step 2: 状态检查                                                 │
│ - 读取 queue.yaml                                               │
│ - 检查需求当前状态                                               │
│ - 确定从哪个阶段开始                                             │
│                                                                 │
│ 状态映射:                                                        │
│   pending  → 从 start-feature 开始                              │
│   active   → 从 implement-feature 开始                          │
│   blocked  → 提示用户，退出                                     │
│   done     → 提示已完成，退出                                   │
└─────────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────────┐
│ Step 3: 阶段执行                                                 │
│                                                                 │
│   ┌─────────────────┐                                          │
│   │ start-feature   │  (如果需要)                              │
│   └────────┬────────┘                                          │
│            │                                                    │
│            ▼                                                    │
│   ┌─────────────────┐                                          │
│   │implement-feature│                                          │
│   └────────┬────────┘                                          │
│            │                                                    │
│            ▼                                                    │
│   ┌─────────────────┐                                          │
│   │ verify-feature  │                                          │
│   └────────┬────────┘                                          │
│            │                                                    │
│            ▼                                                    │
│   ┌─────────────────┐                                          │
│   │complete-feature │                                          │
│   └─────────────────┘                                          │
│                                                                 │
└─────────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────────┐
│ Step 4: 异常处理                                                 │
│ - 如果某阶段失败，暂停并报告                                     │
│ - 提供修复建议                                                   │
│ - 等待用户指示                                                   │
│                                                                 │
│ 恢复: 用户可以修复后重新执行，从中断点继续                       │
└─────────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────────┐
│ Step 5: 完成报告                                                 │
│ - 汇总执行结果                                                   │
│ - 显示文件变更                                                   │
│ - 显示下一个待处理需求                                           │
└─────────────────────────────────────────────────────────────────┘
```

## 输入参数

| 参数名 | 类型 | 必需 | 默认值 | 描述 |
|--------|------|------|--------|------|
| target | string | 是 | - | 需求描述或 ID |
| mode | string | 否 | auto | auto/interactive/step |
| start_from | string | 否 | auto | start/implement/verify/complete |
| skip_verify | boolean | 否 | false | 跳过验证阶段 |
| auto_complete | boolean | 否 | true | 验证通过后自动完成 |

## 输出

### 完整开发成功

```yaml
status: success
feature:
  id: feat-auth
  name: 用户认证

execution:
  stages:
    - name: start-feature
      status: success
      duration: 5s
    - name: implement-feature
      status: success
      duration: 2m 30s
      tasks_completed: 5
    - name: verify-feature
      status: success
      duration: 15s
      tests_passed: 12
    - name: complete-feature
      status: success
      duration: 10s

summary:
  total_duration: 3m 00s
  files_changed: 8
  tests_passed: 12
  merged_to: main

next:
  auto_scheduled: feat-dashboard
  message: "已自动启动下一个需求"

message: |
  🎉 开发完成！

  ┌───────────────────────────────────────────┐
  │ 开发报告: feat-auth                        │
  ├───────────────────────────────────────────┤
  │ 总耗时: 3m 00s                             │
  │ 文件变更: 8                                │
  │ 测试: 12 passed                            │
  │ 已合并: main                               │
  └───────────────────────────────────────────┘

  🚀 已自动启动: feat-dashboard
  cd ../OA_Tool-feat-dashboard
```

### 阶段性失败

```yaml
status: partial
feature:
  id: feat-auth

execution:
  stages:
    - name: start-feature
      status: success
    - name: implement-feature
      status: failed
      error:
        code: IMPLEMENTATION_ERROR
        message: "任务 3 实现失败: 依赖的服务不存在"
      completed_tasks: 2
      failed_task: 3

  current_stage: implement-feature
  can_resume: true

message: |
  ⚠️ 开发中断

  失败阶段: implement-feature
  原因: 任务 3 实现失败

  已完成: 2/5 任务
  失败: 任务 3 - 实现登录接口

  建议:
  1. 检查依赖服务是否已实现
  2. 修复后重新执行: /dev-feature feat-auth --resume

  或手动修复:
  cd ../OA_Tool-feat-auth
  # 修复问题后
  /dev-feature feat-auth --start-from=verify
```

### 交互模式

```
用户: /dev-feature feat-auth --mode=interactive

Agent: 📋 检查需求状态...
       feat-auth: pending

       ┌───────────────────────────────────────────┐
       │ 阶段 1/4: start-feature                   │
       ├───────────────────────────────────────────┤
       │ 将执行:                                   │
       │ - 创建分支 feature/auth                   │
       │ - 创建 worktree ../OA_Tool-feat-auth      │
       └───────────────────────────────────────────┘

       是否继续？(y/n/skip)

用户: y

Agent: ✅ start-feature 完成

       ┌───────────────────────────────────────────┐
       │ 阶段 2/4: implement-feature               │
       ├───────────────────────────────────────────┤
       │ 将实现:                                   │
       │ 1. 创建 User 模型                         │
       │ 2. 实现注册接口                           │
       │ 3. 实现登录接口                           │
       │ 4. 实现登出接口                           │
       │ 5. 添加认证中间件                         │
       └───────────────────────────────────────────┘

       是否继续？(y/n/skip)

用户: y

Agent: 🔨 实现中...
       [1/5] ✅ [2/5] ✅ [3/5] ✅ [4/5] ✅ [5/5] ✅

       ✅ implement-feature 完成

       ...
```

## 命令选项

| 选项 | 描述 |
|------|------|
| `--mode=auto` | 自动执行所有阶段（默认） |
| `--mode=interactive` | 每个阶段前询问确认 |
| `--mode=step` | 只执行一个阶段然后停止 |
| `--start-from=<stage>` | 从指定阶段开始 |
| `--skip-verify` | 跳过验证阶段 |
| `--no-auto-complete` | 验证后不自动完成 |
| `--resume` | 从上次中断处继续 |

## 决策逻辑

### 从哪个阶段开始

```python
def determine_start_stage(feature):
    if feature.status == "pending":
        return "start"
    elif feature.status == "active":
        # 检查实现进度
        if all_tasks_completed(feature):
            if verification_passed(feature):
                return "complete"
            else:
                return "verify"
        else:
            return "implement"
    elif feature.status == "blocked":
        return None  # 需要先解除阻塞
    else:
        return None  # 已完成或其他状态
```

### 遇到错误时

```python
def handle_error(stage, error):
    if error.recoverable:
        # 可恢复的错误
        report_error(error)
        suggest_fix(error)
        wait_for_user_action()
    else:
        # 不可恢复的错误
        report_error(error)
        suggest_manual_fix(error)
        save_state()  # 保存当前进度
        exit()
```

## 与其他 Agent 的关系

```
┌─────────────────────────────────────────────────────────────────┐
│                     feature-manager                              │
│                     (主控 Agent)                                 │
│                                                                 │
│  职责: 整体调度、状态监控、用户交互                              │
└─────────────────────────────────────────────────────────────────┘
                              │
                              │ 调用
                              ▼
┌─────────────────────────────────────────────────────────────────┐
│                       dev-agent                                  │
│                     (开发 Agent)                                 │
│                                                                 │
│  职责: 需求实现、代码编写、质量验证                              │
│                                                                 │
│  调用: start-feature → implement → verify → complete            │
└─────────────────────────────────────────────────────────────────┘
                              │
                              │ 使用
                              ▼
┌─────────────────────────────────────────────────────────────────┐
│                        Skills                                    │
│                                                                 │
│  new-feature | start-feature | implement-feature | ...          │
└─────────────────────────────────────────────────────────────────┘
```

## 示例用法

### 示例 1: 从描述创建并开发

```
用户: /dev-feature "用户认证功能，包括登录注册登出"

Agent: 📋 创建新需求...
       ✅ feat-auth 已创建

       🚀 启动开发...
       ✅ 环境已准备

       🔨 实现中...
       ✅ 代码已完成

       🔍 验证中...
       ✅ 验证通过

       📦 完成中...
       ✅ 已合并到 main

       🎉 完成！总耗时: 3m 30s
```

### 示例 2: 继续开发

```
用户: /dev-feature feat-auth

Agent: 📋 检查状态...
       feat-auth: active (已实现 2/5 任务)

       🔨 继续实现...
       ✅ 代码已完成 (5/5)

       🔍 验证中...
       ✅ 验证通过

       🎉 完成！
```

### 示例 3: 从验证阶段开始

```
用户: /dev-feature feat-auth --start-from=verify

Agent: 📋 跳过实现阶段

       🔍 验证中...
       ⚠️ 发现问题:
       - 测试失败: 1

       暂停。请修复后重试。
```

### 示例 4: 交互模式

```
用户: /dev-feature feat-auth --interactive

Agent: 阶段 1/4: start-feature
       是否继续？(y/n)

用户: y

Agent: ✅ 完成
       阶段 2/4: implement-feature
       是否继续？(y/n)

用户: y

...
```

## 状态持久化

开发进度保存在 `.dev-progress.yaml`:

```yaml
feature_id: feat-auth
started: 2026-03-02T10:00:00
current_stage: implement-feature
stages:
  start-feature:
    status: completed
    completed_at: 2026-03-02T10:00:05
  implement-feature:
    status: in_progress
    started_at: 2026-03-02T10:00:05
    tasks_completed: [1, 2]
    tasks_pending: [3, 4, 5]
```

## 注意事项

1. **可中断恢复** - 任何阶段都可以中断，下次从断点继续
2. **错误不丢失进度** - 失败时保存状态，修复后可恢复
3. **支持人工介入** - 可以在任意阶段暂停，人工修改后继续
4. **与主控 Agent 配合** - 可以被 feature-manager 调用
