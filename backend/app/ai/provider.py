from abc import ABC, abstractmethod
from typing import Any


class AIProvider(ABC):
    @abstractmethod
    async def complete_json(self, system: str, user: str) -> dict[str, Any]:
        ...
