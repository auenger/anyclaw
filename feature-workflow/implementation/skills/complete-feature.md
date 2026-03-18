# Skill: complete-feature

## 元信息

| 属性 | 值 |
|------|-----|
| 名称 | complete-feature |
| 触发命令 | `/complete-feature <id>` |
| 优先级 | P0 (核心) |
| 依赖 | verify-feature |

## 功能描述

完成需求开发，包括：
- 检查 checklist 完成情况
- 在 worktree 中提交代码
- 合并到 main 分支
- 创建归档 tag
- 删除 worktree 和分支
- 归档需求文档
- 更新归档日志
- 触发自动调度

## 输入参数

| 参数名 | 类型 | 必需 | 默认值 | 描述 |
|--------|------|------|--------|------|
| id | string | 是 | - | 需求 ID (如 feat-auth) |
| message | string | 否 | 自动生成 | Git 提交信息 |
| skip_checklist | boolean | 否 | false | 跳过 checklist 检查 |
| no_merge | boolean | 否 | false | 只提交不合并 |
| auto_push | boolean | 否 | false | 合并后自动 push |
| keep_branch | boolean | 否 | false | 保留分支（不删除） |

## 前置条件检查

```
┌─────────────────────────────────────────────────────────────────┐
│ 检查 1: 需求状态                                                 │
│ - 在 queue.yaml 的 active 列表中查找 id                         │
│ - 如果不存在，返回 NOT_FOUND 错误                                │
└─────────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────────┐
│ 检查 2: Worktree 存在                                            │
│ - 验证 worktree 路径是否存在                                     │
│ - 验证是有效的 git worktree                                     │
└─────────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────────┐
│ 检查 3: Checklist 完成                                           │
│ - 读取 features/active-{id}/checklist.md                        │
│ - 解析未完成的检查项 (未被勾选的 - [ ])                          │
│ - 如果有未完成项且 skip_checklist=false:                        │
│   警告并确认是否继续                                             │
└─────────────────────────────────────────────────────────────────┘
```

## 执行流程

