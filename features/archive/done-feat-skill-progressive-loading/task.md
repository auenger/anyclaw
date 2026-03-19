# Task: Skill 渐进式加载

## 任务分解

### Phase 1: SkillsLoader 增强

#### Task 1.1: 增强 SkillsLoader 基础方法
**文件**: `anyclaw/skills/loader.py`
**内容**:
- [x] 添加 `build_skills_summary()` 方法
- [x] 添加 `load_skills_for_context()` 方法
- [x] 添加 `_strip_frontmatter()` 辅助方法
- [x] 添加 `_get_skill_description()` 方法

#### Task 1.2: 依赖检查系统
**文件**: `anyclaw/skills/loader.py`
**内容**:
- [x] 添加 `_check_requirements()` 方法
- [x] 添加 `_get_missing_requirements()` 方法
- [x] 添加 `_parse_nanobot_metadata()` 方法
- [x] 支持 bins 和 env 依赖检查

#### Task 1.3: Always Skills 支持
**文件**: `anyclaw/skills/loader.py`
**内容**:
- [x] 添加 `get_always_skills()` 方法
- [x] 解析 frontmatter 中的 always 标记
- [x] 依赖检查 + always 标记过滤

### Phase 2: Scripts 执行

#### Task 2.1: 脚本执行器
**文件**: `anyclaw/skills/executor.py` (新文件)
**内容**:
- [x] `SkillScriptExecutor` 类
- [x] `execute_script(skill_name, script_path, args)` 方法
- [x] 支持 Python 脚本执行
- [x] 支持 Shell 脚本执行
- [x] 工作目录设置为 skill 目录
- [x] 超时和错误处理

### Phase 3: Context 集成

#### Task 3.1: ContextBuilder 集成
**文件**: `anyclaw/agent/context.py`
**内容**:
- [x] 在上下文中包含 skills summary
- [x] 自动加载 always skills
- [x] 添加 skill 内容加载方法

### Phase 4: 元数据模型增强

#### Task 4.1: 更新 models.py
**文件**: `anyclaw/skills/models.py`
**内容**:
- [x] 添加 `always: bool` 字段到 OpenClawMetadata
- [x] 添加 `scripts: List[str]` 字段
- [x] 添加 `references: List[str]` 字段

### Phase 5: 测试

#### Task 5.1: 单元测试
**文件**: `tests/test_skill_loader.py`
**内容**:
- [x] build_skills_summary 测试
- [x] load_skills_for_context 测试
- [x] 依赖检查测试
- [x] always skills 测试
- [x] scripts 执行测试

## 执行顺序

1. Task 4.1 - 先更新数据模型
2. Task 1.1 + 1.2 - 增强 loader 基础功能
3. Task 1.3 - always skills 支持
4. Task 2.1 - scripts 执行
5. Task 3.1 - context 集成
6. Task 5.1 - 测试

## 依赖关系

```
models.py ──> loader.py ──> executor.py
                  │
                  └──> context.py
```

## 预计工作量

| 阶段 | 预计时间 |
|------|----------|
| Phase 1 | 2h |
| Phase 2 | 1.5h |
| Phase 3 | 1h |
| Phase 4 | 0.5h |
| Phase 5 | 1h |
| **总计** | **6h** |
