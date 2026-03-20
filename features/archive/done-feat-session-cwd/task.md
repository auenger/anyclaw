# feat-session-cwd: 任务分解

## 任务列表

### T1: Session cwd 扩展
**优先级**: P0 | **预估**: 30min

- [ ] Session 添加 `get_cwd()` 方法
- [ ] Session 添加 `set_cwd()` 方法（含路径验证）
- [ ] 确保向后兼容（使用 metadata 存储）

**文件**:
- `anyclaw/session/models.py`

### T2: ExecTool cd 命令检测
**优先级**: P0 | **预估**: 45min

- [ ] 添加 `_detect_cd_command()` 方法
- [ ] 支持绝对路径 cd
- [ ] 支持相对路径 cd（相对于当前 cwd）
- [ ] 支持 `cd /path && cmd` 组合命令
- [ ] 无效路径不更新 cwd

**文件**:
- `anyclaw/tools/shell.py`

### T3: ExecTool 会话集成
**优先级**: P0 | **预估**: 30min

- [ ] ExecTool 接收 session 参数
- [ ] 执行时使用 session.cwd 作为默认工作目录
- [ ] cd 检测后更新 session.cwd
- [ ] 工作目录优先级: 参数 > session.cwd > self.working_dir > os.getcwd()

**文件**:
- `anyclaw/tools/shell.py`
- `anyclaw/agent/loop.py` (工具初始化)

### T4: 工具描述优化
**优先级**: P1 | **预估**: 15min

- [ ] 更新 ExecTool.description
- [ ] 更新 working_dir 参数描述
- [ ] 添加使用建议和示例

**文件**:
- `anyclaw/tools/shell.py`

### T5: 文件工具统一权限检查 ⭐ 新增
**优先级**: P0 | **预估**: 30min

- [ ] WriteFileTool 添加 `allow_all_access` 检查
- [ ] ListDirTool 添加 `allow_all_access` 检查
- [ ] 保持与 ReadFileTool 一致的检查逻辑

**文件**:
- `anyclaw/tools/filesystem.py`

### T6: 工具初始化优化 ⭐ 新增
**优先级**: P0 | **预估**: 20min

- [ ] AgentLoop 工具注册时传递 path_guard
- [ ] SubAgent 工具注册时传递 path_guard
- [ ] 确保所有文件工具都能正确接收配置

**文件**:
- `anyclaw/agent/loop.py`
- `anyclaw/agent/subagent.py`

### T7: 测试套件
**优先级**: P0 | **预估**: 60min

- [ ] Session cwd 测试（get/set/持久化）
- [ ] cd 命令检测测试（绝对/相对/组合/无效）
- [ ] ExecTool 会话集成测试
- [ ] 工作目录优先级测试
- [ ] 文件工具权限测试（allow_all_access 开关）

**文件**:
- `tests/test_session_cwd.py`
- `tests/test_exec_cwd.py`
- `tests/test_filesystem_permissions.py`

## 依赖图

```
T1 ──┬──> T3
     │
T2 ──┘

T4 (独立)

T5 ──> T6 ──> T7

T7 (依赖 T1-T6 完成)
```

## 验收标准

- [ ] 所有测试通过
- [ ] 覆盖率 > 80%
- [ ] 向后兼容（无 session 时行为不变）
- [ ] allow_all_access=true 时所有文件工具可访问任意路径
- [ ] allow_all_access=false 时仍执行安全检查
