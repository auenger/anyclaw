"""Session Manager - 会话管理系统（最终版）

完美复刻 nanobot 的 SessionManager 实现，同时保持向后兼容。
"""

import json
import logging
import shutil
from dataclasses import dataclass, field
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional

from .models import Session, SessionMessage


logger = logging.getLogger(__name__)


@dataclass
class SessionManagerConfig:
    """SessionManager 配置"""
    workspace: Path
    sessions_dir: Optional[Path] = None
    max_history_messages: int = 500
    enable_persistence: bool = True
    enable_memory_cache: bool = True


class SessionManager:
    """
    会话管理器

    特性：
    - JSONL 格式持久化（与 nanobot 兼容）
    - 内存缓存（避免重复磁盘 IO）
    - 多会话支持
    - 会话清理和迁移
    - 工具调用边界检测

    与现有 History 系统的关系：
    - SessionManager 责责持久化和多会话管理
    - ConversationHistory 保持向后兼容，用于简单场景
    - AgentLoop 可以选择使用任一个
    """

    def __init__(self, config: SessionManagerConfig):
        self.config = config
        self.workspace = config.workspace

        # 会话目录
        self.sessions_dir = config.sessions_dir
        if self.sessions_dir is None:
            self.sessions_dir = self.workspace / "sessions"
        elif not isinstance(self.sessions_dir, Path):
            self.sessions_dir = Path(self.sessions_dir)

        if not self.sessions_dir.is_dir():
            self.sessions_dir.mkdir(parents=True, exist_ok=True)

        # 内存缓存
        self._cache: Dict[str, Session] = {}

        logger.info(f"SessionManager initialized with workspace: {self.workspace}")

    def _get_session_path(self, key: str) -> Path:
        """获取会话文件路径"""
        safe_key = key.replace(":", "_")
        return self.sessions_dir / f"{safe_key}.jsonl"

    def get_or_create(self, key: str) -> Session:
        """
        获取或创建会话

        Args:
            key: 会话键（通常为 "channel:chat_id" 或 session_key）

        Returns:
            Session 对象
        """
        # 1. 检查内存缓存
        if key in self._cache:
            logger.debug(f"Session cache hit: {key}")
            return self._cache[key]

        # 2. 尝试从磁盘加载
        path = self._get_session_path(key)
        if path.exists():
            session = Session.load(path)
            if session:
                self._cache[key] = session
                logger.debug(f"Session loaded from disk: {key}")
                return session

        # 3. 创建新会话
        logger.info(f"Creating new session: {key}")
        session = Session(key=key)
        self._cache[key] = session
        return session

    def get(self, key: str) -> Optional[Session]:
        """
        获取会话（不创建）

        Args:
            key: 会话键

        Returns:
            Session 对象，如果不存在则返回 None
        """
        # 1. 检查内存缓存
        if key in self._cache:
            logger.debug(f"Session cache hit: {key}")
            return self._cache[key]

        # 2. 尝试从磁盘加载
        path = self._get_session_path(key)
        if path.exists():
            session = Session.load(path)
            if session:
                self._cache[key] = session
                logger.debug(f"Session loaded from disk: {key}")
                return session

        return None

    def save(self, session: Session) -> None:
        """保存会话到磁盘"""
        if not self.config.enable_persistence:
            return

        path = self._get_session_path(session.key)
        session.save(path)
        self._cache[session.key] = session
        logger.debug(f"Session saved: {session.key}")

    def invalidate(self, key: str) -> None:
        """从内存缓存移除会话"""
        self._cache.pop(key, None)
        logger.debug(f"Session invalidated: {key}")

    def add_message(
        self,
        key: str,
        role: str,
        content: Optional[str] = None,
        **kwargs
    ) -> None:
        """添加消息到会话（快捷方法）"""
        session = self.get_or_create(key)
        # 直接创建消息并添加，避免双重调用
        msg = SessionMessage(
            role=role,
            content=content,
            timestamp=datetime.now().isoformat(),
            **kwargs
        )
        session.messages.append(msg)
        session.updated_at = datetime.now()
        self.save(session)

    def get_history(
        self,
        key: str,
        max_messages: Optional[int] = None
    ) -> List[Dict[str, Any]]:
        """获取会话历史（快捷方法）"""
        session = self.get_or_create(key)
        max_messages = max_messages or self.config.max_history_messages
        return session.get_history(max_messages)

    def clear_session(self, key: str) -> None:
        """清空会话"""
        session = self.get_or_create(key)
        session.clear()
        self.save(session)
        logger.info(f"Session cleared: {key}")

    def list_sessions(self) -> List[Dict[str, Any]]:
        """
        列出所有会话

        Returns:
            会话信息列表
        """
        sessions = []

        for path in self.sessions_dir.glob("*.jsonl"):
            try:
                # 读取元数据行和最后一条消息
                with open(path, encoding="utf-8") as f:
                    first_line = f.readline().strip()
                    if first_line:
                        data = json.loads(first_line)
                        if data.get("_type") == "metadata":
                            key = data.get("key") or path.stem.replace("_", ":", 1)
                            message_count, last_message = self._get_session_info(path)
                            sessions.append({
                                "key": key,
                                "created_at": data.get("created_at"),
                                "updated_at": data.get("updated_at"),
                                "path": str(path),
                                "message_count": message_count,
                                "last_message": last_message,
                            })
            except Exception:
                continue

        return sorted(sessions, key=lambda x: x.get("updated_at", ""), reverse=True)

    @staticmethod
    def _get_session_info(path: Path) -> tuple[int, Optional[str]]:
        """获取会话信息（消息数和最后一条消息）

        Args:
            path: 会话文件路径

        Returns:
            (消息数, 最后一条消息内容)
        """
        count = 0
        last_message = None

        with open(path, encoding="utf-8") as f:
            for line in f:
                line = line.strip()
                if not line:
                    continue
                try:
                    data = json.loads(line)
                    if data.get("_type") == "metadata":
                        continue
                    # 只统计 user 和 assistant 消息
                    role = data.get("role", "")
                    if role in ("user", "assistant"):
                        count += 1
                        content = data.get("content", "")
                        if content:
                            last_message = content
                except json.JSONDecodeError:
                    continue

        return count, last_message

    @staticmethod
    def _count_messages(path: Path) -> int:
        """统计会话文件中的消息数"""
        count, _ = SessionManager._get_session_info(path)
        return count

    def delete_session(self, key: str) -> None:
        """删除会话"""
        path = self._get_session_path(key)
        if path.exists():
            path.unlink()
            logger.info(f"Session deleted: {key}")

        self.invalidate(key)

    def migrate_from_legacy(self, legacy_dir: Path) -> int:
        """
        从旧格式迁移会话

        Args:
            legacy_dir: 旧的会话目录

        Returns:
            迁移的会话数量
        """
        if not legacy_dir.exists():
            return 0

        migrated = 0

        for old_path in legacy_dir.glob("*.jsonl"):
            try:
                session = Session.load(old_path)
                if session:
                    new_path = self._get_session_path(session.key)
                    session.save(new_path)
                    old_path.unlink()
                    migrated += 1
                    logger.info(f"Migrated session: {session.key}")
            except Exception as e:
                logger.warning(f"Failed to migrate session from {old_path}: {e}")
                continue

        return migrated

    def get_config(self) -> Dict[str, Any]:
        """获取当前配置"""
        return {
            "workspace": str(self.workspace),
            "sessions_dir": str(self.sessions_dir),
            "max_history_messages": self.config.max_history_messages,
            "enable_persistence": self.config.enable_persistence,
            "enable_memory_cache": self.config.enable_memory_cache,
            "cached_sessions": len(self._cache),
        }
