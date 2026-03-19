# feat-serve-mode 任务分解

## 任务概览

| # | 任务 | 依赖 | 预计时间 | 状态 |
|---|------|------|----------|------|
| T1 | 实现 serve 命令基础结构 | - | 1h | pending |
| T2 | 多通道并行启动 | T1 | 2h | pending |
| T3 | 日志模式实现 | T1 | 1h | pending |
| T4 | 后台守护进程 | T1, T2 | 2h | pending |
| T5 | 服务管理命令 | T4 | 1h | pending |
| T6 | 测试和文档 | T1-T5 | 1h | pending |

---

## T1: 实现 serve 命令基础结构

**目标**: 创建 `anyclaw serve` CLI 命令骨架

**步骤**:
1. 在 `anyclaw/cli/serve_cmd.py` 创建新的命令模块
2. 在 `anyclaw/cli/app.py` 注册 serve 命令
3. 定义命令参数：
   - `--debug/-d`: Debug 模式
   - `--verbose/-v`: 详细输出
   - `--quiet/-q`: 静默模式
   - `--daemon/-D`: 后台运行
   - `--status`: 查看状态
   - `--stop`: 停止服务
   - `--logs`: 查看日志

**产出**:
- `anyclaw/cli/serve_cmd.py`
- 修改 `anyclaw/cli/app.py`

---

## T2: 多通道并行启动

**目标**: 使用 ChannelManager 同时启动所有启用的通道

**步骤**:
1. 创建 `anyclaw/core/serve.py` 服务管理器
2. 实现 `ServeManager` 类:
   - `__init__(config, bus)`: 初始化
   - `async start()`: 启动所有通道
   - `async stop()`: 停止所有通道
   - `get_status()`: 获取状态
3. 集成 `ChannelManager`
4. 实现消息路由

**产出**:
- `anyclaw/core/serve.py`

---

## T3: 日志模式实现

**目标**: 支持 debug/verbose/quiet 三种日志模式

**步骤**:
1. 创建 `anyclaw/utils/logging_config.py`:
   - `setup_logging(level, format)`: 配置日志
   - `DEBUG`: 详细时间戳 + 模块名
   - `INFO`: 标准格式
   - `WARNING`: 最小输出
2. 在 serve 命令中应用日志配置
3. 配置日志文件输出到 `~/.anyclaw/logs/`
4. 实现日志轮转

**产出**:
- `anyclaw/utils/logging_config.py`
- 日志目录: `~/.anyclaw/logs/`

---

## T4: 后台守护进程

**目标**: 支持 daemon 模式运行

**步骤**:
1. 实现 daemon 化逻辑:
   - fork 子进程
   - 创建新会话
   - 重定向标准输入/输出
   - 写入 PID 文件
2. 创建 PID 管理器 `anyclaw/core/daemon.py`:
   - `write_pid()`: 写入 PID
   - `read_pid()`: 读取 PID
   - `remove_pid()`: 删除 PID
   - `is_running()`: 检查是否运行
3. 实现信号处理:
   - SIGTERM: 优雅关闭
   - SIGINT: Ctrl+C 处理
   - SIGHUP: 重新加载配置

**产出**:
- `anyclaw/core/daemon.py`
- PID 文件: `~/.anyclaw/serve.pid`

---

## T5: 服务管理命令

**目标**: 实现 status/stop/logs 子命令

**步骤**:
1. `anyclaw serve --status`:
   - 读取 PID
   - 检查进程状态
   - 显示运行信息 (uptime, channels, messages)
2. `anyclaw serve --stop`:
   - 发送 SIGTERM
   - 等待优雅关闭
   - 确认进程终止
3. `anyclaw serve --logs`:
   - tail -f 日志文件
   - 支持 Ctrl+C 退出

**产出**:
- 修改 `anyclaw/cli/serve_cmd.py`

---

## T6: 测试和文档

**目标**: 完整测试覆盖和文档更新

**步骤**:
1. 单元测试:
   - `tests/test_serve_manager.py`
   - `tests/test_daemon.py`
   - `tests/test_logging_config.py`
2. 集成测试:
   - 测试多通道并行启动
   - 测试 daemon 模式
   - 测试信号处理
3. 更新文档:
   - `CLI_TEST_SCENARIOS.md` 添加 serve 测试场景
   - `config.template.toml` 添加相关配置注释

**产出**:
- `tests/test_serve_*.py`
- 更新测试场景文档

---

## 风险

| 风险 | 影响 | 缓解措施 |
|------|------|----------|
| Windows daemon 兼容性 | 中 | 使用 python-daemon 或条件实现 |
| 通道启动顺序 | 低 | 并行启动，不依赖顺序 |
| 日志文件过大 | 中 | 实现日志轮转 |
