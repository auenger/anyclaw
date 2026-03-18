# Skill: implement-feature

## 元信息

| 属性 | 值 |
|------|-----|
| 名称 | implement-feature |
| 触发命令 | `/implement-feature <id>` |
| 优先级 | P0 (核心) |
| 依赖 | start-feature |

## 功能描述

根据需求文档实现代码，包括：
- 读取 spec.md 理解需求
- 分析 task.md 确定开发任务
- 在 worktree 中实现代码
- 更新文档记录进度
- 自测验证

## 输入参数

| 参数名 | 类型 | 必需 | 默认值 | 描述 |
|--------|------|------|--------|------|
| id | string | 是 | - | 需求 ID |
| task_index | number | 否 | all | 指定实现某个任务（从 1 开始） |
| dry_run | boolean | 否 | false | 只分析不实现 |

## 前置条件检查

```
┌─────────────────────────────────────────────────────────────────┐
│ 检查 1: 需求状态                                                 │
│ - 需求必须在 queue.yaml 的 active 列表中                        │
│ - worktree 必须已创建                                           │
└─────────────────────────────────────────────────────────────────┘
```

## 执行流程

```
┌─────────────────────────────────────────────────────────────────┐
│ Step 1: 读取需求文档                                             │
│ - 读取 features/active-{id}/spec.md                            │
│   - 需求描述                                                     │
│   - 上下文分析（参考代码、相关文档）                              │
│   - 验收标准                                                     │
│ - 读取 features/active-{id}/task.md                            │
│   - 任务列表                                                     │
│   - 任务状态（已完成/未完成）                                     │
└─────────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────────┐
│ Step 2: 分析任务                                                 │
│ - 解析任务列表                                                   │
│ - 识别任务依赖关系                                               │
│ - 确定实现顺序                                                   │
│ - 估算工作量（可选）                                             │
│                                                                 │
│ 输出:                                                            │
│ - 待实现任务列表                                                 │
│ - 建议的实现顺序                                                 │
│ - 需要参考的代码/文档                                            │
└─────────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────────┐
│ Step 3: 确认实现计划                                             │
│ - 显示分析结果                                                   │
│ - 显示实现计划                                                   │
│ - 询问用户确认                                                   │
│                                                                 │
│ 示例:                                                            │
│ "发现 5 个待实现任务，建议顺序如下：                              │
│   1. 创建 User 模型                                              │
│   2. 实现注册接口                                                │
│   3. 实现登录接口                                                │
│   4. 实现登出接口                                                │
│   5. 添加认证中间件                                              │
│  是否开始实现？(y/n/edit)"                                       │
└─────────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────────┐
│ Step 4: 实现代码                                                 │
│ - 切换到 worktree 目录                                           │
│ - 按顺序实现每个任务                                             │
│ - 每完成一个任务:                                                │
│   - 更新 task.md 中的状态                                        │
│   - 简要说明实现内容                                             │
│ - 更新 spec.md 中的技术方案（如果需要）                           │
│                                                                 │
│ 实现过程中:                                                      │
│ - 参考上下文中提到的现有代码                                     │
│ - 遵循项目代码规范                                               │
│ - 添加必要的注释                                                 │
└─────────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────────┐
│ Step 5: 自测验证                                                 │
│ - 运行现有测试（如果有）                                         │
│ - 手动验证核心功能                                               │
│ - 检查代码质量                                                   │
│ - 记录测试结果                                                   │
└─────────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────────┐
│ Step 6: 生成报告                                                 │
│ - 实现的任务列表                                                 │
│ - 未完成的任务（如果有）                                         │
│ - 测试结果                                                       │
│ - 下一步建议                                                     │
└─────────────────────────────────────────────────────────────────┘
```

## 输出

### 分析阶段输出

```yaml
status: analyzed
feature:
  id: feat-auth
  name: 用户认证

analysis:
  total_tasks: 5
  completed: 1
  pending: 4

  pending_tasks:
    - index: 2
      name: 实现注册接口
      dependencies: []
    - index: 3
      name: 实现登录接口
      dependencies: [2]
    - index: 4
      name: 实现登出接口
      dependencies: [3]
    - index: 5
      name: 添加认证中间件
      dependencies: [2, 3, 4]

  suggested_order: [2, 3, 4, 5]

  context:
    reference_code:
      - src/models/user.ts
      - src/middleware/
    reference_docs:
      - docs/api-design.md

message: |
  📋 分析完成

  待实现任务: 4
  建议顺序:
    1. 实现注册接口
    2. 实现登录接口
    3. 实现登出接口
    4. 添加认证中间件

  参考代码:
    - src/models/user.ts
    - src/middleware/

  是否开始实现？(y/n/edit)
```

### 实现阶段输出

```yaml
status: implemented
feature:
  id: feat-auth

implementation:
  completed_tasks:
    - index: 2
      name: 实现注册接口
      files:
        - src/api/auth/register.ts (new)
        - src/services/user.ts (modified)
    - index: 3
      name: 实现登录接口
      files:
        - src/api/auth/login.ts (new)
    - index: 4
      name: 实现登出接口
      files:
        - src/api/auth/logout.ts (new)
    - index: 5
      name: 添加认证中间件
      files:
        - src/middleware/auth.ts (modified)

  skipped_tasks: []

  files_changed:
    new: 3
    modified: 2
    deleted: 0

testing:
  tests_run: true
  passed: 12
  failed: 0

message: |
  ✅ 实现完成

  完成任务: 4/4
  文件变更: 5

  测试: 12 passed, 0 failed

  下一步:
    - 运行 /verify-feature feat-auth 验证
    - 或运行 /complete-feature feat-auth 完成
```

