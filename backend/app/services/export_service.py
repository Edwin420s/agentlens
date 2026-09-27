from typing import Any

from app.db.repositories import (
    failures as fail_repo,
    failure_groups as fg_repo,
)
from app.schemas.export import ExportResponse


def _to_serializable(value: Any) -> Any:
    from datetime import datetime
    if isinstance(value, datetime):
        return value.isoformat()
    if isinstance(value, dict):
        return {k: _to_serializable(v) for k, v in value.items() if k != "_id"}
    if isinstance(value, list):
        return [_to_serializable(v) for v in value]
    return value


async def export_investigation(investigation_id: str, fmt: str = "json") -> ExportResponse:
    failures = await fail_repo.list_all_failures(investigation_id)
    groups = await fg_repo.list_groups(investigation_id)

    records = []
    for f in failures:
        records.append({
            "kind": "failure",
            "data": _to_serializable(f),
        })
    for g in groups:
        records.append({
            "kind": "group",
            "data": _to_serializable(g),
        })

    return ExportResponse(
        investigation_id=investigation_id,
        format=fmt,
        filename=f"{investigation_id}_export.{fmt}",
        records=len(records),
        data=records,
    )
