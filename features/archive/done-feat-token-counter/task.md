# feat-token-counter: 任务分解

## 阶段 1: Token 计数器实现 (VP1)

### 1.1 添加依赖
- [ ] 添加 tiktoken 到 pyproject.toml
- [ ] 运行 poetry install

### 1.2 实现 TokenCounter
- [ ] 创建 `agent/token_counter.py`
- [ ] 实现 `_get_encoding()` - 获取模型对应编码器
- [ ] 实现 `count()` - 计算单文本 token 数
- [ ] 实现 `count_messages()` - 计算消息列表 token 分布
- [ ] 实现估算方法（无编码器时）

### 1.3 单元测试
- [ ] 创建 `tests/test_token_counter.py`
- [ ] 测试 GPT-4 编码器
- [ ] 测试 GPT-4o 编码器
- [ ] 测试估算方法
- [ ] 测试消息列表计数

---

## 阶段 2: Token 限制器实现 (VP2)

### 2.1 扩展配置
- [ ] 在 `config/settings.py` 添加 token 配置字段
  - `token_soft_limit`
  - `token_hard_limit`
  - `token_warning_threshold`
  - `token_warning_enabled`
- [ ] 更新 `.env.example`

### 2.2 实现 TokenLimiter
- [ ] 创建 `agent/token_limiter.py`
- [ ] 实现 `check()` - 检查 token 使用情况
- [ ] 实现 `should_warn()` - 判断是否需要警告
- [ ] 实现 `is_over_limit()` - 判断是否超过限制

### 2.3 集成到 AgentLoop
- [ ] 修改 `AgentLoop` 初始化 TokenLimiter
- [ ] 在 `process()` 中检查 token
- [ ] 实现警告显示逻辑
- [ ] 实现硬限制阻止逻辑

### 2.4 单元测试
- [ ] 创建 `tests/test_token_limiter.py`
- [ ] 测试软限制警告
- [ ] 测试硬限制阻止
- [ ] 测试自定义阈值
- [ ] 测试禁用警告

---

## 阶段 3: CLI 命令

### 3.1 实现 token 命令组
- [ ] 创建 `cli/token.py`
- [ ] 实现 `token stats` 子命令
- [ ] 实现 `token limit` 子命令
- [ ] 实现 `token warn` 子命令

### 3.2 集成到主 CLI
- [ ] 在 `cli/app.py` 注册 token 命令组
- [ ] 添加单元测试

---

## 阶段 4: 文档和集成

### 4.1 集成测试
- [ ] 测试完整流程
- [ ] 测试与 AgentLoop 集成
- [ ] 测试 CLI 命令

### 4.2 文档
- [ ] 更新 CLAUDE.md
- [ ] 创建 Token 管理使用指南
- [ ] 添加配置示例

---

## 依赖关系

```
1.1 → 1.2 → 1.3
            ↓
2.1 → 2.2 → 2.3 → 2.4
                  ↓
            3.1 → 3.2
                  ↓
            4.1 → 4.2
```

## 预估工时

| 阶段 | 预估 |
|------|------|
| 阶段 1 | 1-2h |
| 阶段 2 | 2-3h |
| 阶段 3 | 1h |
| 阶段 4 | 1-2h |
| **总计** | **5-8h** |
