# Task: IM Channel 支持

> **Feature ID**: feat-im-channels
> **Estimated Effort**: L (3-5 天)

## 任务分解

### Phase 1: MessageBus 基础设施 (Day 1)

#### 1.1 消息事件模型
- [ ] 创建 `anyclaw/bus/__init__.py`
- [ ] 创建 `anyclaw/bus/events.py`
  - `InboundMessage` 数据类 (channel, sender_id, chat_id, content, media, metadata)
  - `OutboundMessage` 数据类 (channel, chat_id, content, media, reply_to, metadata)
- [ ] 创建 `anyclaw/bus/queue.py`
  - `MessageBus` 类
  - `publish_inbound()` 方法
  - `publish_outbound()` 方法
  - `consume_inbound()` 异步迭代器
  - `consume_outbound()` 异步迭代器

#### 1.2 Channel 基类
- [ ] 创建 `anyclaw/channels/base.py`
  - `BaseChannel` 抽象基类
  - `name`, `display_name` 类属性
  - `start()`, `stop()`, `send()` 抽象方法
  - `_handle_message()` 内部方法
  - `is_allowed()` 权限检查
  - `default_config()` 类方法

#### 1.3 Channel 注册与发现
- [ ] 创建 `anyclaw/channels/registry.py`
  - `discover_channel_names()` - 扫描内置模块
  - `load_channel_class()` - 动态加载类
  - `discover_plugins()` - entry_points 插件
  - `discover_all()` - 合并所有发现

#### 1.4 Channel Manager
- [ ] 创建 `anyclaw/channels/manager.py`
  - `ChannelManager` 类
  - `_init_channels()` - 初始化启用的 Channel
  - `start_all()` - 启动所有 Channel
  - `stop_all()` - 停止所有 Channel
  - `_dispatch_outbound()` - 出站消息分发

### Phase 2: CLI Channel 重构 (Day 1-2)

#### 2.1 适配 BaseChannel
- [ ] 更新 `anyclaw/channels/cli.py`
  - 继承 `BaseChannel`
  - 实现 `start()`, `stop()`, `send()`
  - 保留流式输出支持

#### 2.2 更新 CLI 入口
- [ ] 更新 `anyclaw/cli/app.py`
  - 使用 `ChannelManager` 启动 Channel
  - 集成 MessageBus

### Phase 3: 飞书 Channel (Day 2-3)

#### 3.1 配置模型
- [ ] 创建 `FeishuConfig` 配置类
  - `enabled`, `app_id`, `app_secret`
  - `allow_from`, `encrypt_key`

#### 3.2 飞书 Channel 实现
- [ ] 创建 `anyclaw/channels/feishu.py`
  - `FeishuChannel` 类
  - 使用 `lark-oapi` SDK (可选依赖)
  - WebSocket 长连接接收消息
  - REST API 发送消息
  - 消息分割 (超长文本)

#### 3.3 测试
- [ ] 单元测试: 配置解析
- [ ] 单元测试: 权限检查
- [ ] 集成测试: 消息收发 (Mock)

### Phase 4: Discord Channel (Day 3-4)

#### 4.1 配置模型
- [ ] 创建 `DiscordConfig` 配置类
  - `enabled`, `token`, `allow_from`
  - `gateway_url`, `intents`
  - `group_policy` (mention/open)

#### 4.2 Discord Channel 实现
- [ ] 创建 `anyclaw/channels/discord.py`
  - `DiscordChannel` 类
  - Gateway WebSocket 连接
  - Heartbeat 心跳机制
  - MESSAGE_CREATE 事件处理
  - REST API 发送消息
  - @提及检测
  - 回复引用支持
  - 文件附件收发
  - Rate Limit 处理

#### 4.3 测试
- [ ] 单元测试: 配置解析
- [ ] 单元测试: @提及检测
- [ ] 单元测试: 消息分割
- [ ] 集成测试: 消息收发 (Mock)

### Phase 5: 集成与文档 (Day 5)

#### 5.1 配置系统更新
- [ ] 更新 `anyclaw/config/settings.py`
  - 添加 `ChannelsConfig` 配置节
  - 支持从 JSON/环境变量加载

#### 5.2 依赖更新
- [ ] 更新 `pyproject.toml`
  - 添加 `websockets`, `httpx` 依赖
  - `lark-oapi` 作为可选依赖

#### 5.3 文档
- [ ] 更新 CLAUDE.md (架构说明)
- [ ] 创建 `docs/channels.md` (Channel 开发指南)
- [ ] 更新 `.env.example` (配置示例)

#### 5.4 端到端测试
- [ ] 测试 CLI + Feishu 并行运行
- [ ] 测试 CLI + Discord 并行运行
- [ ] 测试多 Channel 消息路由

---

## 实现顺序建议

```
Phase 1 (基础设施)
    ↓
Phase 2 (CLI 重构) ←→ Phase 3 (飞书)
    ↓                      ↓
    └──────────┬───────────┘
               ↓
         Phase 4 (Discord)
               ↓
         Phase 5 (集成)
```

Phase 2 和 Phase 3 可以并行开发，Phase 4 依赖 Phase 1 完成。

---

## 关键文件清单

| 文件 | 操作 | 说明 |
|------|------|------|
| `anyclaw/bus/__init__.py` | 新增 | Bus 模块入口 |
| `anyclaw/bus/events.py` | 新增 | 消息事件模型 |
| `anyclaw/bus/queue.py` | 新增 | MessageBus 实现 |
| `anyclaw/channels/base.py` | 新增 | Channel 基类 |
| `anyclaw/channels/manager.py` | 新增 | Channel 管理器 |
| `anyclaw/channels/registry.py` | 新增 | Channel 注册 |
| `anyclaw/channels/cli.py` | 修改 | 适配 BaseChannel |
| `anyclaw/channels/feishu.py` | 新增 | 飞书 Channel |
| `anyclaw/channels/discord.py` | 新增 | Discord Channel |
| `anyclaw/channels/__init__.py` | 修改 | 导出更新 |
| `anyclaw/config/settings.py` | 修改 | Channel 配置 |
| `anyclaw/cli/app.py` | 修改 | 使用 ChannelManager |
| `pyproject.toml` | 修改 | 添加依赖 |
