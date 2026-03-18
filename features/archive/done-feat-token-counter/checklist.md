# feat-token-counter: 完成检查清单

## VP1: Token 计数器

### 依赖安装
- [ ] tiktoken 已添加到 pyproject.toml
- [ ] poetry install 成功

### TokenCounter 实现
- [ ] `_get_encoding()` 正常工作
- [ ] `count()` 返回正确 token 数
- [ ] `count_messages()` 返回正确分布
- [ ] 估算方法正常工作

### 编码器支持
- [ ] GPT-4 (cl100k_base) 正常
- [ ] GPT-4o (o200k_base) 正常
- [ ] Claude (近似) 正常
- [ ] GLM (近似) 正常

### 单元测试
- [ ] test_token_counter.py 通过
- [ ] 覆盖率 > 80%

---

## VP2: Token 限制器

### 配置扩展
- [ ] `token_soft_limit` 已添加
- [ ] `token_hard_limit` 已添加
- [ ] `token_warning_threshold` 已添加
- [ ] `token_warning_enabled` 已添加
- [ ] `.env.example` 已更新

### TokenLimiter 实现
- [ ] `check()` 正常工作
- [ ] `should_warn()` 正确判断
- [ ] `is_over_limit()` 正确判断

### AgentLoop 集成
- [ ] TokenLimiter 已初始化
- [ ] 警告在正确时机显示
- [ ] 硬限制正确阻止输入
- [ ] 警告消息清晰

### 单元测试
- [ ] test_token_limiter.py 通过
- [ ] 覆盖率 > 80%

---

## CLI 命令

### token stats
- [ ] 显示当前对话 token 数
- [ ] 显示 token 分布
- [ ] 显示使用百分比

### token limit
- [ ] 设置软限制正常
- [ ] 设置硬限制正常
- [ ] 显示当前限制

### token warn
- [ ] 开启/关闭警告正常
- [ ] 设置阈值正常

### 集成
- [ ] 命令组已注册
- [ ] 单元测试通过

---

## 质量标准

### 代码质量
- [ ] 通过 Black 格式化
- [ ] 通过 Ruff 检查
- [ ] 类型注解完整

### 测试
- [ ] 单元测试覆盖率 > 80%
- [ ] 集成测试通过
- [ ] 边界情况有测试

### 文档
- [ ] CLAUDE.md 已更新
- [ ] 使用指南存在

---

## 验收测试

### 手动测试场景

- [ ] **场景 1**: 查看 token 统计
  ```bash
  anyclaw token stats
  ```
  预期: 显示当前对话的 token 使用情况

- [ ] **场景 2**: 触发警告
  ```
  # 设置较低的限制
  export TOKEN_SOFT_LIMIT=1000
  anyclaw chat
  # 进行多轮对话直到触发警告
  ```
  预期: 达到 80% 时显示警告

- [ ] **场景 3**: 禁用警告
  ```bash
  anyclaw token warn off
  anyclaw chat
  ```
  预期: 不显示 token 警告

- [ ] **场景 4**: 设置限制
  ```bash
  anyclaw token limit --soft 50000 --hard 100000
  ```
  预期: 限制已更新

---

## 完成条件

- [ ] 所有 VP1 检查项完成
- [ ] 所有 VP2 检查项完成
- [ ] CLI 命令完成
- [ ] 所有质量标准满足
- [ ] 所有验收测试通过
- [ ] 代码已提交
