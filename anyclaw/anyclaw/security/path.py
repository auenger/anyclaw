"""路径安全防护模块

提供路径遍历防护、符号链接检查、允许目录范围验证等功能。

安全威胁防护：
- 路径遍历攻击：../../../etc/passwd
- 家目录访问：~/.ssh/id_rsa
- 环境变量路径：$HOME/.bashrc
- 符号链接绕过：link -> /etc/secrets
- 绝对路径访问工作区外：/etc/passwd
"""

import os
import re
from pathlib import Path
from typing import List, Optional, Union


class PathSecurityError(PermissionError):
    """路径安全错误"""

    def __init__(self, message: str, path: Optional[Path] = None):
        self.path = path
        super().__init__(message)


class PathGuard:
    """路径安全验证器

    验证所有文件操作路径都在允许的目录范围内，
    防止路径遍历攻击、符号链接绕过等安全威胁。

    Usage:
        guard = PathGuard(workspace="/home/user/project")
        safe_path = guard.resolve_and_validate("src/main.py")  # OK
        guard.resolve_and_validate("../../../etc/passwd")  # raises PermissionError
    """

    # 路径遍历模式
    _TRAVERSAL_PATTERNS = [
        r'\.\./',           # ../
        r'\.\.\\',          # ..\
        r'/\.\.',           # /..
        r'\\\.\.',          # \..
    ]

    # URL 编码的路径遍历模式
    _ENCODED_TRAVERSAL_PATTERNS = [
        r'%2e%2e%2f',       # URL 编码 ../
        r'%2e%2e/',         # 部分 URL 编码
        r'\.\.%2f',         # 部分 URL 编码
        r'%2e%2e%5c',       # URL 编码 ..\
        r'%252e',           # 双重编码
        r'%c0%ae',          # UTF-8 overlong encoding
        r'%c1%9c',          # UTF-8 overlong encoding
    ]

    # 危险协议前缀（防止 file:// 等协议绕过）
    _DANGEROUS_PROTOCOLS = ['file://', 'ftp://', 'sftp://']

    def __init__(
        self,
        workspace: Union[Path, str],
        extra_allowed_dirs: Optional[List[Union[Path, str]]] = None,
        allow_symlinks_in_workspace: bool = True,
        restrict_to_workspace: bool = True,
    ):
        """初始化路径守卫

        Args:
            workspace: 主工作区目录
            extra_allowed_dirs: 额外允许的目录列表
            allow_symlinks_in_workspace: 是否允许工作区内的符号链接
            restrict_to_workspace: 是否限制在工作区内
        """
        self.workspace = Path(workspace).expanduser().resolve()
        self.extra_allowed_dirs = [
            Path(d).expanduser().resolve() for d in (extra_allowed_dirs or [])
        ]
        self.allow_symlinks_in_workspace = allow_symlinks_in_workspace
        self.restrict_to_workspace = restrict_to_workspace

        # 缓存允许的目录列表
        self._allowed_dirs = [self.workspace] + self.extra_allowed_dirs

    def resolve_and_validate(
        self,
        path: Union[str, Path],
        for_write: bool = False,
    ) -> Path:
        """解析并验证路径

        执行完整的安全检查流程：
        1. 基础路径检查（遍历、协议、编码绕过）
        2. 路径展开（环境变量、用户目录）
        3. 解析为绝对路径
        4. 符号链接检查
        5. 目录范围检查

        Args:
            path: 要验证的路径
            for_write: 是否用于写入操作（目前未使用，保留扩展）

        Returns:
            解析后的绝对路径

        Raises:
            PathSecurityError: 路径不合法
        """
        path_str = str(path)

        # 1. 检查危险协议
        self._check_dangerous_protocols(path_str)

        # 2. 检查路径遍历（原始字符串）
        self._check_traversal(path_str)

        # 3. 检查 URL 编码绕过
        self._check_encoded_traversal(path_str)

        # 4. 检查空字节注入
        self._check_null_byte(path_str)

        # 5. 展开路径（环境变量、用户目录）
        expanded_path = self._expand_path(path_str)

        # 6. 构建完整路径
        p = Path(expanded_path)
        if not p.is_absolute():
            p = self.workspace / p

        # 7. 符号链接检查（在 resolve 之前，使用原始路径）
        self._check_symlink_chain(p)

        # 8. 解析为绝对路径
        try:
            resolved = p.resolve(strict=False)
        except OSError as e:
            raise PathSecurityError(f"Invalid path: {e}", p)

        # 9. 范围检查
        if self.restrict_to_workspace:
            self._check_in_allowed_dir(resolved)

        return resolved

    def _check_dangerous_protocols(self, path: str) -> None:
        """检查危险协议前缀"""
        lower_path = path.lower().strip()
        for proto in self._DANGEROUS_PROTOCOLS:
            if lower_path.startswith(proto):
                raise PathSecurityError(
                    f"Dangerous protocol detected: {proto}"
                )

    def _check_traversal(self, path: str) -> None:
        r"""检查路径遍历攻击

        检查明显的遍历模式，包括：
        - ../ 和 ..\
        - /.. 和 \..
        """
        for pattern in self._TRAVERSAL_PATTERNS:
            if re.search(pattern, path, re.IGNORECASE):
                raise PathSecurityError(
                    "Path traversal detected: path contains '..'"
                )

        # 额外检查：纯 ".." 路径
        if path.strip() == ".." or path.strip() == "../":
            raise PathSecurityError(
                "Path traversal detected: path is '..'"
            )

    def _check_encoded_traversal(self, path: str) -> None:
        """检查 URL 编码和 Unicode 编码绕过"""
        lower_path = path.lower()

        for pattern in self._ENCODED_TRAVERSAL_PATTERNS:
            if pattern in lower_path:
                raise PathSecurityError(
                    "Path traversal detected: encoded traversal pattern"
                )

        # 检查 Unicode 绕过（如 \u002e\u002e\u002f）
        try:
            # 尝试解码可能的 Unicode 转义
            if '\\u' in path or '\\x' in path:
                decoded = path.encode().decode('unicode_escape')
                if '..' in decoded:
                    raise PathSecurityError(
                        "Path traversal detected: Unicode encoded traversal"
                    )
        except (UnicodeDecodeError, UnicodeEncodeError):
            pass

    def _check_null_byte(self, path: str) -> None:
        """检查空字节注入"""
        if '\x00' in path or '%00' in path.lower():
            raise PathSecurityError(
                "Null byte injection detected"
            )

    def _expand_path(self, path: str) -> str:
        """展开环境变量和用户目录

        注意：展开后的路径仍需要通过范围检查
        """
        # 展开用户目录 ~/
        expanded = os.path.expanduser(path)

        # 展开环境变量（如 $HOME, ${HOME}）
        expanded = os.path.expandvars(expanded)

        return expanded

    def _check_symlink(self, path: Path) -> None:
        """检查符号链接安全性

        如果 allow_symlinks_in_workspace 为 False，阻止所有符号链接
        否则，只阻止指向允许目录外的符号链接
        """
        if not path.is_symlink():
            return

        # 如果完全禁止符号链接
        if not self.allow_symlinks_in_workspace:
            raise PathSecurityError(
                f"Symlinks are not allowed: {path}"
            )

        # 解析符号链接目标
        try:
            target = path.resolve()
        except OSError:
            raise PathSecurityError(
                f"Cannot resolve symlink target: {path}"
            )

        # 检查目标是否在允许目录内
        if self.restrict_to_workspace:
            self._check_in_allowed_dir(target, context="Symlink target")

    def _check_symlink_chain(self, path: Path) -> None:
        """检查路径中的符号链接链

        递归检查路径中的每个组件是否是符号链接，
        并验证每个符号链接的安全性。
        """
        # 如果完全禁止符号链接，检查路径中的任何符号链接
        if not self.allow_symlinks_in_workspace:
            # 检查路径中的每个组件
            current = path
            while current != current.parent:  # 还没到达根目录
                if current.exists() and current.is_symlink():
                    raise PathSecurityError(
                        f"Symlinks are not allowed: {current}"
                    )
                current = current.parent

            # 也检查路径本身
            if path.exists() and path.is_symlink():
                raise PathSecurityError(
                    f"Symlinks are not allowed: {path}"
                )
            return

        # 如果允许符号链接，检查目标是否在允许目录内
        if path.exists() and path.is_symlink():
            try:
                target = path.resolve()
                if self.restrict_to_workspace:
                    self._check_in_allowed_dir(target, context="Symlink target")
            except OSError:
                raise PathSecurityError(
                    f"Cannot resolve symlink target: {path}"
                )

    def _check_in_allowed_dir(
        self,
        path: Path,
        context: str = "Path"
    ) -> None:
        """检查路径是否在允许的目录内

        Args:
            path: 要检查的路径
            context: 错误消息上下文

        Raises:
            PathSecurityError: 路径在允许目录外
        """
        for allowed_dir in self._allowed_dirs:
            if self._is_under(path, allowed_dir):
                return

        # 构建友好的错误消息
        allowed_dirs_str = ", ".join(str(d) for d in self._allowed_dirs)
        raise PathSecurityError(
            f"{context} '{path}' is outside allowed directories.\n"
            f"Workspace: {self.workspace}\n"
            f"Allowed directories: {allowed_dirs_str}"
        )

    @staticmethod
    def _is_under(path: Path, parent: Path) -> bool:
        """检查 path 是否在 parent 目录下

        使用 relative_to 方法进行可靠的路径比较
        """
        try:
            path.relative_to(parent)
            return True
        except ValueError:
            return False

    def is_safe_path(self, path: Union[str, Path]) -> bool:
        """检查路径是否安全（不抛出异常）

        Args:
            path: 要检查的路径

        Returns:
            路径是否安全
        """
        try:
            self.resolve_and_validate(path)
            return True
        except PathSecurityError:
            return False

    def add_allowed_dir(self, directory: Union[Path, str]) -> None:
        """动态添加允许的目录

        Args:
            directory: 要添加的目录路径
        """
        dir_path = Path(directory).expanduser().resolve()
        if dir_path not in self.extra_allowed_dirs:
            self.extra_allowed_dirs.append(dir_path)
            self._allowed_dirs = [self.workspace] + self.extra_allowed_dirs

    def __repr__(self) -> str:
        return (
            f"PathGuard(workspace={self.workspace}, "
            f"extra_dirs={self.extra_allowed_dirs}, "
            f"allow_symlinks={self.allow_symlinks_in_workspace}, "
            f"restrict={self.restrict_to_workspace})"
        )


