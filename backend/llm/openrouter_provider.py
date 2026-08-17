"""
OpenRouter LLM provider — tertiary fallback.
Uses HTTP API (no dedicated SDK needed).
"""
import logging
import httpx
from typing import Optional

from backend.llm.base_provider import BaseProvider
from backend.core.config import get_settings

logger = logging.getLogger(__name__)


class OpenRouterProvider(BaseProvider):
    API_URL = "https://openrouter.ai/api/v1/chat/completions"
    MODEL = "meta-llama/llama-3.1-8b-instruct:free"  # Free model

    def __init__(self):
        settings = get_settings()
        self._api_key = settings.openrouter_api_key

    def generate(
        self,
        prompt: str,
        temperature: float = 0.2,
        max_tokens: int = 800,
        response_format: Optional[str] = None,
    ) -> str:
        if not self._api_key:
            raise ValueError("OPENROUTER_API_KEY not configured")

        headers = {
            "Authorization": f"Bearer {self._api_key}",
            "Content-Type": "application/json",
            "HTTP-Referer": "https://supportpilot.local",
            "X-Title": "SupportPilot",
        }
        payload = {
            "model": self.MODEL,
            "messages": [{"role": "user", "content": prompt}],
            "temperature": temperature,
            "max_tokens": max_tokens,
        }
        if response_format == "json":
            payload["response_format"] = {"type": "json_object"}

        with httpx.Client(timeout=30) as client:
            response = client.post(self.API_URL, headers=headers, json=payload)
            response.raise_for_status()
            data = response.json()
            return data["choices"][0]["message"]["content"].strip()
