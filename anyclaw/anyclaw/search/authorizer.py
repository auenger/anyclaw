"""动态路径授权器

管理会话级临时授权和持久化授权，支持跨渠道授权交互。
"""

import threading
from pathlib import Path
from typing import Optional, Set


class AuthorizationRequiredError(Exception):
    """需要授权异常 - 携带授权上下文

    当 PathGuard 检测到路径访问越界时抛出此异常，
    Channel 层应捕获此异常并请求用户授权。
    """

    def __init__(self, path: Path, suggested_dir: Path, message: Optional[str] = None):
        """初始化授权异常

        Args:
            path: 请求访问的路径
            suggested_dir: 建议授权的目录
            message: 自定义错误消息
        """
        self.path = path
        self.suggested_dir = suggested_dir
        self.message = message or f"需要授权访问: {suggested_dir}"
        super().__init__(self.message)


class PathAuthorizer:
    """动态路径授权器

    管理会话级临时授权和持久化授权。

    Usage:
        authorizer = PathAuthorizer()

        # 检查授权
        if not authorizer.is_authorized(path):
            raise AuthorizationRequiredError(path, suggested_dir)

        # 授权目录
        authorizer.authorize(suggested_dir, persist=True)
    """

    # 危险路径黑名单 - 永远不允许授权
    DANGEROUS_PATHS: Set[Path] = {
        Path.home() / ".ssh",
        Path.home() / ".gnupg",
        Path("/etc/passwd"),
        Path("/etc/shadow"),
        Path("/etc/sudoers"),
        Path("/root"),
    }

    # 危险目录名称（相对路径）
    DANGEROUS_DIR_NAMES = {
        ".ssh",
        ".gnupg",
        ".kube",
        ".aws",
        ".config/gh",  # GitHub CLI credentials
    }

    _instance: Optional["PathAuthorizer"] = None
    _instance_lock = threading.Lock()

    def __new__(cls, *args, **kwargs) -> "PathAuthorizer":
        """单例模式 - 确保全局共享授权状态"""
        if cls._instance is None:
            with cls._instance_lock:
                if cls._instance is None:
                    cls._instance = super().__new__(cls)
                    cls._instance._initialized = False
        return cls._instance

    def __init__(
        self,
        persistent_allowed_dirs: Optional[Set[Path]] = None,
    ):
        """初始化路径授权器

        Args:
            persistent_allowed_dirs: 持久化授权目录集合
        """
        # 避免重复初始化
        if getattr(self, "_initialized", False):
            return

        self._initialized = True
        self._lock = threading.Lock()

        # 会话级临时授权（内存中，重启失效）
        self._session_allowed_dirs: Set[Path] = set()

        # 持久化授权（从配置加载）
        self._persistent_allowed_dirs: Set[Path] = persistent_allowed_dirs or set()

        # 预解析危险路径（必须在 _preauthorize_common_dirs 之前）
        self._resolved_dangerous_paths: Set[Path] = set()
        for p in self.DANGEROUS_PATHS:
            try:
                self._resolved_dangerous_paths.add(p.resolve())
            except OSError:
                pass

        # 从配置加载权限设置
        self._load_from_config()

        # 预授权常用目录（非危险路径）
        self._preauthorize_common_dirs()

    def _load_from_config(self) -> None:
        """从配置加载权限设置"""
        try:
            from anyclaw.config.settings import settings

            # 1. 检查 allow_all_access（全开放模式）
            self._allow_all = getattr(settings, 'allow_all_access', False)

            # 2. 加载 extra_allowed_dirs
            extra_dirs = getattr(settings, 'path_extra_allowed_dirs', []) or []
            if isinstance(extra_dirs, str):
                extra_dirs = [extra_dirs]

            for dir_str in extra_dirs:
                try:
                    path = Path(dir_str).expanduser().resolve()
                    if not self.is_dangerous(path):
                        self._persistent_allowed_dirs.add(path)
                except OSError:
                    continue

            # 3. 加载搜索专用配置
            search_allow_all = getattr(settings, 'search_allow_all_paths', None)
            if search_allow_all is not None:
                self._allow_all = search_allow_all

            search_extra_dirs = getattr(settings, 'search_extra_allowed_dirs', [])
            if search_extra_dirs:
                for dir_str in search_extra_dirs:
                    try:
                        path = Path(dir_str).expanduser().resolve()
                        if not self.is_dangerous(path):
                            self._session_allowed_dirs.add(path)
                    except OSError:
                        continue

        except Exception:
            # 配置加载失败，使用默认值
            self._allow_all = False

    def _preauthorize_common_dirs(self) -> None:
        """预授权常用目录"""
        # 如果是全开放模式，不需要预授权
        if self._allow_all:
            return

        home = Path.home()
        common_dirs = [
            home / "Downloads",
            home / "Desktop",
            home / "Documents",
            home / "Projects",
            home / "projects",
            home / "mycode",
            home / "code",
            home / "workspace",
            home,  # 用户主目录
        ]

        for dir_path in common_dirs:
            if dir_path.exists() and not self.is_dangerous(dir_path):
                self._session_allowed_dirs.add(dir_path.resolve())

    def authorize(self, dir_path: Path, persist: bool = False) -> bool:
        """授权目录访问

        Args:
            dir_path: 要授权的目录
            persist: 是否持久化到配置

        Returns:
            是否授权成功
        """
        try:
            path = Path(dir_path).expanduser().resolve()
        except OSError:
            return False

        # 检查危险路径黑名单
        if self.is_dangerous(path):
            return False

        with self._lock:
            # 添加到会话授权
            self._session_allowed_dirs.add(path)

            # 持久化授权
            if persist:
                self._persistent_allowed_dirs.add(path)
                self._save_persistent_authorization(path)

        return True

    def is_authorized(self, path: Path) -> bool:
        """检查路径是否已授权

        Args:
            path: 要检查的路径

        Returns:
            是否已授权
        """
        try:
            resolved_path = Path(path).expanduser().resolve()
        except OSError:
            return False

        # 危险路径永远不允许
        if self.is_dangerous(resolved_path):
            return False

        # 全开放模式：允许所有非危险路径
        if self._allow_all:
            return True

        with self._lock:
            # 检查会话授权
            for allowed_dir in self._session_allowed_dirs | self._persistent_allowed_dirs:
                if self._is_under(resolved_path, allowed_dir):
                    return True

        return False

    def is_dangerous(self, path: Path) -> bool:
        """检查是否为危险路径

        Args:
            path: 要检查的路径

        Returns:
            是否为危险路径
        """
        try:
            resolved_path = Path(path).expanduser().resolve()
        except OSError:
            return True  # 无法解析的路径视为危险

        # 检查是否在危险路径下
        for dangerous_path in self._resolved_dangerous_paths:
            if resolved_path == dangerous_path or self._is_under(resolved_path, dangerous_path):
                return True

        # 检查危险目录名称
        for part in resolved_path.parts:
            if part in self.DANGEROUS_DIR_NAMES:
                return True

        return False

    def revoke_session_authorization(self, dir_path: Path) -> bool:
        """撤销会话级授权

        Args:
            dir_path: 要撤销的目录

        Returns:
            是否撤销成功
        """
        try:
            path = Path(dir_path).expanduser().resolve()
        except OSError:
            return False

        with self._lock:
            if path in self._session_allowed_dirs:
                self._session_allowed_dirs.discard(path)
                return True

        return False

    def get_session_authorizations(self) -> Set[Path]:
        """获取当前会话的所有授权目录

        Returns:
            授权目录集合
        """
        with self._lock:
            return self._session_allowed_dirs.copy()

    def get_persistent_authorizations(self) -> Set[Path]:
        """获取所有持久化授权目录

        Returns:
            持久化授权目录集合
        """
        with self._lock:
            return self._persistent_allowed_dirs.copy()

    def clear_session_authorizations(self) -> None:
        """清除所有会话级授权"""
        with self._lock:
            self._session_allowed_dirs.clear()

    @staticmethod
    def _is_under(path: Path, parent: Path) -> bool:
        """检查 path 是否在 parent 目录下

        Args:
            path: 要检查的路径
            parent: 父目录

        Returns:
            path 是否在 parent 下
        """
        try:
            path.relative_to(parent)
            return True
        except ValueError:
            return False

    def _save_persistent_authorization(self, path: Path) -> None:
        """保存持久化授权到配置文件

        Args:
            path: 要保存的授权路径
        """
        try:
            from anyclaw.config.settings import settings

            # 读取现有配置
            extra_dirs = list(getattr(settings, "path_extra_allowed_dirs", []) or [])

            # 添加新目录（避免重复）
            path_str = str(path)
            if path_str not in extra_dirs:
                extra_dirs.append(path_str)

            # 更新配置
            settings.path_extra_allowed_dirs = extra_dirs

            # 保存配置
            if hasattr(settings, "save"):
                settings.save()

        except Exception:
            # 保存失败，忽略（授权仍然在内存中有效）
            pass

    def load_from_config(self) -> None:
        """从配置文件加载持久化授权"""
        try:
            from anyclaw.config.settings import settings

            extra_dirs = getattr(settings, "path_extra_allowed_dirs", []) or []
            if isinstance(extra_dirs, str):
                extra_dirs = [extra_dirs]

            with self._lock:
                for dir_str in extra_dirs:
                    try:
                        path = Path(dir_str).expanduser().resolve()
                        self._persistent_allowed_dirs.add(path)
                    except OSError:
                        continue

        except Exception:
            pass


def get_authorizer() -> PathAuthorizer:
    """获取全局 PathAuthorizer 实例

    Returns:
        PathAuthorizer 单例实例
    """
    return PathAuthorizer()
