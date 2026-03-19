# feat-serve-mode

**状态**: pending
**优先级**: 80 (高)
**大小**: M
**创建时间**: 2026-03-19

---

## 描述

实现 `anyclaw serve` 命令，支持多通道并行运行、多种日志模式和后台守护进程。

---

## 用户价值点

### VP-1: 多通道并行服务

**用户故事**: 作为 AnyClaw 用户，我希望通过一个命令同时启动多个 IM 通道，这样我可以同时通过 CLI、Discord、飞书与 Agent 对话。

**验收场景**:

```gherkin
Feature: 多通道并行服务

  Scenario: 启动所有启用的通道
    Given 配置文件中启用了 CLI、Discord、飞书通道
    When 用户运行 "anyclaw serve"
    Then CLI 通道启动并等待输入
    And Discord Gateway 连接成功
    And 飞书 Webhook 服务启动
    And 显示所有通道的状态

  Scenario: 只启动配置启用的通道
    Given 配置文件中只启用了 Discord 通道
    When 用户运行 "anyclaw serve"
    Then 只启动 Discord 通道
    And 显示 "1 channel enabled"

  Scenario: 没有启用任何通道
    Given 配置文件中没有启用任何通道
    When 用户运行 "anyclaw serve"
    Then 显示警告 "No channels enabled"
    And 提示用户如何启用通道

  Scenario: 通道启动失败
    Given Discord token 无效
    When 用户运行 "anyclaw serve"
    Then 显示错误 "Discord authentication failed"
    And 其他通道继续运行
    And 退出码为 0 (非致命错误)
```

---

### VP-2: 运行模式控制

**用户故事**: 作为 AnyClaw 用户，我希望控制日志输出的详细程度，这样我可以在调试时看到详细信息，在生产环境中保持简洁。

**验收场景**:

```gherkin
Feature: 运行模式控制

  Scenario Outline: 不同的日志级别
    Given 用户运行 "anyclaw serve <mode>"
    When 服务启动
    Then 日志级别设置为 <level>
    And 输出格式为 <format>

    Examples:
      | mode          | level    | format        |
      | --debug       | DEBUG    | 详细时间戳+模块 |
      | -v --verbose  | INFO     | 标准格式       |
      | -q --quiet    | WARNING  | 最小输出       |
      | (默认)        | INFO     | 标准格式       |

  Scenario: Debug 模式显示详细连接信息
    Given 用户运行 "anyclaw serve --debug"
    When Discord Gateway 连接
    Then 显示 "Connecting to wss://gateway.discord.gg..."
    And 显示 "Received HELLO op=10"
    And 显示 "Sending IDENTIFY op=2"
    And 显示 "Received READY event"

  Scenario: Quiet 模式只显示错误
    Given 用户运行 "anyclaw serve --quiet"
    When 服务正常运行
    Then 不显示任何 INFO 级别日志
    When 发生错误
    Then 只显示错误信息
```

---

### VP-3: 后台守护进程

**用户故事**: 作为 AnyClaw 用户，我希望服务在后台运行，这样我可以关闭终端窗口而服务继续工作。

**验收场景**:

```gherkin
Feature: 后台守护进程

  Scenario: 以后台模式启动
    Given 用户运行 "anyclaw serve --daemon"
    When 命令执行完成
    Then 服务在后台运行
    And 终端立即返回
    And 显示 "Started AnyClaw daemon (PID: 12345)"
    And 显示 "Use 'anyclaw serve --status' to check status"

  Scenario: 检查服务状态
    Given 后台服务正在运行
    When 用户运行 "anyclaw serve --status"
    Then 显示服务状态:
      | PID        | 12345              |
      | Uptime     | 2h 30m             |
      | Channels   | CLI, Discord       |
      | Messages   | 156 processed      |
      | Memory     | 128 MB             |

  Scenario: 停止后台服务
    Given 后台服务正在运行 (PID: 12345)
    When 用户运行 "anyclaw serve --stop"
    Then 显示 "Stopping AnyClaw daemon (PID: 12345)..."
    And 显示 "✓ Stopped"
    And 进程 12345 已终止

  Scenario: 优雅关闭
    Given 后台服务正在处理消息
    When 用户运行 "anyclaw serve --stop"
    Then 等待当前消息处理完成
    And 关闭所有通道连接
    And 保存状态
    And 显示处理中的消息数量

  Scenario: 后台服务自动重启
    Given 配置 restart: true
    When 服务意外崩溃
    Then 自动重启服务
    And 记录崩溃日志

  Scenario: 查看服务日志
    Given 后台服务正在运行
    When 用户运行 "anyclaw serve --logs"
    Then 显示最近的日志 (tail -f ~/.anyclaw/logs/serve.log)
    And 支持按 Ctrl+C 退出

  Scenario: 后台服务 PID 文件
    Given 后台服务正在运行
    Then 文件 ~/.anyclaw/serve.pid 存在
    And 内容为进程 PID
    When 服务停止
    Then PID 文件被删除
```

---

## 技术约束

1. **Python 3.9+ 兼容**: 不使用 Python 3.11+ 专有特性
2. **异步架构**: 使用 asyncio 管理多个通道
3. **信号处理**: 支持 SIGTERM/SIGINT 优雅关闭
4. **跨平台**: 支持 macOS/Linux (Windows 部分支持)

---

## 依赖

- `websockets` - Discord Gateway
- `httpx` - HTTP 客户端
- `typer` - CLI 框架
- `rich` - 终端美化

---

## 非功能性需求

- 启动时间 < 5 秒
- 内存占用 < 200MB (空闲时)
- 支持 100+ 并发连接
- 日志文件轮转 (10MB * 5)
