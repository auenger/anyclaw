# SSRF 防护系统

## 背景

AnyClaw 当前完全没有 SSRF（Server-Side Request Forgery）防护。Agent 可以通过 WebFetch、WebSearch 等工具访问任意 URL，包括：
- 内部网络服务（192.168.x.x, 10.x.x.x）
- 本地服务（127.0.0.1, localhost）
- 云元数据端点（169.254.169.254）
- 私有 IPv6 地址

**风险**: Agent 可能被诱导访问内部服务获取敏感信息，或访问云元数据获取 API 密钥。

## 需求

实现完整的 SSRF 防护系统，阻止对内部网络和私有地址的访问。

## 用户价值点

### VP1: 私有网络访问拦截

阻止对 RFC 1918 私有网络和特殊用途地址的访问。

**Gherkin 场景**:

```gherkin
Feature: 私有网络访问拦截

  Scenario: 阻止访问 A 类私有网络
    Given URL 为 "http://10.0.0.1/admin"
    When 检查 URL 安全性
    Then 返回错误 "Access to private network blocked"

  Scenario: 阻止访问 B 类私有网络
    Given URL 为 "http://172.16.0.1/internal"
    When 检查 URL 安全性
    Then 返回错误 "Access to private network blocked"

  Scenario: 阻止访问 C 类私有网络
    Given URL 为 "http://192.168.1.1/router"
    When 检查 URL 安全性
    Then 返回错误 "Access to private network blocked"

  Scenario: 阻止访问本地环回地址
    Given URL 为 "http://127.0.0.1:8080/api"
    When 检查 URL 安全性
    Then 返回错误 "Access to loopback address blocked"

  Scenario: 阻止访问云元数据端点
    Given URL 为 "http://169.254.169.254/latest/meta-data/"
    When 检查 URL 安全性
    Then 返回错误 "Access to link-local address blocked"

  Scenario: 阻止访问 IPv6 本地地址
    Given URL 为 "http://[::1]:8080/admin"
    When 检查 URL 安全性
    Then 返回错误 "Access to IPv6 loopback blocked"
```

### VP2: DNS 重绑定攻击防护

防止通过 DNS 解析到私有 IP 绕过检查。

**Gherkin 场景**:

```gherkin
Feature: DNS 重绑定防护

  Scenario: 解析后检查目标 IP
    Given URL 为 "http://internal.example.com"
    And DNS 解析结果为 "10.0.0.1"
    When 检查 URL 安全性
    Then 返回错误 "DNS resolved to private IP"

  Scenario: 支持配置允许的私有域名
    Given 配置 allowed_private_domains = ["internal.mycompany.com"]
    And URL 为 "http://internal.mycompany.com"
    When 检查 URL 安全性
    Then 允许访问
```

### VP3: 可配置的豁免列表

允许管理员配置需要访问的内部服务白名单。

**Gherkin 场景**:

```gherkin
Feature: 豁免列表配置

  Scenario: 配置允许的私有 IP 段
    Given 配置 allowed_networks = ["192.168.1.0/24"]
    And URL 为 "http://192.168.1.100:8080/api"
    When 检查 URL 安全性
    Then 允许访问

  Scenario: 配置允许的内部域名
    Given 配置 allowed_private_domains = ["internal.company.com"]
    And URL 为 "http://internal.company.com"
    When 检查 URL 安全性
    Then 允许访问
```

## 技术方案

### 1. 网络安全模块

