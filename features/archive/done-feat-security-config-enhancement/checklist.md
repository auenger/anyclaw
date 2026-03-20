# 验收检查清单

## 功能验证

- [x] `allow_all_access = true` 时可以访问任意路径
- [x] `allow_all_access = false` 时路径限制生效
- [x] `extra_allowed_dirs` 可以配置额外允许的目录
- [x] 配置文件可以正确加载新的安全配置项
- [x] Shell 工具支持 `exec_unrestricted` 配置

## 测试验证

- [x] 单元测试通过 (`test_path_guard.py`)
- [x] 配置加载测试通过 (`test_config.py`)
- [x] 新增 `test_create_from_settings_allow_all_access` 测试用例

## 文档验证

- [x] 配置模板包含详细说明
- [x] 配置项有中文注释
- [x] 包含使用示例

## 兼容性验证

- [x] 向后兼容（默认值保持不变）
- [x] 旧配置文件可以正常工作

## 使用示例

### 开放所有权限
```toml
[security]
allow_all_access = true
```

### 开放特定目录
```toml
[security]
restrict_to_workspace = true
extra_allowed_dirs = ["/Users/ryan/mycode/HRExcel"]
```

### 关闭路径限制
```toml
[security]
restrict_to_workspace = false
ssrf_enabled = true  # 保持 SSRF 防护
```
