# Feature: IM Channel 支持 (飞书 + Discord)

> **ID**: feat-im-channels
> **Status**: ✅ 已完成
> **Priority**: 65
> **Size**: L
> **Created**: 2026-03-19
> **Completed**: 2026-03-20
> **Commits**: b8c5e27 (Channel 集成)

## 概述

为 AnyClaw 添加 IM (即时通讯) 渠道支持，首先实现飞书和 Discord 两个平台。采用 nanobot 的 MessageBus 架构模式，实现统一的消息路由机制。

## 参考实现

- `reference/nanobot/nanobot/channels/base.py` - Channel 基类
- `reference/nanobot/nanobot/channels/feishu.py` - 飞书实现
- `reference/nanobot/nanobot/channels/discord.py` - Discord 实现
- `reference/nanobot/nanobot/channels/manager.py` - Channel 管理器
- `reference/nanobot/nanobot/bus/` - MessageBus 实现

---

## 用户价值点

### VP1: MessageBus 消息路由机制

**价值描述**: 统一的消息路由基础设施，支持多渠道接入、消息分发和生命周期管理。

**验收场景**:

```gherkin
Feature: MessageBus 消息路由

  Scenario: 入站消息路由到 Agent
    Given 一个已启动的 MessageBus
    And 一个已注册的 CLI Channel
    When 用户通过 CLI 发送消息 "hello"
    Then MessageBus 将消息路由到 Agent 处理
    And Agent 返回响应

  Scenario: 出站消息路由到指定 Channel
    Given Agent 生成了响应消息
    And 响应指定目标 channel 为 "feishu"
    When MessageBus 处理出站消息
    Then 消息被路由到飞书 Channel 发送

  Scenario: 多 Channel 并行运行
    Given 配置启用了 CLI 和 Feishu 两个 Channel
    When ChannelManager 启动所有 Channel
    Then 两个 Channel 同时运行
    And 各自独立处理消息
```

### VP2: 飞书渠道 (最小化)

**价值描述**: 支持 AnyClaw 通过飞书机器人接收和回复文本消息。

**验收场景**:

```gherkin
Feature: 飞书 Channel (最小化)

  Background:
    Given 飞书 Bot 已配置 app_id 和 app_secret
    And allow_from 包含测试用户

  Scenario: 接收私聊文本消息
    Given 飞书 Channel 已启动
    When 用户发送私聊消息 "你好"
    Then AnyClaw 收到消息内容 "你好"
    And sender_id 被正确识别

  Scenario: 回复文本消息
    Given AnyClaw 生成了响应 "你好，有什么可以帮你的？"
    When 飞书 Channel 发送响应
    Then 用户在飞书中收到文本消息

  Scenario: 权限控制
    Given allow_from 仅包含 ["user_123"]
    When 未授权用户 "user_456" 发送消息
    Then 消息被拒绝处理
    And 记录警告日志

  Scenario: 长消息自动分割
    Given AnyClaw 生成了 5000 字符的响应
    When 飞书 Channel 发送响应
    Then 响应被自动分割为多条消息
    And 每条消息不超过飞书限制
```

### VP3: Discord 渠道 (基础消息)

**价值描述**: 支持 AnyClaw 通过 Discord Bot 接收和回复消息，支持@提及、回复引用和文件附件。

**验收场景**:

