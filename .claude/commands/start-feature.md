---
description: 启动特性开发，创建 Git 分支和 worktree
---

# 启动特性开发

启动指定特性的开发工作。按照以下步骤执行：

## 参数

- `feature-id`: 特性 ID（必需）

## 第 1 步：预检查

**检查 1：特性存在**
- 在 `queue.yaml` 的 pending 列表中查找特性
- 如果未找到，返回 NOT_FOUND 错误
- 如果在 blocked 列表中，返回 BLOCKED 错误

**检查 2：并行限制**
- 读取 `config.yaml` 的 max_concurrent
- 统计 `queue.yaml` 中的 active 特性
- 如果 `active.count >= max_concurrent`：返回 LIMIT_EXCEEDED 错误

**检查 3：依赖已满足**
- 检查特性的 dependencies 字段
- 验证所有依赖都已完成（在 archive-log.yaml 中）
- 如果有未满足的依赖，返回 DEPENDENCY_ERROR

**检查 4：父特性状态（针对子特性）**
- 如果特性有 parent，检查父特性是否 active 或 completed
- 如果父特性是 pending/blocked：返回 PENDING_DEPENDENCY 错误

**检查 5：子特性状态（针对父特性）**
- 如果特性有 children，检查子特性状态
- 如果任何子特性是 active，返回 CHILD_ACTIVE 错误

## 第 2 步：获取特性信息

从 `queue.yaml` pending 列表读取：
- name, priority, dependencies, parent, children, size

## 第 3 步：重命名目录

```bash
mv features/pending-{id} features/active-{id}
```

## 第 4 步：创建 Git 分支

从 `config.yaml` 获取配置：
- project.main_branch（默认 "main"）
- git.remote（默认 "origin"）

**创建分支：**
```bash
git checkout {main_branch}
git pull {remote} {main_branch}
git checkout -b feature/{slug}
```

分支名格式：`{branch_prefix}/{slug}`

## 第 5 步：创建 Worktree

```bash
git checkout {main_branch}
git worktree add ../{project}-{slug} feature/{slug}
```

Worktree 路径：`{worktree_base}/{worktree_prefix}-{slug}`

## 第 6 步：更新队列

更新 `feature-workflow/queue.yaml`：
- 从 pending 列表移除
- 添加到 active 列表，包含 branch 和 worktree 信息

## 输出格式

```
🚀 特性 {id} 已启动！

分支: feature/{slug}
worktree: ../{project}-{slug}
大小: {size}
父特性: {parent 或 "无"}
子特性: {children 或 "无"}

开始开发:
  cd ../{project}-{slug}

查看任务:
  cat features/active-{id}/task.md
```

## 错误处理

| 错误 | 描述 | 解决方案 |
|------|------|---------|
| NOT_FOUND | 特性不在 pending 列表 | 检查 ID，使用 list-features |
| BLOCKED | 特性被阻止 | 检查原因，使用 unblock-feature |
| LIMIT_EXCEEDED | 达到并行限制 | 完成活跃特性或增加限制 |
| DEPENDENCY_ERROR | 依赖未满足 | 先完成依赖的特性 |
| PENDING_DEPENDENCY | 父特性未启动 | 先启动父特性 |
| CHILD_ACTIVE | 子特性仍在活跃 | 等待子特性完成 |
