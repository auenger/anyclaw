# feat-zai-provider: 完成检查清单

## VP1: ZAI Provider 配置

### Provider 基础架构
- [ ] `providers/` 目录已创建
- [ ] `Provider` 基类已定义
- [ ] 基类有必要的抽象方法
- [ ] 单元测试通过

### 配置扩展
- [ ] `zai_api_key` 配置字段已添加
- [ ] `zai_endpoint` 配置字段已添加
- [ ] `zai_base_url` 配置字段已添加
- [ ] `.env.example` 已更新
- [ ] 配置验证正常工作

### ZAI Provider 实现
- [ ] `ZAIProvider` 类已实现
- [ ] 4 种 endpoint 映射正确
- [ ] base_url 解析正确
- [ ] 单元测试通过

---

## VP2: 自动 Endpoint 检测

### 检测逻辑
- [ ] `detect_zai_endpoint()` 已实现
- [ ] 能识别 Coding Plan API Key
- [ ] 能识别普通 API Key
- [ ] 错误处理健壮
- [ ] 超时处理正常
- [ ] 单元测试通过

### Provider 集成
- [ ] `endpoint="auto"` 模式正常工作
- [ ] 检测结果被正确使用
- [ ] 日志记录完整

---

## VP3: CLI Onboard 集成

### Onboard 命令
- [ ] `anyclaw onboard` 命令可用
- [ ] `--auth-choice` 参数正常工作
- [ ] 交互式输入正常
- [ ] `--list-auth-choices` 正常工作

### ZAI Auth Choices
- [ ] `zai-coding-global` 正常工作
- [ ] `zai-coding-cn` 正常工作
- [ ] `zai-global` 正常工作
- [ ] `zai-cn` 正常工作
- [ ] 配置保存正确

### 配置管理
- [ ] 配置写入 `.env` 正常
- [ ] 配置验证正常
- [ ] `anyclaw config show` 显示 ZAI 配置

---

## AgentLoop 集成

### LLM 调用
- [ ] `zai/glm-5` 模型可调用
- [ ] `zai/glm-4.7` 模型可调用
- [ ] api_base 正确设置
- [ ] 错误处理正常

### 测试
- [ ] 各 endpoint 测试通过
- [ ] 错误场景测试通过

---

## 质量标准

### 代码质量
- [ ] 通过 Black 格式化
- [ ] 通过 Ruff 检查
- [ ] 类型注解完整
- [ ] 有适当的文档字符串

### 测试
- [ ] 单元测试覆盖率 > 80%
- [ ] 集成测试通过
- [ ] 边界情况有测试
- [ ] 错误情况有测试

### 文档
- [ ] CLAUDE.md 已更新
- [ ] ZAI Provider 使用指南存在
- [ ] README 已更新
- [ ] 有配置示例

---

## 验收测试

### 手动测试场景

- [ ] **场景 1**: 配置 Coding Plan Global
  ```bash
  export ZAI_API_KEY=your-key
  export ZAI_ENDPOINT=coding-global
  anyclaw chat
  ```
  预期: 使用 GLM-5 模型，请求发送到 Coding Plan endpoint

- [ ] **场景 2**: 配置 Coding Plan CN
  ```bash
  export ZAI_API_KEY=your-key
  export ZAI_ENDPOINT=coding-cn
  anyclaw chat
  ```
  预期: 使用 GLM 模型，请求发送到中国区 endpoint

- [ ] **场景 3**: 使用 onboard 命令
  ```bash
  anyclaw onboard --auth-choice zai-coding-global
  ```
  预期: 交互式配置，保存到 .env

- [ ] **场景 4**: 自动检测
  ```bash
  export ZAI_API_KEY=your-key
  export ZAI_ENDPOINT=auto
  anyclaw config detect-zai
  ```
  预期: 自动检测并显示推荐的 endpoint

- [ ] **场景 5**: 查看配置
  ```bash
  anyclaw config show --provider zai
  ```
  预期: 显示当前 ZAI 配置状态

---

## 完成条件

- [ ] 所有 VP1 检查项完成
- [ ] 所有 VP2 检查项完成
- [ ] 所有 VP3 检查项完成
- [ ] AgentLoop 集成完成
- [ ] 所有质量标准满足
- [ ] 所有验收测试通过
- [ ] 代码已提交
- [ ] PR 已创建并审核通过
