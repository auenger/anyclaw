# Task: Skill 工具链

## 任务分解

### Phase 1: 核心工具模块

#### Task 1.1: 创建 Skill Creator 模块
**文件**: `anyclaw/skills/toolkit/creator.py`
**内容**:
- [ ] `init_skill(name, path, resources, examples)` 函数
- [ ] SKILL.md 模板生成
- [ ] 资源目录创建 (scripts/, references/, assets/)
- [ ] 名称规范化 (hyphen-case)
- [ ] 示例文件生成

#### Task 1.2: 创建 Skill Validator 模块
**文件**: `anyclaw/skills/toolkit/validator.py`
**内容**:
- [ ] `validate_skill(path)` 函数
- [ ] YAML frontmatter 解析
- [ ] 名称验证规则
- [ ] 描述验证规则
- [ ] 允许字段检查
- [ ] 返回 (valid, message) 元组

#### Task 1.3: 创建 Skill Packager 模块
**文件**: `anyclaw/skills/toolkit/packager.py`
**内容**:
- [ ] `package_skill(path, output_dir)` 函数
- [ ] 先验证后打包
- [ ] ZIP 格式，.skill 扩展名
- [ ] 排除 .git, __pycache__ 等
- [ ] 安全检查（拒绝 symlink）
- [ ] 进度输出

### Phase 2: CLI 命令

#### Task 2.1: 创建 Skill CLI 模块
**文件**: `anyclaw/cli/skill_cmd.py`
**内容**:
- [ ] `skill` 命令组
- [ ] `create` 子命令
- [ ] `validate` 子命令
- [ ] `package` 子命令
- [ ] `list` 子命令
- [ ] `install` 子命令
- [ ] `show` 子命令

#### Task 2.2: 集成到主 CLI
**文件**: `anyclaw/cli/app.py`
**内容**:
- [ ] 注册 skill 子命令
- [ ] 更新帮助文档

### Phase 3: 模板和文档

#### Task 3.1: 创建 SKILL.md 模板
**文件**: `anyclaw/templates/skill_template.md`
**内容**:
- [ ] YAML frontmatter 模板
- [ ] TODO 占位符
- [ ] 结构指导说明

### Phase 4: 测试

#### Task 4.1: 单元测试
**文件**: `tests/test_skill_toolkit.py`
**内容**:
- [ ] creator 模块测试
- [ ] validator 模块测试
- [ ] packager 模块测试
- [ ] CLI 命令测试

## 执行顺序

1. Task 1.2 (validator) - 先实现验证，其他模块依赖它
2. Task 1.1 (creator) - 创建模板
3. Task 1.3 (packager) - 打包功能
4. Task 2.1 + 2.2 - CLI 集成
5. Task 3.1 - 模板文件
6. Task 4.1 - 测试

## 依赖关系

```
validator ──┬──> creator
            └──> packager

creator ───────> CLI
validator ─────> CLI
packager ──────> CLI
```

## 预计工作量

| 阶段 | 预计时间 |
|------|----------|
| Phase 1 | 2h |
| Phase 2 | 1h |
| Phase 3 | 0.5h |
| Phase 4 | 1h |
| **总计** | **4.5h** |
