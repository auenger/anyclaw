# Skill: list-features

## 元信息

| 属性 | 值 |
|------|-----|
| 名称 | list-features |
| 触发命令 | `/list-features` |
| 优先级 | P0 (核心) |
| 依赖 | 无 |

## 功能描述

查看所有需求的状态，包括：
- 活跃需求（正在开发）
- 待处理需求（排队中）
- 阻塞需求（有依赖或手动阻塞）
- 已归档需求（已完成）

## 输入参数

| 参数名 | 类型 | 必需 | 默认值 | 描述 |
|--------|------|------|--------|------|
| filter | string | 否 | all | 筛选: all/active/pending/blocked/archived |
| format | string | 否 | table | 输出格式: table/json/simple |

## 执行流程

```
┌─────────────────────────────────────────────────────────────────┐
│ Step 1: 读取数据                                                 │
│ - 读取 config.yaml (获取 max_concurrent)                        │
│ - 读取 queue.yaml (获取 active, pending, blocked)               │
│ - 读取 archive-log.yaml (获取 archived)                         │
└─────────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────────┐
│ Step 2: 计算统计                                                 │
│ - active_count = queue.active.length                            │
│ - pending_count = queue.pending.length                          │
│ - blocked_count = queue.blocked.length                          │
│ - archived_count = archive.archived.length                      │
│ - available_slots = max_concurrent - active_count               │
└─────────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────────┐
│ Step 3: 格式化输出                                               │
│ - 根据 format 参数选择输出格式                                   │
│ - 根据 filter 参数筛选显示内容                                   │
└─────────────────────────────────────────────────────────────────┘
```

## 输出

### Table 格式（默认）

```
┌─────────────────────────────────────────────────────────────────┐
│ Feature Workflow Status                                         │
│ 并行: 1/2  |  可用槽位: 1                                        │
├─────────────────────────────────────────────────────────────────┤
│ Active (1)                                                       │
│ ┌───────────────────────────────────────────────────────────────┤
│ │ ● feat-auth       [90]  2h ago  ../OA_Tool-feat-auth         │
└─────────────────────────────────────────────────────────────────┘
│                                                                  │
│ Pending (2)                                                      │
│ ┌───────────────────────────────────────────────────────────────┤
│ │ ○ feat-dashboard  [80]  1d ago                               │
│ │ ○ feat-report     [70]  3h ago                               │
└─────────────────────────────────────────────────────────────────┘
│                                                                  │
│ Blocked (1)                                                      │
│ ┌───────────────────────────────────────────────────────────────┤
│ │ ⊘ feat-export     [60]  依赖 feat-auth                       │
└─────────────────────────────────────────────────────────────────┘
│                                                                  │
│ Archived: 3                                                      │
└─────────────────────────────────────────────────────────────────┘
```

### JSON 格式

```json
{
  "meta": {
    "max_concurrent": 2,
    "active_count": 1,
    "available_slots": 1
  },
  "active": [
    {
      "id": "feat-auth",
      "name": "用户认证",
      "priority": 90,
      "started": "2026-03-02T08:00:00",
      "elapsed": "2h",
      "worktree": "../OA_Tool-feat-auth"
    }
  ],
  "pending": [
    {
      "id": "feat-dashboard",
      "name": "仪表盘",
      "priority": 80,
      "created": "2026-03-01T14:00:00"
    },
    {
      "id": "feat-report",
      "name": "报表",
      "priority": 70,
      "created": "2026-03-02T06:00:00"
    }
  ],
  "blocked": [
    {
      "id": "feat-export",
      "priority": 60,
      "reason": "依赖 feat-auth"
    }
  ],
  "archived_count": 3
}
```

### Simple 格式

```
Active (1/2):
  feat-auth [90] - 2h ago

Pending:
  feat-dashboard [80]
  feat-report [70]

Blocked:
  feat-export - 依赖 feat-auth

Archived: 3
```

## 状态符号说明

| 符号 | 状态 | 描述 |
|------|------|------|
| ● | active | 正在开发 |
| ○ | pending | 等待中 |
| ⊘ | blocked | 阻塞中 |
| ✓ | done | 已完成 |

## 时间格式化

```
< 1分钟:  just now
< 1小时:  5m ago
< 24小时: 2h ago
< 7天:    3d ago
>= 7天:   2w ago
```

## 筛选选项

| Filter | 显示内容 |
|--------|----------|
| all | 全部（默认） |
| active | 仅活跃 |
| pending | 仅待处理 |
| blocked | 仅阻塞 |
| archived | 仅已归档 |

## 示例用法

### 示例 1: 查看全部

```
用户: /list-features

Agent: (显示完整的表格)
```

### 示例 2: 只看活跃

```
用户: /list-features --filter=active

Agent:
┌─────────────────────────────────────────────────────────────────┐
│ Active (1/2)                                                     │
├─────────────────────────────────────────────────────────────────┤
│ ● feat-auth       [90]  2h ago  ../OA_Tool-feat-auth           │
└─────────────────────────────────────────────────────────────────┘
```

### 示例 3: JSON 输出

```
用户: /list-features --format=json

Agent: {"meta": {...}, "active": [...], ...}
```

## 注意事项

1. **时间计算**: 使用相对时间，便于快速了解状态
2. **排序**: pending 按 priority 降序显示
3. **空状态**: 如果某类别为空，不显示该类别
4. **性能**: 只读取必要的文件，不遍历目录
