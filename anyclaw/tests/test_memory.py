"""记忆系统测试"""

import tempfile
import json
from pathlib import Path
from datetime import date, timedelta

import pytest

from anyclaw.memory.manager import (
    MemoryManager,
    SearchResult,
    DailyLog,
    get_memory_manager,
    reset_memory_manager,
)
from anyclaw.memory.automation import (
    MemoryAutomation,
    MemorySuggestion,
    get_memory_automation,
    reset_memory_automation,
)


class TestMemoryManager:
    """MemoryManager 测试"""

    def test_init_default(self):
        """测试默认初始化"""
        manager = MemoryManager()
        assert manager.max_chars == MemoryManager.DEFAULT_MAX_CHARS
        assert manager.daily_load_days == MemoryManager.DEFAULT_DAILY_LOAD_DAYS

    def test_init_custom(self):
        """测试自定义初始化"""
        with tempfile.TemporaryDirectory() as tmpdir:
            manager = MemoryManager(
                workspace_path=Path(tmpdir),
                max_chars=5000,
                daily_load_days=5,
            )
            assert manager.max_chars == 5000
            assert manager.daily_load_days == 5

    def test_long_term_not_exists(self):
        """测试长期记忆不存在"""
        with tempfile.TemporaryDirectory() as tmpdir:
            manager = MemoryManager(workspace_path=Path(tmpdir))
            assert manager.load_long_term() is None
            assert not manager.long_term_exists()

    def test_save_and_load_long_term(self):
        """测试保存和加载长期记忆"""
        with tempfile.TemporaryDirectory() as tmpdir:
            manager = MemoryManager(workspace_path=Path(tmpdir))

            content = "# 长期记忆\n\n测试内容"
            manager.save_long_term(content)

            assert manager.long_term_exists()
            loaded = manager.load_long_term()
            assert loaded == content

    def test_create_long_term(self):
        """测试创建默认长期记忆"""
        with tempfile.TemporaryDirectory() as tmpdir:
            manager = MemoryManager(workspace_path=Path(tmpdir))

            manager.create_long_term()

            assert manager.long_term_exists()
            content = manager.load_long_term()
            assert "长期记忆" in content
            assert "用户信息" in content

    def test_update_long_term_section(self):
        """测试更新长期记忆特定部分"""
        with tempfile.TemporaryDirectory() as tmpdir:
            manager = MemoryManager(workspace_path=Path(tmpdir))

            manager.create_long_term()
            manager.update_long_term("偏好", "测试偏好内容")

            content = manager.load_long_term()
            assert "测试偏好内容" in content

    def test_long_term_truncation(self):
        """测试长期记忆截断"""
        with tempfile.TemporaryDirectory() as tmpdir:
            manager = MemoryManager(
                workspace_path=Path(tmpdir),
                max_chars=100,
            )

            # 创建超长内容
            long_content = "x" * 200
            manager.save_long_term(long_content)

            loaded = manager.load_long_term()
            assert len(loaded) < 250  # 允许一些额外字符
            assert "截断" in loaded

    def test_get_today_log_path(self):
        """测试获取今日日志路径"""
        with tempfile.TemporaryDirectory() as tmpdir:
            manager = MemoryManager(workspace_path=Path(tmpdir))

            path = manager.get_today_log_path()
            expected_date = date.today().isoformat()
            assert expected_date in str(path)
            assert path.suffix == ".md"

    def test_append_to_today(self):
        """测试追加今日日志"""
        with tempfile.TemporaryDirectory() as tmpdir:
            manager = MemoryManager(workspace_path=Path(tmpdir))

            manager.append_to_today("测试日志条目")

            content = manager.get_today_content()
            assert content is not None
            assert "测试日志条目" in content

    def test_load_daily_empty(self):
        """测试加载空日志"""
        with tempfile.TemporaryDirectory() as tmpdir:
            manager = MemoryManager(workspace_path=Path(tmpdir))

            logs = manager.load_daily()
            assert len(logs) == 0

    def test_load_daily_with_logs(self):
        """测试加载最近日志"""
        with tempfile.TemporaryDirectory() as tmpdir:
            manager = MemoryManager(workspace_path=Path(tmpdir))

            # 创建今日和昨日日志
            manager.append_to_today("今日日志")

            # 创建昨日日志
            yesterday = date.today() - timedelta(days=1)
            yesterday_path = manager.get_log_path(yesterday)
            yesterday_path.parent.mkdir(parents=True, exist_ok=True)
            yesterday_path.write_text("# 昨日日志\n\n昨日内容", encoding="utf-8")

            logs = manager.load_daily(days=2)
            assert len(logs) == 2

    def test_search_empty(self):
        """测试空搜索"""
        with tempfile.TemporaryDirectory() as tmpdir:
            manager = MemoryManager(workspace_path=Path(tmpdir))

            results = manager.search("测试")
            assert len(results) == 0

    def test_search_long_term(self):
        """测试搜索长期记忆"""
        with tempfile.TemporaryDirectory() as tmpdir:
            manager = MemoryManager(workspace_path=Path(tmpdir))

            manager.save_long_term("# 记忆\n\n重要关键词: 测试内容")

            results = manager.search("关键词")
            assert len(results) == 1
            assert results[0].source == "MEMORY.md"

    def test_search_daily_logs(self):
        """测试搜索每日日志"""
        with tempfile.TemporaryDirectory() as tmpdir:
            manager = MemoryManager(workspace_path=Path(tmpdir))

            manager.append_to_today("这是一条测试日志")

            results = manager.search("测试")
            assert len(results) == 1
            assert date.today().isoformat() in results[0].source

    def test_export_markdown(self):
        """测试导出 Markdown"""
        with tempfile.TemporaryDirectory() as tmpdir:
            manager = MemoryManager(workspace_path=Path(tmpdir))

            manager.save_long_term("# 长期记忆\n\n内容")
            manager.append_to_today("今日日志")

            exported = manager.export(format="markdown")
            assert "长期记忆" in exported
            assert "今日日志" in exported

    def test_export_json(self):
        """测试导出 JSON"""
        with tempfile.TemporaryDirectory() as tmpdir:
            manager = MemoryManager(workspace_path=Path(tmpdir))

            manager.save_long_term("# 长期记忆\n\n内容")
            manager.append_to_today("今日日志")

            exported = manager.export(format="json")
            data = json.loads(exported)

            assert "long_term" in data
            assert "daily_logs" in data

    def test_export_invalid_format(self):
        """测试无效导出格式"""
        with tempfile.TemporaryDirectory() as tmpdir:
            manager = MemoryManager(workspace_path=Path(tmpdir))

            with pytest.raises(ValueError):
                manager.export(format="invalid")

    def test_clean_old_logs(self):
        """测试清理旧日志"""
        with tempfile.TemporaryDirectory() as tmpdir:
            manager = MemoryManager(workspace_path=Path(tmpdir))

            # 创建旧日志
            old_date = date.today() - timedelta(days=60)
            old_path = manager.get_log_path(old_date)
            old_path.parent.mkdir(parents=True, exist_ok=True)
            old_path.write_text("# 旧日志", encoding="utf-8")

            # 创建今日日志
            manager.append_to_today("今日日志")

            # 清理 30 天前的日志
            deleted = manager.clean_old_logs(days_to_keep=30)

            assert deleted == 1
            assert not old_path.exists()
            assert manager.get_today_log_path().exists()

    def test_clean_old_logs_no_dir(self):
        """测试清理时目录不存在"""
        with tempfile.TemporaryDirectory() as tmpdir:
            manager = MemoryManager(workspace_path=Path(tmpdir))

            deleted = manager.clean_old_logs()
            assert deleted == 0

    def test_get_stats(self):
        """测试获取统计"""
        with tempfile.TemporaryDirectory() as tmpdir:
            manager = MemoryManager(workspace_path=Path(tmpdir))

            # 空状态
            stats = manager.get_stats()
            assert stats["long_term_exists"] is False
            assert stats["daily_logs_count"] == 0

            # 有内容
            manager.save_long_term("测试内容")
            manager.append_to_today("今日日志")

            stats = manager.get_stats()
            assert stats["long_term_exists"] is True
            assert stats["long_term_chars"] == 4
            assert stats["daily_logs_count"] == 1


