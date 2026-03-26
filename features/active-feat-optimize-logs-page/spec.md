# spec: feat-optimize-logs-page

## 概述

优化 Tauri 桌面应用的 Logs 页面，移除不需要的会话归档功能，并修复系统日志日期选择不生效的问题。

## 背景

### 当前问题

1. **会话归档功能不需要**：Logs 页面有两个 Tab（Sessions 和 System Logs），Sessions Tab 显示会话归档，但用户不需要此功能。

2. **日期选择不生效**：系统日志（System Logs）的日期选择功能看起来无效。原因是 `SystemLogCollector` 是内存日志收集器，日志只存在于内存中（最多 1000 条），应用重启后历史日志丢失。因此选择历史日期时没有数据。

### 技术分析

**系统日志来源**：
- `SystemLogCollector` (anyclaw/utils/log_collector.py)
- 捕获 Python logging 模块的输出
- 存储在内存 `deque(maxlen=1000)`
- 不持久化

**日期过滤逻辑**：
- 后端 `get_logs()` 有正确的日期过滤：`e.timestamp.startswith(date)`
- 但内存中只有当前运行期间的日志

## 用户价值点

### 价值点 1：简化 Logs 页面

**描述**：移除会话归档 Tab，只保留系统日志功能，简化界面。

**验收场景** (Gherkin):

```gherkin
Scenario: Logs 页面只显示系统日志
  Given 用户打开 Logs 页面
  Then 页面不应显示 Tab 切换器
  And 页面直接显示系统日志内容
  And 页面标题为 "系统日志" 或 "System Logs"

Scenario: 移除会话归档相关代码
  Given Logs 页面已简化
  Then useLogs hook 中移除 sessionLogs 相关逻辑
  And api.ts 中保留 getSystemLogs 但可移除 getSessionLogs（如果其他地方不用）
```

### 价值点 2：修复日期选择功能

**描述**：实现系统日志持久化，使日期选择功能真正有效。

**实现方案**：
- 方案 A：将系统日志写入文件（推荐）
  - 日志文件路径：`~/.anyclaw/logs/system-{date}.log`
  - 格式：JSON Lines（每行一个 JSON 对象）
  - 支持按日期读取历史日志文件

- 方案 B：前端限制日期选择
  - 只允许选择有日志的日期
  - 简单但不解决根本问题

**验收场景** (Gherkin):

```gherkin
Scenario: 选择历史日期可查看对应日志
  Given 系统已运行多天并产生日志
  When 用户选择昨天的日期
  Then 显示昨天的系统日志
  And 日志条目数与当天产生的日志数一致

Scenario: 应用重启后历史日志仍可查看
  Given 系统已产生日志
  When 应用重启
  And 用户选择昨天的日期
  Then 仍可查看昨天的系统日志

Scenario: 日志文件自动按日期分割
  Given 系统正在运行
  When 跨过午夜（日期变更）
  Then 新的日志写入新的日期文件
  And 旧日期文件保持不变
```

## 技术方案

### 1. 简化 Logs 页面

**前端修改** (`tauri-app/src/pages/Logs.tsx`):
- 移除 `activeTab` 状态和 Tab 切换 UI
- 移除 Sessions 相关代码
- 简化组件结构

**Hook 修改** (`tauri-app/src/hooks/useLogs.ts`):
- 移除 `sessionLogs`, `selectedSession` 相关状态和方法
- 保留 `systemLogs`, `loadSystemLogs`, `isLive` 等

### 2. 日志持久化

**后端修改** (`anyclaw/utils/log_collector.py`):
- 新增 `FileLogCollectorHandler` 类
- 日志写入 `~/.anyclaw/logs/system-{YYYY-MM-DD}.jsonl`
- 修改 `get_logs()` 支持读取历史文件

**日志文件格式** (JSON Lines):
```json
{"time": "14:30:00", "level": "INFO", "category": "agent", "message": "...", "timestamp": "2026-03-26T14:30:00"}
```

## 影响范围

- `tauri-app/src/pages/Logs.tsx` - 前端页面
- `tauri-app/src/hooks/useLogs.ts` - Hook 简化
- `tauri-app/src/lib/api.ts` - API 客户端（可选移除 session API）
- `tauri-app/src/types/index.ts` - 类型定义（可选清理）
- `anyclaw/anyclaw/utils/log_collector.py` - 日志持久化
- `anyclaw/anyclaw/api/routes/logs.py` - 后端 API（可选清理）

## 依赖

无

## 优先级

50（普通优化）

## 预估大小

M（2 个价值点，可直接创建）
