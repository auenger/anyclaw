# Checklist: IM Channel 支持

> **Feature ID**: feat-im-channels
> **Created**: 2026-03-19

## 完成标准

### Phase 1: MessageBus 基础设施

- [ ] `anyclaw/bus/events.py` 完成
  - [ ] `InboundMessage` 数据类定义正确
  - [ ] `OutboundMessage` 数据类定义正确
  - [ ] 包含必要字段: channel, sender_id, chat_id, content, media, metadata

- [ ] `anyclaw/bus/queue.py` 完成
  - [ ] `MessageBus` 类实现
  - [ ] `publish_inbound()` 异步发布入站消息
  - [ ] `publish_outbound()` 异步发布出站消息
  - [ ] `consume_inbound()` 异步迭代消费入站
  - [ ] `consume_outbound()` 异步迭代消费出站

- [ ] `anyclaw/channels/base.py` 完成
  - [ ] `BaseChannel` 抽象基类
  - [ ] `start()`, `stop()`, `send()` 抽象方法
  - [ ] `is_allowed()` 权限检查
  - [ ] `_handle_message()` 内部方法

- [ ] `anyclaw/channels/registry.py` 完成
  - [ ] 自动发现内置 Channel
  - [ ] 支持 entry_points 插件

- [ ] `anyclaw/channels/manager.py` 完成
  - [ ] 初始化启用的 Channel
  - [ ] 并行启动所有 Channel
  - [ ] 出站消息路由分发

### Phase 2: CLI Channel 重构

- [ ] `anyclaw/channels/cli.py` 重构
  - [ ] 继承 `BaseChannel`
  - [ ] 实现 `start()`, `stop()`, `send()`
  - [ ] 保留流式输出功能

- [ ] `anyclaw/cli/app.py` 更新
  - [ ] 使用 `ChannelManager`
  - [ ] 集成 `MessageBus`

### Phase 3: 飞书 Channel

- [ ] `anyclaw/channels/feishu.py` 完成
  - [ ] `FeishuConfig` 配置类
  - [ ] `FeishuChannel` 继承 `BaseChannel`
  - [ ] WebSocket 连接接收消息
  - [ ] REST API 发送消息
  - [ ] 权限检查 `is_allowed()`
  - [ ] 长消息分割

- [ ] 测试覆盖
  - [ ] 单元测试: 配置解析
  - [ ] 单元测试: 权限检查
  - [ ] 集成测试: 消息收发

### Phase 4: Discord Channel

- [ ] `anyclaw/channels/discord.py` 完成
  - [ ] `DiscordConfig` 配置类
  - [ ] `DiscordChannel` 继承 `BaseChannel`
  - [ ] Gateway WebSocket 连接
  - [ ] Heartbeat 心跳机制
  - [ ] MESSAGE_CREATE 事件处理
  - [ ] REST API 发送消息
  - [ ] @提及检测 (`group_policy`)
  - [ ] 回复引用 (`reply_to`)
  - [ ] 文件附件收发
  - [ ] Rate Limit 处理

- [ ] 测试覆盖
  - [ ] 单元测试: 配置解析
  - [ ] 单元测试: @提及检测
  - [ ] 单元测试: 消息分割
  - [ ] 集成测试: 消息收发

### Phase 5: 集成与文档

- [ ] 配置系统
  - [ ] `ChannelsConfig` 配置节
  - [ ] 从 JSON 加载 Channel 配置
  - [ ] 从环境变量加载敏感信息

- [ ] 依赖更新
  - [ ] `websockets` 依赖
  - [ ] `httpx` 依赖
  - [ ] `lark-oapi` 可选依赖

- [ ] 文档更新
  - [ ] CLAUDE.md 架构说明
  - [ ] `.env.example` 配置示例

- [ ] 端到端测试
  - [ ] CLI + Feishu 并行运行
  - [ ] CLI + Discord 并行运行
  - [ ] 多 Channel 消息路由

---

## 验收测试

### 功能验收

```bash
# 1. MessageBus 基础功能
poetry run pytest tests/test_bus.py -v

# 2. Channel 基础功能
poetry run pytest tests/test_channels/ -v

# 3. 飞书 Channel
poetry run pytest tests/test_feishu_channel.py -v

# 4. Discord Channel
poetry run pytest tests/test_discord_channel.py -v

# 5. 集成测试
poetry run pytest tests/test_integration.py -v
```

### 手动验收

- [ ] CLI 正常工作 (不影响现有功能)
- [ ] 飞书 Bot 能接收私聊消息
- [ ] 飞书 Bot 能回复消息
- [ ] Discord Bot 能接收 DM
- [ ] Discord Bot 能在群聊中响应 @提及
- [ ] Discord Bot 能发送文件附件

---

## 完成确认

- [ ] 所有单元测试通过
- [ ] 所有集成测试通过
- [ ] 代码覆盖率 >= 80%
- [ ] 文档已更新
- [ ] 无 Ruff 检查错误
- [ ] 无类型检查错误 (mypy)
