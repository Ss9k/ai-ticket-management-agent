"""
Google Gemini LLM provider — secondary fallback.
"""
import logging
import json
from typing import Optional

from backend.llm.base_provider import BaseProvider
from backend.core.config import get_settings

logger = logging.getLogger(__name__)


class GeminiProvider(BaseProvider):
    MODEL = "gemini-1.5-flash"

    def __init__(self):
        settings = get_settings()
        self._api_key = settings.gemini_api_key

    def generate(
        self,
        prompt: str,
        temperature: float = 0.2,
        max_tokens: int = 800,
        response_format: Optional[str] = None,
    ) -> str:
        if not self._api_key:
            raise ValueError("GEMINI_API_KEY not configured")

        try:
            import google.generativeai as genai
            genai.configure(api_key=self._api_key)

            generation_config = {
                "temperature": temperature,
                "max_output_tokens": max_tokens,
            }
            # Note: JSON mode requires gemini-1.5-pro model
            # For flash model, we'll parse JSON from text response

            model = genai.GenerativeModel(
                model_name=self.MODEL,
                generation_config=generation_config,
            )
            
            # If JSON format requested, add instruction to prompt
            if response_format == "json":
                prompt = f"{prompt}\n\nRespond with valid JSON only, no other text."
            
            response = model.generate_content(prompt)
            return response.text.strip()
        except ImportError:
            raise RuntimeError("google-generativeai package not installed")