```
┌─────────────────────────────────────────────────────────────────┐
│ Step 1: 获取需求信息                                             │
│ - 从 queue.yaml active 列表读取需求详情                         │
│ - 提取: name, branch, worktree, started                         │
│ - 计算开发时长                                                   │
└─────────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────────┐
│ Step 2: 检查 Checklist                                           │
│ - 读取 checklist.md                                              │
│ - 解析所有 - [ ] 和 - [x] 项                                    │
│ - 统计未完成项                                                   │
│ - 如果有未完成:                                                  │
│   显示未完成列表                                                 │
│   询问用户是否继续                                               │
└─────────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────────┐
│ Step 3: 提交代码                                                 │
│ - cd {worktree}                                                  │
│ - git add .                                                      │
│ - git status (显示变更)                                          │
│ - 如果没有变更，警告用户                                         │
│ - git commit -m "feat({id}): {name}" 或用户指定的 message        │
│ - 记录 commit hash                                               │
└─────────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────────┐
│ Step 4: 合并到 Main                                              │
│ - git checkout main                                              │
│ - git pull origin main (如果配置)                                │
│ - git merge {branch} --no-ff -m "Merge {branch}: {name}"        │
│ - 处理合并冲突（如有）                                           │
│ - 记录 merge commit hash                                         │
│ - 如果 auto_push=true: git push origin main                     │
└─────────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────────┐
│ Step 5: 创建归档 Tag                                             │
│ - 生成 tag 名称: {prefix}-{id}-{date}                           │
│   例: feat-auth-20260302                                        │
│ - git tag -a {tag_name} -m "Archive: {name}"                    │
│ - 如果配置了远程: git push origin {tag_name}                    │
│ - 记录 tag 名称                                                  │
└─────────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────────┐
│ Step 6: 复制需求文档到归档目录 (在清理 Worktree 之前!)            │
│                                                                 │
│ ⭐ 关键步骤 - 必须在删除 worktree 之前执行!                        │
│                                                                 │
│ - 创建归档目录: features/archive/done-{id}-{date}/               │
│ - 复制所有标准文档:                                              │
│   - cp spec.md features/archive/done-{id}-{date}/                │
│   - cp task.md features/archive/done-{id}-{date}/                │
│   - cp checklist.md features/archive/done-{id}-{date}/           │
│ - 复制 evidence 目录 (如果存在):                                 │
│   - cp -r evidence features/archive/done-{id}-{date}/            │
│                                                                 │
│ 为什么这一步很关键:                                              │
│ - worktree 包含代码变更，但需求文档在 active 目录中               │
│ - 如果在复制之前删除 worktree，这些文档将丢失                     │
│ - verify-feature 产生的 evidence 必须被保留                       │
└─────────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────────┐
│ Step 7: 清理 Worktree 和分支                                     │
│ - git worktree remove {worktree}                                │
│ - git branch -d {branch}                                        │
│ - 验证清理成功                                                   │
│                                                                 │
│ 注意: 分支已通过 tag 归档，可随时恢复                            │
└─────────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────────┐
│ Step 8: 验证归档完整性                                           │
│                                                                 │
│ ⚠️ 归档完整性检查 - 记录警告但不中断流程                          │
│                                                                 │
│ 必需文件检查:                                                    │
│ - features/archive/done-{id}-{date}/spec.md        ✅ 必需       │
│ - features/archive/done-{id}-{date}/task.md        ✅ 必需       │
│ - features/archive/done-{id}-{date}/checklist.md   ✅ 必需       │
│ - features/archive/done-{id}-{date}/archive-meta.yaml ✅ 必需    │
│                                                                 │
│ 如果缺少任何必需文件:                                            │
│ - ⚠️ 记录警告但继续执行（文件可从 git tag 恢复）                  │
│ - 在 archive-meta.yaml 中记录缺失文件                             │
│ - 提示用户稍后验证归档完整性                                       │
│ - 不要中断流程                                                    │
└─────────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────────┐
│ Step 9: 更新 spec.md (在归档目录中)                                  │
│ - 读取 features/archive/done-{id}-{date}/spec.md                │
│ - 添加合并记录部分:                                              │
│   - 合并时间                                                     │
│   - merge commit                                                 │
│   - 归档 tag                                                     │
│   - 开发统计                                                     │
│   - 验证证据链接 (如有)                                          │
└─────────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────────┐
│ Step 10: 创建 archive-meta.yaml                                   │
│ - 在归档目录创建元数据文件                                       │
│ - 包含: id, name, completed, branch, commit, tag, evidence        │
│ - 包含冲突记录 (如有)                                             │
│ - 包含变更文件列表                                                 │
└─────────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────────┐
│ Step 11: 更新归档日志                                              │
│ - 更新 features/archive/archive-log.yaml:                      │
│   {id, name, completed, tag, merge_commit, stats}              │
│ - 包含冲突记录和验证摘要                                            │
└─────────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────────┐
│ Step 12: 更新队列                                                 │
│ - 从 active 列表移除该需求                                      │
│ - 更新 meta.last_updated                                        │
└─────────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────────┐
│ Step 13: 清理 Active 目录 (增强验证)                                │
│                                                                 │
│ ⚠️ 确保完全清理，避免残留                                            │
│                                                                 │
│ 执行步骤:                                                         │
│ 1. 删除 .status 和 .log 文件                                      │
│ 2. 删除整个 features/active-{id} 目录                              │
│ 3. 验证删除结果:                                                  │
│    - 如果目录仍存在:                                              │
│      ⚠️ 记录警告                                                  │
│      尝试强制删除: rm -rf                                          │
│      如果仍失败，提示用户手动清理                                   │
│    - 如果目录已删除:                                              │
│      ✅ 确认清理成功                                               │
│                                                                 │
│ 4. 验证 worktree 清理:                                            │
│    - 运行: git worktree list                                      │
│    - 确认 worktree 路径不在列表中                                  │
│    - 如果仍存在:                                                  │
│      git worktree remove --force {path}                           │
│                                                                 │
│ 5. 验证分支清理:                                                  │
│    - 运行: git branch -a                                          │
│    - 确认 feature 分支已删除                                       │
│    - 如果仍存在:                                                  │
│      git branch -D {branch}                                      │
└─────────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────────┐
│ Step 14: 自动调度 (增强版)                                          │
│                                                                 │
│ ⚠️ 支持连续开发模式                                    │
│                                                                 │
│ 1. 读取 config.yaml 的 workflow.auto_start_next 配置              │
│    - 如果 false，跳过自动调度                                  │
│                                                                 │
│ 2. 读取 queue.yaml 的 pending 列表                              │
│    - 如果为空，显示完成汇总并退出                           │
│                                                                 │
│ 3. 取 priority 最高的 feature (pending 列表第一个)                   │
│                                                                 │
│ 4. 检查依赖是否满足:                                              │
│    - 读取 features/pending-{id}/spec.md 或从 queue.yaml               │
│    - 检查 dependencies 字段                              │
│    - 验证所有依赖是否在 completed 列表中                       │
│    - 如果依赖不满足，尝试下一个 pending feature                        │
│                                                                 │
│ 5. 如果找到可启动的 feature:                                  │
│    - 调用 /start-feature {id} 创建 worktree                          │
│    - 返回 feature 信息供调用方使用                                    │
│                                                                 │
│ 6. 返回调度结果:                                              │
│    - auto_started: {feature_id} 或 null                              │
│    - message: 说明信息                                              │
└─────────────────────────────────────────────────────────────────┘
```

