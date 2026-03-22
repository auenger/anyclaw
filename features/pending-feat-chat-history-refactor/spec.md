# feat-chat-history-refactor: 对话历史列表重构

## 概述

重构优化对话历史列表系统，实现「一对话一文件」的独立会话管理，支持新建对话、历史对话加载、上下文自动压缩。

## 核心理念

```
每个对话 = 独立的 session 文件
新建对话 = 干净的上下文（SOUL.md + USER.md + MEMORY.md）
继续对话 = 加载历史 + 自动压缩（如果太长）
```

## 数据模型

### Session Key 格式

```
格式: {channel}:{conversation_id}

示例:
  api:conv_1711084800              # App 创建的对话
  api:conv_1711090000              # App 另一个对话
  cli:conv_1711100000              # CLI 创建的对话
  discord:channel_123:conv_001     # Discord 频道（/new 后）
  discord:channel_123:conv_002     # Discord 同频道另一个对话
  feishu:group_abc:conv_001        # 飞书群组
```

**说明**：
- 单用户场景优先，不按用户 ID 分组
- Discord/IM 渠道用 `/new` 指令开启新对话
- 历史对话通过 App/CLI 查看，Discord 用户不直接切换

### 文件存储

```
~/.anyclaw/workspace/sessions/
├── api_conv_1711084800.jsonl         # App 对话 1
├── api_conv_1711090000.jsonl         # App 对话 2
├── cli_conv_1711100000.jsonl         # CLI 对话
├── discord_channel_123_conv_001.jsonl  # Discord 对话 1
├── discord_channel_123_conv_002.jsonl  # Discord 对话 2
└── ...
```

### `/new` 指令行为

```
用户: /new
    ↓
生成新 conversation_id
    ↓
Session Key: {channel}:{new_conv_id}
    ↓
上下文 = SOUL.md + USER.md + MEMORY.md（干净）
    ↓
开始新对话
```

### ChatItem 数据结构

```typescript
interface ChatItem {
  chat_id: string           // 完整 session key，如 "api:conv_1711084800"
  conversation_id: string   // 短 ID，如 "conv_1711084800"
  name: string              // 显示名称，如 "Chat 3月22日"
  agent_id: string          // Agent ID
  channel: string           // 来源渠道
  last_message_time: string // 最后消息时间
  last_message: string | null  // 最后消息预览
  message_count: number     // 消息数量
  avatar: string | null
  created_at: string        // 创建时间
}
```

## 用户价值点

### VP1: 新建对话 - 独立会话

每次新建对话都是独立的，有唯一的 conversation_id，不会混在一起。

```gherkin
Feature: 新建独立对话

  Scenario: 用户创建新对话
    Given 用户在 App 中点击"新建对话"
    When 前端生成 conversation_id = "conv_1711084800"
    And 用户发送第一条消息 "你好"
    Then 后端应创建 session: "api:conv_1711084800"
    And 上下文应只包含 SOUL.md + USER.md + MEMORY.md
    And 不应包含其他对话的历史消息
    And session 文件应保存为 "api_conv_1711084800.jsonl"

  Scenario: 用户创建第二个对话
    Given 已存在对话 "api:conv_1711084800"
    When 用户再次点击"新建对话"并发送消息
    Then 应创建新的 session: "api:conv_1711090000"
    And 两个对话应完全独立
```

### VP2: 历史对话加载

点击历史对话能正确加载消息，支持自动压缩超长历史。

```gherkin
Feature: 加载历史对话

  Scenario: 加载短历史对话
    Given 对话 "api:conv_1711084800" 有 10 条消息
    When 用户点击该对话
    Then 应加载全部 10 条消息
    And 消息顺序正确（按时间正序）

  Scenario: 加载超长历史对话（自动压缩）
    Given 对话 "api:conv_1711000000" 有 100 条消息
    And 总 token 数超过上下文限制
    When 用户点击该对话并发送新消息
    Then 后端应自动压缩历史（切分或摘要）
    And 上下文 = SOUL.md + USER.md + MEMORY.md + 压缩后的历史
    And 用户能正常继续对话

  Scenario: 历史对话的后续消息
    Given 用户正在对话 "api:conv_1711084800"
    When 用户发送新消息
    Then 新消息应追加到该 session 文件
    And 不应创建新 session
```

### VP3: 对话列表优化

对话列表显示友好的信息，方便用户找到历史对话。

```gherkin
Feature: 对话列表显示

  Scenario: 显示对话列表
    Given 存在 3 个历史对话
    When 用户查看对话列表
    Then 应按最后更新时间排序（最近的在上面）
    And 显示对话名称（如 "Chat 3月22日 14:30"）
    And 显示最后消息预览（前 50 字符）
    And 显示消息数量

  Scenario: 按日期分组
    Given 存在今天、昨天、更早的对话
    When 用户查看对话列表
    Then 应分组显示：今天、昨天、更早
```

### VP4: Discord/IM 渠道 `/new` 指令

Discord 和其他 IM 渠道通过 `/new` 指令开启新对话。

