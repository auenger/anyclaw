# 完成检查清单: workspace 写入限制

## 实现检查

- [x] **配置项**
  - [x] `settings.py` 中添加 `restrict_to_workspace` 字段
  - [x] 默认值为 `True`
  - [x] 支持环境变量覆盖

- [x] **路径检查**
  - [x] `WriteFileTool` 添加 `restrict_to_workspace` 参数
  - [x] `_resolve_path()` 实现路径检查
  - [x] 使用 `resolve()` 处理符号链接
  - [x] 超出范围时返回清晰错误信息

- [x] **配置传递**
  - [x] `AgentLoop` 从 settings 读取配置
  - [x] 正确传递给 `WriteFileTool`

- [x] **文档更新**
  - [x] `TOOLS.md` 更新配置说明

## 测试检查

- [x] **单元测试**
  - [x] 测试默认配置值
  - [x] 测试启用限制 - workspace 内路径允许
  - [x] 测试启用限制 - workspace 外路径阻止
  - [x] 测试禁用限制 - 任意路径允许
  - [x] 测试符号链接处理
  - [x] 测试错误信息格式

- [x] **手动验证**
  - [x] 运行 `python3 -m pytest tests/test_filesystem_restrict.py -v` 全部通过 (12/12)
  - [ ] 手动测试 CLI 场景

## 验收标准

- [x] 默认情况下，`write_file` 只能在 workspace 内写入
- [x] 尝试写入 workspace 外时返回清晰的错误信息
- [x] 设置 `restrict_to_workspace=false` 后可以写入任意路径
- [x] 符号链接无法绕过限制
- [x] 所有测试通过
