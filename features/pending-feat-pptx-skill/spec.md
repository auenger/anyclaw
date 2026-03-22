# PPTX Skill - PowerPoint 演示文稿处理

## 概述

将 Claude Code 的 documents skill 中的 PPTX 功能移植到 AnyClaw 作为内置 skill，使 Agent 能够创建、编辑和分析 PowerPoint 演示文稿。

## 用户价值点

### 1. 创建演示文稿（无模板）

**Gherkin 场景:**
```gherkin
Feature: 创建演示文稿

  Scenario: 从零创建幻灯片
    Given 用户描述演示内容
    When Agent 调用 pptx skill 的 create 功能
    Then 生成包含多张幻灯片的 .pptx 文件
    And 幻灯片有专业设计和布局

  Scenario: 应用设计主题
    Given 用户指定主题风格
    When Agent 选择匹配的配色方案
    Then 演示文稿使用一致的视觉风格
    And 包含标题、内容、结尾幻灯片
```

### 2. 基于模板创建

**Gherkin 场景:**
```gherkin
Feature: 模板化创建

  Scenario: 使用现有模板
    Given 用户提供 .pptx 模板文件
    When Agent 分析模板布局
    Then 根据内容选择合适的幻灯片布局
    And 保持模板的视觉风格

  Scenario: 替换模板内容
    Given 模板包含占位符
    When Agent 提供新内容
    Then 占位符被替换
    And 原有格式被保留
```

### 3. 编辑现有演示文稿

**Gherkin 场景:**
```gherkin
Feature: 编辑演示文稿

  Scenario: 修改幻灯片内容
    Given 存在 .pptx 文件
    When Agent 调用 edit 功能
    Then 指定幻灯片内容被修改
    And 其他幻灯片保持不变

  Scenario: 添加演讲者备注
    Given 需要添加备注的演示文稿
    When Agent 调用 add-notes 功能
    Then 每张幻灯片添加演讲者备注
```

### 4. 分析和提取

**Gherkin 场景:**
```gherkin
Feature: 分析演示文稿

  Scenario: 提取文本内容
    Given 一个 .pptx 文件
    When Agent 调用 extract 功能
    Then 返回所有幻灯片的文本内容
    And 格式为 markdown

  Scenario: 生成缩略图
    Given 需要视觉检查的演示文稿
    When Agent 调用 thumbnail 功能
    Then 生成幻灯片缩略图网格
    And 可用于快速浏览
```

## 技术方案

### 核心依赖

| 库 | 用途 | 安装方式 |
|---|---|---|
| python-pptx | 创建/编辑 PPTX | `pip install python-pptx` |
| markitdown | 文本提取 | `pip install "markitdown[pptx]"` |
| pdf2image | 缩略图生成 | `pip install pdf2image` |

### Skill 结构

```
anyclaw/skills/builtin/pptx/
├── SKILL.md              # 技能文档
├── skill.py              # 核心实现
├── templates/            # 设计模板
│   ├── classic/
│   ├── modern/
│   └── corporate/
└── scripts/
    ├── thumbnail.py      # 缩略图生成
    ├── inventory.py      # 模板分析
    └── replace.py        # 内容替换
```

### 实现要点

1. **创建** - html2pptx 或 python-pptx
2. **模板分析** - inventory.py + thumbnail
3. **内容替换** - replace.py
4. **文本提取** - markitdown
5. **视觉验证** - thumbnail 网格

### 配色方案

内置多种专业配色：
- Classic Blue (深蓝)
- Teal & Coral (青绿)
- Bold Red (红色)
- Warm Blush (暖粉)
- Black & Gold (黑金)

## 依赖

- 无前置特性依赖

## 优先级

65

## 大小

M
