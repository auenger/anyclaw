# 任务分解

## Phase 1: 核心保护层

### Task 1.1: 创建 guards.py 模块
- [ ] 创建 `anyclaw/tools/guards.py`
- [ ] 定义 `CORE_DENY_PATTERNS` 常量
- [ ] 实现 `CoreGuard` 类（封装核心保护逻辑）
- [ ] 添加详细的正则表达式注释

### Task 1.2: 改造 ExecTool
- [ ] 修改 `anyclaw/tools/shell.py`
- [ ] 引入 `CoreGuard` 替代现有的 `_guard_command`
- [ ] 保持向后兼容（deny_patterns 参数保留但语义变化）
- [ ] 添加 `restrict_to_workspace` 支持（与 feat-workspace-restrict 配合）

### Task 1.3: 核心保护测试
- [ ] 创建 `tests/test_exec_guard.py`
- [ ] 测试所有核心保护模式
- [ ] 测试各种绕过尝试

## Phase 2: 配置扩展层

### Task 2.1: 配置项定义
- [ ] 在 `anyclaw/config/settings.py` 添加 `SecuritySettings`
- [ ] 支持 `deny_patterns` 和 `allow_patterns` 配置
- [ ] 添加配置验证逻辑

### Task 2.2: ExecTool 集成配置
- [ ] 从配置读取 `user_deny_patterns`
- [ ] 从配置读取 `allow_patterns`
- [ ] 实现白名单模式逻辑

### Task 2.3: 配置扩展测试
- [ ] 测试用户自定义 deny_patterns
- [ ] 测试 allow_patterns 白名单模式
- [ ] 测试配置与核心保护的优先级

## Phase 3: CLI 支持

### Task 3.1: 查看安全规则命令
- [ ] 添加 `anyclaw security show` 命令
- [ ] 显示核心保护规则（标记 [core]）
- [ ] 显示用户自定义规则（标记 [user]）

### Task 3.2: CLI 测试
- [ ] 测试 `anyclaw security show` 输出
- [ ] 测试配置变更后的显示更新

## 依赖关系

```
Task 1.1 ─→ Task 1.2 ─→ Task 1.3
                │
                ↓
         Task 2.1 ─→ Task 2.2 ─→ Task 2.3
                              │
                              ↓
                        Task 3.1 ─→ Task 3.2
```

## 预计工作量

- Phase 1: 核心保护层 - 1-2 小时
- Phase 2: 配置扩展层 - 1-2 小时
- Phase 3: CLI 支持 - 0.5-1 小时
- 总计: 3-5 小时
