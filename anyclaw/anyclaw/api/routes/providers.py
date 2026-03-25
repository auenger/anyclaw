"""Provider API endpoints.

Provides CRUD operations for LLM provider configurations.
"""

from __future__ import annotations

import logging
from typing import Optional

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel

from anyclaw.config.loader import get_config, save_config, Config, ProviderConfig
from anyclaw.api.services.provider_tester import ProviderTester, TestResult

logger = logging.getLogger(__name__)

router = APIRouter()

# Global tester instance
_tester: Optional[ProviderTester] = None


def get_tester() -> ProviderTester:
    """Get or create ProviderTester instance."""
    global _tester
    if _tester is None:
        _tester = ProviderTester()
    return _tester


# Response models
class ProviderInfo(BaseModel):
    """Provider info for list response."""

    name: str
    display_name: str
    is_configured: bool
    has_api_key: bool
    base_url: Optional[str] = None
    is_default: bool = False


class ProviderDetail(BaseModel):
    """Detailed provider configuration."""

    name: str
    display_name: str
    api_key: Optional[str] = None  # Masked for security
    base_url: Optional[str] = None
    is_configured: bool
    has_api_key: bool
    is_default: bool = False


class ProviderConfigUpdate(BaseModel):
    """Provider configuration update request."""

    api_key: Optional[str] = None
    base_url: Optional[str] = None


# Known providers with their display names
KNOWN_PROVIDERS = {
    "openai": "OpenAI",
    "anthropic": "Anthropic",
    "zai": "ZAI/GLM",
    "deepseek": "DeepSeek",
    "openrouter": "OpenRouter",
    "ollama": "Ollama",
    "custom": "Custom",
}


@router.get("/providers")
async def list_providers() -> list[ProviderInfo]:
    """Get all provider configurations.

    Returns:
        List of provider info with configuration status
    """
    config = get_config()
    providers = []
    current_provider = config.llm.provider

    for name, display_name in KNOWN_PROVIDERS.items():
        provider_config = getattr(config.providers, name, None)
        has_api_key = bool(provider_config and provider_config.api_key)
        has_base_url = bool(provider_config and provider_config.api_base)
        is_configured = has_api_key or name == "ollama"
        is_default = name == current_provider

        providers.append(
            ProviderInfo(
                name=name,
                display_name=display_name,
                is_configured=is_configured,
                has_api_key=has_api_key,
                base_url=provider_config.api_base if has_base_url else None,
                is_default=is_default,
            )
        )

    return providers


@router.get("/providers/{name}")
async def get_provider(name: str) -> ProviderDetail:
    """Get single provider configuration.

    Args:
        name: Provider name

    Returns:
        Provider configuration details
    """
    if name not in KNOWN_PROVIDERS:
        raise HTTPException(status_code=404, detail=f"Provider not found: {name}")

    config = get_config()
    provider_config = getattr(config.providers, name, None)
    current_provider = config.llm.provider

    has_api_key = bool(provider_config and provider_config.api_key)
    # Mask API key for security - show first 8 chars and last 4 chars
    masked_key = None
    if has_api_key and provider_config.api_key:
        key = provider_config.api_key
        if len(key) > 12:
            masked_key = f"{key[:8]}...{key[-4:]}"
        else:
            masked_key = "****"

    return ProviderDetail(
        name=name,
        display_name=KNOWN_PROVIDERS[name],
        api_key=masked_key,
        base_url=provider_config.api_base if provider_config else None,
        is_configured=has_api_key or name == "ollama",
        has_api_key=has_api_key,
        is_default=name == current_provider,
    )


@router.put("/providers/{name}")
async def update_provider(name: str, update: ProviderConfigUpdate) -> dict:
    """Update provider configuration.

    Updates the provider configuration and persists to config file.

    Args:
        name: Provider name
        update: Configuration update

    Returns:
        Success status
    """
    if name not in KNOWN_PROVIDERS:
        raise HTTPException(status_code=404, detail=f"Provider not found: {name}")

    config = get_config()

    # Get or create provider config
    provider_config = getattr(config.providers, name, None)
    if provider_config is None:
        provider_config = ProviderConfig()
        setattr(config.providers, name, provider_config)

    # Update fields
    if update.api_key is not None:
        # Empty string means clear the key
        provider_config.api_key = update.api_key

    if update.base_url is not None:
        # Empty string means clear the base URL
        provider_config.api_base = update.base_url if update.base_url else None

    # Save to file
    try:
        save_config(config)
        logger.info(f"Provider {name} configuration saved")
    except Exception as e:
        logger.error(f"Failed to save provider config: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to save configuration: {e}")

    return {"success": True, "message": f"Provider {name} configuration saved"}


@router.post("/providers/{name}/test", response_model=TestResult)
async def test_provider(name: str, config_update: Optional[ProviderConfigUpdate] = None) -> TestResult:
    """Test provider connection.

    Tests the provider connection using stored config or provided test config.

    Args:
        name: Provider name
        config_update: Optional config to test (without saving)

    Returns:
        Test result with success status and details
    """
    if name not in KNOWN_PROVIDERS:
        raise HTTPException(status_code=404, detail=f"Provider not found: {name}")

    config = get_config()
    provider_config = getattr(config.providers, name, None)

    # Get API key and base URL
    api_key = None
    base_url = None

    # Use test config if provided, otherwise use stored config
    if config_update:
        api_key = config_update.api_key
        base_url = config_update.base_url
    elif provider_config:
        api_key = provider_config.api_key
        base_url = provider_config.api_base

    # Test connection
    tester = get_tester()
    result = await tester.test_connection(name, api_key, base_url)

    return result


@router.post("/providers/{name}/set-default")
async def set_default_provider(name: str) -> dict:
    """Set provider as default.

    Args:
        name: Provider name

    Returns:
        Success status
    """
    if name not in KNOWN_PROVIDERS:
        raise HTTPException(status_code=404, detail=f"Provider not found: {name}")

    config = get_config()

    # Check if provider is configured
    provider_config = getattr(config.providers, name, None)
    if not provider_config or not provider_config.api_key:
        if name != "ollama":
            raise HTTPException(
                status_code=400,
                detail=f"Provider {name} is not configured. Please configure API key first."
            )

    # Update LLM provider
    config.llm.provider = name

    # Save to file
    try:
        save_config(config)
        logger.info(f"Default provider set to {name}")
    except Exception as e:
        logger.error(f"Failed to set default provider: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to save configuration: {e}")

    return {"success": True, "message": f"Default provider set to {name}"}
