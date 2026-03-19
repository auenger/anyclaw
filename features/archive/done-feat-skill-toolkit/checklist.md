# Checklist: Skill 工具链

## 开发前

- [ ] 确认参考 OpenClaw 的 skill-creator 实现
- [ ] 确认 AnyClaw 现有 skill 模块结构
- [ ] 创建 feature 分支

## Phase 1: 核心工具模块

### Creator (anyclaw/skills/toolkit/creator.py)
- [ ] 实现 `init_skill()` 函数
- [ ] 实现 `normalize_skill_name()` 函数
- [ ] 实现 `create_resource_dirs()` 函数
- [ ] SKILL.md 模板生成
- [ ] 处理 --examples 标志

### Validator (anyclaw/skills/toolkit/validator.py)
- [ ] 实现 `validate_skill()` 函数
- [ ] 实现 `_extract_frontmatter()` 函数
- [ ] 名称格式验证
- [ ] 描述长度验证
- [ ] 允许字段检查
- [ ] 返回结构化结果

### Packager (anyclaw/skills/toolkit/packager.py)
- [ ] 实现 `package_skill()` 函数
- [ ] 集成验证逻辑
- [ ] ZIP 打包实现
- [ ] 排除规则 (.git, __pycache__ 等)
- [ ] 安全检查 (symlink)
- [ ] 进度输出

## Phase 2: CLI 命令

### skill_cmd.py
- [ ] `anyclaw skill create` 命令
- [ ] `anyclaw skill validate` 命令
- [ ] `anyclaw skill package` 命令
- [ ] `anyclaw skill list` 命令
- [ ] `anyclaw skill install` 命令
- [ ] `anyclaw skill show` 命令

### app.py 集成
- [ ] 注册 skill 命令组
- [ ] 更新 --help 输出

## Phase 3: 模板

- [ ] 创建 `anyclaw/templates/skill_template.md`

## Phase 4: 测试

- [ ] creator 单元测试
- [ ] validator 单元测试
- [ ] packager 单元测试
- [ ] CLI 命令测试
- [ ] 边界条件测试

## 验收测试

- [ ] 手动测试 `anyclaw skill create my-test --resources scripts --examples`
- [ ] 手动测试 `anyclaw skill validate ./my-test`
- [ ] 手动测试 `anyclaw skill package ./my-test`
- [ ] 手动测试 `anyclaw skill list`
- [ ] 验证生成的 .skill 文件可被解压
- [ ] 验证与 OpenClaw skill 格式兼容

## 完成后

- [ ] 运行完整测试套件
- [ ] 更新 CLAUDE.md 文档
- [ ] 更新 project_context.md
- [ ] 提交代码
