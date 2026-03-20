# 实现任务

## 任务列表

- [x] 1. 扩展 SecurityConfig 模型
  - 添加 `allow_all_access` 字段
  - 添加 `extra_allowed_dirs` 字段
  - 添加 `allow_symlinks` 字段
  - 添加 `ssrf_allowed_networks` 和 `ssrf_allowed_domains` 字段
  - 添加 `exec_unrestricted` 字段

- [x] 2. 更新 Settings 配置
  - 同步添加新的安全配置字段
  - 更新 `_load_from_config_file()` 加载安全配置

- [x] 3. 更新配置模板
  - 完善 `[security]` 部分的说明
  - 添加使用示例

- [x] 4. 更新 PathGuard 创建逻辑
  - `create_path_guard_from_settings()` 支持 `allow_all_access`
  - 当 `allow_all_access=True` 时返回不限制的 PathGuard

- [x] 5. 更新 Shell 工具安全检查
  - `_guard_command()` 支持 `allow_all_access` 和 `exec_unrestricted`
  - 跳过安全检查当配置开放时

- [x] 6. 更新测试用例
  - 添加 `allow_all_access` 到 mock 配置
  - 添加新的测试用例

## 修改的文件

| 文件 | 修改内容 |
|------|---------|
| `config/loader.py` | 扩展 SecurityConfig 模型 |
| `config/settings.py` | 添加新安全配置字段和加载逻辑 |
| `config/config.template.toml` | 完善安全配置模板 |
| `security/path.py` | 支持 allow_all_access 快捷开关 |
| `tools/shell.py` | 支持 allow_all_access 和 exec_unrestricted |
| `tests/test_path_guard.py` | 添加新测试用例 |
