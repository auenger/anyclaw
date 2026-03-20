"""验证器模块测试"""

import pytest
from pathlib import Path

from anyclaw.security.validators import (
    ValidationError,
    Validator,
    URLValidator,
    PathValidator,
    validate_url,
    validate_path,
    validate_filename,
)


class TestValidator:
    """基础验证器测试"""

    def test_not_empty_string(self):
        """测试非空验证 - 有效字符串"""
        assert Validator.not_empty("hello") == "hello"
        assert Validator.not_empty("  hello  ") == "hello"  # strip

    def test_not_empty_number(self):
        """测试非空验证 - 数字"""
        assert Validator.not_empty(123) == 123
        assert Validator.not_empty(0) == 0

    def test_not_empty_none(self):
        """测试非空验证 - None"""
        with pytest.raises(ValidationError) as exc_info:
            Validator.not_empty(None)
        assert "cannot be empty" in str(exc_info.value)

    def test_not_empty_empty_string(self):
        """测试非空验证 - 空字符串"""
        with pytest.raises(ValidationError) as exc_info:
            Validator.not_empty("")
        assert "cannot be empty" in str(exc_info.value)

    def test_not_empty_whitespace_only(self):
        """测试非空验证 - 仅空白"""
        with pytest.raises(ValidationError) as exc_info:
            Validator.not_empty("   \n\t  ")
        assert "cannot be empty" in str(exc_info.value)

    def test_max_length_valid(self):
        """测试最大长度 - 有效"""
        assert Validator.max_length("hello", 10) == "hello"
        assert Validator.max_length("hello", 5) == "hello"

    def test_max_length_invalid(self):
        """测试最大长度 - 无效"""
        with pytest.raises(ValidationError) as exc_info:
            Validator.max_length("hello world", 5)
        assert "exceeds maximum length" in str(exc_info.value)

    def test_min_length_valid(self):
        """测试最小长度 - 有效"""
        assert Validator.min_length("hello", 3) == "hello"
        assert Validator.min_length("hello", 5) == "hello"

    def test_min_length_invalid(self):
        """测试最小长度 - 无效"""
        with pytest.raises(ValidationError) as exc_info:
            Validator.min_length("hi", 5)
        assert "must be at least" in str(exc_info.value)

    def test_in_range_valid(self):
        """测试范围验证 - 有效"""
        assert Validator.in_range(5, 1, 10) == 5
        assert Validator.in_range(1, 1, 10) == 1  # 边界
        assert Validator.in_range(10, 1, 10) == 10  # 边界

    def test_in_range_invalid_low(self):
        """测试范围验证 - 太小"""
        with pytest.raises(ValidationError) as exc_info:
            Validator.in_range(0, 1, 10)
        assert "must be between" in str(exc_info.value)

    def test_in_range_invalid_high(self):
        """测试范围验证 - 太大"""
        with pytest.raises(ValidationError) as exc_info:
            Validator.in_range(11, 1, 10)
        assert "must be between" in str(exc_info.value)

    def test_in_range_invalid_type(self):
        """测试范围验证 - 非数字"""
        with pytest.raises(ValidationError) as exc_info:
            Validator.in_range("5", 1, 10)
        assert "must be a number" in str(exc_info.value)

    def test_pattern_valid(self):
        """测试正则验证 - 有效"""
        import re
        pattern = re.compile(r'^\d+$')
        assert Validator.pattern("123", pattern) == "123"

    def test_pattern_invalid(self):
        """测试正则验证 - 无效"""
        import re
        pattern = re.compile(r'^\d+$')
        with pytest.raises(ValidationError) as exc_info:
            Validator.pattern("abc", pattern)
        assert "invalid format" in str(exc_info.value)

    def test_one_of_valid(self):
        """测试枚举验证 - 有效"""
        assert Validator.one_of("a", ["a", "b", "c"]) == "a"
        assert Validator.one_of(1, [1, 2, 3]) == 1

    def test_one_of_invalid(self):
        """测试枚举验证 - 无效"""
        with pytest.raises(ValidationError) as exc_info:
            Validator.one_of("d", ["a", "b", "c"])
        assert "must be one of" in str(exc_info.value)


class TestURLValidator:
    """URL 验证器测试"""

    def test_valid_http_url(self):
        """测试有效 HTTP URL"""
        assert URLValidator.validate("http://example.com") == "http://example.com"
        assert URLValidator.validate("http://example.com/path") == "http://example.com/path"

    def test_valid_https_url(self):
        """测试有效 HTTPS URL"""
        assert URLValidator.validate("https://example.com") == "https://example.com"
        assert URLValidator.validate("https://example.com/path?query=1") == "https://example.com/path?query=1"

    def test_url_with_port(self):
        """测试带端口的 URL"""
        assert URLValidator.validate("http://example.com:8080") == "http://example.com:8080"

    def test_empty_url(self):
        """测试空 URL"""
        with pytest.raises(ValidationError) as exc_info:
            URLValidator.validate("")
        assert "cannot be empty" in str(exc_info.value)

    def test_empty_url_allow_empty(self):
        """测试空 URL - 允许空"""
        assert URLValidator.validate("", allow_empty=True) == ""

    def test_url_without_protocol(self):
        """测试无协议 URL"""
        with pytest.raises(ValidationError) as exc_info:
            URLValidator.validate("example.com")
        assert "must include protocol" in str(exc_info.value)

    def test_dangerous_protocol_file(self):
        """测试危险协议 - file://"""
        with pytest.raises(ValidationError) as exc_info:
            URLValidator.validate("file:///etc/passwd")
        assert "not allowed" in str(exc_info.value)

    def test_dangerous_protocol_javascript(self):
        """测试危险协议 - javascript:"""
        with pytest.raises(ValidationError) as exc_info:
            URLValidator.validate("javascript:alert(1)")
        assert "not allowed" in str(exc_info.value)

    def test_dangerous_protocol_data(self):
        """测试危险协议 - data:"""
        with pytest.raises(ValidationError) as exc_info:
            URLValidator.validate("data:text/html,<script>alert(1)</script>")
        assert "not allowed" in str(exc_info.value)

    def test_unsupported_protocol(self):
        """测试不支持的协议"""
        with pytest.raises(ValidationError) as exc_info:
            URLValidator.validate("ftp://example.com")
        assert "Only" in str(exc_info.value) and "allowed" in str(exc_info.value)

    def test_url_without_hostname(self):
        """测试无主机名的 URL"""
        with pytest.raises(ValidationError) as exc_info:
            URLValidator.validate("http://")
        assert "must include hostname" in str(exc_info.value)

    def test_is_safe_url(self):
        """测试 is_safe_url 方法"""
        assert URLValidator.is_safe_url("https://example.com") is True
        assert URLValidator.is_safe_url("file:///etc/passwd") is False
        assert URLValidator.is_safe_url("") is False


