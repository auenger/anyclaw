# Skill: feature-config

## 元信息

| 属性 | 值 |
|------|-----|
| 名称 | feature-config |
| 触发命令 | `/feature-config [key]=[value]` |
| 优先级 | P1 (管理) |
| 依赖 | 无 |

## 功能描述

查看或修改工作流配置。

## 输入参数

| 参数名 | 类型 | 必需 | 默认值 | 描述 |
|--------|------|------|--------|------|
| key | string | 否 | - | 配置项路径 |
| value | any | 否 | - | 新值 |

## 使用模式

### 模式 1: 查看全部配置

```
/feature-config
```

### 模式 2: 查看单个配置

```
/feature-config parallelism.max_concurrent
```

### 模式 3: 修改配置

```
/feature-config parallelism.max_concurrent=3
```

## 可配置项

| 配置路径 | 类型 | 默认值 | 描述 |
|----------|------|--------|------|
| parallelism.max_concurrent | number | 2 | 最大并行数 |
| workflow.auto_start | boolean | true | 自动启动下一个 |
| workflow.require_checklist | boolean | true | 完成前检查 checklist |
| naming.feature_prefix | string | feat | 需求 ID 前缀 |
| naming.branch_prefix | string | feature | 分支前缀 |
| naming.worktree_prefix | string | OA_Tool | worktree 前缀 |

## 执行流程

```
┌─────────────────────────────────────────────────────────────────┐
│ 模式: 查看                                                       │
│ - 读取 config.yaml                                              │
│ - 如果指定了 key，返回该值                                       │
│ - 如果没有 key，返回全部配置                                     │
└─────────────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────────────┐
│ 模式: 修改                                                       │
│ - 读取 config.yaml                                              │
│ - 验证 key 是否有效                                              │
│ - 验证 value 类型是否匹配                                        │
│ - 更新配置                                                       │
│ - 写入 config.yaml                                              │
│ - 如果是 max_concurrent，触发自动调度检查                        │
└─────────────────────────────────────────────────────────────────┘
```

## 输出

### 查看全部

```
┌─────────────────────────────────────────────────────────────────┐
│ Feature Workflow Configuration                                  │
├─────────────────────────────────────────────────────────────────┤
│ parallelism:                                                     │
│   max_concurrent: 2                                              │
│                                                                  │
│ workflow:                                                        │
│   auto_start: true                                               │
│   require_checklist: true                                        │
│                                                                  │
│ naming:                                                          │
│   feature_prefix: feat                                           │
│   branch_prefix: feature                                         │
│   worktree_prefix: OA_Tool                                       │
└─────────────────────────────────────────────────────────────────┘
```

### 查看单个

```
max_concurrent = 2
```

### 修改成功

```yaml
status: success
config:
  key: parallelism.max_concurrent
  old_value: 2
  new_value: 3

message: |
  ✅ 配置已更新

  parallelism.max_concurrent: 2 → 3

  检查是否需要启动更多需求...
  当前活跃: 1/3
  🚀 自动启动: feat-dashboard
```

### 验证失败

```yaml
status: error
error:
  code: INVALID_VALUE
  message: "无效的配置值"
  details: "max_concurrent 必须是正整数，收到: -1"
```

## 错误码

| 错误码 | 描述 |
|--------|------|
| INVALID_KEY | 配置项不存在 |
| INVALID_VALUE | 值类型不匹配或无效 |
| PERMISSION_ERROR | 无权限修改配置 |

## 示例用法

```
用户: /feature-config max_concurrent=3

Agent: ✅ 配置已更新
       max_concurrent: 2 → 3

用户: /feature-config auto_start=false

Agent: ✅ 配置已更新
       auto_start: true → false
```

## 注意事项

1. 修改 max_concurrent 会立即触发调度检查
2. 某些配置可能需要重启才能生效（预留）
3. 建议在修改前先查看当前值
