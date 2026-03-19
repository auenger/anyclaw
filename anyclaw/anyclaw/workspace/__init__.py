"""Workspace 工作区管理模块"""

from anyclaw.workspace.manager import WorkspaceManager
from anyclaw.workspace.bootstrap import BootstrapLoader
from anyclaw.workspace.templates import (
    sync_workspace_templates,
    BOOTSTRAP_TEMPLATE,
    GITIGNORE_TEMPLATE,
    SOUL_TEMPLATE,
    USER_TEMPLATE,
    IDENTITY_TEMPLATE,
    TOOLS_TEMPLATE,
)

__all__ = [
    "WorkspaceManager",
    "BootstrapLoader",
    "sync_workspace_templates",
    "BOOTSTRAP_TEMPLATE",
    "GITIGNORE_TEMPLATE",
    "SOUL_TEMPLATE",
    "USER_TEMPLATE",
    "IDENTITY_TEMPLATE",
    "TOOLS_TEMPLATE",
]
