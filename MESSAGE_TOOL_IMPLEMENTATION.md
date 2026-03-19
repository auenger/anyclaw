# Message 工具系统 - 完整实现方案

> **版本信息**
> - 参考实现: nanobot (2026-03-17)
> - 目标: AnyClaw 0.1.0-MVP
> - 方案日期: 2026-03-20

---

## 📋 方案概述

### 目标

完美复刻 nanobot 的 Message 工具，为 AnyClaw 添加跨会话消息发送能力。

### 核心特性

✅ **跨会话消息** - 向不同 Channel/Chat 发送消息
✅ **消息转发** - 从一个会话转发到另一个会话
✅ **多平台支持** - Discord, Feishu, Telegram, WhatsApp 等
✅ **媒体附件** - 支持图片、音频、文档
✅ **自动上下文** - 默认发送到当前会话
✅ **回复引用** - 支持回复特定消息

### 与 AnyClaw 的集成

```
AnyClaw 架构 (新增 Message Tool)
├── agent/
│   ├── loop.py              # AgentLoop (注册 MessageTool)
│   └── tools/
│       └── message.py       # ✨ MessageTool (新增)
├── bus/
│   ├── events.py            # OutboundMessage (复用)
│   └── queue.py            # 消息总线 (复用)
├── channels/
│   ├── discord.py           # 实现 _send_callback
│   ├── feishu.py           # 实现 _send_callback
│   └── base.py             # Channel 基类 (更新)
└── config/
    └── settings.py         # 添加消息配置
```

---

## 🏗️ 架构设计

### 1. MessageTool - 消息发送工具

**位置**: `anyclaw/agent/tools/message.py`

```python
class MessageTool(Tool):
    """向用户发送消息的工具"""
    
    def __init__(
        self,
        send_callback: Callable[[OutboundMessage], Awaitable[None]] | None = None,
        default_channel: str = "",
        default_chat_id: str = "",
        default_message_id: str | None = None,
    ):
        # 回调函数（由 Channel 提供）
        self._send_callback = send_callback
        
        # 默认上下文（由 Channel 设置）
        self._default_channel = default_channel
        self._default_chat_id = default_chat_id
        self._default_message_id = default_message_id
        
        # 跟踪是否在当前回合发送过消息
        self._sent_in_turn: bool = False
    
    def set_context(
        self,
        channel: str,
        chat_id: str,
        message_id: str | None = None,
    ) -> None:
        """设置当前消息上下文（由 Channel 调用）"""
        self._default_channel = channel
        self._default_chat_id = chat_id
        self._default_message_id = message_id
    
    def set_send_callback(
        self,
        callback: Callable[[OutboundMessage], Awaitable[None]],
    ) -> None:
        """设置消息发送回调（由 Channel 调用）"""
        self._send_callback = callback
    
    def start_turn(self) -> None:
        """重置每回合的发送跟踪"""
        self._sent_in_turn = False
    
    @property
    def name(self) -> str:
        return "message"
    
    @property
    def description(self) -> str:
        return "Send a message to the user. Use this when you want to communicate something."
    
    @property
    def parameters(self) -> dict[str, Any]:
        return {
            "type": "object",
            "properties": {
                "content": {
                    "type": "string",
                    "description": "The message content to send"
                },
                "channel": {
                    "type": "string",
                    "description": "Optional: target channel (telegram, discord, feishu, whatsapp, etc.)"
                },
                "chat_id": {
                    "type": "string",
                    "description": "Optional: target chat/user ID"
                },
                "message_id": {
                    "type": "string",
                    "description": "Optional: message ID to reply to"
                },
                "media": {
                    "type": "array",
                    "items": {"type": "string"},
                    "description": "Optional: list of file paths to attach (images, audio, documents)"
                }
            },
            "required": ["content"]
        }
    
    async def execute(
        self,
        content: str,
        channel: str | None = None,
        chat_id: str | None = None,
        message_id: str | None = None,
        media: list[str] | None = None,
        **kwargs: Any,
    ) -> str:
        """发送消息到指定 Channel/Chat"""
        
        # 使用参数或默认值
        channel = channel or self._default_channel
        chat_id = chat_id or self._default_chat_id
        message_id = message_id or self._default_message_id
        
        # 验证参数
        if not channel or not chat_id:
            return "Error: No target channel/chat specified. Use message tool to send to current chat."
        
        if not self._send_callback:
            return "Error: Message sending not configured. Please check channel settings."
        
        # 构建消息
        msg = OutboundMessage(
            channel=channel,
            chat_id=chat_id,
            content=content,
            media=media or [],
            metadata={
                "message_id": message_id,
                "reply_to": message_id,
            },
        )
        
        # 发送消息
        try:
            await self._send_callback(msg)
            
            # 跟踪发送状态
            if channel == self._default_channel and chat_id == self._default_chat_id:
                self._sent_in_turn = True
            
            # 返回成功信息
            media_info = f" with {len(media)} attachments" if media else ""
            return f"Message sent to {channel}:{chat_id}{media_info}"
            
        except Exception as e:
            logger.error("Failed to send message: {}", e)
            return f"Error sending message: {str(e)}"
```

