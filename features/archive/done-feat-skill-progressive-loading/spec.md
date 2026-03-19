# Feature: Skill 渐进式加载

## 概述

实现 OpenClaw 风格的渐进式 skill 加载系统，支持按需加载、依赖检查和 scripts/ 执行能力。

**优先级**: 75 (中)
**大小**: M
**依赖**: feat-skill-toolkit

## 背景与动机

当前 AnyClaw 的 skill 加载存在问题：
- 所有 skill 内容一次性加载到上下文
- 没有 skills summary 概念
- 不支持 scripts/ 目录的执行
- 不支持 references/ 按需读取
- 没有 `always` 标记自动加载

OpenClaw 使用三层渐进式加载：
1. Metadata (name + description) - 始终在上下文
2. SKILL.md body - 当 skill 触发时加载
3. References - 按需读取

## 用户价值点

### VP1: Skills Summary 构建

系统能够构建简洁的 skills 摘要供 LLM 参考。

```gherkin
Feature: Skills Summary

  Scenario: 构建技能摘要
    Given 系统有多个已安装的 skills
    When 构建上下文时
    Then 生成 XML 格式的 skills summary
    And 包含每个 skill 的 name, description, available 状态
    And 显示依赖缺失原因

  Scenario: 标记不可用的 skill
    Given skill "weather" 需要 "curl" 命令
    And 系统未安装 curl
    When 构建 skills summary
    Then weather skill 标记为 available="false"
    And 显示 <requires>CLI: curl</requires>
```

### VP2: 按需加载 SKILL.md

当 LLM 决定使用某个 skill 时才加载完整内容。

```gherkin
Feature: 按需加载

  Scenario: 读取 skill 内容
    Given skill "pdf-editor" 存在
    When LLM 请求加载 skill 内容
    Then 返回 SKILL.md body（不含 frontmatter）
    And 内容可用于上下文构建

  Scenario: 读取 references 文件
    Given skill 有 references/api.md 文件
    When LLM 需要参考文档
    Then 能读取 references/ 下的文件
    And 路径相对于 skill 目录
```

### VP3: Scripts 执行支持

支持执行 skill 内的脚本文件。

```gherkin
Feature: Scripts 执行

  Scenario: 执行 Python 脚本
    Given skill 有 scripts/helper.py
    When 执行 "skill.exec pdf-editor scripts/helper.py --arg value"
    Then 在 skill 目录下执行脚本
    And 返回执行结果

  Scenario: 执行 Shell 脚本
    Given skill 有 scripts/deploy.sh
    When 执行脚本
    Then 使用 bash 执行
    And 捕获 stdout/stderr
```

### VP4: Always Skills 自动加载

支持 `always=true` 的 skill 自动加载到上下文。

```gherkin
Feature: Always Skills

  Scenario: 获取 always skills
    Given skill "project-context" 标记为 always=true
    When 构建上下文
    Then project-context 自动包含在上下文中

  Scenario: Always skill 依赖检查
    Given always skill 依赖未满足
    When 构建上下文
    Then 该 skill 不被包含
    And 记录警告日志
```

## 技术设计

### SkillsLoader 增强

```python
class SkillsLoader:
    def __init__(self, workspace: Path, builtin_skills_dir: Path | None = None):
        ...

    # 现有方法
    def list_skills(self, filter_unavailable: bool = True) -> list[dict]: ...
    def load_skill(self, name: str) -> str | None: ...

    # 新增方法
    def build_skills_summary(self) -> str: ...
    def load_skills_for_context(self, skill_names: list[str]) -> str: ...
    def get_always_skills(self) -> list[str]: ...
    def check_requirements(self, skill_name: str) -> tuple[bool, list[str]]: ...
    def execute_script(self, skill_name: str, script_path: str, args: list[str]) -> str: ...
```

### XML Summary 格式

```xml
<skills>
  <skill available="true">
    <name>pdf-editor</name>
    <description>Edit and manipulate PDF files</description>
    <location>/path/to/skills/pdf-editor/SKILL.md</location>
  </skill>
  <skill available="false">
    <name>weather</name>
    <description>Get weather information</description>
    <location>/path/to/skills/weather/SKILL.md</location>
    <requires>CLI: curl</requires>
  </skill>
</skills>
```

### 目录结构

```
skill-name/
├── SKILL.md           # 必需
├── scripts/           # 可执行脚本
│   ├── helper.py
│   └── deploy.sh
├── references/        # 参考文档（按需读取）
│   ├── api.md
│   └── schema.md
└── assets/            # 静态资源（不加载）
    └── template.html
```

### Frontmatter 扩展

```yaml
---
name: skill-name
description: 描述
metadata:
  openclaw:
    always: true           # 新增：自动加载
    requires:
      bins: [curl, jq]
      env: [API_KEY]
---
```

## 验收标准

- [x] `build_skills_summary()` 生成 XML 格式摘要
- [x] `load_skills_for_context()` 按需加载 skill 内容
- [x] `get_always_skills()` 返回 always=true 的 skills
- [x] 依赖检查正确标记 unavailable skills
- [x] scripts/ 执行功能正常工作
- [x] references/ 文件可被读取
- [x] 有完整的单元测试