class TestPathValidator:
    """路径验证器测试"""

    def test_valid_filename(self):
        """测试有效文件名"""
        assert PathValidator.validate_filename("test.txt") == "test.txt"
        assert PathValidator.validate_filename("my_file.py") == "my_file.py"

    def test_empty_filename(self):
        """测试空文件名"""
        with pytest.raises(ValidationError) as exc_info:
            PathValidator.validate_filename("")
        assert "cannot be empty" in str(exc_info.value)

    def test_filename_with_dangerous_chars(self):
        """测试包含危险字符的文件名"""
        dangerous_chars = ['<', '>', ':', '"', '|', '?', '*']
        for char in dangerous_chars:
            with pytest.raises(ValidationError) as exc_info:
                PathValidator.validate_filename(f"test{char}file.txt")
            assert "invalid character" in str(exc_info.value)

    def test_windows_reserved_con(self):
        """测试 Windows 保留名 - CON"""
        with pytest.raises(ValidationError) as exc_info:
            PathValidator.validate_filename("CON")
        assert "reserved filename" in str(exc_info.value)

    def test_windows_reserved_prn(self):
        """测试 Windows 保留名 - PRN"""
        with pytest.raises(ValidationError) as exc_info:
            PathValidator.validate_filename("PRN")
        assert "reserved filename" in str(exc_info.value)

    def test_windows_reserved_aux(self):
        """测试 Windows 保留名 - AUX"""
        with pytest.raises(ValidationError) as exc_info:
            PathValidator.validate_filename("AUX")
        assert "reserved filename" in str(exc_info.value)

    def test_windows_reserved_nul(self):
        """测试 Windows 保留名 - NUL"""
        with pytest.raises(ValidationError) as exc_info:
            PathValidator.validate_filename("NUL")
        assert "reserved filename" in str(exc_info.value)

    def test_windows_reserved_com(self):
        """测试 Windows 保留名 - COM1"""
        with pytest.raises(ValidationError) as exc_info:
            PathValidator.validate_filename("COM1")
        assert "reserved filename" in str(exc_info.value)

    def test_windows_reserved_lpt(self):
        """测试 Windows 保留名 - LPT1"""
        with pytest.raises(ValidationError) as exc_info:
            PathValidator.validate_filename("LPT1.txt")
        assert "reserved filename" in str(exc_info.value)

    def test_valid_path(self):
        """测试有效路径"""
        assert PathValidator.validate_path("path/to/file.txt") == "path/to/file.txt"

    def test_empty_path(self):
        """测试空路径"""
        with pytest.raises(ValidationError) as exc_info:
            PathValidator.validate_path("")
        assert "cannot be empty" in str(exc_info.value)

    def test_path_traversal(self):
        """测试路径遍历攻击"""
        with pytest.raises(ValidationError) as exc_info:
            PathValidator.validate_path("../../../etc/passwd")
        assert "dangerous pattern" in str(exc_info.value)

    def test_path_with_home(self):
        """测试 Home 目录路径"""
        with pytest.raises(ValidationError) as exc_info:
            PathValidator.validate_path("~/secret")
        assert "dangerous pattern" in str(exc_info.value)

    def test_path_with_etc(self):
        """测试系统目录路径"""
        with pytest.raises(ValidationError) as exc_info:
            PathValidator.validate_path("/etc/passwd")
        assert "dangerous pattern" in str(exc_info.value)

    def test_path_absolute_not_allowed(self):
        """测试绝对路径不被允许"""
        with pytest.raises(ValidationError) as exc_info:
            PathValidator.validate_path("/absolute/path", allow_absolute=False)
        assert "Absolute paths are not allowed" in str(exc_info.value)

    def test_is_safe_filename(self):
        """测试 is_safe_filename 方法"""
        assert PathValidator.is_safe_filename("test.txt") is True
        assert PathValidator.is_safe_filename("CON") is False
        assert PathValidator.is_safe_filename("test<>.txt") is False

    def test_is_safe_path(self):
        """测试 is_safe_path 方法"""
        assert PathValidator.is_safe_path("path/to/file.txt") is True
        assert PathValidator.is_safe_path("../../../etc/passwd") is False


class TestConvenienceFunctions:
    """便捷函数测试"""

    def test_validate_url(self):
        """测试 validate_url 便捷函数"""
        assert validate_url("https://example.com") == "https://example.com"

    def test_validate_path(self):
        """测试 validate_path 便捷函数"""
        assert validate_path("path/to/file.txt") == "path/to/file.txt"

    def test_validate_filename(self):
        """测试 validate_filename 便捷函数"""
        assert validate_filename("test.txt") == "test.txt"
