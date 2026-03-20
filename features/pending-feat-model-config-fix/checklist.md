# feat-model-config-fix 完成检查清单

## 代码修改

- [ ] `anyclaw/channels/cli.py` - 导入并使用全局 `settings`
- [ ] `anyclaw/commands/handlers/model.py` - 兼容 Settings 结构

## 测试验证

- [ ] 现有测试通过: `poetry run pytest tests/test_commands/ -v`
- [ ] 手动验证 `/model` 命令显示正确配置

## 文档更新

- [ ] 无需更新文档（bug 修复）

## 验收标准

- [ ] `/model` 命令显示与配置文件一致的模型和 provider
- [ ] `/model <name>` 可以正常切换模型
- [ ] 无回归问题
