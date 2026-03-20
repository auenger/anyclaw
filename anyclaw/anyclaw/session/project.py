"""Project identification utilities

提供项目识别功能：
- Git root 识别
- 项目标识符生成
- 安全目录名转换
"""

import logging
import re
import subprocess
from pathlib import Path
from typing import Optional


logger = logging.getLogger(__name__)


def find_git_root(path: Path) -> Optional[Path]:
    """查找 Git 仓库根目录

    从给定路径向上查找 .git 目录，返回仓库根目录。

    Args:
        path: 起始路径

    Returns:
        Git 仓库根目录，如果不是 Git 仓库则返回 None
    """
    try:
        result = subprocess.run(
            ["git", "rev-parse", "--show-toplevel"],
            cwd=str(path),
            capture_output=True,
            text=True,
            timeout=5,
        )
        if result.returncode == 0:
            return Path(result.stdout.strip())
    except (subprocess.TimeoutExpired, FileNotFoundError, OSError) as e:
        logger.debug(f"Failed to find git root: {e}")

    return None


def get_git_branch(path: Path) -> Optional[str]:
    """获取当前 Git 分支

    Args:
        path: 仓库路径

    Returns:
        当前分支名，如果不是 Git 仓库则返回 None
    """
    try:
        result = subprocess.run(
            ["git", "rev-parse", "--abbrev-ref", "HEAD"],
            cwd=str(path),
            capture_output=True,
            text=True,
            timeout=5,
        )
        if result.returncode == 0:
            branch = result.stdout.strip()
            # 检查是否处于 detached HEAD 状态
            if branch != "HEAD":
                return branch
    except (subprocess.TimeoutExpired, FileNotFoundError, OSError) as e:
        logger.debug(f"Failed to get git branch: {e}")

    return None


def get_git_remote_url(path: Path) -> Optional[str]:
    """获取 Git 远程仓库 URL

    Args:
        path: 仓库路径

    Returns:
        远程仓库 URL，如果没有则返回 None
    """
    try:
        result = subprocess.run(
            ["git", "remote", "get-url", "origin"],
            cwd=str(path),
            capture_output=True,
            text=True,
            timeout=5,
        )
        if result.returncode == 0:
            return result.stdout.strip()
    except (subprocess.TimeoutExpired, FileNotFoundError, OSError) as e:
        logger.debug(f"Failed to get git remote URL: {e}")

    return None


def make_safe_dirname(path: str) -> str:
    """生成安全的目录名

    将路径转换为可用于目录名的安全字符串：
    - 替换路径分隔符为连字符
    - 移除前导连字符
    - 移除或替换特殊字符

    Args:
        path: 原始路径字符串

    Returns:
        安全的目录名
    """
    # 替换路径分隔符
    safe = path.replace("/", "-").replace("\\", "-")

    # 移除前导连字符
    safe = safe.lstrip("-")

    # 替换其他不安全字符（保留字母、数字、连字符、下划线、点）
    safe = re.sub(r"[^a-zA-Z0-9\-_.]", "_", safe)

    # 压缩连续的连字符和下划线
    safe = re.sub(r"[-_]{2,}", "_", safe)

    # 限制长度（避免路径过长）
    if len(safe) > 100:
        safe = safe[:100]

    return safe or "unknown"


def get_project_identifier(cwd: Path, use_git_root: bool = True) -> str:
    """获取项目标识符

    根据 cwd 确定项目标识符：
    - 如果是 Git 仓库且 use_git_root=True，使用 Git root
    - 否则使用 cwd

    Args:
        cwd: 当前工作目录
        use_git_root: 是否使用 Git root 作为项目标识

    Returns:
        项目标识符（安全目录名格式）
    """
    if use_git_root:
        git_root = find_git_root(cwd)
        if git_root:
            return make_safe_dirname(str(git_root.resolve()))

    return make_safe_dirname(str(cwd.resolve()))


def get_channel_identifier(channel: str, channel_id: str) -> str:
    """获取 Channel 标识符

    生成 Channel 会话的标识符。

    Args:
        channel: 渠道类型（cli/feishu/discord）
        channel_id: 渠道 ID

    Returns:
        Channel 标识符
    """
    return f"{channel}_{channel_id}"


@staticmethod
def get_project_info(cwd: Path) -> dict:
    """获取项目信息

    收集项目的元信息，用于 project.json。

    Args:
        cwd: 当前工作目录

    Returns:
        项目信息字典
    """
    git_root = find_git_root(cwd)
    git_branch = get_git_branch(cwd) if git_root else None
    git_url = get_git_remote_url(cwd) if git_root else None

    return {
        "path": str(cwd.resolve()),
        "git_root": str(git_root.resolve()) if git_root else None,
        "git_branch": git_branch,
        "git_url": git_url,
        "project_id": get_project_identifier(cwd),
    }
