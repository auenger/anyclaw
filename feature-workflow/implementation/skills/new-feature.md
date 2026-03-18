# Skill: new-feature

## 元信息

| 属性 | 值 |
|------|-----|
| 名称 | new-feature |
| 触发命令 | `/new-feature [描述]` |
| 优先级 | P0 (核心) |
| 依赖 | 无 |

## 功能描述

创建新的功能需求，包括：
- 通过对话收集需求信息
- 生成需求 ID
- 创建需求目录和文档
- 更新调度队列
- 可选：自动启动开发

## 输入参数

| 参数名 | 类型 | 必需 | 默认值 | 描述 |
|--------|------|------|--------|------|
| description | string | 否 | - | 需求的简要描述 |
| name | string | 否 | - | 需求名称（如未提供，从描述推断） |
| priority | number | 否 | 50 | 优先级 (1-100) |
| dependencies | string[] | 否 | [] | 依赖的其他需求 ID |

## 对话收集

如果用户只提供描述或什么都不提供，通过对话收集以下信息：

```
Agent: 请提供需求的详细信息：

1. 需求名称（简短描述，如"用户认证"）
2. 详细描述（这个需求要解决什么问题）
3. 优先级（1-100，数字越大越优先，默认50）
4. 是否依赖其他需求？（如有，请提供需求 ID）

用户: 用户认证，实现登录注册功能，优先级 80

Agent: 确认以下信息：
- 名称: 用户认证
- 描述: 实现登录注册功能
- 优先级: 80
- 依赖: 无

是否确认创建？(y/n)
```

## 执行流程

```
┌─────────────────────────────────────────────────────────────────┐
│ Step 1: 收集信息                                                 │
│ - 解析输入参数                                                   │
│ - 如果信息不完整，启动对话收集                                    │
│ - 确认信息                                                       │
└─────────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────────┐
│ Step 2: 生成 ID                                                  │
│ - slug = generate_slug(name)                                    │
│   - 转小写                                                       │
│   - 空格转连字符                                                 │
│   - 移除特殊字符                                                 │
│   - 例: "用户认证" → "user-auth" 或 "auth"                       │
│ - id = "{prefix}-{slug}"                                        │
│   - prefix 从 config.yaml 读取，默认 "feat"                      │
└─────────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────────┐
│ Step 3: 检查冲突                                                 │
│ - 检查 features/pending-{id} 是否存在                           │
│ - 检查 features/active-{id} 是否存在                            │
│ - 检查 features/archive/done-{id} 是否存在                      │
│ - 检查 queue.yaml 中是否已存在该 ID                              │
│ - 如果冲突，生成新 slug (如 auth-2) 或提示用户                   │
└─────────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────────┐
│ Step 4: 创建目录和文件                                           │
│ - mkdir features/pending-{id}                                   │
│ - 读取 templates/spec.md                                        │
│ - 替换模板变量: {{id}}, {{name}}, {{priority}}, {{created}}     │
│ - 写入 features/pending-{id}/spec.md                            │
│ - 同理创建 task.md, checklist.md                                │
└─────────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────────┐
│ Step 5: 更新队列                                                 │
│ - 读取 queue.yaml                                               │
│ - 添加到 pending 列表:                                          │
│   {id, name, priority, created: now}                            │
│ - 按 priority 降序排序 pending 列表                              │
│ - 更新 meta.last_updated                                        │
│ - 写入 queue.yaml                                               │
└─────────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────────┐
│ Step 6: 检查自动启动                                             │
│ - 读取 config.yaml                                              │
│ - 统计 active.count                                             │
│ - if active.count < max_concurrent and auto_start:              │
│     调用 start-feature(id)                                      │
│     返回 status: started                                        │
│ - else:                                                         │
│     返回 status: pending                                        │
└─────────────────────────────────────────────────────────────────┘
```

## 输出

### 成功输出

```yaml
status: success
feature:
  id: feat-auth
  name: 用户认证
  priority: 80
  path: features/pending-feat-auth
  queue_status: pending | started

message: |
  ✅ 需求创建成功！

  ID: feat-auth
  目录: features/pending-feat-auth

  文档:
  - spec.md    需求规格
  - task.md    任务分解
  - checklist.md 完成检查

  状态: pending (等待开发)

  # 如果自动启动:
  🚀 已自动启动开发！
  Worktree: ../OA_Tool-feat-auth
  切换目录: cd ../OA_Tool-feat-auth
```

### 失败输出

```yaml
status: error
error:
  code: ID_CONFLICT
  message: "需求 ID 'feat-auth' 已存在"
  suggestion: "请使用不同的名称，或使用 feat-auth-2"

# 或

status: error
error:
  code: QUEUE_ERROR
  message: "更新队列失败: 文件被锁定"
```

## 错误码

| 错误码 | 描述 | 处理建议 |
|--------|------|----------|
| ID_CONFLICT | ID 已存在 | 使用不同的名称或接受建议的新 ID |
| QUEUE_ERROR | 更新队列失败 | 检查 queue.yaml 权限和格式 |
| TEMPLATE_ERROR | 模板处理失败 | 检查 templates 目录 |
| PERMISSION_ERROR | 无权限创建目录 | 检查文件系统权限 |

## 文件变更

| 文件 | 操作 | 变更内容 |
|------|------|----------|
| features/pending-{id}/ | 创建 | 新目录 |
| features/pending-{id}/spec.md | 创建 | 需求规格文档 |
| features/pending-{id}/task.md | 创建 | 任务分解文档 |
| features/pending-{id}/checklist.md | 创建 | 完成检查文档 |
| queue.yaml | 修改 | pending 列表新增条目 |

## 依赖的配置

```yaml
# config.yaml
naming:
  feature_prefix: feat

paths:
  features_dir: features
```

## 示例用法

### 示例 1: 简单创建

```
用户: /new-feature 用户认证

Agent: 请提供详细信息...
(对话收集)

Agent: ✅ 需求 feat-auth 创建成功！
```

### 示例 2: 完整参数

```
用户: /new-feature --name="用户认证" --priority=80 --description="实现登录注册功能"

Agent: ✅ 需求 feat-auth 创建成功！
       🚀 已自动启动开发！
       cd ../OA_Tool-feat-auth
```

### 示例 3: ID 冲突

```
用户: /new-feature 用户认证

Agent: ⚠️ 需求 ID 'feat-auth' 已存在
       建议使用: feat-auth-2
       是否继续？(y/n)
```

## 注意事项

1. **ID 生成策略**: 优先使用英文 slug，如果无法推断则使用拼音或数字
2. **优先级默认值**: 如果用户未指定，默认 50
3. **自动启动条件**: 需要同时满足 auto_start=true 且有空闲槽位
4. **并发安全**: 如果多人同时创建，需要处理 queue.yaml 的并发写入
