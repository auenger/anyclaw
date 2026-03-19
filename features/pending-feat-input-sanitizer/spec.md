# 输入验证与清理

## 背景

AnyClaw 缺乏系统性的输入验证和清理机制，可能导致：
- 注入攻击（命令注入、路径注入）
- 异常内容导致处理错误
- 恶意输入绕过安全检查
- 数据完整性问题

## 需求

实现统一的输入验证和清理系统，确保所有外部输入都经过安全处理。

## 用户价值点

### VP1: 消息内容清理

清理用户消息和 LLM 响应中的异常内容。

**Gherkin 场景**:

```gherkin
Feature: 消息内容清理

  Scenario: 清理空消息
    Given 用户发送空消息 ""
    When 处理消息
    Then 返回错误 "Message cannot be empty"

  Scenario: 清理纯空白消息
    Given 用户发送消息 "   \n\t  "
    When 处理消息
    Then 返回错误 "Message cannot be empty"

  Scenario: 截断超长消息
    Given 用户发送超过 100,000 字符的消息
    When 处理消息
    Then 消息被截断到 100,000 字符
    And 记录警告日志

  Scenario: 移除危险 Unicode 字符
    Given 消息包含零宽字符和控制字符
    When 清理消息
    Then 危险字符被移除
```

### VP2: 工具参数验证

验证工具调用的参数格式和范围。

**Gherkin 场景**:

```gherkin
Feature: 工具参数验证

  Scenario: 验证文件路径参数
    Given 工具调用 read_file
    And 参数 path = null
    When 验证参数
    Then 返回错误 "Parameter 'path' is required"

  Scenario: 验证数值范围
    Given 工具调用 exec
    And 参数 timeout = 1000
    When 验证参数
    Then 返回错误 "timeout must be between 1 and 300"

  Scenario: 验证字符串长度
    Given 工具调用 write_file
    And 参数 content 超过 10MB
    When 验证参数
    Then 返回错误 "content exceeds maximum size"

  Scenario: 清理命令参数
    Given 工具调用 exec
    And 参数 command 包含注入尝试
    When 清理参数
    Then 注入内容被标记或阻止
```

### VP3: URL 和路径验证

专门验证 URL 和路径格式的安全性。

**Gherkin 场景**:

```gherkin
Feature: URL 和路径验证

  Scenario: 验证 URL 格式
    Given URL = "not-a-url"
    When 验证 URL
    Then 返回错误 "Invalid URL format"

  Scenario: 验证 URL 协议
    Given URL = "file:///etc/passwd"
    When 验证 URL
    Then 返回错误 "Only http/https protocols allowed"

  Scenario: 验证路径格式
    Given path = "con.txt" (Windows 保留名)
    When 验证路径
    Then 返回警告 "Reserved filename"
```

## 技术方案

### 1. 输入验证器

```python
# anyclaw/security/validators.py

import re
from typing import Any, Optional, List, Callable
from pathlib import Path

class ValidationError(Exception):
    """验证错误"""
    pass

class Validator:
    """基础验证器"""

    @staticmethod
    def not_empty(value: str, field_name: str = "value") -> str:
        """非空验证"""
        if not value or not value.strip():
            raise ValidationError(f"{field_name} cannot be empty")
        return value.strip()

    @staticmethod
    def max_length(value: str, max_len: int, field_name: str = "value") -> str:
        """最大长度验证"""
        if len(value) > max_len:
            raise ValidationError(
                f"{field_name} exceeds maximum length ({max_len})"
            )
        return value

    @staticmethod
    def in_range(value: int, min_val: int, max_val: int, field_name: str = "value") -> int:
        """数值范围验证"""
        if not min_val <= value <= max_val:
            raise ValidationError(
                f"{field_name} must be between {min_val} and {max_val}"
            )
        return value


class URLValidator(Validator):
    """URL 验证器"""

    ALLOWED_PROTOCOLS = ["http", "https"]

    # 危险协议
    DANGEROUS_PROTOCOLS = [
        "file", "javascript", "data", "vbscript",
        "about", "blob", "ws", "wss",
    ]

    @classmethod
    def validate(cls, url: str) -> str:
        """验证 URL"""
        from urllib.parse import urlparse

        url = cls.not_empty(url, "URL")

        try:
            parsed = urlparse(url)
        except Exception:
            raise ValidationError("Invalid URL format")

        # 检查协议
        protocol = parsed.scheme.lower()
        if not protocol:
            raise ValidationError("URL must include protocol (http/https)")

        if protocol in cls.DANGEROUS_PROTOCOLS:
            raise ValidationError(f"Protocol '{protocol}' is not allowed")

        if protocol not in cls.ALLOWED_PROTOCOLS:
            raise ValidationError(
                f"Only {cls.ALLOWED_PROTOCOLS} protocols are allowed"
            )

        return url


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

    @classmethod
    def validate_filename(cls, filename: str) -> str:
        """验证文件名"""
        filename = cls.not_empty(filename, "filename")

        # 检查危险字符
        for char in cls.DANGEROUS_CHARS:
            if char in filename:
                raise ValidationError(
                    f"Filename contains invalid character: {repr(char)}"
                )

        # 检查 Windows 保留名
        name_part = filename.split('.')[0].upper()
        if name_part in cls.WINDOWS_RESERVED:
            raise ValidationError(
                f"'{filename}' is a reserved filename on Windows"
            )

        return filename
```

