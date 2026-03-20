# 任务分解

## Phase 1: 核心防护模块

### Task 1.1: 创建路径守卫模块
- [x] 创建 `anyclaw/security/path.py`
- [x] 实现 `PathGuard` 类
- [x] 实现 `_check_traversal()` 方法
- [x] 实现 `_expand_path()` 方法
- [x] 实现 `_check_symlink()` 方法
- [x] 实现 `_check_in_allowed_dir()` 方法

### Task 1.2: 路径解析逻辑
- [x] 实现 `resolve_and_validate()` 主方法
- [x] 处理相对路径转绝对路径
- [x] 处理符号链接解析
- [x] 处理边界情况（不存在的路径等）

### Task 1.3: 核心防护测试
- [x] 创建 `tests/test_path_guard.py`
- [x] 测试路径遍历检测
- [x] 测试家目录访问阻止
- [x] 测试环境变量展开
- [x] 测试符号链接检查

## Phase 2: 配置支持

### Task 2.1: 配置项定义
- [x] 在 `settings.py` 添加 `path_extra_allowed_dirs`
- [x] 支持 `restrict_to_workspace` 开关
- [x] 支持 `extra_allowed_dirs` 列表
- [x] 支持 `allow_symlinks_in_workspace` 开关

### Task 2.2: 配置集成
- [x] PathGuard 从配置读取参数
- [x] 支持运行时配置更新

### Task 2.3: 配置测试
- [x] 测试 extra_allowed_dirs 生效
- [x] 测试配置开关生效

## Phase 3: 工具集成

### Task 3.1: 文件系统工具集成
- [x] ReadFileTool 集成 PathGuard
- [x] WriteFileTool 集成 PathGuard
- [x] ListDirTool 集成 PathGuard
- [x] 返回友好的错误信息

### Task 3.2: Shell 工具集成
- [x] ExecTool 路径参数验证 (现有实现)
- [x] restrict_to_workspace 模式实现

### Task 3.3: 集成测试
- [x] 端到端测试文件操作路径验证
- [x] 测试正常路径仍可访问
- [x] 测试跨平台路径处理

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

- Phase 1: 核心防护模块 - 2-3 小时 ✅
- Phase 2: 配置支持 - 1 小时 ✅
- Phase 3: 工具集成 - 2 小时 ✅
- 总计: 5-6 小时 ✅

## 完成状态

**全部完成** - 2026-03-20

所有任务已完成，37 个测试全部通过。
