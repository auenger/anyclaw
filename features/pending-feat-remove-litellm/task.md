# 任务分解: 移除 litellm 依赖

## Phase 1: 基础设施 (feat-llm-abstraction)

### 1.1 创建 LLM 抽象层
- [ ] 创建 `anyclaw/llm/` 目录结构
- [ ] 定义 `ChatResponse`, `ChatMessage`, `ToolCall` 类型 (`types.py`)
- [ ] 实现 `BaseAdapter` 抽象基类 (`base.py`)
- [ ] 实现 `LLMClient` 统一客户端 (`client.py`)

### 1.2 重试机制
- [ ] 实现 `with_retry` 装饰器 (`retry.py`)
- [ ] 支持指数退避
- [ ] 支持自定义重试条件
- [ ] 空响应检测与恢复逻辑

### 1.3 单元测试
- [ ] 测试类型定义
- [ ] 测试重试装饰器
- [ ] 测试空响应恢复

## Phase 2: Provider Adapters (feat-llm-adapters)

### 2.1 OpenAI Adapter
- [ ] 实现 `OpenAIAdapter` (`adapters/openai.py`)
- [ ] 支持 chat completions
- [ ] 支持 tool calling
- [ ] 支持流式响应
- [ ] 单元测试

### 2.2 Anthropic Adapter
- [ ] 实现 `AnthropicAdapter` (`adapters/anthropic.py`)
- [ ] 支持 messages API
- [ ] 转换 tool_use 格式
- [ ] 单元测试

### 2.3 ZAI Adapter
- [ ] 实现 `ZAIAdapter` (`adapters/zai.py`)
- [ ] 复用 OpenAI SDK
- [ ] 自定义 endpoint 配置
- [ ] 单元测试

### 2.4 集成测试
- [ ] 测试所有 provider 的 chat 调用
- [ ] 测试 tool calling 流程
- [ ] 测试流式响应

## Phase 3: 迁移与清理 (feat-llm-migration)

### 3.1 AgentLoop 迁移
- [ ] 更新 `anyclaw/agent/loop.py`
  - [ ] 替换 `from litellm import acompletion`
  - [ ] 移除 `litellm.*` 全局配置
  - [ ] 使用 `LLMClient` 替代直接调用
  - [ ] 保留流式响应功能

### 3.2 ToolCallingLoop 迁移
- [ ] 更新 `anyclaw/agent/tool_loop.py`
  - [ ] 替换 `from litellm import acompletion`
  - [ ] 使用 `LLMClient`

### 3.3 Summary 迁移
- [ ] 更新 `anyclaw/agent/summary.py`
  - [ ] 替换 `from litellm import acompletion`
  - [ ] 使用 `LLMClient`

### 3.4 Serve 迁移
- [ ] 更新 `anyclaw/core/serve.py`
  - [ ] 替换 `from litellm import acompletion`
  - [ ] 使用 `LLMClient` 生成标题

### 3.5 依赖清理
- [ ] 从 `pyproject.toml` 移除 litellm
- [ ] 更新 `CLAUDE.md` 依赖列表
- [ ] 更新 `build_sidecar.py`（如有 litellm 相关）

### 3.6 最终验证
- [ ] 运行完整测试套件 `pytest tests/ -v`
- [ ] 手动测试 CLI chat 模式
- [ ] 手动测试 Tauri 桌面应用
- [ ] 测试所有 provider (OpenAI/Anthropic/ZAI)

## 依赖关系

```
Phase 1 (基础设施)
    ↓
Phase 2 (Adapters)
    ↓
Phase 3 (迁移)
```

## 预估工时

| Phase | 预估时间 |
|-------|----------|
| Phase 1 | 1 天 |
| Phase 2 | 1.5 天 |
| Phase 3 | 1 天 |
| 测试与验证 | 0.5 天 |
| **总计** | **4 天** |
