"""LLM client abstraction and provider implementations."""

from __future__ import annotations

import json
import logging
import time
import urllib.error
import urllib.request
from typing import Optional, Protocol

from src.config import GROQ_DEFAULT_BASE_URL, Settings, get_settings
from src.domain.exceptions import LLMProviderError

logger = logging.getLogger(__name__)


class LLMClient(Protocol):
    """Protocol for LLM completion providers."""

    def complete(
        self,
        messages: list[dict[str, str]],
        *,
        temperature: float = 0.3,
    ) -> str:
        ...


def _chat_completions(
    settings: Settings,
    messages: list[dict[str, str]],
    *,
    temperature: float,
    base_url: Optional[str] = None,
    provider_name: str = "LLM",
) -> str:
    """Shared OpenAI-compatible chat completions (Groq, OpenAI)."""
    try:
        from openai import OpenAI
    except ImportError as exc:
        raise LLMProviderError("openai package not installed. Run: pip install openai") from exc

    if not settings.llm_api_key:
        raise LLMProviderError(
            "LLM_API_KEY is not set. Add your Groq API key to .env or use LLM_PROVIDER=ollama."
        )

    kwargs: dict = {
        "api_key": settings.llm_api_key,
        "timeout": settings.llm_timeout,
    }
    if base_url:
        kwargs["base_url"] = base_url

    client = OpenAI(**kwargs)
    last_error: Optional[Exception] = None
    max_attempts = 1 + settings.llm_max_retries

    for attempt in range(1, max_attempts + 1):
        try:
            response = client.chat.completions.create(
                model=settings.llm_model,
                messages=messages,
                temperature=temperature,
                response_format={"type": "json_object"},
            )
            content = response.choices[0].message.content
            if not content:
                raise LLMProviderError(f"{provider_name} returned empty response")
            return content.strip()
        except Exception as exc:
            last_error = exc
            logger.warning(
                "%s attempt %d/%d failed: %s",
                provider_name,
                attempt,
                max_attempts,
                exc,
            )
            if attempt < max_attempts:
                time.sleep(2**attempt)

    raise LLMProviderError(f"{provider_name} API failed: {last_error}") from last_error


class GroqClient:
    """Groq Chat Completions API (OpenAI-compatible). Default production provider."""

    def __init__(self, settings: Optional[Settings] = None):
        self._settings = settings or get_settings()

    def complete(
        self,
        messages: list[dict[str, str]],
        *,
        temperature: float = 0.3,
    ) -> str:
        return _chat_completions(
            self._settings,
            messages,
            temperature=temperature,
            base_url=self._settings.groq_base_url.rstrip("/"),
            provider_name="Groq",
        )


class OpenAIClient:
    """OpenAI Chat Completions API client (optional alternative)."""

    def __init__(self, settings: Optional[Settings] = None):
        self._settings = settings or get_settings()

    def complete(
        self,
        messages: list[dict[str, str]],
        *,
        temperature: float = 0.3,
    ) -> str:
        return _chat_completions(
            self._settings,
            messages,
            temperature=temperature,
            base_url=None,
            provider_name="OpenAI",
        )


class OllamaClient:
    """Local Ollama API client (no API key required)."""

    def __init__(self, settings: Optional[Settings] = None):
        self._settings = settings or get_settings()

    def complete(
        self,
        messages: list[dict[str, str]],
        *,
        temperature: float = 0.3,
    ) -> str:
        url = f"{self._settings.ollama_base_url.rstrip('/')}/api/chat"
        payload = {
            "model": self._settings.llm_model,
            "messages": messages,
            "stream": False,
            "format": "json",
            "options": {"temperature": temperature},
        }

        last_error: Optional[Exception] = None
        max_attempts = 1 + self._settings.llm_max_retries

        for attempt in range(1, max_attempts + 1):
            try:
                req = urllib.request.Request(
                    url,
                    data=json.dumps(payload).encode("utf-8"),
                    headers={"Content-Type": "application/json"},
                    method="POST",
                )
                with urllib.request.urlopen(req, timeout=self._settings.llm_timeout) as resp:
                    data = json.loads(resp.read().decode("utf-8"))
                content = data.get("message", {}).get("content", "")
                if not content:
                    raise LLMProviderError("Ollama returned empty response")
                return content.strip()
            except urllib.error.URLError as exc:
                last_error = exc
                logger.warning("Ollama attempt %d/%d failed: %s", attempt, max_attempts, exc)
                if attempt < max_attempts:
                    time.sleep(2**attempt)

        raise LLMProviderError(
            f"Ollama API failed at {url}. Is Ollama running? Error: {last_error}"
        ) from last_error


def get_llm_client(settings: Optional[Settings] = None) -> LLMClient:
    """Factory: return LLM client based on LLM_PROVIDER setting."""
    settings = settings or get_settings()
    provider = settings.llm_provider.lower()

    if provider == "groq":
        return GroqClient(settings)
    if provider == "openai":
        return OpenAIClient(settings)
    if provider == "ollama":
        return OllamaClient(settings)

    raise LLMProviderError(
        f"Unknown LLM_PROVIDER: {provider}. Use groq, openai, or ollama."
    )


def is_llm_available(settings: Optional[Settings] = None) -> bool:
    """Check if LLM can be called with current configuration."""
    settings = settings or get_settings()
    if settings.llm_provider == "ollama":
        return True
    return bool(settings.llm_api_key)
