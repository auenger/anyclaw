---
description: 'Parallel development - spawn Feature Agents and monitor progress (stateless, recoverable)'
---

# Skill: parallel-dev

并行开发编排器。启动多个 Feature Agent 进程，监控进度。

**核心原则**：主 Agent 无状态，所有状态持久化在文件中，可随时恢复。

## Usage

```
/parallel-dev                      # 并行开发/恢复监控
/parallel-dev --status             # 只查看状态
/parallel-dev <feature-id>         # 只处理指定 feature
```

## 工作原理

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
└─────────────────────────────────────────────────────────────────────┘
                              │
                              │  状态持久化在文件中
                              ▼
┌─────────────────────────────────────────────────────────────────────┐
│ 文件系统 (真相来源)                                                  │
│                                                                      │
│  queue.yaml           ← 队列状态                                    │
│  .status              ← 每个 feature 的详细状态                     │
│  .log                 ← 执行日志 + EVENT token                      │
└─────────────────────────────────────────────────────────────────────┘
```

## 状态文件 (.status)

位置: `features/active-{id}/.status`

```yaml
feature_id: feat-auth
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

## Execution Steps

### Step 1: 检查环境

```bash
# 检查启动脚本
SCRIPT="feature-workflow/scripts/start-feature-agent.sh"
if [ ! -x "$SCRIPT" ]; then
    echo "错误: 启动脚本不存在或不可执行"
    exit 1
fi
```

### Step 2: 读取队列状态

读取 `feature-workflow/queue.yaml`:

```yaml
active:
  - id: feat-auth
    name: 用户认证
    worktree: ../OA_Tool-feat-auth
    branch: feature/auth
```

### Step 3: 检查每个 Feature 的状态

对于每个 active feature：

```bash
STATUS_FILE="features/active-$FEATURE_ID/.status"

if [ ! -f "$STATUS_FILE" ]; then
    # 无状态文件 → 需要启动
    STATUS="not_started"
else
    # 读取状态
    STATUS=$(grep '^status:' "$STATUS_FILE" | awk '{print $2}')
    STAGE=$(grep '^stage:' "$STATUS_FILE" | awk '{print $2}')
    UPDATED=$(grep '^updated_at:' "$STATUS_FILE" | awk '{print $2}')
fi
```

### Step 4: 根据状态采取行动

| 状态 | 行动 |
|------|------|
| `not_started` | 启动新的 Feature Agent |
| `started` / `implementing` / `verifying` / `completing` | 显示进度 |
| `done` | 更新队列，可能启动下一个 |
| `blocked` | 提示用户处理 |
| `error` | 提示用户检查日志 |

### Step 5: 启动 Feature Agent

```bash
./feature-workflow/scripts/start-feature-agent.sh "$FEATURE_ID" "$WORKTREE" "$BRANCH"
```

### Step 6: 显示进度面板

```
📊 并行开发进度 @ 10:30:00
═══════════════════════════════════════════════════════════════════════

🔨 feat-auth
   状态: implementing | 阶段: implement
   进度: [████████████░░░░░░░░] 60% (3/5)
   当前: 实现登录 API
   更新: 5 minutes ago

🔍 feat-dashboard
   状态: verifying | 阶段: verify
   进度: [████████████████████] 100% (5/5)
   更新: 1 minute ago

═══════════════════════════════════════════════════════════════════════
运行中: 2 | 完成: 0 | 阻塞: 0
```

### Step 7: 监控循环

在监控过程中，每隔一段时间检查状态：

```
💡 操作:
   [c] 继续监控 (30s 后自动刷新)
   [s] 立即刷新
   [q] 退出 (后台进程继续运行)
   [l] 查看日志
```

### Step 8: 处理完成的 Feature

当检测到某个 feature 的 `status: done` 时：

```markdown
1. 显示完成信息:
   - 提交 hash
   - 完成时间
   - 任务统计

2. 调用 /complete-feature {id} 执行:
   - 合并到 main 分支
   - 创建归档 tag
   - 删除 worktree 和分支
   - 归档需求文档
   - 更新 queue.yaml

3. 验证清理结果:
   - 检查 worktree 目录是否已删除
   - 检查 active 目录是否已删除
   - 如果删除失败，提示用户手动清理
```

### Step 9: 自动循环调度 (核心改进)

**当所有 active feature 都完成时，自动启动下一个 pending feature：**

```markdown
自动调度逻辑:

1. 检查 queue.yaml 的 active 列表是否为空
   - 如果不为空，继续监控当前 feature
   - 如果为空，进入调度逻辑

2. 读取 config.yaml 的 workflow.auto_start_next 配置
   - 如果 false，询问用户是否继续
   - 如果 true，自动调度

3. 自动调度流程:
   a. 读取 queue.yaml 的 pending 列表
   b. 取 priority 最高的 feature (列表第一个)
   c. 检查依赖是否满足:
      - 读取 features/active-{id}/spec.md 或 features/pending-{id}/spec.md
      - 检查 dependencies 字段
      - 验证所有依赖是否在 completed 列表中
   d. 如果依赖满足:
      - 调用 /start-feature {id}
      - 调用 start-feature-agent.sh 启动 Feature Agent
      - 返回 Step 3 继续监控
   e. 如果依赖不满足:
      - 跳过该 feature，尝试下一个
      - 如果所有 pending feature 依赖都不满足，提示用户

4. 如果 pending 列表为空:
   - 显示完成汇总
   - 显示 "🎉 所有 feature 已完成!"
   - 退出
```

