# feat-bundled-skills: 完成检查清单

## VP1: 基础工具 Skills

### weather skill
- [ ] SKILL.md 已复制/创建
- [ ] frontmatter 格式正确
- [ ] 依赖声明完整 (curl)
- [ ] 命令示例可执行
- [ ] 测试通过

### time skill
- [ ] 已转换为 SKILL.md 格式
- [ ] 功能与原 Python skill 一致
- [ ] 测试通过

### echo skill
- [ ] 已转换为 SKILL.md 格式
- [ ] 功能与原 Python skill 一致
- [ ] 测试通过

### summarize skill (可选)
- [ ] SKILL.md 已复制
- [ ] 依赖声明正确
- [ ] 文档说明完整

---

## VP2: 开发工具 Skills

### github skill
- [ ] SKILL.md 已复制
- [ ] frontmatter 格式正确
- [ ] 依赖声明完整 (gh CLI)
- [ ] 命令示例可执行
- [ ] 测试通过

### gh-issues skill
- [ ] SKILL.md 已复制
- [ ] 依赖声明完整
- [ ] 测试通过

### 其他 skills
- [ ] 评估完成
- [ ] 选择的 skills 已移植

---

## VP3: CLI 管理命令

### skills list
- [ ] 命令已实现
- [ ] 显示名称、描述、状态
- [ ] `--all` 过滤正常
- [ ] `--available` 过滤正常
- [ ] 单元测试通过

### skills show
- [ ] 命令已实现
- [ ] 显示详细信息
- [ ] 显示依赖要求
- [ ] 显示使用示例
- [ ] 单元测试通过

### skills doctor
- [ ] 命令已实现
- [ ] 检查 bins 依赖
- [ ] 检查 env 依赖
- [ ] 提供修复建议
- [ ] 单元测试通过

### CLI 集成
- [ ] 命令组已注册
- [ ] `anyclaw --help` 显示 skills
- [ ] 所有子命令可访问

---

## 质量标准

### Skills 质量
- [ ] 所有 SKILL.md 格式正确
- [ ] 所有 frontmatter 有效
- [ ] 所有命令示例可执行
- [ ] 依赖声明准确

### 代码质量
- [ ] 通过 Black 格式化
- [ ] 通过 Ruff 检查
- [ ] 有适当的错误处理

### 测试
- [ ] 每个 skill 有测试
- [ ] CLI 命令有测试
- [ ] 依赖检查有测试

### 文档
- [ ] CLAUDE.md 已更新
- [ ] skills README 存在
- [ ] 使用示例完整

---

## 验收测试

### 手动测试场景

- [ ] **场景 1**: 查看所有 skills
  ```bash
  anyclaw skills list
  ```
  预期: 显示所有内置 skills 及状态

- [ ] **场景 2**: 查看天气
  ```
  用户: 北京今天天气怎么样？
  ```
  预期: 返回天气信息

- [ ] **场景 3**: GitHub 操作 (如有 gh CLI)
  ```
  用户: 列出我的 PR
  ```
  预期: 返回 PR 列表

- [ ] **场景 4**: skills doctor
  ```bash
  anyclaw skills doctor
  ```
  预期: 检查所有依赖，报告问题

- [ ] **场景 5**: skill 详情
  ```bash
  anyclaw skills show weather
  ```
  预期: 显示 weather skill 详细信息

---

## 完成条件

- [ ] 至少 5 个 skills 可用
- [ ] 所有 VP1 检查项完成
- [ ] 所有 VP2 检查项完成
- [ ] 所有 VP3 检查项完成
- [ ] 所有质量标准满足
- [ ] 所有验收测试通过
- [ ] 代码已提交
- [ ] PR 已创建并审核通过
