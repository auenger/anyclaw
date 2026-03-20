# 任务分解

## Phase 1: 核心防护模块

### Task 1.1: 创建安全模块结构
- [ ] 创建 `anyclaw/security/__init__.py`
- [ ] 创建 `anyclaw/security/network.py`
- [ ] 定义 `DEFAULT_BLOCKED_NETWORKS` 常量

### Task 1.2: 实现 SSRFGuard 类
- [ ] 实现 `check_url()` 方法
- [ ] 实现 `is_internal_url()` 方法
- [ ] 实现 IP 解析和 DNS 查询
- [ ] 实现网络范围匹配逻辑

### Task 1.3: 核心防护测试
- [ ] 创建 `tests/test_ssrf_guard.py`
- [ ] 测试所有阻止的网络类型
- [ ] 测试 IPv4 和 IPv6
- [ ] 测试 DNS 解析场景

## Phase 2: 配置支持

### Task 2.1: 配置项定义
- [ ] 在 `settings.py` 添加 `SSRFSettings`
- [ ] 支持 `enabled` 开关
- [ ] 支持 `allowed_networks` 白名单
- [ ] 支持 `allowed_private_domains` 白名单

### Task 2.2: 配置集成
- [ ] SSRFGuard 从配置读取参数
- [ ] 支持运行时配置更新

### Task 2.3: 配置测试
- [ ] 测试白名单配置生效
- [ ] 测试域名白名单生效

## Phase 3: 工具集成

### Task 3.1: WebFetch 工具集成
- [ ] 在 WebFetchTool 中注入 SSRFGuard
- [ ] 请求前进行 SSRF 检查
- [ ] 返回友好的错误信息

### Task 3.2: 其他网络工具集成
- [ ] WebSearch 工具集成（如有）
- [ ] MCP 工具集成（如适用）

### Task 3.3: 集成测试
- [ ] 端到端测试 WebFetch SSRF 拦截
- [ ] 测试正常 URL 仍可访问

## 依赖关系

```
Task 1.1 ─→ Task 1.2 ─→ Task 1.3
                │
                ↓
         Task 2.1 ─→ Task 2.2 ─→ Task 2.3
                              │
                              ↓
                        Task 3.1 ─→ Task 3.3
                              │
                        Task 3.2 ──────────┘
```

## 预计工作量

- Phase 1: 核心防护模块 - 2-3 小时
- Phase 2: 配置支持 - 1 小时
- Phase 3: 工具集成 - 1-2 小时
- 总计: 4-6 小时