def create_path_guard_from_settings(
    workspace: Optional[Union[Path, str]] = None,
) -> PathGuard:
    """从配置创建 PathGuard 实例

    Args:
        workspace: 工作区路径（可选，默认从配置读取）

    Returns:
        配置好的 PathGuard 实例
    """
    from anyclaw.config.settings import settings

    ws = Path(workspace) if workspace else Path(settings.workspace).expanduser()

    # 检查是否开放所有权限
    allow_all = getattr(settings, 'allow_all_access', False)

    # 如果开放所有权限，直接返回不限制的 PathGuard
    if allow_all:
        return PathGuard(
            workspace=ws,
            extra_allowed_dirs=[],  # 不需要，因为 restrict_to_workspace=False
            allow_symlinks_in_workspace=True,
            restrict_to_workspace=False,
        )

    # 读取额外允许目录
    extra_dirs = getattr(settings, 'path_extra_allowed_dirs', [])
    if isinstance(extra_dirs, str):
        extra_dirs = [extra_dirs]

    # 展开额外目录中的 ~ 和环境变量
    expanded_dirs = []
    for d in extra_dirs:
        expanded = os.path.expandvars(os.path.expanduser(d))
        if expanded:
            expanded_dirs.append(expanded)

    return PathGuard(
        workspace=ws,
        extra_allowed_dirs=expanded_dirs,
        allow_symlinks_in_workspace=getattr(settings, 'path_allow_symlinks_in_workspace', True),
        restrict_to_workspace=settings.restrict_to_workspace,
    )
