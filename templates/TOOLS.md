# 工具使用说明

工具签名通过 function calling 自动提供。
此文件记录非显而易见的约束和使用模式。

## exec — 安全限制

ExecTool 实现了**混合模式安全限制**，包含两层保护：

### 核心保护层 [CoreGuard]

硬编码的、**不可绕过**的危险命令拦截：

- **Unix 删除**: `rm -rf`, `rm -fr`
- **Windows 删除**: `del /f`, `rmdir /s`, `rd /s`
- **磁盘操作**: `dd if=`, `mkfs`, `diskpart`, `format`
- **系统电源**: `shutdown`, `reboot`, `poweroff`, `halt`
- **危险权限**: `chmod 777`
- **系统文件**: 写入 `/etc/passwd`, `/etc/shadow`
- **Fork bomb**: `:(){ :|:& };:`

核心保护**不可通过配置关闭**，确保基本安全底线。

### 用户自定义层 [UserGuard]

可通过配置文件添加额外的安全规则：

**配置文件 (~/.anyclaw/config.json)：**
```json
{
  "exec_deny_patterns": ["npm publish", "git push --force"],
  "exec_allow_patterns": []
}
```

**白名单模式**：设置 `exec_allow_patterns` 后，只有匹配的命令允许执行。

### 其他限制

- 命令有可配置的超时时间（默认 60 秒，最大 300 秒）
- 输出在 10,000 字符处截断
- `restrict_to_workspace` 配置可以将文件访问限制在工作区内

### CLI 命令

```bash
# 查看当前安全规则
anyclaw security show

# 测试命令是否会被阻止
anyclaw security test "rm -rf /"

# 列出所有规则（简洁版）
anyclaw security list
```

## cron — 定时提醒

- 使用 `cron` 工具创建/列出/删除定时任务
- 支持自然语言时间表达式（如 "tomorrow at 9am", "every 5 minutes"）
- 提醒消息会发送到当前会话

## 文件操作

- `read_file`: 读取文件内容
- `write_file`: 写入文件（覆盖）
- `edit_file`: 编辑文件（替换指定内容）
- `list_dir`: 列出目录内容
- `search_files`: 搜索文件（按名称或内容）

## 技能系统

- `skill.load <name>`: 加载技能详细内容
- 技能摘要会自动包含在上下文中
- 按需加载技能详情以节省 token

## 安全配置 — restrict_to_workspace

默认情况下，`write_file` 工具只允许在 workspace 目录内写入文件，提升安全性。

### 配置方式

**通过环境变量：**
```bash
export ANYCLAW_RESTRICT_TO_WORKSPACE=false
```

**通过配置文件 (~/.anyclaw/config.json)：**
```json
{
  "restrict_to_workspace": false
}
```

### 行为说明

- `restrict_to_workspace=true`（默认）：只能写入 workspace 目录及其子目录
- `restrict_to_workspace=false`：允许写入任意路径（受系统权限限制）
- 符号链接会被解析为真实路径进行验证
