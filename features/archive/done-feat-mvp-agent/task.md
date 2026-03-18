# Task: Agent 引擎核心

## 任务概述
实现 AnyClaw 的核心 Agent 引擎

## 任务列表

### 阶段 1: 对话历史管理 (已完成)
- [x] 创建 Message 数据类
- [x] 实现 ConversationHistory 类
- [x] 支持最大历史长度限制 (deque)
- [x] 实现历史记录的添加和获取

### 阶段 2: 上下文构建 (已完成)
- [x] 创建 ContextBuilder 类
- [x] 实现系统提示词构建
- [x] 实现技能信息注入
- [x] 整合历史对话

### 阶段 3: Agent 主循环 (已完成)
- [x] 创建 AgentLoop 类
- [x] 集成 litellm 进行 LLM 调用
- [x] 实现异步处理流程
- [x] 添加错误处理

### 阶段 4: 测试 (已完成)
- [x] 编写 ConversationHistory 单元测试
- [x] 编写 AgentLoop 测试框架

## 实际耗时
约 4-5 小时

## 备注
核心 Agent 功能已完整实现，支持扩展
