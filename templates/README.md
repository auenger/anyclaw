# Workspace 模板文件

此目录包含 AnyClaw workspace 的默认模板文件。

## 目录结构

```
templates/
├── AGENTS.md      # Agent 指令（行为规则、工具使用指南）
├── USER.md        # 用户档案（偏好、背景信息）
├── SOUL.md        # Agent 人格（性格、价值观）
├── TOOLS.md       # 工具说明（约束、最佳实践）
├── IDENTITY.md    # Agent 身份（名称、头像）
├── HEARTBEAT.md   # 心跳任务（定期执行的任务）
├── BOOTSTRAP.md   # 引导文件说明
├── README.md      # 本文件
└── memory/
    ├── MEMORY.md  # 长期记忆
    └── HISTORY.md # 对话历史摘要
```

## 使用方式

### 方式一：命令行初始化

```bash
# 在项目目录初始化 workspace
cd /your/project
anyclaw init

# 或初始化全局 workspace
anyclaw setup
```

### 方式二：手动复制

```bash
# 复制到全局 workspace
cp -r templates/* ~/.anyclaw/workspace/

# 复制到项目目录
cp -r templates/* /your/project/.anyclaw/
```

## 文件说明

### AGENTS.md - Agent 指令

定义 Agent 的行为规则：
- 定时提醒使用方式
- 心跳任务管理
- 技能使用指南
- 工具调用最佳实践

### USER.md - 用户档案

存储用户偏好：
- 基本信息（名称、时区、语言）
- 沟通风格偏好
- 技术水平
- 工作背景
- 感兴趣的话题

### SOUL.md - Agent 人格

定义 Agent 的性格和价值观：
- 核心原则（有帮助、有主见、有资源）
- 边界（隐私保护、外部行动谨慎）
- 风格（简洁、不啰嗦）

### TOOLS.md - 工具说明

记录工具使用的约束：
- exec 安全限制
- cron 定时提醒
- 文件操作
- 技能系统

### IDENTITY.md - Agent 身份

定义 Agent 的元信息：
- 名称
- 类型（AI/robot/familiar）
- 风格
- 表情符号
- 头像

### HEARTBEAT.md - 心跳任务

定义定期执行的任务：
- 周期性检查
- 定期提醒
- 后台监控

### memory/MEMORY.md - 长期记忆

存储重要信息：
- 用户偏好
- 项目上下文
- 重要事项

### memory/HISTORY.md - 历史摘要

存储对话历史摘要，用于长期上下文保持。

## 自定义

你可以根据需要修改这些模板文件：

1. **编辑 AGENTS.md**：添加项目特定的指令
2. **编辑 USER.md**：填写你的个人偏好
3. **编辑 SOUL.md**：调整 Agent 的性格
4. **编辑 TOOLS.md**：添加项目特定的工具说明

## 最佳实践

1. **保持简洁**：模板文件不宜过长，避免占用过多 token
2. **定期更新**：随着使用调整文件内容
3. **记忆管理**：重要信息写入 MEMORY.md
4. **技能复用**：常用操作封装成技能放在 `skills/` 目录
