# Skill: start-feature

## 元信息

| 属性 | 值 |
|------|-----|
| 名称 | start-feature |
| 触发命令 | `/start-feature <id>` |
| 优先级 | P0 (核心) |
| 依赖 | new-feature |

## 功能描述

启动需求开发，包括：
- 检查并行限制
- 重命名需求目录（pending → active）
- 创建 Git 分支
- 创建 Worktree
- 更新调度队列

## 输入参数

| 参数名 | 类型 | 必需 | 默认值 | 描述 |
|--------|------|------|--------|------|
| id | string | 是 | - | 需求 ID (如 feat-auth) |

## 前置条件检查

```
┌─────────────────────────────────────────────────────────────────┐
│ 检查 1: 需求存在                                                 │
│ - 在 queue.yaml 的 pending 列表中查找 id                         │
│ - 如果不存在，返回 NOT_FOUND 错误                                │
└─────────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────────┐
│ 检查 2: 并行限制                                                 │
│ - 读取 config.yaml 的 max_concurrent                            │
│ - 统计 queue.yaml 的 active.count                               │
│ - 如果 active.count >= max_concurrent:                          │
│   返回 LIMIT_EXCEEDED 错误                                       │
└─────────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────────┐
│ 检查 3: 依赖满足                                                 │
│ - 检查该需求的 dependencies                                      │
│ - 验证所有依赖是否已完成（在 archive-log.yaml 中）               │
│ - 如果有未满足的依赖:                                            │
│   返回 DEPENDENCY_ERROR 错误                                     │
└─────────────────────────────────────────────────────────────────┘
```

## 执行流程

```
┌─────────────────────────────────────────────────────────────────┐
│ Step 1: 获取需求信息                                             │
│ - 从 queue.yaml pending 列表读取需求详情                         │
│ - 提取: name, priority, dependencies                            │
└─────────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────────┐
│ Step 2: 重命名目录                                               │
│ - mv features/pending-{id} features/active-{id}                 │
│ - 验证目录存在且权限正确                                         │
└─────────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────────┐
│ Step 3: 创建 Git 分支                                            │
│ - git checkout main                                              │
│ - git pull origin main (如果配置了远程)                          │
│ - git checkout -b {branch_prefix}/{slug}                        │
│ - branch_prefix 从 config.yaml 读取，默认 "feature"              │
│ - slug 从 id 提取 (feat-auth → auth)                            │
└─────────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────────┐
│ Step 4: 创建 Worktree                                            │
│ - 计算路径: {worktree_base}/{worktree_prefix}-{slug}            │
│   - worktree_base: 默认 ".."                                    │
│   - worktree_prefix: 默认项目名                                  │
│ - git worktree add {path} {branch}                              │
│ - 验证 worktree 创建成功                                         │
└─────────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────────┐
│ Step 5: 更新队列                                                 │
│ - 从 pending 列表移除该需求                                      │
│ - 添加到 active 列表:                                            │
│   {                                                             │
│     id, name, priority,                                         │
│     branch: "feature/auth",                                     │
│     worktree: "../OA_Tool-feat-auth",                           │
│     started: "2026-03-02T10:00:00"                              │
│   }                                                             │
│ - 更新 meta.last_updated                                        │
└─────────────────────────────────────────────────────────────────┘
```

## 输出

### 成功输出

```yaml
status: success
feature:
  id: feat-auth
  name: 用户认证
  branch: feature/auth
  worktree: ../OA_Tool-feat-auth

message: |
  🚀 需求 feat-auth 已启动！

  分支: feature/auth
  Worktree: ../OA_Tool-feat-auth

  开始开发:
    cd ../OA_Tool-feat-auth

  查看任务:
    cat features/active-feat-auth/task.md
```

### 失败输出

```yaml
status: error
error:
  code: LIMIT_EXCEEDED
  message: "已达并行上限 (2/2)"
  current_active:
    - feat-dashboard
    - feat-report
  suggestion: "请先完成现有需求，或修改 max_concurrent 配置"

# 或

status: error
error:
  code: NOT_FOUND
  message: "需求 'feat-auth' 不存在或不在待处理队列中"
  suggestion: "使用 /list-features 查看所有需求"

# 或

status: error
error:
  code: GIT_ERROR
  message: "创建分支失败: 分支 'feature/auth' 已存在"
  suggestion: "手动删除分支后重试"
```

## 错误码

| 错误码 | 描述 | 处理建议 |
|--------|------|----------|
| NOT_FOUND | 需求不存在 | 检查 ID 是否正确，使用 /list-features |
| LIMIT_EXCEEDED | 并行数已满 | 等待其他需求完成或修改配置 |
| DEPENDENCY_ERROR | 依赖未满足 | 先完成依赖的需求 |
| BRANCH_EXISTS | 分支已存在 | 删除旧分支或使用不同名称 |
| WORKTREE_ERROR | Worktree 创建失败 | 检查路径权限 |
| GIT_ERROR | Git 操作失败 | 检查 Git 状态 |

## 文件变更

| 文件 | 操作 | 变更内容 |
|------|------|----------|
| features/pending-{id}/ | 重命名 | → features/active-{id}/ |
| queue.yaml | 修改 | pending → active |
| Git | 创建 | 新分支 feature/{slug} |
| Git | 创建 | 新 worktree |

## Git 操作详情

```bash
# Step 3: 创建分支
git checkout main
git pull origin main  # 可选
git checkout -b feature/auth

# Step 4: 创建 worktree
git worktree add ../OA_Tool-feat-auth feature/auth

# 验证
git worktree list
# 应该看到:
# /OA_Tool                main
# /OA_Tool-feat-auth      feature/auth
```

## 依赖的配置

```yaml
# config.yaml
naming:
  branch_prefix: feature
  worktree_prefix: OA_Tool

paths:
  worktree_base: ..

git:
  remote: origin  # 可选
  auto_pull: true # 可选
```

## 示例用法

### 示例 1: 正常启动

```
用户: /start-feature feat-auth

Agent: 🚀 需求 feat-auth 已启动！
       cd ../OA_Tool-feat-auth
```

### 示例 2: 并行数已满

```
用户: /start-feature feat-auth

Agent: ❌ 已达并行上限 (2/2)

       当前活跃需求:
       - feat-dashboard (started 2h ago)
       - feat-report (started 1h ago)

       建议:
       1. 完成现有需求: /complete-feature feat-dashboard
       2. 或修改配置: /feature-config max_concurrent=3
```

### 示例 3: 依赖未满足

```
用户: /start-feature feat-export

Agent: ❌ 依赖未满足

       feat-export 依赖:
       - feat-auth (未完成)

       请先完成依赖的需求。
```

## 回滚策略

如果流程中途失败，需要回滚：

```
失败点                    回滚操作
─────────────────────────────────────────────
Step 2 目录重命名失败      无需回滚
Step 3 分支创建失败        无需回滚（分支未创建）
Step 4 worktree 创建失败   删除分支，重命名目录回 pending
Step 5 更新队列失败        删除 worktree，删除分支，重命名目录
```

## 注意事项

1. **分支命名冲突**: 如果分支已存在，提示用户手动处理
2. **Worktree 路径冲突**: 如果目录已存在，提示用户删除或使用其他路径
3. **Git 状态检查**: 确保主仓库没有未提交的变更
4. **远程同步**: 如果配置了远程，建议先 pull 最新代码
