# 特性：飞书 Channel 出站消息支持

## 概述

飞书 channel 缺少 `_outbound_loop` 实现，导致 Agent 处理完飞书消息后无法将响应发送回飞书。

## 背景

### 问题发现

在修复 Discord 消息路由问题时发现，各 channel 的出站消息处理方式不一致：

| Channel | 入站处理 | 出站处理 |
|---------|---------|---------|
| Discord | ✅ 正常 | ✅ `_outbound_loop` 监听 bus |
| API (App) | ✅ 正常 | ✅ SSE 订阅 bus |
| 飞书 | ✅ 正常 | ❌ **缺少 `_outbound_loop`** |

### 消息流程

```
飞书用户消息 → InboundMessage(channel="feishu")
    ↓
ServeManager 处理 → Agent 处理
    ↓
OutboundMessage(channel="feishu", chat_id="xxx")
    ↓
❌ 没有消费者！消息丢失
```

## 用户价值点

### 价值点 1：飞书响应发送

**描述**：飞书用户发送消息后能收到 Agent 的响应

**验收场景**：

```gherkin
Feature: 飞书消息响应

  Scenario: 用户发送文本消息收到回复
    Given 飞书 channel 已配置并启动
    And 用户 open_id 为 "ou_xxx"
    And 聊天 chat_id 为 "oc_xxx"
    When 用户发送消息 "你好"
    Then Agent 处理消息
    And 响应通过飞书 API 发送到 chat_id "oc_xxx"
    And 用户收到 Agent 的回复

  Scenario: 长消息自动分割
    Given 飞书 channel 已配置并启动
    When Agent 响应内容超过 30000 字符
    Then 响应被分割为多个消息
    And 所有消息按顺序发送到飞书

  Scenario: 飞书发送失败记录日志
    Given 飞书 channel 已配置并启动
    When 飞书 API 返回错误
    Then 错误被记录到日志
    And 不会导致 channel 崩溃
```

## 技术方案

### 实现方式

参考 Discord channel 的实现，为飞书添加：

1. `_outbound_task` - 出站消息处理任务
2. `_outbound_loop()` - 异步循环，监听 bus 并发送消息

```python
async def start(self) -> None:
    # ... 现有初始化代码 ...
    self._outbound_task = asyncio.create_task(self._outbound_loop())

async def _outbound_loop(self) -> None:
    """监听出站消息并发送到飞书"""
    while self._running:
        try:
            msg = await asyncio.wait_for(
                self.bus.consume_outbound(),
                timeout=1.0
            )
            if msg.channel == self.name:  # "feishu"
                await self.send(msg)
        except asyncio.TimeoutError:
            continue
        except asyncio.CancelledError:
            break
        except Exception as e:
            logger.error(f"Error in outbound loop: {e}")

async def stop(self) -> None:
    self._running = False
    if self._outbound_task:
        self._outbound_task.cancel()
        self._outbound_task = None
    # ... 现有清理代码 ...
```

### 注意事项

1. 使用 `consume_outbound()` 从主队列消费（与 Discord 一致）
2. SSE 使用广播模式订阅，不会影响 channel 消费
3. 需要正确处理 `stop()` 时的任务取消

## 优先级

低（当前没有飞书用户）

## 依赖

无

## 相关 Issue

- Discord 消息路由修复（2026-03-23）
- MessageBus 广播模式支持
