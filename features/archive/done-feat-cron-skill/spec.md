# Cron 技能实现

## 概述

将现有的 CronTool 功能注册到 AgentLoop 工具系统，同时创建 cron 内置技能，使 Agent 能够通过工具调用或技能两种方式使用定时任务功能。

## 背景问题

当前 AnyClaw 已经有完整的 cron 实现：
- `anyclaw/cron/service.py` - CronService 完整实现
- `anyclaw/cron/tool.py` - CronTool 完整实现（支持 add/list/remove）
- `anyclaw/cron/types.py` - 类型定义

**但存在以下问题**：
1. `AgentLoop._register_default_tools()` 中没有注册 CronTool
2. 内置技能目录 (`skills/builtin/`) 中没有 cron 技能
3. Agent 在对话时无法识别和使用 cron 功能

## 用户价值点

### 价值点 1: CronTool 注册到工具系统

**场景**:
```gherkin
Feature: CronTool 工具注册
  As an Agent
  I want to use cron tool via function calling
  So that I can schedule reminders and recurring tasks

  Scenario: 添加定时任务
    Given AgentLoop 已初始化
    When LLM 调用 cron 工具 with action="add", message="提醒我喝水", every_seconds=3600
    Then 系统应创建定时任务
    And 返回任务 ID

  Scenario: 列出定时任务
    Given 系统中有 2 个定时任务
    When LLM 调用 cron 工具 with action="list"
    Then 系统应返回所有任务列表

  Scenario: 删除定时任务
    Given 系统中有任务 "abc123"
    When LLM 调用 cron 工具 with action="remove", job_id="abc123"
    Then 系统应删除该任务
```

### 价值点 2: Cron 内置技能创建

**场景**:
```gherkin
Feature: Cron 内置技能
  As an Agent
  I want to use cron skill
  So that I can schedule tasks through skill interface

  Scenario: 技能被加载
    Given SkillLoader 加载内置技能
    Then cron 技能应在技能列表中
    And 技能描述应清晰说明功能

  Scenario: 技能摘要显示
    Given Agent 构建上下文
    When 调用 build_skills_summary()
    Then 输出应包含 cron 技能信息
```

### 价值点 3: CronTool 上下文集成

**场景**:
```gherkin
Feature: CronTool 上下文集成
  As a Channel
  I want to set cron context for delivery
  So that cron jobs can deliver messages to correct session

  Scenario: 设置上下文
    Given Channel 启动 AgentLoop
    When 调用 set_cron_context(channel, chat_id)
    Then CronTool 应能正确投递定时任务消息

  Scenario: 定时任务触发
    Given 有一个每 60 秒的定时任务
    When 任务触发时
    Then 系统应向正确的 channel/chat_id 发送消息
```

## 技术设计

### 方案概述

采用"工具+技能"双轨制：

1. **工具层**：将 CronTool 注册到 AgentLoop，支持 function calling
2. **技能层**：创建 `skills/builtin/cron/` 技能，提供 SKILL.md 文档

### 实现要点

1. **AgentLoop 修改**：
   - 在 `_register_default_tools()` 中创建并注册 CronTool
   - 添加 `set_cron_context()` 方法供 Channel 调用
   - 需要 CronService 实例管理

2. **CronService 初始化**：
   - AgentLoop 持有 CronService 实例
   - 启动时调用 `cron_service.start()`
   - 关闭时调用 `cron_service.stop()`

3. **CronTool 上下文**：
   - 需要设置 channel/chat_id 以便投递消息
   - 参考 MessageTool 的上下文设置模式

4. **Cron 技能创建**：
   - 创建 `skills/builtin/cron/skill.py`
   - 创建 `skills/builtin/cron/SKILL.md`
   - 技能描述 cron 功能的使用方法

## 验收标准

- [ ] CronTool 在 AgentLoop 初始化时被注册
- [ ] Agent 可以通过 function calling 使用 cron 工具
- [ ] Cron 技能在技能列表中可见
- [ ] Channel 可以设置 cron 上下文
- [ ] 定时任务可以正确触发并投递消息
- [ ] 所有测试通过

## 依赖

- 无前置依赖

## 风险

- CronService 需要异步启动，可能影响 AgentLoop 初始化时间
- 需要正确处理 CronService 的生命周期（启动/关闭）
