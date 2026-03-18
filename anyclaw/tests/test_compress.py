"""上下文压缩测试"""

import tempfile
import json
import asyncio
from pathlib import Path
from datetime import datetime

import pytest

from anyclaw.agent.compressor import (
    ConversationCompressor,
    CompressionResult,
    get_compressor,
    reset_compressor,
)
from anyclaw.agent.sliding_window import (
    SlidingWindow,
    WindowResult,
    get_sliding_window,
    reset_sliding_window,
)
from anyclaw.agent.checkpoint import (
    CheckpointManager,
    CheckpointInfo,
    get_checkpoint_manager,
    reset_checkpoint_manager,
)


class TestConversationCompressor:
    """ConversationCompressor 测试"""

    def test_init_default(self):
        """测试默认初始化"""
        compressor = ConversationCompressor()
        assert compressor.compress_threshold == ConversationCompressor.DEFAULT_COMPRESS_THRESHOLD
        assert compressor.keep_recent == ConversationCompressor.DEFAULT_KEEP_RECENT

    def test_init_custom(self):
        """测试自定义初始化"""
        compressor = ConversationCompressor(
            compress_threshold=20,
            keep_recent=10,
        )
        assert compressor.compress_threshold == 20
        assert compressor.keep_recent == 10

    def test_needs_compression_false(self):
        """测试不需要压缩"""
        compressor = ConversationCompressor(compress_threshold=10)
        messages = [{"role": "user", "content": f"Message {i}"} for i in range(5)]

        assert compressor.needs_compression(messages) is False

    def test_needs_compression_true(self):
        """测试需要压缩"""
        compressor = ConversationCompressor(compress_threshold=10)
        messages = [{"role": "user", "content": f"Message {i}"} for i in range(15)]

        assert compressor.needs_compression(messages) is True

    def test_separate_messages(self):
        """测试分离消息"""
        compressor = ConversationCompressor(compress_threshold=10, keep_recent=5)
        messages = [{"role": "user", "content": f"Message {i}"} for i in range(15)]

        to_compress, to_keep = compressor._separate_messages(messages)

        assert len(to_compress) == 10
        assert len(to_keep) == 5

    def test_separate_messages_protects_system(self):
        """测试分离时保护系统消息"""
        compressor = ConversationCompressor(compress_threshold=10, keep_recent=3)
        messages = [
            {"role": "system", "content": "System message"},
        ] + [{"role": "user", "content": f"Message {i}"} for i in range(10)]

        to_compress, to_keep = compressor._separate_messages(messages)

        # 系统消息应在 to_keep 中
        assert any(m["role"] == "system" for m in to_keep)

    def test_truncate_strategy(self):
        """测试截断策略"""
        compressor = ConversationCompressor(compress_threshold=5, keep_recent=2)
        messages = [{"role": "user", "content": f"Message {i}"} for i in range(10)]

        result = compressor._truncate(messages)

        # 截断后应该更少
        assert len(result) < len(messages)

    def test_compress_no_need(self):
        """测试不需要压缩时的行为"""
        compressor = ConversationCompressor(compress_threshold=10)
        messages = [{"role": "user", "content": f"Message {i}"} for i in range(5)]

        result = asyncio.run(compressor.compress(messages, strategy="truncate"))

        assert result.strategy == "none"
        assert result.original_messages == result.compressed_messages

    def test_compress_with_truncate(self):
        """测试截断压缩"""
        compressor = ConversationCompressor(compress_threshold=5, keep_recent=2)
        messages = [{"role": "user", "content": f"Message {i}"} for i in range(10)]

        result = asyncio.run(compressor.compress(messages, strategy="truncate"))

        assert result.strategy == "truncate"
        assert len(result.compressed_messages) < len(messages)
        assert result.compression_ratio < 1.0

    def test_get_compression_stats(self):
        """测试获取压缩统计"""
        compressor = ConversationCompressor(compress_threshold=10, keep_recent=5)
        messages = [{"role": "user", "content": f"Message {i}"} for i in range(15)]

        stats = compressor.get_compression_stats(messages)

        assert stats["total_messages"] == 15
        assert stats["needs_compression"] is True
        assert stats["threshold"] == 10


class TestSlidingWindow:
    """SlidingWindow 测试"""

    def test_init_default(self):
        """测试默认初始化"""
        window = SlidingWindow()
        assert window.window_size == SlidingWindow.DEFAULT_WINDOW_SIZE

    def test_init_custom(self):
        """测试自定义初始化"""
        window = SlidingWindow(window_size=30)
        assert window.window_size == 30

    def test_apply_no_change(self):
        """测试不需要应用窗口"""
        window = SlidingWindow(window_size=20)
        messages = [{"role": "user", "content": f"Message {i}"} for i in range(10)]

        result = window.apply(messages)

        assert len(result.windowed_messages) == 10
        assert result.removed_count == 0

    def test_apply_with_removal(self):
        """测试应用窗口删除消息"""
        window = SlidingWindow(window_size=10)
        messages = [{"role": "user", "content": f"Message {i}"} for i in range(20)]

        result = window.apply(messages)

        assert len(result.windowed_messages) <= 10
        assert result.removed_count > 0

    def test_protect_system_messages(self):
        """测试保护系统消息"""
        window = SlidingWindow(window_size=5, protect_system=True)
        messages = [
            {"role": "system", "content": "System"},
        ] + [{"role": "user", "content": f"Message {i}"} for i in range(10)]

        result = window.apply(messages)

        # 系统消息应该在结果中
        assert any(m["role"] == "system" for m in result.windowed_messages)

    def test_set_window_size(self):
        """测试设置窗口大小"""
        window = SlidingWindow(window_size=20)
        window.set_window_size(30)

        assert window.window_size == 30

    def test_set_window_size_minimum(self):
        """测试窗口大小最小值"""
        window = SlidingWindow(window_size=20)
        window.set_window_size(0)

        assert window.window_size == 1

    def test_get_stats(self):
        """测试获取统计"""
        window = SlidingWindow(window_size=10)
        messages = [{"role": "user", "content": f"Message {i}"} for i in range(15)]

        stats = window.get_stats(messages)

        assert stats["total_messages"] == 15
        assert stats["window_size"] == 10
        assert stats["would_remove"] == 5


