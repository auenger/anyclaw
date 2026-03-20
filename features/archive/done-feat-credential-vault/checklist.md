# 完成检查清单

## 代码实现

- [x] `anyclaw/security/credentials.py` 已创建
- [x] `CredentialManager` 类已实现
- [x] 加密存储已实现（基于机器标识 + cryptography Fernet）
- [x] 系统密钥链支持（可选 - 已预留接口）
- [x] 脱敏模式已定义（支持 OpenAI/GitHub/AWS/Anthropic 等）
- [x] 日志过滤器已实现（SensitiveDataFilter）
- [x] 配置显示脱敏已实现（config show --reveal）

## 测试

- [x] `tests/test_credentials.py` 已创建
- [x] 测试加密存储和读取
- [x] 测试各种密钥格式脱敏
- [x] 测试配置显示脱敏
- [x] 测试格式验证
- [x] 测试覆盖率 > 80%（33 tests passed）

## 安全验证

- [x] 配置文件中无明文 API Key（凭证单独存储在 credentials.enc）
- [x] 日志中无明文 API Key（SensitiveDataFilter 过滤）
- [x] `anyclaw config show` 脱敏显示（显示 ***xxxx）
- [x] 重启后凭证可正确读取（加密存储基于机器 ID）

## 文档

- [x] CLI 命令帮助更新（添加 --reveal 选项说明）

## 验收

- [x] `anyclaw config show` 显示 `***xxx` 格式
- [x] 日志中密钥被脱敏
- [x] 所有测试通过：`poetry run pytest tests/test_credentials.py -v`

## 实现摘要

### 新增文件
- `anyclaw/security/credentials.py` - 凭证管理核心模块
- `tests/test_credentials.py` - 完整测试套件 (33 tests)

### 修改文件
- `anyclaw/security/__init__.py` - 导出新模块
- `anyclaw/utils/logging_config.py` - 集成敏感数据过滤器
- `anyclaw/cli/config_cmd.py` - 添加脱敏显示和 --reveal 选项
- `pyproject.toml` - 添加 cryptography 依赖

### 核心功能
1. **CredentialManager** - 凭证加密存储（基于机器 ID 生成密钥）
2. **mask_sensitive()** - 敏感信息脱敏函数
3. **SensitiveDataFilter** - 日志过滤器
4. **config show --reveal** - 脱敏/明文切换显示
