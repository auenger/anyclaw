# 验收清单

## 功能验收

### 配置文件系统
- [x] `anyclaw config init` 创建默认配置文件
- [x] `anyclaw config show` 显示当前配置
- [x] `anyclaw config set zai.api_key xxx` 设置 API key
- [x] `anyclaw config set llm.model glm-4.7` 设置模型
- [x] 配置文件正确保存到 `~/.anyclaw/config.json`

### 记忆工具
- [x] `save_memory` 工具可以保存历史记录
- [x] `save_memory` 工具可以更新长期记忆
- [x] `update_persona` 工具可以更新 SOUL.md
- [x] `update_persona` 工具可以更新 USER.md

### ContextBuilder
- [x] 系统提示词包含 SOUL.md 内容
- [x] 系统提示词包含 USER.md 内容
- [x] 系统提示词包含 MEMORY.md 内容
- [x] 系统提示词包含 TOOLS.md 内容

### ZAI Provider
- [x] 默认使用 `coding` endpoint
- [x] Base URL 为 `https://open.bigmodel.cn/api/coding/paas/v4`
- [x] `zai/glm-4.7` 模型名正确转换
- [x] API 调用成功返回响应

### 命令行入口
- [x] `anyclaw` 命令可用（需要 pip install -e .）
- [x] `anyclaw chat` 正常启动
- [x] `anyclaw config` 子命令可用

## 代码质量

- [x] 无第三方项目引用
- [x] 代码格式符合项目规范
- [x] 无敏感信息泄露

## 测试

- [x] 配置文件加载测试通过
- [x] 记忆工具测试通过
- [x] 完整对话流程测试通过

## 提交

- [x] Git 提交完成
- [x] 提交信息清晰
- [x] 归档到 features/archive
