# 任务分解

## Phase 1: 核心防护模块

### Task 1.1: 创建路径守卫模块
- [ ] 创建 `anyclaw/security/path.py`
- [ ] 实现 `PathGuard` 类
- [ ] 实现 `_check_traversal()` 方法
- [ ] 实现 `_expand_path()` 方法
- [ ] 实现 `_check_symlink()` 方法
- [ ] 实现 `_check_in_allowed_dir()` 方法

### Task 1.2: 路径解析逻辑
- [ ] 实现 `resolve_and_validate()` 主方法
- [ ] 处理相对路径转绝对路径
- [ ] 处理符号链接解析
- [ ] 处理边界情况（不存在的路径等）

### Task 1.3: 核心防护测试
- [ ] 创建 `tests/test_path_guard.py`
- [ ] 测试路径遍历检测
- [ ] 测试家目录访问阻止
- [ ] 测试环境变量展开
- [ ] 测试符号链接检查

## Phase 2: 配置支持

### Task 2.1: 配置项定义
- [ ] 在 `settings.py` 添加 `PathSecuritySettings`
- [ ] 支持 `restrict_to_workspace` 开关
- [ ] 支持 `extra_allowed_dirs` 列表
- [ ] 支持 `allow_symlinks_in_workspace` 开关

### Task 2.2: 配置集成
- [ ] PathGuard 从配置读取参数
- [ ] 支持运行时配置更新

### Task 2.3: 配置测试
- [ ] 测试 extra_allowed_dirs 生效
- [ ] 测试配置开关生效

## Phase 3: 工具集成

### Task 3.1: 文件系统工具集成
- [ ] ReadFileTool 集成 PathGuard
- [ ] WriteFileTool 集成 PathGuard
- [ ] ListDirTool 集成 PathGuard
- [ ] 返回友好的错误信息

### Task 3.2: Shell 工具集成
- [ ] ExecTool 路径参数验证
- [ ] restrict_to_workspace 模式实现

### Task 3.3: 集成测试
- [ ] 端到端测试文件操作路径验证
- [ ] 测试正常路径仍可访问
- [ ] 测试跨平台路径处理

## 依赖关系

```
Task 1.1 ─→ Task 1.2 ─→ Task 1.3
                │
                ↓
         Task 2.1 ─→ Task 2.2 ─→ Task 2.3
                              │
                              ↓
                        Task 3.1 ─→ Task 3.3
                              │
                        Task 3.2 ──────────┘
```

## 预计工作量

- Phase 1: 核心防护模块 - 2-3 小时
- Phase 2: 配置支持 - 1 小时
- Phase 3: 工具集成 - 2 小时
- 总计: 5-6 小时
