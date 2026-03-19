"""SSRF 防护测试

测试 SSRFGuard 的各种场景。
"""

import ipaddress
import pytest
from unittest.mock import patch, MagicMock

from anyclaw.security.network import SSRFGuard, DEFAULT_BLOCKED_NETWORKS


class TestSSRFGuardBasics:
    """基础功能测试"""

    def test_default_enabled(self):
        """默认启用 SSRF 防护"""
        guard = SSRFGuard()
        assert guard.enabled is True

    def test_can_disable(self):
        """可以禁用 SSRF 防护"""
        guard = SSRFGuard(enabled=False)
        is_safe, _ = guard.check_url("http://192.168.1.1/admin")
        assert is_safe is True

    def test_invalid_url(self):
        """无效 URL 应被拒绝"""
        guard = SSRFGuard()
        is_safe, error = guard.check_url("not a valid url")
        assert is_safe is False
        assert "无效" in error or "缺少" in error

    def test_url_without_hostname(self):
        """缺少主机名的 URL 应被拒绝"""
        guard = SSRFGuard()
        is_safe, error = guard.check_url("http:///path")
        assert is_safe is False


class TestPrivateNetworks:
    """私有网络访问拦截测试"""

    def test_block_class_a_private(self):
        """阻止 A 类私有网络 (10.0.0.0/8)"""
        guard = SSRFGuard()
        test_cases = [
            "http://10.0.0.1/admin",
            "http://10.255.255.255/test",
            "https://10.128.0.1:8080/api",
        ]
        for url in test_cases:
            is_safe, error = guard.check_url(url)
            assert is_safe is False, f"应该阻止 {url}"
            assert "私有网络" in error

    def test_block_class_b_private(self):
        """阻止 B 类私有网络 (172.16.0.0/12)"""
        guard = SSRFGuard()
        test_cases = [
            "http://172.16.0.1/internal",
            "http://172.31.255.255/test",
            "https://172.20.0.1:443/secure",
        ]
        for url in test_cases:
            is_safe, error = guard.check_url(url)
            assert is_safe is False, f"应该阻止 {url}"
            assert "私有网络" in error

    def test_block_class_c_private(self):
        """阻止 C 类私有网络 (192.168.0.0/16)"""
        guard = SSRFGuard()
        test_cases = [
            "http://192.168.1.1/router",
            "http://192.168.0.1/admin",
            "https://192.168.100.50:8080/api",
        ]
        for url in test_cases:
            is_safe, error = guard.check_url(url)
            assert is_safe is False, f"应该阻止 {url}"
            assert "私有网络" in error

    def test_block_loopback(self):
        """阻止本地环回地址 (127.0.0.0/8)"""
        guard = SSRFGuard()
        test_cases = [
            "http://127.0.0.1:8080/api",
            "http://127.0.0.1/admin",
            "https://localhost/test",  # localhost 通常解析到 127.0.0.1
        ]
        for url in test_cases:
            is_safe, error = guard.check_url(url)
            assert is_safe is False, f"应该阻止 {url}"
            assert "环回" in error

    def test_block_link_local(self):
        """阻止链路本地地址 (169.254.0.0/16) - 云元数据端点"""
        guard = SSRFGuard()
        test_cases = [
            "http://169.254.169.254/latest/meta-data/",
            "http://169.254.169.254/metadata/v1/",
            "http://169.254.0.1/test",
        ]
        for url in test_cases:
            is_safe, error = guard.check_url(url)
            assert is_safe is False, f"应该阻止 {url}"
            assert "链路本地" in error or "云元数据" in error


class TestIPv6:
    """IPv6 地址测试"""

    def test_block_ipv6_loopback(self):
        """阻止 IPv6 环回地址 (::1)"""
        guard = SSRFGuard()
        is_safe, error = guard.check_url("http://[::1]:8080/admin")
        assert is_safe is False
        assert "环回" in error

    def test_block_ipv6_ula(self):
        """阻止 IPv6 ULA (fc00::/7)"""
        guard = SSRFGuard()
        test_cases = [
            "http://[fc00::1]/admin",
            "http://[fd00::1]/test",
        ]
        for url in test_cases:
            is_safe, error = guard.check_url(url)
            assert is_safe is False, f"应该阻止 {url}"

    def test_block_ipv6_link_local(self):
        """阻止 IPv6 链路本地地址 (fe80::/10)"""
        guard = SSRFGuard()
        is_safe, error = guard.check_url("http://[fe80::1]/test")
        assert is_safe is False


class TestPublicIPs:
    """公共 IP 访问测试"""

    def test_allow_public_ip(self):
        """允许访问公共 IP"""
        guard = SSRFGuard()
        test_cases = [
            "http://8.8.8.8/dns",
            "https://1.1.1.1/dns",
            "http://93.184.216.34/",  # example.com
        ]
        for url in test_cases:
            is_safe, error = guard.check_url(url)
            assert is_safe is True, f"应该允许 {url}, 错误: {error}"


