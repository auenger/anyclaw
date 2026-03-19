"""Bootstrap 引导系统"""

import os
from pathlib import Path
from typing import Optional

from anyclaw.workspace.manager import WorkspaceManager


class BootstrapLoader:
    """引导文件加载器

    负责加载和管理引导文件，包括文件截断和完成标记。
    """

    DEFAULT_MAX_CHARS = 20000
    DEFAULT_TOTAL_MAX_CHARS = 150000

    def __init__(
        self,
        workspace: Optional[WorkspaceManager] = None,
        max_chars: Optional[int] = None,
        total_max_chars: Optional[int] = None,
    ):
        """初始化引导加载器

        Args:
            workspace: 工作区管理器
            max_chars: 单个文件最大字符数
            total_max_chars: 总最大字符数
        """
        self.workspace = workspace or WorkspaceManager()
        self.max_chars = max_chars or int(
            os.environ.get("ANYCLAW_BOOTSTRAP_MAX_CHARS", self.DEFAULT_MAX_CHARS)
        )
        self.total_max_chars = total_max_chars or int(
            os.environ.get("ANYCLAW_BOOTSTRAP_TOTAL_MAX_CHARS", self.DEFAULT_TOTAL_MAX_CHARS)
        )

    def load(self) -> tuple[str, bool]:
        """加载引导内容

        Returns:
            (引导内容, 是否需要截断)
        """
        files = self.workspace.get_bootstrap_files()

        if not files:
            return "", False

        contents = []
        total_chars = 0
        truncated = False

        for file_info in files:
            content = file_info["content"]
            file_size = len(content)

            # 检查单个文件大小
            if file_size > self.max_chars:
                content = content[:self.max_chars]
                content += f"\n\n... [文件 {file_info['name']} 已截断，原大小: {file_size} 字符]"
                truncated = True

            # 检查总大小
            if total_chars + len(content) > self.total_max_chars:
                remaining = self.total_max_chars - total_chars
                if remaining > 0:
                    content = content[:remaining]
                    content += f"\n\n... [总内容已截断，达到 {self.total_max_chars} 字符限制]"
                    truncated = True
                else:
                    break

            contents.append(f"### {file_info['name']}\n\n{content}")
            total_chars += len(content)

        return "\n\n".join(contents), truncated

    def has_bootstrap(self) -> bool:
        """检查是否存在引导文件"""
        bootstrap_path = self.workspace.path / "BOOTSTRAP.md"
        return bootstrap_path.exists()

    def is_completed(self) -> bool:
        """检查引导是否已完成

        引导完成的标志是 BOOTSTRAP.md 文件不存在。
        """
        return not self.has_bootstrap()

    def mark_completed(self) -> bool:
        """标记引导完成

        通过删除 BOOTSTRAP.md 文件来标记完成。

        Returns:
            是否成功标记
        """
        return self.workspace.delete_bootstrap()

    def get_bootstrap_prompt(self) -> str:
        """获取引导提示词

        Returns:
            用于注入到系统提示的引导内容
        """
        content, truncated = self.load()

        if not content:
            return ""

        prompt = f"""
## 首次运行引导

以下是首次运行的引导内容，请引导用户完成设置：

{content}

"""
        if truncated:
            prompt += "\n[注意: 部分内容因长度限制已被截断]\n"

        prompt += "\n请引导用户完成以上步骤，完成后告知用户可以删除 BOOTSTRAP.md 文件。\n"

        return prompt
