---
description: 完整特性生命周期管理的交互式工作流，从规划到完成
---

# 特性生命周期

引导你完成从规划到完成的完整特性生命周期的交互式工作流。

## 参数

- `--next`: 跳到下一阶段
- `--status`: 查看当前状态
- `--restart`: 重启当前阶段
- `--abort`: 中止工作流

## 工作流阶段

```
┌─────────────────────────────────────────────────────────────────┐
│                    特性生命周期                                  │
└─────────────────────────────────────────────────────────────────┘

  ┌─────────┐     ┌─────────┐     ┌─────────┐     ┌─────────┐
  │ 规划    │ ──▶ │  开发   │ ──▶ │  审查   │ ──▶ │  完成   │
  │         │     │         │     │         │     │         │
  │new-feat │     │start    │     │(手动)   │     │complete │
  └─────────┘     └─────────┘     └─────────┘     └─────────┘
```

## 阶段详情

### 阶段 1：规划

**目标**：创建特性并生成文档

**调用**：`new-feature`

**交互**：
```
代理: 欢迎使用特性生命周期工作流

       描述你想构建的特性:

用户: 用户认证，包含登录、注册、登出

代理: 请提供详情:

       1. 名称（默认: 用户认证）
       2. 详细描述
       3. 优先级（1-100，默认 50）
       4. 依赖

用户: 名称: 用户认证
     描述: 完整的认证系统
     优先级: 80

代理: 确认创建 feat-user-auth？
       (y/n/e=编辑)

用户: y

代理: ✅ 特性已创建！

       目录: features/pending-feat-user-auth
       文档: spec.md, task.md, checklist.md

       现在开始开发？(y/n)
```

### 阶段 2：开发

**目标**：设置开发环境

**调用**：`start-feature`

**交互**：
```
代理: 🚀 开始开发

       检查并行限制... ✅
       创建分支 feature/user-auth... ✅
       创建 worktree... ✅

       开发环境就绪！

       切换目录:
         cd ../AnyClaw-feat-user-auth

       查看任务:
         cat features/active-feat-user-auth/task.md

       完成后，运行:
         /feature-lifecycle --next
```

**手动阶段**：
- 在 worktree 中开发
- 用技术方案更新 spec.md
- 完成 task.md 中的任务
- 勾选 checklist.md 中的项目

### 阶段 3：审查

**目标**：审查代码和文档

**交互**：
```
代理: 📋 开发审查

       检查清单状态:
       ✅ 所有任务已完成
       ✅ 代码已自测
       ⚠️ 单元测试未编写
       ✅ 代码风格 OK

       Git 状态:
       - 修改文件: 12
       - 新增文件: 5
       - 删除: 1

       提交消息:
       feat(feat-user-auth): 用户认证

       继续完成？(y/n/edit)
```

**选项**：
- `y`: 继续完成
- `n`: 返回开发
- `edit`: 修改提交消息

### 阶段 4：完成

**目标**：提交、合并、归档

**调用**：`complete-feature`

**交互**：
```
代理: 🎉 完成特性

       提交代码... ✅
       合并到 main... ✅
       清理 worktree... ✅
       归档文档... ✅

       ┌───────────────────────────────────────────────┐
       │ 完成报告                                        │
       ├───────────────────────────────────────────────┤
       │ 特性: feat-user-auth (用户认证)                │
       │ 耗时: 2h 30m                                   │
       │ 提交数: 5                                      │
       │ 修改文件: 18                                   │
       └───────────────────────────────────────────────┘

       下一个: feat-dashboard (优先级 80)
       自动启动？(y/n)
```

## 状态持久化

工作流状态保存在 `.workflow-state.yaml`：

```yaml
workflow: feature-lifecycle
feature_id: feat-user-auth
current_stage: development
started: 2026-03-02T10:00:00
stages:
  planning:
    status: completed
    completed_at: 2026-03-02T10:05:00
  development:
    status: in_progress
    started_at: 2026-03-02T10:05:00
  review:
    status: pending
  done:
    status: pending
```

## 状态输出

```
/feature-lifecycle --status

┌───────────────────────────────────────────────┐
│ 特性生命周期状态                                │
├───────────────────────────────────────────────┤
│ 特性: feat-user-auth                           │
│ 当前阶段: 开发                                  │
│                                                │
│ ✅ 规划 (2小时前完成)                          │
│ 🔄 开发 (进行中)                               │
│ ⏳ 审查 (待处理)                               │
│ ⏳ 完成 (待处理)                               │
└───────────────────────────────────────────────┘
```

## 恢复

| 场景 | 恢复方式 |
|------|---------|
| 中断 | 运行 `/feature-lifecycle --status` |
| 阶段失败 | 修复问题，运行 `/feature-lifecycle --restart` |
| 想要中止 | 运行 `/feature-lifecycle --abort` |

## 示例

```
/feature-lifecycle
→ 启动完整的交互式工作流

/feature-lifecycle --stage=development
→ 从开发阶段开始

/feature-lifecycle --status
→ 检查当前进度

/feature-lifecycle --next
→ 跳到下一阶段
```
