# feat-session-cwd: 会话级工作目录

## 背景

当前存在两个问题：

**问题 1: 命令行 cd 模式效率低**
- ExecTool 已支持 `working_dir` 参数，但 LLM 习惯使用 `cd /path && cmd` 模式
- 命令可读性差，每次都需要重复 cd，日志充斥 `cd /path &&` 前缀

**问题 2: 文件工具权限检查不一致**
- ReadFileTool 有 `allow_all_access` 检查
- WriteFileTool、ListDirTool 缺少此检查
- 导致设置 `allow_all_access = true` 后仍报 "Path traversal detected" 错误

## 用户价值点

### VP1: 会话级 cwd 继承

在 Session.metadata 中存储当前工作目录，后续命令自动继承。

**Gherkin 场景:**

```gherkin
Feature: 会话级 cwd 继承

  Scenario: 首次执行命令使用默认 cwd
    Given 一个新会话
    When 用户执行命令 "ls"
    Then 命令在 os.getcwd() 目录执行

  Scenario: 设置 cwd 后后续命令自动继承
    Given 一个新会话
    When 用户执行命令设置 working_dir 为 "/Users/ryan/mycode/HRExcel/pyexcel"
    And 用户执行命令 "cat config.ini"
    Then 命令在 "/Users/ryan/mycode/HRExcel/pyexcel" 目录执行
    And 命令参数中无需指定 working_dir

  Scenario: 会话持久化保留 cwd
    Given 一个会话的 cwd 设置为 "/path/to/project"
    When 会话保存并重新加载
    Then cwd 仍然为 "/path/to/project"
```

### VP2: cd 命令智能检测

自动检测命令中的 `cd /path` 模式，更新会话 cwd。

**Gherkin 场景:**

```gherkin
Feature: cd 命令智能检测

  Scenario: 检测 cd 命令更新 cwd
    Given 一个新会话
    When 用户执行命令 "cd /Users/ryan/mycode/HRExcel/pyexcel"
    Then 会话 cwd 更新为 "/Users/ryan/mycode/HRExcel/pyexcel"
    And 后续命令在该目录执行

  Scenario: 检测 cd && 组合命令
    Given 一个新会话
    When 用户执行命令 "cd /path/to/project && cat config.ini"
    Then 会话 cwd 更新为 "/path/to/project"
    And 命令在 "/path/to/project" 目录执行

  Scenario: 相对路径 cd 相对于当前 cwd
    Given 会话 cwd 为 "/Users/ryan/mycode"
    When 用户执行命令 "cd HRExcel/pyexcel"
    Then 会话 cwd 更新为 "/Users/ryan/mycode/HRExcel/pyexcel"

  Scenario: 无效路径 cd 不更新 cwd
    Given 会话 cwd 为 "/Users/ryan/mycode"
    When 用户执行命令 "cd /nonexistent/path"
    Then 会话 cwd 保持不变
```

### VP3: 工具描述增强

优化 ExecTool 的 description，引导 LLM 优先使用 `working_dir` 参数。

**Gherkin 场景:**

```gherkin
Feature: 工具描述增强

  Scenario: ExecTool description 包含 working_dir 使用说明
    When 获取 ExecTool 的 description
    Then description 应包含 working_dir 参数说明
    And description 应建议使用 working_dir 而非 cd && 组合

  Scenario: ExecTool parameters 包含 working_dir 示例
    When 获取 ExecTool 的 parameters schema
    Then working_dir 参数应有清晰的 description
    And description 应包含使用示例
```

### VP4: 文件工具统一权限检查

所有文件操作工具统一支持 `allow_all_access` 配置，确保权限检查一致性。

**Gherkin 场景:**

```gherkin
Feature: 文件工具统一权限检查

  Scenario: WriteFileTool 支持 allow_all_access
    Given 配置 allow_all_access = true
    When 用户写入文件到任意路径 "/tmp/test/file.txt"
    Then 操作成功执行
    And 不报 "Path traversal detected" 错误

  Scenario: ListDirTool 支持 allow_all_access
    Given 配置 allow_all_access = true
    When 用户列出任意目录 "/tmp/test"
    Then 操作成功执行
    And 不报路径限制错误

  Scenario: 关闭 allow_all_access 时仍执行安全检查
    Given 配置 allow_all_access = false
    When 用户尝试访问 workspace 外的路径
    Then 操作被拒绝
    And 返回清晰的权限错误信息

  Scenario: 工具初始化时正确传递 path_guard
    Given 配置 allow_all_access = false 且 restrict_to_workspace = true
    When AgentLoop 初始化文件工具
    Then 工具应收到正确配置的 path_guard 实例
```

