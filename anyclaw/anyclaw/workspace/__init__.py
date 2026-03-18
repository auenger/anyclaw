"""Workspace 工作区管理模块"""

from anyclaw.workspace.manager import WorkspaceManager
from anyclaw.workspace.bootstrap import BootstrapLoader
from anyclaw.workspace.templates import BOOTSTRAP_TEMPLATE, GITIGNORE_TEMPLATE

__all__ = [
    "WorkspaceManager",
    "BootstrapLoader",
    "BOOTSTRAP_TEMPLATE",
    "GITIGNORE_TEMPLATE",
]
