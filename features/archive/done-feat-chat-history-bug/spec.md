# 对话历史记录持久化 Bug 修复

## 问题描述

用户报告 Tauri 桌面应用中对话历史记录存在以下问题：

1. **历史记录显示不完全**：`api_conv_1774432711585.jsonl` 对话只显示第一次对话的记录，后续对话的新记录丢失
2. **切换对话后历史消失**：在当前对话中继续对话时新消息可以正常渲染，但切换到其他对话再切换回来后，新记录全部消失
3. **重启应用后问题依旧**：重启 Tauri 桌面应用后，历史记录仍然不完整

## 问题分析

### 代码流程分析

1. **前端发送消息流程**：
   - `Chat.tsx` → `send()` → `api.sendMessage()` → 后端 `/api/messages`
   - `conversation_id` 格式：`api:conv_XXX`

2. **后端消息处理流程**：
   - `messages.py` → `InboundMessage` → `ServeManager._process_messages`
   - `SessionAgentPool.get_or_create(session_key)` → `AgentLoop.process()`
   - `AgentLoop.process()` → `session_manager.add_message()`

3. **历史记录加载流程**：
   - 前端 `loadChat(chatId)` → `api.getChat(chatId)` → 后端 `/api/chats/{chatId}`
   - `SessionManager.get(chatId)` → `Session.load(path)`

### 可能的问题点

1. **SessionManager 消息持久化问题**：
   - `SessionManager.add_message()` 调用 `Session.save()` 每次都会覆盖整个文件
   - 如果保存过程中发生异常，可能导致消息丢失

2. **Session 对象缓存与磁盘不同步**：
   - `SessionManager.get_or_create()` 优先使用内存缓存
   - 如果内存中的 Session 对象与磁盘文件不同步，可能导致数据不一致

3. **AgentLoop 实例复用问题**：
   - `SessionAgentPool` 复用 AgentLoop 实例
   - 每个实例有独立的 `session_manager`
   - 可能存在实例间的 session 数据不同步

4. **前端状态管理问题**：
   - `loadChat` 时如果 API 返回空消息，会用空数组覆盖当前消息

## 用户价值点

### 价值点 1：消息正确持久化到 JSONL 文件

**验收场景**：
```gherkin
Feature: 消息持久化

Scenario: 用户发送消息后消息被保存到 JSONL 文件
  Given 用户在对话 "api:conv_123456" 中
  When 用户发送消息 "你好"
  Then 消息应该被追加到 sessions/api_conv_123456.jsonl 文件
  And 文件应该包含完整的 user 和 assistant 消息

Scenario: 多次对话后所有消息都被保存
  Given 用户在对话 "api:conv_123456" 中
  When 用户发送第一条消息 "你好"
  And 助手回复 "你好！有什么可以帮助你的？"
  And 用户发送第二条消息 "今天天气怎么样？"
  And 助手回复 "抱歉，我无法获取实时天气信息"
  Then JSONL 文件应该包含 4 条消息记录（2 user + 2 assistant）
```

### 价值点 2：历史记录正确加载显示

**验收场景**：
```gherkin
Feature: 历史记录加载

Scenario: 切换对话后历史记录完整显示
  Given 用户在对话 A 中有 10 条历史消息
  And 用户切换到对话 B
  When 用户切换回对话 A
  Then 对话 A 的 10 条历史消息应该完整显示

Scenario: 重启应用后历史记录完整加载
  Given 用户在对话 "api:conv_123456" 中有历史消息
  When 用户重启 Tauri 桌面应用
  And 用户打开对话 "api:conv_123456"
  Then 所有历史消息应该完整加载并显示
```

### 价值点 3：前后端状态同步

**验收场景**：
```gherkin
Feature: 状态同步

Scenario: SSE 实时消息与历史记录同步
  Given 用户在对话 A 中发送消息
  When SSE 返回助手回复
  Then 消息应该同时保存到 SessionManager
  And 切换对话再切换回来后消息应该仍然存在
```

## 大小评估

**S** - 3 个价值点，但可能需要深入调试定位根本原因

## 根本原因分析

**问题根因**：`SessionAgentPool` 中的每个 `AgentLoop` 创建独立的 `SessionManager` 实例，导致：

1. 消息被保存到 `SessionAgentPool` 中 `AgentLoop` 的 `SessionManager` 内存缓存
2. 但 API `/api/chats/{chatId}` 读取历史时使用 `ServeManager.agent.session_manager`（不同的实例）
3. 两个 `SessionManager` 实例的内存缓存不同步

虽然它们共享同一个磁盘目录，但由于内存缓存的存在：
- Pool 中 AgentLoop 的 SessionManager 缓存了最新的 session 数据
- 主 AgentLoop 的 SessionManager 缓存可能是旧的或空的
- API 优先使用内存缓存，导致返回旧数据

## 修复方案

**核心修改**：让所有 AgentLoop 共享同一个 SessionManager 实例

### 修改文件

1. **`anyclaw/agent/loop.py`**
   - 添加 `session_manager` 参数，支持外部注入
   - 如果注入了外部 SessionManager，直接使用；否则内部创建

2. **`anyclaw/core/session_pool.py`**
   - 添加 `session_manager` 参数
   - 创建 AgentLoop 时传递共享的 SessionManager

3. **`anyclaw/core/serve.py`**
   - 创建共享的 SessionManager 实例
   - 传递给主 AgentLoop 和 SessionAgentPool

### 代码变更摘要

```python
# AgentLoop.__init__
def __init__(
    self,
    ...
    session_manager: Optional["SessionManager"] = None,  # 新增参数
):
    self.session_manager = session_manager  # 优先使用外部注入
    if self.session_manager:
        logger.info("AgentLoop using shared SessionManager")
    elif enable_session_manager:
        # 内部创建 SessionManager
        ...

# SessionAgentPool.__init__
def __init__(
    self,
    ...
    session_manager: Optional["SessionManager"] = None,  # 新增参数
):
    self._shared_session_manager = session_manager

# SessionAgentPool.get_or_create
agent = AgentLoop(
    ...
    session_manager=self._shared_session_manager,  # 使用共享的 SessionManager
)

# ServeManager.initialize
shared_session_manager = SessionManager(session_config)
self.agent = AgentLoop(..., session_manager=shared_session_manager)
self._session_pool = SessionAgentPool(..., session_manager=shared_session_manager)
```

## 技术栈

- 后端：Python 3.11+, FastAPI, JSONL 持久化
- 前端：React, TypeScript, Zustand
- 桌面：Tauri 2.0
