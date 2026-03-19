# 完成检查清单

## 代码实现

- [ ] `anyclaw/security/validators.py` 已创建
- [ ] `Validator` 基类已实现
- [ ] `URLValidator` 已实现
- [ ] `PathValidator` 已实现
- [ ] `anyclaw/security/sanitizers.py` 已创建
- [ ] `ContentSanitizer` 已实现
- [ ] `anyclaw/tools/decorators.py` 已创建
- [ ] `@validate_params` 装饰器已实现

## 测试

- [ ] `tests/test_validators.py` 已创建
- [ ] 测试非空验证
- [ ] 测试长度验证
- [ ] 测试范围验证
- [ ] 测试 URL 验证
- [ ] 测试路径验证
- [ ] `tests/test_sanitizers.py` 已创建
- [ ] 测试 Unicode 清理
- [ ] 测试控制字符清理
- [ ] 测试消息截断
- [ ] 测试覆盖率 > 85%

## 集成

- [ ] AgentLoop 消息清理已集成
- [ ] 工具参数验证已集成
- [ ] 错误信息友好

## 文档

- [ ] 代码有详细注释
- [ ] 验证规则文档

## 验收

- [ ] 空消息返回清晰错误
- [ ] 10万+ 字符消息被截断
- [ ] 零宽字符被移除
- [ ] file:// URL 被阻止
- [ ] Windows 保留名被警告
- [ ] 所有测试通过

## 安全验证

- [ ] Unicode 绕过测试
- [ ] 编码绕过测试
- [ ] 混合攻击测试
