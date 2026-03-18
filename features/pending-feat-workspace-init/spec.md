# feat-workspace-init: Workspace 初始化和引导

## 概述

为 AnyClaw 创建智能体工作区系统，类似 OpenClaw 的 `~/.openclaw/workspace`。工作区是智能体的"家"，用于存储人设、记忆和引导文件，与配置和凭证分离。

## 依赖

- `feat-mvp-agent` (已完成) - Agent 引擎核心
- `feat-mvp-cli` (已完成) - CLI 交互频道

## 用户价值点

### VP1: Workspace 目录管理

**价值**: 创建和管理智能体工作区目录，支持多工作区和配置覆盖。

**Gherkin 场景**:

```gherkin
Feature: Workspace 目录管理

  Scenario: 默认工作区创建
    Given 用户首次运行 anyclaw
    When 执行 "anyclaw setup" 或 "anyclaw onboard"
    Then 应在 ~/.anyclaw/workspace 创建工作区
    And 工作区应包含默认引导文件
    And 应初始化 git 仓库

  Scenario: 自定义工作区位置
    Given 用户想使用自定义工作区路径
    When 在配置中设置 workspace: "~/my-workspace"
    Then 应使用自定义路径作为工作区
    And 配置应持久化到 ~/.anyclaw/anyclaw.json

  Scenario: Profile 多工作区
    Given 设置环境变量 ANYCLAW_PROFILE=work
    When 启动 anyclaw
    Then 应使用 ~/.anyclaw/workspace-work 作为工作区
    And 与默认工作区隔离

  Scenario: 工作区状态检查
    Given 工作区已存在
    When 执行 "anyclaw workspace status"
    Then 应显示工作区路径
    And 显示已存在的文件列表
    And 显示 git 状态（如果是仓库）
```

### VP2: 引导文件系统

**价值**: 提供工作区引导文件，在会话开始时自动加载。

**Gherkin 场景**:

```gherkin
Feature: 引导文件系统

  Scenario: 创建默认引导文件
    Given 全新工作区
    When 执行 "anyclaw setup"
    Then 应创建 BOOTSTRAP.md
    And 应创建 .gitignore
    And 文件应包含模板内容

  Scenario: 首次运行仪式
    Given 工作区包含 BOOTSTRAP.md
    When 智能体首次启动
    Then 应读取并执行 BOOTSTRAP.md 内容
    And 仪式完成后应标记为已完成

  Scenario: 跳过引导文件创建
    Given 配置 skip_bootstrap: true
    When 执行 "anyclaw setup"
    Then 不应创建引导文件
    And 使用用户提供的文件

  Scenario: 引导文件大小限制
    Given 引导文件超过 20000 字符
    When 加载到上下文
    Then 应截断文件内容
    And 显示截断警告
```

## 技术设计

### 核心组件

```
anyclaw/
├── workspace/
│   ├── __init__.py
│   ├── manager.py       # WorkspaceManager 类
│   ├── templates.py     # 模板文件
│   └── bootstrap.py     # 引导系统
└── cli/
    └── workspace.py     # workspace 命令
```

### WorkspaceManager 设计

