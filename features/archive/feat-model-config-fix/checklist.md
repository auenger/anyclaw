# feat-model-config-fix 完成检查清单

## 代码修改

- [x] `anyclaw/channels/cli.py` - 导入并使用全局 `settings`
- [x] `anyclaw/commands/handlers/model.py` - 兼容 Settings 结构

## 测试验证

- [x] 现有测试通过: `poetry run pytest tests/test_commands/ -v` (32 passed)
- [x] 无回归: `poetry run pytest tests/test_channels.py -v` (10 passed)

## 文档更新

- [x] 无需更新文档（bug 修复）

## 验收标准

- [x] `/model` 命令显示与配置文件一致的模型和 provider
- [x] `/model <name>` 可以正常切换模型
- [x] 无回归问题