### Step 10: 循环监控实现

```
┌─────────────────────────────────────────────────────────────────────┐
│                        主循环                                        │
│                                                                      │
│  while true:                                                         │
│    1. 读取 queue.yaml                                                │
│    2. 对于每个 active feature:                                       │
│       - 读取 .status 文件                                            │
│       - 如果 status = done:                                          │
│         → 调用 /complete-feature                                     │
│         → 从 active 移除                                             │
│       - 如果 status = blocked:                                       │
│         → 显示阻塞原因                                               │
│         → 等待用户处理                                               │
│       - 如果 status = implementing/verifying/completing:             │
│         → 显示进度                                                   │
│                                                                      │
│    3. 如果 active 为空:                                              │
│       - 如果 auto_start_next = true 且 pending 不为空:               │
│         → 自动启动下一个 feature                                     │
│         → 继续循环                                                   │
│       - 如果 pending 为空:                                           │
│         → 显示完成汇总                                               │
│         → 退出                                                       │
│       - 如果 auto_start_next = false:                                │
│         → 询问用户是否继续                                           │
│                                                                      │
│    4. 等待 30 秒 (或用户输入)                                        │
│    5. 继续循环                                                       │
│                                                                      │
└─────────────────────────────────────────────────────────────────────┘
```

## 恢复逻辑

**关键**：任何时候重新运行 `/parallel-dev` 都能恢复。

```markdown
恢复流程:

1. 读取 queue.yaml
2. 对于每个 active feature:
   - 检查 .status 文件
   - 根据当前状态决定行动
   - 无需记住"上次做了什么"

3. 如果所有 feature 都是 done:
   - 显示完成汇总
   - 询问是否启动下一个 pending feature

4. 如果有 blocked:
   - 显示阻塞原因
   - 提供解决建议
```

## Output

### 首次启动

```
🚀 启动并行开发

检查 active features...
├── feat-auth: 需要启动
└── feat-dashboard: 需要启动

==================================================
启动 Feature Agent: feat-auth
==================================================
Feature ID:    feat-auth
Worktree:      ../OA_Tool-feat-auth
✅ 后台进程已启动 (PID: 12345)

==================================================
启动 Feature Agent: feat-dashboard
==================================================
...

📊 进入监控模式...
```

### 恢复运行

```
📊 恢复并行开发监控

检查 active features...
├── feat-auth: implementing (3/5) - 继续监控
└── feat-dashboard: verifying (5/5) - 继续监控

📊 当前进度...
```

### 全部完成

```
📊 并行开发进度 @ 10:45:00
═══════════════════════════════════════════════════════════════════════

✅ feat-auth
   状态: done
   耗时: 2h 30m | 提交: 5 | Tag: feat-auth-20260305

✅ feat-dashboard
   状态: done
   耗时: 1h 45m | 提交: 3 | Tag: feat-dashboard-20260305

═══════════════════════════════════════════════════════════════════════

🎉 所有 feature 已完成!

📊 汇总:
┌─────────────────┬──────────┬─────────┬────────────────────────┐
│ Feature         │ Duration │ Commits │ Tag                    │
├─────────────────┼──────────┼─────────┼────────────────────────┤
│ feat-auth       │ 2h 30m   │ 5       │ feat-auth-20260305     │
│ feat-dashboard  │ 1h 45m   │ 3       │ feat-dashboard-20260305│
└─────────────────┴──────────┴─────────┴────────────────────────┘

Pending: feat-export (priority 80)
🚀 启动下一个? [y/n]
```

### 有阻塞

```
📊 并行开发进度 @ 10:30:00
═══════════════════════════════════════════════════════════════════════

✅ feat-auth - done

⚠️ feat-dashboard
   状态: blocked | 阶段: complete
   进度: [████████████████████] 100% (5/5)
   ⚠️ 阻塞: Rebase 冲突: src/utils/helper.ts

═══════════════════════════════════════════════════════════════════════

⚠️ 有 feature 被阻塞

处理步骤:
1. cd ../OA_Tool-feat-dashboard
2. 解决 src/utils/helper.ts 中的冲突
3. git add . && git rebase --continue
4. /parallel-dev feat-dashboard --resume
```

## 错误处理

| 场景 | 检测 | 处理 |
|------|------|------|
| Feature Agent 崩溃 | status 不是 done 但 updated_at 过旧 | 标记 error，提示查看日志 |
| Worktree 不存在 | 目录检查失败 | 提示先运行 /start-feature |
| 启动脚本失败 | 脚本返回非零 | 显示错误信息 |

## 日志查看

```bash
# 查看实时日志
tail -f features/active-feat-auth/.log

# 查看最近事件
grep "^EVENT:" features/active-feat-auth/.log | tail -10

# 查看状态
cat features/active-feat-auth/.status
```

## 设计原则

1. **主 Agent 无状态**: 不依赖内存状态
2. **文件是真相**: 所有状态持久化在文件中
3. **可随时恢复**: 重新运行 /parallel-dev 即可
4. **上下文可控**: 只读取小的 .status 文件，不膨胀
5. **进程自治**: Feature Agent 完成后自动退出
