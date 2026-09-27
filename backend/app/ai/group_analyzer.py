import json
import logging
from datetime import datetime, timezone

from app.ai.prompts import GROUP_ANALYSIS_SYSTEM
from app.ai.analyzer import _get_provider, provider_available
from app.db.repositories import ai_analysis as ai_repo
from app.db.repositories.counters import format_id

logger = logging.getLogger(__name__)


async def analyze_group_ai(group: dict, failures: list[dict]) -> dict | None:
    if not provider_available():
        return None

    try:
        provider = _get_provider()
    except Exception as exc:
        logger.warning("AI provider unavailable for group analysis: %s", exc)
        return None

    payload = {
        "group_id": group["group_id"],
        "failure_type": group["failure_type"],
        "occurrence_count": group["occurrence_count"],
        "sample_failures": [
            {
                "failure_id": f["failure_id"],
                "title": f["title"],
                "summary": f["summary"],
                "signals": f.get("signals", []),
                "evidence_event_ids": f.get("evidence_event_ids", []),
            }
            for f in failures[:10]
        ],
    }

    try:
        raw = await provider.complete_json(
            GROUP_ANALYSIS_SYSTEM, json.dumps(payload, default=str)
        )
    except Exception as exc:
        logger.error("Group AI analysis failed: %s", exc)
        return None

    analysis_id = await format_id("AI", "ai_analysis", 5)
    doc = {
        "analysis_id": analysis_id,
        "investigation_id": group["investigation_id"],
        "session_id": None,
        "group_id": group["group_id"],
        "model": "groq",
        "analysis_version": "v1",
        "pattern": str(raw.get("pattern", ""))[:3000] or "No pattern.",
        "common_signals": raw.get("common_signals", [])[:30],
        "affected_workflows": raw.get("affected_workflows", [])[:30],
        "investigation_area": str(raw.get("investigation_area", ""))[:2000] or "N/A",
        "recommendation": str(raw.get("recommendation", ""))[:3000] or "N/A",
        "evidence": raw.get("evidence", [])[:50],
        "alternative_explanations": raw.get("alternative_explanations", [])[:10],
        "confidence": max(0.0, min(1.0, float(raw.get("confidence", 0.5)))),
        "needs_human_review": bool(raw.get("needs_human_review", False)),
        "created_at": datetime.now(timezone.utc),
    }
    await ai_repo.insert_analysis(doc)
    return doc
