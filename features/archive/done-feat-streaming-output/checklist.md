# 完成检查清单：流式输出支持

## 实现检查

### 配置
- [ ] `settings.py` 添加 `stream_enabled` 配置
- [ ] 配置项有正确的默认值
- [ ] 配置可通过环境变量覆盖

### Agent 流式响应
- [ ] `loop.py` 添加 `process_stream()` 方法
- [ ] `loop.py` 添加 `_stream_llm()` 方法
- [ ] 流式响应正确使用 async generator
- [ ] 完整响应正确保存到历史
- [ ] 原有 `process()` 方法保持不变

### Tool Calling 流式
- [ ] `tool_loop.py` 添加 `process_with_tools_stream()` 方法
- [ ] 工具调用前流式显示思考内容
- [ ] 工具执行时显示状态
- [ ] 多次工具调用正确处理

### CLI 流式显示
- [ ] `cli.py` 添加 `print_stream()` 方法
- [ ] `cli.py` 添加 `run_stream()` 方法
- [ ] 流式内容实时显示
- [ ] 正确的颜色和格式
- [ ] 中断处理（Ctrl+C）

### CLI 集成
- [ ] `app.py` chat 命令支持 `--stream/--no-stream` 选项
- [ ] 根据配置选择流式/非流式模式
- [ ] 命令行帮助正确显示

## 测试检查

- [ ] 创建 `tests/test_streaming.py`
- [ ] 测试 `process_stream()` 返回 async generator
- [ ] 测试流式响应内容完整
- [ ] 测试流式中断处理
- [ ] 测试配置开关
- [ ] 测试 Tool Calling 流式
- [ ] 所有现有测试仍然通过

## 文档检查

- [ ] 更新 CLAUDE.md 功能说明
- [ ] 添加流式输出使用说明
- [ ] 代码注释清晰
- [ ] 方法文档字符串完整

## 质量检查

- [ ] 代码格式化（black）
- [ ] 代码检查通过（ruff）
- [ ] 类型提示完整
- [ ] 无硬编码敏感信息

## 验收检查

- [ ] 启用流式时，响应实时显示
- [ ] 禁用流式时，等待完整响应后显示
- [ ] Tool Calling 场景流式正常
- [ ] Ctrl+C 可以中断流式输出
- [ ] 中断后不影响后续对话
- [ ] 错误信息正确显示

## 兼容性检查

- [ ] 原有 API 保持向后兼容
- [ ] OpenAI 模型流式正常
- [ ] Anthropic 模型流式正常
- [ ] ZAI 模型流式正常
- [ ] 不支持流式的模型自动回退