## 输出

### 成功输出

```yaml
status: success
feature:
  id: feat-auth
  name: 用户认证
  merged: true
  tag: feat-auth-20260302
  archived_to: features/archive/done-feat-auth

git:
  merge_commit: abc123def456
  tag: feat-auth-20260302
  branch_deleted: feature/auth
  worktree_deleted: ../OA_Tool-feat-auth

stats:
  duration: "2h 30m"
  commits: 5
  files_changed: 8

next:
  auto_started: feat-dashboard | null

message: |
  ✅ 需求 feat-auth 已完成！

  ┌───────────────────────────────────────────┐
  │ 完成报告                                   │
  ├───────────────────────────────────────────┤
  │ 提交: feat(feat-auth): 用户认证            │
  │ 合并: feature/auth → main                  │
  │ 归档: feat-auth-20260302 (tag)             │
  │                                           │
  │ 📊 统计:                                   │
  │ - 开发时长: 2h 30m                         │
  │ - 提交数: 5                                │
  │ - 变更文件: 8                              │
  │                                           │
  │ 🗑️ 已清理:                                 │
  │ - worktree: 已删除                         │
  │ - branch: 已删除 (可通过 tag 恢复)         │
  └───────────────────────────────────────────┘
  📁 归档位置: features/archive/done-feat-auth

  {{#if auto_started}}
  🚀 自动启动下一个需求: {{auto_started}}
  cd ../OA_Tool-{{auto_started}}
  {{else}}
  📋 没有更多待开发的需求
  {{/if}}
```

### Checklist 警告输出

```yaml
status: warning
feature:
  id: feat-auth

message: |
  ⚠️ 以下检查项未完成:

  - [ ] 单元测试已编写
  - [ ] 文档已更新

  是否继续完成？(y/n)

  y - 继续完成（记录跳过原因）
  n - 取消
```

### 失败输出

```yaml
status: error
error:
  code: MERGE_CONFLICT
  message: "合并时发生冲突"
  conflicts:
    - src/auth/login.ts
    - src/auth/register.ts
  suggestion: |
    请手动解决冲突:
    1. cd /OA_Tool
    2. 打开冲突文件，解决 <<<< 标记
    3. git add .
    4. git commit
    5. /complete-feature feat-auth --no-commit

# 或

status: error
error:
  code: NOT_FOUND
  message: "需求 'feat-auth' 不在活跃列表中"

# 或

status: error
error:
  code: NOTHING_TO_COMMIT
  message: "没有需要提交的变更"
  suggestion: "确认是否已在 worktree 中开发"
```

## 错误码