### Dry Run 模式输出

```yaml
status: dry_run
message: |
  🔍 Dry Run - 分析结果

  将实现以下任务:
  1. 实现注册接口
     - 新建 src/api/auth/register.ts
     - 修改 src/services/user.ts

  2. 实现登录接口
     - 新建 src/api/auth/login.ts

  ...

  不会实际修改文件
  使用 /implement-feature feat-auth 执行
```

### 失败输出

```yaml
status: error
error:
  code: NOT_ACTIVE
  message: "需求 feat-auth 不在活跃列表中"
  suggestion: "请先运行 /start-feature feat-auth"

# 或

status: error
error:
  code: WORKTREE_NOT_FOUND
  message: "Worktree 不存在"
  worktree: ../OA_Tool-feat-auth
  suggestion: "请先运行 /start-feature feat-auth"

# 或

status: partial
error:
  code: IMPLEMENTATION_FAILED
  message: "任务 3 实现失败"
  details: "登录接口依赖的用户服务不存在"
  completed: [1, 2]
  failed: 3
  pending: [4, 5]
```

## 错误码

| 错误码 | 描述 | 处理建议 |
|--------|------|----------|
| NOT_FOUND | 需求不存在 | 检查 ID |
| NOT_ACTIVE | 需求不在活跃列表 | 先执行 start-feature |
| WORKTREE_NOT_FOUND | Worktree 不存在 | 先执行 start-feature |
| SPEC_PARSE_ERROR | spec.md 解析失败 | 检查文档格式 |
| TASK_PARSE_ERROR | task.md 解析失败 | 检查文档格式 |
| IMPLEMENTATION_FAILED | 实现失败 | 查看详情，手动修复 |

## 文件变更

| 文件 | 操作 | 变更内容 |
|------|------|----------|
| worktree 中的代码文件 | 创建/修改 | 实现的代码 |
| features/active-{id}/task.md | 修改 | 更新任务状态 |
| features/active-{id}/spec.md | 修改 | 补充技术方案 |

## Spec 文档结构要求

```markdown
# Feature: feat-auth 用户认证

## 基本信息
- **ID**: feat-auth
- **名称**: 用户认证
- **优先级**: 80

## 需求描述
实现用户登录、注册、登出功能...

## 上下文分析
### 需要参考的现有代码
- `src/models/user.ts` - 用户模型
- `src/middleware/auth.ts` - 现有认证中间件

### 相关文档
- API 设计文档

## 技术方案
（Agent 实现时补充）

## 验收标准
- [ ] 用户可以注册
- [ ] 用户可以登录
- [ ] 用户可以登出
```

## Task 文档结构要求

```markdown
# Tasks: feat-auth

## 任务列表

### 1. 数据模型
- [x] 创建 User 模型
- [ ] 添加认证相关字段

### 2. API 接口
- [ ] POST /auth/register
- [ ] POST /auth/login
- [ ] POST /auth/logout

### 3. 中间件
- [ ] 认证中间件

### 4. 测试
- [ ] 单元测试
```

## 实现策略

### 代码生成策略

```
1. 优先参考现有代码风格
2. 复用现有组件和工具函数
3. 遵循项目目录结构
4. 添加必要的错误处理
5. 添加必要的类型定义（TypeScript）
```

### 任务依赖处理

```
如果任务 B 依赖任务 A:
1. 先实现任务 A
2. 验证 A 完成后再实现 B
3. 如果 A 失败，暂停并报告
```

### 中断恢复

```
如果实现过程中断:
1. task.md 记录了已完成的状态
2. 重新执行时跳过已完成的任务
3. 从上次中断处继续
```

## 示例用法

### 示例 1: 完整实现

```
用户: /implement-feature feat-auth

Agent: 📋 分析需求...

       待实现任务: 4
       建议顺序: 注册 → 登录 → 登出 → 中间件

       是否开始？(y/n)

用户: y

Agent: 🔨 实现中...

       [1/4] 实现注册接口... ✅
       [2/4] 实现登录接口... ✅
       [3/4] 实现登出接口... ✅
       [4/4] 添加认证中间件... ✅

       ✅ 实现完成！

       文件变更: 5
       测试: 12 passed

       下一步: /verify-feature feat-auth
```

### 示例 2: 只分析不实现

```
用户: /implement-feature feat-auth --dry-run

Agent: 🔍 Dry Run 模式

       将实现:
       1. 实现注册接口
          - 新建 src/api/auth/register.ts
       ...

       不会实际执行
```

### 示例 3: 实现单个任务

```
用户: /implement-feature feat-auth --task=2

Agent: 只实现任务 2: 实现注册接口

       🔨 实现中... ✅

       已更新 task.md
```

### 示例 4: 中断恢复

```
用户: /implement-feature feat-auth

Agent: 📋 检测到上次进度

       已完成: 1/4
       待实现: 3 (登录、登出、中间件)

       是否从上次继续？(y/n/restart)

用户: y

Agent: 🔨 从任务 2 继续...
```

## 与其他 Skill 的关系

```
start-feature           →  创建环境和 worktree
         ↓
implement-feature  ←──  →  读取 spec/task，实现代码
         ↓
verify-feature          →  执行 checklist 验证
         ↓
complete-feature        →  提交、合并、归档
```

## 注意事项

1. **不自动提交** - 实现完成后代码在 worktree 中，未提交
2. **依赖现有代码** - 优先参考 spec 中提到的上下文
3. **保持文档同步** - 实现时更新 task.md 状态
4. **支持中断恢复** - 可以随时中断，下次继续
