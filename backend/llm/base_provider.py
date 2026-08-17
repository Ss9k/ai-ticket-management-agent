"""
Abstract base class for all LLM providers.
"""
from abc import ABC, abstractmethod
from typing import Optional


class BaseProvider(ABC):
    """All LLM providers implement this interface."""

    @abstractmethod
    def generate(
        self,
        prompt: str,
        temperature: float = 0.2,
        max_tokens: int = 800,
        response_format: Optional[str] = None,
    ) -> str:
        """
        Generate a text response from the LLM.

        Args:
            prompt: The full prompt string.
            temperature: Sampling temperature (0.0–1.0).
            max_tokens: Maximum tokens in response.
            response_format: Optional format hint (e.g. "json").

        Returns:
            Generated text string.

        Raises:
            Exception: On provider-level failure (caller handles retry/fallback).
        """
        ...
