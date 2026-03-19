# Feature: Skill 工具链

## 概述

为 AnyClaw 添加完整的 Skill 开发工具链，包括创建、验证、打包和 CLI 管理功能。

**优先级**: 90 (高)
**大小**: M
**依赖**: 无

## 背景与动机

当前 AnyClaw 的 skill 系统缺少必要的开发工具：
- 用户需要手动创建 skill 目录和 SKILL.md 文件
- 没有验证工具检查 skill 格式正确性
- 没有打包工具分发 skill
- 缺少 CLI 命令管理 skill

参考 OpenClaw 的 skill-creator 工具链，我们需要补充这些缺失的能力。

## 用户价值点

### VP1: Skill 创建向导

用户可以通过命令快速创建符合规范的 skill 模板。

```gherkin
Feature: Skill 创建向导

  Scenario: 创建基础 skill
    Given 用户想要创建名为 "my-helper" 的新 skill
    When 用户执行 "anyclaw skill create my-helper"
    Then 系统在当前目录创建 my-helper/ 目录
    And 目录包含 SKILL.md 模板文件
    And SKILL.md 包含正确的 YAML frontmatter

  Scenario: 创建带资源目录的 skill
    Given 用户想要创建带有脚本的 skill
    When 用户执行 "anyclaw skill create my-skill --resources scripts,references"
    Then 系统创建 scripts/ 和 references/ 子目录
    And 可选创建示例文件 (使用 --examples 标志)

  Scenario: 指定输出路径
    Given 用户想要在特定位置创建 skill
    When 用户执行 "anyclaw skill create my-skill --path ~/.anyclaw/skills"
    Then 系统在指定路径创建 skill 目录
```

### VP2: Skill 验证工具

用户可以验证 skill 格式是否符合规范。

```gherkin
Feature: Skill 验证

  Scenario: 验证有效的 skill
    Given 存在一个格式正确的 skill 目录
    When 用户执行 "anyclaw skill validate ./my-skill"
    Then 系统返回 "Skill is valid!"
    And 退出码为 0

  Scenario: 检测缺失的 frontmatter
    Given skill 的 SKILL.md 缺少 YAML frontmatter
    When 用户执行 "anyclaw skill validate ./my-skill"
    Then 系统返回错误 "Invalid frontmatter format"
    And 退出码为 1

  Scenario: 检测无效的 skill 名称
    Given skill 名称包含非法字符 "My_Skill!"
    When 用户执行 "anyclaw skill validate ./my-skill"
    Then 系统返回错误 "Name should be hyphen-case"
    And 退出码为 1

  Scenario: 检测过长的描述
    Given skill 描述超过 1024 字符
    When 用户执行 "anyclaw skill validate ./my-skill"
    Then 系统返回错误 "Description is too long"
    And 退出码为 1
```

### VP3: Skill 打包工具

用户可以将 skill 打包为可分发的 .skill 文件。

```gherkin
Feature: Skill 打包

  Scenario: 打包 skill
    Given 存在一个有效的 skill 目录
    When 用户执行 "anyclaw skill package ./my-skill"
    Then 系统先验证 skill 格式
    And 创建 my-skill.skill 文件
    And .skill 文件是 ZIP 格式，包含完整目录结构

  Scenario: 指定输出目录
    Given 用户想要输出到特定目录
    When 用户执行 "anyclaw skill package ./my-skill --output ./dist"
    Then 系统在 ./dist/ 目录创建 my-skill.skill

  Scenario: 打包失败时拒绝创建
    Given skill 格式验证失败
    When 用户执行 "anyclaw skill package ./my-skill"
    Then 系统显示验证错误
    And 不创建 .skill 文件
    And 退出码为 1
```

### VP4: Skill CLI 管理

用户可以通过 CLI 管理 skills。

```gherkin
Feature: Skill CLI 管理

  Scenario: 列出已安装的 skills
    Given 系统有多个已安装的 skills
    When 用户执行 "anyclaw skill list"
    Then 系统显示所有 skill 的名称、描述、来源

  Scenario: 安装 skill 从目录
    Given 存在一个 skill 目录
    When 用户执行 "anyclaw skill install ./my-skill"
    Then 系统将 skill 复制到 managed skills 目录
    And 显示安装成功消息

  Scenario: 安装 skill 从 .skill 文件
    Given 存在 my-skill.skill 打包文件
    When 用户执行 "anyclaw skill install ./my-skill.skill"
    Then 系统解压到 managed skills 目录
    And 显示安装成功消息

  Scenario: 显示 skill 详情
    Given 存在已安装的 skill "weather"
    When 用户执行 "anyclaw skill show weather"
    Then 系统显示 skill 的完整信息
    And 包括依赖检查状态
```

## 技术设计

### 目录结构

```
anyclaw/anyclaw/
├── skills/
│   ├── toolkit/              # 新增：工具链模块
│   │   ├── __init__.py
│   │   ├── creator.py        # init_skill 逻辑
│   │   ├── validator.py      # quick_validate 逻辑
│   │   └── packager.py       # package_skill 逻辑
│   └── ...
├── cli/
│   ├── app.py               # 添加 skill 子命令
│   └── skill_cmd.py         # 新增：skill CLI 命令
└── templates/
    └── skill_template.md    # SKILL.md 模板
```

### CLI 命令设计

```bash
anyclaw skill create <name> [options]
  --path PATH         输出目录 (默认: 当前目录)
  --resources LIST    资源目录: scripts,references,assets
  --examples          创建示例文件

anyclaw skill validate <path>
anyclaw skill package <path> [options]
  --output PATH       输出目录 (默认: 当前目录)

anyclaw skill list [--all]
anyclaw skill install <path>
anyclaw skill show <name>
```

### 验证规则

| 字段 | 规则 |
|------|------|
| name | 必需，小写字母+数字+连字符，≤64字符 |
| description | 必需，≤1024字符，不含<> |
| frontmatter | 只允许 name, description, license, metadata |

## 验收标准

- [ ] `anyclaw skill create` 能创建符合规范的 skill 模板
- [ ] `anyclaw skill validate` 能检测所有格式错误
- [ ] `anyclaw skill package` 能打包并验证 skill
- [ ] `anyclaw skill list/show/install` 命令正常工作
- [ ] 与 OpenClaw skill 格式完全兼容
- [ ] 有完整的单元测试
