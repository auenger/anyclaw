---
description: 清理旧的或已完成的特性数据，管理磁盘空间
---

# 清理特性

清理旧的特性数据、归档特性，并管理 feature workflow 系统使用的磁盘空间。

## 参数

- `--older-than=<days>`: 清理超过指定天数的特性
- `--keep-last=<n>`: 只保留最近 N 个已完成的特性
- `--dry-run`: 显示将要删除的内容而不实际删除
- `--confirm`: 跳过确认提示

## 第 1 步：扫描特性数据

扫描可清理的数据：
- `features/archive/done-*` 目录
- 父目录中的旧 worktree
- `archive-log.yaml` 中的归档数据

## 第 2 步：计算大小

计算磁盘空间使用：
- 每个归档特性的大小
- 所有归档特性的总大小
- 旧 worktree 的大小

## 第 3 步：应用过滤

根据参数应用过滤：
- `--older-than`: 只超过 N 天的特性
- `--keep-last`: 只保留最近 N 个特性
- 组合：保留超过阈值且最近 N 个

## 第 4 步：预览删除

显示将要删除的内容：
- 要删除的特性列表
- 可释放的总大小
- 确认提示（除非 --confirm）

## 第 5 步：执行清理

如果确认：
1. 删除归档特性目录
2. 删除旧 worktree
3. 更新 archive-log.yaml
4. 更新 queue.yaml 元数据

## 输出格式（Dry Run）

```
🧹 特性清理预览

扫描特性: 15
匹配过滤: 8

将要删除的特性:
  ┌──────────────┬─────────────┬──────────┬────────────┐
  │ ID           │ 完成时间    │ 大小     │ 时长       │
  ├──────────────┼─────────────┼──────────┼────────────┤
  │ feat-old-1   │ 2024-01-15  │ 2.3 MB   │ 60 天      │
  │ feat-old-2   │ 2024-02-01  │ 1.8 MB   │ 45 天      │
  │ feat-old-3   │ 2024-02-10  │ 3.1 MB   │ 35 天      │
  └──────────────┴─────────────┴──────────┴────────────┘

可释放空间总计: 7.2 MB

将要删除的 Worktree:
  - ../AnyClaw-feat-old-1 (2.3 MB)
  - ../AnyClaw-feat-old-2 (1.8 MB)

Worktree 空间总计: 4.1 MB

总计: 11.3 MB

这是 dry run。不会进行任何更改。
使用 --confirm 实际删除这些特性。
```

## 安全特性

1. **从不删除活跃特性**
2. **从不删除待处理特性**
3. **除非 --confirm 否则总是显示预览**
4. **保留最近 5 个特性的最低限度**
5. **清理前备份 archive-log**

## 示例

```
/cleanup-features --dry-run --older-than=30

/cleanup-features --confirm --older-than=60

/cleanup-features --confirm --keep-last=20

/cleanup-features --confirm --keep-last=10 --older-than=30
```
