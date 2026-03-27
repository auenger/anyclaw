# feat-acp-mcp-bridge 任务分解

## 任务列表

### T1: acp-mcp 配置支持
- [ ] 验证 acp-mcp 与 AnyClaw MCP Client 的兼容性
- [ ] 确定配置格式 (TOML)
- [ ] 准备常用 Agent 的预配置模板 (Claude Code, Gemini CLI)

### T2: 便捷 CLI 命令
- [ ] 实现 `anyclaw acp add <name>` — 添加 ACP Agent 配置
- [ ] 实现 `anyclaw acp list` — 列出已配置的 ACP Agent
- [ ] 实现 `anyclaw acp remove <name>` — 移除 ACP Agent 配置
- [ ] 实现 `anyclaw acp test <name>` — 测试 ACP Agent 连接
- [ ] 集成到 Typer CLI 应用

### T3: 配置模板更新
- [ ] config.template.toml 添加 acp-mcp 示例配置
- [ ] 配置加载器验证 acp-mcp 配置格式

### T4: 文档
- [ ] 编写 ACP 集成指南文档
- [ ] 包含 Claude Code / Gemini CLI 配置示例
- [ ] 说明 Agent 编排使用场景
- [ ] 说明与 ACP Server/Client 的区别和选择建议

### T5: 测试
- [ ] CLI 命令单元测试 (add/list/remove)
- [ ] 配置验证测试
