"""Model Command Handler - /model for viewing and switching LLM models."""

from __future__ import annotations

from typing import TYPE_CHECKING, Optional

from anyclaw.commands.base import CommandHandler, CommandResult
from anyclaw.commands.context import CommandContext

if TYPE_CHECKING:
    from anyclaw.config.settings import Settings


# Available models by provider
AVAILABLE_MODELS = {
    "openai": ["gpt-4o", "gpt-4o-mini", "gpt-4-turbo", "gpt-3.5-turbo", "gpt-3.5-turbo-16k"],
    "anthropic": ["claude-3-5-sonnet-20241022", "claude-3-5-haiku-20241022", "claude-3-opus-20240229"],
    "zai": ["glm-4.7", "glm-4-plus", "glm-4-flash", "glm-4-air", "glm-4-long"],
    "deepseek": ["deepseek-chat", "deepseek-coder"],
    "openrouter": ["anthropic/claude-3.5-sonnet", "openai/gpt-4o", "google/gemini-pro-1.5"],
    "ollama": ["llama3.1", "llama3.2", "qwen2.5", "mistral", "codellama"],
}


class ModelCommandHandler(CommandHandler):
    """Handle /model command - view and switch LLM models.

    Usage:
        /model              - Show current model and available models
        /model <name>       - Switch to specified model
    """

    @property
    def description(self) -> str:
        return "查看/切换模型"

    @property
    def aliases(self) -> list[str]:
        return ["models"]

    async def execute(
        self,
        args: Optional[str],
        context: CommandContext,
    ) -> CommandResult:
        """Execute /model command.

        Args:
            args: Optional model name to switch to.
            context: Execution context.

        Returns:
            CommandResult with model info or switch result.
        """
        config: Settings | None = context.config

        if config is None:
            return CommandResult.fail("配置不可用")

        # Get current model and provider
        current_model = getattr(config.llm, "model", "unknown") if hasattr(config, "llm") else "unknown"
        current_provider = getattr(config.llm, "provider", "unknown") if hasattr(config, "llm") else "unknown"

        # No args - show current model and available models
        if not args or not args.strip():
            return self._show_models(current_model, current_provider)

        # Switch model
        new_model = args.strip()
        return await self._switch_model(new_model, current_model, current_provider, config)

    def _show_models(self, current: str, provider: str) -> CommandResult:
        """Show current model and available models.

        Args:
            current: Current model name.
            provider: Current provider name.

        Returns:
            CommandResult with model list.
        """
        lines = [
            "🤖 **模型信息**",
            "",
            f"**当前模型**: {current}",
            f"**Provider**: {provider}",
            "",
            "**可用模型**:",
        ]

        # Show models for current provider
        if provider in AVAILABLE_MODELS:
            lines.append(f"\n[{provider}]")
            for model in AVAILABLE_MODELS[provider]:
                marker = " ✅" if model == current else ""
                lines.append(f"  {model}{marker}")

        # Show other providers (abbreviated)
        lines.append("\n**其他 Provider 模型**:")
        for prov, models in AVAILABLE_MODELS.items():
            if prov != provider:
                lines.append(f"  [{prov}] {', '.join(models[:3])}...")

        lines.append("\n💡 使用 `/model <名称>` 切换模型")

        return CommandResult.success("\n".join(lines))

    async def _switch_model(
        self,
        new_model: str,
        current: str,
        provider: str,
        config: Settings,
    ) -> CommandResult:
        """Switch to a new model.

        Args:
            new_model: Model name to switch to.
            current: Current model name.
            provider: Current provider name.
            config: Application settings.

        Returns:
            CommandResult with switch result.
        """
        # Check if already using this model
        if new_model == current:
            return CommandResult.success(f"💡 已经在使用模型 {new_model}")

        # Validate model exists
        all_models = []
        for models in AVAILABLE_MODELS.values():
            all_models.extend(models)

        if new_model not in all_models:
            return CommandResult.success(
                f"❌ 未知模型: {new_model}\n"
                f"当前 Provider [{provider}] 支持的模型: {', '.join(AVAILABLE_MODELS.get(provider, []))}"
            )

        try:
            # Update config
            if hasattr(config, "llm") and hasattr(config.llm, "model"):
                # Try to set the model
                if hasattr(config, "set_value"):
                    config.set_value("llm.model", new_model)
                else:
                    # Direct attribute set as fallback
                    config.llm.model = new_model

            return CommandResult.success(
                f"✅ 模型已切换\n"
                f"   {current} → {new_model}"
            )

        except Exception as e:
            return CommandResult.fail(f"切换模型失败: {e}")
