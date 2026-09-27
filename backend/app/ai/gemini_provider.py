import json
import logging
from typing import Any

import google.generativeai as genai
from tenacity import retry, stop_after_attempt, wait_exponential

from app.ai.provider import AIProvider
from app.config import get_settings
from app.exceptions import AIProviderError

logger = logging.getLogger(__name__)


class GeminiProvider(AIProvider):
    def __init__(self) -> None:
        s = get_settings()
        if not s.gemini_api_key:
            raise AIProviderError("GEMINI_API_KEY is not configured.")
        genai.configure(api_key=s.gemini_api_key)
        self._model = genai.GenerativeModel(
            s.gemini_model,
            generation_config={"response_mime_type": "application/json", "temperature": 0.1},
        )
        self._max_retries = s.ai_max_retries

    async def complete_json(self, system: str, user: str) -> dict[str, Any]:
        @retry(
            stop=stop_after_attempt(self._max_retries),
            wait=wait_exponential(multiplier=1, min=1, max=8),
            reraise=True,
        )
        async def _call():
            prompt = f"{system}\n\n---\n\n{user}"
            resp = await self._model.generate_content_async(prompt)
            text = resp.text or "{}"
            try:
                return json.loads(text)
            except json.JSONDecodeError as exc:
                raise AIProviderError(f"Gemini returned invalid JSON: {exc}")

        try:
            return await _call()
        except AIProviderError:
            raise
        except Exception as exc:
            raise AIProviderError(f"Gemini call failed: {exc}")
