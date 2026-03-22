# Cron 技能实现 - 任务分解

## 任务概览

| 任务 | 优先级 | 预估复杂度 | 依赖 |
|------|--------|-----------|------|
| T1: AgentLoop 集成 CronTool | P0 | M | - |
| T2: 创建 cron 内置技能 | P1 | S | - |
| T3: 编写测试 | P2 | M | T1, T2 |

---

## T1: AgentLoop 集成 CronTool

### 1.1 添加 CronService 管理

**文件**: `anyclaw/agent/loop.py`

**修改内容**:
1. 导入 CronService 和 CronTool
2. 在 `__init__` 中初始化 CronService
3. 添加 `_cron_service` 属性
4. 在 `_register_default_tools()` 中注册 CronTool

```python
# 导入
from anyclaw.cron.service import CronService
from anyclaw.cron.tool import CronTool

# __init__ 中
self._cron_service: Optional[CronService] = None
self._cron_tool: Optional[CronTool] = None

# 初始化 CronService
cron_store_path = self.workspace / ".anyclaw" / "cron_jobs.json"
self._cron_service = CronService(cron_store_path)

# _register_default_tools() 中
if self._cron_service:
    self._cron_tool = CronTool(self._cron_service)
    self.tools.register(self._cron_tool)
```

### 1.2 添加 CronService 生命周期管理

**文件**: `anyclaw/agent/loop.py`

**新增方法**:
```python
async def start_cron_service(self) -> None:
    """启动 CronService"""
    if self._cron_service:
        await self._cron_service.start()
        logger.info("CronService started")

async def stop_cron_service(self) -> None:
    """停止 CronService"""
    if self._cron_service:
        self._cron_service.stop()
        logger.info("CronService stopped")
```

### 1.3 添加 CronTool 上下文设置

**文件**: `anyclaw/agent/loop.py`

**新增方法**:
```python
def set_cron_context(self, channel: str, chat_id: str) -> None:
    """设置 CronTool 的上下文（由 Channel 调用）"""
    if self._cron_tool:
        self._cron_tool.set_context(channel, chat_id)
```

### 1.4 Channel 集成

**文件**: `anyclaw/channels/cli.py` (及其他 channel)

**修改内容**:
在 Channel 启动时调用:
```python
await agent_loop.start_cron_service()
agent_loop.set_cron_context(channel="cli", chat_id=session_id)
```

在 Channel 关闭时调用:
```python
await agent_loop.stop_cron_service()
```

---

## T2: 创建 cron 内置技能

### 2.1 创建技能目录

**目录**: `anyclaw/skills/builtin/cron/`

### 2.2 创建 SKILL.md

**文件**: `anyclaw/skills/builtin/cron/SKILL.md`

```markdown
---
name: cron
description: 定时任务和提醒功能，支持添加、列出、删除定时任务
version: 1.0.0
author: AnyClaw Team
---

# Cron 定时任务

## 功能说明

使用 cron 技能可以创建定时任务和提醒。

## 支持的操作

### 添加任务 (add)

**参数**:
- `message`: 提醒消息内容
- `every_seconds`: 间隔秒数（循环任务）
- `at`: ISO 格式时间（一次性任务）
- `cron_expr`: Cron 表达式（高级调度）

**示例**:
- 每小时提醒喝水: `every_seconds=3600, message="该喝水了"`
- 明天上午 9 点提醒: `at="2026-03-23T09:00:00", message="开会"`
- 每天 9 点提醒: `cron_expr="0 9 * * *", message="早安"`

### 列出任务 (list)

显示所有已创建的定时任务。

### 删除任务 (remove)

**参数**:
- `job_id`: 任务 ID

## 注意事项

- 定时任务在会话结束后仍会保留
- 可以使用 `/status` 命令查看当前任务状态
```

### 2.3 创建 skill.py（可选）

**文件**: `anyclaw/skills/builtin/cron/skill.py`

如果需要通过技能接口调用，创建 Python 技能包装器。

---

## T3: 编写测试

### 3.1 CronTool 注册测试

**文件**: `tests/test_agent_loop_cron.py`

```python
import pytest
from anyclaw.agent.loop import AgentLoop

@pytest.mark.asyncio
async def test_cron_tool_registered():
    """测试 CronTool 被正确注册"""
    loop = AgentLoop()
    tools = loop.tools.list_tools()
    tool_names = [t.name for t in tools]
    assert "cron" in tool_names

@pytest.mark.asyncio
async def test_cron_context_setting():
    """测试 CronTool 上下文设置"""
    loop = AgentLoop()
    loop.set_cron_context("cli", "test-session")
    # 验证上下文已设置
    assert loop._cron_tool._channel == "cli"
    assert loop._cron_tool._chat_id == "test-session"
```

### 3.2 CronService 生命周期测试

```python
@pytest.mark.asyncio
async def test_cron_service_lifecycle():
    """测试 CronService 启动和停止"""
    loop = AgentLoop()
    await loop.start_cron_service()
    assert loop._cron_service._running is True

    await loop.stop_cron_service()
    assert loop._cron_service._running is False
```

### 3.3 Cron 技能加载测试

**文件**: `tests/test_cron_skill.py`

```python
def test_cron_skill_loaded():
    """测试 cron 技能被加载"""
    from anyclaw.skills.loader import SkillLoader
    from pathlib import Path

    bundled_dir = Path(__file__).parent.parent / "anyclaw" / "skills" / "builtin"
    loader = SkillLoader(skills_dirs=[str(bundled_dir)])
    loader.load_all()

    assert "cron" in loader.md_skills or "cron" in loader.python_skills
```

---

## 实现顺序

1. **T1.1** - AgentLoop 添加 CronService 和 CronTool（核心）
2. **T1.2** - 添加生命周期管理方法
3. **T1.3** - 添加上下文设置方法
4. **T2** - 创建 cron 内置技能
5. **T3** - 编写测试验证
6. **T1.4** - Channel 集成（最后）