| 错误码 | 描述 | 处理建议 |
|--------|------|----------|
| NOT_FOUND | 需求不存在或不在 active | 检查 ID 是否正确 |
| WORKTREE_NOT_FOUND | Worktree 不存在 | 检查 worktree 是否被手动删除 |
| NOTHING_TO_COMMIT | 没有变更需要提交 | 确认是否已开发 |
| MERGE_CONFLICT | 合并冲突 | 手动解决后重试 |
| TAG_EXISTS | Tag 已存在 | 使用不同的 tag 名称 |
| GIT_ERROR | Git 操作失败 | 检查 Git 状态 |
| ARCHIVE_ERROR | 归档失败 | 检查目录权限 |

## 文件变更

| 文件 | 操作 | 变更内容 |
|------|------|----------|
| features/active-{id}/ | 移动 | → features/archive/done-{id}/ |
| features/archive/archive-log.yaml | 修改 | 添加归档记录 |
| features/archive/done-{id}/spec.md | 修改 | 添加合并记录和统计 |
| feature-workflow/queue.yaml | 修改 | active 列表移除该条目 |
| Git (main) | 提交 | 合并提交 |
| Git (tag) | 创建 | 归档 tag |
| Git (worktree) | 删除 | 清理 worktree |
| Git (branch) | 删除 | 清理 feature 分支 |

## Git 操作详情

```bash
# Step 3: 提交代码
cd ../OA_Tool-feat-auth
git add .
git status
git commit -m "feat(feat-auth): 用户认证功能"
# 记录: commit_hash = git rev-parse HEAD

# Step 4: 合并到 main
cd /OA_Tool
git checkout main
git pull origin main  # 如果配置了远程
git merge feature/auth --no-ff -m "Merge feature/auth: 用户认证"
# 记录: merge_commit = git rev-parse HEAD
git push origin main  # 如果 auto_push=true

# Step 5: 创建归档 Tag
TAG_NAME="feat-auth-$(date +%Y%m%d)"
git tag -a "$TAG_NAME" -m "Archive: 用户认证功能"
git push origin "$TAG_NAME"  # 如果配置了远程

# Step 6: 清理
git worktree remove ../OA_Tool-feat-auth
git branch -d feature/auth

# 验证
git worktree list
# 应该只看到:
# /OA_Tool    main

git tag -l "feat-auth*"
# 应该看到:
# feat-auth-20260302
```

### 恢复已归档的分支

如果需要恢复已删除的分支：

```bash
# 从 tag 创建新分支
git checkout -b feature/auth-restored feat-auth-20260302

# 或者查看历史
git log feat-auth-20260302
```

## 归档日志格式

### features/archive/archive-log.yaml

```yaml
# 归档日志
# 记录所有已完成需求的归档信息

meta:
  last_updated: 2026-03-02T18:00:00
  total_archived: 2

archived:
  - id: feat-auth
    name: 用户认证
    completed: 2026-03-02T18:00:00

    # Git 归档信息
    tag: feat-auth-20260302
    merge_commit: abc123def456
    merged_to: main

    # 清理信息
    branch_deleted: true
    branch_name: feature/auth
    worktree_deleted: true
    worktree_path: ../OA_Tool-feat-auth

    # 需求目录
    docs_path: done-feat-auth

    # 统计
    stats:
      started: 2026-03-02T15:30:00
      duration: "2h30m"
      commits: 5
      files_changed: 8
      additions: 450
      deletions: 20

    # Checklist 跳过记录（如果有）
    checklist_skipped:
      - "单元测试已编写"
      reason: "后续补充"

  - id: feat-login
    name: 登录页面
    completed: 2026-03-01T16:00:00
    tag: feat-login-20260301
    # ...
```

## spec.md 合并记录

完成后更新 spec.md，添加合并记录部分：

```markdown
# Feature: feat-auth 用户认证

## 基本信息
- **ID**: feat-auth
- **名称**: 用户认证
- **状态**: ✅ 已完成
- **优先级**: 80

## 合并记录
- **完成时间**: 2026-03-02 18:00
- **合并到**: main
- **合并方式**: --no-ff
- **Merge Commit**: abc123def456
- **归档 Tag**: feat-auth-20260302

## 开发统计
- **开发时长**: 2h 30m
- **提交数**: 5
- **变更文件**: 8
- **代码变更**: +450 / -20

## 需求描述
实现用户登录、注册、登出功能...

## 技术方案
...

## 验收标准
- [x] 用户可以注册
- [x] 用户可以登录
- [x] 用户可以登出
```

