# Workflow: auto-schedule

## 元信息

| 属性 | 值 |
|------|-----|
| 名称 | auto-schedule |
| 触发方式 | 自动触发 / 手动调用 |
| 手动命令 | `/auto-schedule` |
| 类型 | 自动化工作流 |
| 描述 | 自动调度待处理需求 |

## 功能描述

根据配置和队列状态，自动启动待处理需求。

## 触发条件

### 自动触发

| 事件 | 触发条件 |
|------|----------|
| /new-feature 完成 | auto_start=true 且有空闲槽位 |
| /complete-feature 完成 | auto_start=true 且 pending 不为空 |
| /unblock-feature 完成 | auto_start=true 且有空闲槽位 |
| /feature-config 修改 max_concurrent | 增加了并行数 |

### 手动触发

```
/auto-schedule
/auto-schedule --dry-run
```

## 调度算法

```
┌─────────────────────────────────────────────────────────────────┐
│                      调度算法                                    │
└─────────────────────────────────────────────────────────────────┘

function auto_schedule():
  config = read_config()
  queue = read_queue()

  while queue.active.length < config.max_concurrent:

    # 1. 检查 pending 是否为空
    if queue.pending is empty:
      log("没有待处理的需求")
      break

    # 2. 获取最高优先级的需求
    candidates = sort_by_priority(queue.pending)
    next = candidates[0]

    # 3. 检查依赖
    if next.dependencies:
      unmet = check_dependencies(next.dependencies)
      if unmet:
        # 移到 blocked
        move_to_blocked(next, reason=f"依赖未满足: {unmet}")
        continue  # 继续检查下一个

    # 4. 启动需求
    result = start_feature(next.id)
    if result.success:
      log(f"已启动: {next.id}")
    else:
      log(f"启动失败: {result.error}")
      break

  return {
    active_count: queue.active.length,
    started: [...]
  }
```

## 优先级排序规则

1. **主要排序**: priority 降序（数字越大越优先）
2. **次要排序**: created 升序（先创建的优先）

```
示例:
  feat-a: priority=90, created=2026-03-01
  feat-b: priority=90, created=2026-03-02  ← feat-a 先
  feat-c: priority=80                      ← 最后
```

## 依赖检查

```python
def check_dependencies(dependencies):
  """
  检查依赖是否都已满足

  Returns:
    [] 如果全部满足
    [未满足的依赖列表] 如果有不满足的
  """
  archive = read_archive_log()
  unmet = []

  for dep_id in dependencies:
    if dep_id not in archive.archived:
      unmet.append(dep_id)

  return unmet
```

## 执行流程

```
┌─────────────────────────────────────────────────────────────────┐
│ Step 1: 读取状态                                                 │
│ - 读取 config.yaml                                              │
│ - 读取 queue.yaml                                               │
│ - 读取 archive-log.yaml (用于依赖检查)                          │
└─────────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────────┐
│ Step 2: 计算可用槽位                                             │
│ - available = max_concurrent - active.count                     │
│ - 如果 available <= 0，退出                                     │
└─────────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────────┐
│ Step 3: 遍历 pending 队列                                        │
│ - 按 priority 排序                                              │
│ - 对每个需求:                                                    │
│   - 检查依赖                                                     │
│   - 如果依赖未满足 → 移到 blocked                               │
│   - 如果依赖满足 → 加入启动列表                                 │
│ - 直到启动列表满或 pending 为空                                  │
└─────────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────────┐
│ Step 4: 执行启动                                                 │
│ - 对启动列表中的每个需求:                                        │
│   - 调用 start-feature skill                                   │
│   - 记录结果                                                     │
└─────────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────────┐
│ Step 5: 报告结果                                                 │
│ - 显示已启动的需求                                               │
│ - 显示被阻塞的需求                                               │
│ - 显示仍在等待的需求                                             │
└─────────────────────────────────────────────────────────────────┘
```

## 输出

### 有需求被启动

```yaml
status: scheduled
started:
  - id: feat-dashboard
    priority: 80
    worktree: ../OA_Tool-feat-dashboard

blocked:
  - id: feat-export
    reason: "依赖 feat-auth 未完成"

remaining:
  - feat-report (priority 70)

message: |
  🚀 自动调度完成

  已启动:
  - feat-dashboard → ../OA_Tool-feat-dashboard

  被阻塞:
  - feat-export (依赖未满足)

  等待中: 1
```

### 无需调度

```yaml
status: no_action
reason: "没有空闲槽位"
active_count: 2
max_concurrent: 2

message: |
  ℹ️ 当前已达并行上限 (2/2)

  活跃需求:
  - feat-auth
  - feat-dashboard
```

### Dry Run 模式

```
用户: /auto-schedule --dry-run

Agent:
🔍 Dry Run - 以下是将执行的操作:

[启动] feat-dashboard (priority 80)
  → 分支: feature/dashboard
  → worktree: ../OA_Tool-feat-dashboard

[阻塞] feat-export
  → 原因: 依赖 feat-auth 未完成

不会实际执行
```

## 配置选项

```yaml
# config.yaml
parallelism:
  max_concurrent: 2

workflow:
  auto_start: true           # 是否在触发事件后自动调度
  check_dependencies: true   # 是否检查依赖
  retry_on_failure: false    # 启动失败时是否重试
```

## 示例场景

### 场景 1: 创建需求后自动启动

```
用户: /new-feature 用户认证 --priority=90

Agent: ✅ 需求 feat-auth 已创建

       检查自动调度...
       当前活跃: 0/2
       🚀 自动启动 feat-auth

       cd ../OA_Tool-feat-auth
```

### 场景 2: 完成后自动启动下一个

```
用户: /complete-feature feat-auth

Agent: ✅ feat-auth 已完成

       检查自动调度...
       当前活跃: 0/2
       pending: feat-dashboard (80), feat-report (70)
       🚀 自动启动 feat-dashboard
```

### 场景 3: 依赖阻塞

```
用户: /complete-feature feat-auth

Agent: ✅ feat-auth 已完成

       检查自动调度...
       当前活跃: 0/2

       检查 feat-export: 依赖 feat-dashboard (未完成)
       → 移到 blocked

       检查 feat-dashboard: 无依赖
       🚀 自动启动 feat-dashboard
```

### 场景 4: 达到并行上限

```
用户: /new-feature 通知功能 --priority=60

Agent: ✅ 需求 feat-notification 已创建

       检查自动调度...
       当前活跃: 2/2 (已达上限)

       feat-notification 已加入等待队列
       位置: #3 (priority 60)
```

## 注意事项

1. **依赖循环检测**: 如果 A 依赖 B，B 依赖 A，两者都会被阻塞
2. **优先级动态调整**: 可以在创建后修改 priority 影响排序
3. **手动干预**: 可以使用 /block-feature 手动阻塞某个需求
4. **配置变更**: 修改 max_concurrent 会立即触发重新调度
