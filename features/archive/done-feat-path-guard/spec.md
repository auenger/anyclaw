# 路径遍历防护系统

## 背景

AnyClaw 的文件系统工具（read_file, write_file, list_dir）缺乏严格的路径验证。攻击者可能通过以下方式绕过限制：
- 路径遍历：`../../../etc/passwd`
- 符号链接：创建指向系统目录的软链接
- 家目录访问：`~/.ssh/id_rsa`
- 环境变量：`$HOME/.config`

**风险**: Agent 可能读取或修改敏感系统文件、用户凭证、SSH 密钥等。

## 需求

实现严格的路径验证系统，确保所有文件操作都在允许的目录范围内。

## 用户价值点

### VP1: 路径遍历防护

阻止使用 `..`、绝对路径等方式访问工作区外的文件。

**Gherkin 场景**:

```gherkin
Feature: 路径遍历防护

  Scenario: 阻止相对路径遍历
    Given workspace 为 "/home/user/project"
    And 请求路径为 "../../../etc/passwd"
    When 验证路径
    Then 返回错误 "Path traversal detected"

  Scenario: 阻止绝对路径访问工作区外
    Given workspace 为 "/home/user/project"
    And 请求路径为 "/etc/passwd"
    When 验证路径
    Then 返回错误 "Path outside workspace"

  Scenario: 阻止家目录访问
    Given workspace 为 "/home/user/project"
    And 请求路径为 "~/.ssh/id_rsa"
    When 验证路径
    Then 返回错误 "Path outside workspace"

  Scenario: 阻止环境变量路径
    Given workspace 为 "/home/user/project"
    And 请求路径为 "$HOME/.bashrc"
    When 验证路径
    Then 返回错误 "Path outside workspace"

  Scenario: 允许工作区内正常访问
    Given workspace 为 "/home/user/project"
    And 请求路径为 "src/main.py"
    When 验证路径
    Then 解析为 "/home/user/project/src/main.py"
```

### VP2: 符号链接防护

防止通过符号链接绕过路径限制。

**Gherkin 场景**:

```gherkin
Feature: 符号链接防护

  Scenario: 阻止指向工作区外的符号链接
    Given workspace 为 "/home/user/project"
    And 存在符号链接 "link_to_secret" 指向 "/etc/secrets"
    And 请求路径为 "link_to_secret/data"
    When 验证路径
    Then 返回错误 "Symlink points outside workspace"

  Scenario: 允许工作区内的符号链接
    Given workspace 为 "/home/user/project"
    And 存在符号链接 "lib" 指向 "./vendor/lib"
    And 请求路径为 "lib/module.py"
    When 验证路径
    Then 允许访问
```

### VP3: 可配置的额外允许目录

允许配置工作区外的可信目录（如全局配置目录）。

**Gherkin 场景**:

```gherkin
Feature: 额外允许目录

  Scenario: 配置额外的允许目录
    Given workspace 为 "/home/user/project"
    And 配置 extra_allowed_dirs = ["/home/user/.config/anyclaw"]
    And 请求路径为 "/home/user/.config/anyclaw/settings.json"
    When 验证路径
    Then 允许访问

  Scenario: 额外目录的子目录也允许
    Given workspace 为 "/home/user/project"
    And 配置 extra_allowed_dirs = ["/home/user/.config"]
    And 请求路径为 "/home/user/.config/anyclaw/settings.json"
    When 验证路径
    Then 允许访问
```

## 技术方案

### 1. 路径守卫模块

