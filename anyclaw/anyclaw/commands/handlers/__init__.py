"""Built-in Command Handlers."""

from anyclaw.commands.handlers.session import (
    NewCommandHandler,
    ResetCommandHandler,
    ClearCommandHandler,
)
from anyclaw.commands.handlers.task import StopCommandHandler
from anyclaw.commands.handlers.info import (
    HelpCommandHandler,
    StatusCommandHandler,
    VersionCommandHandler,
)

# Advanced handlers (feat-special-commands-advanced)
from anyclaw.commands.handlers.compact import CompactCommandHandler
from anyclaw.commands.handlers.model import ModelCommandHandler
from anyclaw.commands.handlers.agent_cmd import AgentCommandHandler
from anyclaw.commands.handlers.session_cmd import SessionCommandHandler

__all__ = [
    # Core handlers
    "NewCommandHandler",
    "ResetCommandHandler",
    "ClearCommandHandler",
    "StopCommandHandler",
    "HelpCommandHandler",
    "StatusCommandHandler",
    "VersionCommandHandler",
    # Advanced handlers
    "CompactCommandHandler",
    "ModelCommandHandler",
    "AgentCommandHandler",
    "SessionCommandHandler",
]


def register_builtin_commands(dispatcher) -> None:
    """Register all built-in commands with the dispatcher.

    Args:
        dispatcher: CommandDispatcher instance.
    """
    from anyclaw.commands import CommandDispatcher

    # Session commands (core)
    dispatcher.register("new", NewCommandHandler())
    dispatcher.register("reset", ResetCommandHandler())
    dispatcher.register("clear", ClearCommandHandler())

    # Task commands (core)
    dispatcher.register("stop", StopCommandHandler(), aliases=["abort"])

    # Info commands (core)
    dispatcher.register("help", HelpCommandHandler(), aliases=["?"], description="显示帮助信息")
    dispatcher.register("status", StatusCommandHandler(), description="显示会话状态")
    dispatcher.register("version", VersionCommandHandler(), description="显示版本号")

    # Advanced commands (feat-special-commands-advanced)
    dispatcher.register("compact", CompactCommandHandler(), aliases=["compress"], description="压缩上下文")
    dispatcher.register("model", ModelCommandHandler(), aliases=["models"], description="查看/切换模型")
    dispatcher.register("agent", AgentCommandHandler(), aliases=["agents"], description="查看/切换 Agent")
    dispatcher.register("session", SessionCommandHandler(), aliases=["sess"], description="会话生命周期管理")


def register_advanced_commands(dispatcher) -> None:
    """Register only advanced commands (for incremental loading).

    Args:
        dispatcher: CommandDispatcher instance.
    """
    dispatcher.register("compact", CompactCommandHandler(), aliases=["compress"], description="压缩上下文")
    dispatcher.register("model", ModelCommandHandler(), aliases=["models"], description="查看/切换模型")
    dispatcher.register("agent", AgentCommandHandler(), aliases=["agents"], description="查看/切换 Agent")
    dispatcher.register("session", SessionCommandHandler(), aliases=["sess"], description="会话生命周期管理")
