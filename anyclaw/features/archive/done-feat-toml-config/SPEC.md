# feat-toml-config

**状态**: ✅ 已完成
**完成时间**: 2026-03-19
**优先级**: 70
**大小**: M

## 描述

将配置系统从 JSON 升级为 TOML 格式，支持注释和更友好的配置体验。同时集成 IM Channels 配置。

## 价值点

1. **TOML 配置支持**
   - 添加 `tomli` (Python < 3.11) 和 `tomli-w` 依赖
   - 配置加载优先级: `config.toml` > `config.json`
   - 向后兼容 JSON 格式

2. **配置模板文件** (`config.template.toml`)
   - 包含所有可配置参数
   - 每个参数都有详细的中文注释
   - 分组清晰：agent, llm, providers, channels, security, memory, compression 等

3. **IM Channels 配置集成**
   - CLI Channel 配置
   - 飞书 Channel: app_id, app_secret, encrypt_key, verification_token
   - Discord Channel: token, group_policy

4. **CLI 命令增强**
   - `anyclaw config init --format toml` - 创建 TOML 配置模板
   - `anyclaw config template` - 显示配置模板
   - `anyclaw config migrate` - JSON → TOML 迁移
   - `anyclaw config set feishu.*` / `discord.*` - IM 配置支持

## 修改的文件

- `pyproject.toml` - 添加 tomli 和 tomli-w 依赖
- `anyclaw/config/loader.py` - 重写为支持 TOML/JSON 双格式
- `anyclaw/config/config.template.toml` - 新增配置模板
- `anyclaw/cli/config_cmd.py` - 增强配置命令

## 配置文件位置

```
~/.anyclaw/config.toml  (推荐)
~/.anyclaw/config.json  (向后兼容)
```

## 使用示例

```bash
# 初始化 TOML 配置
anyclaw config init --format toml

# 编辑配置（打开编辑器）
anyclaw config edit

# 设置飞书配置
anyclaw config set feishu.enabled true
anyclaw config set feishu.app_id your_app_id

# 设置 Discord 配置
anyclaw config set discord.enabled true
anyclaw config set discord.token your_bot_token

# 查看配置
anyclaw config show

# 查看模板
anyclaw config template
```

## 测试

所有配置测试通过：
```
tests/test_config.py - 5 passed
```
