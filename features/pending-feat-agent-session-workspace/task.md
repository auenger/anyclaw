# 实现任务

## 任务列表

### 任务 1: 修改 SessionAgentPool.get_or_create()
- [ ] 检查 workspace 参数是否与默认 workspace 不同
- [ ] 如果不同，不传递共享的 SessionManager，让 AgentLoop 自己创建
- [ ] 添加日志记录，便于调试

### 任务 2: 验证修复
- [ ] 启动 sidecar 服务
- [ ] 选择非默认 Agent 进行对话
- [ ] 检查 session 文件是否保存到正确的目录

### 任务 3: 测试
- [ ] 添加单元测试验证不同 workspace 的 session 存储

## 技术要点

### SessionAgentPool.get_or_create() 修改

```python
def get_or_create(self, session_key: str, workspace: Optional[Path] = None) -> AgentLoop:
    effective_workspace = workspace or self.workspace

    # 检查是否在 pool 中
    if session_key in self._pool:
        agent, _ = self._pool[session_key]
        self._pool[session_key] = (agent, time.time())
        return agent

    # 决定是否使用共享的 SessionManager
    use_shared_session_manager = (
        self._shared_session_manager is not None
        and effective_workspace == self.workspace  # 只有默认 workspace 才使用共享的
    )

    # 创建 AgentLoop
    agent = AgentLoop(
        workspace=effective_workspace,
        enable_session_manager=True,
        enable_message_tool=True,
        enable_archive=True,
        session_manager=self._shared_session_manager if use_shared_session_manager else None,
    )
    # ...
```

## 风险评估

- **低风险**: 只影响非默认 workspace 的 AgentLoop 创建逻辑
- **向后兼容**: 默认 workspace 仍然使用共享的 SessionManager