class TestMemoryAutomation:
    """MemoryAutomation 测试"""

    def test_init(self):
        """测试初始化"""
        automation = MemoryAutomation()
        assert automation.memory_manager is None

    def test_init_with_manager(self):
        """测试带管理器初始化"""
        with tempfile.TemporaryDirectory() as tmpdir:
            manager = MemoryManager(workspace_path=Path(tmpdir))
            automation = MemoryAutomation(memory_manager=manager)
            assert automation.memory_manager is manager

    def test_analyze_preference(self):
        """测试识别偏好"""
        automation = MemoryAutomation()

        result = automation.analyze_message("我喜欢使用 Python")
        assert result is not None
        assert result.type == "preference"
        assert "Python" in result.content

    def test_analyze_note(self):
        """测试识别笔记"""
        automation = MemoryAutomation()

        result = automation.analyze_message("记住明天要开会")
        assert result is not None
        assert result.type == "note"

    def test_analyze_decision(self):
        """测试识别决策"""
        automation = MemoryAutomation()

        result = automation.analyze_message("决定使用 React 框架")
        assert result is not None
        assert result.type == "decision"

    def test_analyze_personal_info(self):
        """测试识别个人信息"""
        automation = MemoryAutomation()

        result = automation.analyze_message("我叫张三")
        assert result is not None
        assert result.type == "info"

    def test_analyze_no_match(self):
        """测试无匹配"""
        automation = MemoryAutomation()

        result = automation.analyze_message("今天天气不错")
        assert result is None

    def test_analyze_negative_pattern(self):
        """测试否定模式"""
        automation = MemoryAutomation()

        result = automation.analyze_message("不，我不需要")
        assert result is None

    def test_analyze_conversation(self):
        """测试分析对话"""
        automation = MemoryAutomation()

        messages = [
            {"role": "user", "content": "我喜欢 Python"},
            {"role": "assistant", "content": "好的，我记住了"},
            {"role": "user", "content": "今天天气不错"},
        ]

        suggestions = automation.analyze_conversation(messages)
        assert len(suggestions) == 1
        assert suggestions[0].type == "preference"

    def test_should_update_memory_empty(self):
        """测试空建议不更新"""
        automation = MemoryAutomation()

        result = automation.should_update_memory({"suggestions": []})
        assert result is False

    def test_should_update_memory_low_confidence(self):
        """测试低置信度不更新"""
        automation = MemoryAutomation()

        suggestion = MemorySuggestion(
            type="note",
            content="测试",
            section="笔记",
            original_message="测试消息",
            confidence=0.5,
        )

        result = automation.should_update_memory({
            "suggestions": [suggestion],
            "confidence_threshold": 0.7,
        })
        assert result is False

    def test_should_update_memory_high_confidence(self):
        """测试高置信度更新"""
        automation = MemoryAutomation()

        suggestion = MemorySuggestion(
            type="note",
            content="测试",
            section="笔记",
            original_message="测试消息",
            confidence=0.9,
        )

        result = automation.should_update_memory({
            "suggestions": [suggestion],
            "confidence_threshold": 0.7,
        })
        assert result is True

    def test_suggest_memory_update(self):
        """测试生成更新建议"""
        automation = MemoryAutomation()

        suggestion = MemorySuggestion(
            type="preference",
            content="使用 Python",
            section="偏好",
            original_message="我喜欢使用 Python",
            confidence=0.9,
        )

        text = automation.suggest_memory_update(suggestion)
        assert "Python" in text
        assert "记忆" in text

    def test_generate_update_content(self):
        """测试生成更新内容"""
        automation = MemoryAutomation()

        suggestion = MemorySuggestion(
            type="preference",
            content="使用 Python",
            section="偏好",
            original_message="我喜欢使用 Python",
            confidence=0.9,
        )

        content = automation.generate_update_content(suggestion)
        assert "Python" in content


