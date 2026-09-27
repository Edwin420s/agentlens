import json
import logging
from datetime import datetime, timezone

from app.ai.prompts import SESSION_ANALYSIS_SYSTEM
from app.ai.provider import AIProvider
from app.config import get_settings
from app.db.repositories import ai_analysis as ai_repo
from app.db.repositories.counters import format_id
from app.schemas.enums import AnalysisStatus, FailureType
from app.schemas.ai_analysis import AIClassification, AIAnalysisDocument

logger = logging.getLogger(__name__)


def provider_available() -> bool:
    s = get_settings()
    if s.ai_provider == "gemini":
        return bool(s.gemini_api_key)
    return bool(s.groq_api_key)


def _get_provider() -> AIProvider:
    s = get_settings()
    if s.ai_provider == "gemini":
        from app.ai.gemini_provider import GeminiProvider
        return GeminiProvider()
    from app.ai.groq_provider import GroqProvider
    return GroqProvider()


def _validate_evidence(evidence_ids: list[str], valid: set[str]) -> list[str]:
    return [e for e in evidence_ids if e in valid]


async def analyze_session_ai(session: dict, events: list[dict]) -> AIAnalysisDocument | None:
    if not provider_available():
        return None

    try:
        provider = _get_provider()
    except Exception as exc:
        logger.warning("AI provider unavailable: %s", exc)
        return None

    valid_ids = {e["event_id"] for e in events}
    payload = {
        "session_id": session["session_id"],
        "user_request": session["user_request"],
        "events": [
            {
                "event_id": e["event_id"],
                "sequence": e["sequence"],
                "event_type": e["event_type"],
                "actor": e["actor"],
                "content": e.get("content"),
                "tool_name": e.get("tool_name"),
                "tool_input": e.get("tool_input"),
                "tool_output": e.get("tool_output"),
            }
            for e in events
        ],
    }

    try:
        raw = await provider.complete_json(
            SESSION_ANALYSIS_SYSTEM,
            json.dumps(payload, default=str),
        )
    except Exception as exc:
        logger.error("AI session analysis failed: %s", exc)
        return None

    status = raw.get("status", "ambiguous")
    if status not in {"success", "failure", "ambiguous"}:
        status = "ambiguous"

    ft_raw = raw.get("failure_type")
    try:
        ft = FailureType(ft_raw) if ft_raw else None
    except ValueError:
        ft = None

    confidence = float(raw.get("confidence", 0.5))
    confidence = max(0.0, min(1.0, confidence))

    evidence_ids = _validate_evidence(raw.get("evidence_event_ids", []), valid_ids)

    analysis_id = await format_id("AI", "ai_analysis", 5)
    doc = {
        "analysis_id": analysis_id,
        "investigation_id": session["investigation_id"],
        "session_id": session["session_id"],
        "failure_id": None,
        "model": get_settings().groq_model,
        "analysis_version": "v1",
        "status": AnalysisStatus.completed.value,
        "classification": {
            "status": status,
            "failure_type": ft.value if ft else None,
            "confidence": confidence,
        },
        "summary": str(raw.get("summary", ""))[:3000] or "No summary provided.",
        "evidence": [
            {"event_id": eid} for eid in evidence_ids
        ],
        "impact": str(raw.get("impact", ""))[:2000] or "Not specified.",
        "recommendation": str(raw.get("recommendation", ""))[:3000] or "Not specified.",
        "alternative_interpretations": [
            str(x)[:500] for x in raw.get("alternative_interpretations", [])[:10]
        ],
        "needs_human_review": bool(raw.get("needs_human_review", False)),
        "created_at": datetime.now(timezone.utc),
    }

    await ai_repo.insert_analysis(doc)
    return AIAnalysisDocument.model_validate({k: v for k, v in doc.items() if k != "_id"})