```python
# anyclaw/security/network.py

import ipaddress
from typing import Optional
from urllib.parse import urlparse
import socket

# 默认阻止的网络
DEFAULT_BLOCKED_NETWORKS = [
    ipaddress.ip_network("0.0.0.0/8"),       # 当前网络
    ipaddress.ip_network("10.0.0.0/8"),      # A 类私有
    ipaddress.ip_network("100.64.0.0/10"),   # 运营商级 NAT
    ipaddress.ip_network("127.0.0.0/8"),     # 本地环回
    ipaddress.ip_network("169.254.0.0/16"),  # 链路本地 / 云元数据
    ipaddress.ip_network("172.16.0.0/12"),   # B 类私有
    ipaddress.ip_network("192.168.0.0/16"),  # C 类私有
    ipaddress.ip_network("224.0.0.0/4"),     # 多播
    ipaddress.ip_network("240.0.0.0/4"),     # 保留
    ipaddress.ip_network("::1/128"),         # IPv6 环回
    ipaddress.ip_network("fc00::/7"),        # IPv6 ULA
    ipaddress.ip_network("fe80::/10"),       # IPv6 链路本地
]

class SSRFGuard:
    def __init__(
        self,
        blocked_networks: list = None,
        allowed_networks: list = None,
        allowed_private_domains: list = None,
    ):
        self.blocked_networks = blocked_networks or DEFAULT_BLOCKED_NETWORKS
        self.allowed_networks = [
            ipaddress.ip_network(n) for n in (allowed_networks or [])
        ]
        self.allowed_private_domains = set(allowed_private_domains or [])

    def check_url(self, url: str) -> tuple[bool, str]:
        """检查 URL 是否安全，返回 (is_safe, error_message)"""
        parsed = urlparse(url)
        hostname = parsed.hostname

        if not hostname:
            return False, "Invalid URL: no hostname"

        # 检查是否在允许的私有域名列表
        if hostname in self.allowed_private_domains:
            return True, ""

        # 解析 IP
        try:
            # 先尝试直接解析为 IP
            ip = ipaddress.ip_address(hostname)
        except ValueError:
            # 不是 IP，需要 DNS 解析
            try:
                ip_str = socket.gethostbyname(hostname)
                ip = ipaddress.ip_address(ip_str)
            except socket.gaierror:
                return False, f"Cannot resolve hostname: {hostname}"

        # 检查是否在阻止列表
        for network in self.blocked_networks:
            if ip in network:
                # 检查是否在允许列表
                for allowed_net in self.allowed_networks:
                    if ip in allowed_net:
                        return True, ""
                return False, f"Access to private network blocked: {ip}"

        return True, ""

    def is_internal_url(self, url: str) -> bool:
        """检查是否为内部 URL（用于工具调用前检查）"""
        is_safe, _ = self.check_url(url)
        return not is_safe
```

### 2. 配置扩展

```json
// ~/.anyclaw/config.json
{
  "security": {
    "ssrf": {
      "enabled": true,
      "allowed_networks": ["192.168.1.0/24"],
      "allowed_private_domains": ["internal.company.com"]
    }
  }
}
```

### 3. 工具集成

```python
# anyclaw/tools/web.py (或类似文件)

class WebFetchTool(Tool):
    def __init__(self, ssrf_guard: SSRFGuard = None):
        self.ssrf_guard = ssrf_guard or SSRFGuard()

    async def execute(self, url: str, **kwargs) -> str:
        # SSRF 检查
        is_safe, error = self.ssrf_guard.check_url(url)
        if not is_safe:
            return f"Error: {error}"

        # 正常执行...
```

## 影响范围

- `anyclaw/security/__init__.py` - 新建安全模块
- `anyclaw/security/network.py` - SSRF 防护核心
- `anyclaw/config/settings.py` - 添加 ssrf 配置项
- `anyclaw/tools/` - 集成到 WebFetch/WebSearch 工具
- `tests/test_ssrf_guard.py` - 测试文件

## 验收标准

- [ ] 阻止所有 RFC 1918 私有网络访问
- [ ] 阻止本地环回地址 (127.0.0.1, ::1)
- [ ] 阻止云元数据端点 (169.254.169.254)
- [ ] DNS 解析后检查目标 IP
- [ ] 支持配置允许的私有 IP 段
- [ ] 支持配置允许的私有域名
- [ ] 测试覆盖率 > 90%