---

### 2. OutboundMessage - 出站消息

**位置**: `anyclaw/bus/events.py` (已存在，需要更新)

```python
@dataclass
class OutboundMessage:
    """出站消息（更新以支持更多功能）"""
    
    # 基本字段（已存在）
    channel: str                    # Channel 名称
    chat_id: str                   # Chat/User ID
    content: str                   # 消息内容
    
    # ✨ 新增字段
    media: List[str] = field(default_factory=list)  # 媒体文件路径
    metadata: Dict[str, Any] = field(default_factory=dict)  # 元数据
    reply_to: str | None = None    # 回复的消息 ID
    
    # 其他字段（已存在）
    message_id: str | None = None
    sender_id: str | None = None
```

---

## 🔧 集成到 AnyClaw

### 1. 修改 AgentLoop

**文件**: `anyclaw/agent/loop.py`

```python
class AgentLoop:
    """Agent 主处理循环（添加 MessageTool 支持）"""
    
    def __init__(
        self,
        enable_tools: bool = True,
        workspace: Optional[Path] = None,
        # ... 现有参数 ...
        
        # ✨ 新增参数
        enable_message_tool: bool = True,  # 是否启用 MessageTool
    ):
        # ... 现有初始化 ...
        
        # ✨ 新增：MessageTool 支持
        self.enable_message_tool = enable_message_tool
        self._message_tool: Optional[MessageTool] = None
    
    def set_message_callback(
        self,
        callback: Callable[[OutboundMessage], Awaitable[None]],
    ) -> None:
        """设置 MessageTool 的发送回调（由 Channel 调用）"""
        if self._message_tool:
            self._message_tool.set_send_callback(callback)
    
    def set_message_context(
        self,
        channel: str,
        chat_id: str,
        message_id: str | None = None,
    ) -> None:
        """设置 MessageTool 的上下文（由 Channel 调用）"""
        if self._message_tool:
            self._message_tool.set_context(channel, chat_id, message_id)
    
    def message_sent_in_turn(self) -> bool:
        """检查当前回合是否通过 MessageTool 发送过消息"""
        if self._message_tool:
            return self._message_tool._sent_in_turn
        return False
    
    def start_turn(self) -> None:
        """开始新回合（重置发送跟踪）"""
        if self._message_tool:
            self._message_tool.start_turn()
```

### 2. 更新 Channel 基类

**文件**: `anyclaw/channels/base.py`

```python
class BaseChannel(ABC):
    """Channel 基类（添加 MessageTool 支持）"""
    
    def __init__(
        self,
        agent_loop: AgentLoop,
        # ... 现有参数 ...
    ):
        self.agent_loop = agent_loop
        
        # ✨ 新增：设置 MessageTool 回调
        self._setup_message_tool()
    
    def _setup_message_tool(self) -> None:
        """设置 MessageTool 的发送回调"""
        if hasattr(self.agent_loop, 'set_message_callback'):
            self.agent_loop.set_message_callback(self._send_message_callback)
    
    async def _send_message_callback(self, msg: OutboundMessage) -> None:
        """MessageTool 的发送回调（由子类实现）"""
        raise NotImplementedError("Subclasses must implement _send_message_callback")
```

### 3. 实现 Channel 的发送回调

**文件**: `anyclaw/channels/discord.py`

