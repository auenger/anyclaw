"""CLI 频道"""
import asyncio
from typing import Callable, AsyncGenerator
from rich.console import Console
from rich.prompt import Prompt
from rich.live import Live
from rich.text import Text
from anyclaw.config.settings import settings


class CLIChannel:
    """CLI 频道"""

    def __init__(self):
        self.console = Console()
        self.running = False
        self._stream_interrupted = False

    def print_welcome(self):
        """打印欢迎信息"""
        self.console.print(f"\n[bold blue]Welcome to {settings.agent_name}![/bold blue]")
        self.console.print("[dim]Type 'exit' or 'quit' to exit[/dim]")
        self.console.print("[dim]Type 'clear' to clear conversation history[/dim]\n")

    def print_response(self, response: str):
        """打印响应"""
        self.console.print(f"\n[bold green]{settings.agent_name}:[/bold green] {response}\n")

    def get_input(self) -> str:
        """获取用户输入"""
        return Prompt.ask(settings.cli_prompt, console=self.console)

    async def run(self, process_func: Callable[[str], str]):
        """运行 CLI 循环（非流式）"""
        self.print_welcome()
        self.running = True

        while self.running:
            try:
                user_input = self.get_input()

                # 处理特殊命令
                if user_input.lower() in ['exit', 'quit']:
                    self.console.print("[yellow]Goodbye![/yellow]")
                    break

                if user_input.lower() == 'clear':
                    self.console.print("[yellow]Conversation cleared.[/yellow]")
                    continue

                if not user_input.strip():
                    continue

                # 处理用户输入
                response = await process_func(user_input)
                self.print_response(response)

            except KeyboardInterrupt:
                self.console.print("\n[yellow]Interrupted. Goodbye![/yellow]")
                break
            except Exception as e:
                self.console.print(f"[red]Error: {e}[/red]")

    # ========== 流式输出支持 ==========

    async def run_stream(
        self,
        stream_func: Callable[[str], AsyncGenerator[str, None]]
    ):
        """运行 CLI 循环（流式模式）

        Args:
            stream_func: 返回 async generator 的函数，接收用户输入，生成响应块
        """
        self.print_welcome()
        self.running = True

        while self.running:
            try:
                user_input = self.get_input()

                # 处理特殊命令
                if user_input.lower() in ['exit', 'quit']:
                    self.console.print("[yellow]Goodbye![/yellow]")
                    break

                if user_input.lower() == 'clear':
                    self.console.print("[yellow]Conversation cleared.[/yellow]")
                    continue

                if not user_input.strip():
                    continue

                # 流式处理用户输入
                await self.print_stream(stream_func(user_input))

            except KeyboardInterrupt:
                self.console.print("\n[yellow]Interrupted.[/yellow]")
                self._stream_interrupted = True
            except Exception as e:
                self.console.print(f"[red]Error: {e}[/red]")

    async def print_stream(self, stream_gen: AsyncGenerator[str, None]):
        """打印流式响应

        Args:
            stream_gen: async generator，生成响应块
        """
        self._stream_interrupted = False

        # 打印 Agent 名称前缀
        self.console.print(f"\n[bold green]{settings.agent_name}:[/bold green] ", end="")

        try:
            async for chunk in stream_gen:
                if self._stream_interrupted:
                    break
                # 直接打印块（不换行）
                self.console.print(chunk, end="", highlight=False)

        except asyncio.CancelledError:
            self.console.print("\n[dim][interrupted][/dim]")
        except Exception as e:
            self.console.print(f"\n[red][Error: {e}][/red]")

        # 完成后换行
        self.console.print()

    async def print_stream_with_live(
        self,
        stream_gen: AsyncGenerator[str, None],
        show_cursor: bool = True
    ):
        """使用 Rich Live 打印流式响应（带光标效果）

        Args:
            stream_gen: async generator，生成响应块
            show_cursor: 是否显示打字光标
        """
        self._stream_interrupted = False
        text = Text()

        try:
            with Live(text, console=self.console, refresh_per_second=20) as live:
                async for chunk in stream_gen:
                    if self._stream_interrupted:
                        break
                    text.append(chunk)
                    live.update(text)

        except asyncio.CancelledError:
            text.append("\n[dim][interrupted][/dim]")
        except Exception as e:
            text.append(f"\n[red][Error: {e}][/red]")

    def interrupt_stream(self):
        """中断当前流式输出"""
        self._stream_interrupted = True
