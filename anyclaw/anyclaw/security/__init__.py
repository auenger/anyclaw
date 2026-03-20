"""AnyClaw 安全模块

提供各种安全防护功能：
- SSRF 防护 (SSRFGuard)
- 凭证安全管理 (CredentialManager)
- 日志敏感数据过滤 (SensitiveDataFilter)
- 输入验证器 (Validator, URLValidator, PathValidator)
- 内容清理器 (ContentSanitizer)
- 路径遍历防护 (PathGuard)
"""

from anyclaw.security.network import SSRFGuard
from anyclaw.security.credentials import (
    CredentialManager,
    CredentialMetadata,
    SensitiveDataFilter,
    get_credential_manager,
    mask_sensitive,
)
from anyclaw.security.validators import (
    ValidationError,
    Validator,
    URLValidator,
    PathValidator,
    validate_url,
    validate_path,
    validate_filename,
)
from anyclaw.security.sanitizers import (
    ContentSanitizer,
    sanitize_message,
    sanitize_command,
    sanitize_tool_output,
)
from anyclaw.security.path import (
    PathGuard,
    PathSecurityError,
    create_path_guard_from_settings,
)

__all__ = [
    # Network
    "SSRFGuard",
    # Credentials
    "CredentialManager",
    "CredentialMetadata",
    "SensitiveDataFilter",
    "get_credential_manager",
    "mask_sensitive",
    # Validators
    "ValidationError",
    "Validator",
    "URLValidator",
    "PathValidator",
    "validate_url",
    "validate_path",
    "validate_filename",
    # Sanitizers
    "ContentSanitizer",
    "sanitize_message",
    "sanitize_command",
    "sanitize_tool_output",
    # Path Security
    "PathGuard",
    "PathSecurityError",
    "create_path_guard_from_settings",
]
