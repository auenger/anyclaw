# feat-bundled-skills: 内置 Skills 移植与扩展

## 概述

从 OpenClaw 移植常用的 skills 到 AnyClaw，并提供开箱即用的工具能力。包括基础工具、开发工具、以及新增的文件操作、代码执行、网络搜索和数据处理能力。

## 依赖

- `feat-tool-calling` (pending) - Tool Calling 核心框架

## 用户价值点

### VP1: 基础工具 Skills

**价值**: 提供日常使用的基础工具 skills，覆盖天气、时间、文本处理等常见需求。

**Skills 列表**:
- `weather` - 天气查询 (wttr.in)
- `summarize` - URL/文件摘要
- `time` - 时间查询 (已有，需转换格式)
- `echo` - 回显测试

**Gherkin 场景**:

```gherkin
Feature: 基础工具 Skills

  Scenario: 使用 weather skill
    Given 已安装 weather skill
    And 系统有 curl 命令
    When 用户问 "北京今天天气怎么样"
    Then Agent 应调用 weather skill
    And 返回北京的天气信息

  Scenario: 使用 summarize skill
    Given 已安装 summarize skill
    And 系统有 summarize CLI
    When 用户说 "帮我总结这篇文章 https://example.com"
    Then Agent 应调用 summarize skill
    And 返回文章摘要

  Scenario: 使用 time skill
    Given 已安装 time skill
    When 用户问 "现在几点"
    Then Agent 应调用 time skill
    And 返回当前时间
```

### VP2: 开发工具 Skills

**价值**: 提供开发相关的 skills，支持 GitHub 操作、代码搜索等功能。

**Skills 列表**:
- `github` - GitHub CLI 操作
- `gh-issues` - GitHub Issues 管理
- `coding-agent` - 代码相关任务

**Gherkin 场景**:

```gherkin
Feature: 开发工具 Skills

  Scenario: 使用 github skill 查看 PR
    Given 已安装 github skill
    And 系统有 gh CLI 且已认证
    When 用户说 "查看 PR #123 的状态"
    Then Agent 应调用 github skill
    And 返回 PR 状态信息

  Scenario: 使用 gh-issues skill
    Given 已安装 gh-issues skill
    And 系统有 gh CLI
    When 用户说 "列出所有未解决的 bug issues"
    Then Agent 应调用 gh-issues skill
    And 返回 issue 列表

  Scenario: GitHub CLI 未安装
    Given 系统没有 gh 命令
    When 用户尝试使用 github skill
    Then skill 应被标记为不可用
    And Agent 应提示用户安装 gh CLI
```

### VP3: 文件操作 Skills (新增)

**价值**: 提供安全的文件和目录操作能力，支持读写、搜索、管理等功能。

**Skills 列表**:
- `file_ops` - 文件读写、目录操作

**Gherkin 场景**:

```gherkin
Feature: 文件操作 Skills

  Scenario: 读取文件
    Given 已安装 file_ops skill
    And 工作目录中有 test.txt 文件
    When 用户说 "读取 test.txt 的内容"
    Then Agent 应调用 file_ops skill
    And 返回文件内容

  Scenario: 写入文件
    Given 已安装 file_ops skill
    When 用户说 "创建 hello.txt 并写入 Hello World"
    Then Agent 应调用 file_ops skill
    And 创建文件并确认写入成功

  Scenario: 列出目录
    Given 已安装 file_ops skill
    When 用户说 "列出当前目录下的所有 Python 文件"
    Then Agent 应调用 file_ops skill
    And 返回匹配的文件列表

  Scenario: 搜索文件内容
    Given 已安装 file_ops skill
    When 用户说 "在 src 目录搜索包含 TODO 的文件"
    Then Agent 应调用 file_ops skill
    And 返回匹配的文件和行号

  Scenario: 安全限制
    Given 已安装 file_ops skill
    When 用户尝试访问工作目录外的文件
    Then 应拒绝操作
    And 返回安全错误信息
```

### VP4: 代码执行 Skills (新增)

**价值**: 提供安全的代码执行能力，支持 Python 脚本运行，有安全限制。

**Skills 列表**:
- `code_exec` - Python 代码执行

**Gherkin 场景**:

```gherkin
Feature: 代码执行 Skills

  Scenario: 执行简单 Python 代码
    Given 已安装 code_exec skill
    When 用户说 "计算 1 到 100 的和"
    Then Agent 应调用 code_exec skill
    And 返回结果 5050

  Scenario: 执行数据处理脚本
    Given 已安装 code_exec skill
    When 用户说 "用 Python 分析 data.json 文件"
    Then Agent 应调用 code_exec skill
    And 返回处理结果

  Scenario: 黑名单命令阻止
    Given 已安装 code_exec skill
    When 用户尝试执行 "rm -rf /" 或 "sudo" 命令
    Then 应拒绝执行
    And 返回安全错误

  Scenario: 执行超时
    Given 已安装 code_exec skill
    And 设置了 30 秒超时
    When 代码执行超过 30 秒
    Then 应终止执行
    And 返回超时错误

  Scenario: 资源限制
    Given 已安装 code_exec skill
    When 代码尝试占用过多内存
    Then 应限制资源使用
    And 返回资源限制错误
```

