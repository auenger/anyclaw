"""记忆管理器

管理长期记忆（MEMORY.md）和每日日志（memory/YYYY-MM-DD.md）。
"""

from pathlib import Path
from datetime import datetime, date, timedelta
from typing import Optional, List, Dict, Any
from dataclasses import dataclass, field
import re
import json


@dataclass
class SearchResult:
    """搜索结果"""
    source: str
    matches: List[str]


@dataclass
class DailyLog:
    """每日日志"""
    date: str
    content: str


class MemoryManager:
    """记忆管理器

    管理两种类型的记忆：
    - 长期记忆 (memory/MEMORY.md): 跨会话持久化的重要信息
    - 每日日志 (memory/YYYY-MM-DD.md): 按日期记录的会话日志
    """

    MEMORY_DIR = "memory"
    LONG_TERM_FILE = "MEMORY.md"
    HISTORY_FILE = "HISTORY.md"

    # 默认配置
    DEFAULT_MAX_CHARS = 10000
    DEFAULT_DAILY_LOAD_DAYS = 2

    def __init__(
        self,
        workspace_path: Optional[Path] = None,
        max_chars: int = DEFAULT_MAX_CHARS,
        daily_load_days: int = DEFAULT_DAILY_LOAD_DAYS,
    ):
        """初始化记忆管理器

        Args:
            workspace_path: 工作区路径
            max_chars: 单个记忆文件最大字符数
            daily_load_days: 加载最近几天的日志
        """
        self.workspace_path = workspace_path or Path.home() / ".anyclaw" / "workspace"
        self.memory_dir = self.workspace_path / self.MEMORY_DIR
        self.max_chars = max_chars
        self.daily_load_days = daily_load_days

    # ==================== 长期记忆 ====================

    def load_long_term(self) -> Optional[str]:
        """加载长期记忆

        Returns:
            长期记忆内容，如果不存在返回 None
        """
        self.memory_dir.mkdir(parents=True, exist_ok=True)
        filepath = self.memory_dir / self.LONG_TERM_FILE
        if filepath.exists():
            content = filepath.read_text(encoding="utf-8")
            # 检查大小限制
            if len(content) > self.max_chars:
                content = content[:self.max_chars] + "\n\n... (内容已截断)"
            return content
        return None

    def save_long_term(self, content: str) -> None:
        """保存长期记忆

        Args:
            content: 要保存的内容
        """
        self.memory_dir.mkdir(parents=True, exist_ok=True)
        filepath = self.memory_dir / self.LONG_TERM_FILE
        filepath.write_text(content, encoding="utf-8")

    def update_long_term(self, section: str, content: str) -> None:
        """更新长期记忆的特定部分

        Args:
            section: 要更新的部分标题
            content: 新的内容
        """
        current = self.load_long_term() or self._get_default_long_term()
        updated = self._update_section(current, section, content)
        self.save_long_term(updated)

    def _update_section(self, content: str, section: str, new_content: str) -> str:
        """更新内容的特定部分

        Args:
            content: 当前内容
            section: 部分标题
            new_content: 新内容

        Returns:
            更新后的内容
        """
        lines = content.split("\n")
        result = []
        in_section = False
        section_found = False
        section_pattern = re.compile(rf"^##\s*{re.escape(section)}", re.IGNORECASE)

        i = 0
        while i < len(lines):
            line = lines[i]

            # 检测目标部分
            if section_pattern.match(line.strip()):
                in_section = True
                section_found = True
                result.append(line)
                result.append("")
                result.append(new_content)
                result.append("")
                # 跳过原部分内容直到下一个 ## 标题
                i += 1
                while i < len(lines):
                    if lines[i].strip().startswith("## ") and not section_pattern.match(lines[i].strip()):
                        in_section = False
                        result.append(lines[i])
                        break
                    i += 1
            else:
                result.append(line)

            i += 1

        # 如果部分不存在，添加到末尾
        if not section_found:
            result.append(f"\n## {section}\n\n{new_content}\n")

        return "\n".join(result)

    def _get_default_long_term(self) -> str:
        """获取默认的长期记忆模板"""
        return """# 长期记忆

此文件存储跨会话持久化的重要信息。

## 用户信息

（关于用户的重要信息）

## 偏好

（用户偏好学习）

## 项目上下文

（正在进行的项目的相关信息）

## 重要笔记

（需要记住的事情）

---

*此文件由 AnyClaw 自动更新，当有重要信息时应被记住。*
"""

    def create_long_term(self) -> None:
        """创建默认的长期记忆文件"""
        if not self.long_term_exists():
            self.save_long_term(self._get_default_long_term())

    def long_term_exists(self) -> bool:
        """检查长期记忆是否存在"""
        return (self.memory_dir / self.LONG_TERM_FILE).exists()

    # ==================== 每日日志 ====================

    def get_today_log_path(self) -> Path:
        """获取今日日志路径

        Returns:
            今日日志文件路径
        """
        today = date.today().isoformat()
        return self.memory_dir / f"{today}.md"

    def get_log_path(self, log_date: date) -> Path:
        """获取指定日期的日志路径

        Args:
            log_date: 日期

        Returns:
            日志文件路径
        """
        return self.memory_dir / f"{log_date.isoformat()}.md"

    def load_daily(self, days: Optional[int] = None) -> List[DailyLog]:
        """加载最近 N 天的日志

        Args:
            days: 加载天数，默认使用配置值

        Returns:
            日志列表（按日期倒序）
        """
        days = days or self.daily_load_days
        logs = []

        for i in range(days):
            log_date = date.today() - timedelta(days=i)
            log_path = self.get_log_path(log_date)

            if log_path.exists():
                logs.append(DailyLog(
                    date=log_date.isoformat(),
                    content=log_path.read_text(encoding="utf-8"),
                ))

        return logs

    def append_to_today(self, entry: str) -> None:
        """追加到今日日志

        Args:
            entry: 日志条目
        """
        self.memory_dir.mkdir(parents=True, exist_ok=True)
        log_path = self.get_today_log_path()

        if not log_path.exists():
            log_path.write_text(self._get_daily_header(), encoding="utf-8")

        with open(log_path, "a", encoding="utf-8") as f:
            timestamp = datetime.now().strftime("%H:%M")
            f.write(f"\n### {timestamp}\n\n{entry}\n")

    def _get_daily_header(self) -> str:
        """获取每日日志头部"""
        today = date.today()
        weekdays = ["周一", "周二", "周三", "周四", "周五", "周六", "周日"]
        weekday = weekdays[today.weekday()]
        return f"# {today.isoformat()} ({weekday})\n\n"

    def get_today_content(self) -> Optional[str]:
        """获取今日日志内容

        Returns:
            今日日志内容，如果不存在返回 None
        """
        log_path = self.get_today_log_path()
        if log_path.exists():
            return log_path.read_text(encoding="utf-8")
        return None

    # ==================== 搜索和导出 ====================

    def search(self, keyword: str) -> List[SearchResult]:
        """搜索所有记忆

        Args:
            keyword: 搜索关键词

        Returns:
            搜索结果列表
        """
        results = []
        pattern = re.compile(re.escape(keyword), re.IGNORECASE)

        # 搜索长期记忆
        long_term = self.load_long_term()
        if long_term and pattern.search(long_term):
            results.append(SearchResult(
                source="MEMORY.md",
                matches=self._extract_matches(long_term, pattern),
            ))

        # 搜索每日日志
        if self.memory_dir.exists():
            for log_file in sorted(self.memory_dir.glob("*.md"), reverse=True):
                content = log_file.read_text(encoding="utf-8")
                if pattern.search(content):
                    results.append(SearchResult(
                        source=log_file.stem,
                        matches=self._extract_matches(content, pattern),
                    ))

        return results

    def _extract_matches(self, content: str, pattern: re.Pattern, context_chars: int = 50) -> List[str]:
        """提取匹配内容

        Args:
            content: 原始内容
            pattern: 正则模式
            context_chars: 上下文字符数

        Returns:
            匹配片段列表
        """
        matches = []
        lines = content.split("\n")

        for line in lines:
            if pattern.search(line):
                # 清理并截断
                clean_line = line.strip()
                if len(clean_line) > context_chars * 2:
                    # 找到匹配位置
                    match = pattern.search(clean_line)
                    if match:
                        start = max(0, match.start() - context_chars)
                        end = min(len(clean_line), match.end() + context_chars)
                        clean_line = "..." + clean_line[start:end] + "..."
                matches.append(clean_line)

        return matches[:10]  # 最多返回 10 个匹配

    def export(self, format: str = "markdown") -> str:
        """导出所有记忆

        Args:
            format: 导出格式 (markdown/json)

        Returns:
            导出内容
        """
        if format == "markdown":
            return self._export_markdown()
        elif format == "json":
            return self._export_json()
        raise ValueError(f"不支持的格式: {format}")

    def _export_markdown(self) -> str:
        """导出为 Markdown 格式"""
        lines = ["# AnyClaw 记忆导出\n"]
        lines.append(f"导出时间: {datetime.now().isoformat()}\n\n")

        # 长期记忆
        lines.append("## 长期记忆\n\n")
        long_term = self.load_long_term()
        if long_term:
            lines.append(long_term)
        else:
            lines.append("*(无长期记忆)*\n")

        # 每日日志
        lines.append("\n---\n\n## 每日日志\n\n")
        if self.memory_dir.exists():
            for log_file in sorted(self.memory_dir.glob("*.md"), reverse=True):
                lines.append(f"### {log_file.stem}\n\n")
                lines.append(log_file.read_text(encoding="utf-8"))
                lines.append("\n\n")

        return "".join(lines)

    def _export_json(self) -> str:
        """导出为 JSON 格式"""
        data = {
            "exported_at": datetime.now().isoformat(),
            "long_term": self.load_long_term(),
            "daily_logs": [],
        }

        if self.memory_dir.exists():
            for log_file in sorted(self.memory_dir.glob("*.md"), reverse=True):
                data["daily_logs"].append({
                    "date": log_file.stem,
                    "content": log_file.read_text(encoding="utf-8"),
                })

        return json.dumps(data, ensure_ascii=False, indent=2)

    def clean_old_logs(self, days_to_keep: int = 30) -> int:
        """清理旧日志

        Args:
            days_to_keep: 保留天数

        Returns:
            删除的文件数
        """
        if not self.memory_dir.exists():
            return 0

        deleted = 0
        cutoff = date.today() - timedelta(days=days_to_keep)

        for log_file in self.memory_dir.glob("*.md"):
            try:
                file_date = date.fromisoformat(log_file.stem)
                if file_date < cutoff:
                    log_file.unlink()
                    deleted += 1
            except ValueError:
                # 文件名不是有效日期，跳过
                pass

        return deleted

    def get_stats(self) -> Dict[str, Any]:
        """获取记忆统计信息

        Returns:
            统计信息字典
        """
        stats = {
            "long_term_exists": self.long_term_exists(),
            "long_term_chars": 0,
            "daily_logs_count": 0,
            "oldest_log": None,
            "newest_log": None,
        }

        # 长期记忆统计
        if self.long_term_exists():
            content = self.load_long_term()
            if content:
                stats["long_term_chars"] = len(content)

        # 每日日志统计
        if self.memory_dir.exists():
            log_files = sorted(self.memory_dir.glob("*.md"))
            stats["daily_logs_count"] = len(log_files)

            if log_files:
                stats["oldest_log"] = log_files[0].stem
                stats["newest_log"] = log_files[-1].stem

        return stats


# 全局实例
_memory_manager: Optional[MemoryManager] = None


def get_memory_manager(
    workspace_path: Optional[Path] = None,
    max_chars: Optional[int] = None,
    daily_load_days: Optional[int] = None,
) -> MemoryManager:
    """获取全局记忆管理器实例

    Args:
        workspace_path: 工作区路径
        max_chars: 最大字符数
        daily_load_days: 加载天数

    Returns:
        MemoryManager 实例
    """
    global _memory_manager

    if _memory_manager is None:
        _memory_manager = MemoryManager(
            workspace_path=workspace_path,
            max_chars=max_chars or MemoryManager.DEFAULT_MAX_CHARS,
            daily_load_days=daily_load_days or MemoryManager.DEFAULT_DAILY_LOAD_DAYS,
        )

    return _memory_manager


def reset_memory_manager() -> None:
    """重置全局记忆管理器"""
    global _memory_manager
    _memory_manager = None
