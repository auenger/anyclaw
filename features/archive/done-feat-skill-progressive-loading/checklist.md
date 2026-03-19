# Checklist: Skill 渐进式加载

## 开发前

- [x] 确认 feat-skill-toolkit 已完成
- [x] 阅读 OpenClaw nanobot/agent/skills.py 实现
- [x] 确认现有 loader.py 结构
- [x] 创建 feature 分支

## Phase 1: SkillsLoader 增强

### loader.py 增强
- [x] 实现 `build_skills_summary()` - XML 格式输出
- [x] 实现 `load_skills_for_context()` - 批量加载
- [x] 实现 `_strip_frontmatter()` - 去除 YAML frontmatter
- [x] 实现 `_get_skill_description()` - 从 frontmatter 获取描述

### 依赖检查
- [x] 实现 `_check_requirements()` - bins/env 检查
- [x] 实现 `_get_missing_requirements()` - 缺失项描述
- [x] 实现 `_parse_nanobot_metadata()` - JSON metadata 解析
- [x] 集成到 list_skills() 过滤

### Always Skills
- [x] 实现 `get_always_skills()` - 获取 always=true 列表
- [x] 解析 metadata.openclaw.always
- [x] 依赖检查 + always 过滤

## Phase 2: Scripts 执行

### executor.py (新文件)
- [x] 创建 SkillScriptExecutor 类
- [x] 实现 `execute_script(skill_name, script_path, args)`
- [x] Python 脚本执行 (python3)
- [x] Shell 脚本执行 (bash)
- [x] 设置正确的工作目录
- [x] 超时处理 (默认 60s)
- [x] 错误捕获和返回

## Phase 3: Context 集成

### context.py 修改
- [x] 在 `build()` 中包含 skills summary
- [x] 自动加载 always skills 内容
- [x] 添加 `load_skill_content(name)` 辅助方法

## Phase 4: 数据模型

### models.py 更新
- [x] OpenClawMetadata 添加 `always: bool`
- [x] OpenClawMetadata 添加 `scripts: List[str]`
- [x] OpenClawMetadata 添加 `references: List[str]`

## Phase 5: 测试

- [x] build_skills_summary 输出格式测试
- [x] load_skills_for_context 内容测试
- [x] 依赖检查单元测试
- [x] always skills 过滤测试
- [x] scripts 执行测试
- [x] 边界条件测试

## 验收测试

- [x] 启动 agent，验证 skills summary 在上下文中
- [x] 创建 always=true 的 skill，验证自动加载
- [x] 创建有依赖的 skill，验证 available 标记
- [x] 执行 skill 内的脚本，验证输出
- [x] 读取 references 文件，验证内容

## 完成后

- [x] 运行完整测试套件
- [ ] 更新 CLAUDE.md 文档
- [ ] 更新 project_context.md
- [x] 提交代码
