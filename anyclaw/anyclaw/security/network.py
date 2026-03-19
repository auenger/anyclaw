"""SSRF 防护模块

阻止对私有网络、云元数据端点、本地服务的访问。

使用方法:
    guard = SSRFGuard()
    is_safe, error = guard.check_url("http://192.168.1.1/admin")
    if not is_safe:
        print(f"访问被拒绝: {error}")
"""

import ipaddress
import socket
from typing import List, Optional, Set, Tuple, Union
from urllib.parse import urlparse


# =============================================================================
# 默认阻止的网络范围
# =============================================================================

DEFAULT_BLOCKED_NETWORKS = [
    # IPv4 特殊用途地址
    ipaddress.ip_network("0.0.0.0/8"),        # 当前网络 (RFC 1700)
    ipaddress.ip_network("10.0.0.0/8"),       # A 类私有网络 (RFC 1918)
    ipaddress.ip_network("100.64.0.0/10"),    # 运营商级 NAT (RFC 6598)
    ipaddress.ip_network("127.0.0.0/8"),      # 本地环回 (RFC 1122)
    ipaddress.ip_network("169.254.0.0/16"),   # 链路本地 / 云元数据 (RFC 3927)
    ipaddress.ip_network("172.16.0.0/12"),    # B 类私有网络 (RFC 1918)
    ipaddress.ip_network("192.0.0.0/24"),     # IETF 协议分配 (RFC 6890)
    ipaddress.ip_network("192.0.2.0/24"),     # TEST-NET-1 (RFC 5737)
    ipaddress.ip_network("192.168.0.0/16"),   # C 类私有网络 (RFC 1918)
    ipaddress.ip_network("198.18.0.0/15"),    # 网络基准测试 (RFC 2544)
    ipaddress.ip_network("198.51.100.0/24"),  # TEST-NET-2 (RFC 5737)
    ipaddress.ip_network("203.0.113.0/24"),   # TEST-NET-3 (RFC 5737)
    ipaddress.ip_network("224.0.0.0/4"),      # 多播 (RFC 5771)
    ipaddress.ip_network("240.0.0.0/4"),      # 保留 (RFC 1112)
    ipaddress.ip_network("255.255.255.255/32"),  # 受限广播

    # IPv6 特殊用途地址
    ipaddress.ip_network("::1/128"),          # IPv6 环回
    ipaddress.ip_network("::/128"),           # 未指定地址
    ipaddress.ip_network("::ffff:0:0/96"),    # IPv4 映射地址
    ipaddress.ip_network("64:ff9b::/96"),     # IPv4-IPv6 转换
    ipaddress.ip_network("100::/64"),         # 仅丢弃 (RFC 6666)
    ipaddress.ip_network("2001::/23"),        # IETF 协议分配
    ipaddress.ip_network("2001:2::/48"),      # 基准测试 (RFC 5180)
    ipaddress.ip_network("2001:db8::/32"),    # 文档用途 (RFC 3849)
    ipaddress.ip_network("2001:10::/28"),     # ORCHID (RFC 4843)
    ipaddress.ip_network("2002::/16"),        # 6to4 (RFC 3056)
    ipaddress.ip_network("fc00::/7"),         # IPv6 ULA (RFC 4193)
    ipaddress.ip_network("fe80::/10"),        # IPv6 链路本地 (RFC 4291)
    ipaddress.ip_network("ff00::/8"),         # IPv6 多播 (RFC 4291)
]