```gherkin
Feature: Discord /new 指令

  Scenario: Discord 频道首次消息
    Given Discord 频道 #general
    When 用户发送第一条消息 "你好"
    Then 应自动创建 session "discord:channel_123:conv_001"
    And 正常回复

  Scenario: Discord 使用 /new 开启新对话
    Given Discord 频道当前对话为 conv_001
    When 用户发送 "/new"
    Then 应创建新 session "discord:channel_123:conv_002"
    And 回复 "✅ 已开始新对话"
    And 上下文重置（干净）

  Scenario: Discord 继续当前对话
    Given Discord 频道当前对话为 conv_002
    When 用户发送消息 "继续"
    Then 消息应追加到 conv_002
    And 不应创建新 session
```

### VP4: Discord/IM 渠道 /new 指令

Discord 和其他 IM 渠道通过 `/new` 指令开启新对话。

```gherkin
Feature: Discord /new 指令

  Scenario: Discord 频道首次消息
    Given Discord 频道 #general 无历史对话
    When 用户发送消息 "你好"
    Then 后端应自动创建 session: "discord:channel_123:conv_001"
    And 保存消息到该 session

  Scenario: Discord 用户发送 /new
    Given Discord 频道已有对话 "discord:channel_123:conv_001"
    When 用户发送 "/new"
    Then 后端应创建新 session: "discord:channel_123:conv_002"
    And 回复 "✅ 已开始新对话"
    And 上下文重置（SOUL.md + USER.md + MEMORY.md）

  Scenario: Discord 继续当前对话
    Given Discord 频道当前对话为 "discord:channel_123:conv_002"
    When 用户发送消息 "继续"
    Then 消息应追加到 conv_002
    And 不应创建新 session

  Scenario: Discord 渠道 session key 格式
    Given 多个 IM 渠道
    Then Discord 应使用 "discord:{channel_id}:{conv_id}"
    And 飞书应使用 "feishu:{group_id}:{conv_id}"
    And CLI 应使用 "cli:{conv_id}"
```

## 技术方案

### 1. 前端修改

#### chatCtx.tsx

```typescript
// 新建对话：生成唯一 ID
const newChat = useCallback(() => {
  const newChatId = `conv_${Date.now()}`
  setActiveChatId(newChatId)
  initChat(newChatId)  // 初始化空的本地状态
}, [setActiveChatId, initChat])

// 发送消息：使用 activeChatId 或生成新 ID
const send = useCallback(async (prompt: string, attachments?: Attachment[]) => {
  const effectiveChatId = activeChatId ?? `conv_${Date.now()}`
  // ...
}, [activeChatId, ...])
```

#### api.ts

```typescript
// 发送消息时传递 conversation_id
async sendMessage(agentId: string, content: string, conversationId?: string): Promise<{ message_id: string }> {
  const response = await fetch(`${this.baseUrl}/api/messages`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({
      agent_id: agentId,
      content,
      conversation_id: conversationId,  // 传递给后端
    }),
  })
  return response.json()
}
```

### 2. 后端修改

#### serve.py

```python
# 已正确实现
session_key = f"{msg.channel}:{msg.chat_id}"  # 如 "api:conv_1711084800"
self.agent.set_session_key(session_key)
```

#### chats.py

```python
def _session_to_chat_item(session_info: dict) -> ChatItem:
    key = session_info.get("key", "")
    # "api:conv_1711084800" → channel="api", conversation_id="conv_1711084800"
    parts = key.split(":", 1)
    channel = parts[0] if len(parts) == 2 else "cli"
    conversation_id = parts[1] if len(parts) == 2 else key

    # 生成友好的显示名称
    name = _generate_chat_name(session_info)

    return ChatItem(
        chat_id=key,  # 完整 key
        conversation_id=conversation_id,
        name=name,
        # ...
    )
```

### 3. 历史压缩策略

当对话历史超过 token 限制时：

```python
# 方案 A：切分（保留最近 N 条）
def truncate_history(messages: list, max_messages: int = 20) -> list:
    return messages[-max_messages:]

# 方案 B：摘要（LLM 压缩）
async def summarize_history(messages: list, agent: AgentLoop) -> str:
    summary_prompt = f"请总结以下对话的关键信息：\n{format_messages(messages)}"
    return await agent.call_llm(summary_prompt)
```

## 影响范围

### 前端
- `tauri-app/src/hooks/chatCtx.tsx` - 新建对话逻辑
- `tauri-app/src/lib/api.ts` - API 调用
- `tauri-app/src/lib/chat-utils.ts` - 工具函数

### 后端
- `anyclaw/api/routes/chats.py` - API 端点
- `anyclaw/session/manager.py` - Session 管理

## 验收标准

- [ ] 新建对话生成唯一 conversation_id
- [ ] 每个对话保存到独立的 session 文件
- [ ] 对话列表显示所有历史对话
- [ ] 点击对话能加载历史消息
- [ ] 超长历史能自动压缩
- [ ] 继续对话时消息追加到正确的 session
- [ ] 删除对话能正确清理 session 文件
