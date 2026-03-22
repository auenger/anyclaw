# XLSX Skill - Excel 电子表格处理

## 概述

将 Claude Code 的 documents skill 中的 XLSX 功能移植到 AnyClaw 作为内置 skill，使 Agent 能够创建、编辑和分析 Excel 电子表格，支持公式、财务建模和数据分析。

## 用户价值点

### 1. 创建电子表格

**Gherkin 场景:**
```gherkin
Feature: 创建电子表格

  Scenario: 创建带公式的表格
    Given 用户描述数据结构和计算需求
    When Agent 调用 xlsx skill 的 create 功能
    Then 生成包含公式（非硬编码值）的 .xlsx 文件
    And 公式可自动重算

  Scenario: 创建财务模型
    Given 用户需要财务预测模型
    When Agent 创建电子表格时
    Then 使用蓝色输入、黑色公式、绿色链接的配色
    And 所有假设在独立单元格
```

### 2. 编辑现有表格

**Gherkin 场景:**
```gherkin
Feature: 编辑电子表格

  Scenario: 修改表格数据
    Given 存在 .xlsx 文件
    When Agent 调用 edit 功能
    Then 指定单元格被修改
    And 现有公式和格式被保留

  Scenario: 添加计算列
    Given 需要添加新计算的表格
    When Agent 添加公式列
    Then 公式正确引用现有数据
```

### 3. 数据分析

**Gherkin 场景:**
```gherkin
Feature: 分析电子表格数据

  Scenario: 读取和分析数据
    Given 包含数据的 .xlsx 文件
    When Agent 调用 analyze 功能
    Then 返回数据统计和洞察
    And 支持筛选、分组、聚合

  Scenario: 数据可视化
    Given 表格数据
    When Agent 生成分析报告
    Then 包含关键指标和趋势
```

### 4. 公式重算

**Gherkin 场景:**
```gherkin
Feature: 公式计算

  Scenario: 重算公式值
    Given 包含公式的 .xlsx 文件
    When Agent 调用 recalc 功能
    Then 所有公式被重新计算
    And 返回错误检查结果

  Scenario: 错误检测
    Given 可能存在错误的表格
    When Agent 执行公式验证
    Then 报告所有 #REF!, #DIV/0! 等错误
    And 提供错误位置
```

## 技术方案

### 核心依赖

| 库 | 用途 | 安装方式 |
|---|---|---|
| openpyxl | 创建/编辑（公式支持） | `pip install openpyxl` |
| pandas | 数据分析 | `pip install pandas` |
| LibreOffice | 公式重算 | 系统安装 |

### Skill 结构

```
anyclaw/skills/builtin/xlsx/
├── SKILL.md          # 技能文档
├── skill.py          # 核心实现
├── recalc.py         # 公式重算脚本
└── templates/        # 财务模型模板
```

### 关键规则

1. **公式优先** - 永远使用公式，不硬编码计算值
2. **零错误交付** - 所有 #REF!, #DIV/0! 必须修复
3. **配色规范**：
   - 蓝色 (RGB: 0,0,255) - 输入值
   - 黑色 (RGB: 0,0,0) - 公式
   - 绿色 (RGB: 0,128,0) - 跨表链接
   - 红色 (RGB: 255,0,0) - 外部链接
   - 黄色背景 - 关键假设

### 格式规范

- 年份：文本格式（"2024" 不是 "2,024"）
- 货币：$#,##0 格式，标题注明单位
- 零值：显示为 "-"
- 百分比：0.0% 格式
- 负数：括号表示 (123)

## 依赖

- 无前置特性依赖

## 优先级

65

## 大小

M
