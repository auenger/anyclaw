# feat-task-interrupt: 完成检查清单

## 实现检查

### VP1: AgentLoop 中断机制

- [ ] 添加 `_active_tasks` 字典
- [ ] 添加 `_abort_flags` 字典
- [ ] 实现 `register_task()` 方法
- [ ] 实现 `unregister_task()` 方法
- [ ] 实现 `request_abort()` 方法
- [ ] 修改 `_run_with_tools()` 检查中断标志
- [ ] 中断时返回友好消息

### VP2: CLIChannel 直接处理 /stop

- [ ] 添加 `agent_loop` 属性
- [ ] 实现 `set_agent_loop()` 方法
- [ ] 修改 `run()` 直接处理 `/stop`
- [ ] 实现 `_handle_stop_direct()` 方法
- [ ] 实现 `_dispatch_with_tracking()` 方法
- [ ] 修改 `run_stream()` 支持中断

### VP3: chat 命令集成

- [ ] 在 `chat()` 中调用 `channel.set_agent_loop(agent)`

### VP4: StopCommandHandler 更新

- [ ] 使用 `request_abort()` 方法
- [ ] 保持向后兼容

## 测试检查

- [ ] 测试任务注册和取消注册
- [ ] 测试中断标志设置
- [ ] 测试任务取消
- [ ] 测试迭代循环检查中断
- [ ] 测试 CLI 直接处理 /stop
- [ ] 测试消息处理作为独立 Task
- [ ] 所有测试通过

## 文档检查

- [ ] 更新 CLAUDE.md（如有必要）
- [ ] 代码注释完整

## 验收测试

- [ ] 启动 `anyclaw chat`
- [ ] 发送会触发多次工具调用的消息
- [ ] 在工具执行过程中输入 `/stop`
- [ ] 验证任务立即中断
- [ ] 显示 "任务已停止" 提示

## 完成标准

- [ ] 所有测试通过
- [ ] 代码审查完成
- [ ] 功能验收通过
