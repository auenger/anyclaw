"""CLI 频道"""
from typing import Callable
from rich.console import Console
from rich.prompt import Prompt
from anyclaw.config.settings import settings


class CLIChannel:
    """CLI 频道"""

    def __init__(self):
        self.console = Console()
        self.running = False

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
        """运行 CLI 循环"""
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
