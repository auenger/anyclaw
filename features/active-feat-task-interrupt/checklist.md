# feat-task-interrupt: 完成检查清单

## 实现检查

### VP1: AgentLoop 中断机制

- [x] 添加 `_active_tasks` 字典
- [x] 添加 `_abort_flags` 字典
- [x] 实现 `register_task()` 方法
- [x] 实现 `unregister_task()` 方法
- [x] 实现 `request_abort()` 方法
- [x] 修改 `_run_with_tools()` 检查中断标志
- [x] 中断时返回友好消息

### VP2: CLIChannel 直接处理 /stop

- [x] 添加 `_agent_loop` 属性
- [x] 实现 `set_agent_loop()` 方法
- [x] 修改 `start()` 直接处理 `/stop`
- [x] 实现 `_handle_stop_direct()` 方法
- [x] 修改 `run_stream()` 支持中断

### VP3: chat 命令集成

- [x] 在 `chat()` 中调用 `channel.set_agent_loop(agent)`

### VP4: StopCommandHandler 更新

- [x] 使用 `request_abort()` 方法
- [x] 保持向后兼容

## 测试检查

- [x] 测试任务注册和取消注册
- [x] 测试中断标志设置
- [x] 测试任务取消
- [x] 测试迭代循环检查中断
- [x] 测试 CLI 直接处理 /stop
- [x] 所有测试通过 (17/17)

## 文档检查

- [x] 代码注释完整

## 验收测试

- [ ] 启动 `anyclaw chat`
- [ ] 发送会触发多次工具调用的消息
- [ ] 在工具执行过程中输入 `/stop`
- [ ] 验证任务立即中断
- [ ] 显示 "任务已停止" 提示

## 完成标准

- [x] 所有测试通过
- [ ] 代码审查完成
- [ ] 功能验收通过
