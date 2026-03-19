# 任务分解: workspace 写入限制

## 任务列表

### Task 1: 添加配置项
**文件**: `anyclaw/config/settings.py`

- [ ] 添加 `restrict_to_workspace` 配置项
  - 类型: `bool`
  - 默认值: `True`
  - 描述: 是否限制文件写入到 workspace 内
  - 支持环境变量: `ANYCLAW_RESTRICT_TO_WORKSPACE`

### Task 2: 实现路径检查
**文件**: `anyclaw/tools/filesystem.py`

- [ ] 修改 `WriteFileTool.__init__()`
  - 添加 `restrict_to_workspace` 参数
  - 存储配置值

- [ ] 修改 `WriteFileTool._resolve_path()`
  - 添加路径检查逻辑
  - 使用 `resolve()` 解析真实路径（处理符号链接）
  - 当 `restrict_to_workspace=True` 时检查路径是否在 `allowed_dir` 内
  - 超出范围时抛出 `PermissionError`

- [ ] 修改 `WriteFileTool.execute()`
  - 捕获 `PermissionError`
  - 返回友好的错误信息

### Task 3: 传递配置到工具
**文件**: `anyclaw/agent/loop.py`

- [ ] 修改 `AgentLoop._register_default_tools()`
  - 从 settings 读取 `restrict_to_workspace`
  - 传递给 `WriteFileTool` 初始化

### Task 4: 更新文档
**文件**: `anyclaw/templates/TOOLS.md`

- [ ] 更新 TOOLS.md
  - 说明 `restrict_to_workspace` 配置的作用
  - 说明如何禁用限制

### Task 5: 添加测试
**文件**: `tests/test_filesystem_restrict.py`

- [ ] 测试默认配置
- [ ] 测试启用限制时的路径检查
- [ ] 测试禁用限制时允许任意路径
- [ ] 测试符号链接处理
- [ ] 测试错误提示信息

## 执行顺序

```
Task 1 (配置项)
    ↓
Task 2 (路径检查) ← 依赖 Task 1
    ↓
Task 3 (传递配置) ← 依赖 Task 1, 2
    ↓
Task 4 (更新文档) ← 可并行
    ↓
Task 5 (添加测试) ← 依赖所有实现
```

## 预估工作量

- Task 1: 10 分钟
- Task 2: 20 分钟
- Task 3: 5 分钟
- Task 4: 5 分钟
- Task 5: 15 分钟

**总计**: 约 55 分钟
