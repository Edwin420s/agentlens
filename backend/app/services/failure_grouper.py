import logging
from datetime import datetime, timezone

from app.db.repositories import failure_groups as fg_repo
from app.db.repositories.counters import format_id
from app.schemas.enums import FailureStatus, Severity

logger = logging.getLogger(__name__)


def _pick_severity(failures: list[dict]) -> Severity:
    order = {"critical": 4, "high": 3, "medium": 2, "low": 1}
    best = max(failures, key=lambda f: order.get(f["severity"], 0))
    return Severity(best["severity"])


async def group_failures(investigation_id: str, failures: list[dict]) -> list[dict]:
    """Group failures by failure_type within an investigation."""
    await fg_repo.delete_groups_for_investigation(investigation_id)

    buckets: dict[str, list[dict]] = {}
    for f in failures:
        buckets.setdefault(f["failure_type"], []).append(f)

    groups: list[dict] = []
    now = datetime.now(timezone.utc)

    for ftype, items in buckets.items():
        group_id = await format_id("GROUP", "failure_groups", 3)
        session_ids = list({f["session_id"] for f in items})
        failure_ids = [f["failure_id"] for f in items]
        severity = _pick_severity(items)
        confidence = sum(f["confidence"] for f in items) / len(items)

        common_signals: list[str] = []
        for f in items:
            for s in f.get("signals", []):
                if s not in common_signals:
                    common_signals.append(s)

        first = items[0]
        group = {
            "group_id": group_id,
            "investigation_id": investigation_id,
            "failure_type": ftype,
            "title": first["title"],
            "description": first["summary"],
            "occurrence_count": len(items),
            "severity": severity.value,
            "confidence": round(confidence, 3),
            "failure_ids": failure_ids,
            "session_ids": session_ids,
            "common_signals": common_signals,
            "ai_summary": first["summary"],
            "recommendation": first["recommendation"],
            "status": FailureStatus.new.value,
            "created_at": now,
        }
        await fg_repo.insert_group(group)
        groups.append(group)

    return groups
