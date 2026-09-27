from typing import Any

from .common import AgentLensBaseModel


class ExportResponse(AgentLensBaseModel):
    investigation_id: str
    format: str
    filename: str
    records: int
    data: list[dict[str, Any]]
