# feat-zai-provider: ZAI/GLM CodePlan Provider

## 概述

为 AnyClaw 添加 Z.AI (GLM) Provider 支持，包括 GLM Coding Plan 的集成。用户可以使用 GLM-5、GLM-4.7 等模型，支持全球和中国区 endpoint，以及 Coding Plan 专属 endpoint。

## 依赖

- `feat-mvp-agent` (已完成) - Agent 引擎核心
- `feat-tool-calling` (pending) - 可选，Tool Calling 支持

## 用户价值点

### VP1: ZAI Provider 配置

**价值**: 支持配置 ZAI API Key 和选择不同的 endpoint，让用户可以使用 GLM 系列模型。

**Gherkin 场景**:

```gherkin
Feature: ZAI Provider 配置

  Scenario: 配置 ZAI API Key
    Given 用户有 ZAI_API_KEY
    When 设置环境变量 ZAI_API_KEY
    Then AnyClaw 应能识别并使用该 key
    And 可以使用 zai/glm-5 模型

  Scenario: 选择 Global endpoint
    Given 用户想使用全球 endpoint
    When 配置 ZAI_ENDPOINT=global
    Then 请求应发送到 api.z.ai
    And 使用 api.z.ai/api/paas/v4 作为 base URL

  Scenario: 选择 CN endpoint
    Given 用户想使用中国区 endpoint
    When 配置 ZAI_ENDPOINT=cn
    Then 请求应发送到 open.bigmodel.cn
    And 使用 open.bigmodel.cn/api/paas/v4 作为 base URL

  Scenario: 选择 Coding Plan Global
    Given 用户是 GLM Coding Plan 用户
    When 配置 ZAI_ENDPOINT=coding-global
    Then 请求应发送到 Coding Plan endpoint
    And 默认使用 glm-5 模型

  Scenario: 选择 Coding Plan CN
    Given 用户是 GLM Coding Plan 中国区用户
    When 配置 ZAI_ENDPOINT=coding-cn
    Then 请求应发送到 Coding Plan CN endpoint
    And 默认使用 glm-5 或 glm-4.7 模型

  Scenario: 使用 zai/ 模型前缀
    Given 配置了 ZAI_API_KEY
    When 设置 llm_model="zai/glm-5"
    Then Agent 应使用 GLM-5 模型
    And 请求通过 ZAI provider 发送
```

### VP2: 自动 Endpoint 检测

**价值**: 根据 API Key 自动检测是 Coding Plan 还是普通 API，无需手动配置 endpoint。

**Gherkin 场景**:

```gherkin
Feature: 自动 Endpoint 检测

  Scenario: 检测 Coding Plan API Key
    Given 用户提供了一个 Coding Plan API Key
    When 运行自动检测
    Then 应识别为 coding-global 或 coding-cn
    And 返回推荐的模型 ID

  Scenario: 检测普通 API Key
    Given 用户提供了一个普通 ZAI API Key
    When 运行自动检测
    Then 应识别为 global 或 cn
    And 返回推荐的模型 ID

  Scenario: 检测失败时回退
    Given API Key 无效或网络错误
    When 运行自动检测
    Then 应返回默认配置
    And 记录警告日志
    And 不应阻止用户手动配置

  Scenario: CLI 自动检测命令
    Given 用户想自动配置 ZAI
    When 运行 "anyclaw config detect-zai"
    Then 应尝试检测最佳 endpoint
    And 显示检测结果
    And 可选保存到配置
```

### VP3: CLI Onboard 集成

**价值**: 提供简化的 CLI 命令配置 ZAI Provider，类似 OpenClaw 的 onboard 流程。

**Gherkin 场景**:

