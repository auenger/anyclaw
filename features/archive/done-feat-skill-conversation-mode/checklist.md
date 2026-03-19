# Checklist: 技能对话模式 (feat-skill-conversation-mode)

## Phase 1: skill-creator 内置技能

### Task 1.1: 创建目录结构
- [x] 创建 `anyclaw/skills/builtin/skill-creator/` 目录
- [x] 创建 `scripts/` 子目录

### Task 1.2: 编写 SKILL.md
- [x] 编写技能概述和核心原则
- [x] 编写技能结构说明 (SKILL.md, scripts/, references/, assets/)
- [x] 编写技能创建流程 (6 步骤)
- [x] 编写技能命名规范
- [x] 添加设计模式参考
- [x] 添加模板示例

### Task 1.3: 验证加载
- [x] 确认 builtin 目录被 SkillLoader 扫描
- [x] 确认 skill-creator 技能出现在技能列表
- [x] 确认 Agent 能读取技能内容

---

## Phase 2: 技能工具函数

### Task 2.1: 创建工具模块
- [x] 创建 `anyclaw/tools/skill_tools.py`
- [x] 实现 `CreateSkillTool` 类
  - [x] name 参数验证 (hyphen-case, 长度限制)
  - [x] description 参数
  - [x] resources 参数 (scripts, references, assets)
  - [x] 创建目录和模板文件
- [x] 实现 `ReloadSkillTool` 类
  - [x] 无参数时重载所有技能
  - [x] 有参数时重载指定技能
  - [x] 返回重载统计信息
- [x] 实现 `ValidateSkillTool` 类
  - [x] 验证 SKILL.md 格式
  - [x] 验证 frontmatter 字段
  - [x] 返回验证结果和错误
- [x] 实现 `ShowSkillTool` 类
  - [x] 显示技能元信息
  - [x] 显示内容预览
- [x] 实现 `ListSkillsTool` 类
  - [x] 列出所有技能

### Task 2.2: 注册工具
- [x] 创建 `register_skill_tools()` 函数
- [x] 工具描述清晰，Agent 能理解用途

### Task 2.3: AgentLoop 集成
- [x] 提供集成接口 (skill_loader 参数)

---

## Phase 3: 技能热重载

### Task 3.1: 变化检测
- [x] 在 `SkillLoader` 添加 `get_skills_mtime()` 方法
- [x] 在 `SkillLoader` 添加 `has_skills_changed()` 方法
- [x] 记录上次加载时间戳 (`_last_mtime`)

### Task 3.2: 自动重载
- [x] 添加 `auto_reload_if_changed()` 方法
- [x] 返回重载统计或 None

### Task 3.3: 文件监听 (可选)
- [ ] 使用 watchdog 监听 SKILL.md 文件 (未实现，优先级低)

---

## Phase 4: 测试和文档

### Task 4.1: 单元测试
- [x] 创建 `tests/test_skill_conversation_mode.py`
- [x] test_skill_creator_loaded
- [x] test_create_skill_tool
- [x] test_reload_skill_tool
- [x] test_validate_skill_tool
- [x] test_hot_reload_detection
- [x] 23 个测试全部通过

### Task 4.2: 文档更新
- [x] 更新 `tests/CLI_TEST_SCENARIOS.md`
- [x] 添加技能对话测试场景

---

## 验收标准

### 功能验收
- [x] Agent 能读取 skill-creator 技能
- [x] Agent 能使用 CreateSkillTool 创建技能
- [x] Agent 能使用 ReloadSkillTool 重载技能
- [x] Agent 能使用 ValidateSkillTool 验证技能
- [x] 新创建的技能可以立即使用
- [x] 修改现有技能后下次对话生效

### 质量验收
- [x] 所有测试通过 (23/23)
- [x] 代码通过 Black 格式化
- [x] 代码通过 Ruff 检查
- [x] 无类型错误

### 文档验收
- [x] CLI 测试场景文档更新
- [x] 代码有适当注释

---

## 完成记录

**开始时间**: 2026-03-19T23:30:00
**完成时间**: 2026-03-19T23:45:00
**实际耗时**: ~15分钟
**遇到的问题**: 无
**解决方案**: N/A

## 实现摘要

### 新增文件
1. `anyclaw/skills/builtin/skill-creator/SKILL.md` - skill-creator 内置技能
2. `anyclaw/tools/skill_tools.py` - 技能工具函数模块
3. `tests/test_skill_conversation_mode.py` - 完整测试套件

### 修改文件
1. `anyclaw/skills/loader.py` - 添加热重载检测方法
2. `anyclaw/skills/toolkit/__init__.py` - 更新导出
3. `tests/CLI_TEST_SCENARIOS.md` - 添加测试场景

### 工具函数列表
| 工具名 | 功能 |
|--------|------|
| `create_skill` | 创建新技能 |
| `reload_skill` | 重载技能 |
| `validate_skill` | 验证技能格式 |
| `show_skill` | 显示技能详情 |
| `list_skills` | 列出所有技能 |