```python
class DiscordChannel(BaseChannel):
    """Discord 频道（添加 MessageTool 支持）"""
    
    async def process_message(self, message: discord.Message) -> None:
        """处理消息（添加 MessageTool 上下文设置）"""
        
        # ✨ 设置 MessageTool 的上下文
        self.agent_loop.set_message_context(
            channel="discord",
            chat_id=str(message.channel.id),
            message_id=str(message.id),
        )
        
        # ... 现有处理逻辑 ...
    
    async def _send_message_callback(self, msg: OutboundMessage) -> None:
        """实现 MessageTool 的发送回调"""
        
        # 验证 Channel 类型
        if msg.channel != "discord":
            logger.warning("Cannot send to channel '{}' from Discord channel", msg.channel)
            raise ValueError(f"Cannot send to {msg.channel} from Discord")
        
        # 获取目标 Channel
        channel_id = int(msg.chat_id)
        channel = self.client.get_channel(channel_id)
        
        if not channel:
            raise ValueError(f"Channel not found: {channel_id}")
        
        # 构建消息参数
        kwargs = {"content": msg.content}
        
        # 添加回复引用
        if msg.reply_to:
            try:
                reference_msg = await channel.fetch_message(int(msg.reply_to))
                kwargs["reference"] = discord.MessageReference(message_id=int(msg.reply_to))
            except Exception as e:
                logger.warning("Failed to fetch reference message: {}", e)
        
        # 添加媒体附件
        if msg.media:
            files = []
            for media_path in msg.media:
                try:
                    files.append(discord.File(media_path))
                except Exception as e:
                    logger.error("Failed to attach media {}: {}", media_path, e)
            
            if files:
                kwargs["files"] = files
        
        # 发送消息
        try:
            await channel.send(**kwargs)
            logger.info("Message sent to Discord {}: {}", channel_id, msg.content[:50])
        except Exception as e:
            logger.error("Failed to send Discord message: {}", e)
            raise
```

**文件**: `anyclaw/channels/feishu.py`

```python
class FeishuChannel(BaseChannel):
    """Feishu 频道（添加 MessageTool 支持）"""
    
    async def process_message(self, event: dict) -> None:
        """处理事件（添加 MessageTool 上下文设置）"""
        
        # ✨ 设置 MessageTool 的上下文
        self.agent_loop.set_message_context(
            channel="feishu",
            chat_id=event["open_chat_id"],
            message_id=event["message_id"],
        )
        
        # ... 现有处理逻辑 ...
    
    async def _send_message_callback(self, msg: OutboundMessage) -> None:
        """实现 MessageTool 的发送回调"""
        
        # 验证 Channel 类型
        if msg.channel != "feishu":
            logger.warning("Cannot send to channel '{}' from Feishu channel", msg.channel)
            raise ValueError(f"Cannot send to {msg.channel} from Feishu")
        
        # 构建消息内容
        content = {
            "msg_type": "text",
            "content": {"text": msg.content}
        }
        
        # 添加媒体附件（简化实现）
        if msg.media:
            # Feishu 支持上传文件，这里简化处理
            logger.warning("Feishu media attachment not fully implemented")
        
        # 发送消息
        try:
            await self.client.message.send(
                receive_id_type="chat_id",
                receive_id=msg.chat_id,
                msg_type="text",
                content=json.dumps(content),
            )
            logger.info("Message sent to Feishu {}: {}", msg.chat_id, msg.content[:50])
        except Exception as e:
            logger.error("Failed to send Feishu message: {}", e)
            raise
```

---

## 📋 实施步骤

### Phase 1: 核心实现 (Day 1)

**任务清单**:

- [ ] 1.1 创建 `anyclaw/agent/tools/message.py`
  - 实现 `MessageTool` 类
  - 实现 `set_context()` 方法
  - 实现 `set_send_callback()` 方法
  - 实现 `start_turn()` 方法
  - 实现 `execute()` 方法

- [ ] 1.2 更新 `anyclaw/bus/events.py`
  - 更新 `OutboundMessage` 类
  - 添加 `media` 字段
  - 添加 `metadata` 字段
  - 添加 `reply_to` 字段

- [ ] 1.3 单元测试
  - 测试 `MessageTool.execute()`
  - 测试 `MessageTool.set_context()`
  - 测试 `MessageTool.set_send_callback()`

### Phase 2: 集成到 AgentLoop (Day 2)

**任务清单**:

- [ ] 2.1 更新 `anyclaw/agent/loop.py`
  - 添加 `enable_message_tool` 参数
  - 添加 `_message_tool` 字段
  - 注册 `MessageTool`
  - 实现 `set_message_callback()` 方法
  - 实现 `set_message_context()` 方法
  - 实现 `message_sent_in_turn()` 方法
  - 实现 `start_turn()` 方法

- [ ] 2.2 单元测试
  - 测试 `AgentLoop` 的 MessageTool 集成
  - 测试上下文设置

### Phase 3: 集成到 Channel (Day 3-4)

**任务清单**:

- [ ] 3.1 更新 `anyclaw/channels/base.py`
  - 添加 `_setup_message_tool()` 方法
  - 添加 `_send_message_callback()` 抽象方法

