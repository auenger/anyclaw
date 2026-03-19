# 配置文件系统和记忆持久化功能

## 概述

为 AnyClaw 添加 JSON 配置文件支持，实现配置的持久化存储，并集成记忆系统到 Agent 的上下文构建中。

## 目标

1. 支持从 JSON 配置文件加载设置（API keys、模型配置等）
2. 添加 `save_memory` 和 `update_persona` 工具，让 LLM 可以主动更新记忆
3. ContextBuilder 集成 PersonaLoader 和 MemoryManager
4. ZAI Provider 默认使用 coding endpoint
5. 新增 `config` 命令行子命令

## 功能需求

### 1. 配置文件系统

- 配置文件位置：`~/.anyclaw/config.json`
- 支持的配置项：
  - Agent 配置（名称、工作区）
  - LLM 配置（模型、provider、temperature、max_tokens）
  - Provider 配置（API keys、base URLs）
- 配置优先级：环境变量 > 配置文件 > 默认值

### 2. 记忆持久化工具

- `save_memory` 工具：保存历史记录和更新长期记忆
- `update_persona` 工具：更新 SOUL.md 和 USER.md 文件
- LLM 可以通过工具调用主动更新用户偏好

### 3. ContextBuilder 增强

- 加载 SOUL.md（Agent 人设）
- 加载 USER.md（用户档案）
- 加载 MEMORY.md（长期记忆）
- 加载 TOOLS.md（工具说明）

### 4. ZAI Provider 优化

- 默认使用 `coding` endpoint（GLM Coding Plan）
- Base URL: `https://open.bigmodel.cn/api/coding/paas/v4`
- 支持 `zai/` 模型前缀自动转换为 `openai/` 前缀

### 5. 命令行工具

- `anyclaw config init`：初始化配置文件
- `anyclaw config show`：显示当前配置
- `anyclaw config set <key> <value>`：设置配置项
- `anyclaw config path`：显示配置文件路径
- `anyclaw config edit`：用编辑器打开配置文件

## 技术实现

### 文件结构

```
anyclaw/
├── config/
│   ├── settings.py      # Pydantic Settings（环境变量）
│   └── loader.py        # JSON 配置加载器
├── tools/
│   └── memory.py        # save_memory 和 update_persona 工具
├── agent/
│   └── context.py       # ContextBuilder（集成记忆和人设）
└── cli/
    └── config_cmd.py    # config 命令实现
```

### 配置文件格式

```json
{
  "agent": {
    "name": "AnyClaw",
    "workspace": "~/.anyclaw/workspace"
  },
  "llm": {
    "model": "glm-4.7",
    "provider": "zai",
    "max_tokens": 2000,
    "temperature": 0.7
  },
  "providers": {
    "openai": { "api_key": "" },
    "anthropic": { "api_key": "" },
    "zai": { "api_key": "", "api_base": "" }
  }
}
```

## 验收标准

- [x] 可以通过 `anyclaw config` 命令管理配置
- [x] 配置文件正确加载 API keys
- [x] `save_memory` 工具可以保存记忆
- [x] ContextBuilder 正确加载 workspace 文件
- [x] ZAI Provider 使用正确的 endpoint
- [x] 支持 `zai/` 模型前缀
