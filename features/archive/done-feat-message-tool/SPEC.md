# feat-message-tool

**状态**: ✅ 已完成
**完成时间**: 2026-03-20
**优先级**: 75
**大小**: S
**提交**: 9ba8bc4, b8c5e27

## 描述

实现 MessageTool 跨会话消息工具，支持向其他会话/频道发送消息，与 nanobot 的 MessageTool 保持兼容。

## 价值点

1. **跨会话消息发送**
   - 向指定 channel/chat_id 发送消息
   - 支持异步发送
   - 自动路由到对应 Channel

2. **媒体附件支持**
   - 图片附件 (images)
   - 音频附件 (audio)
   - 文档附件 (documents)

3. **消息引用**
   - 回复特定消息 (reply_to)
   - 消息引用链追踪

4. **防重复发送**
   - per-turn 发送追踪
   - 避免同一轮对话重复发送

## 实现文件

- `anyclaw/agent/tools/message.py` - MessageTool 核心实现
- `anyclaw/agent/loop.py` - AgentLoop 集成 (set_message_context)
- `anyclaw/channels/discord.py` - Discord Channel 集成
- `anyclaw/channels/feishu.py` - 飞书 Channel 集成
- `anyclaw/config/settings.py` - 配置项 (enable_message_tool)

## 配置项

```json
{
  "enable_message_tool": true
}
```

## 使用示例

```python
from anyclaw.agent.tools.message import MessageTool

# 在 Channel 中设置上下文
message_tool.set_context(
    channel="discord",
    chat_id="123456789",
    message_id="987654321"
)

# 发送文本消息
result = await message_tool.execute(
    action="send",
    content="Hello from AnyClaw!"
)

# 发送带附件的消息
result = await message_tool.execute(
    action="send",
    content="Check this image",
    images=["/tmp/screenshot.png"]
)

# 回复消息
result = await message_tool.execute(
    action="send",
    content="This is a reply",
    reply_to="123456789"
)
```

## MessageTool 接口

```python
class MessageTool(BaseTool):
    name = "message"
    description = "向其他会话或频道发送消息"

    async def execute(
        self,
        action: str,           # "send" | "reply"
        content: str,          # 消息内容
        channel: str = None,   # 目标频道 (可选，默认当前)
        chat_id: str = None,   # 目标会话 (可选，默认当前)
        reply_to: str = None,  # 回复的消息 ID
        images: List[str] = None,    # 图片路径
        audio: List[str] = None,     # 音频路径
        documents: List[str] = None  # 文档路径
    ) -> Dict[str, Any]:
        pass
```

## 架构流程

```
AgentLoop → MessageTool.execute(action="send", content="...")
    ↓
检查 message_sent_in_turn() (防重复)
    ↓
调用 Channel 回调 (DiscordChannel._send_message_callback)
    ↓
Discord/Feishu API 发送消息
    ↓
返回发送结果
```

## Channel 集成

### Discord

```python
# DiscordChannel 中设置上下文
def _handle_message_create(self, message):
    self.agent_loop.set_message_context(
        channel="discord",
        chat_id=str(message.channel.id),
        message_id=str(message.id)
    )
```

### 飞书

```python
# FeishuChannel 中设置上下文
def _handle_message(self, event):
    self.agent_loop.set_message_context(
        channel="feishu",
        chat_id=event.message.chat_id,
        message_id=event.message.message_id
    )
```

## 测试

```
tests/test_message_tool.py
```

## 与 nanobot 对比

| 特性 | nanobot | AnyClaw | 状态 |
|------|---------|---------|------|
| 跨会话发送 | ✅ | ✅ | 完全兼容 |
| 媒体附件 | ✅ | ✅ | 完全兼容 |
| Reply-to | ✅ | ✅ | 完全兼容 |
| Channel 集成 | ✅ | ✅ | 完全兼容 |
| 防重复发送 | ✅ | ✅ | 完全兼容 |