### 2. 内容清理器

```python
# anyclaw/security/sanitizers.py

import re
from typing import Optional

class ContentSanitizer:
    """内容清理器"""

    # 危险 Unicode 字符
    DANGEROUS_UNICODE = [
        '\x00',  # NULL
        '\x1b',  # ESC
        '\u200b',  # 零宽空格
        '\u200c',  # 零宽非连接符
        '\u200d',  # 零宽连接符
        '\u200e',  # 从左到右标记
        '\u200f',  # 从右到左标记
        '\ufeff',  # BOM
    ]

    # 最大消息长度
    MAX_MESSAGE_LENGTH = 100_000

    @classmethod
    def sanitize_message(cls, content: str) -> str:
        """清理消息内容"""
        if not content:
            raise ValueError("Message cannot be empty")

        # 移除危险 Unicode
        for char in cls.DANGEROUS_UNICODE:
            content = content.replace(char, '')

        # 移除控制字符（保留换行、制表符）
        content = re.sub(r'[\x00-\x08\x0b\x0c\x0e-\x1f\x7f]', '', content)

        # 标准化空白
        content = content.strip()

        if not content:
            raise ValueError("Message cannot be empty")

        # 截断超长消息
        if len(content) > cls.MAX_MESSAGE_LENGTH:
            content = content[:cls.MAX_MESSAGE_LENGTH]
            # 记录警告

        return content

    @classmethod
    def sanitize_command(cls, command: str) -> str:
        """清理命令（保留原始内容，仅记录风险）"""
        # 不修改命令，只返回原始值
        # 安全检查由 SSRFGuard 和 PathGuard 负责
        return command.strip()
```

### 3. 工具参数验证装饰器

```python
# anyclaw/tools/decorators.py

from functools import wraps
from typing import Dict, Any

def validate_params(**validators):
    """
    参数验证装饰器

    Usage:
        @validate_params(
            path=PathValidator.validate,
            timeout=lambda x: Validator.in_range(x, 1, 300)
        )
        async def execute(self, path, timeout, **kwargs):
            ...
    """
    def decorator(func):
        @wraps(func)
        async def wrapper(self, *args, **kwargs):
            for param_name, validator in validators.items():
                if param_name in kwargs:
                    try:
                        kwargs[param_name] = validator(kwargs[param_name])
                    except ValidationError as e:
                        return f"Error: {e}"
            return await func(self, *args, **kwargs)
        return wrapper
    return decorator
```

## 影响范围

- `anyclaw/security/validators.py` - 验证器模块
- `anyclaw/security/sanitizers.py` - 清理器模块
- `anyclaw/tools/decorators.py` - 验证装饰器
- `anyclaw/agent/context.py` - 消息清理集成
- `tests/test_validators.py` - 测试文件
- `tests/test_sanitizers.py` - 测试文件

## 验收标准

- [ ] 空消息被正确处理
- [ ] 超长消息被截断
- [ ] 危险 Unicode 字符被移除
- [ ] 工具参数格式验证
- [ ] 数值范围验证
- [ ] URL 协议验证
- [ ] 文件名安全性验证
- [ ] 测试覆盖率 > 85%
