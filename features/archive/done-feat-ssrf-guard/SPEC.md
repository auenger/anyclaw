# feat-ssrf-guard

**状态**: ✅ 已完成
**完成时间**: 2026-03-19
**优先级**: 80
**大小**: M

## 描述

实现 SSRF (Server-Side Request Forgery) 防护模块，阻止对私有网络、云元数据端点、本地服务的访问。

## 价值点

1. **SSRF 防护**
   - 阻止对私有 IP 地址的访问 (10.x, 172.16.x, 192.168.x 等)
   - 阻止对云元数据端点的访问 (169.254.169.254)
   - 阻止对本地环回地址的访问 (127.0.0.1, ::1)
   - 支持 IPv4 和 IPv6 地址检测

2. **URL 安全检查**
   - DNS 重绑定攻击防护
   - URL 解析和验证
   - 域名到 IP 地址解析

3. **可配置性**
   - 自定义允许/阻止的网络范围
   - 白名单机制

## 实现文件

- `anyclaw/security/network.py` - SSRF 防护核心模块
- `anyclaw/security/__init__.py` - 模块导出
- `tests/test_ssrf_guard.py` - 单元测试

## 使用示例

```python
from anyclaw.security import SSRFGuard

guard = SSRFGuard()

# 检查 URL 是否安全
is_safe, error = guard.check_url("http://192.168.1.1/admin")
if not is_safe:
    print(f"访问被拒绝: {error}")

# 检查 IP 地址
is_safe, error = guard.check_ip("10.0.0.1")
```

## 阻止的网络范围

默认阻止以下网络：
- `0.0.0.0/8` - 当前网络
- `10.0.0.0/8` - A 类私有网络
- `127.0.0.0/8` - 本地环回
- `169.254.0.0/16` - 链路本地 / 云元数据
- `172.16.0.0/12` - B 类私有网络
- `192.168.0.0/16` - C 类私有网络
- 以及其他特殊用途地址

## 测试

```
tests/test_ssrf_guard.py
```
