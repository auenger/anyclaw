"""CLI Channel implementation with streaming support."""

from __future__ import annotations

import asyncio
from typing import Any, AsyncGenerator, Callable

from rich.console import Console
from rich.prompt import Prompt
from rich.live import Live
from rich.text import Text

from anyclaw.bus.events import OutboundMessage
from anyclaw.bus.queue import MessageBus
from anyclaw.channels.base import BaseChannel


class CLIConfig:
    """CLI channel configuration."""

    def __init__(self, config: dict[str, Any] | None = None):
        config = config or {}
        self.enabled: bool = config.get("enabled", True)
        self.allow_from: list[str] = config.get("allow_from", ["*"])
        self.prompt: str = config.get("prompt", "You: ")
        self.agent_name: str = config.get("agent_name", "AnyClaw")


class CLIChannel(BaseChannel):
    """CLI channel with streaming output support."""

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

    @classmethod
    def default_config(cls) -> dict[str, Any]:
        return {"enabled": True, "allow_from": ["*"]}

    def set_response_callback(
        self, callback: Callable[[str], AsyncGenerator[str, None]]
    ) -> None:
        """Set callback to generate streaming responses."""
        self._response_callback = callback

    async def start(self) -> None:
        """Start the CLI channel loop."""
        self._running = True
        self._print_welcome()

        while self._running:
            try:
                user_input = self._get_input()

                # Handle special commands
                if user_input.lower() in ["exit", "quit"]:
                    self.console.print("[yellow]Goodbye![/yellow]")
                    break

                if user_input.lower() == "clear":
                    self.console.print("[yellow]Conversation cleared.[/yellow]")
                    continue

                if not user_input.strip():
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

    def _print_welcome(self) -> None:
        """Print welcome message."""
        self.console.print(f"\n[bold blue]Welcome to {self.config.agent_name}![/bold blue]")
        self.console.print("[dim]Type 'exit' or 'quit' to exit[/dim]")
        self.console.print("[dim]Type 'clear' to clear conversation history[/dim]\n")

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
