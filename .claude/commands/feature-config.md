---
description: 管理 feature workflow 配置设置
---

# 管理配置

查看和修改 feature workflow 配置设置。

## 参数

- `--show`: 显示当前配置
- `--set=<key=value>`: 设置配置值
- `--reset`: 重置为默认配置

## 第 1 步：加载配置

读取 `feature-workflow/config.yaml`

## 第 2 步：显示或修改

**如果 --show：**
显示所有配置值及描述

**如果 --set：**
- 验证键
- 验证值
- 更新配置
- 保存更改

**如果 --reset：**
- 恢复默认配置
- 保存更改

## 第 3 步：更新相关文件

如果配置更改影响：
- 队列结构 → 更新 queue.yaml
- 模板路径 → 验证模板存在
- Git 设置 → 验证 git 配置

## 配置选项

| 键 | 类型 | 默认值 | 描述 |
|----|------|--------|------|
| `project.name` | string | - | 项目名称 |
| `project.main_branch` | string | "main" | 主分支名称 |
| `git.remote` | string | "origin" | Git 远程名称 |
| `git.branch_prefix` | string | "feature" | 分支名称前缀 |
| `workflow.auto_start` | boolean | false | 自动启动特性 |
| `workflow.max_concurrent` | number | 3 | 最大活跃特性数 |
| `worktree.base` | string | ".." | Worktree 基础路径 |
| `worktree.prefix` | string | 项目名称 | Worktree 前缀 |
| `feature.id_prefix` | string | "feat" | 特性 ID 前缀 |
| `feature.default_priority` | number | 50 | 默认优先级 |

## 输出格式（显示配置）

```
┌─────────────────────────────────────────────────────────────────┐
│                    Feature Workflow 配置                         │
├─────────────────────────────────────────────────────────────────┤
│                                                                  │
│  Project:                                                        │
│    name: AnyClaw                                                │
│    main_branch: main                                            │
│                                                                  │
│  Git:                                                            │
│    remote: origin                                               │
│    branch_prefix: feature                                       │
│                                                                  │
│  Workflow:                                                       │
│    auto_start: false                                           │
│    max_concurrent: 3                                            │
│                                                                  │
│  Worktree:                                                       │
│    base: ..                                                     │
│    prefix: AnyClaw                                              │
│                                                                  │
│  Feature:                                                        │
│    id_prefix: feat                                              │
│    default_priority: 50                                         │
│                                                                  │
└─────────────────────────────────────────────────────────────────┘
```

## 示例

```
/feature-config --show

/feature-config --set=workflow.max_concurrent=5

/feature-config --set=workflow.auto_start=true

/feature-config --set=feature.default_priority=70

/feature-config --reset
```
