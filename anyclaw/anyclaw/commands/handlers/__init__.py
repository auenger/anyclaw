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

__all__ = [
    "NewCommandHandler",
    "ResetCommandHandler",
    "ClearCommandHandler",
    "StopCommandHandler",
    "HelpCommandHandler",
    "StatusCommandHandler",
    "VersionCommandHandler",
]


def register_builtin_commands(dispatcher) -> None:
    """Register all built-in commands with the dispatcher.

    Args:
        dispatcher: CommandDispatcher instance.
    """
    from anyclaw.commands import CommandDispatcher

    # Session commands
    dispatcher.register("new", NewCommandHandler())
    dispatcher.register("reset", ResetCommandHandler())
    dispatcher.register("clear", ClearCommandHandler())

    # Task commands
    dispatcher.register("stop", StopCommandHandler(), aliases=["abort"])

    # Info commands
    dispatcher.register("help", HelpCommandHandler(), aliases=["?"], description="显示帮助信息")
    dispatcher.register("status", StatusCommandHandler(), description="显示会话状态")
    dispatcher.register("version", VersionCommandHandler(), description="显示版本号")
