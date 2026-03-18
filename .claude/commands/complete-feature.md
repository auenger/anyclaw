---
description: 完成特性，提交代码、合并到主分支、清理并归档
---

# 完成特性

提交更改、合并到主分支、清理 worktree 并归档文档。按照以下步骤执行：

## 参数

- `feature-id`: 要完成的特性 ID（必需）
- `--skip-verify`: 跳过验证步骤（谨慎使用）
- `--keep-worktree`: 完成后保留 worktree（用于调试）

## 第 1 步：预检查

- 验证特性在 active 列表中
- 检查所有任务已完成（除非 --skip-verify）
- 验证测试通过（除非 --skip-verify）

## 第 2 步：审查更改

切换到 worktree 并显示：
- 修改的文件
- 新增的文件
- 删除的文件
- Diff 摘要

在继续之前请求确认。

## 第 3 步：提交更改

在 worktree 中：
```bash
git add .
git commit -m "feat({id}): {feature_name}

{detailed_description}"
```

提交消息格式：
```
feat({id}): {feature_name}

{detailed_description}
```

## 第 4 步：合并到主分支

切换到主分支并合并：
```bash
cd {repo_path}
git checkout {main_branch}
git merge feature/{slug} --no-ff
```

## 第 5 步：清理

**删除 worktree：**
```bash
git worktree remove ../{project}-{slug}
```

**删除特性分支：**
```bash
git branch -d feature/{slug}
```

**归档特性：**
```bash
mv features/active-{id} features/archive/done-{id}
```

## 第 6 步：更新队列

更新 `feature-workflow/queue.yaml`：
- 从 active 列表移除
- 添加到 archive-log.yaml

## 第 7 步：生成完成报告

输出工作摘要。

## 输出格式

```
🎉 特性完成: {id}

摘要:
  名称: {feature_name}
  耗时: {time_from_start}
  提交数: {commit_count}
  修改文件: {file_count}

Git:
  分支: feature/{slug}
  合并到: {main_branch}
  提交: {commit_hash}

归档:
  位置: features/archive/done-{id}

下一个特性:
  - {next_feature_1} (优先级: {p1})
  - {next_feature_2} (优先级: {p2})

是否自动启动下一个特性？(y/n)
```

## 回滚策略

如果合并后完成失败：
- 特性在队列中保持完成状态
- Worktree 保留以供检查
- 用户可以手动清理

如果合并前完成失败：
- Worktree 保留
- 特性保持 active 状态
- 用户可以修复并重试