class SSRFGuard:
    """SSRF 防护器

    检查 URL 是否指向私有网络或敏感地址。

    检查流程:
    1. 解析 URL 获取主机名
    2. 检查是否在允许的私有域名列表中
    3. 解析主机名到 IP 地址（支持 DNS 解析）
    4. 检查 IP 是否在阻止列表中
    5. 检查 IP 是否在允许列表中（可覆盖阻止列表）
    """

    def __init__(
        self,
        enabled: bool = True,
        blocked_networks: Optional[List[Union[ipaddress.IPv4Network, ipaddress.IPv6Network]]] = None,
        allowed_networks: Optional[List[str]] = None,
        allowed_private_domains: Optional[List[str]] = None,
    ):
        """初始化 SSRF 防护器

        Args:
            enabled: 是否启用 SSRF 防护
            blocked_networks: 自定义阻止的网络列表（默认使用 DEFAULT_BLOCKED_NETWORKS）
            allowed_networks: 允许访问的网络白名单（CIDR 格式）
            allowed_private_domains: 允许访问的私有域名白名单
        """
        self.enabled = enabled
        self.blocked_networks = (
            list(blocked_networks) if blocked_networks else list(DEFAULT_BLOCKED_NETWORKS)
        )
        self.allowed_networks = self._parse_networks(allowed_networks or [])
        self.allowed_private_domains: Set[str] = set(allowed_private_domains or [])

    def _parse_networks(
        self, networks: List[str]
    ) -> List[Union[ipaddress.IPv4Network, ipaddress.IPv6Network]]:
        """解析网络列表

        Args:
            networks: CIDR 格式的网络列表

        Returns:
            解析后的网络对象列表
        """
        result = []
        for net in networks:
            try:
                result.append(ipaddress.ip_network(net, strict=False))
            except ValueError:
                # 忽略无效的网络格式
                pass
        return result

    def check_url(self, url: str) -> Tuple[bool, str]:
        """检查 URL 是否安全

        Args:
            url: 要检查的 URL

        Returns:
            Tuple[bool, str]: (是否安全, 错误信息)
                - 如果安全，返回 (True, "")
                - 如果不安全，返回 (False, "错误原因")
        """
        if not self.enabled:
            return True, ""

        # 解析 URL
        try:
            parsed = urlparse(url)
        except Exception as e:
            return False, f"无效的 URL: {e}"

        hostname = parsed.hostname
        if not hostname:
            return False, "URL 缺少主机名"

        # 检查是否在允许的私有域名列表中
        if hostname.lower() in {d.lower() for d in self.allowed_private_domains}:
            return True, ""

        # 解析 IP 地址
        try:
            ip = self._resolve_hostname(hostname)
        except socket.gaierror as e:
            return False, f"无法解析主机名 {hostname}: {e}"
        except ValueError as e:
            return False, str(e)

        # 检查 IP 是否在阻止列表中
        for blocked_net in self.blocked_networks:
            if ip in blocked_net:
                # 检查是否在允许列表中
                for allowed_net in self.allowed_networks:
                    if ip in allowed_net:
                        return True, ""

                # 返回具体的阻止原因
                return False, self._get_block_reason(ip, blocked_net)

        return True, ""

    def is_safe_url(self, url: str) -> bool:
        """检查 URL 是否安全（简化版）

        Args:
            url: 要检查的 URL

        Returns:
            bool: True 表示安全
        """
        is_safe, _ = self.check_url(url)
        return is_safe

    def is_internal_url(self, url: str) -> bool:
        """检查是否为内部 URL

        Args:
            url: 要检查的 URL

        Returns:
            bool: True 表示是内部 URL
        """
        return not self.is_safe_url(url)

    def _resolve_hostname(self, hostname: str) -> Union[ipaddress.IPv4Address, ipaddress.IPv6Address]:
        """解析主机名到 IP 地址

        Args:
            hostname: 主机名或 IP 地址字符串

        Returns:
            IP 地址对象

        Raises:
            ValueError: 如果是无效的 IP 地址
            socket.gaierror: 如果 DNS 解析失败
        """
        # 先尝试直接解析为 IP 地址
        try:
            # 处理 IPv6 地址（可能带方括号）
            clean_hostname = hostname.strip("[]")
            return ipaddress.ip_address(clean_hostname)
        except ValueError:
            pass

        # 不是 IP 地址，进行 DNS 解析
        # 注意：这会进行实际的网络请求
        try:
            # getaddrinfo 返回 IPv4 和 IPv6 地址
            # 我们只取第一个
            addr_info = socket.getaddrinfo(hostname, None)
            if not addr_info:
                raise ValueError(f"无法解析主机名: {hostname}")

            # 获取第一个地址
            _, _, _, _, sockaddr = addr_info[0]
            ip_str = sockaddr[0]
            return ipaddress.ip_address(ip_str)
        except socket.gaierror:
            raise

    def _get_block_reason(
        self,
        ip: Union[ipaddress.IPv4Address, ipaddress.IPv6Address],
        network: Union[ipaddress.IPv4Network, ipaddress.IPv6Network],
    ) -> str:
        """生成阻止原因描述

        Args:
            ip: 被阻止的 IP 地址
            network: 匹配的网络

        Returns:
            人类可读的阻止原因
        """
        ip_str = str(ip)
        network_str = str(network)

        # 特殊情况
        if network == ipaddress.ip_network("127.0.0.0/8") or network == ipaddress.ip_network("::1/128"):
            return f"访问环回地址被阻止: {ip_str}"
        elif network == ipaddress.ip_network("169.254.0.0/16") or network == ipaddress.ip_network("fe80::/10"):
            return f"访问链路本地地址被阻止: {ip_str} (可能是云元数据端点)"
        elif network in [
            ipaddress.ip_network("10.0.0.0/8"),
            ipaddress.ip_network("172.16.0.0/12"),
            ipaddress.ip_network("192.168.0.0/16"),
        ]:
            return f"访问私有网络被阻止: {ip_str} (RFC 1918)"
        elif network == ipaddress.ip_network("fc00::/7"):
            return f"访问 IPv6 ULA 被阻止: {ip_str}"
        else:
            return f"访问受限网络被阻止: {ip_str} (网络: {network_str})"

    def add_allowed_network(self, network: str) -> None:
        """添加允许的网络

        Args:
            network: CIDR 格式的网络地址
        """
        try:
            net = ipaddress.ip_network(network, strict=False)
            if net not in self.allowed_networks:
                self.allowed_networks.append(net)
        except ValueError:
            pass

    def add_allowed_domain(self, domain: str) -> None:
        """添加允许的私有域名

        Args:
            domain: 域名
        """
        self.allowed_private_domains.add(domain.lower())

    def get_config(self) -> dict:
        """获取当前配置

        Returns:
            dict: 配置信息
        """
        return {
            "enabled": self.enabled,
            "blocked_networks_count": len(self.blocked_networks),
            "allowed_networks": [str(n) for n in self.allowed_networks],
            "allowed_private_domains": list(self.allowed_private_domains),
        }
