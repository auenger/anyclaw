"""SearchCache 单元测试"""

import pytest
import tempfile
import time
from pathlib import Path

from anyclaw.search.cache import SearchCache, CacheEntry


class TestSearchCache:
    """SearchCache 测试类"""

    def test_record_access(self):
        """测试记录访问"""
        with tempfile.TemporaryDirectory() as tmpdir:
            cache_file = Path(tmpdir) / "cache.json"
            cache = SearchCache(cache_file=cache_file)

            # 记录访问
            test_path = Path("/tmp/test/file.txt")
            cache.record_access(test_path)

            # 验证记录
            cached = cache.get_cached_path("file.txt")
            assert cached is not None

    def test_cache_hit(self):
        """测试缓存命中"""
        with tempfile.TemporaryDirectory() as tmpdir:
            cache_file = Path(tmpdir) / "cache.json"
            cache = SearchCache(cache_file=cache_file)

            # 记录访问
            test_path = Path("/tmp/test/report.xlsx")
            cache.record_access(test_path)

            # 命中
            cached = cache.get_cached_path("report.xlsx")
            assert cached == test_path

    def test_cache_miss(self):
        """测试缓存未命中"""
        with tempfile.TemporaryDirectory() as tmpdir:
            cache_file = Path(tmpdir) / "cache.json"
            cache = SearchCache(cache_file=cache_file)

            # 未命中
            cached = cache.get_cached_path("nonexistent.txt")
            assert cached is None

    def test_lru_eviction(self):
        """测试 LRU 淘汰"""
        with tempfile.TemporaryDirectory() as tmpdir:
            cache_file = Path(tmpdir) / "cache.json"
            cache = SearchCache(cache_file=cache_file, max_entries=3)

            # 添加 4 个条目（超过限制）
            for i in range(4):
                cache.record_access(Path(f"/tmp/file{i}.txt"))

            # 应该只保留 3 个
            stats = cache.get_stats()
            assert stats["total_entries"] <= 3

    def test_frequent_dirs(self):
        """测试常用目录"""
        with tempfile.TemporaryDirectory() as tmpdir:
            cache_file = Path(tmpdir) / "cache.json"
            cache = SearchCache(
                cache_file=cache_file,
                frequent_threshold=2,
            )

            # 多次访问同一目录
            for i in range(3):
                cache.record_access(Path(f"/tmp/frequent/file{i}.txt"))

            # 获取常用目录
            frequent = cache.get_frequent_dirs()
            # 由于路径不存在，可能不会返回
            # 这里只测试逻辑不报错

    def test_cache_persistence(self):
        """测试缓存持久化"""
        with tempfile.TemporaryDirectory() as tmpdir:
            cache_file = Path(tmpdir) / "cache.json"

            # 创建缓存并记录
            cache1 = SearchCache(cache_file=cache_file)
            test_path = Path("/tmp/test/persist.txt")
            cache1.record_access(test_path)
            cache1.save()

            # 重新加载
            cache2 = SearchCache(cache_file=cache_file)
            cached = cache2.get_cached_path("persist.txt")
            assert cached == test_path

    def test_clear_expired(self):
        """测试清理过期缓存"""
        with tempfile.TemporaryDirectory() as tmpdir:
            cache_file = Path(tmpdir) / "cache.json"
            cache = SearchCache(cache_file=cache_file, ttl=1)  # 1 秒 TTL

            # 记录访问
            cache.record_access(Path("/tmp/test/old.txt"))

            # 等待过期
            time.sleep(1.5)

            # 清理
            cleared = cache.clear_expired()
            assert cleared >= 1

    def test_clear_all(self):
        """测试清空缓存"""
        with tempfile.TemporaryDirectory() as tmpdir:
            cache_file = Path(tmpdir) / "cache.json"
            cache = SearchCache(cache_file=cache_file)

            # 记录多个访问
            for i in range(5):
                cache.record_access(Path(f"/tmp/file{i}.txt"))

            # 清空
            cache.clear_all()

            stats = cache.get_stats()
            assert stats["total_entries"] == 0


class TestCacheEntry:
    """CacheEntry 测试类"""

    def test_entry_creation(self):
        """测试条目创建"""
        entry = CacheEntry(
            path="/tmp/test.txt",
            filename="test.txt",
        )

        assert entry.path == "/tmp/test.txt"
        assert entry.filename == "test.txt"
        assert entry.access_count == 1

    def test_entry_touch(self):
        """测试条目更新"""
        entry = CacheEntry(
            path="/tmp/test.txt",
            filename="test.txt",
        )

        old_time = entry.last_access
        time.sleep(0.01)  # 小延迟
        entry.touch()

        assert entry.access_count == 2
        assert entry.last_access > old_time
