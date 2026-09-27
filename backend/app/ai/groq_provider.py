import json
import logging
from typing import Any

from groq import AsyncGroq
from tenacity import retry, stop_after_attempt, wait_exponential

from app.ai.provider import AIProvider
from app.config import get_settings
from app.exceptions import AIProviderError

logger = logging.getLogger(__name__)


class GroqProvider(AIProvider):
    def __init__(self) -> None:
        s = get_settings()
        if not s.groq_api_key:
            raise AIProviderError("GROQ_API_KEY is not configured.")
        self._client = AsyncGroq(api_key=s.groq_api_key)
        self._model = s.groq_model
        self._max_retries = s.ai_max_retries

    async def complete_json(self, system: str, user: str) -> dict[str, Any]:
        @retry(
            stop=stop_after_attempt(self._max_retries),
            wait=wait_exponential(multiplier=1, min=1, max=8),
            reraise=True,
        )
        async def _call():
            resp = await self._client.chat.completions.create(
                model=self._model,
                messages=[
                    {"role": "system", "content": system},
                    {"role": "user", "content": user},
                ],
                response_format={"type": "json_object"},
                temperature=0.1,
            )
            content = resp.choices[0].message.content or "{}"
            try:
                return json.loads(content)
            except json.JSONDecodeError as exc:
                raise AIProviderError(f"Groq returned invalid JSON: {exc}")

        try:
            return await _call()
        except AIProviderError:
            raise
        except Exception as exc:
            raise AIProviderError(f"Groq call failed: {exc}")
