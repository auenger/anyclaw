# 完成检查清单

## 代码实现

- [ ] `anyclaw/security/path.py` 已创建
- [ ] `PathGuard` 类已实现
- [ ] 路径遍历检测已实现
- [ ] 家目录 `~` 处理已实现
- [ ] 环境变量展开已实现
- [ ] 符号链接检查已实现
- [ ] 允许目录范围检查已实现
- [ ] 配置项已添加到 settings.py

## 测试

- [ ] `tests/test_path_guard.py` 已创建
- [ ] 测试 `../` 路径遍历阻止
- [ ] 测试绝对路径范围检查
- [ ] 测试 `~/.ssh/id_rsa` 阻止
- [ ] 测试 `$HOME/.bashrc` 阻止
- [ ] 测试符号链接指向工作区外阻止
- [ ] 测试 extra_allowed_dirs 生效
- [ ] 测试正常路径允许访问
- [ ] 测试覆盖率 > 90%

## 工具集成

- [ ] ReadFileTool 已集成
- [ ] WriteFileTool 已集成
- [ ] ListDirTool 已集成
- [ ] ExecTool 路径参数已集成

## 文档

- [ ] 代码有详细注释
- [ ] 错误信息清晰友好

## 验收

- [ ] `read_file("../../../etc/passwd")` 被阻止
- [ ] `read_file("/etc/passwd")` 被阻止（不在 workspace）
- [ ] `read_file("~/.ssh/id_rsa")` 被阻止
- [ ] `read_file("src/main.py")` 正常工作
- [ ] 符号链接绕过被阻止
- [ ] 所有测试通过：`poetry run pytest tests/test_path_guard.py -v`

## 安全验证

- [ ] URL 编码绕过测试 (`%2e%2e%2f`)
- [ ] 双重编码绕过测试
- [ ] Unicode 绕过测试
- [ ] 空字节注入测试
- [ ] 长路径攻击测试
