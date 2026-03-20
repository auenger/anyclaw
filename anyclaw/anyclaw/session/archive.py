"""Session Archive Manager

会话归档管理器，支持：
- 按项目隔离（Git root 或 cwd）
- 按日期归档
- 完整的记录类型支持
- JSONL 追加写入
"""

import json
import logging
import uuid
from dataclasses import dataclass, field
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional

from .records import (
    SessionRecord,
    SessionStart,
    SessionEnd,
    UserMessage,
    AssistantMessage,
    ToolCall,
    ToolResult,
    SkillCall,
    SkillResult,
    Thinking,
    ErrorRecord,
    parse_record,
)
from .project import (
    find_git_root,
    get_git_branch,
    get_project_identifier,
    make_safe_dirname,
)


logger = logging.getLogger(__name__)

# 默认归档基础目录
DEFAULT_ARCHIVE_BASE = Path.home() / ".anyclaw" / "sessions"


@dataclass
class ArchiveConfig:
    """归档配置"""
    base_dir: Path = field(default_factory=lambda: DEFAULT_ARCHIVE_BASE)
    enable_archive: bool = True
    retention_days: int = 30  # 会话保留天数


class SessionArchiveManager:
    """
    会话归档管理器

    目录结构：
    ~/.anyclaw/sessions/
    ├── cli/
    │   ├── -Users-ryan-mycode-AnyClaw/        # Git 项目
    │   │   ├── project.json                   # 项目元信息
    │   │   ├── 2026-03-19/
    │   │   │   ├── {session-uuid}.jsonl       # 会话文件
    │   │   │   └── index.json                 # 日期索引
    │   │   └── 2026-03-18/
    │   └── -tmp-test/                         # 非 Git 项目
    ├── channels/
    │   ├── feishu/
    │   │   └── {chat-id}/
    │   │       └── 2026-03-19/
    │   └── discord/
    │       └── {channel-id}/
    └── index.db                               # SQLite 索引（可选）
    """

    def __init__(self, config: Optional[ArchiveConfig] = None):
        self.config = config or ArchiveConfig()
        self.base_dir = Path(self.config.base_dir)

        # 当前会话状态
        self.current_session_id: Optional[str] = None
        self.current_project_id: Optional[str] = None
        self.session_start_time: Optional[datetime] = None
        self._message_count: int = 0
        self._tool_call_count: int = 0
        self._skill_call_count: int = 0
        self._last_message_uuid: Optional[str] = None

        # 确保基础目录存在
        if self.config.enable_archive:
            self.base_dir.mkdir(parents=True, exist_ok=True)

        logger.debug(f"SessionArchiveManager initialized: {self.base_dir}")

    def start_session(
        self,
        cwd: Path,
        channel: str = "cli",
        channel_id: Optional[str] = None,
        version: str = "",
    ) -> str:
        """
        开始新会话

        Args:
            cwd: 当前工作目录
            channel: 渠道类型（cli/feishu/discord）
            channel_id: 渠道 ID（非 CLI 渠道需要）
            version: AnyClaw 版本

        Returns:
            会话 ID
        """
        if not self.config.enable_archive:
            return ""

        # 生成会话 ID
        self.current_session_id = str(uuid.uuid4())
        self.session_start_time = datetime.now()
        self._message_count = 0
        self._tool_call_count = 0
        self._skill_call_count = 0
        self._last_message_uuid = None

        # 确定项目标识
        if channel == "cli":
            self.current_project_id = get_project_identifier(cwd)
        else:
            self.current_project_id = f"{channel}_{channel_id}"

        # 写入 session_start
        start_record = SessionStart(
            session_id=self.current_session_id,
            project_id=self.current_project_id,
            cwd=str(cwd),
            git_branch=get_git_branch(cwd),
            channel=channel,
            version=version,
        )
        self._append_record(start_record)

        logger.info(f"Session started: {self.current_session_id} (project: {self.current_project_id})")
        return self.current_session_id

    def end_session(self) -> None:
        """结束当前会话"""
        if not self.current_session_id or not self.config.enable_archive:
            return

        duration = (datetime.now() - self.session_start_time).total_seconds()
        end_record = SessionEnd(
            session_id=self.current_session_id,
            message_count=self._message_count,
            tool_call_count=self._tool_call_count,
            skill_call_count=self._skill_call_count,
            duration_seconds=duration,
        )
        self._append_record(end_record)

        logger.info(
            f"Session ended: {self.current_session_id} "
            f"({self._message_count} messages, {self._tool_call_count} tools, "
            f"{duration:.1f}s)"
        )

    def record_user_message(
        self,
        content: str,
        media: Optional[List[str]] = None,
        images: Optional[List[Dict]] = None,
    ) -> str:
        """
        记录用户消息

        Args:
            content: 消息内容
            media: 媒体文件路径列表
            images: 图片数据列表

        Returns:
            消息 UUID
        """
        if not self.current_session_id or not self.config.enable_archive:
            return ""

        record = UserMessage(
            parent_uuid=self._last_message_uuid,
            content=content,
            media=media or [],
            images=images or [],
        )
        self._append_record(record)
        self._message_count += 1
        self._last_message_uuid = record.uuid
        return record.uuid

    def record_assistant_message(
        self,
        content: str,
        model: Optional[str] = None,
        stop_reason: Optional[str] = None,
    ) -> str:
        """
        记录助手消息

        Args:
            content: 响应内容
            model: 使用的模型
            stop_reason: 停止原因

        Returns:
            消息 UUID
        """
        if not self.current_session_id or not self.config.enable_archive:
            return ""

        record = AssistantMessage(
            parent_uuid=self._last_message_uuid,
            content=content,
            model=model,
            stop_reason=stop_reason,
        )
        self._append_record(record)
        self._message_count += 1
        self._last_message_uuid = record.uuid
        return record.uuid

    def record_tool_call(
        self,
        tool_name: str,
        tool_input: Dict[str, Any],
    ) -> str:
        """
        记录工具调用

        Args:
            tool_name: 工具名称
            tool_input: 工具输入

        Returns:
            工具调用 ID
        """
        if not self.current_session_id or not self.config.enable_archive:
            return ""

        call_id = f"call_{uuid.uuid4().hex[:8]}"
        record = ToolCall(
            parent_uuid=self._last_message_uuid,
            tool_call_id=call_id,
            tool_name=tool_name,
            tool_input=tool_input,
        )
        self._append_record(record)
        self._tool_call_count += 1
        return call_id

    def record_tool_result(
        self,
        tool_call_id: str,
        output: str,
        duration_ms: int = 0,
        success: bool = True,
    ) -> None:
        """
        记录工具结果

        Args:
            tool_call_id: 工具调用 ID
            output: 工具输出
            duration_ms: 执行耗时（毫秒）
            success: 是否成功
        """
        if not self.current_session_id or not self.config.enable_archive:
            return

        record = ToolResult(
            tool_call_id=tool_call_id,
            output=output,
            duration_ms=duration_ms,
            success=success,
        )
        self._append_record(record)

    def record_skill_call(
        self,
        skill_name: str,
        skill_args: str = "",
    ) -> str:
        """
        记录技能调用

        Args:
            skill_name: 技能名称
            skill_args: 技能参数

        Returns:
            技能调用 ID
        """
        if not self.current_session_id or not self.config.enable_archive:
            return ""

        call_id = f"skill_{uuid.uuid4().hex[:8]}"
        record = SkillCall(
            parent_uuid=self._last_message_uuid,
            skill_call_id=call_id,
            skill_name=skill_name,
            skill_args=skill_args,
        )
        self._append_record(record)
        self._skill_call_count += 1
        return call_id

    def record_skill_result(
        self,
        skill_call_id: str,
        output: str,
        success: bool = True,
    ) -> None:
        """
        记录技能结果

        Args:
            skill_call_id: 技能调用 ID
            output: 技能输出
            success: 是否成功
        """
        if not self.current_session_id or not self.config.enable_archive:
            return

        record = SkillResult(
            skill_call_id=skill_call_id,
            output=output,
            success=success,
        )
        self._append_record(record)

    def record_thinking(self, content: str) -> str:
        """
        记录思考过程

        Args:
            content: 思考内容

        Returns:
            记录 UUID
        """
        if not self.current_session_id or not self.config.enable_archive:
            return ""

        record = Thinking(
            parent_uuid=self._last_message_uuid,
            content=content,
        )
        self._append_record(record)
        return record.uuid

    def record_error(
        self,
        error_type: str,
        message: str,
        traceback: Optional[str] = None,
    ) -> str:
        """
        记录错误

        Args:
            error_type: 错误类型
            message: 错误消息
            traceback: 堆栈追踪

        Returns:
            记录 UUID
        """
        if not self.current_session_id or not self.config.enable_archive:
            return ""

        record = ErrorRecord(
            parent_uuid=self._last_message_uuid,
            error_type=error_type,
            message=message,
            traceback=traceback,
        )
        self._append_record(record)
        return record.uuid

    def _get_session_file_path(self) -> Path:
        """获取当前会话文件路径"""
        date_dir = datetime.now().strftime("%Y-%m-%d")

        # 检查是否是 Channel 类型
        if self.current_project_id.startswith("feishu_") or \
           self.current_project_id.startswith("discord_"):
            # Channel 类型：channels/{channel_type}/{channel_id}/{date}/
            parts = self.current_project_id.split("_", 1)
            channel_type = parts[0]
            channel_id = parts[1] if len(parts) > 1 else "unknown"
            return (
                self.base_dir / "channels" / channel_type / channel_id /
                date_dir / f"{self.current_session_id}.jsonl"
            )
        else:
            # CLI 类型：cli/{project_id}/{date}/
            return (
                self.base_dir / "cli" / self.current_project_id /
                date_dir / f"{self.current_session_id}.jsonl"
            )

    def _append_record(self, record: SessionRecord) -> None:
        """追加记录到会话文件"""
        file_path = self._get_session_file_path()
        file_path.parent.mkdir(parents=True, exist_ok=True)

        with open(file_path, "a", encoding="utf-8") as f:
            f.write(record.to_json() + "\n")

        logger.debug(f"Record appended: {record.type} to {file_path}")

    # ==================== 查询方法 ====================

    def list_sessions(
        self,
        date: Optional[str] = None,
        project: Optional[str] = None,
        channel: Optional[str] = None,
        limit: int = 50,
    ) -> List[Dict[str, Any]]:
        """
        列出会话

        Args:
            date: 日期过滤 (YYYY-MM-DD)
            project: 项目 ID 过滤
            channel: 渠道过滤
            limit: 最大返回数量

        Returns:
            会话信息列表
        """
        sessions = []

        # 确定搜索目录
        if channel and channel != "cli":
            search_dirs = [self.base_dir / "channels" / channel]
        elif project:
            search_dirs = [self.base_dir / "cli" / project]
        else:
            search_dirs = [self.base_dir / "cli", self.base_dir / "channels"]

        for search_dir in search_dirs:
            if not search_dir.exists():
                continue

            # 递归查找所有 .jsonl 文件
            pattern = f"**/{date}/*.jsonl" if date else "**/*.jsonl"
            for path in search_dir.glob(pattern):
                try:
                    session_info = self._read_session_info(path)
                    if session_info:
                        sessions.append(session_info)
                except Exception as e:
                    logger.debug(f"Failed to read session {path}: {e}")
                    continue

        # 按时间排序
        sessions.sort(key=lambda x: x.get("started_at", ""), reverse=True)
        return sessions[:limit]

    def get_session(self, session_id: str) -> Optional[Dict[str, Any]]:
        """
        获取会话详情

        Args:
            session_id: 会话 ID

        Returns:
            会话详情（包含所有记录）
        """
        # 查找会话文件
        for path in self.base_dir.glob(f"**/{session_id}.jsonl"):
            return self._read_session_detail(path)

        return None

    def search_sessions(
        self,
        query: str,
        tool: Optional[str] = None,
        limit: int = 20,
    ) -> List[Dict[str, Any]]:
        """
        搜索会话内容

        Args:
            query: 搜索关键词
            tool: 按工具名称过滤
            limit: 最大返回数量

        Returns:
            匹配的会话片段列表
        """
        results = []
        query_lower = query.lower()

        for path in self.base_dir.glob("**/*.jsonl"):
            try:
                matches = self._search_in_file(path, query_lower, tool)
                results.extend(matches)
            except Exception as e:
                logger.debug(f"Failed to search in {path}: {e}")
                continue

        results.sort(key=lambda x: x.get("timestamp", ""), reverse=True)
        return results[:limit]

    def export_session(
        self,
        session_id: str,
        format: str = "markdown",
        output_path: Optional[Path] = None,
    ) -> Optional[str]:
        """
        导出会话

        Args:
            session_id: 会话 ID
            format: 导出格式 (markdown/json)
            output_path: 输出文件路径（可选）

        Returns:
            导出内容（如果未指定输出路径）
        """
        session = self.get_session(session_id)
        if not session:
            return None

        if format == "json":
            content = json.dumps(session, ensure_ascii=False, indent=2)
        else:
            content = self._format_as_markdown(session)

        if output_path:
            output_path = Path(output_path)
            output_path.parent.mkdir(parents=True, exist_ok=True)
            output_path.write_text(content, encoding="utf-8")
            logger.info(f"Session exported to: {output_path}")
            return None

        return content

    def clean_old_sessions(
        self,
        days: int = 30,
        dry_run: bool = False,
    ) -> List[str]:
        """
        清理旧会话

        Args:
            days: 保留天数
            dry_run: 仅显示将删除的内容

        Returns:
            被删除（或将要删除）的会话文件列表
        """
        from datetime import timedelta

        cutoff = datetime.now() - timedelta(days=days)
        deleted = []

        for path in self.base_dir.glob("**/*.jsonl"):
            try:
                # 检查文件修改时间
                mtime = datetime.fromtimestamp(path.stat().st_mtime)
                if mtime < cutoff:
                    if dry_run:
                        deleted.append(str(path))
                    else:
                        path.unlink()
                        deleted.append(str(path))
                        logger.info(f"Deleted old session: {path}")
            except Exception as e:
                logger.debug(f"Failed to check/delete {path}: {e}")
                continue

        # 清理空目录
        if not dry_run:
            self._clean_empty_dirs()

        return deleted

    # ==================== 内部方法 ====================

    def _read_session_info(self, path: Path) -> Optional[Dict[str, Any]]:
        """读取会话基本信息"""
        with open(path, encoding="utf-8") as f:
            first_line = f.readline().strip()
            if not first_line:
                return None

            data = json.loads(first_line)
            if data.get("type") != "session_start":
                return None

            return {
                "session_id": data.get("session_id"),
                "project_id": data.get("project_id"),
                "channel": data.get("channel", "cli"),
                "cwd": data.get("cwd"),
                "git_branch": data.get("git_branch"),
                "started_at": data.get("timestamp"),
                "path": str(path),
            }

    def _read_session_detail(self, path: Path) -> Optional[Dict[str, Any]]:
        """读取会话详情"""
        records = []
        session_info = None

        with open(path, encoding="utf-8") as f:
            for line in f:
                line = line.strip()
                if not line:
                    continue

                try:
                    data = json.loads(line)
                    record = parse_record(data)
                    if record:
                        if record.type == "session_start":
                            session_info = {
                                "session_id": record.session_id,
                                "project_id": record.project_id,
                                "channel": record.channel,
                                "cwd": record.cwd,
                                "git_branch": record.git_branch,
                                "started_at": record.timestamp,
                            }
                        elif record.type == "session_end":
                            session_info["ended_at"] = record.timestamp
                            session_info["message_count"] = record.message_count
                            session_info["tool_call_count"] = record.tool_call_count
                            session_info["duration_seconds"] = record.duration_seconds
                        else:
                            records.append(record.to_dict())
                except json.JSONDecodeError:
                    continue

        if session_info:
            session_info["records"] = records
            session_info["path"] = str(path)
            return session_info

        return None

    def _search_in_file(
        self,
        path: Path,
        query: str,
        tool: Optional[str] = None,
    ) -> List[Dict[str, Any]]:
        """在会话文件中搜索"""
        matches = []

        with open(path, encoding="utf-8") as f:
            for line in f:
                line = line.strip()
                if not line:
                    continue

                try:
                    data = json.loads(line)
                    record_type = data.get("type", "")

                    # 工具过滤
                    if tool and record_type == "tool_call":
                        if data.get("tool_name") != tool:
                            continue

                    # 内容搜索
                    content = json.dumps(data, ensure_ascii=False).lower()
                    if query in content:
                        matches.append({
                            "session_id": path.stem,
                            "path": str(path),
                            "type": record_type,
                            "timestamp": data.get("timestamp"),
                            "content": data,
                        })
                except json.JSONDecodeError:
                    continue

        return matches

    def _format_as_markdown(self, session: Dict[str, Any]) -> str:
        """格式化会话为 Markdown"""
        lines = [
            f"# Session: {session.get('session_id', 'unknown')}",
            "",
            f"**Channel**: {session.get('channel', 'cli')}",
            f"**Project**: {session.get('project_id', 'unknown')}",
            f"**Started**: {session.get('started_at', 'unknown')}",
            f"**CWD**: {session.get('cwd', 'unknown')}",
        ]

        if session.get("git_branch"):
            lines.append(f"**Branch**: {session['git_branch']}")

        lines.append("")
        lines.append("---")
        lines.append("")

        for record in session.get("records", []):
            record_type = record.get("type", "")

            if record_type == "user_message":
                lines.append(f"## User")
                lines.append(f"{record.get('content', '')}")
                lines.append("")

            elif record_type == "assistant_message":
                lines.append(f"## Assistant")
                if record.get("model"):
                    lines.append(f"_Model: {record['model']}_")
                lines.append(f"{record.get('content', '')}")
                lines.append("")

            elif record_type == "tool_call":
                lines.append(f"### Tool Call: {record.get('tool_name', 'unknown')}")
                lines.append(f"```json")
                lines.append(json.dumps(record.get("tool_input", {}), indent=2))
                lines.append(f"```")
                lines.append("")

            elif record_type == "tool_result":
                status = "✓" if record.get("success") else "✗"
                lines.append(f"### Tool Result [{status}] ({record.get('duration_ms', 0)}ms)")
                lines.append(f"```")
                lines.append(record.get("output", "")[:500])  # 截断
                lines.append(f"```")
                lines.append("")

            elif record_type == "skill_call":
                lines.append(f"### Skill: {record.get('skill_name', 'unknown')}")
                lines.append(f"Args: {record.get('skill_args', '')}")
                lines.append("")

            elif record_type == "skill_result":
                status = "✓" if record.get("success") else "✗"
                lines.append(f"### Skill Result [{status}]")
                lines.append(f"{record.get('output', '')[:500]}")
                lines.append("")

            elif record_type == "error":
                lines.append(f"### Error: {record.get('error_type', 'unknown')}")
                lines.append(f"{record.get('message', '')}")
                lines.append("")

        return "\n".join(lines)

    def _clean_empty_dirs(self) -> None:
        """清理空目录"""
        for path in sorted(self.base_dir.rglob("*"), reverse=True):
            if path.is_dir() and not any(path.iterdir()):
                try:
                    path.rmdir()
                    logger.debug(f"Removed empty directory: {path}")
                except OSError:
                    pass
