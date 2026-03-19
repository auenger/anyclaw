"""上下文构建器

负责构建 Agent 的系统提示词，包括：
- 基础身份信息
- Bootstrap 文件（SOUL.md, USER.md, AGENTS.md, TOOLS.md）
- 长期记忆（MEMORY.md）
- 技能信息
"""

from pathlib import Path
from typing import List, Dict, Any, Optional

from anyclaw.config.settings import settings
from anyclaw.workspace.persona import PersonaLoader
from anyclaw.memory.manager import MemoryManager
from .history import ConversationHistory


class ContextBuilder:
    """上下文构建器

    
    """

    def __init__(
        self,
        history: ConversationHistory,
        skills_info: List[Dict],
        workspace: Optional[Path] = None,
    ):
        self.history = history
        self.skills_info = skills_info
        self.workspace = workspace or Path(settings.workspace).expanduser()

        # 初始化加载器
        from anyclaw.workspace.manager import WorkspaceManager
        ws_manager = WorkspaceManager(workspace_path=str(self.workspace))
        self.persona = PersonaLoader(workspace=ws_manager)
        self.memory = MemoryManager(workspace_path=self.workspace)

    def build(self) -> List[Dict]:
        """构建完整上下文"""
        context = []

        # 1. 系统提示词（包含所有内容）
        system_prompt = self.build_system_prompt()
        context.append({"role": "system", "content": system_prompt})

        # 2. 历史对话
        context.extend(self.history.get_history())

        return context

    def build_system_prompt(self) -> str:
        """构建系统提示词

        
        1. 基础身份
        2. Bootstrap 文件（SOUL.md, USER.md, AGENTS.md, TOOLS.md）
        3. 记忆（MEMORY.md）
        4. 技能摘要
        """
        parts = []

        # 1. 基础身份
        parts.append(self._get_identity())

        # 2. Bootstrap 文件
        bootstrap = self._load_bootstrap_files()
        if bootstrap:
            parts.append(bootstrap)

        # 3. 记忆上下文
        memory_context = self._get_memory_context()
        if memory_context:
            parts.append(memory_context)

        # 4. 技能信息
        if self.skills_info:
            skills_desc = self._build_skills_summary()
            if skills_desc:
                parts.append(skills_desc)

        return "\n\n---\n\n".join(parts)

    def _get_identity(self) -> str:
        """获取基础身份信息"""
        import platform

        workspace_path = str(self.workspace.expanduser().resolve())
        system = platform.system()
        runtime = f"{'macOS' if system == 'Darwin' else system} {platform.machine()}, Python {platform.python_version()}"

        return f"""# {settings.agent_name}

You are {settings.agent_name}, a helpful AI assistant.

## Runtime
{runtime}

## Workspace
Your workspace is at: {workspace_path}
- Long-term memory: {workspace_path}/memory/MEMORY.md (write important facts here using save_memory tool)
- History log: {workspace_path}/memory/HISTORY.md (grep-searchable)
- Custom skills: {workspace_path}/skills/{{skill-name}}/SKILL.md

## Guidelines
- State intent before tool calls, but NEVER predict or claim results before receiving them.
- Before modifying a file, read it first. Do not assume files or directories exist.
- If a tool call fails, analyze the error before retrying with a different approach.
- Ask for clarification when the request is ambiguous.
- Use the save_memory tool to persist important user preferences and facts.

Reply directly with text for conversations."""

    def _load_bootstrap_files(self) -> str:
        """加载所有 bootstrap 文件"""
        parts = []

        # 使用 PersonaLoader 加载人设文件
        persona = self.persona.load_all(is_private=True)

        if persona.get("soul"):
            parts.append(f"## SOUL.md\n\n{persona['soul']}")

        if persona.get("user"):
            parts.append(f"## USER.md\n\n{persona['user']}")

        if persona.get("identity"):
            parts.append(f"## AGENTS.md\n\n{persona['identity']}")

        if persona.get("tools"):
            parts.append(f"## TOOLS.md\n\n{persona['tools']}")

        return "\n\n".join(parts) if parts else ""

    def _get_memory_context(self) -> str:
        """获取记忆上下文"""
        # 加载长期记忆
        long_term = self.memory.load_long_term()
        if long_term:
            return f"# Memory\n\n## Long-term Memory\n{long_term}"
        return ""

    def _build_skills_summary(self) -> str:
        """构建技能摘要（XML 格式）"""
        # 如果 skills_info 是字典且包含 loader，使用新的 XML 格式
        if isinstance(self.skills_info, dict) and "loader" in self.skills_info:
            loader = self.skills_info["loader"]
            xml_summary = loader.build_skills_summary()

            # 获取并加载 always skills
            always_skills = loader.get_always_skills()
            always_content = ""
            if always_skills:
                always_content = loader.load_skills_for_context(always_skills)

            parts = ["# Skills\n", xml_summary]

            if always_content:
                parts.append("\n## Always-loaded Skills\n")
                parts.append(always_content)

            parts.append("\nUse skills when appropriate. Request skill content with `skill.load <name>` when needed.")

            return "\n".join(parts)

        # 向后兼容：旧格式
        lines = ["# Skills", ""]
        lines.append("You have access to these skills:")
        lines.append("")

        for skill in self.skills_info:
            lines.append(f"- **{skill['name']}**: {skill['description']}")

        lines.append("")
        lines.append("Use skills when appropriate to help the user.")

        return "\n".join(lines)
