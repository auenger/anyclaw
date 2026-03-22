"""记忆工具

提供 save_memory 工具，让 LLM 可以主动更新长期记忆。

"""

import json
from datetime import datetime
from typing import Any, Dict, Optional

from anyclaw.memory.manager import MemoryManager
from anyclaw.tools.base import Tool
from anyclaw.config.settings import settings


class SaveMemoryTool(Tool):
    """保存记忆工具

    让 LLM 可以主动更新长期记忆（MEMORY.md）和追加历史记录（HISTORY.md）。
    """

    name = "save_memory"
    description = """Save important information to persistent memory.

Use this tool to:
- Remember user preferences (name, communication style, work style, etc.)
- Store important facts about the user (background, skills, projects)
- Record decisions or agreements made during conversation
- Update user profile when new information is discovered

WHEN TO USE:
- User mentions new personal information → save to memory
- User shares preferences or opinions → remember them
- Important decisions are made → record for future reference
- User corrects information → update the memory

The memory persists across sessions. Be proactive in remembering useful information!"""

    parameters = {
        "type": "object",
        "properties": {
            "history_entry": {
                "type": "string",
                "description": "A brief summary of key events/decisions from this conversation. "
                "Start with [YYYY-MM-DD HH:MM]. Include detail useful for grep search.",
            },
            "memory_update": {
                "type": "string",
                "description": "The updated long-term memory content in markdown format. "
                "Include all existing facts plus new ones. Return unchanged if nothing new to add.",
            },
            "section": {
                "type": "string",
                "description": "Optional: specific section to update (e.g., '用户信息', '偏好'). "
                "If provided, only that section will be updated.",
            },
        },
        "required": ["history_entry"],
    }

    def __init__(self, workspace_path: Optional[str] = None):
        """初始化工具

        Args:
            workspace_path: 工作区路径，默认使用 settings 中的配置
        """
        from pathlib import Path
        workspace = Path(workspace_path) if workspace_path else Path(settings.workspace).expanduser()
        self.memory = MemoryManager(workspace_path=workspace)

    async def execute(
        self,
        history_entry: str,
        memory_update: Optional[str] = None,
        section: Optional[str] = None,
        **kwargs,
    ) -> str:
        """执行保存记忆

        Args:
            history_entry: 历史记录条目
            memory_update: 完整的更新后记忆内容
            section: 可选，只更新特定部分

        Returns:
            操作结果信息
        """
        results = []

        # 1. 追加历史记录
        try:
            # 确保有时间戳前缀
            if not history_entry.startswith("["):
                timestamp = datetime.now().strftime("%Y-%m-%d %H:%M")
                history_entry = f"[{timestamp}] {history_entry}"

            self.memory.append_to_today(history_entry)
            results.append("✓ History entry saved")
        except Exception as e:
            results.append(f"✗ Failed to save history: {e}")

        # 2. 更新长期记忆（如果提供了）
        if memory_update:
            try:
                self.memory.save_long_term(memory_update)
                results.append("✓ Long-term memory updated")
            except Exception as e:
                results.append(f"✗ Failed to update memory: {e}")
        elif section:
            # 只更新特定部分
            try:
                # 从 history_entry 中提取内容作为 section 内容
                content = history_entry.split("]", 1)[-1].strip() if "]" in history_entry else history_entry
                self.memory.update_long_term(section, content)
                results.append(f"✓ Memory section '{section}' updated")
            except Exception as e:
                results.append(f"✗ Failed to update section: {e}")

        return "\n".join(results)


class UpdatePersonaTool(Tool):
    """更新人设工具

    让 LLM 可以更新 workspace 下的关键配置文件。
    """

    name = "update_persona"
    description = """Update workspace configuration files.

Use this tool to update:
- USER.md: User profile (name, preferences, background, contact info, etc.)
- SOUL.md: Assistant personality and behavior guidelines
- AGENTS.md: Agent instructions and rules
- TOOLS.md: Tool documentation
- HEARTBEAT.md: Periodic tasks

WHEN TO USE:
- User provides new personal information → update USER.md
- User asks to change assistant behavior → update SOUL.md
- User wants to modify agent rules → update AGENTS.md
- User explicitly asks to update any of these files

ALWAYS use this tool when user mentions updating their profile or settings."""

    # 支持的文件列表
    SUPPORTED_FILES = ["SOUL.md", "USER.md", "AGENTS.md", "TOOLS.md", "HEARTBEAT.md"]

    parameters = {
        "type": "object",
        "properties": {
            "file": {
                "type": "string",
                "enum": ["SOUL.md", "USER.md", "AGENTS.md", "TOOLS.md", "HEARTBEAT.md"],
                "description": "Which file to update. "
                "USER.md = user profile, SOUL.md = assistant personality, "
                "AGENTS.md = agent rules, TOOLS.md = tool docs, HEARTBEAT.md = periodic tasks.",
            },
            "content": {
                "type": "string",
                "description": "The new content for the file in markdown format. "
                "Provide COMPLETE file content, not just changes.",
            },
            "action": {
                "type": "string",
                "enum": ["replace", "append", "prepend"],
                "description": "How to update: 'replace' (default) = full replacement, "
                "'append' = add to end, 'prepend' = add to beginning.",
            },
        },
        "required": ["file", "content"],
    }

    def __init__(self, workspace_path: Optional[str] = None):
        """初始化工具"""
        from pathlib import Path
        from anyclaw.workspace.manager import WorkspaceManager

        workspace = Path(workspace_path) if workspace_path else Path(settings.workspace).expanduser()
        self.workspace = workspace
        self.ws_manager = WorkspaceManager(workspace_path=str(workspace))

    async def execute(
        self,
        file: str,
        content: str,
        action: str = "replace",
        **kwargs
    ) -> str:
        """执行更新人设文件"""
        from anyclaw.workspace.persona import PersonaLoader

        # 验证文件名
        if file not in self.SUPPORTED_FILES:
            return f"✗ Invalid file: {file}. Must be one of: {', '.join(self.SUPPORTED_FILES)}"

        file_path = self.workspace / file

        try:
            # 根据操作类型处理
            if action == "replace" or not file_path.exists():
                new_content = content
            elif action == "append":
                existing = file_path.read_text(encoding="utf-8")
                new_content = existing.rstrip() + "\n\n" + content
            elif action == "prepend":
                existing = file_path.read_text(encoding="utf-8")
                new_content = content.rstrip() + "\n\n" + existing
            else:
                new_content = content

            file_path.write_text(new_content, encoding="utf-8")

            # 清除 PersonaLoader 缓存
            try:
                persona = PersonaLoader(workspace=self.ws_manager)
                persona.clear_cache()
            except Exception:
                pass

            return f"✓ {file} updated successfully ({action}, {len(new_content)} chars)"
        except Exception as e:
            return f"✗ Failed to update {file}: {e}"


# 工具定义（用于注册到 registry）
SAVE_MEMORY_TOOL_DEF = {
    "type": "function",
    "function": {
        "name": "save_memory",
        "description": SaveMemoryTool.description,
        "parameters": SaveMemoryTool.parameters,
    }
}

UPDATE_PERSONA_TOOL_DEF = {
    "type": "function",
    "function": {
        "name": "update_persona",
        "description": UpdatePersonaTool.description,
        "parameters": UpdatePersonaTool.parameters,
    }
}
