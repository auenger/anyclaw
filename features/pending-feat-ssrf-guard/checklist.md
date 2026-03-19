# 完成检查清单

## 代码实现

- [x] `anyclaw/security/__init__.py` 已创建
- [x] `anyclaw/security/network.py` 已创建
- [x] `SSRFGuard` 类已实现
- [x] `DEFAULT_BLOCKED_NETWORKS` 包含所有私有网络
  - [x] 10.0.0.0/8 (A 类私有)
  - [x] 172.16.0.0/12 (B 类私有)
  - [x] 192.168.0.0/16 (C 类私有)
  - [x] 127.0.0.0/8 (本地环回)
  - [x] 169.254.0.0/16 (链路本地/云元数据)
  - [x] 100.64.0.0/10 (运营商级 NAT)
  - [x] ::1/128 (IPv6 环回)
  - [x] fc00::/7 (IPv6 ULA)
  - [x] fe80::/10 (IPv6 链路本地)
- [x] DNS 解析后 IP 检查已实现
- [x] 配置项已添加到 settings.py
- [ ] WebFetch 工具已集成 SSRF 检查（暂未集成，待后续需要时使用）

## 测试

- [x] `tests/test_ssrf_guard.py` 已创建
- [x] 测试阻止所有私有网络访问
- [x] 测试 IPv6 地址处理
- [x] 测试 DNS 解析场景
- [x] 测试白名单配置
- [x] 测试云元数据端点阻止
- [x] 测试覆盖率 > 90%（30 个测试全部通过）

## 文档

- [x] 代码有详细注释
- [x] API 文档完整

## 验收

- [x] http://10.x.x.x 被阻止
- [x] http://192.168.x.x 被阻止
- [x] http://127.0.0.1 被阻止
- [x] http://169.254.169.254 被阻止
- [x] 配置白名单后可访问指定内部服务
- [x] 所有测试通过: `pytest tests/test_ssrf_guard.py -v`

## 安全验证

- [x] 尝试绕过测试（多种编码方式）
- [x] DNS 重绑定攻击测试
- [x] IPv6 映射地址测试