class TestCheckpointManager:
    """CheckpointManager 测试"""

    def test_init(self):
        """测试初始化"""
        with tempfile.TemporaryDirectory() as tmpdir:
            manager = CheckpointManager(checkpoint_dir=tmpdir)
            assert manager.checkpoint_dir.exists()

    def test_save_and_load(self):
        """测试保存和加载"""
        with tempfile.TemporaryDirectory() as tmpdir:
            manager = CheckpointManager(checkpoint_dir=tmpdir)

            messages = [
                {"role": "user", "content": "Hello"},
                {"role": "assistant", "content": "Hi!"},
            ]

            info = manager.save("test-checkpoint", messages, token_count=100)

            assert info.name == "test-checkpoint"
            assert info.message_count == 2

            # 加载
            loaded_messages, loaded_info = manager.load("test-checkpoint")

            assert len(loaded_messages) == 2
            assert loaded_info.token_count == 100

    def test_list_empty(self):
        """测试空列表"""
        with tempfile.TemporaryDirectory() as tmpdir:
            manager = CheckpointManager(checkpoint_dir=tmpdir)

            checkpoints = manager.list()

            assert len(checkpoints) == 0

    def test_list_with_checkpoints(self):
        """测试有检查点的列表"""
        with tempfile.TemporaryDirectory() as tmpdir:
            manager = CheckpointManager(checkpoint_dir=tmpdir)

            messages = [{"role": "user", "content": "Test"}]

            manager.save("checkpoint-1", messages)
            manager.save("checkpoint-2", messages)

            checkpoints = manager.list()

            assert len(checkpoints) == 2

    def test_delete(self):
        """测试删除检查点"""
        with tempfile.TemporaryDirectory() as tmpdir:
            manager = CheckpointManager(checkpoint_dir=tmpdir)

            messages = [{"role": "user", "content": "Test"}]
            manager.save("to-delete", messages)

            assert manager.exists("to-delete")

            result = manager.delete("to-delete")

            assert result is True
            assert not manager.exists("to-delete")

    def test_exists(self):
        """测试检查点存在"""
        with tempfile.TemporaryDirectory() as tmpdir:
            manager = CheckpointManager(checkpoint_dir=tmpdir)

            assert manager.exists("nonexistent") is False

            messages = [{"role": "user", "content": "Test"}]
            manager.save("existing", messages)

            assert manager.exists("existing") is True

    def test_export_to_markdown(self):
        """测试导出为 Markdown"""
        with tempfile.TemporaryDirectory() as tmpdir:
            manager = CheckpointManager(checkpoint_dir=tmpdir)

            messages = [
                {"role": "system", "content": "System message"},
                {"role": "user", "content": "User message"},
                {"role": "assistant", "content": "Assistant message"},
            ]
            manager.save("export-test", messages)

            markdown = manager.export_to_markdown("export-test")

            assert "System message" in markdown
            assert "User message" in markdown
            assert "Assistant message" in markdown

    def test_export_to_markdown_with_file(self):
        """测试导出到文件"""
        with tempfile.TemporaryDirectory() as tmpdir:
            manager = CheckpointManager(checkpoint_dir=tmpdir)

            messages = [{"role": "user", "content": "Test"}]
            manager.save("file-export", messages)

            output_path = Path(tmpdir) / "export.md"
            markdown = manager.export_to_markdown("file-export", str(output_path))

            assert output_path.exists()
            assert "Test" in output_path.read_text()

    def test_sanitize_name(self):
        """测试名称清理"""
        with tempfile.TemporaryDirectory() as tmpdir:
            manager = CheckpointManager(checkpoint_dir=tmpdir)

            # 测试特殊字符
            assert manager._sanitize_name("Test Checkpoint!") == "test_checkpoint_"
            assert manager._sanitize_name("test-123") == "test-123"
            assert manager._sanitize_name("UPPERCASE") == "uppercase"


class TestGlobalInstances:
    """全局实例测试"""

    def test_get_compressor(self):
        """测试获取全局压缩器"""
        reset_compressor()
        c1 = get_compressor()
        c2 = get_compressor()
        assert c1 is c2

    def test_reset_compressor(self):
        """测试重置压缩器"""
        c1 = get_compressor()
        reset_compressor()
        c2 = get_compressor()
        assert c1 is not c2

    def test_get_sliding_window(self):
        """测试获取全局滑动窗口"""
        reset_sliding_window()
        w1 = get_sliding_window()
        w2 = get_sliding_window()
        assert w1 is w2

    def test_reset_sliding_window(self):
        """测试重置滑动窗口"""
        w1 = get_sliding_window()
        reset_sliding_window()
        w2 = get_sliding_window()
        assert w1 is not w2

    def test_get_checkpoint_manager(self):
        """测试获取全局检查点管理器"""
        reset_checkpoint_manager()
        m1 = get_checkpoint_manager()
        m2 = get_checkpoint_manager()
        assert m1 is m2

    def test_reset_checkpoint_manager(self):
        """测试重置检查点管理器"""
        m1 = get_checkpoint_manager()
        reset_checkpoint_manager()
        m2 = get_checkpoint_manager()
        assert m1 is not m2
