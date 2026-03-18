# Feature Spec: CLI 交互频道

## 元数据
- **ID**: feat-mvp-cli
- **名称**: CLI 交互频道
- **优先级**: 90
- **尺寸**: M
- **状态**: completed
- **创建日期**: 2026-03-18
- **完成日期**: 2026-03-18
- **依赖**: feat-mvp-init

## 描述
实现 AnyClaw 的命令行交互界面，提供用户与 Agent 交互的 CLI 频道。

## 用户价值点

### 价值点: CLI 交互能力
用户可以通过命令行与 Agent 进行对话交互。

**Gherkin 场景**:
```gherkin
Scenario: 启动 CLI 聊天
  Given 用户运行 `poetry run python -m anyclaw chat`
  Then 应该显示欢迎信息
  And 用户可以输入消息
  And Agent 应该响应

Scenario: 使用特殊命令
  Given CLI 聊天已启动
  When 用户输入 "exit"
  Then 应该退出程序
```

## 技术栈
- Typer (CLI 框架)
- Rich (终端美化)

## 实现文件
- `anyclaw/anyclaw/cli/app.py` - Typer CLI 应用
- `anyclaw/anyclaw/channels/cli.py` - CLIChannel 频道实现

## 验收标准
- [x] 支持 chat 命令启动交互式聊天
- [x] 支持 config 命令查看配置
- [x] 支持 version 命令查看版本
- [x] 支持 exit/quit/clear 特殊命令
- [x] 使用 Rich 美化输出

## 完成说明
CLI 频道已完成，包括：
- CLIChannel: 处理 CLI 输入输出，支持特殊命令
- Typer App: 三个命令 (chat, config, version)
- Rich 集成: 彩色输出和美化界面
