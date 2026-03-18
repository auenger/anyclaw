# 内置技能扩展 V2

## 概述

扩展现有内置技能系统，增加更多实用技能，对齐 OpenClaw 的核心能力。

## 背景

当前 AnyClaw 已有 6 个基础内置技能（echo、time、calc、file、http、weather），需要扩展以支持更丰富的功能，特别是代码执行、进程管理等核心能力。

## 用户价值点

### 价值点 1：代码执行能力（code_exec）

执行 Python/JavaScript/Bash 代码片段，支持安全的沙箱环境。

**验收场景**：
```gherkin
Feature: 代码执行技能

Scenario: 执行 Python 代码
  Given 用户请求执行 Python 代码
  When 调用 code_exec 技能，语言为 python，代码为 "print(1+1)"
  Then 返回执行结果 "2"
  And 状态为成功

Scenario: 执行 JavaScript 代码
  Given 用户请求执行 JavaScript 代码
  When 调用 code_exec 技能，语言为 javascript，代码为 "console.log(2*3)"
  Then 返回执行结果 "6"

Scenario: 执行超时处理
  Given 用户执行长时间运行的代码
  When 代码执行超过 30 秒
  Then 返回超时错误
  And 进程被终止

Scenario: 执行错误代码
  Given 用户执行有语法错误的代码
  When 调用 code_exec 技能
  Then 返回错误信息
  And 不影响系统稳定性
```

### 价值点 2：进程管理能力（process）

管理后台进程，支持启动、监控、终止操作。

**验收场景**：
```gherkin
Feature: 进程管理技能

Scenario: 启动后台进程
  Given 用户需要后台运行命令
  When 调用 process 技能，action 为 start，command 为 "sleep 60"
  Then 返回 session_id
  And 进程在后台运行

Scenario: 查询进程状态
  Given 存在运行中的后台进程
  When 调用 process 技能，action 为 status，session_id 为有效 ID
  Then 返回进程状态（running/completed/failed）

Scenario: 获取进程输出
  Given 存在运行中的后台进程
  When 调用 process 技能，action 为 log，session_id 为有效 ID
  Then 返回进程的标准输出和错误输出

Scenario: 终止进程
  Given 存在运行中的后台进程
  When 调用 process 技能，action 为 kill，session_id 为有效 ID
  Then 进程被终止
  And 返回确认信息

Scenario: 列出所有进程
  Given 存在多个后台进程
  When 调用 process 技能，action 为 list
  Then 返回所有进程的列表及状态
```

### 价值点 3：文本处理能力（text）

提供文本处理功能：摘要、提取、格式化。

**验收场景**：
```gherkin
Feature: 文本处理技能

Scenario: 统计文本信息
  Given 用户提供一段文本
  When 调用 text 技能，action 为 stats
  Then 返回字符数、单词数、行数

Scenario: 提取关键信息
  Given 用户提供一段文本
  When 调用 text 技能，action 为 extract，pattern 为邮箱
  Then 返回所有匹配的邮箱地址

Scenario: 文本格式转换
  Given 用户提供 Markdown 文本
  When 调用 text 技能，action 为 format，target 为 json
  Then 返回转换后的 JSON 格式

Scenario: 文本搜索替换
  Given 用户提供文本和搜索模式
  When 调用 text 技能，action 为 replace
  Then 返回替换后的文本
```

### 价值点 4：系统信息能力（system）

获取系统信息和执行系统操作。

**验收场景**：
```gherkin
Feature: 系统信息技能

Scenario: 获取系统信息
  Given 用户请求系统信息
  When 调用 system 技能，action 为 info
  Then 返回操作系统、CPU、内存等信息

Scenario: 获取环境变量
  Given 用户请求环境变量
  When 调用 system 技能，action 为 env
  Then 返回环境变量列表

Scenario: 检查命令可用性
  Given 用户需要检查命令是否存在
  When 调用 system 技能，action 为 which，command 为 "python3"
  Then 返回命令路径或不存在提示
```

### 价值点 5：JSON/YAML 处理能力（data）

处理 JSON 和 YAML 数据。

**验收场景**：
```gherkin
Feature: 数据处理技能

Scenario: 解析 JSON
  Given 用户提供 JSON 字符串
  When 调用 data 技能，action 为 parse，format 为 json
  Then 返回解析后的结构化数据

Scenario: JSON 路径查询
  Given 用户提供 JSON 数据和 JSONPath 查询
  When 调用 data 技能，action 为 query
  Then 返回查询结果

Scenario: 格式转换
  Given 用户提供 JSON 数据
  When 调用 data 技能，action 为 convert，target 为 yaml
  Then 返回 YAML 格式数据

Scenario: 数据验证
  Given 用户提供数据和 JSON Schema
  When 调用 data 技能，action 为 validate
  Then 返回验证结果
```

## 技术设计

### 技能结构

```
anyclaw/skills/builtin/
├── code_exec/           # 代码执行
│   └── skill.py
├── process/             # 进程管理
│   └── skill.py
├── text/                # 文本处理
│   └── skill.py
├── system/              # 系统信息
│   └── skill.py
├── data/                # 数据处理
│   └── skill.py
└── (现有技能保持不变)
```

### 代码执行安全

- 使用 subprocess 执行代码
- 设置超时限制（默认 30 秒）
- 限制内存使用
- 不允许文件系统写入（可选配置）
- 沙箱模式（未来扩展）

## 优先级

78 - 与记忆系统同等优先级，是核心功能扩展

## 依赖

- 无前置依赖
- 可选依赖：feat-bundled-skills（已完成）

## 大小评估

**M** - 5 个价值点，每个价值点实现相对独立，代码量适中
