# XLSX Skill 任务分解

## Phase 1: 基础结构

- [ ] 创建 skill 目录结构
  - `anyclaw/skills/builtin/xlsx/`
  - `SKILL.md`, `skill.py`

- [ ] 实现 XlsxSkill 基类
  - 继承 Skill 基类
  - 定义动作路由

## Phase 2: 创建功能

- [ ] 实现 `create` 动作
  - 使用 openpyxl
  - 支持公式（非硬编码）
  - 支持样式设置

- [ ] 实现财务模型配色
  - 蓝色输入、黑色公式、绿色链接
  - 黄色背景标记假设

- [ ] 实现格式规范
  - 年份/货币/百分比格式
  - 零值显示为 "-"

## Phase 3: 编辑功能

- [ ] 实现 `edit` 动作
  - 使用 load_workbook 保留格式
  - 修改单元格数据
  - 添加公式列

- [ ] 实现格式保留
  - 现有样式不丢失
  - 公式引用正确

## Phase 4: 分析功能

- [ ] 实现 `analyze` 动作
  - 使用 pandas 读取
  - 统计分析
  - 数据洞察

- [ ] 实现 `extract` 动作
  - 导出为 CSV/JSON
  - 多 sheet 支持

## Phase 5: 公式功能

- [ ] 实现 `recalc` 动作
  - LibreOffice 宏调用
  - 自动配置

- [ ] 实现错误检测
  - 扫描 #REF!, #DIV/0!, #VALUE! 等
  - 返回错误位置和计数

## Phase 6: 测试和文档

- [ ] 单元测试
- [ ] 集成测试
- [ ] 完善 SKILL.md
