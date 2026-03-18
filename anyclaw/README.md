# AnyClaw

AnyClaw 是一个轻量级、可扩展的 AI 智能体框架。

## 特性

- 🤖 支持 LLM 对话
- 🔌 可扩展的技能系统
- ⚙️ 灵活的配置管理
- 🖥️ 命令行界面

## 安装

\```bash
# 安装依赖
pip install pydantic pydantic-settings typer rich litellm openai

# 或使用 Poetry
poetry install
\```

## 配置

创建 `.env` 文件：

\```bash
OPENAI_API_KEY=sk-your-api-key-here
AGENT_NAME=AnyClaw
\```

## 使用

\```bash
# 启动 CLI
python -m anyclaw chat

# 或使用 Poetry
poetry run anyclaw chat
\```

## 版本

v0.1.0-MVP