```gherkin
Feature: Discord Channel (基础消息)

  Background:
    Given Discord Bot 已配置 token
    And allow_from 包含测试用户

  Scenario: 接收私聊消息
    Given Discord Channel 已启动并连接 Gateway
    When 用户发送 DM "hello"
    Then AnyClaw 收到消息内容 "hello"
    And chat_id 被正确识别

  Scenario: 群聊 @提及响应
    Given group_policy 设置为 "mention"
    And Bot 在群聊中被 @提及
    When 用户发送 "@Bot 你好"
    Then AnyClaw 处理该消息
    And 返回响应到群聊

  Scenario: 群聊非提及忽略
    Given group_policy 设置为 "mention"
    When 用户在群聊发送消息但不 @Bot
    Then 消息被忽略

  Scenario: 回复引用消息
    Given 用户消息引用了 Bot 之前的消息
    When AnyClaw 发送响应
    Then 响应消息包含 reply_to 引用

  Scenario: 发送文件附件
    Given AnyClaw 生成了文件路径 "/tmp/result.png"
    When Discord Channel 发送消息
    Then 文件作为附件上传
    And 用户看到文件预览

  Scenario: 接收文件附件
    Given 用户发送了带附件的消息
    When Discord Channel 处理消息
    Then 附件被下载到 media 目录
    And 消息内容包含 "[attachment: /path/to/file]"

  Scenario: Rate Limit 处理
    Given Discord API 返回 429 Rate Limit
    When Channel 发送消息
    Then 等待 retry_after 秒后重试
    And 消息最终成功发送
```

---

## 技术设计

### 架构图

```
┌─────────────────────────────────────────────────────────────┐
│                        AnyClaw                              │
├─────────────────────────────────────────────────────────────┤
│                                                             │
│  ┌─────────────┐    ┌─────────────┐    ┌─────────────┐     │
│  │ CLI Channel │    │Feishu Ch.   │    │Discord Ch.  │     │
│  └──────┬──────┘    └──────┬──────┘    └──────┬──────┘     │
│         │                  │                   │            │
│         └──────────────────┼───────────────────┘            │
│                            │                                │
│                   ┌────────▼────────┐                       │
│                   │   MessageBus    │                       │
│                   │  (Inbound/Out)  │                       │
│                   └────────┬────────┘                       │
│                            │                                │
│                   ┌────────▼────────┐                       │
│                   │ ChannelManager  │                       │
│                   └────────┬────────┘                       │
│                            │                                │
│                   ┌────────▼────────┐                       │
│                   │   AgentLoop     │                       │
│                   └─────────────────┘                       │
│                                                             │
└─────────────────────────────────────────────────────────────┘
```

### 目录结构

```
anyclaw/
├── bus/                    # 新增: 消息总线
│   ├── __init__.py
│   ├── events.py           # InboundMessage, OutboundMessage
│   └── queue.py            # MessageBus 实现
├── channels/
│   ├── __init__.py         # 更新: 导出所有 Channel
│   ├── base.py             # 新增: BaseChannel 抽象类
│   ├── manager.py          # 新增: ChannelManager
│   ├── registry.py         # 新增: Channel 自动发现
│   ├── cli.py              # 更新: 适配 BaseChannel
│   ├── feishu.py           # 新增: 飞书 Channel
│   └── discord.py          # 新增: Discord Channel
└── config/
    └── settings.py         # 更新: Channel 配置
```

### 依赖

```toml
# 新增依赖
websockets = ">=12.0"        # Discord Gateway
httpx = ">=0.25.0"           # HTTP 客户端
lark-oapi = ">=1.0.0"        # 飞书 SDK (可选)
```

---

## 配置示例

```json
{
  "channels": {
    "cli": {
      "enabled": true
    },
    "feishu": {
      "enabled": true,
      "app_id": "cli_xxx",
      "app_secret": "xxx",
      "allow_from": ["ou_xxx"],
      "encrypt_key": ""
    },
    "discord": {
      "enabled": true,
      "token": "Bot xxx",
      "allow_from": ["123456789"],
      "group_policy": "mention"
    }
  }
}
```

---

## 风险与缓解

| 风险 | 影响 | 缓解措施 |
|------|------|----------|
| 飞书 SDK 依赖较大 | 安装体积增加 | 作为可选依赖，运行时检测 |
| Discord Rate Limit | 消息延迟 | 实现重试机制，记录日志 |
| 多 Channel 并发 | 资源占用 | 异步 IO，连接池管理 |

---

## 依赖特性

无

## 后续扩展

- 飞书富文本卡片、文件附件
- Discord Slash Commands、Embed
- 其他 IM 平台 (Telegram, Slack, 钉钉等)
