---
description: 创建新的特性请求，通过交互式对话收集需求，生成文档，并添加到队列
---

# 创建新特性

你需要帮助用户创建一个新的特性请求。按照以下步骤执行：

## 第 1 步：加载项目上下文

在创建特性之前，先加载项目上下文：

1. 检查 `project-context.md` - 如果存在，读取并加载
2. 检查 `CLAUDE.md` - 如果存在，读取项目信息
3. 如有必要，快速扫描项目结构了解技术栈

## 第 2 步：收集信息

通过对话收集以下信息：
- **name**: 特性名称（简短，如 "用户认证"）
- **description**: 详细描述需要构建什么
- **priority**: 1-100（默认 50，越高越紧急）
- **dependencies**: 依赖的其他特性 ID 列表（可选）

## 第 3 步：分析用户价值点

分析特性描述：
1. 识别独立的用户价值点
2. 为每个价值点生成 Gherkin 格式的验收场景

**价值点定义**：一个独特的能力，可以独立交付和测试，有清晰的验收标准。

## 第 4 步：评估大小和拆分决策

| 价值点数量 | 大小 | 操作 |
|-----------|------|------|
| 1 | S | 直接创建 |
| 2 | M | 直接创建（可选拆分建议） |
| 3+ | L | 建议拆分 |

如果价值点 ≥ 3，建议拆分特性以防止实现时 AI 上下文溢出。

## 第 5 步：生成特性 ID

格式：`{prefix}-{slug}`（prefix 从 config.yaml 获取，默认 "feat"）

## 第 6 步：检查冲突

检查 ID 是否已存在于：
- `features/pending-{id}/`
- `features/active-{id}/`
- `features/archive/done-{id}/`
- `feature-workflow/queue.yaml`

## 第 7 步：创建特性目录和文件

创建目录：`features/pending-{id}/`

创建三个文件：
- **spec.md**: 需求规范，包含用户价值点和 Gherkin 场景
- **task.md**: 任务分解
- **checklist.md**: 完成检查清单

## 第 8 步：更新队列

添加特性到 `feature-workflow/queue.yaml` 的 pending 列表，按优先级排序。

## 第 9 步：检查自动启动

读取 `feature-workflow/config.yaml` - 如果 `workflow.auto_start: true` 且 `active.count < max_concurrent`，自动启动第一个特性。

## 输出格式

```
✅ 特性创建成功！

ID: {id}
大小: {S|M|L}
目录: features/pending-{id}

文档:
- spec.md      需求规范
- task.md      任务分解
- checklist.md 完成检查清单

状态: pending（等待开发）
```
