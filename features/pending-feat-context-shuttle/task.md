# 任务分解：上下文穿梭

## 概述

实现"上下文穿梭"机制，通过"选择-穿梭-执行"模式减少技能加载对上下文的占用。

---

## 任务列表

### Phase 1: 核心基础设施

- [ ] **T1.1 技能摘要生成（含 description）**
  - 在 `SkillLoader` 中确认 `build_skill_summary()` 包含 name + description
  - XML 格式输出，方便 LLM 理解
  - 确保每个技能有简短但清晰的描述

- [ ] **T1.2 SessionSkillCache 会话缓存**
  - 创建 `anyclaw/session/skill_cache.py`
  - 实现 `loaded_skills` 字典缓存
  - 实现 `get/set/has/get_all_loaded` 方法

### Phase 2: 穿梭机制

- [ ] **T2.1 选择结果解析器**
  - 创建 `anyclaw/agent/selection_parser.py`
  - 从 LLM 自然语言回答中提取技能名称
  - 支持多种回答格式（列表、叙述等）

- [ ] **T2.2 ContextShuttle 穿梭处理器**
  - 创建 `anyclaw/agent/shuttle.py`
  - 实现两阶段处理流程（选择 → 穿梭 → 执行）
  - 实现技能列表删除逻辑
  - 集成会话缓存

- [ ] **T2.3 AgentLoop 集成**
  - 修改 `anyclaw/agent/loop.py`
  - 添加穿梭模式开关
  - 调用 `ContextShuttle.process_with_shuttle()`

### Phase 3: 配置与优化

- [ ] **T3.1 配置项支持**
  - 在 `settings.py` 添加 `[context_shuttle]` 配置组
  - `enabled`, `cache_across_session`, `max_shuttles_per_turn`

- [ ] **T3.2 Always 技能兼容**
  - 穿梭时跳过 Always 技能
  - Always 技能自动预加载到上下文
  - 避免重复加载

### Phase 4: 测试

- [ ] **T4.1 单元测试**
  - `test_skill_cache.py` - 缓存逻辑
  - `test_selection_parser.py` - 选择解析
  - `test_context_shuttle.py` - 穿梭流程

- [ ] **T4.2 集成测试**
  - `test_shuttle_integration.py` - AgentLoop 集成
  - Token 节省验证

---

## 依赖关系

```
T1.1 ─┬─→ T2.1 ─→ T2.2 ─→ T2.3 ─→ T4.2
      │
T1.2 ─┘
                      ↓
              T3.1 ──→ T3.2
```

---

## 预估工作量

| Phase | 任务数 | 预估 |
|-------|--------|------|
| Phase 1 | 2 | 0.5 天 |
| Phase 2 | 3 | 1 天 |
| Phase 3 | 2 | 0.5 天 |
| Phase 4 | 2 | 0.5 天 |
| **总计** | **9** | **2.5 天** |