```python
# workspace/manager.py
from pathlib import Path
from typing import Optional
import os

class WorkspaceManager:
    """工作区管理器"""

    DEFAULT_DIR = "~/.anyclaw/workspace"
    STATE_DIR = ".anyclaw"

    def __init__(
        self,
        workspace_path: Optional[str] = None,
        profile: Optional[str] = None,
    ):
        if workspace_path:
            self.path = Path(workspace_path).expanduser()
        elif profile and profile.lower() != "default":
            self.path = Path.home() / ".anyclaw" / f"workspace-{profile}"
        else:
            self.path = Path.home() / ".anyclaw" / "workspace"

    def exists(self) -> bool:
        """检查工作区是否存在"""
        return self.path.exists()

    def create(self, init_git: bool = True) -> None:
        """创建工作区"""
        self.path.mkdir(parents=True, exist_ok=True)
        if init_git:
            self._init_git()
        self._create_default_files()

    def _init_git(self) -> None:
        """初始化 git 仓库"""
        git_dir = self.path / ".git"
        if not git_dir.exists():
            import subprocess
            subprocess.run(["git", "init"], cwd=self.path, check=True)

    def _create_default_files(self) -> None:
        """创建默认文件"""
        # 创建 BOOTSTRAP.md
        bootstrap_path = self.path / "BOOTSTRAP.md"
        if not bootstrap_path.exists():
            bootstrap_path.write_text(self._get_bootstrap_template())

        # 创建 .gitignore
        gitignore_path = self.path / ".gitignore"
        if not gitignore_path.exists():
            gitignore_path.write_text(self._get_gitignore_template())

    def get_bootstrap_files(self) -> list[dict]:
        """获取所有引导文件"""
        files = []
        for filename in ["BOOTSTRAP.md"]:
            filepath = self.path / filename
            if filepath.exists():
                files.append({
                    "name": filename,
                    "path": str(filepath),
                    "content": filepath.read_text(),
                })
        return files

    @property
    def state_dir(self) -> Path:
        """状态目录 (~/.anyclaw/)"""
        return Path.home() / ".anyclaw"
```

### 引导模板

```python
# workspace/templates.py

BOOTSTRAP_TEMPLATE = """# 首次运行仪式

欢迎使用 AnyClaw！这是你的首次运行引导。

## 完成以下步骤

1. [ ] 配置你的 API Key
2. [ ] 运行 `anyclaw chat` 开始对话
3. [ ] 编辑 SOUL.md 设置人设
4. [ ] 编辑 USER.md 填写你的信息

完成后删除此文件。

---
*此文件仅在首次运行时加载。*
"""

GITIGNORE_TEMPLATE = """# 系统文件
.DS_Store

# 环境变量
.env

# 密钥
*.key
*.pem
**/secrets*
"""
```

### CLI 命令

```bash
# 工作区管理
anyclaw workspace init [--path PATH]       # 初始化工作区
anyclaw workspace status                   # 查看状态
anyclaw workspace path                     # 显示路径
anyclaw workspace files                    # 列出文件

# 设置
anyclaw setup [--workspace PATH]           # 创建/更新工作区
```

### 配置扩展

```python
# config/settings.py 新增
class Settings(BaseSettings):
    # 工作区配置
    workspace: str = Field(default="~/.anyclaw/workspace")
    skip_bootstrap: bool = Field(default=False)
    bootstrap_max_chars: int = Field(default=20000)
    bootstrap_total_max_chars: int = Field(default=150000)
```

## 数据流

```
anyclaw setup / onboard
    ↓
检查工作区是否存在
    ├─ 存在 → 加载现有文件
    └─ 不存在 ↓
        创建目录结构
            ↓
        初始化 git
            ↓
        创建引导文件
            ↓
        首次运行仪式
```

## 与配置目录的分离

| 工作区 (~/.anyclaw/workspace) | 配置目录 (~/.anyclaw/) |
|------------------------------|------------------------|
| SOUL.md, USER.md | anyclaw.json (配置) |
| MEMORY.md, memory/ | credentials/ (凭证) |
| BOOTSTRAP.md | sessions/ (会话) |
| skills/ | skills/ (托管 Skills) |
| **可提交 git** | **不应提交** |

## 验收标准

- [ ] 默认工作区正确创建
- [ ] 支持自定义路径
- [ ] 支持多 Profile
- [ ] 引导文件正确生成
- [ ] git 初始化正常
- [ ] CLI 命令正常工作
- [ ] 测试覆盖率 > 80%

## 优先级

| 功能 | 优先级 | 理由 |
|------|--------|------|
| 目录创建 | P0 | 基础能力 |
| 引导文件 | P0 | 首次体验 |
| 多 Profile | P1 | 高级功能 |

## 参考

- OpenClaw `docs/zh-CN/concepts/agent-workspace.md`
- OpenClaw `src/agents/workspace.ts`
- Nanobot `nanobot/templates/`
