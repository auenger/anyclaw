# AnyClaw 终端测试场景

本文档定义了 AnyClaw 项目的 CLI 终端测试场景，覆盖所有主要功能模块。

## 目录

1. [环境准备](#1-环境准备)
2. [基础命令测试](#2-基础命令测试)
3. [配置管理测试](#3-配置管理测试)
4. [工作区管理测试](#4-工作区管理测试)
5. [技能系统测试](#5-技能系统测试)
6. [MCP 服务测试](#6-mcp-服务测试)
7. [Agent 聊天测试](#7-agent-聊天测试)
8. [技能对话模式测试](#8-技能对话模式测试)
9. [Provider 管理测试](#9-provider-管理测试)
10. [错误处理测试](#10-错误处理测试)
11. [集成测试场景](#11-集成测试场景)

---

## 1. 环境准备

### 1.1 安装依赖

```bash
cd /Users/ryan/mycode/AnyClaw/anyclaw

# 使用 Poetry 安装
poetry install

# 验证安装
poetry run anyclaw version
# 预期输出: AnyClaw v0.1.0-MVP
```

### 1.2 环境变量设置

```bash
# 复制示例配置
cp .env.example .env

# 编辑配置文件
# 设置必要的 API Key
```

---

## 2. 基础命令测试

### 2.1 查看版本

```bash
poetry run anyclaw version
# 预期输出: AnyClaw v0.1.0-MVP
```

### 2.2 查看帮助

```bash
# 主命令帮助
poetry run anyclaw --help

# 子命令帮助
poetry run anyclaw chat --help
poetry run anyclaw skill --help
poetry run anyclaw mcp --help
poetry run anyclaw config --help
poetry run anyclaw workspace --help
```

### 2.3 查看 Providers

```bash
poetry run anyclaw providers
# 预期输出: 表格显示 openai/anthropic/zai 的配置状态
```

---

## 3. 配置管理测试

### 3.1 初始化配置

```bash
# 初始化配置文件
poetry run anyclaw config init
# 预期: 在 ~/.anyclaw/ 创建 config.json

# 查看配置路径
poetry run anyclaw config path
# 预期输出: /Users/ryan/.anyclaw/config.json
```

### 3.2 查看配置

```bash
# 显示当前配置
poetry run anyclaw config show
# 预期输出:
# - Agent 配置表格 (名称、工作区)
# - LLM 配置表格 (provider、model、max_tokens、temperature)
# - Providers API Keys 表格
```

### 3.3 设置配置

```bash
# 设置 LLM 模型
poetry run anyclaw config set llm.model gpt-4o
poetry run anyclaw config set llm.model glm-4.7

# 设置 API Key
poetry run anyclaw config set openai.api_key sk-test-key
poetry run anyclaw config set zai.api_key your-zai-key

# 使用简化模式设置 provider key
poetry run anyclaw config set -p openai sk-xxx
poetry run anyclaw config set -p zai your-key

# 设置 temperature
poetry run anyclaw config set llm.temperature 0.7

# 验证设置
poetry run anyclaw config show
```

### 3.4 编辑配置

```bash
# 使用编辑器打开配置文件
poetry run anyclaw config edit
# 预期: 使用 $EDITOR 环境变量指定的编辑器打开配置文件
```

### 3.5 查看 Providers

```bash
poetry run anyclaw config providers
# 预期输出: 显示 openai/anthropic/zai 配置状态的表格
```

---

## 4. 工作区管理测试

### 4.1 初始化工作区

```bash
# 创建默认工作区 (~/.anyclaw/workspace)
poetry run anyclaw setup

# 预期输出:
# - 工作区创建成功
# - 创建文件列表 (SOUL.md, USER.md, AGENTS.md, TOOLS.md, HEARTBEAT.md, memory/, skills/)
# - Git 仓库初始化状态

# 强制重新创建
poetry run anyclaw setup --force

# 跳过 git 初始化
poetry run anyclaw setup --no-git

# 指定自定义路径
poetry run anyclaw setup --workspace /tmp/test-workspace
```

### 4.2 项目级初始化

```bash
# 在当前目录创建 .anyclaw
cd /tmp/test-project
poetry run anyclaw init

# 预期输出:
# - 在当前目录创建 .anyclaw/
# - 同步模板文件
```

### 4.3 Workspace 子命令

```bash
# 查看工作区状态
poetry run anyclaw workspace status

# 列出工作区文件
poetry run anyclaw workspace list

# 同步模板
poetry run anyclaw workspace sync
```

---

## 5. 技能系统测试

### 5.1 创建技能

```bash
# 创建基础技能
poetry run anyclaw skill create my-first-skill

# 预期输出:
# - Created skill: ./my-first-skill
# - Files: SKILL.md

# 指定输出路径
poetry run anyclaw skill create test-skill --path /tmp/skills

# 带资源目录
poetry run anyclaw skill create data-skill --resources data,templates

# 带描述
poetry run anyclaw skill create helper-skill --description "A helper skill"

# 带示例文件
poetry run anyclaw skill create demo-skill --examples
```

### 5.2 验证技能

```bash
# 验证技能目录
poetry run anyclaw skill validate ./my-first-skill
# 预期: ✓ Skill is valid!

# 验证 SKILL.md 文件
poetry run anyclaw skill validate ./my-first-skill/SKILL.md

# 验证无效技能 (测试错误处理)
mkdir -p /tmp/invalid-skill
poetry run anyclaw skill validate /tmp/invalid-skill
# 预期: ✗ Validation failed (缺少 SKILL.md)
```

### 5.3 列出技能

```bash
# 列出已安装技能
poetry run anyclaw skill list

# 列出所有技能 (包括内置)
poetry run anyclaw skill list --all
```

### 5.4 安装技能

```bash
# 从目录安装
poetry run anyclaw skill install ./my-first-skill

# 强制覆盖安装
poetry run anyclaw skill install ./my-first-skill --force

# 从 .skill 文件安装 (需要先打包)
poetry run anyclaw skill install ./my-first-skill.skill
```

### 5.5 打包技能

```bash
# 打包技能
poetry run anyclaw skill package ./my-first-skill

# 指定输出目录
poetry run anyclaw skill package ./my-first-skill --output /tmp/packages

# 跳过验证打包
poetry run anyclaw skill package ./my-first-skill --no-validate
```

### 5.6 查看技能详情

```bash
# 显示技能详情
poetry run anyclaw skill show my-first-skill

# 预期输出:
# - 技能名称和描述
# - 源路径
# - 内容预览
# - 依赖状态
```

### 5.7 重载技能

```bash
# 重载所有技能
poetry run anyclaw skill reload

# 重载单个技能
poetry run anyclaw skill reload my-first-skill
```

---

## 6. MCP 服务测试

### 6.1 列出 MCP Servers

```bash
poetry run anyclaw mcp list

# 无配置时预期输出:
# - "没有配置 MCP Server"
# - 配置示例说明

# 有配置时预期输出:
# - 表格显示: 名称、类型、地址/命令、超时、启用工具
```

### 6.2 测试 MCP 连接

```bash
# 测试指定 server (需要先配置)
poetry run anyclaw mcp test filesystem

# 指定超时时间
poetry run anyclaw mcp test filesystem --timeout 30

# 测试不存在的 server (错误处理)
poetry run anyclaw mcp test nonexistent
# 预期: 错误: MCP Server 'nonexistent' 未配置
```

### 6.3 MCP 配置示例

```json
// ~/.anyclaw/config.json 中添加
{
  "mcp_servers": {
    "filesystem": {
      "command": "npx",
      "args": ["-y", "@modelcontextprotocol/server-filesystem", "~"],
      "tool_timeout": 30,
      "enabled_tools": ["*"]
    }
  }
}
```

---

## 7. Agent 聊天测试

### 7.1 启动聊天

```bash
# 启动交互式聊天
poetry run anyclaw chat

# 预期输出:
# - "Starting AnyClaw..."
# - "Workspace: ~/.anyclaw/workspace"
# - "Streaming: enabled/disabled"
# - "Loaded N skills"

# 指定 Agent 名称
poetry run anyclaw chat --agent-name TestAgent

# 指定模型
poetry run anyclaw chat --model gpt-4o
poetry run anyclaw chat --model glm-4.7

# 禁用流式输出
poetry run anyclaw chat --no-stream

# 指定工作区
poetry run anyclaw chat --workspace /tmp/test-workspace
```

### 7.2 聊天交互测试

```
# 进入聊天后测试:
> 你好
# 预期: Agent 回复问候

> 你叫什么名字?
# 预期: 返回配置的 Agent 名称

> 退出
# 预期: 退出聊天会话
```

---

## 8. 技能对话模式测试

技能对话模式允许 Agent 在对话中动态创建、验证和管理技能，实现技能的自助式开发。

### 8.1 skill-creator 内置技能验证

```bash
# 验证 skill-creator 技能存在
ls ~/.anyclaw/workspace/skills/skill-creator/
# 或检查内置目录
ls anyclaw/anyclaw/skills/builtin/skill-creator/

# 预期输出:
# SKILL.md  (必需)
# scripts/  (可选)
# references/  (可选)
```

### 8.2 在对话中创建技能

```
# 启动聊天
poetry run anyclaw chat

# 进入聊天后，请求创建技能:
> 请帮我创建一个名为 "code-reviewer" 的技能，用于代码审查

# 预期 Agent 行为:
# 1. Agent 识别到技能创建请求
# 2. 调用 create_skill 工具
# 3. 返回创建结果:
#    [OK] Skill 'code-reviewer' created at: ~/.anyclaw/workspace/skills/code-reviewer/
# 4. 提示用户可以编辑 SKILL.md 添加详细说明
```

### 8.3 create_skill 工具测试

```
# 在聊天中测试 create_skill 工具

# 测试 1: 创建基础技能
> 使用 create_skill 创建一个名为 "test-skill" 的技能，描述为"测试技能"

# 预期输出:
# [OK] Skill 'test-skill' created at: ...

# 测试 2: 创建带资源的技能
> 创建一个名为 "api-helper" 的技能，包含 scripts 和 references 资源目录

# 预期输出:
# [OK] Skill 'api-helper' created with resources: scripts, references

# 测试 3: 创建已存在的技能（错误处理）
> 再次创建名为 "test-skill" 的技能

# 预期输出:
# [ERROR] Skill 'test-skill' already exists. Use --force to overwrite.
```

### 8.4 validate_skill 工具测试

```
# 在聊天中验证技能

# 测试 1: 验证有效技能
> 验证 test-skill 技能的格式是否正确

# 预期输出:
# [OK] Skill 'test-skill' is valid!
# - Has SKILL.md
# - Valid frontmatter (name, description)
# - Body content present

# 测试 2: 验证无效技能
> 验证一个不存在的技能路径

# 预期输出:
# [ERROR] Path does not exist: /path/to/nonexistent

# 测试 3: 验证缺少必需字段的技能
# (先手动创建一个无效的 SKILL.md)
> 验证 invalid-skill 技能

# 预期输出:
# [ERROR] Validation failed:
# - Missing required field: name
# - Missing required field: description
```

### 8.5 reload_skill 工具测试

```
# 测试技能热重载

# 测试 1: 重载所有技能
> 重载所有技能

# 预期输出:
# [OK] Reloaded 5 skills (5 success, 0 failed)

# 测试 2: 重载单个技能
> 重载 test-skill 技能

# 预期输出:
# [OK] Skill 'test-skill' reloaded successfully

# 测试 3: 重载不存在的技能
> 重载 nonexistent-skill 技能

# 预期输出:
# [ERROR] Skill 'nonexistent-skill' not found
```

### 8.6 show_skill 工具测试

```
# 查看技能详情

# 测试 1: 显示存在的技能
> 显示 test-skill 技能的详情

# 预期输出:
# === Skill: test-skill ===
# Source: workspace
# Path: ~/.anyclaw/workspace/skills/test-skill
# Description: 测试技能
# Content Preview:
# [SKILL.md 内容预览...]

# 测试 2: 显示不存在的技能
> 显示 nonexistent-skill 技能的详情

# 预期输出:
# [ERROR] Skill 'nonexistent-skill' not found
```

### 8.7 list_skills 工具测试

```
# 列出所有技能

# 测试 1: 列出所有可用技能
> 列出所有技能

# 预期输出:
# === Available Skills ===
# [Python Skills]
# - echo (bundled) - Echo input text
# - calc (bundled) - Calculator operations
#
# [MD Skills]
# - skill-creator (bundled) - Create or update AgentSkills
# - test-skill (workspace) - 测试技能
# Total: 4 skills

# 测试 2: 空技能列表
# (在新的工作区中)
> 列出所有技能

# 预期输出:
# No skills installed. Use 'create_skill' to create one.
```

### 8.8 热重载检测测试

```bash
# 手动测试热重载检测

# 1. 启动聊天
poetry run anyclaw chat

# 2. 在另一个终端创建新技能
poetry run anyclaw skill create hot-reload-test

# 3. 回到聊天，发送消息
> 你好

# 预期: Agent 应该检测到技能变化并自动重载
# 输出可能包含:
# [System] Detected skill changes, reloading...
# [System] Reloaded 1 new skill(s)

# 4. 验证新技能可用
> 列出所有技能

# 预期输出包含: hot-reload-test
```

### 8.9 完整工作流测试

```
# 在对话中完成完整的技能创建流程

# Step 1: 创建技能
> 创建一个名为 "code-formatter" 的技能，
> 描述为 "代码格式化工具，支持 Python、JavaScript、TypeScript"，
> 包含 scripts 资源目录

# 预期: [OK] Skill created...

# Step 2: 查看技能
> 显示 code-formatter 技能的详情

# 预期: 显示技能信息和内容预览

# Step 3: 编辑技能 (Agent 无法直接编辑，但可以指导用户)
> 我应该如何编辑这个技能？

# 预期: Agent 提供编辑指导，说明 SKILL.md 的位置和格式

# Step 4: 验证技能
> 验证 code-formatter 技能

# 预期: [OK] Skill is valid!

# Step 5: 重载技能
> 重载 code-formatter 技能

# 预期: [OK] Skill reloaded

# Step 6: 确认技能可用
> 列出所有技能

# 预期: 输出包含 code-formatter
```

### 8.10 技能即时可用测试

```
# 验证新创建的技能在下次对话中可用

# 1. 启动新对话
poetry run anyclaw chat

# 2. 创建技能
> 创建技能 "quick-test"，描述 "快速测试技能"

# 3. 退出对话
> 退出

# 4. 启动新对话
poetry run anyclaw chat

# 5. 检查技能是否可用
> 列出所有技能

# 预期: quick-test 出现在技能列表中

# 6. 使用新技能（如果技能内容完整）
> 使用 quick-test 技能

# 预期: Agent 根据 quick-test 的 SKILL.md 内容执行操作
```

---

## 9. Provider 管理测试

### 9.1 Onboard 配置

```bash
# 查看认证选项
poetry run anyclaw onboard --list-auth-choices

# 交互式配置
poetry run anyclaw onboard
```

### 9.2 Token 管理

```bash
# 查看token使用情况
poetry run anyclaw token status

# 查看token统计
poetry run anyclaw token stats
```

---

## 10. 错误处理测试

### 10.1 无效命令

```bash
# 执行不存在的命令
poetry run anyclaw invalid-command
# 预期: 显示错误信息和帮助
```

### 10.2 缺少参数

```bash
# skill create 缺少名称
poetry run anyclaw skill create
# 预期: 错误提示缺少必需参数

# config set 缺少值
poetry run anyclaw config set openai.api_key
# 预期: 用法提示
```

### 10.3 无效配置键

```bash
poetry run anyclaw config set invalid.key value
# 预期: "未知的配置段: invalid"
```

### 10.4 文件不存在

```bash
poetry run anyclaw skill validate /nonexistent/path
# 预期: 错误提示路径不存在

poetry run anyclaw skill install /nonexistent/path
# 预期: 错误提示路径未找到
```

### 10.5 技能已存在

```bash
# 安装已存在的技能 (不使用 --force)
poetry run anyclaw skill install ./my-first-skill
poetry run anyclaw skill install ./my-first-skill
# 预期: "Skill already exists" 提示使用 --force
```

---

## 11. 集成测试场景

### 11.1 完整工作流程

```bash
# 1. 清理环境
rm -rf ~/.anyclaw
rm -rf /tmp/anyclaw-test

# 2. 初始化配置
poetry run anyclaw config init

# 3. 设置 API Key
poetry run anyclaw config set zai.api_key your-api-key

# 4. 创建工作区
poetry run anyclaw setup --workspace /tmp/anyclaw-test

# 5. 创建并验证技能
cd /tmp
poetry run anyclaw skill create test-integration --description "Integration test skill"
poetry run anyclaw skill validate ./test-integration

# 6. 安装技能
poetry run anyclaw skill install ./test-integration

# 7. 验证安装
poetry run anyclaw skill list | grep test-integration

# 8. 查看技能详情
poetry run anyclaw skill show test-integration

# 9. 启动聊天 (需要有效 API Key)
poetry run anyclaw chat --workspace /tmp/anyclaw-test --no-stream

# 10. 清理
poetry run anyclaw skill list  # 确认技能存在
```

### 11.2 多 Provider 切换

```bash
# 设置 OpenAI
poetry run anyclaw config set llm.provider openai
poetry run anyclaw config set llm.model gpt-4o-mini
poetry run anyclaw config show

# 切换到 ZAI
poetry run anyclaw config set llm.provider zai
poetry run anyclaw config set llm.model glm-4.7
poetry run anyclaw config show

# 验证切换成功
poetry run anyclaw config providers
```

### 11.3 工作区模板同步

```bash
# 创建新工作区
poetry run anyclaw setup --workspace /tmp/sync-test

# 删除部分模板文件
rm /tmp/sync-test/workspace/SOUL.md

# 重新同步
poetry run anyclaw setup --workspace /tmp/sync-test
# 预期: 只创建缺失的 SOUL.md

# 强制重建
poetry run anyclaw setup --workspace /tmp/sync-test --force
# 预期: 重新创建所有文件
```

---

## 测试检查清单

### 基础功能

- [ ] `anyclaw version` 正确显示版本
- [ ] `anyclaw --help` 显示完整命令列表
- [ ] `anyclaw providers` 显示 provider 状态

### 配置管理

- [ ] `config init` 创建配置文件
- [ ] `config show` 显示所有配置
- [ ] `config set` 正确更新配置值
- [ ] `config path` 返回正确路径

### 工作区

- [ ] `setup` 创建完整工作区结构
- [ ] `init` 在当前目录创建 .anyclaw
- [ ] 模板同步只创建缺失文件

### 技能系统

- [ ] `skill create` 生成正确的目录结构
- [ ] `skill validate` 检测有效/无效技能
- [ ] `skill list` 显示已安装技能
- [ ] `skill install` 正确安装技能
- [ ] `skill package` 生成 .skill 文件
- [ ] `skill show` 显示技能详情
- [ ] `skill reload` 重载技能

### 技能对话模式 (Skill Conversation Mode)

- [ ] Agent 能读取 skill-creator 内置技能
- [ ] Agent 能在对话中创建新技能 (create_skill 工具)
- [ ] 新创建的技能在下次对话中立即可用
- [ ] Agent 能验证技能格式 (validate_skill 工具)
- [ ] Agent 能重载技能 (reload_skill 工具)
- [ ] Agent 能查看技能详情 (show_skill 工具)
- [ ] Agent 能列出所有技能 (list_skills 工具)
- [ ] 热重载检测功能正常工作

### MCP

- [ ] `mcp list` 显示配置的 servers
- [ ] `mcp test` 测试连接成功/失败

### Agent

- [ ] `chat` 启动交互式会话
- [ ] 流式/非流式模式切换正常
- [ ] 自定义 workspace 生效

### 错误处理

- [ ] 无效命令正确报错
- [ ] 缺少参数显示用法
- [ ] 文件不存在正确处理
- [ ] 配置错误给出明确提示

---

## 自动化测试脚本

```bash
#!/bin/bash
# run_cli_tests.sh - 自动化 CLI 测试脚本

set -e

echo "=== AnyClaw CLI 测试 ==="

# 进入项目目录
cd /Users/ryan/mycode/AnyClaw/anyclaw

# 1. 基础测试
echo "[1/8] 基础命令测试..."
poetry run anyclaw version
poetry run anyclaw --help

# 2. 配置测试
echo "[2/8] 配置管理测试..."
poetry run anyclaw config show
poetry run anyclaw config path

# 3. Provider 测试
echo "[3/8] Provider 测试..."
poetry run anyclaw providers

# 4. 工作区测试
echo "[4/8] 工作区测试..."
rm -rf /tmp/anyclaw-test-ws
poetry run anyclaw setup --workspace /tmp/anyclaw-test-ws --no-git

# 5. 技能测试
echo "[5/8] 技能系统测试..."
rm -rf /tmp/test-skill
poetry run anyclaw skill create test-skill --path /tmp
poetry run anyclaw skill validate /tmp/test-skill
poetry run anyclaw skill list

# 6. MCP 测试
echo "[6/8] MCP 测试..."
poetry run anyclaw mcp list

# 7. 帮助测试
echo "[7/8] 帮助命令测试..."
poetry run anyclaw skill --help
poetry run anyclaw mcp --help
poetry run anyclaw config --help

# 8. 清理
echo "[8/8] 清理测试环境..."
rm -rf /tmp/anyclaw-test-ws
rm -rf /tmp/test-skill

echo "=== 所有测试完成 ==="
```

---

## 测试环境要求

- Python 3.9+
- Poetry 已安装
- 至少配置一个有效的 Provider API Key (用于聊天测试)
- Node.js 和 npm (用于 MCP filesystem server 测试)

## 注意事项

1. 某些测试需要有效的 API Key 才能通过
2. MCP 测试需要预先配置 MCP Server
3. 集成测试会创建临时文件和目录
4. 测试完成后建议清理临时环境
