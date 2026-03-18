# Skill: unblock-feature

## 元信息

| 属性 | 值 |
|------|-----|
| 名称 | unblock-feature |
| 触发命令 | `/unblock-feature <id>` |
| 优先级 | P1 (管理) |
| 依赖 | block-feature |

## 功能描述

解除需求的阻塞状态，使其重新进入待调度队列。

## 输入参数

| 参数名 | 类型 | 必需 | 默认值 | 描述 |
|--------|------|------|--------|------|
| id | string | 是 | - | 需求 ID |

## 执行流程

```
┌─────────────────────────────────────────────────────────────────┐
│ Step 1: 检查需求状态                                             │
│ - 在 queue.yaml 的 blocked 列表中查找                           │
│ - 如果不存在，返回错误                                           │
└─────────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────────┐
│ Step 2: 更新队列                                                 │
│ - 从 blocked 移到 pending                                       │
│ - 按 priority 重新排序 pending 列表                              │
│ - 更新 meta.last_updated                                        │
└─────────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────────┐
│ Step 3: 检查自动启动                                             │
│ - 读取 config.yaml                                              │
│ - 如果 auto_start=true 且有空闲槽位:                            │
│   - 检查该需求是否为最高优先级                                   │
│   - 如果是，调用 start-feature                                  │
└─────────────────────────────────────────────────────────────────┘
```

## 输出

### 成功输出

```yaml
status: success
feature:
  id: feat-report
  previous_status: blocked
  current_status: pending | started

message: |
  🔓 需求 feat-report 已解除阻塞

  状态: pending (等待调度)

  # 如果自动启动:
  🚀 已自动启动！
  cd ../OA_Tool-feat-report
```

### 失败输出

```yaml
status: error
error:
  code: NOT_BLOCKED
  message: "需求 feat-report 不在阻塞列表中"
```

## 错误码

| 错误码 | 描述 |
|--------|------|
| NOT_FOUND | 需求不存在 |
| NOT_BLOCKED | 需求不在阻塞列表 |

## 示例用法

```
用户: /unblock-feature feat-report

Agent: 🔓 需求 feat-report 已解除阻塞
       状态: pending
```

## 注意事项

1. 解除后按优先级排序，不保证立即启动
2. 如果 auto_start=true 且有空闲槽位，可能立即启动
