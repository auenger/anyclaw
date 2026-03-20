# 任务分解：迭代限制智能汇报

## 任务列表

### Task 1: 创建迭代摘要生成器
**优先级**: P0
**预估工作量**: 2h

- [ ] 创建 `agent/summary.py` 模块
- [ ] 实现 `IterationSummaryCollector` 类
  - `collect_tool_calls()` - 收集工具调用记录
  - `collect_statistics()` - 统计成功/失败/重复
  - `detect_loops()` - 检测重复调用循环
- [ ] 实现 `IterationSummaryGenerator` 类
  - `build_prompt()` - 构建分析 Prompt
  - `generate()` - 调用 LLM 生成汇报

### Task 2: 集成到 AgentLoop
**优先级**: P0
**预估工作量**: 1h

- [ ] 修改 `agent/loop.py` 的 `_run_with_tools()` 方法
  - 在迭代循环中收集工具调用数据
  - 达到限制时调用摘要生成器
  - 返回智能汇报而非简单字符串
- [ ] 添加配置项 `iteration_summary_enabled`

### Task 3: 集成到 ToolCallingLoop
**优先级**: P1
**预估工作量**: 0.5h

- [ ] 修改 `agent/tool_loop.py` 的 `process_with_tools()` 方法
- [ ] 复用 `IterationSummaryGenerator`

### Task 4: 适配 SubAgent
**优先级**: P1
**预估工作量**: 1h

- [ ] 修改 `agent/subagent.py`
- [ ] 确保 SubAgent 的汇报能正确传递给父 Agent

### Task 5: 配置支持
**优先级**: P2
**预估工作量**: 0.5h

- [ ] 在 `config/settings.py` 添加配置项
- [ ] 更新 `config.template.toml`

### Task 6: 测试
**优先级**: P0
**预估工作量**: 2h

- [ ] 单元测试：`test_iteration_summary.py`
  - 测试数据收集
  - 测试循环检测
  - 测试 Prompt 构建
- [ ] 集成测试：AgentLoop 达到限制时的行为
- [ ] 验收测试：运行实际场景验证汇报质量

## 依赖关系

```
Task 1 (创建摘要生成器)
    ↓
Task 2 (集成 AgentLoop) ← Task 5 (配置)
    ↓
Task 3 (集成 ToolCallingLoop)
    ↓
Task 4 (适配 SubAgent)
    ↓
Task 6 (测试)
```

## 风险与缓解

| 风险 | 影响 | 缓解措施 |
|------|------|----------|
| LLM 调用增加延迟 | 中 | 可配置开关，默认启用 |
| 汇报内容不准确 | 低 | 使用结构化 Prompt 模板 |
| 循环检测误报 | 低 | 设置合理的阈值（3 次） |
