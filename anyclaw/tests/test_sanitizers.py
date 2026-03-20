"""清理器模块测试"""

import pytest

from anyclaw.security.sanitizers import (
    ContentSanitizer,
    sanitize_message,
    sanitize_command,
    sanitize_tool_output,
)


class TestContentSanitizer:
    """内容清理器测试"""

    # ========== sanitize_message 测试 ==========

    def test_sanitize_valid_message(self):
        """测试有效消息"""
        result = ContentSanitizer.sanitize_message("Hello, world!")
        assert result == "Hello, world!"

    def test_sanitize_message_strip(self):
        """测试消息首尾空白处理"""
        result = ContentSanitizer.sanitize_message("  Hello  ")
        assert result == "Hello"

    def test_sanitize_message_preserve_newlines(self):
        """测试保留换行符"""
        result = ContentSanitizer.sanitize_message("Line1\nLine2\nLine3")
        assert result == "Line1\nLine2\nLine3"

    def test_sanitize_message_preserve_tabs(self):
        """测试保留制表符"""
        result = ContentSanitizer.sanitize_message("Col1\tCol2")
        assert result == "Col1\tCol2"

    def test_sanitize_empty_message(self):
        """测试空消息"""
        with pytest.raises(ValueError) as exc_info:
            ContentSanitizer.sanitize_message("")
        assert "cannot be empty" in str(exc_info.value)

    def test_sanitize_none_message(self):
        """测试 None 消息"""
        with pytest.raises(ValueError) as exc_info:
            ContentSanitizer.sanitize_message(None)  # type: ignore
        assert "cannot be empty" in str(exc_info.value)

    def test_sanitize_whitespace_only_message(self):
        """测试仅包含空白的消息"""
        with pytest.raises(ValueError) as exc_info:
            ContentSanitizer.sanitize_message("   \n\t  ")
        assert "cannot be empty" in str(exc_info.value)

    # ========== 危险 Unicode 字符测试 ==========

    def test_remove_null_char(self):
        """测试移除 NULL 字符"""
        result = ContentSanitizer.sanitize_message("Hello\x00World")
        assert result == "HelloWorld"
        assert "\x00" not in result

    def test_remove_escape_char(self):
        """测试移除 ESC 字符"""
        result = ContentSanitizer.sanitize_message("Hello\x1bWorld")
        assert result == "HelloWorld"

    def test_remove_zero_width_space(self):
        """测试移除零宽空格"""
        result = ContentSanitizer.sanitize_message("Hello\u200bWorld")
        assert result == "HelloWorld"

    def test_remove_zero_width_non_joiner(self):
        """测试移除零宽非连接符"""
        result = ContentSanitizer.sanitize_message("Hello\u200cWorld")
        assert result == "HelloWorld"

    def test_remove_zero_width_joiner(self):
        """测试移除零宽连接符"""
        result = ContentSanitizer.sanitize_message("Hello\u200dWorld")
        assert result == "HelloWorld"

    def test_remove_lrm(self):
        """测试移除从左到右标记"""
        result = ContentSanitizer.sanitize_message("Hello\u200eWorld")
        assert result == "HelloWorld"

    def test_remove_rlm(self):
        """测试移除从右到左标记"""
        result = ContentSanitizer.sanitize_message("Hello\u200fWorld")
        assert result == "HelloWorld"

    def test_remove_bom(self):
        """测试移除 BOM"""
        result = ContentSanitizer.sanitize_message("\ufeffHello")
        assert result == "Hello"

    def test_remove_multiple_dangerous_chars(self):
        """测试移除多个危险字符"""
        result = ContentSanitizer.sanitize_message("H\x00e\u200bl\u200cl\u200do")
        assert result == "Hello"

    # ========== 控制字符测试 ==========

    def test_remove_control_chars(self):
        """测试移除控制字符"""
        # 控制字符 (0x01-0x08, 0x0b, 0x0c, 0x0e-0x1f)
        result = ContentSanitizer.sanitize_message("Hello\x01\x02\x03World")
        assert result == "HelloWorld"

    def test_preserve_newline_and_tab(self):
        """测试保留换行和制表符"""
        result = ContentSanitizer.sanitize_message("Line1\nLine2\tTab")
        assert "\n" in result
        assert "\t" in result

    # ========== 长度限制测试 ==========

    def test_truncate_long_message(self):
        """测试截断超长消息"""
        long_msg = "A" * 150_000
        result = ContentSanitizer.sanitize_message(long_msg)
        assert len(result) == 100_000

    def test_truncate_custom_length(self):
        """测试自定义长度截断"""
        long_msg = "A" * 200
        result = ContentSanitizer.sanitize_message(long_msg, max_length=100)
        assert len(result) == 100

    def test_no_truncate_flag(self):
        """测试不截断标志"""
        long_msg = "A" * 150_000
        with pytest.raises(ValueError) as exc_info:
            ContentSanitizer.sanitize_message(long_msg, truncate=False)
        assert "exceeds maximum length" in str(exc_info.value)

    # ========== sanitize_command 测试 ==========

    def test_sanitize_valid_command(self):
        """测试有效命令"""
        result = ContentSanitizer.sanitize_command("ls -la")
        assert result == "ls -la"

    def test_sanitize_command_strip(self):
        """测试命令首尾空白处理"""
        result = ContentSanitizer.sanitize_command("  ls -la  ")
        assert result == "ls -la"

    def test_sanitize_empty_command(self):
        """测试空命令"""
        with pytest.raises(ValueError) as exc_info:
            ContentSanitizer.sanitize_command("")
        assert "cannot be empty" in str(exc_info.value)

    def test_sanitize_whitespace_only_command(self):
        """测试仅空白的命令"""
        with pytest.raises(ValueError) as exc_info:
            ContentSanitizer.sanitize_command("   ")
        assert "cannot be empty" in str(exc_info.value)

    def test_sanitize_too_long_command(self):
        """测试超长命令"""
        long_cmd = "A" * 15_000
        with pytest.raises(ValueError) as exc_info:
            ContentSanitizer.sanitize_command(long_cmd)
        assert "exceeds maximum length" in str(exc_info.value)

    # ========== sanitize_tool_output 测试 ==========

    def test_sanitize_tool_output(self):
        """测试工具输出清理"""
        result = ContentSanitizer.sanitize_tool_output("Output content")
        assert result == "Output content"

    def test_sanitize_empty_tool_output(self):
        """测试空工具输出"""
        result = ContentSanitizer.sanitize_tool_output("")
        assert result == ""

    def test_sanitize_tool_output_none(self):
        """测试 None 工具输出"""
        result = ContentSanitizer.sanitize_tool_output(None)  # type: ignore
        assert result == ""

    def test_sanitize_tool_output_truncate(self):
        """测试工具输出截断"""
        long_output = "A" * 150_000
        result = ContentSanitizer.sanitize_tool_output(long_output)
        assert len(result) < len(long_output)
        assert "truncated" in result

    def test_sanitize_tool_output_remove_dangerous(self):
        """测试工具输出移除危险字符"""
        result = ContentSanitizer.sanitize_tool_output("Output\x00\u200b")
        assert "\x00" not in result
        assert "\u200b" not in result

    # ========== 辅助方法测试 ==========

    def test_remove_zero_width_chars(self):
        """测试移除零宽字符方法"""
        result = ContentSanitizer.remove_zero_width_chars("H\u200be\u200cl\u200dl\u200eo")
        assert result == "Hello"

    def test_normalize_whitespace(self):
        """测试标准化空白"""
        result = ContentSanitizer.normalize_whitespace("  Hello    World  ")
        assert result == "Hello World"

    def test_normalize_whitespace_preserve_newlines(self):
        """测试标准化空白保留换行"""
        result = ContentSanitizer.normalize_whitespace("Line1\n  Line2")
        assert result == "Line1\nLine2"

    def test_is_safe_content(self):
        """测试 is_safe_content 方法"""
        assert ContentSanitizer.is_safe_content("Hello World") is True
        assert ContentSanitizer.is_safe_content("") is False
        assert ContentSanitizer.is_safe_content("   ") is False


