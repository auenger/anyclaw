# Task: 项目初始化和配置系统

## 任务概述
创建 AnyClaw 项目的基础架构

## 任务列表

### 阶段 1: 项目结构 (已完成)
- [x] 创建 anyclaw/ 主包目录
- [x] 创建 config/ 配置模块
- [x] 创建 tests/ 测试目录

### 阶段 2: Poetry 配置 (已完成)
- [x] 创建 pyproject.toml
- [x] 配置核心依赖 (pydantic, pydantic-settings, typer, rich, litellm, openai)
- [x] 配置开发依赖 (pytest, pytest-asyncio, black, ruff)

### 阶段 3: 配置系统 (已完成)
- [x] 实现 Settings 类
- [x] 定义配置字段 (agent_name, llm_model, api_keys 等)
- [x] 实现环境变量加载

### 阶段 4: 开发工具 (已完成)
- [x] 配置 Black (line-length=100)
- [x] 配置 Ruff (E, F, I, N, W 规则)
- [ ] 配置 Pre-commit hooks (待完成)

### 阶段 5: 文档和示例 (已完成)
- [x] 创建 .env.example
- [x] 编写配置单元测试

## 实际耗时
约 2-3 小时

## 备注
基础架构已可用于后续开发
