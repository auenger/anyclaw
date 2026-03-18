# Skill: block-feature

## 元信息

| 属性 | 值 |
|------|-----|
| 名称 | block-feature |
| 触发命令 | `/block-feature <id> [reason]` |
| 优先级 | P1 (管理) |
| 依赖 | 无 |

## 功能描述

阻塞某个需求，使其不会被自动调度。常用于：
- 等待依赖完成
- 外部因素阻塞（如 API 未就绪）
- 临时暂停开发

## 输入参数

| 参数名 | 类型 | 必需 | 默认值 | 描述 |
|--------|------|------|--------|------|
| id | string | 是 | - | 需求 ID |
| reason | string | 否 | "手动阻塞" | 阻塞原因 |

## 前置条件检查

```
┌─────────────────────────────────────────────────────────────────┐
│ 检查 1: 需求状态                                                 │
│ - 需求必须在 pending 或 blocked 列表中                          │
│ - 不能阻塞 active 状态的需求                                    │
└─────────────────────────────────────────────────────────────────┘
```

## 执行流程

```
┌─────────────────────────────────────────────────────────────────┐
│ Step 1: 检查需求状态                                             │
│ - 查找需求在 queue.yaml 中的位置                                │
│ - 如果在 active，返回错误                                       │
│ - 如果已在 blocked，更新原因                                    │
└─────────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────────┐
│ Step 2: 更新队列                                                 │
│ - 从 pending 移到 blocked                                       │
│ - 记录 reason                                                   │
│ - 更新 meta.last_updated                                        │
└─────────────────────────────────────────────────────────────────┘
```

## 输出

### 成功输出

```yaml
status: success
feature:
  id: feat-report
  previous_status: pending
  current_status: blocked

message: |
  🔒 需求 feat-report 已阻塞

  原因: 等待 API 接口就绪

  解除阻塞: /unblock-feature feat-report
```

### 失败输出

```yaml
status: error
error:
  code: CANNOT_BLOCK_ACTIVE
  message: "无法阻塞进行中的需求 feat-auth"
  suggestion: |
    请先完成或放弃该需求:
    /complete-feature feat-auth
    或
    /abandon-feature feat-auth
```

## 错误码

| 错误码 | 描述 | 处理建议 |
|--------|------|----------|
| NOT_FOUND | 需求不存在 | 检查 ID |
| CANNOT_BLOCK_ACTIVE | 无法阻塞活跃需求 | 先完成或放弃 |
| ALREADY_BLOCKED | 已经在阻塞列表 | 可更新原因 |

## 示例用法

```
用户: /block-feature feat-report 等待第三方API

Agent: 🔒 需求 feat-report 已阻塞
       原因: 等待第三方API
```

## 注意事项

1. 不影响 active 状态的需求
2. 阻塞的需求不会被自动调度
3. 可以重复执行更新阻塞原因
