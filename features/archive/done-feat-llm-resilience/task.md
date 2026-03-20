# 任务分解：LLM 响应韧性增强

## 任务列表

### Task 1: 配置项扩展
**文件**: `anyclaw/config/settings.py`

- [ ] 添加 `llm_empty_response_retry` 配置项（默认 2）
- [ ] 添加 `llm_max_retries` 配置项（默认 3）
- [ ] 添加 `llm_retry_delay` 配置项（默认 1.0）
- [ ] 添加 `llm_log_response_detail` 配置项（默认 False）

### Task 2: LiteLLM 重试配置
**文件**: `anyclaw/agent/loop.py`

- [ ] 在模块顶部配置 litellm 重试参数
- [ ] 从 settings 读取重试配置
- [ ] 添加重试日志记录

### Task 3: 空响应检测与恢复
**文件**: `anyclaw/agent/loop.py`

- [ ] 在 `_run_with_tools` 方法中添加空响应检测
- [ ] 实现空响应计数器（会话级别）
- [ ] 实现自动追加提示消息逻辑
- [ ] 添加重试次数限制
- [ ] 记录空响应警告日志

### Task 4: 增强诊断日志
**文件**: `anyclaw/agent/logger.py`

- [ ] 添加 `log_llm_response_detail` 方法
- [ ] 记录响应详情（model, content, tool_calls, usage, time）
- [ ] 在 loop.py 中调用诊断日志

### Task 5: 测试用例
**文件**: `tests/test_llm_resilience.py`

- [ ] 测试空响应检测
- [ ] 测试自动重试逻辑
- [ ] 测试重试次数限制
- [ ] 测试诊断日志输出
- [ ] 测试配置项读取

### Task 6: 文档更新
**文件**: `CLAUDE.md`

- [ ] 更新配置说明
- [ ] 添加故障排查指南

## 依赖关系

```
Task 1 (配置) ──→ Task 2 (LiteLLM配置)
              ──→ Task 3 (空响应处理)
              ──→ Task 4 (诊断日志)
                    ↓
              Task 5 (测试)
                    ↓
              Task 6 (文档)
```

## 预估工作量

| 任务 | 预估时间 | 复杂度 |
|------|----------|--------|
| Task 1 | 15 min | 低 |
| Task 2 | 20 min | 低 |
| Task 3 | 45 min | 中 |
| Task 4 | 30 min | 低 |
| Task 5 | 45 min | 中 |
| Task 6 | 15 min | 低 |
| **总计** | **~3h** | |
