# 完成检查清单: 移除 litellm 依赖

## 功能完成

- [ ] LLM 抽象层创建完成
- [ ] OpenAI adapter 实现完成
- [ ] Anthropic adapter 实现完成
- [ ] ZAI adapter 实现完成
- [ ] 重试机制实现完成
- [ ] 流式响应支持完成

## 迁移完成

- [ ] `anyclaw/agent/loop.py` 已迁移
- [ ] `anyclaw/agent/tool_loop.py` 已迁移
- [ ] `anyclaw/agent/summary.py` 已迁移
- [ ] `anyclaw/core/serve.py` 已迁移
- [ ] 无残留 `from litellm` 导入
- [ ] 无残留 `litellm.` 全局配置

## 依赖清理

- [ ] `pyproject.toml` 已移除 litellm
- [ ] `poetry.lock` 已更新
- [ ] `CLAUDE.md` 依赖列表已更新
- [ ] `build_sidecar.py` 已更新（如有）

## 测试通过

- [ ] 单元测试: `pytest tests/test_llm/ -v`
- [ ] Agent 测试: `pytest tests/test_agent.py -v`
- [ ] 完整测试: `pytest tests/ -v`
- [ ] 覆盖率 >= 80%

## 手动验证

- [ ] CLI chat 模式正常
- [ ] OpenAI provider 正常
- [ ] Anthropic provider 正常（如有 key）
- [ ] ZAI provider 正常
- [ ] Tauri 桌面应用正常
- [ ] 流式响应正常
- [ ] Tool calling 正常

## 文档更新

- [ ] CLAUDE.md 技术栈说明已更新
- [ ] 新模块有适当的 docstring
- [ ] 代码注释清晰
