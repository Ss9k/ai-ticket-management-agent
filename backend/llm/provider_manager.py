"""
LLM Provider Manager — handles retry and fallback across providers.
Provider order: Groq -> Gemini -> OpenRouter
"""
import logging
import time
from typing import Optional

from backend.llm.base_provider import BaseProvider
from backend.llm.groq_provider import GroqProvider
from backend.llm.gemini_provider import GeminiProvider
from backend.llm.openrouter_provider import OpenRouterProvider
from backend.core.config import get_settings

logger = logging.getLogger(__name__)


class LLMProviderManager:
    """
    Manages ordered LLM provider list with per-provider retry and cascade fallback.
    Application code calls llm.generate(prompt) and never instantiates providers directly.
    """

    def __init__(self):
        settings = get_settings()
        self._max_retries = settings.llm_max_retries
        self._providers: list[tuple[str, BaseProvider]] = [
            ("GroqProvider", GroqProvider()),
            ("GeminiProvider", GeminiProvider()),
            ("OpenRouterProvider", OpenRouterProvider()),
        ]

    def generate(
        self,
        prompt: str,
        temperature: Optional[float] = None,
        max_tokens: Optional[int] = None,
        response_format: Optional[str] = None,
    ) -> str:
        """
        Try each provider in order.
        For each provider, retry up to max_retries times before moving on.
        Raises RuntimeError only if ALL providers fail.
        """
        settings = get_settings()
        temp = temperature if temperature is not None else settings.llm_temperature
        tokens = max_tokens if max_tokens is not None else settings.llm_max_tokens

        last_error: Exception = RuntimeError("No LLM providers available")

        for provider_name, provider in self._providers:
            for attempt in range(1, self._max_retries + 1):
                try:
                    logger.info(f"Trying {provider_name} (attempt {attempt}/{self._max_retries})")
                    result = provider.generate(
                        prompt=prompt,
                        temperature=temp,
                        max_tokens=tokens,
                        response_format=response_format,
                    )
                    logger.info(f"{provider_name} success")
                    return result
                except Exception as e:
                    last_error = e
                    logger.warning(f"{provider_name} attempt {attempt} failed: {e}")
                    if attempt < self._max_retries:
                        time.sleep(1)

            logger.error(f"{provider_name} failed after {self._max_retries} attempts. "
                         f"Switching to next provider.")

        logger.error("All LLM providers failed.")
        raise RuntimeError(f"All LLM providers exhausted. Last error: {last_error}")


# Module-level singleton — application code imports this
_manager_instance: LLMProviderManager | None = None


def get_llm_manager() -> LLMProviderManager:
    global _manager_instance
    if _manager_instance is None:
        _manager_instance = LLMProviderManager()
    return _manager_instance
