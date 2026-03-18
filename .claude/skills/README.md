# AnyClaw Feature Workflow Skills

本目录包含了从 feature-workflow 系统转换而来的所有技能定义，这些技能用于管理完整的特性开发工作流。

## 技能列表

### 核心技能 (Core Skills)

| 技能 | 描述 | 用途 |
|-----|------|-----|
| **new-feature** | 创建新特性请求 | 收集需求、生成文档、添加到队列 |
| **start-feature** | 启动特性开发 | 创建分支、创建工作树 |
| **implement-feature** | 实现特性代码 | 编写代码、更新任务状态 |
| **verify-feature** | 验证已实现的特性 | 检查完成状态、运行测试 |
| **complete-feature** | 完成特性 | 提交代码、合并到主分支、清理 |

### 管理技能 (Management Skills)

| 技能 | 描述 | 用途 |
|-----|------|-----|
| **list-features** | 列出所有特性 | 查看状态、优先级、过滤和排序 |
| **block-feature** | 阻止特性 | 阻止特性启动（带原因） |
| **unblock-feature** | 解除阻止 | 允许被阻止的特性重新启动 |
| **feature-config** | 管理配置 | 查看或修改工作流配置 |
| **cleanup-features** | 清理特性数据 | 清理旧的特性数据、释放空间 |

### Agent 技能 (Agent Skills)

| 技能 | 描述 | 用途 |
|-----|------|-----|
| **dev-agent** | 开发代理 | 自动化完整的特性开发流程 |
| **feature-manager** | 特性管理器 | 编排多个特性、处理依赖关系 |

### Workflow 技能 (Workflow Skills)

| 技能 | 描述 | 用途 |
|-----|------|-----|
| **feature-lifecycle** | 特性生命周期工作流 | 引导式完整的特性开发体验 |
| **auto-schedule** | 自动调度 | 基于优先级和依赖关系自动启动特性 |

## 使用示例

### 创建并开发新特性

```
# 1. 创建新特性
/new-feature "用户认证系统，包含登录、注册、登出"

# 2. 启动开发
/start-feature feat-auth

# 3. 实现代码
/implement-feature feat-auth

# 4. 验证
/verify-feature feat-auth

# 5. 完成
/complete-feature feat-auth
```

### 使用自动化代理

```
# 完全自动化开发流程
/dev-agent "用户认证系统"

# 继续开发现有特性
/dev-agent feat-auth --mode=interactive

# 从错误恢复
/dev-agent feat-auth --resume
```

### 使用工作流

```
# 启动完整的交互式工作流
/feature-lifecycle

# 查看状态
/feature-lifecycle --status

# 进入下一阶段
/feature-lifecycle --next
```

### 管理特性

```
# 列出所有特性
/list-features --status=pending --sort=priority

# 阻止特性
/block-feature feat-upload --reason "等待存储基础设施完成"

# 解除阻止
/unblock-feature feat-upload

# 清理旧特性
/cleanup-features --older-than=30 --confirm
```

### 自动调度

```
# 预览将要调度的特性
/auto-schedule --dry-run

# 自动调度
/auto-schedule

# 覆盖并发限制
/auto-schedule --max=5
```

## 配置

所有技能使用 `feature-workflow/config.yaml` 中的配置：

```yaml
project:
  name: AnyClaw
  main_branch: main

git:
  remote: origin
  branch_prefix: feature

workflow:
  auto_start: false
  max_concurrent: 3

worktree:
  base: ..
  prefix: AnyClaw

feature:
  id_prefix: feat
  default_priority: 50
```

## 工作流程

```
new-feature → start-feature → implement-feature → verify-feature → complete-feature
      ↓              ↓                 ↓                    ↓                    ↓
   创建需求      设置环境         编写代码              验证功能            提交完成
```

## 技能依赖关系

```
feature-manager (编排器)
    ├─→ dev-agent (自动化开发)
    │       ├─→ new-feature
    │       ├─→ start-feature
    │       ├─→ implement-feature
    │       ├─→ verify-feature
    │       └─→ complete-feature
    │
    ├─→ feature-lifecycle (交互式工作流)
    │       └─→ (调用所有核心技能)
    │
    ├─→ auto-schedule (自动调度)
    │       └─→ start-feature
    │
    └─→ (管理技能)
        ├─→ list-features
        ├─→ block-feature
        ├─→ unblock-feature
        ├─→ feature-config
        └─→ cleanup-features
```

## 状态转换

```
pending → active → done
   ↓         ↓
blocked   (error)
   ↓         ↓
pending   active
```

## 文件位置

- 技能定义: `.claude/skills/*.md`
- 工作流配置: `feature-workflow/config.yaml`
- 特性队列: `feature-workflow/queue.yaml`
- 特性文档: `features/{status}-{id}/*.md`

## 更多信息

详细的 feature-workflow 系统文档位于: `feature-workflow/DOCUMENTATION.md`
