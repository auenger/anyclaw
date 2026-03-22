# PDF Skill 任务分解

## Phase 1: 基础结构

- [ ] 创建 skill 目录结构
  - `anyclaw/skills/builtin/pdf/`
  - `SKILL.md`, `skill.py`

- [ ] 实现 PdfSkill 基类
  - 继承 Skill 基类
  - 定义动作路由

## Phase 2: 基础操作

- [ ] 实现 `create` 动作
  - 使用 reportlab
  - 支持多页文档

- [ ] 实现 `merge` 动作
  - 使用 pypdf 合并多个 PDF

- [ ] 实现 `split` 动作
  - 按页码范围拆分

- [ ] 实现 `rotate` 动作
  - 页面旋转

## Phase 3: 提取功能

- [ ] 实现 `extract-text` 动作
  - 使用 pdfplumber
  - 保留布局

- [ ] 实现 `extract-tables` 动作
  - 表格识别和提取
  - 导出为 CSV/Excel

- [ ] 实现 `extract-metadata` 动作
  - 获取 PDF 元数据

## Phase 4: 高级功能

- [ ] 实现 `fill-form` 动作
  - 读取表单字段
  - 填充字段值
  - 扁平化表单

- [ ] 实现 `ocr` 动作
  - 扫描 PDF 文字识别
  - 多语言支持

- [ ] 实现 `watermark` 动作
  - 添加水印

- [ ] 实现 `encrypt` 动作
  - 密码保护

## Phase 5: 测试和文档

- [ ] 单元测试
- [ ] 集成测试
- [ ] 完善 SKILL.md