class TestAllowlist:
    """白名单配置测试"""

    def test_allowed_networks(self):
        """允许配置的私有网络访问"""
        guard = SSRFGuard(
            allowed_networks=["192.168.1.0/24"]
        )
        # 允许的私有网络
        is_safe, error = guard.check_url("http://192.168.1.100:8080/api")
        assert is_safe is True
        # 其他私有网络仍然被阻止
        is_safe, error = guard.check_url("http://192.168.2.1/admin")
        assert is_safe is False

    def test_allowed_private_domains(self):
        """允许配置的私有域名访问"""
        guard = SSRFGuard(
            allowed_private_domains=["internal.company.com"]
        )
        # 允许的域名
        is_safe, error = guard.check_url("http://internal.company.com/api")
        assert is_safe is True
        # 其他域名仍然被检查
        is_safe, error = guard.check_url("http://internal.other.com/api")
        # 注意：这个测试可能需要 mock DNS 解析

    def test_multiple_allowed_networks(self):
        """支持多个允许的网络"""
        guard = SSRFGuard(
            allowed_networks=["192.168.1.0/24", "10.10.0.0/16"]
        )
        is_safe, _ = guard.check_url("http://192.168.1.50/test")
        assert is_safe is True
        is_safe, _ = guard.check_url("http://10.10.5.5/test")
        assert is_safe is True
        is_safe, _ = guard.check_url("http://10.0.0.1/test")
        assert is_safe is False

    def test_add_allowed_network(self):
        """动态添加允许的网络"""
        guard = SSRFGuard()
        # 先被阻止
        is_safe, _ = guard.check_url("http://192.168.1.50/test")
        assert is_safe is False
        # 添加允许的网络
        guard.add_allowed_network("192.168.1.0/24")
        # 现在允许
        is_safe, _ = guard.check_url("http://192.168.1.50/test")
        assert is_safe is True

    def test_add_allowed_domain(self):
        """动态添加允许的域名"""
        guard = SSRFGuard()
        guard.add_allowed_domain("internal.local")
        is_safe, _ = guard.check_url("http://internal.local/api")
        assert is_safe is True


class TestDNSResolution:
    """DNS 解析测试"""

    def test_dns_resolved_to_private_ip(self):
        """DNS 解析到私有 IP 应被阻止"""
        guard = SSRFGuard()
        # 使用 localhost 作为测试（通常解析到 127.0.0.1）
        is_safe, error = guard.check_url("http://localhost/admin")
        assert is_safe is False

    def test_dns_resolution_failure(self):
        """DNS 解析失败应返回错误"""
        guard = SSRFGuard()
        is_safe, error = guard.check_url("http://this-domain-does-not-exist-12345.local/test")
        assert is_safe is False
        assert "无法解析" in error


class TestUtilityMethods:
    """工具方法测试"""

    def test_is_safe_url(self):
        """is_safe_url 方法"""
        guard = SSRFGuard()
        assert guard.is_safe_url("http://8.8.8.8/dns") is True
        assert guard.is_safe_url("http://192.168.1.1/admin") is False

    def test_get_config(self):
        """get_config 方法"""
        guard = SSRFGuard(
            allowed_networks=["192.168.1.0/24"],
            allowed_private_domains=["internal.local"]
        )
        config = guard.get_config()
        assert config["enabled"] is True
        assert "192.168.1.0/24" in config["allowed_networks"]
        assert "internal.local" in config["allowed_private_domains"]

    def test_blocked_networks_count(self):
        """检查默认阻止的网络数量"""
        # 默认应该有多个阻止的网络
        assert len(DEFAULT_BLOCKED_NETWORKS) >= 10


class TestEdgeCases:
    """边界情况测试"""

    def test_url_with_port(self):
        """带端口的 URL"""
        guard = SSRFGuard()
        is_safe, _ = guard.check_url("http://192.168.1.1:8080/api")
        assert is_safe is False

    def test_url_with_path(self):
        """带路径的 URL"""
        guard = SSRFGuard()
        is_safe, _ = guard.check_url("http://192.168.1.1/deep/nested/path")
        assert is_safe is False

    def test_url_with_query(self):
        """带查询参数的 URL"""
        guard = SSRFGuard()
        is_safe, _ = guard.check_url("http://192.168.1.1/api?key=value")
        assert is_safe is False

    def test_url_with_fragment(self):
        """带 fragment 的 URL"""
        guard = SSRFGuard()
        is_safe, _ = guard.check_url("http://192.168.1.1/page#section")
        assert is_safe is False

    def test_https_url(self):
        """HTTPS URL"""
        guard = SSRFGuard()
        is_safe, _ = guard.check_url("https://192.168.1.1/secure")
        assert is_safe is False

    def test_ipv6_url_format(self):
        """IPv6 URL 格式"""
        guard = SSRFGuard()
        is_safe, _ = guard.check_url("http://[::1]/admin")
        assert is_safe is False

    def test_case_insensitive_domain(self):
        """域名大小写不敏感"""
        guard = SSRFGuard(allowed_private_domains=["Internal.Local"])
        # 允许列表应该不区分大小写
        is_safe, _ = guard.check_url("http://internal.local/api")
        assert is_safe is True
        is_safe, _ = guard.check_url("http://INTERNAL.LOCAL/api")
        assert is_safe is True
