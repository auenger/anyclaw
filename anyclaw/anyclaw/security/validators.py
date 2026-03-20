"""输入验证器模块

提供统一的输入验证功能：
- 基础验证器 (非空、长度、范围)
- URL 验证器 (协议、格式)
- 路径验证器 (文件名安全性)
"""

import re
from pathlib import Path
from typing import Any, Optional, List, Pattern
from urllib.parse import urlparse


class ValidationError(Exception):
    """验证错误异常"""

    def __init__(self, message: str, field: Optional[str] = None):
        self.message = message
        self.field = field
        super().__init__(message)


class Validator:
    """基础验证器"""

    @staticmethod
    def not_empty(value: Any, field_name: str = "value") -> Any:
        """
        非空验证

        Args:
            value: 要验证的值
            field_name: 字段名称（用于错误消息）

        Returns:
            验证后的值（字符串会 strip）

        Raises:
            ValidationError: 值为空或仅包含空白
        """
        if value is None:
            raise ValidationError(f"{field_name} cannot be empty", field_name)

        if isinstance(value, str):
            if not value.strip():
                raise ValidationError(f"{field_name} cannot be empty", field_name)
            return value.strip()

        return value

    @staticmethod
    def max_length(value: str, max_len: int, field_name: str = "value") -> str:
        """
        最大长度验证

        Args:
            value: 字符串值
            max_len: 最大长度
            field_name: 字段名称

        Returns:
            原始值

        Raises:
            ValidationError: 超过最大长度
        """
        if len(value) > max_len:
            raise ValidationError(
                f"{field_name} exceeds maximum length ({max_len} chars)",
                field_name
            )
        return value

    @staticmethod
    def min_length(value: str, min_len: int, field_name: str = "value") -> str:
        """
        最小长度验证

        Args:
            value: 字符串值
            min_len: 最小长度
            field_name: 字段名称

        Returns:
            原始值

        Raises:
            ValidationError: 小于最小长度
        """
        if len(value) < min_len:
            raise ValidationError(
                f"{field_name} must be at least {min_len} chars",
                field_name
            )
        return value

    @staticmethod
    def in_range(
        value: int,
        min_val: int,
        max_val: int,
        field_name: str = "value"
    ) -> int:
        """
        数值范围验证

        Args:
            value: 数值
            min_val: 最小值（包含）
            max_val: 最大值（包含）
            field_name: 字段名称

        Returns:
            原始值

        Raises:
            ValidationError: 超出范围
        """
        if not isinstance(value, (int, float)):
            raise ValidationError(
                f"{field_name} must be a number",
                field_name
            )
        if not min_val <= value <= max_val:
            raise ValidationError(
                f"{field_name} must be between {min_val} and {max_val}",
                field_name
            )
        return value

    @staticmethod
    def pattern(
        value: str,
        regex: Pattern,
        field_name: str = "value",
        error_msg: Optional[str] = None
    ) -> str:
        """
        正则表达式验证

        Args:
            value: 字符串值
            regex: 正则表达式
            field_name: 字段名称
            error_msg: 自定义错误消息

        Returns:
            原始值

        Raises:
            ValidationError: 不匹配正则
        """
        if not regex.match(value):
            msg = error_msg or f"{field_name} has invalid format"
            raise ValidationError(msg, field_name)
        return value

    @staticmethod
    def one_of(value: Any, options: List[Any], field_name: str = "value") -> Any:
        """
        枚举值验证

        Args:
            value: 值
            options: 允许的选项列表
            field_name: 字段名称

        Returns:
            原始值

        Raises:
            ValidationError: 值不在允许列表中
        """
        if value not in options:
            raise ValidationError(
                f"{field_name} must be one of: {options}",
                field_name
            )
        return value


class URLValidator(Validator):
    """URL 验证器"""

    # 允许的协议
    ALLOWED_PROTOCOLS = ["http", "https"]

    # 危险协议（会被阻止）
    DANGEROUS_PROTOCOLS = [
        "file",      # 本地文件访问
        "javascript", # XSS
        "data",      # Data URI
        "vbscript",  # VBScript
        "about",     # 浏览器内部
        "blob",      # Blob URI
        "ws",        # WebSocket
        "wss",       # Secure WebSocket
    ]

    @classmethod
    def validate(cls, url: str, allow_empty: bool = False) -> str:
        """
        验证 URL

        Args:
            url: URL 字符串
            allow_empty: 是否允许空值

        Returns:
            验证后的 URL

        Raises:
            ValidationError: URL 无效
        """
        # 处理空值
        if not url or not url.strip():
            if allow_empty:
                return ""
            raise ValidationError("URL cannot be empty", "url")

        url = url.strip()

        try:
            parsed = urlparse(url)
        except Exception:
            raise ValidationError("Invalid URL format", "url")

        # 检查协议
        protocol = parsed.scheme.lower()

        if not protocol:
            raise ValidationError(
                "URL must include protocol (http/https)",
                "url"
            )

        if protocol in cls.DANGEROUS_PROTOCOLS:
            raise ValidationError(
                f"Protocol '{protocol}' is not allowed for security reasons",
                "url"
            )

        if protocol not in cls.ALLOWED_PROTOCOLS:
            raise ValidationError(
                f"Only {cls.ALLOWED_PROTOCOLS} protocols are allowed",
                "url"
            )

        # 检查主机名
        if not parsed.netloc:
            raise ValidationError("URL must include hostname", "url")

        return url

    @classmethod
    def is_safe_url(cls, url: str) -> bool:
        """
        检查 URL 是否安全（不抛出异常）

        Args:
            url: URL 字符串

        Returns:
            是否安全
        """
        try:
            cls.validate(url)
            return True
        except ValidationError:
            return False


