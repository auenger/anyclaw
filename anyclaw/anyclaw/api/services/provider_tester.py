"""Provider connection testing service.

Tests API connections for various LLM providers.
"""

from __future__ import annotations

import asyncio
import logging
import time
from typing import Any, Optional

import httpx
from pydantic import BaseModel

logger = logging.getLogger(__name__)


class TestResult(BaseModel):
    """Provider connection test result."""

    success: bool
    message: str
    latency_ms: Optional[int] = None
    error_code: Optional[str] = None
    models_count: Optional[int] = None


class ProviderTester:
    """Tests LLM provider connections."""

    # Provider display names and default endpoints
    PROVIDERS = {
        "openai": {
            "display_name": "OpenAI",
            "default_base_url": "https://api.openai.com/v1",
        },
        "anthropic": {
            "display_name": "Anthropic",
            "default_base_url": "https://api.anthropic.com/v1",
        },
        "zai": {
            "display_name": "ZAI/GLM",
            "default_base_url": "https://open.bigmodel.cn/api/paas/v4",
        },
        "deepseek": {
            "display_name": "DeepSeek",
            "default_base_url": "https://api.deepseek.com/v1",
        },
        "openrouter": {
            "display_name": "OpenRouter",
            "default_base_url": "https://openrouter.ai/api/v1",
        },
        "ollama": {
            "display_name": "Ollama",
            "default_base_url": "http://localhost:11434/v1",
        },
    }

    def __init__(self, timeout: float = 10.0):
        """Initialize tester.

        Args:
            timeout: Request timeout in seconds
        """
        self.timeout = timeout

    async def test_connection(
        self,
        provider: str,
        api_key: Optional[str] = None,
        base_url: Optional[str] = None,
    ) -> TestResult:
        """Test provider connection.

        Args:
            provider: Provider name
            api_key: API key for authentication
            base_url: Custom base URL (optional)

        Returns:
            TestResult with success status and details
        """
        provider_lower = provider.lower()

        if provider_lower not in self.PROVIDERS:
            return TestResult(
                success=False,
                message=f"Unknown provider: {provider}",
                error_code="UNKNOWN_PROVIDER",
            )

        provider_info = self.PROVIDERS[provider_lower]
        effective_base_url = base_url or provider_info["default_base_url"]
        display_name = provider_info["display_name"]

        # Ollama doesn't need API key
        if provider_lower == "ollama":
            return await self._test_ollama(effective_base_url, display_name)

        # Other providers need API key
        if not api_key:
            return TestResult(
                success=False,
                message="API Key is required",
                error_code="MISSING_API_KEY",
            )

        # Test based on provider type
        if provider_lower == "openai":
            return await self._test_openai_compatible(
                effective_base_url, api_key, display_name
            )
        elif provider_lower == "anthropic":
            return await self._test_anthropic(effective_base_url, api_key, display_name)
        elif provider_lower == "zai":
            return await self._test_zai(effective_base_url, api_key, display_name)
        elif provider_lower == "deepseek":
            return await self._test_openai_compatible(
                effective_base_url, api_key, display_name
            )
        elif provider_lower == "openrouter":
            return await self._test_openai_compatible(
                effective_base_url, api_key, display_name
            )
        else:
            return TestResult(
                success=False,
                message=f"Provider {provider} not implemented",
                error_code="NOT_IMPLEMENTED",
            )

    async def _test_openai_compatible(
        self, base_url: str, api_key: str, display_name: str
    ) -> TestResult:
        """Test OpenAI-compatible API (OpenAI, DeepSeek, OpenRouter)."""
        start_time = time.time()

        try:
            async with httpx.AsyncClient(timeout=self.timeout) as client:
                response = await client.get(
                    f"{base_url.rstrip('/')}/models",
                    headers={"Authorization": f"Bearer {api_key}"},
                )

            latency_ms = int((time.time() - start_time) * 1000)

            if response.status_code == 200:
                data = response.json()
                models_count = len(data.get("data", []))
                return TestResult(
                    success=True,
                    message=f"Connected successfully, {models_count} models available",
                    latency_ms=latency_ms,
                    models_count=models_count,
                )
            elif response.status_code == 401:
                return TestResult(
                    success=False,
                    message="Invalid API Key",
                    error_code="INVALID_API_KEY",
                    latency_ms=latency_ms,
                )
            else:
                return TestResult(
                    success=False,
                    message=f"HTTP {response.status_code}: {response.text[:100]}",
                    error_code="HTTP_ERROR",
                    latency_ms=latency_ms,
                )

        except httpx.TimeoutException:
            return TestResult(
                success=False,
                message="Connection timeout",
                error_code="TIMEOUT",
            )
        except httpx.ConnectError:
            return TestResult(
                success=False,
                message="Unable to connect to server",
                error_code="CONNECTION_ERROR",
            )
        except Exception as e:
            logger.error(f"Provider test error: {e}")
            return TestResult(
                success=False,
                message=f"Connection failed: {str(e)[:50]}",
                error_code="UNKNOWN_ERROR",
            )

    async def _test_anthropic(
        self, base_url: str, api_key: str, display_name: str
    ) -> TestResult:
        """Test Anthropic API connection."""
        start_time = time.time()

        try:
            # Anthropic doesn't have a /models endpoint, use a minimal message request
            async with httpx.AsyncClient(timeout=self.timeout) as client:
                response = await client.post(
                    f"{base_url.rstrip('/')}/messages",
                    headers={
                        "x-api-key": api_key,
                        "anthropic-version": "2023-06-01",
                        "Content-Type": "application/json",
                    },
                    json={
                        "model": "claude-3-haiku-20240307",
                        "max_tokens": 1,
                        "messages": [{"role": "user", "content": "hi"}],
                    },
                )

            latency_ms = int((time.time() - start_time) * 1000)

            if response.status_code == 200:
                return TestResult(
                    success=True,
                    message="Connected successfully",
                    latency_ms=latency_ms,
                )
            elif response.status_code == 401:
                return TestResult(
                    success=False,
                    message="Invalid API Key",
                    error_code="INVALID_API_KEY",
                    latency_ms=latency_ms,
                )
            elif response.status_code == 404:
                return TestResult(
                    success=False,
                    message="Endpoint not found, check base URL",
                    error_code="ENDPOINT_NOT_FOUND",
                    latency_ms=latency_ms,
                )
            else:
                return TestResult(
                    success=False,
                    message=f"HTTP {response.status_code}: {response.text[:100]}",
                    error_code="HTTP_ERROR",
                    latency_ms=latency_ms,
                )

        except httpx.TimeoutException:
            return TestResult(
                success=False,
                message="Connection timeout",
                error_code="TIMEOUT",
            )
        except httpx.ConnectError:
            return TestResult(
                success=False,
                message="Unable to connect to server",
                error_code="CONNECTION_ERROR",
            )
        except Exception as e:
            logger.error(f"Anthropic test error: {e}")
            return TestResult(
                success=False,
                message=f"Connection failed: {str(e)[:50]}",
                error_code="UNKNOWN_ERROR",
            )

    async def _test_zai(
        self, base_url: str, api_key: str, display_name: str
    ) -> TestResult:
        """Test ZAI/GLM API connection (OpenAI compatible)."""
        return await self._test_openai_compatible(base_url, api_key, display_name)

    async def _test_ollama(self, base_url: str, display_name: str) -> TestResult:
        """Test Ollama API connection."""
        start_time = time.time()

        try:
            async with httpx.AsyncClient(timeout=self.timeout) as client:
                response = await client.get(f"{base_url.rstrip('/')}/tags")

            latency_ms = int((time.time() - start_time) * 1000)

            if response.status_code == 200:
                data = response.json()
                models = data.get("models", [])
                models_count = len(models)
                return TestResult(
                    success=True,
                    message=f"Connected successfully, {models_count} models available",
                    latency_ms=latency_ms,
                    models_count=models_count,
                )
            else:
                return TestResult(
                    success=False,
                    message=f"HTTP {response.status_code}: {response.text[:100]}",
                    error_code="HTTP_ERROR",
                    latency_ms=latency_ms,
                )

        except httpx.TimeoutException:
            return TestResult(
                success=False,
                message="Connection timeout. Is Ollama running?",
                error_code="TIMEOUT",
            )
        except httpx.ConnectError:
            return TestResult(
                success=False,
                message="Unable to connect. Is Ollama running?",
                error_code="CONNECTION_ERROR",
            )
        except Exception as e:
            logger.error(f"Ollama test error: {e}")
            return TestResult(
                success=False,
                message=f"Connection failed: {str(e)[:50]}",
                error_code="UNKNOWN_ERROR",
            )
