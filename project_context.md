# AnyClaw Project Context

> 项目上下文文档 - 最后更新: 2026-03-19

## 项目简介

**AnyClaw** 是一个轻量级、可扩展的 AI 智能体框架，采用 Python 3.11+ 开发。目标是提供一个灵活的 AI 助手构建平台，支持多种 LLM Provider、Tool Calling、技能系统、MCP 协议等功能。

## 技术栈

| 类别 | 技术 |
|------|------|
| 语言 | Python 3.11+ |
| 依赖管理 | Poetry |
| 数据验证 | Pydantic 2.x |
| 配置管理 | Pydantic-settings |
| CLI 框架 | Typer + Rich |
| LLM 接口 | LiteLLM |
| 测试 | pytest + pytest-asyncio |
| 代码质量 | Black + Ruff |

## 核心模块

### 1. Agent 系统 (`anyclaw/agent/`)
- **loop.py**: 主处理循环，处理用户输入、LLM 调用、Tool Calling
- **context.py**: 上下文构建器，整合 SOUL/USER/AGENTS/Skills
- **history.py**: 对话历史管理
- **compression.py**: 智能上下文压缩

### 2. 技能系统 (`anyclaw/skills/`)
- **loader.py**: 技能加载器，支持渐进式加载、热重载
- **executor.py**: 脚本执行器，支持 Python/Shell 脚本
- **toolkit.py**: 技能工具链 (create/validate/package)
- **models.py**: 数据模型定义
- **parser.py**: SKILL.md 解析器
- **builtin/**: 内置技能目录

### 3. 工具系统 (`anyclaw/tools/`)
- **base.py**: 工具基类
- **registry.py**: 工具注册表
- **shell.py**: Shell 执行工具
- **filesystem.py**: 文件系统工具

### 4. 频道系统 (`anyclaw/channels/`)
- **cli.py**: CLI 交互频道
- **feishu.py**: 飞书 Channel
- **discord.py**: Discord Channel
- **bus.py**: 消息路由 (MessageBus)

### 5. MCP 客户端 (`anyclaw/mcp/`)
- **client.py**: MCP Server 连接管理
- **wrapper.py**: MCP 工具包装器
- **config.py**: MCP 配置

### 6. 工作区管理 (`anyclaw/workspace/`)
- **manager.py**: 工作区管理器
- **templates.py**: 模板同步
- **bootstrap.py**: 引导系统
- **restrict.py**: 写入限制

### 7. 记忆系统 (`anyclaw/memory/`)
- **manager.py**: 记忆管理器
- **automation.py**: 记忆自动化

### 8. Provider (`anyclaw/providers/`)
- **zai.py**: ZAI/GLM CodePlan Provider

## 工作流程

### Agent 处理流程
```
用户输入 → Channel → AgentLoop.process()
    ↓
添加到历史记录
    ↓
构建上下文 (SOUL + USER + AGENTS + Skills)
    ↓
调用 LLM
    ↓
处理 Tool Calls (如有)
    ↓
返回响应
```

### Feature 开发流程
```
/new-feature → spec.md/task.md/checklist.md
    ↓
/start-feature → Git branch + worktree
    ↓
/implement-feature → 编写代码
    ↓
/verify-feature → 运行测试
    ↓
/complete-feature → 提交 + 合并 + 归档
```

## 配置系统

### 配置优先级
1. 环境变量
2. 配置文件 (`~/.anyclaw/config.json`)
3. 默认值

### 主要配置项
```json
{
  "llm": {
    "model": "glm-4.7",
    "provider": "zai",
    "streaming": true
  },
  "providers": {
    "zai": { "api_key": "..." },
    "openai": { "api_key": "..." }
  },
  "workspace": {
    "restrict_to_workspace": true
  }
}
```

## 测试策略

- 单元测试与源代码并列
- 异步测试使用 `@pytest.mark.asyncio`
- 目标覆盖率 >80%
- 主要测试文件:
  - `tests/test_skill_loader.py` - 技能加载测试 (24 tests)
  - `tests/test_skill_toolkit.py` - 工具链测试
  - `tests/test_agent.py` - Agent 测试
  - `tests/test_config.py` - 配置测试

## 安全考虑

### 已实现
- Workspace 写入限制 (`restrict_to_workspace`)
- 符号链接解析防绕过
- MCP 工具过滤

### 计划中
- ExecTool 危险命令限制
- SSRF 防护
- 路径遍历防护
- 凭证安全管理
- 输入验证与清理

## 依赖关系

```
agent/
  ├── skills/ (技能加载)
  ├── tools/ (工具调用)
  ├── channels/ (交互)
  └── mcp/ (MCP 工具)

skills/
  ├── loader.py (核心加载)
  ├── executor.py (脚本执行)
  └── toolkit.py (工具链)

channels/
  ├── cli.py
  ├── feishu.py
  └── discord.py
      └── bus.py (消息路由)
```

## 关键文件

| 文件 | 说明 |
|------|------|
| `anyclaw/agent/loop.py` | Agent 主循环 |
| `anyclaw/skills/loader.py` | 技能加载器 |
| `anyclaw/tools/registry.py` | 工具注册表 |
| `anyclaw/config/settings.py` | 配置管理 |
| `anyclaw/cli/app.py` | CLI 入口 |
| `feature-workflow/queue.yaml` | Feature 队列 |

## 开发规范

1. **异步优先**: Agent、LLM、技能执行都使用 async/await
2. **类型提示**: 所有函数必须有类型注解
3. **代码格式**: Black (line-length=100)
4. **代码检查**: Ruff (E, F, I, N, W)
5. **测试驱动**: 新功能必须有对应测试

## 下一步计划

1. **安全增强**: 完成 SSRF 防护、路径遍历防护
2. **凭证管理**: API Key 加密存储、日志脱敏
3. **Web UI**: 提供图形界面
4. **多 Agent 协作**: 支持多 Agent 通信