## 依赖的配置

```yaml
# feature-workflow/config.yaml
project:
  name: OA_Tool
  main_branch: main

workflow:
  auto_start: true
  require_checklist: true

completion:
  # 归档策略
  archive:
    create_tag: true              # 创建归档 tag
    tag_format: "{id}-{date}"     # tag 格式
    tag_date_format: "%Y%m%d"     # 日期格式

  # 清理策略
  cleanup:
    delete_worktree: true         # 删除 worktree
    delete_branch: true           # 删除分支（已通过 tag 归档）

  # 记录策略
  record:
    update_spec: true             # 更新 spec.md
    update_archive_log: true      # 更新 archive-log.yaml

git:
  auto_push: false
  merge_strategy: "--no-ff"
  push_tags: false                # 是否自动推送 tag
```

## 示例用法

### 示例 1: 正常完成

```
用户: /complete-feature feat-auth

Agent: 🔍 检查 checklist...
       ✅ 所有检查项已完成

       📝 提交变更...
       ✅ 已提交: feat(feat-auth): 用户认证

       🔀 合并到 main...
       ✅ 已合并: feature/auth → main

       🏷️ 创建归档 tag...
       ✅ 已创建: feat-auth-20260302

       🗑️ 清理...
       ✅ 已删除 worktree 和分支

       📁 归档...
       ✅ 已归档到 features/archive/done-feat-auth

       🚀 自动启动: feat-dashboard
       cd ../OA_Tool-feat-dashboard
```

### 示例 2: Checklist 未完成

```
用户: /complete-feature feat-auth

Agent: ⚠️ 以下检查项未完成:

       - [ ] 单元测试已编写
       - [ ] 文档已更新

       是否继续？(y/n)

       y - 继续完成（记录跳过原因）
       n - 取消

用户: y

Agent: ✅ 继续完成...
       （记录跳过原因到 archive-log.yaml）
```

### 示例 3: 合并冲突

```
用户: /complete-feature feat-auth

Agent: ❌ 合并时发生冲突

       冲突文件:
       - src/auth/login.ts
       - src/auth/register.ts

       请手动解决:
       1. cd /OA_Tool
       2. 打开冲突文件，解决 <<<< 标记
       3. git add .
       4. git commit
       5. /complete-feature feat-auth --no-commit
```

### 示例 4: 只提交不合并

```
用户: /complete-feature feat-auth --no-merge

Agent: ✅ 已提交，跳过合并

       分支 feature/auth 保留
       Worktree ../OA_Tool-feat-auth 保留

       需要时手动合并:
       git checkout main
       git merge feature/auth
       /complete-feature feat-auth --no-commit
```

### 示例 5: 保留分支

```
用户: /complete-feature feat-auth --keep-branch

Agent: ✅ 已完成

       🏷️ 归档 tag: feat-auth-20260302
       🗑️ 已删除 worktree
       🌿 保留分支: feature/auth
```

## 回滚策略

| 失败点 | 回滚操作 |
|--------|----------|
| Step 3 提交失败 | 无需回滚 |
| Step 4 合并失败 | 等待用户手动解决冲突 |
| Step 5 tag 创建失败 | 跳过 tag，继续后续步骤 |
| Step 6 清理失败 | 保留 worktree，提示手动清理 |
| Step 7-8 归档失败 | 手动移动目录 |

## 注意事项

1. **Tag 命名冲突**: 如果当天有同名需求，自动添加序号 (feat-auth-20260302-2)
2. **合并冲突**: 不自动解决，需要用户手动处理
3. **空提交**: 如果没有变更，警告用户
4. **Checklist 跳过**: 记录跳过原因到 archive-log.yaml
5. **分支恢复**: 可通过 tag 随时恢复已删除的分支
6. **Tag 推送**: 默认不推送 tag 到远程，需配置 push_tags: true