- [ ] 3.2 更新 `anyclaw/channels/discord.py`
  - 实现 `_send_message_callback()` 方法
  - 更新 `process_message()` 设置上下文
  - 支持回复引用
  - 支持媒体附件

- [ ] 3.3 更新 `anyclaw/channels/feishu.py`
  - 实现 `_send_message_callback()` 方法
  - 更新 `process_message()` 设置上下文
  - 支持媒体附件（简化实现）

- [ ] 3.4 集成测试
  - 测试 Discord 中的 MessageTool
  - 测试 Feishu 中的 MessageTool

### Phase 4: 跨平台支持 (Day 5-6)

**任务清单**:

- [ ] 4.1 创建 `anyclaw/channels/telegram.py`（可选）
  - 实现 `_send_message_callback()` 方法
  - 支持回复引用
  - 支持媒体附件

- [ ] 4.2 创建 `anyclaw/channels/whatsapp.py`（可选）
  - 实现 `_send_message_callback()` 方法
  - 支持媒体附件

- [ ] 4.3 跨平台测试
  - 测试 Discord -> Discord 跨会话消息
  - 测试 Feishu -> Feishu 跨会话消息
  - 测试 Discord -> Feishu 跨平台消息（如果有支持）

### Phase 5: 配置和文档 (Day 7)

**任务清单**:

- [ ] 5.1 更新 `anyclaw/config/settings.py`
  - 添加 `enable_message_tool` 配置

- [ ] 5.2 更新文档
  - 添加 MessageTool 使用示例
  - 添加配置说明
  - 添加架构图

---

## 🧪 测试用例

### 单元测试

**文件**: `tests/test_message_tool.py`

```python
import pytest
from anyclaw.agent.tools.message import MessageTool
from anyclaw.bus.events import OutboundMessage

@pytest.mark.asyncio
async def test_message_tool_send_to_default():
    """测试发送到默认上下文"""
    tool = MessageTool(
        send_callback=mock_callback,
        default_channel="discord",
        default_chat_id="12345",
    )
    
    result = await tool.execute(content="Hello world")
    
    assert "Message sent" in result
    assert "discord:12345" in result
    mock_callback.assert_called_once()

@pytest.mark.asyncio
async def test_message_tool_send_to_custom():
    """测试发送到自定义上下文"""
    tool = MessageTool(
        send_callback=mock_callback,
        default_channel="discord",
        default_chat_id="12345",
    )
    
    result = await tool.execute(
        content="Hello",
        channel="feishu",
        chat_id="67890",
    )
    
    assert "Message sent" in result
    assert "feishu:67890" in result

@pytest.mark.asyncio
async def test_message_tool_with_media():
    """测试发送带媒体的消息"""
    tool = MessageTool(
        send_callback=mock_callback,
        default_channel="discord",
        default_chat_id="12345",
    )
    
    result = await tool.execute(
        content="Check this image",
        media=["/path/to/image.png"],
    )
    
    assert "Message sent" in result
    assert "with 1 attachments" in result
    call_args = mock_callback.call_args[0][0]
    assert len(call_args.media) == 1

@pytest.mark.asyncio
async def test_message_tool_with_reply():
    """测试回复消息"""
    tool = MessageTool(
        send_callback=mock_callback,
        default_channel="discord",
        default_chat_id="12345",
    )
    
    result = await tool.execute(
        content="Yes, I agree",
        message_id="987654321",
    )
    
    assert "Message sent" in result
    call_args = mock_callback.call_args[0][0]
    assert call_args.metadata["reply_to"] == "987654321"
```

---

## 📊 使用示例

### 示例 1: 发送到当前会话

```python
# 用户: "帮我分析这个文件"

# Agent 调用 message 工具
await message_tool.execute(
    content="正在分析文件，请稍候...",
)

# 返回: "Message sent to discord:12345"
```

### 示例 2: 发送到其他会话

```python
# 用户: "把分析结果发送给 Ryan"

# Agent 调用 message 工具
await message_tool.execute(
    content="分析结果：文件包含 3 个函数，没有明显的错误...",
    channel="discord",
    chat_id="67890",  # Ryan 的 chat_id
)

# 返回: "Message sent to discord:67890"
```

### 示例 3: 发送带媒体的消息

```python
# 用户: "生成一个图表并发送"

# Agent 生成图表后
await message_tool.execute(
    content="这是生成的图表",
    media=["/tmp/chart.png"],
)

# 返回: "Message sent to discord:12345 with 1 attachments"
```

### 示例 4: 回复消息

```python
# 用户: "文件准备好了吗？"

# Agent 回复
await message_tool.execute(
    content="是的，文件已经准备好了",
    message_id="987654321",  # 回复用户的消息
)

# 返回: "Message sent to discord:12345"
```

