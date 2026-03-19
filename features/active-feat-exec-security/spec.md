# ExecTool 危险命令混合模式安全限制

## 背景

当前 ExecTool 通过 `deny_patterns` 拦截危险命令，但存在两个问题：
1. 默认的 deny_patterns 覆盖不够全面（缺少 Windows 命令、dd、format、fork bomb 等）
2. deny_patterns 完全可配置，无法保证核心安全策略不被绕过

## 需求

实现**混合模式**安全限制：
- **核心保护层**: 硬编码的不可配置关闭的危险命令拦截
- **扩展保护层**: 用户可通过配置文件自定义 deny/allow patterns

## 用户价值点

### VP1: 核心保护层（Core Guard）

硬编码的、不可绕过的危险命令拦截，确保基本安全底线。

**Gherkin 场景**:

```gherkin
Feature: 核心保护层

  Scenario: 拦截 rm -rf 命令
    Given 用户尝试执行 "rm -rf /"
    When ExecTool 执行命令前检查
    Then 返回错误 "命令被安全策略阻止"
    And 命令不会被执行

  Scenario: 拦截 dd 命令
    Given 用户尝试执行 "dd if=/dev/zero of=/dev/sda"
    When ExecTool 执行命令前检查
    Then 返回错误 "命令被安全策略阻止"

  Scenario: 拦截系统关机命令
    Given 用户尝试执行 "shutdown -h now"
    When ExecTool 执行命令前检查
    Then 返回错误 "命令被安全策略阻止"

  Scenario: 拦截磁盘格式化命令
    Given 用户尝试执行 "mkfs.ext4 /dev/sda1"
    When ExecTool 执行命令前检查
    Then 返回错误 "命令被安全策略阻止"

  Scenario: 拦截 fork bomb
    Given 用户尝试执行 ":(){ :|:& };:"
    When ExecTool 执行命令前检查
    Then 返回错误 "命令被安全策略阻止"

  Scenario: 拦截 Windows 危险命令
    Given 用户尝试执行 "format C:"
    When ExecTool 执行命令前检查
    Then 返回错误 "命令被安全策略阻止"

  Scenario: 核心保护不可通过配置关闭
    Given 用户在配置中设置空的 deny_patterns
    When ExecTool 初始化
    Then 核心保护模式仍然生效
```

### VP2: 可配置扩展层（Configurable Guard）

用户可通过配置文件自定义额外的安全规则。

**Gherkin 场景**:

```gherkin
Feature: 可配置扩展层

  Scenario: 用户添加自定义 deny_pattern
    Given 配置文件中添加 deny_pattern "npm publish"
    When 用户尝试执行 "npm publish"
    Then 返回错误 "命令被安全策略阻止"

  Scenario: 用户使用 allow_patterns 白名单模式
    Given 配置中设置 allow_patterns ["git status", "ls"]
    When 用户尝试执行 "git status"
    Then 命令正常执行

  Scenario: allow_patterns 阻止非白名单命令
    Given 配置中设置 allow_patterns ["git status", "ls"]
    When 用户尝试执行 "npm install"
    Then 返回错误 "命令不在允许列表中"

  Scenario: 自定义规则与核心保护共存
    Given 用户配置空的 deny_patterns
    And 用户添加自定义 deny_pattern "npm publish"
    When 用户尝试执行 "rm -rf /"
    Then 仍然被核心保护拦截

  Scenario: 通过配置查看当前安全规则
    Given 用户执行 "anyclaw config show security"
    Then 显示核心保护规则（标记为 [core]）
    And 显示用户自定义规则（标记为 [user]）
```

## 技术方案

### 1. 核心保护模式定义

```python
# anyclaw/tools/guards.py

CORE_DENY_PATTERNS = [
    # Unix 删除
    r"\brm\s+-[rf]{1,2}\b",
    # Windows 删除
    r"\bdel\s+/[sfq]\b",
    r"\brmdir\s+/[sq]\b",
    # 磁盘操作
    r"\bdd\s+if=",
    r">\s*/dev/sd",
    r"\b(mkfs|diskpart)\b",
    r"(?:^|[;&|]\s*)format\b",
    # 系统电源
    r"\b(shutdown|reboot|poweroff|halt)\b",
    # Fork bomb
    r":\(\)\s*\{.*\};\s*:",
]
```

### 2. 配置扩展

```json
// ~/.anyclaw/config.json
{
  "security": {
    "deny_patterns": [
      "npm publish",
      "git push --force"
    ],
    "allow_patterns": []  // 空 = 禁用白名单模式
  }
}
```

### 3. ExecTool 改造

```python
class ExecTool(Tool):
    def __init__(self, ...):
        # 核心保护（不可覆盖）
        self.core_deny_patterns = CORE_DENY_PATTERNS
        # 用户扩展（可配置）
        self.user_deny_patterns = config.get("security.deny_patterns", [])
        self.allow_patterns = config.get("security.allow_patterns", [])

    def _guard_command(self, command: str, cwd: str) -> str | None:
        # 1. 核心保护检查（优先级最高）
        for pattern in self.core_deny_patterns:
            if re.search(pattern, command, re.IGNORECASE):
                return "Error: Command blocked by core safety guard"

        # 2. 用户 deny_patterns 检查
        for pattern in self.user_deny_patterns:
            if re.search(pattern, command, re.IGNORECASE):
                return "Error: Command blocked by user policy"

        # 3. allow_patterns 白名单检查（如果启用）
        if self.allow_patterns:
            if not any(re.search(p, command) for p in self.allow_patterns):
                return "Error: Command not in allowlist"

        return None
```

## 影响范围

- `anyclaw/tools/shell.py` - ExecTool 改造
- `anyclaw/tools/guards.py` - 新建，核心保护定义
- `anyclaw/config/settings.py` - 添加 security 配置项
- `anyclaw/cli/app.py` - 添加 `anyclaw config show security` 命令
- `tests/test_exec_guard.py` - 新建测试文件

## 验收标准

- [ ] 核心保护模式覆盖所有危险命令类型
- [ ] 核心保护不可通过配置关闭
- [ ] 用户可添加自定义 deny_patterns
- [ ] 用户可启用 allow_patterns 白名单模式
- [ ] 配置变更实时生效（无需重启）
- [ ] 提供查看当前安全规则的 CLI 命令
- [ ] 测试覆盖率 > 80%
