---
description: 解除阻止的特性，允许其重新启动
---

# 解除阻止特性

解除被阻止的特性，将其移回 pending 列表。

## 参数

- `feature-id`: 要解除阻止的特性 ID（必需）

## 第 1 步：查找特性

在 `queue.yaml` 的 blocked 列表中定位特性：
- 按 ID 查找特性
- 如果未找到，报错
- 检查当前阻止状态

## 第 2 步：显示阻止信息

显示特性被阻止的原因：
- 阻止原因
- 阻止时间戳
- 阻止者
- 阻止持续时间

## 第 3 步：验证依赖

检查依赖是否已满足：
- 验证所有依赖都在 archive-log.yaml 中
- 检查阻止问题是否已解决
- 如果依赖仍未满足，发出警告

## 第 4 步：确认解除阻止

请求用户确认：
- 显示阻止信息
- 显示依赖状态
- 请求确认

## 第 5 步：更新队列

在 `queue.yaml` 中将特性从 blocked 移到 pending 列表：

```yaml
pending:
  - id: {id}
    name: {name}
    priority: {priority}
    size: {size}
    parent: {parent 或 null}
    children: {children 或 []}
    dependencies: {dependencies}
    created: {original_created}
    unblocked_at: {timestamp}
    previous_block: {original_block_reason}
```

## 第 6 步：检查自动启动

读取 `config.yaml`：
- 如果 `workflow.auto_start: true` 且 `active.count < max_concurrent`
- 提供立即启动特性的选项

## 输出格式

```
✅ 特性已解除阻止: {id}

特性: {name}
被阻止时长: {duration}
原原因: {reason}

状态:
  依赖: ✅ 已满足
  可以启动: ✅ 是

当前并行使用: 1/3

选项:
  [1] 立即启动特性 (/start-feature {id})
  [2] 加入队列稍后启动
  [3] 查看特性详情
```

## 示例

```
/unblock-feature feat-upload

输出:
🔓 特性已解除阻止: feat-upload

特性: 文件上传
被阻止时长: 2 周
原原因: "等待存储基础设施"

状态:
  依赖: ✅ 全部满足
  Storage feat-storage: ✅ 已完成
  可以启动: ✅ 是

选项:
  [1] 立即启动特性
  [2] 加入队列
```
