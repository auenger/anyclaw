# feat-model-config-fix: 修复 /model 命令配置传递问题

## 背景

用户反馈 `/model` 命令返回的模型信息与实际配置不符。经代码分析，发现配置传递链路中存在两个 bug。

## 问题描述

### Bug 1: CLI Channel 配置字段引用错误

**文件**: `anyclaw/channels/cli.py:204`

```python
context = CommandContext(
    ...
    config=self._config,  # ❌ self._config 不存在！
)
```

`CLIChannel` 类中定义的是 `self.config`（CLIConfig 类型），但第 204 行引用的是 `self._config`，导致 `context.config` 为 `None`。

### Bug 2: model.py 与 Settings 结构不兼容

**文件**: `anyclaw/commands/handlers/model.py:61-62`

```python
current_model = getattr(config.llm, "model", "unknown") if hasattr(config, "llm") else "unknown"
```

期望 `config` 有 `llm` 属性（Config 结构），但 `Settings` 类使用扁平字段 `llm_model`、`llm_provider`。

## 用户价值点

### VP1: /model 命令正确显示当前配置

用户执行 `/model` 命令时，应显示配置文件中的实际模型和 provider。

**验收场景**:

```gherkin
Feature: /model 命令配置显示

Scenario: 显示当前模型配置
  Given 用户已配置 ~/.anyclaw/config.toml 中 [llm] model = "glm-4.7"
  When 用户在 CLI 中输入 "/model"
  Then 应显示 "当前模型: glm-4.7"
  And 应显示 "Provider: zai"

Scenario: 配置不存在时显示默认值
  Given 配置文件不存在或无法加载
  When 用户在 CLI 中输入 "/model"
  Then 应显示默认模型 "gpt-4o-mini"
  And 应显示默认 provider "openai"
```

### VP2: /model 命令支持模型切换

用户可以通过 `/model <name>` 切换模型，切换后配置应正确保存。

**验收场景**:

```gherkin
Feature: /model 命令模型切换

Scenario: 切换到有效模型
  Given 当前模型为 "gpt-4o-mini"
  When 用户在 CLI 中输入 "/model gpt-4o"
  Then 应显示 "模型已切换 gpt-4o-mini → gpt-4o"
  And 后续 /model 命令应显示新模型

Scenario: 切换到无效模型
  Given 当前模型为 "gpt-4o-mini"
  When 用户在 CLI 中输入 "/model invalid-model-xyz"
  Then 应显示 "未知模型: invalid-model-xyz"
```

## 技术方案

### 修复 1: cli.py 导入全局 settings

```python
# anyclaw/channels/cli.py
from anyclaw.config.settings import settings

async def _handle_command(self, user_input: str) -> "CommandResult":
    context = CommandContext(
        ...
        config=settings,  # 使用全局 settings
    )
```

### 修复 2: model.py 兼容 Settings 结构

```python
# anyclaw/commands/handlers/model.py
if hasattr(config, "llm"):
    # Config 结构 (loader.py)
    current_model = getattr(config.llm, "model", "unknown")
    current_provider = getattr(config.llm, "provider", "unknown")
elif hasattr(config, "llm_model"):
    # Settings 结构 (settings.py)
    current_model = config.llm_model
    current_provider = config.llm_provider
else:
    current_model = "unknown"
    current_provider = "unknown"
```

## 影响范围

- **修改文件**:
  - `anyclaw/channels/cli.py` (1 行)
  - `anyclaw/commands/handlers/model.py` (2 行)
- **测试文件**: 无需新增，现有测试应继续通过
- **向后兼容**: 完全兼容

## 大小评估

| 指标 | 评估 |
|-----|------|
| 价值点 | 2 |
| 大小 | S |
| 风险 | 低 |
| 预估工时 | 15 分钟 |
