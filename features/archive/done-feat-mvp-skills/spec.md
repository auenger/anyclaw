# Feature Spec: 技能系统

## 元数据
- **ID**: feat-mvp-skills
- **名称**: 技能系统
- **优先级**: 85
- **尺寸**: M
- **状态**: completed
- **创建日期**: 2026-03-18
- **完成日期**: 2026-03-18
- **依赖**: feat-mvp-agent

## 描述
实现 AnyClaw 的技能系统，支持动态加载和执行技能，允许 Agent 调用各种工具能力。

## 用户价值点

### 价值点: 技能调用功能
Agent 可以调用各种技能来扩展其能力。

**Gherkin 场景**:
```gherkin
Scenario: Agent 知道可用技能
  Given 技能目录中有 echo 和 time 技能
  When 启动 Agent
  Then 系统提示词中应该包含技能描述

Scenario: 执行技能
  Given EchoSkill 已加载
  When 调用 execute_skill("EchoSkill", message="Hello")
  Then 应该返回 "Echo: Hello"
```

## 技术栈
- Python ABC (抽象基类)
- importlib (动态导入)

## 实现文件
- `anyclaw/anyclaw/skills/base.py` - Skill 抽象基类
- `anyclaw/anyclaw/skills/loader.py` - SkillLoader 动态加载器
- `anyclaw/anyclaw/skills/builtin/echo/skill.py` - EchoSkill 示例
- `anyclaw/anyclaw/skills/builtin/time/skill.py` - TimeSkill 示例
- `anyclaw/tests/test_skills.py` - 技能测试

## 验收标准
- [x] Skill 基类定义清晰
- [x] SkillLoader 可以动态加载技能
- [x] 至少 2 个示例技能已实现
- [x] 技能信息注入到 Agent 上下文

## 完成说明
技能系统已完成，包括：
- Skill 基类: 抽象基类，定义 execute() 接口
- SkillLoader: 动态加载 builtin 目录下的技能
- 内置技能: EchoSkill (回显), TimeSkill (获取时间)
- 技能信息自动注入到系统提示词
