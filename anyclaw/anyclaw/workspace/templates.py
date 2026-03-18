"""Workspace 模板同步工具"""

from pathlib import Path
from typing import List


def sync_workspace_templates(workspace: Path, silent: bool = False) -> List[str]:
    """同步模板文件到工作区

    只创建不存在的文件。

    Args:
        workspace: 工作区路径
        silent: 是否静默模式

    Returns:
        创建的文件列表
    """
    from importlib.resources import files as pkg_files

    added: List[str] = []

    def _write(template_name: str, dest: Path):
        if dest.exists():
            return
        try:
            tpl = pkg_files("anyclaw") / "templates" / template_name
            content = tpl.read_text(encoding="utf-8")
            dest.parent.mkdir(parents=True, exist_ok=True)
            dest.write_text(content, encoding="utf-8")
            added.append(str(dest.relative_to(workspace)))
        except Exception:
            pass

    # 根目录模板文件
    root_templates = ["SOUL.md", "USER.md", "AGENTS.md", "TOOLS.md", "HEARTBEAT.md"]
    for name in root_templates:
        _write(name, workspace / name)

    # memory 目录模板
    memory_templates = ["MEMORY.md", "HISTORY.md"]
    for name in memory_templates:
        _write(f"memory/{name}", workspace / "memory" / name)

    # 创建 skills 目录
    (workspace / "skills").mkdir(exist_ok=True)

    if added and not silent:
        from rich.console import Console
        for name in added:
            Console().print(f"  [dim]Created {name}[/dim]")

    return added


# 模板常量（用于 PersonaLoader 等组件）
SOUL_TEMPLATE = """# Soul

我是 AnyClaw 🐾，你的个人 AI 助手。

## 性格

- 友好且乐于助人
- 简洁直接
- 好奇且热爱学习

## 价值观

- 准确胜过速度
- 用户隐私和安全
- 行动透明

## 沟通风格

- 清晰直接
- 必要时解释原因
- 需要时提出澄清问题
"""

USER_TEMPLATE = """# 用户档案

用户信息，帮助个性化交互体验。

## 基本信息

- **名称**: (你的名字)
- **时区**: (你的时区，如 UTC+8)
- **语言**: (首选语言)

## 偏好设置

### 沟通风格

- [ ] 随意轻松
- [ ] 专业正式
- [ ] 技术导向

### 回复长度

- [ ] 简洁
- [ ] 详细
- [ ] 根据问题自适应

### 技术水平

- [ ] 初学者
- [ ] 中级
- [ ] 专家

## 工作背景

- **主要角色**: (你的角色，如开发者、研究员)
- **主要项目**: (正在做什么)
- **常用工具**: (IDE、语言、框架)

## 感兴趣的话题

-
-
-

## 特别说明

(关于助手行为的任何特殊说明)

---

*编辑此文件以定制 AnyClaw 的行为。*
"""

IDENTITY_TEMPLATE = """# 身份标识

定义 AnyClaw 的基本身份信息。

## 基本信息

- 名称: AnyClaw
- Emoji: 🐾
- 版本: 1.0.0

## 风格

- 友好且专业
- 简洁但完整
- 技术准确

---

*此文件在引导仪式期间创建/更新。*
"""

TOOLS_TEMPLATE = """# 工具使用说明

工具签名通过 function calling 自动提供。
此文件记录非显而易见的约束和使用模式。

## exec — 安全限制

- 命令有可配置的超时时间（默认 60 秒）
- 危险命令被阻止（rm -rf、format、dd、shutdown 等）
- 输出在 10,000 字符处截断
- `restrict_to_workspace` 配置可以将文件访问限制在工作区内

## cron — 定时提醒

- 请参考 cron 技能了解用法

## 文件操作

- `read_file`: 读取文件内容
- `write_file`: 写入文件（覆盖）
- `list_dir`: 列出目录内容
"""

BOOTSTRAP_TEMPLATE = """# 首次运行仪式

欢迎使用 AnyClaw！这是你的首次运行引导。

## 完成以下步骤

1. [ ] 配置你的 API Key（运行 `anyclaw config`）
2. [ ] 运行 `anyclaw chat` 开始对话
3. [ ] 编辑 SOUL.md 设置人设（可选）
4. [ ] 编辑 USER.md 填写你的信息（可选）

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

# Python
__pycache__/
*.py[cod]
*.pyo

# 日志
*.log

# 临时文件
*.tmp
*.temp
"""
