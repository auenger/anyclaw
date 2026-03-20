# Security Config Enhancement

## 概述

增强 AnyClaw 的安全配置系统，提供更细粒度的权限控制和便捷的"开放所有权限"快捷开关。

## 背景

用户在使用 AnyClaw 时，当尝试访问 workspace 之外的文件路径时，会遇到路径限制错误：
- `Path traversal detected - path must be within base directory`
- `命令被安全策略阻止 - 路径超出工作目录`

原有的安全配置不够完善，缺少：
1. 快捷的"开放所有权限"选项
2. 额外允许目录的配置
3. SSRF 防护的详细配置
4. 命令执行的灵活控制

## 需求

### 功能需求

1. **快捷开关**: 添加 `allow_all_access` 配置项，一键禁用所有限制
2. **路径控制**: 支持 `extra_allowed_dirs` 配置额外允许的目录
3. **SSRF 配置**: 支持 `ssrf_allowed_networks` 和 `ssrf_allowed_domains`
4. **命令执行**: 支持 `exec_unrestricted` 独立控制命令执行限制

### 非功能需求

- 配置文件使用 TOML 格式
- 保持向后兼容
- 提供详细的配置说明

## 技术方案

### 配置结构

```toml
[security]
# 快捷开关
allow_all_access = false

# 路径控制
restrict_to_workspace = true
extra_allowed_dirs = []
allow_symlinks = true

# SSRF 防护
ssrf_enabled = true
ssrf_allowed_networks = []
ssrf_allowed_domains = []

# 命令执行
exec_deny_patterns = []
exec_allow_patterns = []
exec_unrestricted = false
```

### 实现要点

1. 扩展 `SecurityConfig` 模型
2. 更新 `create_path_guard_from_settings()` 支持 `allow_all_access`
3. 更新 shell 工具的 `_guard_command()` 方法
4. 更新配置加载逻辑 `_load_from_config_file()`

## 影响范围

- `anyclaw/config/loader.py` - SecurityConfig 模型
- `anyclaw/config/settings.py` - Settings 配置
- `anyclaw/config/config.template.toml` - 配置模板
- `anyclaw/security/path.py` - PathGuard 创建
- `anyclaw/tools/shell.py` - 命令安全检查
- `tests/test_path_guard.py` - 测试用例
