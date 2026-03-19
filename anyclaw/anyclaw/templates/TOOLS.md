# 工具使用说明

工具签名通过 function calling 自动提供。
此文件记录非显而易见的约束和使用模式。

## exec — 安全限制

- 命令有可配置的超时时间（默认 60 秒）
- 危险命令被阻止（rm -rf、format、dd、shutdown 等）
- 输出在 10,000 字符处截断
- `restrict_to_workspace` 配置可以将文件访问限制在工作区内

## cron — 定时提醒

- 请参考 cron 技能了解用法

## 文件操作

- `read_file`: 读取文件内容
- `write_file`: 写入文件（覆盖）
- `list_dir`: 列出目录内容

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
  "security": {
    "restrict_to_workspace": false
  }
}
```

### 行为说明

- `restrict_to_workspace=true`（默认）：只能写入 workspace 目录及其子目录
- `restrict_to_workspace=false`：允许写入任意路径（受系统权限限制）
- 符号链接会被解析为真实路径进行验证
