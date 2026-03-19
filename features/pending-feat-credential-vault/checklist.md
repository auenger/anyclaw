# 完成检查清单

## 代码实现

- [ ] `anyclaw/security/credentials.py` 已创建
- [ ] `CredentialManager` 类已实现
- [ ] 加密存储已实现
- [ ] 系统密钥链支持（可选）
- [ ] 脱敏模式已定义
- [ ] 日志过滤器已实现
- [ ] 配置显示脱敏已实现

## 测试

- [ ] `tests/test_credentials.py` 已创建
- [ ] 测试加密存储和读取
- [ ] 测试各种密钥格式脱敏
- [ ] 测试配置显示脱敏
- [ ] 测试格式验证
- [ ] 测试覆盖率 > 80%

## 安全验证

- [ ] 配置文件中无明文 API Key
- [ ] 日志中无明文 API Key
- [ ] `anyclaw config show` 脱敏显示
- [ ] 重启后凭证可正确读取

## 文档

- [ ] 凭证管理文档
- [ ] CLI 命令帮助更新

## 验收

- [ ] `cat ~/.anyclaw/config.json` 不显示明文密钥
- [ ] `anyclaw config show` 显示 `sk-***xxx`
- [ ] 日志中密钥被脱敏
- [ ] 所有测试通过：`poetry run pytest tests/test_credentials.py -v`
