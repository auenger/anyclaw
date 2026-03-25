# Logs 页面功能实现

## 概述

为 Tauri 桌面应用的 Logs 页面实现完整的日志查看功能，支持会话归档日志和系统运行日志的查看、过滤和搜索。

## 用户价值点

### 价值点 1：后端 Logs API

创建 `/api/logs` 相关端点，暴露 SessionArchiveManager 功能并新增系统日志收集器。

**Gherkin 场景：**

```gherkin
Feature: Logs API

  Scenario: 获取会话归档日志
    Given 用户已启动 sidecar 服务
    When 请求 GET /api/logs/sessions?date=2024-03-21
    Then 返回指定日期的会话归档列表
    And 每个会话包含 session_id, project_id, started_at 等信息

  Scenario: 获取会话详情
    Given 用户已启动 sidecar 服务
    And 存在会话 ID "abc123"
    When 请求 GET /api/logs/sessions/abc123
    Then 返回该会话的所有记录
    And 包含 user_message, assistant_message, tool_call 等类型

  Scenario: 获取系统运行日志
    Given 用户已启动 sidecar 服务
    When 请求 GET /api/logs/system?level=ERROR&date=2024-03-21
    Then 返回指定日期的 ERROR 级别系统日志
    And 每条日志包含 time, level, category, message

  Scenario: 搜索会话日志
    Given 用户已启动 sidecar 服务
    When 请求 GET /api/logs/sessions/search?q=ReadFileTool
    Then 返回包含 "ReadFileTool" 的会话记录
    And 标注来源会话 ID

  Scenario: 实时日志流
    Given 用户已启动 sidecar 服务
    When 连接 SSE /api/logs/stream
    Then 实时推送新的日志条目
    And 支持按 category 过滤
```

### 价值点 2：前端 Logs 页面完整实现

对接后端 API，实现日志查看界面，支持会话日志和系统日志切换。

**Gherkin 场景：**

```gherkin
Feature: Logs 页面

  Scenario: 查看今日会话日志
    Given 用户打开 Logs 页面
    When 页面加载完成
    Then 默认显示"会话归档"标签
    And 显示今日的会话列表
    And 显示 "Live" 实时指示器

  Scenario: 切换到系统日志
    Given 用户打开 Logs 页面
    When 点击"系统日志"标签
    Then 显示系统运行日志列表
    And 支持按级别过滤 (DEBUG/INFO/WARN/ERROR)

  Scenario: 按日期过滤
    Given 用户打开 Logs 页面
    When 选择日期 "2024-03-20"
    Then 显示该日期的日志
    And "Live" 指示器消失（非今日）

  Scenario: 按类别过滤
    Given 用户打开 Logs 页面
    When 点击类别按钮 "tool"
    Then 只显示 tool 类别的日志
    And 更新日志条数统计

  Scenario: 搜索日志
    Given 用户打开 Logs 页面
    When 在搜索框输入 "error" 并回车
    Then 过滤显示包含 "error" 的日志条目

  Scenario: 展开日志详情
    Given 用户打开 Logs 页面
    And 存在带有 details 的日志条目
    When 点击该日志条目
    Then 展开显示 JSON 格式的详情信息
    And 再次点击可收起

  Scenario: 查看会话详情
    Given 用户正在查看会话归档列表
    When 点击某个会话条目
    Then 显示该会话的完整记录
    And 可返回列表视图
```

## 技术设计

### 后端 API 设计

```
# Session Logs API
GET    /api/logs/sessions              # 获取会话列表
GET    /api/logs/sessions/:id          # 获取会话详情
GET    /api/logs/sessions/search       # 搜索会话内容

# System Logs API
GET    /api/logs/system                # 获取系统日志
GET    /api/logs/stream                # SSE 实时日志流

# 统计 API
GET    /api/logs/stats                 # 获取日志统计
```

### 系统日志收集器设计

```python
class SystemLogCollector:
    """收集 Python logging 模块的日志"""

    def __init__(self, max_entries: int = 1000):
        self.entries: List[LogEntry] = []
        self.max_entries = max_entries

    def add_handler(self):
        """添加自定义 Handler 到 logging"""

    def get_logs(self, level: str, date: str) -> List[LogEntry]:
        """获取过滤后的日志"""

    def stream_logs(self):
        """生成器，实时推送日志"""
```

### 前端组件结构

```
src/pages/Logs.tsx
├── Header
│   ├── Title + Live Indicator
│   ├── DatePicker
│   ├── CategoryFilter
│   ├── LevelFilter
│   └── SearchInput
├── TabSwitcher (会话归档 / 系统日志)
└── LogContent
    ├── SessionLogList (会话归档)
    │   └── SessionItem (可展开)
    └── SystemLogList (系统日志)
        └── LogEntry (可展开详情)
```

### 日志数据结构

```typescript
// 会话归档日志
interface SessionLog {
  session_id: string
  project_id: string
  channel: string
  started_at: string
  message_count: number
  tool_call_count: number
}

// 系统运行日志
interface SystemLogEntry {
  time: string
  level: 'DEBUG' | 'INFO' | 'WARN' | 'ERROR'
  category: 'agent' | 'tool' | 'task' | 'system'
  agent?: string
  message: string
  details?: Record<string, unknown>
}
```

## 依赖

- feat-memory-pages（建议先完成，复用 API 模式）

## 验收标准

- [ ] 后端 API 全部实现并通过测试
- [ ] 前端页面正确对接 API
- [ ] 支持会话归档日志查看
- [ ] 支持系统运行日志查看
- [ ] 支持日期、类别、级别过滤
- [ ] 支持日志搜索功能
- [ ] 支持 SSE 实时日志流（今日日志）
- [ ] 支持 i18n 国际化
