"""搜索缓存管理器

缓存最近访问的文件和常用目录，避免重复搜索。
"""

import json
import threading
import time
from collections import OrderedDict
from dataclasses import dataclass, field, asdict
from pathlib import Path
from typing import Dict, List, Optional, Set


@dataclass
class CacheEntry:
    """缓存条目"""
    path: str
    filename: str
    access_count: int = 1
    last_access: float = field(default_factory=time.time)
    first_access: float = field(default_factory=time.time)

    def touch(self) -> None:
        """更新访问时间和计数"""
        self.access_count += 1
        self.last_access = time.time()


class SearchCache:
    """搜索缓存管理器

    使用 LRU 策略管理最近访问的文件，并跟踪常用目录。

    Usage:
        cache = SearchCache()

        # 记录访问
        cache.record_access(Path("/Users/ryan/Downloads/report.xlsx"))

        # 查询缓存
        cached = cache.get_cached_path("report.xlsx")

        # 获取常用目录
        frequent_dirs = cache.get_frequent_dirs()
    """

    DEFAULT_CACHE_FILE = "~/.anyclaw/cache/search.json"
    DEFAULT_MAX_ENTRIES = 100
    DEFAULT_TTL = 24 * 60 * 60  # 24 小时（秒）
    DEFAULT_FREQUENT_THRESHOLD = 3  # 访问超过 3 次视为常用

    def __init__(
        self,
        cache_file: Optional[Path] = None,
        max_entries: int = DEFAULT_MAX_ENTRIES,
        ttl: int = DEFAULT_TTL,
        frequent_threshold: int = DEFAULT_FREQUENT_THRESHOLD,
    ):
        """初始化搜索缓存

        Args:
            cache_file: 缓存文件路径
            max_entries: 最大缓存条目数
            ttl: 缓存过期时间（秒）
            frequent_threshold: 常用目录访问阈值
        """
        self.cache_file = Path(cache_file or self.DEFAULT_CACHE_FILE).expanduser()
        self.max_entries = max_entries
        self.ttl = ttl
        self.frequent_threshold = frequent_threshold

        # LRU 缓存（OrderedDict 实现）
        self._file_cache: OrderedDict[str, CacheEntry] = OrderedDict()

        # 常用目录缓存（目录路径 -> 访问次数）
        self._dir_access: Dict[str, int] = {}

        # 线程锁
        self._lock = threading.Lock()

        # 启动时加载缓存
        self._load_cache()

    def record_access(self, path: Path) -> None:
        """记录文件访问

        Args:
            path: 访问的文件路径
        """
        with self._lock:
            path_str = str(path)
            filename = path.name

            # 更新或创建缓存条目
            if path_str in self._file_cache:
                # 移动到末尾（最近使用）
                self._file_cache.move_to_end(path_str)
                self._file_cache[path_str].touch()
            else:
                # 创建新条目
                self._file_cache[path_str] = CacheEntry(
                    path=path_str,
                    filename=filename,
                )

            # 更新目录访问计数
            dir_path = str(path.parent)
            self._dir_access[dir_path] = self._dir_access.get(dir_path, 0) + 1

            # 检查 LRU 淘汰
            self._evict_if_needed()

    def get_cached_path(self, filename: str) -> Optional[Path]:
        """从缓存中查找文件路径

        Args:
            filename: 文件名

        Returns:
            缓存的路径，如果未找到返回 None
        """
        with self._lock:
            # 查找匹配的缓存条目
            for path_str, entry in reversed(self._file_cache.items()):
                if entry.filename == filename:
                    # 检查是否过期
                    if not self._is_expired(entry):
                        # 更新访问
                        self._file_cache.move_to_end(path_str)
                        entry.touch()
                        return Path(path_str)

            return None

    def get_frequent_dirs(self) -> List[Path]:
        """获取常用目录列表

        Returns:
            常用目录路径列表（按访问次数排序）
        """
        with self._lock:
            # 过滤并排序
            frequent = [
                (dir_path, count)
                for dir_path, count in self._dir_access.items()
                if count >= self.frequent_threshold
            ]

            # 按访问次数降序排序
            frequent.sort(key=lambda x: -x[1])

            # 转换为 Path 并过滤不存在的目录
            result = []
            for dir_path, _ in frequent:
                path = Path(dir_path)
                if path.exists():
                    result.append(path)

            return result

    def clear_expired(self) -> int:
        """清理过期缓存条目

        Returns:
            清理的条目数
        """
        with self._lock:
            expired_keys = []

            for path_str, entry in self._file_cache.items():
                if self._is_expired(entry):
                    expired_keys.append(path_str)

            for key in expired_keys:
                del self._file_cache[key]

            return len(expired_keys)

    def clear_all(self) -> None:
        """清空所有缓存"""
        with self._lock:
            self._file_cache.clear()
            self._dir_access.clear()

    def save(self) -> None:
        """保存缓存到文件"""
        with self._lock:
            self._save_cache()

    def get_stats(self) -> Dict:
        """获取缓存统计信息

        Returns:
            缓存统计字典
        """
        with self._lock:
            total_entries = len(self._file_cache)
            total_dirs = len(self._dir_access)
            frequent_dirs = len(self.get_frequent_dirs())

            return {
                "total_entries": total_entries,
                "max_entries": self.max_entries,
                "total_dirs": total_dirs,
                "frequent_dirs": frequent_dirs,
                "ttl_hours": self.ttl / 3600,
            }

    def _is_expired(self, entry: CacheEntry) -> bool:
        """检查缓存条目是否过期

        Args:
            entry: 缓存条目

        Returns:
            是否过期
        """
        return (time.time() - entry.last_access) > self.ttl

    def _evict_if_needed(self) -> None:
        """如果超过最大条目数，执行 LRU 淘汰"""
        while len(self._file_cache) > self.max_entries:
            # 删除最旧的条目（OrderedDict 的第一个）
            self._file_cache.popitem(last=False)

    def _load_cache(self) -> None:
        """从文件加载缓存"""
        try:
            if self.cache_file.exists():
                with open(self.cache_file, "r", encoding="utf-8") as f:
                    data = json.load(f)

                # 加载文件缓存
                for path_str, entry_data in data.get("files", {}).items():
                    entry = CacheEntry(
                        path=path_str,
                        filename=entry_data.get("filename", Path(path_str).name),
                        access_count=entry_data.get("access_count", 1),
                        last_access=entry_data.get("last_access", time.time()),
                        first_access=entry_data.get("first_access", time.time()),
                    )
                    # 跳过过期条目
                    if not self._is_expired(entry):
                        self._file_cache[path_str] = entry

                # 加载目录访问计数
                self._dir_access = data.get("dirs", {})

        except (OSError, json.JSONDecodeError):
            # 加载失败，使用空缓存
            pass

    def _save_cache(self) -> None:
        """保存缓存到文件"""
        try:
            # 确保目录存在
            self.cache_file.parent.mkdir(parents=True, exist_ok=True)

            # 序列化缓存数据
            files_data = {}
            for path_str, entry in self._file_cache.items():
                files_data[path_str] = {
                    "filename": entry.filename,
                    "access_count": entry.access_count,
                    "last_access": entry.last_access,
                    "first_access": entry.first_access,
                }

            data = {
                "files": files_data,
                "dirs": self._dir_access,
                "saved_at": time.time(),
            }

            # 写入文件
            with open(self.cache_file, "w", encoding="utf-8") as f:
                json.dump(data, f, indent=2, ensure_ascii=False)

        except OSError:
            # 保存失败，忽略
            pass

    def __del__(self) -> None:
        """析构时保存缓存"""
        try:
            self.save()
        except Exception:
            pass