```python
# anyclaw/security/path.py

import os
from pathlib import Path
from typing import Optional

class PathGuard:
    """路径安全验证器"""

    def __init__(
        self,
        workspace: Path | str,
        extra_allowed_dirs: list[Path | str] = None,
        allow_symlinks_in_workspace: bool = True,
    ):
        self.workspace = Path(workspace).resolve()
        self.extra_allowed_dirs = [
            Path(d).resolve() for d in (extra_allowed_dirs or [])
        ]
        self.allow_symlinks_in_workspace = allow_symlinks_in_workspace

    def resolve_and_validate(
        self,
        path: str | Path,
        for_write: bool = False,
    ) -> Path:
        """
        解析并验证路径

        Args:
            path: 要验证的路径
            for_write: 是否用于写入操作

        Returns:
            解析后的绝对路径

        Raises:
            PermissionError: 路径不合法
        """
        # 1. 基础路径检查
        self._check_traversal(str(path))

        # 2. 解析路径（相对于 workspace）
        p = Path(path)
        if not p.is_absolute():
            p = self.workspace / p

        # 3. 展开环境和用户
        p = self._expand_path(p)

        # 4. 解析为绝对路径（不跟随符号链接）
        try:
            resolved = p.resolve(strict=False)
        except OSError as e:
            raise PermissionError(f"Invalid path: {e}")

        # 5. 符号链接检查
        if resolved.exists() or resolved.is_symlink():
            self._check_symlink(resolved)

        # 6. 范围检查
        self._check_in_allowed_dir(resolved)

        return resolved

    def _check_traversal(self, path: str) -> None:
        """检查路径遍历攻击"""
        # 检查明显的遍历模式
        suspicious = ["../", "..\\", "/..", "\\.."]
        path_lower = path.lower()
        for pattern in suspicious:
            if pattern in path_lower:
                raise PermissionError(
                    "Path traversal detected: path contains '..'"
                )

    def _expand_path(self, path: Path) -> Path:
        """展开环境变量和用户目录"""
        # 展开用户目录 ~/
        path_str = str(path)
        path_str = os.path.expanduser(path_str)
        # 展开环境变量
        path_str = os.path.expandvars(path_str)
        return Path(path_str)

    def _check_symlink(self, path: Path) -> None:
        """检查符号链接安全性"""
        if not path.is_symlink():
            return

        # 解析符号链接目标
        try:
            target = path.resolve()
        except OSError:
            raise PermissionError("Cannot resolve symlink target")

        # 检查目标是否在允许目录内
        self._check_in_allowed_dir(target)

    def _check_in_allowed_dir(self, path: Path) -> None:
        """检查路径是否在允许的目录内"""
        all_dirs = [self.workspace] + self.extra_allowed_dirs

        for allowed_dir in all_dirs:
            if self._is_under(path, allowed_dir):
                return

        raise PermissionError(
            f"Path '{path}' is outside allowed directories. "
            f"Workspace: {self.workspace}"
        )

    @staticmethod
    def _is_under(path: Path, parent: Path) -> bool:
        """检查 path 是否在 parent 目录下"""
        try:
            path.relative_to(parent)
            return True
        except ValueError:
            return False
```

### 2. 文件系统工具集成

```python
# anyclaw/tools/filesystem.py

class ReadFileTool(Tool):
    def __init__(self, path_guard: PathGuard = None, **kwargs):
        self.path_guard = path_guard

    async def execute(self, path: str, **kwargs) -> str:
        # 路径验证
        if self.path_guard:
            try:
                safe_path = self.path_guard.resolve_and_validate(path)
            except PermissionError as e:
                return f"Error: {e}"
        else:
            safe_path = Path(path)

        # 正常读取...
```

### 3. 配置扩展

```json
// ~/.anyclaw/config.json
{
  "security": {
    "path": {
      "restrict_to_workspace": true,
      "extra_allowed_dirs": [
        "~/.config/anyclaw"
      ],
      "allow_symlinks_in_workspace": true
    }
  }
}
```

## 影响范围

- `anyclaw/security/path.py` - 路径守卫核心
- `anyclaw/tools/filesystem.py` - 集成路径验证
- `anyclaw/tools/shell.py` - Shell 命令路径参数验证
- `anyclaw/config/settings.py` - 添加 path 配置项
- `tests/test_path_guard.py` - 测试文件

## 验收标准

- [ ] 阻止 `../` 路径遍历
- [ ] 阻止绝对路径访问工作区外
- [ ] 阻止 `~` 家目录访问
- [ ] 阻止环境变量路径
- [ ] 阻止指向工作区外的符号链接
- [ ] 支持配置额外允许目录
- [ ] 所有文件工具集成路径验证
- [ ] 测试覆盖率 > 90%
