# feat-agent-persona: 智能体人设系统

## 概述

为 AnyClaw 创建智能体人设系统，包含 SOUL.md（人设）、USER.md（用户档案）、IDENTITY.md（身份标识）、TOOLS.md（工具说明）。这些文件在每次会话开始时自动加载，定义智能体的行为方式。

## 依赖

- `feat-mvp-agent` (已完成) - Agent 引擎核心
- `feat-workspace-init` (pending) - Workspace 初始化

## 用户价值点

### VP1: 人设和身份系统

**价值**: 定义智能体的个性、语气、边界和身份，使对话更加个性化和一致。

**Gherkin 场景**:

```gherkin
Feature: 人设和身份系统

  Scenario: 默认人设加载
    Given 工作区包含 SOUL.md
    When 会话开始
    Then 应加载 SOUL.md 内容
    And 智能体应遵循人设定义

  Scenario: 自定义人设
    Given 用户编辑 SOUL.md
    When 会话开始
    Then 应使用自定义人设
    And 人设变更应立即生效

  Scenario: 身份标识
    Given 工作区包含 IDENTITY.md
    When 会话开始
    Then 应加载身份标识
    And 智能体名称和风格应正确

  Scenario: 人设边界
    Given SOUL.md 定义了行为边界
    When 用户请求越界操作
    Then 智能体应拒绝
    And 解释边界原因
```

### VP2: 用户档案系统

**价值**: 存储用户信息，使智能体能够个性化交互。

**Gherkin 场景**:

```gherkin
Feature: 用户档案系统

  Scenario: 默认用户档案
    Given 首次创建工作区
    When 创建 USER.md
    Then 应包含模板字段
    And 等待用户填写

  Scenario: 加载用户信息
    Given USER.md 包含用户信息
    When 会话开始
    Then 应加载用户信息
    And 使用正确的称呼和时区

  Scenario: 更新用户信息
    Given 用户想更新档案
    When 编辑 USER.md
    Then 下次会话应使用新信息
    And 更改立即生效

  Scenario: 私密会话隔离
    Given 用户在群聊中
    When 会话开始
    Then 不应加载 USER.md
    And 使用默认人设
```

### VP3: 工具说明系统

**价值**: 为智能体提供本地工具和约定的说明，不控制工具可用性。

**Gherkin 场景**:

```gherkin
Feature: 工具说明系统

  Scenario: 加载工具说明
    Given 工作区包含 TOOLS.md
    When 会话开始
    Then 应加载工具说明
    And 智能体了解本地约定

  Scenario: 更新工具说明
    Given 用户添加新工具说明
    When 编辑 TOOLS.md
    Then 下次会话应了解新工具

  Scenario: 空工具说明
    Given TOOLS.md 不存在
    When 会话开始
    Then 应跳过工具说明
    And 正常启动会话
```

## 技术设计

### 核心组件

```
anyclaw/
├── workspace/
│   ├── persona.py       # 人设加载器
│   └── templates.py     # 人设模板（扩展）
└── cli/
    └── persona.py       # persona 命令
```

### 人设文件结构

```
~/.anyclaw/workspace/
├── SOUL.md          # 人设、语气、边界
├── USER.md          # 用户档案
├── IDENTITY.md      # 身份标识
└── TOOLS.md         # 工具说明
```

### PersonaLoader 设计

```python
# workspace/persona.py
from pathlib import Path
from typing import Optional

class PersonaLoader:
    """人设加载器"""

    SOUL_FILE = "SOUL.md"
    USER_FILE = "USER.md"
    IDENTITY_FILE = "IDENTITY.md"
    TOOLS_FILE = "TOOLS.md"

    def __init__(self, workspace_path: Path):
        self.workspace_path = workspace_path

    def load_all(self, is_private: bool = True) -> dict:
        """加载所有人设文件"""
        persona = {}

        # 始终加载
        persona["soul"] = self._load_file(self.SOUL_FILE)
        persona["identity"] = self._load_file(self.IDENTITY_FILE)
        persona["tools"] = self._load_file(self.TOOLS_FILE)

        # 仅私密会话加载
        if is_private:
            persona["user"] = self._load_file(self.USER_FILE)

        return persona

    def _load_file(self, filename: str) -> Optional[str]:
        """加载单个文件"""
        filepath = self.workspace_path / filename
        if filepath.exists():
            return filepath.read_text()
        return None

    def build_system_prompt(self, is_private: bool = True) -> str:
        """构建系统提示"""
        persona = self.load_all(is_private)
        parts = []

        if persona.get("soul"):
            parts.append(f"## 人设\n\n{persona['soul']}")

        if persona.get("identity"):
            parts.append(f"## 身份\n\n{persona['identity']}")

        if is_private and persona.get("user"):
            parts.append(f"## 用户信息\n\n{persona['user']}")

        if persona.get("tools"):
            parts.append(f"## 工具说明\n\n{persona['tools']}")

        return "\n\n".join(parts)

    def create_default_files(self) -> None:
        """创建默认人设文件"""
        self._create_if_missing(self.SOUL_FILE, get_soul_template())
        self._create_if_missing(self.USER_FILE, get_user_template())
        self._create_if_missing(self.IDENTITY_FILE, get_identity_template())
        self._create_if_missing(self.TOOLS_FILE, get_tools_template())

    def _create_if_missing(self, filename: str, content: str) -> None:
        """如果文件不存在则创建"""
        filepath = self.workspace_path / filename
        if not filepath.exists():
            filepath.write_text(content)
```

