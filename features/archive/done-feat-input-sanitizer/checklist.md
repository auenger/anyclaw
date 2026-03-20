# 完成检查清单

## 代码实现

- [x] `anyclaw/security/validators.py` 已创建
- [x] `Validator` 基类已实现
- [x] `URLValidator` 已实现
- [x] `PathValidator` 已实现
- [x] `anyclaw/security/sanitizers.py` 已创建
- [x] `ContentSanitizer` 已实现
- [x] `anyclaw/tools/decorators.py` 已创建
- [x] `@validate_params` 装饰器已实现
- [x] `@sanitize_input` 装饰器已实现
- [x] `@require_params` 装饰器已实现
- [x] `@validate_and_sanitize` 组合装饰器已实现

## 测试

- [x] `tests/test_validators.py` 已创建
- [x] 测试非空验证
- [x] 测试长度验证
- [x] 测试范围验证
- [x] 测试 URL 验证
- [x] 测试路径验证
- [x] `tests/test_sanitizers.py` 已创建
- [x] 测试 Unicode 清理
- [x] 测试控制字符清理
- [x] 测试消息截断
- [x] 测试覆盖率 > 85% (validators: 93%, sanitizers: 100%)

## 集成

- [x] AgentLoop 消息清理已集成 (`anyclaw/agent/loop.py`)
- [x] 工具参数验证已集成
  - `ExecTool`: 命令验证 + 超时范围验证
  - `ReadFileTool`: 路径验证
  - `WriteFileTool`: 路径验证 + 内容非空检查
- [x] 错误信息友好

## 文档

- [x] 代码有详细注释
- [x] 验证规则在代码中明确说明

## 验收

- [x] 空消息返回清晰错误
- [x] 10万+ 字符消息被截断
- [x] 零宽字符被移除
- [x] file:// URL 被阻止
- [x] Windows 保留名被警告
- [x] 所有测试通过 (91 passed)

## 安全验证

- [x] Unicode 绕过测试
- [x] 编码绕过测试
- [x] 混合攻击测试
