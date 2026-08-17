"""
Groq LLM provider — primary provider.
"""
import logging
from typing import Optional

from backend.llm.base_provider import BaseProvider
from backend.core.config import get_settings

logger = logging.getLogger(__name__)


class GroqProvider(BaseProvider):
    MODEL = "llama-3.1-8b-instant"  # Updated to current model

    def __init__(self):
        settings = get_settings()
        self._api_key = settings.groq_api_key

    def generate(
        self,
        prompt: str,
        temperature: float = 0.2,
        max_tokens: int = 800,
        response_format: Optional[str] = None,
    ) -> str:
        if not self._api_key:
            raise ValueError("GROQ_API_KEY not configured")

        try:
            from groq import Groq
            client = Groq(api_key=self._api_key)

            kwargs = dict(
                model=self.MODEL,
                messages=[{"role": "user", "content": prompt}],
                temperature=temperature,
                max_tokens=max_tokens,
            )
            if response_format == "json":
                kwargs["response_format"] = {"type": "json_object"}

            response = client.chat.completions.create(**kwargs)
            return response.choices[0].message.content.strip()
        except ImportError:
            raise RuntimeError("groq package not installed")
