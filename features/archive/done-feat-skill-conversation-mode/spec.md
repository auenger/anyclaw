# Feature: 技能对话模式 (skill-conversation-mode)

> ID: feat-skill-conversation-mode
> Priority: 85
> Size: M
> Status: pending
> Created: 2026-03-19

## 背景

当前 AnyClaw 的技能系统需要通过 CLI 命令创建，新创建的技能需要重启 chat 会话才能使用。参考 nanobot 和 openclaw 的实现，可以让 Agent 在对话中动态创建和使用技能。

## 目标

让 Agent 能够在对话中：
1. 创建新技能（通过 skill-creator 内置技能指导）
2. 编辑现有技能
3. 立即使用新创建的技能（热重载）

## 用户价值点

### VP1: skill-creator 内置技能

**描述**: Agent 通过读取这个技能学会如何创建/编辑/打包技能

**参考实现**: `reference/nanobot/nanobot/skills/skill-creator/`

**Gherkin 场景**:

```gherkin
Feature: skill-creator 内置技能

  Scenario: Agent 读取 skill-creator 技能
    Given 用户询问 "如何创建一个新技能"
    When Agent 需要创建技能
    Then Agent 应该能够读取 skill-creator 技能的内容
    And 获得技能创建的完整指南

  Scenario: Agent 按指南创建技能
    Given Agent 读取了 skill-creator 技能
    When 用户请求创建一个 "my-helper" 技能
    Then Agent 应该能够创建正确的 SKILL.md 文件
    And 包含有效的 YAML frontmatter
    And 包含 name 和 description 字段

  Scenario: Agent 创建带资源的技能
    Given Agent 正在创建技能
    When 技能需要脚本或参考文档
    Then Agent 应该能够创建 scripts/ 目录
    And 能够创建 references/ 目录
    And 能够创建 assets/ 目录
```

### VP2: 技能热重载

**描述**: 新创建的技能无需重启 chat 立即可用

**参考实现**: `reference/openclaw/src/agents/skills/refresh.ts`

**Gherkin 场景**:

```gherkin
Feature: 技能热重载

  Scenario: 检测新技能文件
    Given Agent 正在 chat 会话中
    When 在 skills/ 目录下创建新的 SKILL.md 文件
    Then 系统应该检测到新技能
    And 自动加载到技能列表中

  Scenario: 检测技能文件修改
    Given 技能 "my-helper" 已加载
    When SKILL.md 文件被修改
    Then 系统应该重新加载该技能
    And 下一次对话使用更新后的内容

  Scenario: 手动触发热重载
    Given Agent 需要刷新技能列表
    When 调用 reload_skills 工具或命令
    Then 所有技能应该被重新加载
    And 返回加载统计信息

  Scenario: 删除技能文件
    Given 技能 "old-skill" 已加载
    When SKILL.md 文件被删除
    Then 该技能应该从技能列表中移除
```

### VP3: 技能工具函数

**描述**: Agent 可调用的 create_skill/reload_skill 等工具

**Gherkin 场景**:

```gherkin
Feature: 技能工具函数

  Scenario: 使用 create_skill 工具
    Given Agent 需要创建技能
    When 调用 create_skill 工具
      | name | "my-skill" |
      | description | "A helper skill" |
      | resources | "scripts,references" |
    Then 应该在正确位置创建技能目录
    And 返回创建的路径

  Scenario: 使用 reload_skill 工具
    Given Agent 创建了新技能
    When 调用 reload_skill 工具（无参数）
    Then 应该重新加载所有技能
    And 返回加载统计

  Scenario: 使用 validate_skill 工具
    Given Agent 创建或修改了技能
    When 调用 validate_skill 工具
      | path | "skills/my-skill" |
    Then 应该验证 SKILL.md 格式
    And 返回验证结果和错误信息

  Scenario: 使用 show_skill 工具
    Given 技能 "my-skill" 存在
    When 调用 show_skill 工具
      | name | "my-skill" |
    Then 应该返回技能的完整信息
    And 包含内容预览和依赖状态
```

## 技术设计

### 1. skill-creator 内置技能

位置: `anyclaw/skills/builtin/skill-creator/`

```
skill-creator/
├── SKILL.md           # 技能创建指南
└── scripts/
    └── init_skill.py  # 初始化脚本（可选，也可内联）
```

SKILL.md 内容参考 nanobot 的实现，包含：
- 技能结构和设计原则
- 创建流程指南
- 模板和示例

### 2. 热重载机制

修改 `anyclaw/skills/loader.py`:
- 添加文件监听（可选，使用 watchdog）
- 或在每次对话开始时检查文件变化
- 提供 `reload_skill()` 和 `reload_all()` 方法（已存在，需暴露给 Agent）

修改 `anyclaw/agent/loop.py`:
- 在处理用户输入前检查技能变化
- 或提供显式的 `/reload` 命令

### 3. 技能工具函数

创建 `anyclaw/tools/skill_tools.py`:
- `CreateSkillTool` - 创建新技能
- `ReloadSkillTool` - 重载技能
- `ValidateSkillTool` - 验证技能
- `ShowSkillTool` - 显示技能详情

注册到 `anyclaw/tools/registry.py`

## 验收标准

- [ ] skill-creator 技能可以被 Agent 读取和使用
- [ ] 在对话中创建的新技能可以立即使用
- [ ] 修改现有技能后下次对话生效
- [ ] 提供完整的技能工具函数
- [ ] 测试覆盖率 > 80%

## 依赖

无外部依赖，依赖现有的技能系统基础设施。

## 风险

| 风险 | 影响 | 缓解措施 |
|------|------|----------|
| 文件监听可能消耗资源 | 中 | 使用轮询或只在对话开始时检查 |
| 技能格式错误导致加载失败 | 低 | 验证后加载，错误不中断会话 |

## 参考

- `reference/nanobot/nanobot/skills/skill-creator/` - nanobot 的 skill-creator 实现
- `reference/openclaw/src/agents/skills/refresh.ts` - openclaw 的热重载实现
- `reference/openclaw/src/agents/skills/workspace.ts` - openclaw 的技能加载
