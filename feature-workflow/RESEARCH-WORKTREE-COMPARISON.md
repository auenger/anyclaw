# 研究报告：Claude Code 原生 Worktree vs Feature-Workflow

> 研究日期：2026-03-03
> 研究目标：对比 Claude Code 原生 `--worktree` 功能与 feature-workflow 系统的差异，探索结合可能性

## 1. Claude Code 原生 `--worktree` 概述

### 1.1 基本信息

Claude Code 从 v2.1.50 版本开始原生支持 Git Worktree，由 Boris Cherny（Claude Code 负责人）于 2026 年 2 月正式宣布。

### 1.2 核心命令

```bash
# 指定名称创建 worktree
claude --worktree feature-auth

# 自动命名（如 "bright-running-fox"）
claude --worktree

# 在隔离的 tmux 会话中运行
claude --worktree --tmux

# 简写形式
claude -w feature-test
```

### 1.3 工作机制

| 阶段 | 行为 |
|------|------|
| 创建 | 在 `.claude/worktrees/<name>/` 创建独立工作目录 |
| 分支 | 自动创建 `worktree-<name>` 分支 |
| 隔离 | 每个 worktree 有独立的 HEAD 和暂存区，共享 `.git` 数据库 |
| 清理 | 用 `/exit` 退出时，无改动则自动删除 worktree 和分支 |

### 1.4 设计理念

**"并行宇宙"** —— 每个 Agent 获得独立的工作目录副本，从根本上避免同时修改同一文件的问题。

---

## 2. 功能对比

### 2.1 核心差异

| 维度 | Claude Code 原生 `--worktree` | Feature-Workflow |
|------|------------------------------|------------------|
| **定位** | 轻量级会话隔离 | 完整的需求生命周期管理 |
| **创建位置** | `.claude/worktrees/<name>/` | `../OA_Tool-{slug}` (可配置) |
| **命名规则** | 自动随机命名或手动指定 | 结构化命名 `feature/{slug}` |
| **文档管理** | 无 | spec.md / task.md / checklist.md |
| **状态队列** | 无 | pending / active / blocked / completed |
| **并行控制** | 无限制 | `max_concurrent` 可配置 |
| **自动清理** | 无改动时自动删除 | 完成后手动触发清理 |
| **归档机制** | 无 | Git tag + archive 目录 |
| **配置化** | 无 | config.yaml 全可配置 |
| **冲突处理** | 靠隔离避免 | 可扩展冲突检测 |

### 2.2 生命周期对比

**原生 --worktree：**
```
启动会话 → 临时隔离 → 退出即销毁
```

**Feature-Workflow：**
```
new-feature → start-feature → 开发 → verify → complete → 归档
（完整的流程，有记录、可追溯）
```

### 2.3 使用场景对比

| 场景 | 原生 --worktree | Feature-Workflow |
|------|-----------------|------------------|
| 快速修个小 bug | 推荐 | 过重 |
| 正式需求开发 | 可用 | 推荐 |
| 团队协作 | 无支持 | 推荐 |
| 临时并行任务 | 推荐 | 可用 |
| 需要历史追溯 | 不支持 | 支持 |

---

## 3. 冲突处理机制分析

### 3.1 原生 --worktree 的冲突处理

**核心答案：靠隔离避免冲突，不是主动处理冲突**

```
┌─────────────────────────────────────────────────┐
│                    主仓库                         │
│  (共享 .git 数据库，但各自有独立的 HEAD 和工作区)    │
├─────────────┬─────────────┬─────────────────────┤
│ worktree-A  │ worktree-B  │ worktree-C          │
│ feature/a   │ fix/bug-123 │ refactor/config     │
│ 独立文件副本 │ 独立文件副本 │ 独立文件副本          │
└─────────────┴─────────────┴─────────────────────┘
```

**各 worktree 之间互不干扰，没有实时同步。**

### 3.2 合并时的冲突处理

当多个 worktree 完成后合并回主分支时，**冲突仍需手动处理**：

```bash
git merge feature/a
git merge feature/b  # ← 可能产生冲突
```

解决方式：
1. 人工介入
2. 让 Claude 辅助：*"当前文件存在 Git 冲突，冲突区域已标记，请帮我解决冲突"*

### 3.3 原生功能的局限

| 场景 | 原生 --worktree 能力 |
|------|---------------------|
| 开发时避免冲突 | ✅ 隔离解决 |
| 合并时冲突检测 | ❌ 无主动检测 |
| 冲突自动解决 | ❌ 需人工或让 Claude 辅助 |
| 冲突预防提醒 | ❌ 无 |
| 文件锁定机制 | ❌ 无 |

---

## 4. 结合可能性

### 4.1 互补关系

| 方面 | 原生 --worktree | Feature-Workflow |
|------|-----------------|------------------|
| 物理隔离 | ✅ 提供 | ✅ 已有 |
| 逻辑协调 | ❌ 无 | ✅ 可提供 |
| 流程管理 | ❌ 无 | ✅ 已有 |
| 即时性 | ✅ 快速启动 | 需要流程 |

### 4.2 潜在集成方案

**方案 A：在 worktree 内启动 Claude**

```bash
# start-feature 创建 worktree 后
cd ../OA_Tool-feat-auth
claude  # 直接在 worktree 里启动 Claude 会话
```

**方案 B：集成原生 --worktree 参数**

```bash
# 让 start-feature 调用
claude --worktree feat-auth
```

**方案 C：增强冲突检测**

在 `complete-feature` 技能中加入合并前冲突检测：

```bash
# 合并前检测冲突
git merge --no-commit --no-ff feature/{slug}
if conflicts; then
  echo "检测到冲突，请先解决"
  git diff --name-only --diff-filter=U
  exit 1
fi
```

### 4.3 配置扩展建议

可在 `config.yaml` 增加冲突相关配置：

```yaml
conflict:
  check_before_merge: true     # 合并前检测
  notify_on_overlap: true      # 文件重叠提醒
  lock_critical_files: false   # 锁定关键文件（可选）
```

---

## 5. 结论与建议

### 5.1 定位总结

| 系统 | 定位 |
|------|------|
| 原生 --worktree | **工具层** - 即时隔离，快速并行 |
| Feature-Workflow | **框架层** - 工程化管理，流程追溯 |

### 5.2 使用建议

| 场景 | 推荐方案 |
|------|---------|
| 快速并行修小 bug | 原生 `--worktree` |
| 正式需求开发 | Feature-Workflow |
| 团队协作项目 | Feature-Workflow |
| 两者结合 | 用 Feature-Workflow 管理流程，在 worktree 里用 Claude 开发 |

### 5.3 后续行动

1. **短期**：在 `complete-feature` 中增加合并前冲突检测
2. **中期**：探索调用原生 `claude --worktree` 的可能性
3. **长期**：考虑文件重叠预警机制

---

## 参考资料

- [Claude Code原生Git Worktree](https://m.blog.csdn.net/shebao3333/article/details/158543646)
- [Claude Code 并行革命！Git Worktree原生黑科技](https://m.blog.csdn.net/linxiaoliuyi/article/details/158420315)
- [一个参数多开Claude? Claude Code 把Worktree 变成"官方并行模式"](https://www.51cto.com/article/836654.html)
- [Claude Code正式引入Git Worktree原生支持](https://view.inews.qq.com/wxn/20260221A060TH00)
- [Boris 同时开 15 个 Claude Code 的秘密](https://cloud.tencent.com/developer/article/2621968)
- [Claude Code 使用笔记 - 多任务并行开发](https://m.blog.csdn.net/qq_33595819/article/details/157430709)
