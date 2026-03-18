# Skill: cleanup-features

## 元信息

| 属性 | 值 |
|------|-----|
| 名称 | cleanup-features |
| 触发命令 | `/cleanup-features` |
| 优先级 | P1 (管理) |
| 依赖 | 无 |

## 功能描述

清理无效的 worktree 和不一致的状态，包括：
- 孤立的 worktree（存在但不在队列中）
- 丢失的 worktree（在队列中但实际不存在）
- 无效的目录引用

## 输入参数

| 参数名 | 类型 | 必需 | 默认值 | 描述 |
|--------|------|------|--------|------|
| auto | boolean | 否 | false | 自动清理，不询问 |
| dry_run | boolean | 否 | false | 只显示不执行 |

## 执行流程

```
┌─────────────────────────────────────────────────────────────────┐
│ Step 1: 收集信息                                                 │
│ - 读取 queue.yaml 获取记录的 worktree                           │
│ - 执行 git worktree list 获取实际的 worktree                    │
│ - 扫描 features/ 目录获取需求目录                               │
└─────────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────────┐
│ Step 2: 检测异常                                                 │
│ - orphaned_worktrees: 实际存在但未记录的 worktree               │
│ - missing_worktrees: 记录但实际不存在的 worktree                │
│ - orphaned_dirs: 目录存在但不在队列中                           │
│ - missing_dirs: 在队列中但目录不存在                            │
└─────────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────────┐
│ Step 3: 显示结果                                                 │
│ - 如果没有异常，显示"一切正常"                                   │
│ - 如果有异常，显示详情并询问处理方式                             │
└─────────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────────┐
│ Step 4: 执行清理（如果确认）                                     │
│ - 对于孤立 worktree: 询问是否删除                               │
│ - 对于丢失 worktree: 从队列中移除或标记为需要修复               │
│ - 对于孤立目录: 询问是否归档或删除                              │
│ - 对于丢失目录: 从队列中移除                                    │
└─────────────────────────────────────────────────────────────────┘
```

## 检测逻辑

### 孤立 Worktree

```python
actual_worktrees = git worktree list --porcelain | grep "worktree"
recorded_worktrees = queue.active[*].worktree

orphaned = actual_worktrees - recorded_worktrees
```

### 丢失 Worktree

```python
missing = recorded_worktrees - actual_worktrees
```

## 输出

### 一切正常

```
┌─────────────────────────────────────────────────────────────────┐
│ Cleanup Check                                                    │
├─────────────────────────────────────────────────────────────────┤
│ ✅ 一切正常                                                      │
│                                                                  │
│ Worktrees: 1 记录 / 1 实际                                       │
│ 需求目录: 3 记录 / 3 实际                                        │
└─────────────────────────────────────────────────────────────────┘
```

### 发现异常

```
┌─────────────────────────────────────────────────────────────────┐
│ Cleanup Check                                                    │
├─────────────────────────────────────────────────────────────────┤
│ ⚠️ 发现异常                                                      │
│                                                                  │
│ 孤立的 Worktrees (1):                                            │
│   ../OA_Tool-feat-old (不在队列中)                               │
│                                                                  │
│ 丢失的 Worktrees (1):                                            │
│   feat-dashboard: 记录为 ../OA_Tool-feat-dashboard 但不存在     │
│                                                                  │
│ 孤立的需求目录 (1):                                              │
│   active-feat-obsolete (不在队列中)                              │
└─────────────────────────────────────────────────────────────────┘

处理选项:
1. 删除孤立 worktree: ../OA_Tool-feat-old
2. 标记 feat-dashboard 为需要修复
3. 归档孤立目录 active-feat-obsolete

选择要执行的操作 (1,2,3/all/none):
```

### Dry Run 模式

```
用户: /cleanup-features --dry-run

Agent:
🔍 Dry Run 模式 - 以下是将执行的操作:

[删除] git worktree remove ../OA_Tool-feat-old
[更新] queue.yaml: 移除 feat-dashboard 的 worktree 记录
[移动] active-feat-obsolete → archive/

不会实际执行，使用 /cleanup-features 确认执行
```

## 清理操作

| 异常类型 | 操作选项 |
|----------|----------|
| 孤立 worktree | 删除 / 保留并添加到队列 |
| 丢失 worktree | 从队列移除 / 标记需要修复 |
| 孤立目录 (pending-*) | 归档 / 删除 / 添加到队列 |
| 孤立目录 (active-*) | 归档 / 删除 / 检查 worktree |

## 错误码

| 错误码 | 描述 |
|--------|------|
| GIT_ERROR | Git 操作失败 |
| PERMISSION_ERROR | 无权限删除文件 |

## 示例用法

### 示例 1: 检查并清理

```
用户: /cleanup-features

Agent: 发现 2 个异常...
       (显示详情)
       是否全部清理？(y/n)

用户: y

Agent: ✅ 清理完成
       - 删除 1 个孤立 worktree
       - 更新 1 条队列记录
```

### 示例 2: 自动清理

```
用户: /cleanup-features --auto

Agent: ✅ 自动清理完成
       - 删除 1 个孤立 worktree
       - 归档 1 个孤立目录
```

### 示例 3: 只检查不执行

```
用户: /cleanup-features --dry-run

Agent: 🔍 发现以下异常...
       (显示但不执行)
```

## 注意事项

1. 删除操作不可逆，建议先用 --dry-run
2. 孤立目录可能是手动创建的，谨慎处理
3. 清理后建议执行 /list-features 确认状态
