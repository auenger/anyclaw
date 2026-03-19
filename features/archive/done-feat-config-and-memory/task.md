# 任务清单

## Phase 1: 配置文件系统

- [x] 创建 `config/loader.py` - JSON 配置加载器
- [x] 定义配置 Schema（Config, LLMConfig, ProviderConfig）
- [x] 实现 `load_config()` 和 `save_config()` 函数
- [x] 修改 `settings.py` 集成配置文件加载

## Phase 2: 记忆工具

- [x] 创建 `tools/memory.py`
- [x] 实现 `SaveMemoryTool` - 保存历史和长期记忆
- [x] 实现 `UpdatePersonaTool` - 更新 SOUL.md 和 USER.md
- [x] 在 `AgentLoop` 中注册新工具

## Phase 3: ContextBuilder 增强

- [x] 修改 `agent/context.py`
- [x] 集成 `PersonaLoader` 加载人设文件
- [x] 集成 `MemoryManager` 加载长期记忆
- [x] 构建完整的系统提示词

## Phase 4: ZAI Provider 优化

- [x] 修改默认 endpoint 为 `coding`
- [x] 更新默认 base URL
- [x] 支持 `zai/` 模型前缀转换
- [x] 处理 `_model_override` 参数

## Phase 5: CLI 命令

- [x] 创建 `cli/config_cmd.py`
- [x] 实现 `config init` 命令
- [x] 实现 `config show` 命令
- [x] 实现 `config set` 命令
- [x] 实现 `config path` 命令
- [x] 实现 `config edit` 命令
- [x] 注册到主 CLI 应用

## Phase 6: 清理和提交

- [x] 移除所有第三方项目引用
- [x] 更新 pyproject.toml 入口点
- [x] 测试完整流程
- [x] 提交代码
