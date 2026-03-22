# PDF Skill - PDF 文档处理

## 概述

将 Claude Code 的 documents skill 中的 PDF 功能移植到 AnyClaw 作为内置 skill，使 Agent 能够创建、合并、拆分、提取文本和表格、填充表单等。

## 用户价值点

### 1. PDF 创建

**Gherkin 场景:**
```gherkin
Feature: 创建 PDF 文档

  Scenario: 从数据生成 PDF
    Given 用户提供数据和模板要求
    When Agent 调用 pdf skill 的 create 功能
    Then 生成格式正确的 .pdf 文件
    And 包含指定的文本和图形内容

  Scenario: 多页文档创建
    Given 需要创建多页报告
    When Agent 使用 reportlab 创建
    Then 生成包含目录、章节、页码的 PDF
```

### 2. PDF 合并/拆分

**Gherkin 场景:**
```gherkin
Feature: PDF 合并和拆分

  Scenario: 合并多个 PDF
    Given 多个 .pdf 文件
    When Agent 调用 merge 功能
    Then 生成包含所有页面的单个 PDF

  Scenario: 拆分 PDF
    Given 一个多页 PDF 文件
    When Agent 调用 split 功能指定页码
    Then 生成指定页面范围的独立 PDF 文件
```

### 3. 文本和表格提取

**Gherkin 场景:**
```gherkin
Feature: 提取 PDF 内容

  Scenario: 提取文本
    Given 一个包含文本的 PDF
    When Agent 调用 extract-text 功能
    Then 返回保留布局的纯文本内容

  Scenario: 提取表格
    Given 一个包含表格的 PDF
    When Agent 调用 extract-tables 功能
    Then 返回结构化的表格数据
    And 可导出为 CSV 或 Excel 格式
```

### 4. PDF 表单填充

**Gherkin 场景:**
```gherkin
Feature: 填充 PDF 表单

  Scenario: 填充可填写表单
    Given 一个带表单字段的 PDF
    When Agent 提供字段名和值
    Then 生成填充完成的 PDF
    And 表单可被扁平化防止修改
```

## 技术方案

### 核心依赖

| 库 | 用途 | 安装方式 |
|---|---|---|
| pypdf | 合并/拆分/旋转 | `pip install pypdf` |
| pdfplumber | 文本/表格提取 | `pip install pdfplumber` |
| reportlab | 创建 PDF | `pip install reportlab` |
| pytesseract | OCR | `pip install pytesseract` |
| pdf2image | PDF 转图片 | `pip install pdf2image` |

### Skill 结构

```
anyclaw/skills/builtin/pdf/
├── SKILL.md          # 技能文档
├── skill.py          # 核心实现
├── forms.py          # 表单填充
├── ocr.py            # OCR 支持
└── scripts/
    ├── merge.py
    ├── split.py
    └── extract.py
```

### 实现要点

1. **创建** - reportlab (Canvas/Platypus)
2. **合并/拆分** - pypdf / qpdf CLI
3. **提取** - pdfplumber + pandas
4. **表单** - pypdf 或 pdf-lib
5. **OCR** - pytesseract + pdf2image
6. **操作** - 水印、加密、旋转

## 依赖

- 无前置特性依赖

## 优先级

70

## 大小

M