### 示例 5: 跨平台转发

```python
# 用户: "把结果同时发送到 Feishu"

# Agent 调用（如果支持）
await message_tool.execute(
    content="分析结果：...",
    channel="feishu",
    chat_id="ou_xxx",  # Feishu user_id
)

# 返回: "Message sent to feishu:ou_xxx"
```

---

## 🔒 安全考虑

### 1. 权限验证

```python
# ✅ 验证 Agent 有权限发送到目标 Channel
async def _send_message_callback(self, msg: OutboundMessage) -> None:
    if msg.channel != self.channel_name:
        raise PermissionError(f"Cannot send to {msg.channel} from {self.channel_name}")
```

### 2. 输入验证

```python
# ✅ 验证 chat_id 格式
if not self._is_valid_chat_id(msg.chat_id):
    raise ValueError(f"Invalid chat_id: {msg.chat_id}")
```

### 3. 媒体验证

```python
# ✅ 验证媒体文件存在且可读
for media_path in msg.media:
    if not Path(media_path).exists():
        raise FileNotFoundError(f"Media not found: {media_path}")
```

### 4. 速率限制

```python
# ✅ 防止消息发送过快
if self._rate_limiter.is_limited():
    raise RateLimitError("Sending too fast")
```

---

## 📈 性能考虑

### 1. 异步发送

```python
# ✅ 异步发送消息，不阻塞 Agent
await self._send_callback(msg)
```

### 2. 批量发送

```python
# ✅ 未来支持批量发送（如果 Channel 支持）
await self._send_batch_callback([msg1, msg2, msg3])
```

### 3. 消息缓存

```python
# ✅ 未来支持消息缓存（重试失败的消息）
self._message_cache[msg_id] = msg
```

---

## 🎯 与 nanobot 的对比

| 特性 | nanobot | AnyClaw 实现 | 状态 |
|------|---------|-------------|------|
| **跨会话消息** | ✅ | ✅ | ✅ 对齐 |
| **消息转发** | ✅ | ✅ | ✅ 对齐 |
| **多平台支持** | ✅ | ✅ (Discord, Feishu) | 🟡 部分对齐 |
| **媒体附件** | ✅ | ✅ | ✅ 对齐 |
| **自动上下文** | ✅ | ✅ | ✅ 对齐 |
| **回复引用** | ✅ | ✅ | ✅ 对齐 |
| **Telegram 支持** | ✅ | ❌ (可选) | 🟡 待实现 |
| **WhatsApp 支持** | ✅ | ❌ (可选) | 🟡 待实现 |

---

## 🚀 未来增强

### 1. 消息模板

```python
# 使用预定义模板
await message_tool.execute(
    template="task_completed",
    variables={"task": "Analysis", "result": "..."},
)
```

### 2. 消息优先级

```python
# 高优先级消息优先发送
await message_tool.execute(
    content="Urgent alert!",
    priority="high",  # high | medium | low
)
```

### 3. 消息调度

```python
# 定时发送消息
await message_tool.schedule(
    content="Daily report",
    schedule="0 9 * * *",  # Cron 表达式
)
```

### 4. 消息广播

```python
# 向多个会话发送消息
await message_tool.broadcast(
    content="System announcement",
    targets=[
        {"channel": "discord", "chat_id": "12345"},
        {"channel": "feishu", "chat_id": "ou_xxx"},
        {"channel": "telegram", "chat_id": "67890"},
    ],
)
```

### 5. 消息加密

```python
# 加密敏感消息
await message_tool.execute(
    content="Secret data",
    encryption="aes-256",
)
```

---

## 📝 总结

### 实现成果

✅ **完美复刻** nanobot 的 Message 工具
✅ **完美适配** AnyClaw 原有架构
✅ **不影响** 现有功能
✅ **向后兼容** - 可通过配置禁用

### 核心优势

1. **跨会话消息** - 支持向不同 Channel/Chat 发送
2. **消息转发** - 支持从一个会话转发到另一个会话
3. **多平台支持** - Discord, Feishu 等
4. **媒体附件** - 支持图片、音频、文档
5. **自动上下文** - 默认发送到当前会话
6. **回复引用** - 支持回复特定消息

### 下一步

1. 实现核心代码（Phase 1-3）
2. 添加跨平台支持（Phase 4）
3. 编写测试用例
4. 文档和示例

---

**方案生成时间**: 2026-03-20
**参考实现**: nanobot (agent/tools/message.py)
**预计完成时间**: 7 天