## 技术方案

### 1. Session 扩展

```python
# anyclaw/session/models.py
@dataclass
class Session:
    # ... 现有字段 ...

    def get_cwd(self) -> str:
        """获取当前工作目录"""
        return self.metadata.get("cwd", os.getcwd())

    def set_cwd(self, path: str) -> bool:
        """设置工作目录（验证路径存在性）"""
        if os.path.isdir(path):
            self.metadata["cwd"] = str(Path(path).resolve())
            return True
        return False
```

### 2. ExecTool 扩展

```python
# anyclaw/tools/shell.py
class ExecTool(Tool):
    def __init__(self, session: Optional[Session] = None, ...):
        self.session = session
        # ...

    async def execute(self, command: str, working_dir: Optional[str] = None, ...):
        # 优先级: 参数 > session.cwd > self.working_dir > os.getcwd()
        cwd = working_dir or (self.session.get_cwd() if self.session else None) or self.working_dir or os.getcwd()

        # 检测 cd 命令，更新 session cwd
        new_cwd = self._detect_cd_command(command, cwd)
        if new_cwd and self.session:
            self.session.set_cwd(new_cwd)

        # ...

    def _detect_cd_command(self, command: str, cwd: str) -> Optional[str]:
        """检测 cd 命令并返回新目录"""
        # 匹配 "cd /path" 或 "cd /path && ..." 模式
        # 返回解析后的绝对路径（如果有效）
```

### 3. 工具描述优化

```python
@property
def description(self) -> str:
    return """执行 shell 命令并返回输出。

使用建议：
- 固定项目目录时，使用 working_dir 参数而非 cd && 组合
- 示例: {"command": "cat config.ini", "working_dir": "/path/to/project"}
- 设置 working_dir 后，后续命令可省略该参数（会话级继承）"""

@property
def parameters(self) -> Dict[str, Any]:
    return {
        "type": "object",
        "properties": {
            "command": {
                "type": "string",
                "description": "要执行的 shell 命令",
            },
            "working_dir": {
                "type": "string",
                "description": "工作目录（推荐用于固定项目路径）。设置后，后续命令自动继承此目录。",
            },
            # ...
        },
        "required": ["command"],
    }
```

### 4. 文件工具统一权限检查

```python
# anyclaw/tools/filesystem.py

class WriteFileTool(Tool):
    async def execute(self, path: str, content: str, **kwargs: Any) -> str:
        from anyclaw.config.settings import settings

        try:
            # 检查是否开放所有权限（与 ReadFileTool 保持一致）
            if settings.allow_all_access:
                file_path = Path(path).expanduser().resolve()
            elif self.path_guard:
                file_path = self.path_guard.resolve_and_validate(path, for_write=True)
            else:
                # 旧逻辑...
                pass
            # ...

class ListDirTool(Tool):
    async def _list_directory(self, path: str, max_entries: int) -> str:
        from anyclaw.config.settings import settings

        # 检查是否开放所有权限（与 ReadFileTool 保持一致）
        if settings.allow_all_access:
            dir_path = Path(path).expanduser().resolve()
        elif self.path_guard:
            dir_path = self.path_guard.resolve_and_validate(path)
        else:
            dir_path = self._resolve_path(path)
        # ...
```

### 5. 工具初始化优化

```python
# anyclaw/agent/loop.py
def _register_tools(self):
    from anyclaw.security.path import create_path_guard_from_settings

    # 创建 path_guard（自动处理 allow_all_access）
    path_guard = create_path_guard_from_settings(self.workspace)

    self.tools.register(ReadFileTool(
        workspace=self.workspace,
        path_guard=path_guard,  # 传递 path_guard
    ))
    self.tools.register(WriteFileTool(
        workspace=self.workspace,
        path_guard=path_guard,  # 传递 path_guard
        restrict_to_workspace=settings.restrict_to_workspace,
    ))
    self.tools.register(ListDirTool(
        workspace=self.workspace,
        path_guard=path_guard,  # 传递 path_guard
        timeout=list_dir_timeout,
        max_entries=list_dir_max_entries,
    ))
```

## 风险评估

| 风险 | 影响 | 缓解措施 |
|------|------|---------|
| cd 检测误判 | 中 | 使用严格正则，仅匹配标准 cd 模式 |
| 相对路径解析错误 | 低 | 相对于当前 cwd 解析，失败不更新 |
| Session 不兼容 | 低 | 使用 metadata 字典存储，向后兼容 |

## 依赖

无外部依赖。
