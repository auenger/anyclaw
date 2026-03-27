# feat-acp-mcp-bridge 完成检查清单

## 代码实现
- [ ] `anyclaw acp add/list/remove/test` CLI 命令
- [ ] 配置模板更新 (acp-mcp 示例)
- [ ] 配置加载器兼容性

## 功能验证
- [ ] `anyclaw acp add claude-code` 正确添加配置
- [ ] `anyclaw acp list` 显示已配置 Agent
- [ ] `anyclaw acp remove claude-code` 正确移除配置
- [ ] `anyclaw acp test claude-code` 能测试连接 (需要 Claude Code 已安装)
- [ ] AnyClaw MCP Client 能连接 acp-mcp 适配器
- [ ] AnyClaw Agent 能通过 MCP 调用外部 ACP Agent

## 文档
- [ ] ACP 集成指南文档
- [ ] 配置模板注释完整

## 测试
- [ ] CLI 命令单元测试
- [ ] 配置验证测试
- [ ] 所有测试通过

## 兼容性
- [ ] 不影响现有 MCP Client 功能
- [ ] 不影响现有 MCP Server 配置
- [ ] acp-mcp 不可用时优雅降级
