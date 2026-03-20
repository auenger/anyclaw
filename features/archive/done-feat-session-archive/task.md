# 任务分解

## Phase 1: 核心数据结构

### Task 1.1: 创建会话模块结构
- [ ] 创建 `anyclaw/session/__init__.py`
- [ ] 定义模块公共接口

### Task 1.2: 记录类型定义
- [ ] 创建 `anyclaw/session/records.py`
- [ ] 实现 `SessionRecord` 基类
- [ ] 实现 `SessionStart` / `SessionEnd`
- [ ] 实现 `UserMessage` / `AssistantMessage`
- [ ] 实现 `ToolCall` / `ToolResult`
- [ ] 实现 `SkillCall` / `SkillResult`
- [ ] 实现 `Thinking` / `ErrorRecord`

### Task 1.3: 记录类型测试
- [ ] 创建 `tests/test_session_records.py`
- [ ] 测试序列化/反序列化
- [ ] 测试字段验证

## Phase 2: 会话管理器

### Task 2.1: 项目识别逻辑
- [ ] 创建 `anyclaw/session/project.py`
- [ ] 实现 `find_git_root()` 函数
- [ ] 实现 `get_project_identifier()` 函数
- [ ] 实现 `make_safe_dirname()` 函数

### Task 2.2: 会话管理器核心
- [ ] 创建 `anyclaw/session/manager.py`
- [ ] 实现 `SessionManager` 类
- [ ] 实现 `start_session()` / `end_session()`
- [ ] 实现 `_get_session_file_path()`
- [ ] 实现 `_append_record()`

### Task 2.3: 消息记录方法
- [ ] 实现 `record_user_message()`
- [ ] 实现 `record_assistant_message()`
- [ ] 实现 `record_tool_call()` / `record_tool_result()`
- [ ] 实现 `record_skill_call()` / `record_skill_result()`

### Task 2.4: 会话管理器测试
- [ ] 创建 `tests/test_session_manager.py`
- [ ] 测试会话开始/结束
- [ ] 测试消息记录
- [ ] 测试工具调用记录
- [ ] 测试项目隔离

## Phase 3: Agent 集成

### Task 3.1: History 类改造
- [ ] 修改 `anyclaw/agent/history.py`
- [ ] 集成 `SessionManager`
- [ ] 保持向后兼容

### Task 3.2: AgentLoop 集成
- [ ] 修改 `anyclaw/agent/loop.py`
- [ ] 在 process 开始时记录 user message
- [ ] 在 process 结束时记录 assistant message
- [ ] 工具调用前后记录 tool_call/tool_result

### Task 3.3: Channel 集成
- [ ] 修改 CLI Channel
- [ ] 修改飞书 Channel（如有）
- [ ] 修改 Discord Channel（如有）

### Task 3.4: 集成测试
- [ ] 创建 `tests/test_session_integration.py`
- [ ] 端到端测试 CLI 会话
- [ ] 测试跨日会话
- [ ] 测试多项目切换

## Phase 4: CLI 命令

### Task 4.1: session list 命令
- [ ] 创建 `anyclaw/cli/session.py`
- [ ] 实现会话列表查询
- [ ] 支持 --date / --project 过滤
- [ ] Rich 表格输出

### Task 4.2: session show 命令
- [ ] 实现会话详情显示
- [ ] 支持 tree/json/markdown 格式
- [ ] 显示调用链结构

### Task 4.3: session search 命令
- [ ] 实现关键词搜索
- [ ] 支持 --tool 过滤
- [ ] 高亮匹配结果

### Task 4.4: session export 命令
- [ ] 实现 Markdown 导出
- [ ] 实现 JSON 导出
- [ ] 支持指定输出文件

### Task 4.5: session clean 命令
- [ ] 实现旧会话清理
- [ ] 支持 --dry-run
- [ ] 支持 --days 参数

### Task 4.6: CLI 测试
- [ ] 测试各 CLI 命令
- [ ] 测试参数解析

## Phase 5: 索引优化（可选）

### Task 5.1: 日期索引
- [ ] 实现 `_update_date_index()`
- [ ] 索引文件格式设计

### Task 5.2: SQLite 索引（可选）
- [ ] 创建索引数据库 schema
- [ ] 实现增量索引更新
- [ ] 支持快速全文搜索

## 依赖关系

```
Phase 1 (数据结构)
    │
    ↓
Phase 2 (会话管理器) ───→ Phase 4 (CLI 命令)
    │                        ↑
    ↓                        │
Phase 3 (Agent 集成) ────────┘
    │
    ↓
Phase 5 (索引优化) - 可选
```

## 预计工作量

- Phase 1: 核心数据结构 - 1-2 小时
- Phase 2: 会话管理器 - 3-4 小时
- Phase 3: Agent 集成 - 2-3 小时
- Phase 4: CLI 命令 - 2-3 小时
- Phase 5: 索引优化 - 2 小时（可选）
- **总计: 8-14 小时**
