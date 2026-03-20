"""CLI Channel implementation with streaming support."""

from __future__ import annotations

import asyncio
import os
from typing import TYPE_CHECKING, Any, AsyncGenerator, Callable, Optional

from rich.console import Console
from rich.prompt import Prompt
from rich.live import Live
from rich.text import Text

from anyclaw.bus.events import InboundMessage, OutboundMessage
from anyclaw.bus.queue import MessageBus
from anyclaw.channels.base import BaseChannel, AuthorizationRequiredError
from anyclaw.commands import CommandDispatcher, CommandContext
from anyclaw.commands.handlers import register_builtin_commands

if TYPE_CHECKING:
    from anyclaw.commands.dispatcher import CommandResult


class CLIConfig:
    """CLI channel configuration."""

    def __init__(self, config: dict[str, Any] | None = None):
        config = config or {}
        self.enabled: bool = config.get("enabled", True)
        self.allow_from: list[str] = config.get("allow_from", ["*"])
        self.prompt: str = config.get("prompt", "You: ")
        self.agent_name: str = config.get("agent_name", "AnyClaw")
        # In serve mode, CLI is monitor-only (no interactive input)
        self.interactive: bool = config.get("interactive", True)


class CLIChannel(BaseChannel):
    """CLI channel with streaming output support.

    Features:
    - Streaming output for LLM responses
    - Special command support (/help, /new, /reset, /stop, /clear, etc.)
    - Interrupt handling with Ctrl+C
    """

    name = "cli"
    display_name = "CLI"

    def __init__(self, config: Any, bus: MessageBus):
        if isinstance(config, dict):
            config = CLIConfig(config)
        super().__init__(config, bus)
        self.config: CLIConfig = config
        self.console = Console()
        self._stream_interrupted = False
        self._response_callback: Callable[[str], AsyncGenerator[str, None]] | None = None

        # Initialize command dispatcher
        self._command_dispatcher: Optional[CommandDispatcher] = None
        self._setup_command_dispatcher()

    def _setup_command_dispatcher(self) -> None:
        """Set up command dispatcher with builtin commands."""
        self._command_dispatcher = CommandDispatcher()
        register_builtin_commands(self._command_dispatcher)

    @classmethod
    def default_config(cls) -> dict[str, Any]:
        return {"enabled": True, "allow_from": ["*"], "interactive": True}

    def set_response_callback(
        self, callback: Callable[[str], AsyncGenerator[str, None]]
    ) -> None:
        """Set callback to generate streaming responses."""
        self._response_callback = callback

    async def start(self) -> None:
        """Start the CLI channel loop."""
        self._running = True

        # In non-interactive mode (serve mode), just wait forever
        # Messages will be displayed via send() method
        if not self.config.interactive:
            self.console.print("[dim]CLI channel in monitor mode (no interactive input)[/dim]")
            while self._running:
                await asyncio.sleep(1)
            return

        # Interactive mode
        self._print_welcome()

        while self._running:
            try:
                user_input = self._get_input()

                # Handle exit commands
                if user_input.lower() in ["exit", "quit"]:
                    self.console.print("[yellow]Goodbye![/yellow]")
                    break

                # Handle empty input
                if not user_input.strip():
                    continue

                # Check for special commands
                if self._command_dispatcher and self._command_dispatcher.is_command(user_input):
                    result = await self._handle_command(user_input)
                    if result.handled:
                        if result.reply:
                            self.console.print(f"\n{result.reply}\n")
                        continue

                # Forward to bus via _handle_message
                await self._handle_message(
                    sender_id="user",
                    chat_id="default",
                    content=user_input,
                )

            except KeyboardInterrupt:
                self.console.print("\n[yellow]Interrupted. Goodbye![/yellow]")
                break
            except Exception as e:
                self.console.print(f"[red]Error: {e}[/red]")

    async def stop(self) -> None:
        """Stop the CLI channel."""
        self._running = False

    async def send(self, msg: OutboundMessage) -> None:
        """Send a message to the CLI (print to console)."""
        content = msg.content
        if not content:
            return

        # Print with agent name prefix
        self.console.print(f"\n[bold green]{self.config.agent_name}:[/bold green] {content}\n")

    async def request_authorization(
        self,
        error: AuthorizationRequiredError,
        chat_id: Optional[str] = None,
        timeout: float = 60.0,
    ) -> Optional[str]:
        """请求用户授权访问目录（CLI 交互式实现）

        显示交互式菜单让用户选择授权方式。

        Args:
            error: 授权异常
            chat_id: 聊天 ID（CLI 忽略）
            timeout: 超时时间（秒）

        Returns:
            授权决策: "session" / "persist" / "deny" / None
        """
        self.console.print()
        self.console.print(f"[yellow]🔐 需要授权[/]")
        self.console.print(f"   路径: [blue]{error.suggested_dir}[/]")
        self.console.print()

        try:
            choice = Prompt.ask(
                "选择授权方式",
                choices=["y", "p", "n"],
                default="y",
                console=self.console,
            )

            return {
                "y": "session",
                "p": "persist",
                "n": "deny",
            }.get(choice.lower())

        except (KeyboardInterrupt, EOFError):
            self.console.print("\n[dim]授权已取消[/]")
            return "deny"

    def _print_welcome(self) -> None:
        """Print welcome message."""
        self.console.print(f"\n[bold blue]Welcome to {self.config.agent_name}![/bold blue]")
        self.console.print("[dim]Type 'exit' or 'quit' to exit[/dim]")
        self.console.print("[dim]Type '/help' to see available commands[/dim]\n")

    async def _handle_command(self, user_input: str) -> "CommandResult":
        """Handle a special command.

        Args:
            user_input: User input string.

        Returns:
            CommandResult from the command handler.
        """
        from anyclaw.commands import CommandContext

        # Build command context
        context = CommandContext(
            user_id="user",
            chat_id="default",
            channel=self,
            channel_type="cli",
            session_key=self._current_session_key,
            config=self._config,
        )

        # Dispatch command
        result = await self._command_dispatcher.dispatch(user_input, context)

        # Handle special commands that need channel interaction
        if result.handled and result.reply:
            # Check for /clear command - actually clear the screen
            if user_input.lower().startswith("/clear"):
                os.system("clear" if os.name == "posix" else "cls")
                return result

        return result

    def _get_input(self) -> str:
        """Get user input."""
        return Prompt.ask(self.config.prompt, console=self.console)

    # ========== Streaming Support (for direct use without bus) ==========

    async def run_stream(
        self,
        stream_func: Callable[[str], AsyncGenerator[str, None]]
    ) -> None:
        """Run CLI with streaming output (bypasses bus)."""
        self._response_callback = stream_func
        self._print_welcome()
        self._running = True

        while self._running:
            try:
                user_input = self._get_input()

                if user_input.lower() in ["exit", "quit"]:
                    self.console.print("[yellow]Goodbye![/yellow]")
                    break

                if user_input.lower() == "clear":
                    self.console.print("[yellow]Conversation cleared.[/yellow]")
                    continue

                if not user_input.strip():
                    continue

                # Stream the response
                await self._print_stream(stream_func(user_input))

            except KeyboardInterrupt:
                self.console.print("\n[yellow]Interrupted.[/yellow]")
                self._stream_interrupted = True
            except Exception as e:
                self.console.print(f"[red]Error: {e}[/red]")

    async def _print_stream(self, stream_gen: AsyncGenerator[str, None]) -> None:
        """Print streaming response."""
        self._stream_interrupted = False

        # Print agent name prefix
        self.console.print(f"\n[bold green]{self.config.agent_name}:[/bold green] ", end="")

        try:
            async for chunk in stream_gen:
                if self._stream_interrupted:
                    break
                self.console.print(chunk, end="", highlight=False)

        except asyncio.CancelledError:
            self.console.print("\n[dim][interrupted][/dim]")
        except Exception as e:
            self.console.print(f"\n[red][Error: {e}][/red]")

        # New line after completion
        self.console.print()

    def interrupt_stream(self) -> None:
        """Interrupt current streaming output."""
        self._stream_interrupted = True
