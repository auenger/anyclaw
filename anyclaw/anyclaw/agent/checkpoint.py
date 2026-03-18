"""检查点管理器

保存和恢复对话状态，支持长对话的持久化。
"""

import json
import os
from datetime import datetime
from pathlib import Path
from typing import Optional, List, Dict, Any
from dataclasses import dataclass, asdict


@dataclass
class CheckpointInfo:
    """检查点信息"""
    name: str
    created_at: str
    message_count: int
    token_count: int
    metadata: Dict[str, Any]

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "CheckpointInfo":
        return cls(**data)


class CheckpointManager:
    """检查点管理器

    管理对话检查点的创建、加载、列表和删除。
    """

    DEFAULT_CHECKPOINT_DIR = "~/.anyclaw/checkpoints"
    CHECKPOINT_EXTENSION = ".json"

    def __init__(
        self,
        checkpoint_dir: Optional[str] = None,
        profile: Optional[str] = None,
    ):
        """初始化检查点管理器

        Args:
            checkpoint_dir: 检查点目录
            profile: Profile 名称（用于隔离不同配置的检查点）
        """
        self._profile = profile or os.environ.get("ANYCLAW_PROFILE", "default")
        self._base_dir = Path(checkpoint_dir or self.DEFAULT_CHECKPOINT_DIR).expanduser()
        self._checkpoint_dir = self._base_dir / self._profile

        # 确保目录存在
        self._checkpoint_dir.mkdir(parents=True, exist_ok=True)

    @property
    def checkpoint_dir(self) -> Path:
        """检查点目录"""
        return self._checkpoint_dir

    def save(
        self,
        name: str,
        messages: List[Dict[str, Any]],
        metadata: Optional[Dict[str, Any]] = None,
        token_count: int = 0,
    ) -> CheckpointInfo:
        """保存检查点

        Args:
            name: 检查点名称
            messages: 消息列表
            metadata: 额外元数据
            token_count: token 数

        Returns:
            CheckpointInfo 检查点信息
        """
        # 清理名称
        safe_name = self._sanitize_name(name)
        filepath = self._checkpoint_dir / f"{safe_name}{self.CHECKPOINT_EXTENSION}"

        # 创建检查点信息
        info = CheckpointInfo(
            name=safe_name,
            created_at=datetime.now().isoformat(),
            message_count=len(messages),
            token_count=token_count,
            metadata=metadata or {},
        )

        # 保存数据
        data = {
            "info": info.to_dict(),
            "messages": messages,
        }

        filepath.write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8")

        return info

    def load(self, name: str) -> tuple[List[Dict[str, Any]], CheckpointInfo]:
        """加载检查点

        Args:
            name: 检查点名称

        Returns:
            (消息列表, 检查点信息)

        Raises:
            FileNotFoundError: 检查点不存在
        """
        safe_name = self._sanitize_name(name)
        filepath = self._checkpoint_dir / f"{safe_name}{self.CHECKPOINT_EXTENSION}"

        if not filepath.exists():
            raise FileNotFoundError(f"Checkpoint not found: {name}")

        data = json.loads(filepath.read_text(encoding="utf-8"))

        messages = data["messages"]
        info = CheckpointInfo.from_dict(data["info"])

        return messages, info

    def list(self) -> List[CheckpointInfo]:
        """列出所有检查点

        Returns:
            检查点信息列表
        """
        checkpoints = []

        for filepath in self._checkpoint_dir.glob(f"*{self.CHECKPOINT_EXTENSION}"):
            try:
                data = json.loads(filepath.read_text(encoding="utf-8"))
                info = CheckpointInfo.from_dict(data["info"])
                checkpoints.append(info)
            except Exception:
                # 跳过无效的检查点
                continue

        # 按创建时间排序（最新的在前）
        checkpoints.sort(key=lambda x: x.created_at, reverse=True)

        return checkpoints

    def delete(self, name: str) -> bool:
        """删除检查点

        Args:
            name: 检查点名称

        Returns:
            是否成功删除
        """
        safe_name = self._sanitize_name(name)
        filepath = self._checkpoint_dir / f"{safe_name}{self.CHECKPOINT_EXTENSION}"

        if filepath.exists():
            filepath.unlink()
            return True

        return False

    def exists(self, name: str) -> bool:
        """检查检查点是否存在

        Args:
            name: 检查点名称

        Returns:
            是否存在
        """
        safe_name = self._sanitize_name(name)
        filepath = self._checkpoint_dir / f"{safe_name}{self.CHECKPOINT_EXTENSION}"
        return filepath.exists()

    def get_path(self, name: str) -> Path:
        """获取检查点文件路径

        Args:
            name: 检查点名称

        Returns:
            文件路径
        """
        safe_name = self._sanitize_name(name)
        return self._checkpoint_dir / f"{safe_name}{self.CHECKPOINT_EXTENSION}"

    def export_to_markdown(
        self,
        name: str,
        output_path: Optional[str] = None,
    ) -> str:
        """导出检查点为 Markdown

        Args:
            name: 检查点名称
            output_path: 输出路径（可选）

        Returns:
            Markdown 内容
        """
        messages, info = self.load(name)

        lines = [
            f"# 对话检查点: {info.name}",
            f"",
            f"- 创建时间: {info.created_at}",
            f"- 消息数: {info.message_count}",
            f"- Token 数: {info.token_count}",
            f"",
            "---",
            f"",
            "## 对话内容",
            f"",
        ]

        for msg in messages:
            role = msg.get("role", "unknown")
            content = msg.get("content", "")

            if isinstance(content, list):
                content = " ".join(str(c) for c in content)

            role_display = {
                "system": "🤖 System",
                "user": "👤 User",
                "assistant": "🤖 Assistant",
            }.get(role, role)

            lines.append(f"### {role_display}")
            lines.append(f"")
            lines.append(content)
            lines.append(f"")

        content = "\n".join(lines)

        if output_path:
            Path(output_path).write_text(content, encoding="utf-8")

        return content

    def _sanitize_name(self, name: str) -> str:
        """清理检查点名称

        Args:
            name: 原始名称

        Returns:
            安全的名称
        """
        # 替换不安全字符
        safe_name = "".join(c if c.isalnum() or c in "-_" else "_" for c in name)
        # 移除扩展名
        if safe_name.endswith(self.CHECKPOINT_EXTENSION):
            safe_name = safe_name[:-len(self.CHECKPOINT_EXTENSION)]
        return safe_name.lower()


# 全局检查点管理器实例
_checkpoint_manager: Optional[CheckpointManager] = None


def get_checkpoint_manager(
    checkpoint_dir: Optional[str] = None,
    profile: Optional[str] = None,
) -> CheckpointManager:
    """获取全局检查点管理器实例"""
    global _checkpoint_manager

    if _checkpoint_manager is None:
        _checkpoint_manager = CheckpointManager(
            checkpoint_dir=checkpoint_dir,
            profile=profile,
        )

    return _checkpoint_manager


def reset_checkpoint_manager() -> None:
    """重置全局检查点管理器"""
    global _checkpoint_manager
    _checkpoint_manager = None