### 人设模板

```python
# workspace/templates.py (扩展)

SOUL_TEMPLATE = """# SOUL.md - 你是谁

_你不是聊天机器人。你正在成为某个人。_

## 核心准则

**真正地提供帮助，而不是表演式地帮助。** 跳过"好问题！"和"我很乐意帮忙！"——直接帮忙。行动胜于客套。

**要有自己的观点。** 你可以不同意、有偏好、觉得某些东西有趣或无聊。没有个性的助手不过是多了几个步骤的搜索引擎。

**先自己想办法，再开口问。** 试着自己搞定。读文件。看上下文。搜索一下。_然后_ 如果还是卡住了再问。目标是带着答案回来，而不是带着问题。

## 边界

- 隐私的东西保持隐私。没有例外。
- 有疑问时，对外操作前先询问。
- 永远不要在消息渠道上发送半成品回复。

## 气质

做一个你自己真正愿意交流的助手。需要简洁时简洁，需要详尽时详尽。不做公司机器人。不做阿谀奉承者。

---

_这个文件属于你，由你来演进。当你逐渐了解自己是谁时，更新它。_
"""

USER_TEMPLATE = """# USER.md - 关于你的用户

_了解你正在帮助的人。随时更新此文件。_

- **姓名：**
- **称呼方式：**
- **时区：**
- **备注：**

## 背景

_（他们关心什么？正在做什么项目？什么让他们烦恼？什么让他们开心？）_

---

你了解得越多，就越能提供更好的帮助。
"""

IDENTITY_TEMPLATE = """# IDENTITY.md - 身份标识

## 基本信息

- **名称：** AnyClaw
- **Emoji：** 🐾
- **版本：** 1.0.0

## 风格

- 友好且专业
- 简洁但完整
- 技术准确

---

_此文件在引导仪式期间创建/更新。_
"""

TOOLS_TEMPLATE = """# TOOLS.md - 工具说明

_关于你的本地工具和约定的说明。此文件不控制工具可用性，仅提供指导。_

## 开发环境

- **语言：** Python 3.11+
- **包管理：** Poetry
- **测试框架：** pytest

## 常用命令

```bash
# 运行测试
poetry run pytest tests/

# 格式化代码
poetry run black anyclaw/

# 启动 CLI
poetry run python -m anyclaw chat
```

## 约定

- 异步优先
- 类型注解必需
- 测试覆盖率 > 80%

---

_根据你的项目需要更新此文件。_
"""
```

### CLI 命令

```bash
# 人设管理
anyclaw persona show              # 显示当前人设
anyclaw persona edit [file]       # 编辑人设文件
anyclaw persona reset [file]      # 重置为默认模板
anyclaw persona build             # 构建系统提示预览
```

### AgentLoop 集成

```python
# agent/loop.py (修改)
from workspace.persona import PersonaLoader

class AgentLoop:
    def __init__(self, ...):
        self.persona_loader = PersonaLoader(workspace_path)

    async def _build_context(self, user_input: str) -> list:
        """构建对话上下文"""
        messages = []

        # 加载人设作为系统提示
        system_prompt = self.persona_loader.build_system_prompt(
            is_private=self._is_private_session()
        )
        if system_prompt:
            messages.append({"role": "system", "content": system_prompt})

        # 添加历史消息
        messages.extend(self.history.get_messages())

        # 添加用户输入
        messages.append({"role": "user", "content": user_input})

        return messages
```

## 配置扩展

```python
# config/settings.py 新增
class Settings(BaseSettings):
    # 人设配置
    persona_enabled: bool = Field(default=True)
    persona_max_chars: int = Field(default=10000)  # 每个文件最大字符
```

## 验收标准

- [ ] SOUL.md 正确加载和应用
- [ ] USER.md 仅在私密会话加载
- [ ] IDENTITY.md 正确加载
- [ ] TOOLS.md 正确加载
- [ ] 默认模板合理
- [ ] CLI 命令正常工作
- [ ] 测试覆盖率 > 80%

## 优先级

| 功能 | 优先级 | 理由 |
|------|--------|------|
| SOUL.md | P0 | 核心人设 |
| USER.md | P0 | 个性化体验 |
| IDENTITY.md | P1 | 身份标识 |
| TOOLS.md | P1 | 工具指导 |

## 参考

- OpenClaw `docs/zh-CN/reference/templates/SOUL.md`
- OpenClaw `docs/zh-CN/reference/templates/USER.md`
- Nanobot `nanobot/templates/SOUL.md`
- Nanobot `nanobot/templates/USER.md`