class TestConvenienceFunctions:
    """便捷函数测试"""

    def test_sanitize_message_func(self):
        """测试 sanitize_message 便捷函数"""
        result = sanitize_message("  Hello  ")
        assert result == "Hello"

    def test_sanitize_command_func(self):
        """测试 sanitize_command 便捷函数"""
        result = sanitize_command("  ls -la  ")
        assert result == "ls -la"

    def test_sanitize_tool_output_func(self):
        """测试 sanitize_tool_output 便捷函数"""
        result = sanitize_tool_output("Output")
        assert result == "Output"


class TestEdgeCases:
    """边界情况测试"""

    def test_unicode_bypass_attempt(self):
        """测试 Unicode 绕过尝试"""
        # 尝试使用各种 Unicode 字符绕过
        bypasses = [
            "Hello\u202eWorld",  # RTL Override (不在危险列表，应该保留)
            "test\ufffe",  # 非字符
        ]
        for text in bypasses:
            # 不应该抛出异常
            result = ContentSanitizer.sanitize_message(text)
            assert isinstance(result, str)

    def test_mixed_attack(self):
        """测试混合攻击"""
        # 零宽字符 + 控制字符
        result = ContentSanitizer.sanitize_message(
            "H\x00e\u200bl\u200cl\u200do"
        )
        assert result == "Hello"

    def test_exact_max_length(self):
        """测试恰好最大长度"""
        msg = "A" * 100_000
        result = ContentSanitizer.sanitize_message(msg)
        assert len(result) == 100_000

    def test_one_over_max_length(self):
        """测试超过最大长度一个字符"""
        msg = "A" * 100_001
        result = ContentSanitizer.sanitize_message(msg)
        assert len(result) == 100_000
