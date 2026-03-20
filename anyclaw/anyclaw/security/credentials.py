"""凭证安全管理模块

提供 API Key 等敏感信息的安全管理：
- 加密存储（基于机器标识）
- 日志脱敏
- 配置显示脱敏
- 凭证格式验证
"""

from __future__ import annotations

import base64
import hashlib
import json
import os
import platform
import re
import subprocess
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, List, Optional, Tuple

from pydantic import BaseModel


class CredentialMetadata(BaseModel):
    """凭证元数据"""

    key_name: str
    created_at: Optional[str] = None
    expires_at: Optional[str] = None
    last_used: Optional[str] = None


class CredentialManager:
    """凭证安全管理器

    功能：
    - 加密存储敏感凭证
    - 脱敏显示敏感信息
    - 凭证格式验证
    - 过期检测
    """

    # 敏感字段列表
    SENSITIVE_FIELDS = [
        "api_key",
        "secret_key",
        "access_token",
        "password",
        "credential",
        "private_key",
        "app_secret",
        "encrypt_key",
        "verification_token",
        "token",
    ]

    # 脱敏模式：匹配常见 API Key 格式
    MASK_PATTERNS = [
        # OpenAI style: sk-xxxx...
        (r"sk-[a-zA-Z0-9]{20,}", lambda m: f"sk-***{m.group(0)[-4:]}"),
        # OpenAI project key: sk-proj-xxxx...
        (r"sk-proj-[a-zA-Z0-9]{20,}", lambda m: f"sk-proj-***{m.group(0)[-4:]}"),
        # GitHub PAT: ghp_xxxx
        (r"ghp_[a-zA-Z0-9]{36}", lambda m: "ghp_***"),
        # AWS Access Key: AKIAxxxx
        (r"AKIA[A-Z0-9]{16}", lambda m: "AKI***"),
        # Anthropic API Key: sk-ant-xxxx
        (r"sk-ant-[a-zA-Z0-9\-]{20,}", lambda m: f"sk-ant-***{m.group(0)[-4:]}"),
        # Generic secret patterns (at least 20 chars after prefix)
        (r"(api[_-]?key|secret|token|password)[=:]\s*[\"']?([a-zA-Z0-9_\-]{20,})[\"']?",
         lambda m: f"{m.group(1)}=***"),
    ]

    # API Key 格式验证规则
    FORMAT_RULES = {
        "openai": (r"^sk-[a-zA-Z0-9]{20,}$", "OpenAI API Key 格式应为 sk-xxx（至少 20 字符）"),
        "anthropic": (r"^sk-ant-[a-zA-Z0-9\-]{20,}$", "Anthropic API Key 格式应为 sk-ant-xxx"),
        "zai": (r"^[a-zA-Z0-9\-_]{20,}$", "ZAI API Key 格式应为至少 20 字符"),
        "github": (r"^ghp_[a-zA-Z0-9]{36}$", "GitHub PAT 格式应为 ghp_xxx（36 字符）"),
        "aws": (r"^AKIA[A-Z0-9]{16}$", "AWS Access Key 格式应为 AKIAxxx（20 字符）"),
    }

    def __init__(
        self,
        config_dir: Optional[Path] = None,
        use_keyring: bool = False,
    ):
        """初始化凭证管理器

        Args:
            config_dir: 配置目录，默认 ~/.anyclaw
            use_keyring: 是否使用系统密钥链（需要 keyring 包）
        """
        self.config_dir = config_dir or Path.home() / ".anyclaw"
        self.credentials_file = self.config_dir / "credentials.enc"
        self.metadata_file = self.config_dir / "credentials_meta.json"
        self.use_keyring = use_keyring
        self._cipher = None
        self._metadata: Dict[str, CredentialMetadata] = {}

        # 确保目录存在
        self.config_dir.mkdir(parents=True, exist_ok=True)

        # 加载元数据
        self._load_metadata()

    def _get_machine_id(self) -> str:
        """获取机器唯一标识

        用于生成加密密钥的基础。
        支持 Linux、macOS、Windows。
        """
        machine_id = None

        # Linux: /etc/machine-id
        if os.path.exists("/etc/machine-id"):
            try:
                with open("/etc/machine-id", "r") as f:
                    machine_id = f.read().strip()
            except Exception:
                pass

        # macOS: IOPlatformUUID
        if not machine_id and platform.system() == "Darwin":
            try:
                result = subprocess.run(
                    ["ioreg", "-rd1", "-c", "IOPlatformExpertDevice"],
                    capture_output=True,
                    text=True,
                    timeout=5,
                )
                for line in result.stdout.split("\n"):
                    if "IOPlatformUUID" in line:
                        machine_id = line.split('"')[-2]
                        break
            except Exception:
                pass

        # Windows: MachineGuid
        if not machine_id and platform.system() == "Windows":
            try:
                import winreg

                with winreg.OpenKey(
                    winreg.HKEY_LOCAL_MACHINE,
                    r"SOFTWARE\Microsoft\Cryptography",
                ) as key:
                    machine_id, _ = winreg.QueryValueEx(key, "MachineGuid")
            except Exception:
                pass

        # Fallback: hostname + username hash
        if not machine_id:
            fallback = f"{platform.node()}-{os.getlogin()}-{platform.system()}"
            machine_id = hashlib.sha256(fallback.encode()).hexdigest()

        return machine_id

    def _get_cipher(self):
        """获取加密器（基于机器标识生成密钥）"""
        if self._cipher is not None:
            return self._cipher

        try:
            from cryptography.fernet import Fernet
            from cryptography.hazmat.primitives import hashes
            from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC

            # 使用机器标识作为密钥基础
            machine_id = self._get_machine_id()
            salt = b"anyclaw_credentials_v1"

            kdf = PBKDF2HMAC(
                algorithm=hashes.SHA256(),
                length=32,
                salt=salt,
                iterations=100000,
            )
            key = base64.urlsafe_b64encode(kdf.derive(machine_id.encode()))
            self._cipher = Fernet(key)
            return self._cipher
        except ImportError:
            # 如果 cryptography 不可用，返回 None（不加密）
            return None

    def store(self, key: str, value: str, expires_days: Optional[int] = None) -> None:
        """安全存储凭证

        Args:
            key: 凭证名称（如 "openai.api_key"）
            value: 凭证值
            expires_days: 过期天数（可选）
        """
        cipher = self._get_cipher()

        # 加载现有凭证
        credentials = self._load_encrypted()

        # 存储凭证
        if cipher:
            credentials[key] = cipher.encrypt(value.encode()).decode()
        else:
            # Fallback: 不加密（警告用户）
            credentials[key] = value

        # 保存
        self._save_encrypted(credentials)

        # 更新元数据
        now = datetime.now().isoformat()
        expires_at = None
        if expires_days:
            expires_at = (datetime.now() + timedelta(days=expires_days)).isoformat()

        self._metadata[key] = CredentialMetadata(
            key_name=key,
            created_at=now,
            expires_at=expires_at,
        )
        self._save_metadata()

    def retrieve(self, key: str) -> Optional[str]:
        """读取凭证

        Args:
            key: 凭证名称

        Returns:
            凭证值，不存在返回 None
        """
        # 更新最后使用时间
        if key in self._metadata:
            self._metadata[key].last_used = datetime.now().isoformat()
            self._save_metadata()

        cipher = self._get_cipher()
        credentials = self._load_encrypted()

        if key not in credentials:
            return None

        value = credentials[key]
        if cipher and value:
            try:
                return cipher.decrypt(value.encode()).decode()
            except Exception:
                # 解密失败，可能是明文存储的旧数据
                return value
        return value

    def delete(self, key: str) -> bool:
        """删除凭证

        Args:
            key: 凭证名称

        Returns:
            是否删除成功
        """
        credentials = self._load_encrypted()
        if key in credentials:
            del credentials[key]
            self._save_encrypted(credentials)
            if key in self._metadata:
                del self._metadata[key]
                self._save_metadata()
            return True
        return False

    def list_credentials(self) -> List[str]:
        """列出所有凭证名称"""
        return list(self._load_encrypted().keys())

    def _load_encrypted(self) -> Dict[str, str]:
        """加载加密的凭证文件"""
        if not self.credentials_file.exists():
            return {}
        try:
            with open(self.credentials_file, "r", encoding="utf-8") as f:
                return json.load(f)
        except Exception:
            return {}

    def _save_encrypted(self, credentials: Dict[str, str]) -> None:
        """保存加密的凭证文件"""
        with open(self.credentials_file, "w", encoding="utf-8") as f:
            json.dump(credentials, f, indent=2)
        # 设置文件权限（仅所有者可读写）
        os.chmod(self.credentials_file, 0o600)

    def _load_metadata(self) -> None:
        """加载凭证元数据"""
        if not self.metadata_file.exists():
            return
        try:
            with open(self.metadata_file, "r", encoding="utf-8") as f:
                data = json.load(f)
                self._metadata = {
                    k: CredentialMetadata(**v) for k, v in data.items()
                }
        except Exception:
            self._metadata = {}

    def _save_metadata(self) -> None:
        """保存凭证元数据"""
        data = {k: v.model_dump() for k, v in self._metadata.items()}
        with open(self.metadata_file, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=2)

    # ========== 脱敏功能 ==========

    def mask(self, text: str) -> str:
        """脱敏文本中的敏感信息

        Args:
            text: 原始文本

        Returns:
            脱敏后的文本
        """
        result = text
        for pattern, replacement in self.MASK_PATTERNS:
            if callable(replacement):
                result = re.sub(pattern, replacement, result)
            else:
                result = re.sub(pattern, replacement, result)
        return result

    def mask_value(self, value: str, visible_chars: int = 4) -> str:
        """脱敏单个值

        Args:
            value: 原始值
            visible_chars: 可见的末尾字符数

        Returns:
            脱敏后的值，如 "sk-***1234"
        """
        if not value or len(value) <= visible_chars:
            return "***"

        return f"***{value[-visible_chars:]}"

    def is_sensitive_field(self, field_name: str) -> bool:
        """检查字段名是否为敏感字段

        Args:
            field_name: 字段名

        Returns:
            是否为敏感字段
        """
        field_lower = field_name.lower()
        return any(sensitive in field_lower for sensitive in self.SENSITIVE_FIELDS)

    # ========== 凭证验证 ==========

    def validate_format(self, provider: str, api_key: str) -> Tuple[bool, Optional[str]]:
        """验证 API Key 格式

        Args:
            provider: Provider 名称
            api_key: API Key 值

        Returns:
            (是否有效, 错误消息)
        """
        if provider not in self.FORMAT_RULES:
            # 未知 provider，不验证格式
            return True, None

        pattern, error_msg = self.FORMAT_RULES[provider]
        if re.match(pattern, api_key):
            return True, None
        return False, error_msg

    def check_expiration(self, key: str) -> Tuple[bool, Optional[int]]:
        """检查凭证是否即将过期

        Args:
            key: 凭证名称

        Returns:
            (是否即将过期, 剩余天数)
        """
        if key not in self._metadata:
            return False, None

        meta = self._metadata[key]
        if not meta.expires_at:
            return False, None

        try:
            expires = datetime.fromisoformat(meta.expires_at)
            remaining = expires - datetime.now()
            days = remaining.days

            # 7 天内过期则警告
            if days <= 7:
                return True, max(0, days)
            return False, days
        except Exception:
            return False, None

    def get_expiration_warnings(self) -> List[Tuple[str, int]]:
        """获取所有即将过期的凭证警告

        Returns:
            [(凭证名称, 剩余天数), ...]
        """
        warnings = []
        for key in self.list_credentials():
            expiring, days = self.check_expiration(key)
            if expiring and days is not None:
                warnings.append((key, days))
        return warnings


