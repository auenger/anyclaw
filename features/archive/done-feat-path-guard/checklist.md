# 完成检查清单

## 代码实现

- [x] `anyclaw/security/path.py` 已创建
- [x] `PathGuard` 类已实现
- [x] 路径遍历检测已实现
- [x] 家目录 `~` 处理已实现
- [x] 环境变量展开已实现
- [x] 符号链接检查已实现
- [x] 允许目录范围检查已实现
- [x] 配置项已添加到 settings.py

## 测试

- [x] `tests/test_path_guard.py` 已创建
- [x] 测试 `../` 路径遍历阻止
- [x] 测试绝对路径范围检查
- [x] 测试 `~/.ssh/id_rsa` 阻止
- [x] 测试 `$HOME/.bashrc` 阻止
- [x] 测试符号链接指向工作区外阻止
- [x] 测试 extra_allowed_dirs 生效
- [x] 测试正常路径允许访问
- [x] 测试覆盖率 > 90% (37 tests)

## 工具集成

- [x] ReadFileTool 已集成
- [x] WriteFileTool 已集成
- [x] ListDirTool 已集成
- [x] ExecTool 路径参数已集成 (现有实现)

## 文档

- [x] 代码有详细注释
- [x] 错误信息清晰友好

## 验收

- [x] `read_file("../../../etc/passwd")` 被阻止
- [x] `read_file("/etc/passwd")` 被阻止（不在 workspace）
- [x] `read_file("~/.ssh/id_rsa")` 被阻止
- [x] `read_file("src/main.py")` 正常工作
- [x] 符号链接绕过被阻止
- [x] 所有测试通过：`poetry run pytest tests/test_path_guard.py -v`

## 安全验证

- [x] URL 编码绕过测试 (`%2e%2e%2f`)
- [x] 双重编码绕过测试
- [x] Unicode 绕过测试
- [x] 空字节注入测试
- [x] 长路径攻击测试
