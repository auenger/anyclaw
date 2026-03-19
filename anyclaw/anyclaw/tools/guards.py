"""ExecTool 安全保护模块

实现混合模式安全限制：
- 核心保护层：硬编码的、不可绕过的危险命令拦截
- 扩展保护层：用户可通过配置自定义 deny/allow patterns
"""

import re
from typing import List, Optional, Tuple


# =============================================================================
# 核心保护模式（不可配置关闭）
# =============================================================================

CORE_DENY_PATTERNS = [
    # -------------------------------------------------------------------------
    # Unix 删除命令
    # -------------------------------------------------------------------------
    # rm -rf / rm -fr / rm -r -f 等变体
    (r"\brm\s+(-[rf]{1,2}\b|-[a-z]*r[a-z]*f[a-z]*\b)", "Unix 递归强制删除"),

    # -------------------------------------------------------------------------
    # Windows 删除命令
    # -------------------------------------------------------------------------
    # del /f / del /q / del /s 等
    (r"\bdel\s+/[sfaq]\b", "Windows 强制删除"),
    # rmdir /s / rmdir /q
    (r"\brmdir\s+/[sq]\b", "Windows 递归删除目录"),
    # rd /s / rd /q
    (r"\brd\s+/[sq]\b", "Windows 递归删除目录"),

    # -------------------------------------------------------------------------
    # 磁盘操作命令
    # -------------------------------------------------------------------------
    # dd if=/dev/zero of=/dev/sda
    (r"\bdd\s+if=", "磁盘写入 (dd)"),
    # 直接写入 /dev/sd* 或 /dev/hd*
    (r">\s*/dev/[sh]d[a-z]", "直接写入磁盘设备"),
    # mkfs 系列
    (r"\bmkfs(?:\.[a-z0-9]+)?\b", "格式化文件系统"),
    # diskpart (Windows)
    (r"\bdiskpart\b", "Windows 磁盘分区工具"),
    # format 命令 (Windows)
    (r"(?:^|[;&|]\s*)format\s+[a-zA-Z]:", "Windows 格式化磁盘"),

    # -------------------------------------------------------------------------
    # 系统电源命令
    # -------------------------------------------------------------------------
    (r"\b(shutdown|reboot|poweroff|halt|init\s+[06])\b", "系统关机/重启"),

    # -------------------------------------------------------------------------
    # Fork bomb
    # -------------------------------------------------------------------------
    # :(){ :|:& };:
    (r":\(\)\s*\{[^}]*\};\s*:", "Fork bomb"),
    # 变体
    (r"\.\s*\(\s*\)\s*\{[^}]*\}\s*;\s*\.", "Fork bomb 变体"),

    # -------------------------------------------------------------------------
    # 权限提升
    # -------------------------------------------------------------------------
    # chmod 777 / chmod -R 777
    (r"\bchmod\s+(-R\s+)?777\b", "危险权限设置 (777)"),
    # chown 修改系统文件
    (r"\bchown\s+.*\s+/(?:etc|usr|bin|sbin|lib)\b", "修改系统文件所有权"),

    # -------------------------------------------------------------------------
    # 网络危险命令
    # -------------------------------------------------------------------------
    # iptables flush
    (r"\biptables\s+-F\b", "清空防火墙规则"),
    # 危险的网络配置
    (r"\bifconfig\s+\w+\s+down\b", "关闭网络接口"),

    # -------------------------------------------------------------------------
    # 系统关键文件修改
    # -------------------------------------------------------------------------
    # 直接写入 /etc/passwd 或 /etc/shadow
    (r">\s*/etc/(?:passwd|shadow|sudoers)\b", "修改系统认证文件"),
    # 追加写入
    (r">>\s*/etc/(?:passwd|shadow|sudoers)\b", "修改系统认证文件"),
]

# 编译核心保护正则表达式
CORE_DENY_COMPILED = [
    (re.compile(pattern, re.IGNORECASE), description)
    for pattern, description in CORE_DENY_PATTERNS
]


