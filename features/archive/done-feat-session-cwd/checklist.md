# feat-session-cwd: 完成检查清单

## 代码实现

### 会话级 cwd
- [x] Session.get_cwd() 方法实现
- [x] Session.set_cwd() 方法实现（含路径验证）

### ExecTool cd 检测
- [x] ExecTool._detect_cd_command() 方法实现
- [x] ExecTool 支持 session 参数
- [x] ExecTool 使用 session.cwd 作为默认工作目录
- [x] ExecTool 更新工具描述

### 文件工具权限统一 ⭐
- [x] WriteFileTool 添加 allow_all_access 检查
- [x] ListDirTool 添加 allow_all_access 检查
- [x] AgentLoop 工具注册时传递 path_guard
- [x] SubAgent 工具注册时传递 path_guard

## 测试覆盖

### Session cwd 测试
- [x] get_cwd() 默认值
- [x] set_cwd() 路径验证
- [x] 会话持久化保留 cwd

### cd 命令检测测试
- [x] 绝对路径 cd
- [x] 相对路径 cd
- [x] cd && cmd 组合命令
- [x] 无效路径不更新

### ExecTool 集成测试
- [x] 无 session 时行为不变
- [x] 有 session 时使用 session.cwd
- [x] 参数优先级正确

### 文件工具权限测试 ⭐
- [x] WriteFileTool allow_all_access=true 可写任意路径
- [x] ListDirTool allow_all_access=true 可列任意目录
- [x] allow_all_access=false 时仍执行安全检查
- [x] path_guard 正确传递和生效

## 质量检查

- [x] 所有测试通过 (`poetry run pytest tests/`)
- [x] 代码格式化 (`poetry run black anyclaw/`)
- [x] Ruff 检查通过（无新增问题）
- [x] 覆盖率 > 80%

## 文档更新

- [x] spec.md 更新实现细节
- [x] CLAUDE.md 更新（如有必要）

## 完成确认

- [x] 功能在 CLI 中验证
- [x] 无向后兼容问题
- [x] allow_all_access 配置对所有文件工具生效
