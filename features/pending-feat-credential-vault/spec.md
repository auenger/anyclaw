# 凭证安全管理

## 背景

AnyClaw 当前将 API Key 等敏感凭证明文存储在 `~/.anyclaw/config.json` 中，存在以下风险：
- 配置文件被意外提交到 Git
- 日志中可能泄露敏感信息
- 多用户系统中的权限问题
- 缺乏凭证轮换机制

## 需求

实现安全的凭证管理系统，保护敏感信息不被泄露。

## 用户价值点

### VP1: 凭证加密存储

使用系统密钥链或加密存储敏感凭证。

**Gherkin 场景**:

```gherkin
Feature: 凭证加密存储

  Scenario: API Key 加密存储
    Given 用户设置 API Key "sk-xxx"
    When 配置保存到文件
    Then 文件中不包含明文 API Key
    And 重启后可正确读取

  Scenario: 使用系统密钥链（可选）
    Given 系统支持密钥链（macOS Keychain / Windows Credential Manager / Linux Secret Service）
    And 配置 use_keyring = true
    When 用户设置 API Key
    Then 凭证存储在系统密钥链中

  Scenario: 配置文件脱敏显示
    Given 配置中包含 API Key
    When 用户执行 "anyclaw config show"
    Then API Key 显示为 "sk-***xxx"（部分隐藏）
```

### VP2: 日志脱敏

防止敏感信息出现在日志中。

**Gherkin 场景**:

```gherkin
Feature: 日志脱敏

  Scenario: 自动脱敏 API Key
    Given 日志记录包含 "Using API Key: sk-proj-abc123"
    When 日志输出
    Then 显示为 "Using API Key: sk-***123"

  Scenario: 脱敏多种格式的密钥
    Given 日志包含多种密钥格式
    When 日志输出
    Then 所有密钥都被脱敏：
      | 原始值 | 脱敏后 |
      | sk-xxx... | sk-***... |
      | ghp_xxx | ghp_*** |
      | AKIAxxx | AKI*** |
```

### VP3: 凭证验证

在使用前验证凭证有效性。

**Gherkin 场景**:

```gherkin
Feature: 凭证验证

  Scenario: 验证 API Key 格式
    Given 用户设置 API Key "invalid-key"
    When 验证凭证
    Then 返回警告 "API Key format may be invalid"

  Scenario: 检测即将过期的凭证
    Given 凭证设置了过期时间
    And 距离过期还有 7 天
    When 启动应用
    Then 显示警告 "Credential will expire in 7 days"
```

## 技术方案

### 1. 凭证管理器

```python
# anyclaw/security/credentials.py

import os
import json
import base64
from pathlib import Path
from typing import Optional
from cryptography.fernet import Fernet
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC

class CredentialManager:
    """凭证安全管理器"""

    # 敏感字段列表
    SENSITIVE_FIELDS = [
        "api_key", "secret_key", "access_token",
        "password", "credential", "private_key",
    ]

    # 脱敏模式
    MASK_PATTERNS = [
        (r"sk-[a-zA-Z0-9]{20,}", r"sk-***\g<0>[-4:]"),  # OpenAI style
        (r"ghp_[a-zA-Z0-9]{36}", r"ghp_***"),           # GitHub PAT
        (r"AKIA[A-Z0-9]{16}", r"AKI***"),               # AWS Access Key
    ]

    def __init__(self, config_dir: Path = None, use_keyring: bool = False):
        self.config_dir = config_dir or Path.home() / ".anyclaw"
        self.credentials_file = self.config_dir / "credentials.enc"
        self.use_keyring = use_keyring
        self._cipher = None

    def store(self, key: str, value: str) -> None:
        """安全存储凭证"""
        if self.use_keyring:
            self._store_in_keyring(key, value)
        else:
            self._store_encrypted(key, value)

    def retrieve(self, key: str) -> Optional[str]:
        """读取凭证"""
        if self.use_keyring:
            return self._retrieve_from_keyring(key)
        return self._retrieve_encrypted(key)

    def mask(self, text: str) -> str:
        """脱敏文本中的敏感信息"""
        import re
        for pattern, replacement in self.MASK_PATTERNS:
            text = re.sub(pattern, replacement, text)
        return text

    def _get_cipher(self) -> Fernet:
        """获取加密器（基于机器标识生成密钥）"""
        if self._cipher is None:
            # 使用机器标识作为密钥基础
            machine_id = self._get_machine_id()
            kdf = PBKDF2HMAC(
                algorithm=hashes.SHA256(),
                length=32,
                salt=b"anyclaw_credentials",
                iterations=100000,
            )
            key = base64.urlsafe_b64encode(kdf.derive(machine_id.encode()))
            self._cipher = Fernet(key)
        return self._cipher

    def _get_machine_id(self) -> str:
        """获取机器唯一标识"""
        # 尝试读取 /etc/machine-id (Linux)
        # 或使用 system.uuid (macOS)
        # 或 fallback 到 hostname
        ...
```

### 2. 配置集成

```python
# anyclaw/config/settings.py

class SecuritySettings(BaseModel):
    credentials: CredentialSettings = CredentialSettings()

class CredentialSettings(BaseModel):
    encrypted_storage: bool = Field(default=True)
    use_keyring: bool = Field(default=False)
    mask_in_logs: bool = Field(default=True)
    validate_on_load: bool = Field(default=True)
```

### 3. 日志过滤器

```python
# anyclaw/utils/logging.py

class SensitiveDataFilter:
    """日志敏感数据过滤器"""

    def __init__(self, credential_manager: CredentialManager):
        self.credential_manager = credential_manager

    def filter(self, record):
        record.msg = self.credential_manager.mask(record.msg)
        return True
```

## 影响范围

- `anyclaw/security/credentials.py` - 凭证管理核心
- `anyclaw/config/settings.py` - 配置集成
- `anyclaw/utils/logging.py` - 日志脱敏
- `anyclaw/cli/app.py` - CLI 命令更新
- `tests/test_credentials.py` - 测试文件

## 验收标准

- [ ] API Key 不以明文存储在配置文件
- [ ] 支持系统密钥链存储（可选）
- [ ] `anyclaw config show` 脱敏显示敏感信息
- [ ] 日志自动脱敏敏感信息
- [ ] 支持凭证格式验证
- [ ] 测试覆盖率 > 80%