class CoreGuard:
    """核心安全保护器

    提供不可绕过的危险命令拦截功能。
    """

    @staticmethod
    def check(command: str) -> Tuple[bool, Optional[str]]:
        """检查命令是否被核心保护阻止

        Args:
            command: 要检查的命令字符串

        Returns:
            Tuple[bool, Optional[str]]: (是否被阻止, 阻止原因)
        """
        cmd = command.strip()

        for pattern, description in CORE_DENY_COMPILED:
            if pattern.search(cmd):
                return True, f"核心安全策略阻止 ({description})"

        return False, None

    @staticmethod
    def get_patterns() -> List[Tuple[str, str]]:
        """获取所有核心保护模式

        Returns:
            List of (pattern, description) tuples
        """
        return [(p, d) for p, d in CORE_DENY_PATTERNS]


class UserGuard:
    """用户自定义安全保护器

    支持用户通过配置添加额外的 deny/allow 规则。
    """

    def __init__(
        self,
        deny_patterns: Optional[List[str]] = None,
        allow_patterns: Optional[List[str]] = None,
    ):
        """初始化用户保护器

        Args:
            deny_patterns: 用户自定义的黑名单模式
            allow_patterns: 用户自定义的白名单模式（启用后只允许匹配的命令）
        """
        self.deny_patterns = [
            re.compile(p, re.IGNORECASE) for p in (deny_patterns or [])
        ]
        self.allow_patterns = [
            re.compile(p) for p in (allow_patterns or [])
        ]
        self.allow_mode = bool(allow_patterns)

    def check(self, command: str) -> Tuple[bool, Optional[str]]:
        """检查命令是否被用户规则阻止

        Args:
            command: 要检查的命令字符串

        Returns:
            Tuple[bool, Optional[str]]: (是否被阻止, 阻止原因)
        """
        cmd = command.strip()

        # 1. 检查用户 deny_patterns
        for pattern in self.deny_patterns:
            if pattern.search(cmd):
                return True, "用户安全策略阻止"

        # 2. 如果启用白名单模式，检查命令是否在白名单中
        if self.allow_mode:
            allowed = any(pattern.search(cmd) for pattern in self.allow_patterns)
            if not allowed:
                return True, "命令不在允许列表中"

        return False, None

    def get_deny_patterns(self) -> List[str]:
        """获取用户 deny 模式列表"""
        return [p.pattern for p in self.deny_patterns]

    def get_allow_patterns(self) -> List[str]:
        """获取用户 allow 模式列表"""
        return [p.pattern for p in self.allow_patterns]


class CommandGuard:
    """命令安全保护器（组合核心保护 + 用户保护）

    检查优先级：
    1. 核心保护（最高优先级，不可绕过）
    2. 用户 deny_patterns
    3. 用户 allow_patterns（如果启用）
    """

    def __init__(
        self,
        user_deny_patterns: Optional[List[str]] = None,
        user_allow_patterns: Optional[List[str]] = None,
    ):
        """初始化命令保护器

        Args:
            user_deny_patterns: 用户自定义的黑名单模式
            user_allow_patterns: 用户自定义的白名单模式
        """
        self.core_guard = CoreGuard()
        self.user_guard = UserGuard(
            deny_patterns=user_deny_patterns,
            allow_patterns=user_allow_patterns,
        )

    def check(self, command: str) -> Tuple[bool, Optional[str]]:
        """检查命令是否被阻止

        Args:
            command: 要检查的命令字符串

        Returns:
            Tuple[bool, Optional[str]]: (是否被阻止, 阻止原因)
        """
        # 1. 核心保护检查（最高优先级）
        blocked, reason = self.core_guard.check(command)
        if blocked:
            return True, f"[CoreGuard] {reason}"

        # 2. 用户保护检查
        blocked, reason = self.user_guard.check(command)
        if blocked:
            return True, f"[UserGuard] {reason}"

        return False, None

    def is_allowed(self, command: str) -> bool:
        """检查命令是否被允许

        Args:
            command: 要检查的命令字符串

        Returns:
            bool: True 表示允许执行
        """
        blocked, _ = self.check(command)
        return not blocked

    def get_all_rules(self) -> dict:
        """获取所有安全规则

        Returns:
            dict: 包含核心规则和用户规则的字典
        """
        return {
            "core": {
                "patterns": [
                    {"pattern": p, "description": d, "source": "core"}
                    for p, d in self.core_guard.get_patterns()
                ],
            },
            "user": {
                "deny_patterns": self.user_guard.get_deny_patterns(),
                "allow_patterns": self.user_guard.get_allow_patterns(),
                "allow_mode": self.user_guard.allow_mode,
            },
        }
