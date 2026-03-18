---
description: 阻止特性，带有原因，防止其被启动
---

# 阻止特性

阻止一个待处理的特性，直到解除阻止前无法启动。

## 参数

- `feature-id`: 要阻止的特性 ID（必需）
- `--reason=<text>`: 阻止原因（必需）

## 第 1 步：查找特性

在 `queue.yaml` 中定位特性：
- 检查 pending 列表
- 如果未找到，检查 active 列表（警告用户）
- 如果在 blocked 列表中，报错（已阻止）

## 第 2 步：验证阻止原因

确保阻止原因已提供且有意义的：
- 不为空
- 不太模糊（如 "就是因为"）
- 应该尽可能可操作

## 第 3 步：更新队列

在 `queue.yaml` 中将特性从 pending 移到 blocked 列表：

```yaml
blocked:
  - id: {id}
    name: {name}
    priority: {priority}
    size: {size}
    parent: {parent 或 null}
    children: {children 或 []}
    dependencies: {dependencies}
    blocked_at: {timestamp}
    blocked_by: {user}
    reason: {reason}
```

## 第 4 步：处理子特性

如果特性有子特性：
- 选项 1：自动阻止所有子特性
- 选项 2：警告用户但不阻止子特性
- 选项 3：询问用户如何处理

## 第 5 步：更新受影响的特性

如果有活跃特性依赖此特性：
- 警告用户
- 提供阻止依赖特性的选项
- 或在依赖特性中记录

## 输出格式

```
🚫 特性已阻止: {id}

特性: {name}
原因: {reason}

阻止时间: {timestamp}
阻止者: {user}

受影响的特性:
  - feat-child-1 (依赖 {id})
  - feat-child-2 (依赖 {id})

选项:
  [1] 同时阻止依赖特性
  [2] 保持依赖特性活跃
  [3] 查看依赖特性详情
```

## 示例

```
/block-feature feat-upload --reason "等待存储基础设施完成"

/block-feature feat-auth --reason "安全审查待定，等待安全团队批准"

/block-feature feat-payment --reason "支付网关 API 尚未可用，预计 2 周"
```