```gherkin
Feature: CLI Onboard 集成

  Scenario: Onboard 使用 Coding Plan Global
    Given 用户是 GLM Coding Plan 用户
    When 运行 "anyclaw onboard --auth-choice zai-coding-global"
    Then 应提示输入 ZAI_API_KEY
    And 配置默认模型为 zai/glm-5
    And 配置 endpoint 为 coding-global

  Scenario: Onboard 使用 Coding Plan CN
    Given 用户是 GLM Coding Plan 中国区用户
    When 运行 "anyclaw onboard --auth-choice zai-coding-cn"
    Then 应提示输入 ZAI_API_KEY
    And 配置默认模型为 zai/glm-5
    And 配置 endpoint 为 coding-cn

  Scenario: Onboard 使用普通 Global API
    Given 用户有普通 ZAI API
    When 运行 "anyclaw onboard --auth-choice zai-global"
    Then 应提示输入 ZAI_API_KEY
    And 配置默认模型为 zai/glm-5

  Scenario: 列出可用 auth choices
    Given 用户想查看所有配置选项
    When 运行 "anyclaw onboard --list-auth-choices"
    Then 应显示所有支持的 provider 选项
    And 包含 zai-coding-global, zai-coding-cn, zai-global, zai-cn

  Scenario: 查看 ZAI 配置状态
    Given 已配置 ZAI Provider
    When 运行 "anyclaw config show --provider zai"
    Then 应显示当前 ZAI 配置
    And 显示 endpoint
    And 显示默认模型
    And 显示 API Key 状态（已配置/未配置）
```

## 技术设计

### 配置扩展

```python
# settings.py 扩展
class Settings(BaseSettings):
    # 新增 ZAI 配置
    zai_api_key: str = Field(default="", description="ZAI API Key")
    zai_endpoint: str = Field(
        default="auto",
        description="ZAI endpoint: auto/global/cn/coding-global/coding-cn"
    )
    zai_base_url: Optional[str] = Field(
        default=None,
        description="自定义 ZAI base URL"
    )
```

### Endpoint 映射

```python
ZAI_ENDPOINTS = {
    "global": "https://api.z.ai/api/paas/v4",
    "cn": "https://open.bigmodel.cn/api/paas/v4",
    "coding-global": "https://api.z.ai/api/paas/v4",
    "coding-cn": "https://open.bigmodel.cn/api/paas/v4",
}
```

### litellm 集成

```python
# litellm 调用时设置 api_base
response = await acompletion(
    model="zai/glm-5",
    messages=messages,
    api_key=settings.zai_api_key,
    api_base=resolve_zai_base_url(settings.zai_endpoint),
)
```

### 目录结构

```
anyclaw/
├── providers/
│   ├── __init__.py
│   ├── base.py           # Provider 基类
│   ├── zai.py            # ZAI Provider 实现
│   └── zai_detect.py     # Endpoint 自动检测
└── cli/
    └── onboard.py        # Onboard 命令
```

## 数据流

```
用户配置 ZAI_API_KEY
        ↓
Settings 加载配置
        ↓
ZAIProvider 初始化
    ├─ 读取 endpoint 配置
    ├─ (可选) 自动检测
    └─ 解析 base_url
        ↓
AgentLoop 调用 LLM
    ├─ model="zai/glm-5"
    ├─ api_key=settings.zai_api_key
    └─ api_base=zai_base_url
        ↓
litellm 发送请求到 ZAI
```

## 验收标准

- [ ] 支持 4 种 endpoint 配置
- [ ] 支持环境变量配置 ZAI_API_KEY
- [ ] 自动检测功能正常工作
- [ ] CLI onboard 命令可用
- [ ] 与现有 litellm 集成无冲突
- [ ] 测试覆盖率 > 80%
- [ ] 文档完整

## 参考

- OpenClaw ZAI Extension: `reference/openclaw/extensions/zai/`
- OpenClaw ZAI Detect: `reference/openclaw/src/plugins/provider-zai-endpoint.ts`
- OpenClaw GLM Docs: `reference/openclaw/docs/providers/glm.md`
- litellm ZAI Support: https://docs.litellm.ai/docs/providers/zhipu
