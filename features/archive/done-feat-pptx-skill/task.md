# PPTX Skill 任务分解

## Phase 1: 基础结构

- [ ] 创建 skill 目录结构
  - `anyclaw/skills/builtin/pptx/`
  - `SKILL.md`, `skill.py`

- [ ] 实现 PptxSkill 基类
  - 继承 Skill 基类
  - 定义动作路由

## Phase 2: 创建功能

- [ ] 实现 `create` 动作
  - 使用 python-pptx
  - 支持多种布局类型
  - 标题、内容、图表幻灯片

- [ ] 实现配色方案
  - 内置多种专业配色
  - 自动选择匹配主题

- [ ] 实现设计原则
  - Web-safe 字体
  - 视觉层次
  - 可读性检查

## Phase 3: 模板功能

- [ ] 实现 `analyze-template` 动作
  - 提取模板库存
  - 生成缩略图网格

- [ ] 实现 `use-template` 动作
  - 选择合适布局
  - 重组幻灯片顺序

- [ ] 实现 `replace-content` 动作
  - 提取文本库存
  - 替换占位符内容
  - 保留格式

## Phase 4: 编辑和分析

- [ ] 实现 `edit` 动作
  - OOXML unpack/edit/pack
  - 修改特定幻灯片

- [ ] 实现 `add-notes` 动作
  - 添加演讲者备注

- [ ] 实现 `extract` 动作
  - 使用 markitdown 提取文本

- [ ] 实现 `thumbnail` 动作
  - 生成缩略图网格
  - 视觉验证

## Phase 5: 测试和文档

- [ ] 单元测试
- [ ] 集成测试
- [ ] 完善 SKILL.md
