"""Config API endpoints."""

from __future__ import annotations

from typing import Any

from fastapi import APIRouter
from pydantic import BaseModel

from anyclaw.api.deps import get_serve_manager

router = APIRouter()


class LLMSettingsModel(BaseModel):
    """LLM settings model."""

    model: str = "gpt-4o"
    temperature: float = 0.7
    max_tokens: int = 4096
    stream: bool = True


class ProviderSettingsModel(BaseModel):
    """Provider settings model."""

    name: str
    api_key: str | None = None
    base_url: str | None = None


class SettingsResponse(BaseModel):
    """Settings response model."""

    llm: LLMSettingsModel = LLMSettingsModel()
    providers: dict[str, ProviderSettingsModel] = {}


@router.get("/config", response_model=SettingsResponse)
async def get_config() -> SettingsResponse:
    """Get current configuration.

    Returns:
        SettingsResponse with LLM and provider settings
    """
    manager = get_serve_manager()
    config = manager.config

    # Build LLM settings
    llm = LLMSettingsModel(
        model=config.llm.model,
        temperature=config.llm.temperature,
        max_tokens=config.llm.max_tokens,
        stream=config.llm.stream,
    )

    # Build provider settings (without sensitive data)
    providers: dict[str, ProviderSettingsModel] = {}
    if hasattr(config, "providers") and config.providers:
        for name, provider in config.providers.items():
            providers[name] = ProviderSettingsModel(
                name=name,
                api_key=None,  # Don't expose API keys
                base_url=provider.base_url if hasattr(provider, "base_url") else None,
            )

    return SettingsResponse(llm=llm, providers=providers)


@router.put("/config")
async def update_config(config: dict[str, Any]) -> dict[str, bool]:
    """Update configuration.

    Args:
        config: Configuration updates

    Returns:
        Success status
    """
    manager = get_serve_manager()

    # Update config values
    # Note: This is a simplified implementation
    # In production, you'd want proper validation and persistence
    if "llm" in config:
        llm_config = config["llm"]
        if hasattr(manager.config, "llm"):
            for key, value in llm_config.items():
                if hasattr(manager.config.llm, key):
                    setattr(manager.config.llm, key, value)

    return {"success": True}
