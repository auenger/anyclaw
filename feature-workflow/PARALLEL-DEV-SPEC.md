# parallel-dev 最终方案

## 设计理念

**主 Agent 无状态，文件是真相**

- 使用 `claude --print` 非交互模式启动独立的 Feature Agent
- Feature Agent 自治：implement → verify → complete → 退出
- 所有状态持久化在文件中，可随时恢复
- 主 Agent 通过轮询 .status 文件监控进度

## 架构

```
┌─────────────────────────────────────────────────────────────────────┐
│ 主 Agent (无状态，可恢复)                                            │
│                                                                      │
│  每次运行都:                                                         │
│  1. 读取 queue.yaml (获取 active features)                          │
│  2. 检查每个 .status 文件                                           │
│  3. 根据状态决定: 启动新进程 / 显示进度 / 更新队列                    │
│  4. 询问用户是否继续监控                                             │
│                                                                      │
│  任何时候被中断，重新运行 /parallel-dev 即可恢复                      │
│                                                                      │
│  上下文: 只读小的 .status 文件，不会膨胀                             │
└─────────────────────────────────────────────────────────────────────┘
         │
         │  ./scripts/start-feature-agent.sh feat-auth ../worktree &
         │
         ▼
┌─────────────────────────────────────────────────────────────────────┐
│ Feature Agent (独立进程，自治)                                       │
│                                                                      │
│  生命周期: implement → verify → complete → 退出                     │
│                                                                      │
│  输出:                                                               │
│  - .status (结构化状态)                                              │
│  - .log (日志 + EVENT token)                                        │
│                                                                      │
│  EVENT Token:                                                        │
│  - EVENT:START feat-auth                                            │
│  - EVENT:STAGE feat-auth implement                                  │
│  - EVENT:PROGRESS feat-auth 3/5                                     │
│  - EVENT:BLOCKED feat-auth "reason"                                 │
│  - EVENT:COMPLETE feat-auth feat-auth-20260305                      │
└─────────────────────────────────────────────────────────────────────┘
```

## 文件结构

```
feature-workflow/
├── config.yaml
├── queue.yaml
├── scripts/
│   └── start-feature-agent.sh      # ✅ 启动脚本
└── implementation/skills/
    └── parallel-dev.md              # ✅ 主编排 skill

features/
├── active-feat-auth/
│   ├── spec.md                      # 需求文档
│   ├── task.md                      # 任务列表
│   ├── checklist.md                 # 检查清单
│   ├── .status                      # ✅ 状态文件 (核心)
│   └── .log                         # ✅ 日志 + EVENT token
```

## 状态文件 (.status)

```yaml
feature_id: feat-auth
feature_name: 用户认证
status: started | implementing | verifying | completing | blocked | done | error
stage: init | implement | verify | complete
progress:
  tasks_total: 5
  tasks_done: 3
  current_task: "实现登录 API"
started_at: 2026-03-05T10:00:00Z
updated_at: 2026-03-05T10:30:00Z

# 完成时
completion:
  duration: "2h 30m"
  commits: 5
  tag: feat-auth-20260305

# 阻塞时
blocked:
  reason: "Rebase 冲突"
  stage: "complete"
  needs_help: true

# 错误时
error:
  message: "进程异常"
```

## EVENT Token 格式

Feature Agent 在 .log 中输出标准事件：

```
EVENT:START feat-auth
EVENT:STAGE feat-auth implement
EVENT:PROGRESS feat-auth 3/5
EVENT:BLOCKED feat-auth "Rebase conflict"
EVENT:COMPLETE feat-auth feat-auth-20260305
EVENT:ERROR feat-auth "Something went wrong"
```

用途：
- 方便调试和审计
- 可以用 `grep "^EVENT:" .log | tail -10` 查看最近事件

## 恢复机制

**核心原则**：主 Agent 无状态，所有状态在文件中。

```
恢复流程:

1. 用户运行 /parallel-dev

2. 主 Agent 读取 queue.yaml

3. 对于每个 active feature:
   - 检查 .status 文件
   - 根据当前状态决定行动:
     - not_started → 启动 Feature Agent
     - implementing/verifying/completing → 显示进度
     - done → 更新队列
     - blocked → 提示用户处理
     - error → 提示查看日志

4. 如果所有 feature 都是 done:
   - 显示完成汇总
   - 询问是否启动下一个

5. 如果有 blocked:
   - 显示阻塞原因
   - 提供解决建议
```

**任何时候被中断（Ctrl+C、Compact、超时），重新运行 `/parallel-dev` 即可恢复。**

## 使用方法

### 1. 创建 feature 并 start

```
/new-feature 用户认证
/start-feature feat-auth
```

### 2. 启动并行开发

```
/parallel-dev
```

### 3. 查看状态

```bash
# 查看状态文件
cat features/active-feat-auth/.status

# 查看日志
tail -f features/active-feat-auth/.log

# 查看最近事件
grep "^EVENT:" features/active-feat-auth/.log | tail -10
```

## 实现组件

### ✅ 已完成

| 组件 | 文件 | 说明 |
|------|------|------|
| 方案文档 | `PARALLEL-DEV-SPEC.md` | 本文档 |
| 启动脚本 | `scripts/start-feature-agent.sh` | 启动 Feature Agent |
| parallel-dev skill | `implementation/skills/parallel-dev.md` | 主编排 skill |

### 组件职责

| 组件 | 职责 |
|------|------|
| **parallel-dev skill** | 读取队列、检查状态、启动进程、显示进度 |
| **start-feature-agent.sh** | 初始化状态、构建 prompt、启动 claude --print |
| **Feature Agent** | 执行 implement → verify → complete，输出 EVENT token |
| **.status 文件** | 持久化状态，主 Agent 读取 |

## 设计决策

### 为什么不用 Monitor 进程？

Monitor 进程无法直接通知主 Agent，还是要通过文件。所以直接让主 Agent 轮询 .status 文件更简单。

### 为什么用 EVENT Token？

1. 方便调试：可以快速查看执行过程
2. 审计追踪：完整的执行历史
3. 可选监控：如果需要更实时的监控，可以 `tail -f .log | grep EVENT`

### 为什么主 Agent 无状态？

1. **Compact 安全**：即使被压缩，也能从文件恢复
2. **可中断恢复**：任何时候都能恢复
3. **上下文可控**：只读小文件，不会膨胀

## 跨平台支持

| 平台 | 启动方式 |
|------|----------|
| macOS/Linux | `claude --print ... &` |
| Windows | `claude --print ... &` (Git Bash / WSL) |

## 错误处理

| 场景 | 检测 | 处理 |
|------|------|------|
| 正常完成 | status: done | 更新队列，汇报 |
| 阻塞 | status: blocked | 提示用户处理 |
| 进程崩溃 | status 不是 done 且 updated_at 过旧 | 标记 error，提示查看日志 |
| Worktree 不存在 | 目录检查失败 | 提示先运行 /start-feature |

## 优势

1. **主 Agent 无状态**：不依赖内存，可随时恢复
2. **文件是真相**：所有状态持久化
3. **上下文可控**：只读小的 .status 文件
4. **进程自治**：Feature Agent 完成后自动退出
5. **跨平台**：claude --print 通用
6. **可观测**：.status + .log + EVENT token
