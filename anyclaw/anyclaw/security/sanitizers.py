"""内容清理器模块

提供输入内容清理功能：
- 消息内容清理
- 危险 Unicode 移除
- 控制字符过滤
- 消息长度限制
"""

import logging
import re
from typing import Optional, Set

logger = logging.getLogger(__name__)


class ContentSanitizer:
    """内容清理器"""

    # 危险 Unicode 字符
    DANGEROUS_UNICODE: Set[str] = {
        '\x00',      # NULL
        '\x01',      # SOH
        '\x02',      # STX
        '\x03',      # ETX
        '\x04',      # EOT
        '\x05',      # ENQ
        '\x06',      # ACK
        '\x07',      # BEL
        '\x08',      # BS
        '\x0b',      # VT
        '\x0c',      # FF
        '\x0e',      # SO
        '\x0f',      # SI
        '\x10',      # DLE
        '\x11',      # DC1
        '\x12',      # DC2
        '\x13',      # DC3
        '\x14',      # DC4
        '\x15',      # NAK
        '\x16',      # SYN
        '\x17',      # ETB
        '\x18',      # CAN
        '\x19',      # EM
        '\x1a',      # SUB
        '\x1b',      # ESC
        '\x1c',      # FS
        '\x1d',      # GS
        '\x1e',      # RS
        '\x1f',      # US
        '\x7f',      # DEL
        '\u200b',    # 零宽空格 (ZWSP)
        '\u200c',    # 零宽非连接符 (ZWNJ)
        '\u200d',    # 零宽连接符 (ZWJ)
        '\u200e',    # 从左到右标记 (LRM)
        '\u200f',    # 从右到左标记 (RLM)
        '\ufeff',    # BOM (Byte Order Mark)
        '\u2060',    # 字连接符 (WJ)
        '\u2061',    # 函数应用
        '\u2062',    # 不可见乘号
        '\u2063',    # 不可见逗号
        '\u2064',    # 不可见加号
        '\u206a',    # 抑制对称交换
        '\u206b',    # 激活对称交换
        '\u206c',    # 抑制阿拉伯成形
        '\u206d',    # 激活阿拉伯成形
        '\u206e',    # 数字形状
        '\u206f',    # 数字形状
    }

    # 控制字符正则（保留换行和制表符）
    CONTROL_CHARS_PATTERN = re.compile(r'[\x00-\x08\x0b\x0c\x0e-\x1f\x7f]')

    # 最大消息长度（字符数）
    MAX_MESSAGE_LENGTH = 100_000

    # 最大命令长度
    MAX_COMMAND_LENGTH = 10_000

    @classmethod
    def sanitize_message(
        cls,
        content: str,
        max_length: Optional[int] = None,
        truncate: bool = True
    ) -> str:
        """
        清理消息内容

        Args:
            content: 原始消息内容
            max_length: 最大长度（默认使用 MAX_MESSAGE_LENGTH）
            truncate: 是否截断超长消息（False 则抛出异常）

        Returns:
            清理后的消息

        Raises:
            ValueError: 消息为空或超过长度限制（truncate=False 时）
        """
        if not content:
            raise ValueError("Message cannot be empty")

        # 移除危险 Unicode 字符
        for char in cls.DANGEROUS_UNICODE:
            content = content.replace(char, '')

        # 移除控制字符（保留换行 \n 和制表符 \t）
        content = cls.CONTROL_CHARS_PATTERN.sub('', content)

        # 标准化空白
        content = content.strip()

        if not content:
            raise ValueError("Message cannot be empty")

        # 检查/截断长度
        max_len = max_length or cls.MAX_MESSAGE_LENGTH
        if len(content) > max_len:
            if truncate:
                original_len = len(content)
                content = content[:max_len]
                logger.warning(
                    f"Message truncated from {original_len} to {max_len} chars"
                )
            else:
                raise ValueError(
                    f"Message exceeds maximum length ({max_len} chars)"
                )

        return content

    @classmethod
    def sanitize_command(
        cls,
        command: str,
        max_length: Optional[int] = None
    ) -> str:
        """
        清理命令内容

        注意：此方法只进行基本清理，不做安全检查。
        安全检查由 SSRFGuard 和 ExecGuard 负责。

        Args:
            command: 原始命令
            max_length: 最大长度

        Returns:
            清理后的命令

        Raises:
            ValueError: 命令为空或超过长度限制
        """
        if not command:
            raise ValueError("Command cannot be empty")

        # 只做基本清理
        command = command.strip()

        if not command:
            raise ValueError("Command cannot be empty")

        # 检查长度
        max_len = max_length or cls.MAX_COMMAND_LENGTH
        if len(command) > max_len:
            raise ValueError(
                f"Command exceeds maximum length ({max_len} chars)"
            )

        return command

    @classmethod
    def sanitize_tool_output(
        cls,
        output: str,
        max_length: Optional[int] = None
    ) -> str:
        """
        清理工具输出

        Args:
            output: 工具输出
            max_length: 最大长度

        Returns:
            清理后的输出
        """
        if not output:
            return ""

        # 移除危险 Unicode
        for char in cls.DANGEROUS_UNICODE:
            output = output.replace(char, '')

        # 截断超长输出
        max_len = max_length or cls.MAX_MESSAGE_LENGTH
        if len(output) > max_len:
            output = output[:max_len] + "\n... (output truncated)"

        return output

    @classmethod
    def remove_zero_width_chars(cls, text: str) -> str:
        """
        移除零宽字符

        Args:
            text: 输入文本

        Returns:
            清理后的文本
        """
        zero_width_chars = {
            '\u200b',  # ZWSP
            '\u200c',  # ZWNJ
            '\u200d',  # ZWJ
            '\u200e',  # LRM
            '\u200f',  # RLM
            '\ufeff',  # BOM
            '\u2060',  # WJ
        }

        for char in zero_width_chars:
            text = text.replace(char, '')

        return text

    @classmethod
    def normalize_whitespace(cls, text: str) -> str:
        """
        标准化空白字符

        - 移除首尾空白
        - 将多个连续空格压缩为一个
        - 保留换行符

        Args:
            text: 输入文本

        Returns:
            标准化后的文本
        """
        # 压缩多个空格为一个（保留换行）
        lines = text.split('\n')
        lines = [' '.join(line.split()) for line in lines]
        return '\n'.join(lines).strip()

    @classmethod
    def is_safe_content(cls, content: str) -> bool:
        """
        检查内容是否安全（不抛出异常）

        Args:
            content: 内容

        Returns:
            是否安全
        """
        try:
            cls.sanitize_message(content)
            return True
        except ValueError:
            return False


# 便捷函数
def sanitize_message(content: str, max_length: Optional[int] = None) -> str:
    """清理消息内容（便捷函数）"""
    return ContentSanitizer.sanitize_message(content, max_length)


def sanitize_command(command: str) -> str:
    """清理命令（便捷函数）"""
    return ContentSanitizer.sanitize_command(command)


def sanitize_tool_output(output: str) -> str:
    """清理工具输出（便捷函数）"""
    return ContentSanitizer.sanitize_tool_output(output)