class SensitiveDataFilter:
    """日志敏感数据过滤器

    用于过滤日志中的敏感信息。
    """

    def __init__(self, credential_manager: Optional[CredentialManager] = None):
        """初始化过滤器

        Args:
            credential_manager: 凭证管理器实例
        """
        self.manager = credential_manager or CredentialManager()

    def filter(self, record) -> bool:
        """过滤日志记录

        Args:
            record: 日志记录对象

        Returns:
            总是返回 True（允许记录），但会修改消息内容
        """
        # 脱敏消息
        if hasattr(record, "msg") and isinstance(record.msg, str):
            record.msg = self.manager.mask(record.msg)

        # 脱敏参数
        if hasattr(record, "args") and record.args:
            if isinstance(record.args, dict):
                record.args = {
                    k: self.manager.mask(str(v)) if isinstance(v, str) else v
                    for k, v in record.args.items()
                }
            elif isinstance(record.args, tuple):
                record.args = tuple(
                    self.manager.mask(str(arg)) if isinstance(arg, str) else arg
                    for arg in record.args
                )

        return True


# 全局实例（延迟初始化）
_credential_manager: Optional[CredentialManager] = None


def get_credential_manager() -> CredentialManager:
    """获取全局凭证管理器实例"""
    global _credential_manager
    if _credential_manager is None:
        _credential_manager = CredentialManager()
    return _credential_manager


def mask_sensitive(text: str) -> str:
    """脱敏敏感信息的便捷函数

    Args:
        text: 原始文本

    Returns:
        脱敏后的文本
    """
    return get_credential_manager().mask(text)
