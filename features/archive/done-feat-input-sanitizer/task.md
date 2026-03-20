# 任务分解

## Phase 1: 验证器模块

### Task 1.1: 创建基础验证器
- [ ] 创建 `anyclaw/security/validators.py`
- [ ] 实现 `Validator` 基类
- [ ] 实现 `not_empty()` 方法
- [ ] 实现 `max_length()` 方法
- [ ] 实现 `in_range()` 方法

### Task 1.2: URL 验证器
- [ ] 实现 `URLValidator` 类
- [ ] 实现 URL 格式验证
- [ ] 实现协议白名单
- [ ] 实现危险协议阻止

### Task 1.3: 路径验证器
- [ ] 实现 `PathValidator` 类
- [ ] 实现文件名验证
- [ ] 实现 Windows 保留名检查
- [ ] 实现危险字符检查

### Task 1.4: 验证器测试
- [ ] 创建 `tests/test_validators.py`
- [ ] 测试所有验证方法

## Phase 2: 清理器模块

### Task 2.1: 创建清理器
- [ ] 创建 `anyclaw/security/sanitizers.py`
- [ ] 实现 `ContentSanitizer` 类
- [ ] 实现危险 Unicode 移除
- [ ] 实现控制字符清理
- [ ] 实现消息长度限制

### Task 2.2: 清理器测试
- [ ] 创建 `tests/test_sanitizers.py`
- [ ] 测试各种清理场景

## Phase 3: 集成

### Task 3.1: 工具验证装饰器
- [ ] 创建 `anyclaw/tools/decorators.py`
- [ ] 实现 `@validate_params` 装饰器
- [ ] 集成到现有工具

### Task 3.2: 消息处理集成
- [ ] 集成到 AgentLoop
- [ ] 集成到 Channel

### Task 3.3: 集成测试
- [ ] 端到端测试消息清理
- [ ] 端到端测试参数验证

## 依赖关系

```
Task 1.1 ─→ Task 1.2 ─→ Task 1.4
      │           │
      ↓           │
Task 1.3 ─────────┘
      │
      ↓
Task 2.1 ─→ Task 2.2
      │
      ↓
Task 3.1 ─→ Task 3.3
      │
Task 3.2 ──────────┘
```

## 预计工作量

- Phase 1: 验证器模块 - 2 小时
- Phase 2: 清理器模块 - 1-2 小时
- Phase 3: 集成 - 2 小时
- 总计: 5-6 小时
