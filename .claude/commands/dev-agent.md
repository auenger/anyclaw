---
description: 开发代理，自动执行完整的特性开发流程，从启动到完成
---

# 开发代理

自动执行完整的特性开发流程：start → implement → verify → complete。

## 参数

- `feature-id`: 要开发的特性 ID（如果提供描述则可选）
- `description`: 特性描述（创建新特性）
- `--mode=<mode>`: 执行模式（auto, interactive, step）
- `--start-from=<stage>`: 从特定阶段开始
- `--skip-verify`: 跳过验证阶段
- `--resume`: 从上次中断处恢复

## 执行模式

### 模式 1：完整开发（auto）

从描述创建并开发特性：
```
/dev-agent "用户认证特性"
```

自动执行：
1. new-feature（创建）
2. start-feature（设置）
3. implement-feature（代码）
4. verify-feature（检查）
5. complete-feature（完成）

### 模式 2：继续开发

从现有特性继续：
```
/dev-agent feat-auth
```

检查状态然后：
- 如果 pending：start → implement → verify → complete
- 如果 active：implement → verify → complete
- 如果 blocked：提示解除阻止

### 模式 3：交互式

每个阶段请求确认：
```
/dev-agent feat-auth --mode=interactive
```

## 执行流程

```
┌─────────────────────────────────────────────────────────────────┐
│                      dev-agent 主流程                            │
└─────────────────────────────────────────────────────────────────┘
                              │
                              ▼
                    解析输入并确定模式
                              │
                              ▼
                    检查特性状态
                              │
                              ▼
                    执行阶段（start → implement → verify → complete）
                              │
                              ▼
                    处理错误（暂停、报告、建议修复）
                              │
                              ▼
                    报告完成
```

## 状态持久化

进度保存在 `.dev-progress.yaml`：
```yaml
feature_id: feat-auth
started: 2026-03-02T10:00:00
current_stage: implement-feature
stages:
  start-feature:
    status: completed
    completed_at: 2026-03-02T10:00:05
  implement-feature:
    status: in_progress
    started_at: 2026-03-02T10:00:05
    tasks_completed: [1, 2]
    tasks_pending: [3, 4, 5]
```

## 输出格式

### 完全成功
```
🎉 开发完成！

特性: feat-auth (用户认证)

执行:
  ✓ start-feature (5s)
  ✓ implement-feature (2m 30s)
  ✓ verify-feature (15s)
  ✓ complete-feature (10s)

摘要:
  总计: 3m 00s
  修改文件: 8
  测试通过: 12
  合并到: main

下一个: feat-dashboard (优先级 80)
```

### 部分失败
```
⚠️ 开发中断

特性: feat-auth
失败于: implement-feature
原因: 任务 3 失败

已完成: 2/5 任务

建议:
修复并运行: /dev-agent feat-auth --resume
```

## 示例

```
# 从描述开始
/dev-agent "用户认证，包含登录、注册、登出"

# 继续开发
/dev-agent feat-auth

# 交互模式
/dev-agent feat-auth --mode=interactive

# 错误后恢复
/dev-agent feat-auth --resume
```