class PathValidator(Validator):
    """路径验证器"""

    # Windows 保留文件名
    WINDOWS_RESERVED = {
        "CON", "PRN", "AUX", "NUL",
        "COM1", "COM2", "COM3", "COM4", "COM5", "COM6", "COM7", "COM8", "COM9",
        "LPT1", "LPT2", "LPT3", "LPT4", "LPT5", "LPT6", "LPT7", "LPT8", "LPT9",
    }

    # 危险文件名字符
    DANGEROUS_CHARS = ['<', '>', ':', '"', '|', '?', '*', '\x00']

    # 危险路径模式
    DANGEROUS_PATTERNS = [
        r'\.\.',           # 路径遍历
        r'~/',             # Home 目录
        r'/etc/',          # Unix 系统目录
        r'/proc/',         # Unix proc 文件系统
        r'/sys/',          # Unix sys 文件系统
        r'/dev/',          # Unix 设备目录
    ]

    @classmethod
    def validate_filename(cls, filename: str) -> str:
        """
        验证文件名

        Args:
            filename: 文件名

        Returns:
            验证后的文件名

        Raises:
            ValidationError: 文件名无效
        """
        if not filename or not filename.strip():
            raise ValidationError("Filename cannot be empty", "filename")

        filename = filename.strip()

        # 检查危险字符
        for char in cls.DANGEROUS_CHARS:
            if char in filename:
                raise ValidationError(
                    f"Filename contains invalid character: {repr(char)}",
                    "filename"
                )

        # 检查 Windows 保留名
        name_part = filename.split('.')[0].upper()
        if name_part in cls.WINDOWS_RESERVED:
            raise ValidationError(
                f"'{filename}' is a reserved filename on Windows",
                "filename"
            )

        # 检查以点开头的隐藏文件（警告级别，不阻止）
        # 由调用方决定是否处理

        return filename

    @classmethod
    def validate_path(
        cls,
        path: str,
        base_dir: Optional[Path] = None,
        allow_absolute: bool = True
    ) -> str:
        """
        验证路径

        Args:
            path: 路径字符串
            base_dir: 基础目录（用于检查路径遍历）
            allow_absolute: 是否允许绝对路径

        Returns:
            验证后的路径

        Raises:
            ValidationError: 路径无效
        """
        if not path or not path.strip():
            raise ValidationError("Path cannot be empty", "path")

        path = path.strip()

        # 检查危险模式
        for pattern in cls.DANGEROUS_PATTERNS:
            if re.search(pattern, path):
                raise ValidationError(
                    f"Path contains potentially dangerous pattern",
                    "path"
                )

        # 检查危险字符
        for char in cls.DANGEROUS_CHARS:
            if char in path:
                raise ValidationError(
                    f"Path contains invalid character: {repr(char)}",
                    "path"
                )

        # 检查绝对路径
        p = Path(path)
        if p.is_absolute() and not allow_absolute:
            raise ValidationError(
                "Absolute paths are not allowed",
                "path"
            )

        # 检查路径遍历（如果有 base_dir）
        if base_dir:
            try:
                # 解析真实路径
                full_path = (base_dir / path).resolve()
                base_resolved = base_dir.resolve()

                # 检查是否在 base_dir 内
                if not str(full_path).startswith(str(base_resolved)):
                    raise ValidationError(
                        "Path traversal detected - path must be within base directory",
                        "path"
                    )
            except OSError:
                # 路径解析失败（如不存在的路径）
                pass

        return path

    @classmethod
    def is_safe_filename(cls, filename: str) -> bool:
        """
        检查文件名是否安全（不抛出异常）

        Args:
            filename: 文件名

        Returns:
            是否安全
        """
        try:
            cls.validate_filename(filename)
            return True
        except ValidationError:
            return False

    @classmethod
    def is_safe_path(cls, path: str, base_dir: Optional[Path] = None) -> bool:
        """
        检查路径是否安全（不抛出异常）

        Args:
            path: 路径
            base_dir: 基础目录

        Returns:
            是否安全
        """
        try:
            cls.validate_path(path, base_dir)
            return True
        except ValidationError:
            return False


# 便捷函数
def validate_url(url: str) -> str:
    """验证 URL（便捷函数）"""
    return URLValidator.validate(url)


def validate_path(path: str, base_dir: Optional[Path] = None) -> str:
    """验证路径（便捷函数）"""
    return PathValidator.validate_path(path, base_dir)


def validate_filename(filename: str) -> str:
    """验证文件名（便捷函数）"""
    return PathValidator.validate_filename(filename)