### VP5: 网络搜索 Skills (新增)

**价值**: 提供网络搜索能力，支持 DuckDuckGo、Bing 等搜索引擎。

**Skills 列表**:
- `web_search` - 琜索引擎集成

**Gherkin 场景**:

```gherkin
Feature: 网络搜索 Skills

  Scenario: 搜索一般信息
    Given 已安装 web_search skill
    When 用户说 "搜索 Python asyncio 教程"
    Then Agent 应调用 web_search skill
    And 返回搜索结果摘要

  Scenario: 搜索技术文档
    Given 已安装 web_search skill
    When 用户说 "查找 FastAPI 官方文档"
    Then Agent 应调用 web_search skill
    And 返回相关文档链接

  Scenario: 搜索失败处理
    Given 已安装 web_search skill
    And 网络不可用
    When 用户尝试搜索
    Then 应返回错误信息
    And Agent 应建议稍后重试

  Scenario: 无 API Key 搜索
    Given 已安装 web_search skill
    And 未配置搜索 API
    When 用户尝试搜索
    Then 应使用免费搜索引擎（DuckDuckGo）
    And 返回基本搜索结果
```

### VP6: Skills 管理命令

**价值**: 提供 CLI 命令管理 skills，支持查看、安装、更新等操作。

**Gherkin 场景**:

```gherkin
Feature: Skills 管理命令

  Scenario: 列出所有 skills
    Given 存在多个 skills
    When 运行 "anyclaw skills list"
    Then 应显示所有可用 skills
    And 显示每个 skill 的状态（可用/不可用）
    And 显示依赖要求

  Scenario: 查看 skill 详情
    Given 存在 weather skill
    When 运行 "anyclaw skills show weather"
    Then 应显示 skill 详细信息
    And 显示使用说明
    And 显示命令示例

  Scenario: 检查 skills 状态
    Given 部分 skills 依赖未满足
    When 运行 "anyclaw skills doctor"
    Then 应检查所有 skills 依赖
    And 报告不可用的 skills
    And 提供修复建议
```

## Skills 目录结构

```
anyclaw/
└── skills/
    └── builtin/
        # 基础工具
        ├── weather/
        │   └── SKILL.md
        ├── summarize/
        │   └── SKILL.md
        ├── time/
        │   └── SKILL.md
        ├── echo/
        │   └── SKILL.md
        # 开发工具
        ├── github/
        │   └── SKILL.md
        ├── gh-issues/
        │   └── SKILL.md
        # 扩展工具 (新增)
        ├── file_ops/
        │   └── SKILL.md
        ├── code_exec/
        │   └── SKILL.md
        ├── web_search/
        │   └── SKILL.md
        └── data_process/
            └── SKILL.md
```

## 技术设计

### Skill 转换规则

1. **OpenClaw SKILL.md → 直接复制**
2. **现有 Python skill → SKILL.md**
3. **新增 Skill → SKILL.md**

### 安全设计

**code_exec 安全限制**:
- 黑名单命令: `rm -rf`, `sudo`, `mkfs`, `dd`, `chmod 777`
- 工作目录限制: 只能在 `workspace_dir` 内执行
- 执行超时: 默认 30 秒
- 资源限制: 内存和 CPU 限制

**file_ops 安全限制**:
- 工作目录限制: 只能访问 `workspace_dir` 内的文件
- 敏感文件保护: 不允许访问 `.env`, `.git` 等敏感文件

### CLI 命令设计

```bash
anyclaw skills list [--all] [--available]
anyclaw skills show <name>
anyclaw skills doctor
anyclaw skills install <name>
anyclaw skills update [<name>]
```

## 验收标准

- [ ] 至少移植 5 个 OpenClaw skills
- [ ] 至少新增 4 个扩展 skills (file_ops, code_exec, web_search, data_process)
- [ ] 所有 skills 格式符合 SKILL.md 规范
- [ ] CLI skills 命令正常工作
- [ ] code_exec 有安全限制
- [ ] 文档完整

## 优先级排序

| 优先级 | Skill | 类型 | 理由 |
|--------|-------|------|------|
| P0 | weather | 移植 | 无依赖，最常用 |
| P0 | time | 移植 | 已有实现，转换格式 |
| P0 | file_ops | 新增 | 核心能力 |
| P1 | github | 移植 | 开发常用 |
| P1 | gh-issues | 移植 | 开发常用 |
| P1 | code_exec | 新增 | 核心能力 |
| P2 | summarize | 移植 | 需要 summarize CLI |
| P2 | web_search | 新增 | 扩展能力 |
| P2 | data_process | 新增 | 扩展能力 |

## 参考

- OpenClaw Skills 源: `reference/openclaw/skills/`
- Skill 格式规范: `feat-tool-calling/spec.md`
