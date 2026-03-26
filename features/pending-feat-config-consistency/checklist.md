# 完成检查清单

## 代码实现

- [x] Python: 添加 `CommandsPermissionsConfig` 类到 loader.py
- [x] Python: 添加 `CommandsConfig` 类到 loader.py
- [x] Python: 在 `Config` 类中添加 `commands` 字段
- [x] Tauri: 添加 `channelsFields` 到 configSchema.ts
- [x] Tauri: 在 `configGroups` 中添加 channels 分组
- [x] Tauri: 添加 `mcpServerFields` 到 configSchema.ts
- [x] Tauri: 在 `configGroups` 中添加 mcp_servers 分组
- [x] i18n: 添加 channels 相关翻译 (zh-CN, en-US)
- [x] i18n: 添加 mcp_servers 相关翻译 (zh-CN, en-US)

## 测试验证

- [x] 测试: Python 配置加载不报错（包含所有 section）
- [x] 测试: 配置加载 commands section 正常解析
- [x] 测试: TypeScript 类型检查通过
- [ ] 测试: sidecar 能正常启动（需手动验证）
- [ ] 测试: Tauri 表单能显示 channels 配置（需手动验证）
- [ ] 测试: Tauri 表单能保存 channels 配置（需手动验证）
- [ ] 测试: Tauri 表单能显示 mcp_servers 配置（需手动验证）
- [ ] 测试: Tauri 表单能保存 mcp_servers 配置（需手动验证）

## 文档更新

- [x] 更新 checklist.md 完成状态
