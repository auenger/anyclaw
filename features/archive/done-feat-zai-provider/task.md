# feat-zai-provider: 任务分解

## 阶段 1: Provider 系统设计 (VP1)

### 1.1 创建 Provider 基础架构
- [ ] 创建 `anyclaw/providers/` 目录
- [ ] 创建 `providers/__init__.py`
- [ ] 创建 `providers/base.py` - Provider 基类
- [ ] 定义 `Provider` 抽象基类接口

### 1.2 扩展配置系统
- [ ] 在 `config/settings.py` 添加 ZAI 配置字段
  - `zai_api_key`
  - `zai_endpoint`
  - `zai_base_url`
- [ ] 更新 `.env.example` 添加 ZAI 示例
- [ ] 添加配置验证逻辑

### 1.3 实现 ZAI Provider
- [ ] 创建 `providers/zai.py`
- [ ] 实现 `ZAIProvider` 类
- [ ] 实现 endpoint 映射逻辑
- [ ] 实现 base_url 解析
- [ ] 添加单元测试

---

## 阶段 2: Endpoint 自动检测 (VP2)

### 2.1 实现检测逻辑
- [ ] 创建 `providers/zai_detect.py`
- [ ] 实现 `detect_zai_endpoint()` 函数
- [ ] 实现 API Key 探测逻辑
- [ ] 实现 Coding Plan 识别
- [ ] 添加错误处理和回退

### 2.2 检测 API 设计
- [ ] 定义探测请求格式
- [ ] 实现超时处理
- [ ] 实现结果缓存（可选）
- [ ] 添加单元测试

### 2.3 集成到 Provider
- [ ] 在 `ZAIProvider` 中集成自动检测
- [ ] 实现 `endpoint="auto"` 模式
- [ ] 添加日志记录
- [ ] 添加集成测试

---

## 阶段 3: CLI Onboard 集成 (VP3)

### 3.1 创建 Onboard 命令
- [ ] 创建 `cli/onboard.py`
- [ ] 实现 `onboard` 命令入口
- [ ] 实现 `--auth-choice` 参数
- [ ] 实现交互式 API Key 输入

### 3.2 实现 ZAI Auth Choices
- [ ] 实现 `zai-coding-global` 选项
- [ ] 实现 `zai-coding-cn` 选项
- [ ] 实现 `zai-global` 选项
- [ ] 实现 `zai-cn` 选项
- [ ] 实现 `--list-auth-choices` 命令

### 3.3 配置保存
- [ ] 实现配置写入 `.env`
- [ ] 实现配置验证
- [ ] 实现配置显示命令
- [ ] 添加单元测试

---

## 阶段 4: AgentLoop 集成

### 4.1 修改 AgentLoop
- [ ] 更新 `_call_llm()` 支持 ZAI
- [ ] 实现动态 api_base 设置
- [ ] 实现模型前缀解析（`zai/`）
- [ ] 添加错误处理

### 4.2 测试集成
- [ ] 测试 `zai/glm-5` 模型调用
- [ ] 测试 `zai/glm-4.7` 模型调用
- [ ] 测试各 endpoint
- [ ] 测试错误场景

---

## 阶段 5: 文档和测试

### 5.1 单元测试
- [ ] `test_zai_provider.py`
- [ ] `test_zai_detect.py`
- [ ] `test_onboard.py`

### 5.2 集成测试
- [ ] 测试完整 onboard 流程
- [ ] 测试端到端 LLM 调用（mock）
- [ ] 测试配置持久化

### 5.3 文档
- [ ] 更新 CLAUDE.md
- [ ] 创建 ZAI Provider 使用指南
- [ ] 更新 README
- [ ] 添加配置示例

---

## 依赖关系

```
1.1 → 1.2 → 1.3
            ↓
2.1 → 2.2 → 2.3
            ↓
3.1 → 3.2 → 3.3
            ↓
4.1 → 4.2
        ↓
  5.1 → 5.2 → 5.3
```

## 预估工时

| 阶段 | 预估 |
|------|------|
| 阶段 1 | 2-3h |
| 阶段 2 | 2-3h |
| 阶段 3 | 2-3h |
| 阶段 4 | 1-2h |
| 阶段 5 | 2-3h |
| **总计** | **9-14h** |

## 关键决策

### Q1: litellm 原生支持 vs 自定义 Provider？

**litellm 原生支持**：
- ✅ 简单，直接使用 `zai/glm-5`
- ✅ 自动处理认证
- ❌ 不支持自定义 endpoint（Coding Plan）

**自定义 Provider**：
- ✅ 完全控制 endpoint
- ✅ 支持自动检测
- ❌ 需要更多代码

**决策**: 混合方案 - 使用 litellm 原生支持，但通过 `api_base` 参数自定义 endpoint。

### Q2: 配置存储位置？

**选项**：
1. `.env` 文件（当前方案）
2. `~/.anyclaw/config.json`
3. 两者都支持

**决策**: 优先支持 `.env`，未来可扩展到 `config.json`。
