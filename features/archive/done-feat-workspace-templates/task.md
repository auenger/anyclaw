# feat-workspace-templates 任务列表

## 任务分解

### T1: 创建模板目录结构 ✅

- [x] 创建 `anyclaw/templates/` 目录
- [x] 创建 `anyclaw/templates/__init__.py`
- [x] 创建 `anyclaw/templates/memory/` 子目录

### T2: 创建模板文件 ✅

- [x] 创建 `SOUL.md` - Agent 人设模板
- [x] 创建 `USER.md` - 用户档案模板
- [x] 创建 `AGENTS.md` - Agent 指令模板
- [x] 创建 `TOOLS.md` - 工具说明模板
- [x] 创建 `HEARTBEAT.md` - 心跳任务模板
- [x] 创建 `memory/MEMORY.md` - 长期记忆模板
- [x] 创建 `memory/HISTORY.md` - 历史记录模板

### T3: 更新 workspace/templates.py ✅

- [x] 实现 `sync_workspace_templates()` 函数
- [x] 添加模板常量 (SOUL_TEMPLATE, USER_TEMPLATE 等)
- [x] 支持从包内资源读取模板
- [x] 只创建缺失文件（不覆盖现有）

### T4: 更新 workspace/manager.py ✅

- [x] 添加 `ensure_exists()` 方法
- [x] 添加 `get_bootstrap_files()` 方法
- [x] 添加 `delete_bootstrap()` 方法
- [x] 更新 `create()` 使用模板同步

### T5: 更新 CLI 命令 ✅

- [x] 更新 `setup` 命令
  - [x] 添加 `--force` 选项
  - [x] 显示工作区结构
  - [x] 显示下一步提示
- [x] 添加 `init` 命令
  - [x] 在当前目录创建 `.anyclaw`
  - [x] 同步模板文件

### T6: 更新打包配置 ✅

- [x] 更新 `pyproject.toml`
  - [x] 添加 `include` 配置包含 templates 目录

### T7: 测试验证 ✅

- [x] 测试 `anyclaw setup` 命令
- [x] 测试 `anyclaw init` 命令
- [x] 验证模板文件正确创建
- [x] 验证 memory/ 目录创建
- [x] 验证 skills/ 目录创建
- [x] 验证不覆盖现有文件

## 执行记录

### 2026-03-18

1. 创建 templates 目录和所有模板文件
2. 实现 sync_workspace_templates 函数
3. 更新 WorkspaceManager 类
4. 更新 CLI 命令
5. 更新 pyproject.toml 打包配置
6. 测试验证通过
