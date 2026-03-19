# Task: 技能对话模式 (feat-skill-conversation-mode)

## 任务分解

### Phase 1: skill-creator 内置技能

#### Task 1.1: 创建 skill-creator 技能目录结构
**文件**: `anyclaw/skills/builtin/skill-creator/`
**描述**: 创建内置技能目录和 SKILL.md 文件
**估计**: 30min

```bash
mkdir -p anyclaw/skills/builtin/skill-creator/scripts
```

#### Task 1.2: 编写 SKILL.md 内容
**文件**: `anyclaw/skills/builtin/skill-creator/SKILL.md`
**描述**: 基于 nanobot 参考实现，编写技能创建指南
**依赖**: Task 1.1
**估计**: 1h

内容包含：
- 技能概述和核心原则
- 技能结构说明 (SKILL.md, scripts/, references/, assets/)
- 技能创建流程 (6 步骤)
- 技能命名规范
- 设计模式参考

#### Task 1.3: 确保内置技能被正确加载
**文件**: `anyclaw/skills/loader.py`
**描述**: 验证 builtin 目录下的技能能被 SkillLoader 加载
**依赖**: Task 1.2
**估计**: 15min

---

### Phase 2: 技能工具函数

#### Task 2.1: 创建技能工具模块
**文件**: `anyclaw/tools/skill_tools.py`
**描述**: 创建 Agent 可调用的技能工具函数
**估计**: 2h

工具列表：
- `CreateSkillTool` - 创建新技能目录和 SKILL.md
- `ReloadSkillTool` - 重载技能列表
- `ValidateSkillTool` - 验证技能格式
- `ShowSkillTool` - 显示技能详情

#### Task 2.2: 注册技能工具
**文件**: `anyclaw/tools/registry.py`
**描述**: 将技能工具注册到工具注册表
**依赖**: Task 2.1
**估计**: 15min

#### Task 2.3: 在 AgentLoop 中集成技能工具
**文件**: `anyclaw/agent/loop.py`
**描述**: 确保 AgentLoop 能调用技能工具
**依赖**: Task 2.2
**估计**: 30min

---

### Phase 3: 技能热重载

#### Task 3.1: 添加技能变化检测
**文件**: `anyclaw/skills/loader.py`
**描述**: 添加检测技能文件变化的方法
**估计**: 45min

实现：
- `get_skills_mtime()` - 获取技能目录修改时间
- `has_skills_changed()` - 检测是否有变化

#### Task 3.2: 在对话开始时自动重载
**文件**: `anyclaw/agent/loop.py`
**描述**: 在处理用户输入前检查并重载技能
**依赖**: Task 3.1
**估计**: 30min

逻辑：
```python
async def process(self, user_input: str) -> str:
    # 检查技能变化
    if self.skill_loader.has_skills_changed():
        self.skill_loader.reload_all()
    # ... 继续正常处理
```

#### Task 3.3: 可选 - 添加文件监听
**文件**: `anyclaw/skills/watcher.py` (新建)
**描述**: 使用 watchdog 监听技能目录变化（可选优化）
**依赖**: Task 3.1
**估计**: 1h
**优先级**: 低

---

### Phase 4: 测试和文档

#### Task 4.1: 编写单元测试
**文件**: `tests/test_skill_conversation_mode.py`
**描述**: 测试技能对话模式的各项功能
**估计**: 1.5h

测试用例：
- test_skill_creator_loaded
- test_create_skill_tool
- test_reload_skill_tool
- test_validate_skill_tool
- test_hot_reload_detection

#### Task 4.2: 更新 CLI 测试场景文档
**文件**: `tests/CLI_TEST_SCENARIOS.md`
**描述**: 添加技能对话模式的测试场景
**估计**: 15min

---

## 任务依赖图

```
Phase 1 (skill-creator)
├── Task 1.1 (目录结构)
│   └── Task 1.2 (SKILL.md)
│       └── Task 1.3 (加载验证)

Phase 2 (工具函数)
├── Task 2.1 (工具模块)
│   └── Task 2.2 (注册工具)
│       └── Task 2.3 (AgentLoop集成)

Phase 3 (热重载)
├── Task 3.1 (变化检测)
│   ├── Task 3.2 (自动重载)
│   └── Task 3.3 (文件监听) [可选]

Phase 4 (测试)
└── Task 4.1 (单元测试)
    └── Task 4.2 (文档更新)
```

## 关键路径

```
Task 1.1 → Task 1.2 → Task 1.3 → Task 2.1 → Task 2.2 → Task 2.3
                                                       ↓
Task 3.1 → Task 3.2 ──────────────────────────────→ Task 4.1 → Task 4.2
```

## 总估计

| Phase | 时间 |
|-------|------|
| Phase 1 | 1h 45min |
| Phase 2 | 2h 45min |
| Phase 3 | 1h 15min |
| Phase 4 | 1h 45min |
| **总计** | **7h 30min** |

## 实现顺序建议

1. **Phase 1** - 先让 Agent 能读取创建指南
2. **Phase 2** - 提供工具函数让 Agent 能执行操作
3. **Phase 3** - 实现热重载让新技能立即可用
4. **Phase 4** - 完善测试和文档
