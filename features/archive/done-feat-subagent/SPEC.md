# feat-subagent

**状态**: ✅ 已完成
**完成时间**: 2026-03-20
**优先级**: 80
**大小**: M
**提交**: 9ba8bc4, b8c5e27

## 描述

实现 SubAgent 子代理系统，支持后台任务执行、独立工具集、工作区隔离，与 nanobot 的 SpawnTool 保持兼容。

## 价值点

1. **后台任务执行**
   - 异步启动子代理执行任务
   - 不阻塞主会话
   - 完成后通过 MessageBus 通知

2. **独立工具集**
   - 子代理拥有独立的工具集
   - 可限制可用工具范围
   - 继承父会话的安全策略

3. **工作区隔离**
   - 子代理可配置独立工作区
   - 文件访问隔离
   - 可配置 restrict_workspace

4. **任务管理**
   - 创建/取消/查询子代理
   - 迭代次数限制
   - 超时控制

## 实现文件

- `anyclaw/agent/subagent.py` - SubagentManager 核心实现
- `anyclaw/agent/tools/spawn.py` - SpawnTool 工具定义
- `anyclaw/config/settings.py` - 配置项 (enable_subagent, subagent_max_iterations)

## 配置项

```json
{
  "enable_subagent": true,
  "subagent_max_iterations": 10,
  "subagent_restrict_workspace": true
}
```

## 使用示例

```python
from anyclaw.agent.subagent import SubagentManager
from anyclaw.agent.tools.spawn import SpawnTool

# 通过 SpawnTool 创建子代理
spawn_tool = SpawnTool(subagent_manager)
spawn_tool.set_context(channel="discord", chat_id="123456")

result = await spawn_tool.execute(
    task="分析代码库并生成文档",
    timeout=300
)
# 返回: {"status": "spawned", "subagent_id": "sub_abc123"}
```

## 架构流程

```
主会话 → SpawnTool.execute(task="...")
    ↓
SubagentManager.spawn(task, context)
    ↓
创建独立 AgentLoop (后台线程)
    ↓
执行任务 (独立工具集、独立工作区)
    ↓
完成 → MessageBus.publish_inbound(result)
    ↓
主会话收到通知
```

## SpawnTool 接口

```python
class SpawnTool(BaseTool):
    name = "spawn"
    description = "启动子代理执行后台任务"

    async def execute(
        self,
        task: str,           # 任务描述
        timeout: int = 300,  # 超时秒数
        tools: List[str] = None  # 可选：限制工具集
    ) -> Dict[str, Any]:
        pass
```

## 测试

```
tests/test_subagent.py
```

## 与 nanobot 对比

| 特性 | nanobot | AnyClaw | 状态 |
|------|---------|---------|------|
| 后台任务执行 | ✅ | ✅ | 完全兼容 |
| SpawnTool | ✅ | ✅ | 完全兼容 |
| 工作区隔离 | ✅ | ✅ | 完全兼容 |
| MessageBus 通知 | ✅ | ✅ | 完全兼容 |
| Channel 集成 | ✅ | ✅ | 完全兼容 |
