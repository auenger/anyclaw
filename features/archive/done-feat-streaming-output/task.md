# 任务分解：流式输出支持

## 任务列表

### 任务 1：添加流式配置

**文件**: `anyclaw/config/settings.py`

**实现要点**:
- 添加 `stream_enabled` 配置项
- 添加 `stream_buffer_size` 配置项（可选）

**代码框架**:
```python
# 流式输出配置
stream_enabled: bool = Field(
    default=True,
    description="是否启用流式输出"
)
```

---

### 任务 2：实现 Agent 流式响应

**文件**: `anyclaw/agent/loop.py`

**实现要点**:
- 添加 `process_stream()` 方法（async generator）
- 添加 `_stream_llm()` 私有方法
- 保持原有 `process()` 方法不变（向后兼容）
- 处理流式异常

**代码框架**:
```python
async def process_stream(self, user_input: str):
    """流式处理用户输入"""
    self.history.add_user_message(user_input)

    context_builder = ContextBuilder(self.history, self._get_skills_info())
    messages = context_builder.build()

    full_response = []

    # 流式调用
    if self.enable_tools and self.tool_loop and self.skills:
        async for chunk in self.tool_loop.process_with_tools_stream(messages):
            full_response.append(chunk)
            yield chunk
    else:
        async for chunk in self._stream_llm(messages):
            full_response.append(chunk)
            yield chunk

    # 保存完整响应到历史
    self.history.add_assistant_message("".join(full_response))


async def _stream_llm(self, messages: list):
    """流式调用 LLM"""
    kwargs = self._get_llm_kwargs(settings.llm_model)
    kwargs["model"] = settings.llm_model
    kwargs["messages"] = messages
    kwargs["stream"] = True

    try:
        response = await acompletion(**kwargs)
        async for chunk in response:
            content = chunk.choices[0].delta.content
            if content:
                yield content
    except Exception as e:
        yield f"[Error: {str(e)}]"
```

---

### 任务 3：实现 Tool Calling 流式支持

**文件**: `anyclaw/agent/tool_loop.py`

**实现要点**:
- 添加 `process_with_tools_stream()` 方法
- 流式输出工具调用前的思考内容
- 工具执行时显示状态

**代码框架**:
```python
async def process_with_tools_stream(self, messages: list):
    """流式处理带工具调用的请求"""
    iteration = 0

    while iteration < self.max_iterations:
        # 流式获取响应
        response_text = []
        tool_calls = []

        async for chunk in await self._stream_completion(messages):
            # 累积内容
            if chunk.choices[0].delta.content:
                content = chunk.choices[0].delta.content
                response_text.append(content)
                yield content

            # 检测工具调用
            # ...

        # 如果有工具调用，执行并继续
        if tool_calls:
            # 执行工具
            # 添加到消息历史
            iteration += 1
        else:
            break
```

---

### 任务 4：实现 CLI 流式显示

**文件**: `anyclaw/channels/cli.py`

**实现要点**:
- 添加 `print_stream()` 方法
- 修改 `run()` 支持流式处理函数
- 处理中断信号

**代码框架**:
```python
async def print_stream(self, stream_gen):
    """打印流式响应"""
    self.console.print(f"\n[bold green]{settings.agent_name}:[/bold green] ", end="")

    try:
        async for chunk in stream_gen:
            self.console.print(chunk, end="", highlight=False)
    except asyncio.CancelledError:
        self.console.print("\n[dim][interrupted][/dim]")

    self.console.print()  # 完成后换行


async def run_stream(self, process_func: Callable[[str], AsyncGenerator]):
    """运行 CLI 循环（流式）"""
    self.print_welcome()
    self.running = True

    while self.running:
        try:
            user_input = self.get_input()

            if user_input.lower() in ['exit', 'quit']:
                self.console.print("[yellow]Goodbye![/yellow]")
                break

            if not user_input.strip():
                continue

            # 流式处理
            await self.print_stream(process_func(user_input))

        except KeyboardInterrupt:
            self.console.print("\n[yellow]Interrupted. Goodbye![/yellow]")
            break
```

---

### 任务 5：集成到 CLI 应用

**文件**: `anyclaw/cli/app.py`

**实现要点**:
- 修改 `chat` 命令支持流式模式
- 根据配置选择流式/非流式

**代码框架**:
```python
@app.command()
def chat(
    agent_name: str = typer.Option(None, help="Agent name"),
    model: str = typer.Option(None, help="LLM model"),
    stream: bool = typer.Option(None, "--stream/--no-stream", help="Enable streaming"),
):
    """Start interactive chat"""

    # 覆盖配置
    if stream is not None:
        settings.stream_enabled = stream

    # ...

    if settings.stream_enabled:
        asyncio.run(channel.run_stream(agent.process_stream))
    else:
        asyncio.run(channel.run(agent.process))
```

---

### 任务 6：编写测试

**文件**: `tests/test_streaming.py`

**测试覆盖**:
- 流式响应测试
- 流式中断测试
- 配置开关测试
- CLI 流式显示测试

---

### 任务 7：更新文档

**文件**:
- `CLAUDE.md` - 更新功能说明
- `README.md` - 添加流式输出说明

---

## 依赖关系

```
任务 1: 配置
    ↓
任务 2: Agent 流式 ─────┐
    ↓                   │
任务 3: Tool Calling    │
    ↓                   │
任务 4: CLI 流式 ←──────┘
    ↓
任务 5: 集成
    ↓
任务 6: 测试
    ↓
任务 7: 文档
```

## 预计工作量

| 任务 | 预计时间 | 复杂度 |
|------|----------|--------|
| 任务 1: 配置 | 5 min | 低 |
| 任务 2: Agent 流式 | 30 min | 中 |
| 任务 3: Tool Calling 流式 | 45 min | 高 |
| 任务 4: CLI 流式 | 20 min | 中 |
| 任务 5: 集成 | 10 min | 低 |
| 任务 6: 测试 | 25 min | 中 |
| 任务 7: 文档 | 10 min | 低 |

**总计**: ~2.5 小时

## 注意事项

1. **向后兼容**: 保留原有的 `process()` 方法
2. **错误处理**: 流式过程中的错误要优雅处理
3. **中断安全**: Ctrl+C 要正确清理状态
4. **性能**: 流式输出不应增加额外延迟