class TestGlobalInstances:
    """全局实例测试"""

    def test_get_memory_manager(self):
        """测试获取全局管理器"""
        reset_memory_manager()
        m1 = get_memory_manager()
        m2 = get_memory_manager()
        assert m1 is m2

    def test_reset_memory_manager(self):
        """测试重置管理器"""
        m1 = get_memory_manager()
        reset_memory_manager()
        m2 = get_memory_manager()
        assert m1 is not m2

    def test_get_memory_automation(self):
        """测试获取全局自动化"""
        reset_memory_automation()
        a1 = get_memory_automation()
        a2 = get_memory_automation()
        assert a1 is a2

    def test_reset_memory_automation(self):
        """测试重置自动化"""
        a1 = get_memory_automation()
        reset_memory_automation()
        a2 = get_memory_automation()
        assert a1 is not a2


class TestMemoryManagerEdgeCases:
    """边界情况测试"""

    def test_update_nonexistent_section(self):
        """测试更新不存在的部分"""
        with tempfile.TemporaryDirectory() as tmpdir:
            manager = MemoryManager(workspace_path=Path(tmpdir))

            manager.save_long_term("# 记忆\n\n现有内容")
            manager.update_long_term("新部分", "新内容")

            content = manager.load_long_term()
            assert "新部分" in content
            assert "新内容" in content

    def test_get_today_content_empty(self):
        """测试今日日志为空"""
        with tempfile.TemporaryDirectory() as tmpdir:
            manager = MemoryManager(workspace_path=Path(tmpdir))

            content = manager.get_today_content()
            assert content is None

    def test_search_with_regex_chars(self):
        """测试搜索包含正则字符"""
        with tempfile.TemporaryDirectory() as tmpdir:
            manager = MemoryManager(workspace_path=Path(tmpdir))

            manager.save_long_term("测试 [括号] 和 (圆括号)")

            # 应该正确转义特殊字符
            results = manager.search("[括号]")
            assert len(results) == 1

    def test_clean_logs_with_invalid_filename(self):
        """测试清理时有无效文件名"""
        with tempfile.TemporaryDirectory() as tmpdir:
            manager = MemoryManager(workspace_path=Path(tmpdir))

            # 创建无效文件名的日志
            manager.memory_dir.mkdir(parents=True, exist_ok=True)
            invalid_file = manager.memory_dir / "not-a-date.md"
            invalid_file.write_text("无效日志", encoding="utf-8")

            # 应该跳过无效文件
            deleted = manager.clean_old_logs()
            assert deleted == 0
            assert invalid_file.exists()

    def test_multiple_append_to_today(self):
        """测试多次追加今日日志"""
        with tempfile.TemporaryDirectory() as tmpdir:
            manager = MemoryManager(workspace_path=Path(tmpdir))

            manager.append_to_today("第一条")
            manager.append_to_today("第二条")
            manager.append_to_today("第三条")

            content = manager.get_today_content()
            assert "第一条" in content
            assert "第二条" in content
            assert "第三条" in content
