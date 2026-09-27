import logging
from datetime import datetime, timezone

from app.db.repositories import events as ev_repo
from app.db.repositories.counters import format_id
from app.schemas.enums import FailureStatus, FailureType, Severity
from app.services.severity import SIGNAL_TO_TYPE, severity_for

logger = logging.getLogger(__name__)


_FAILURE_TITLES: dict[FailureType, str] = {
    FailureType.unsupported_success: "Agent claims success without performing the requested action",
    FailureType.no_progress: "Agent failed to make progress on the request",
    FailureType.wrong_record: "Agent operated on the wrong record",
    FailureType.repeated_question: "Agent repeatedly asked the same question",
    FailureType.incomplete_request: "Agent completed only part of the request",
}


_FAILURE_SUMMARIES: dict[FailureType, str] = {
    FailureType.unsupported_success: (
        "The agent reported a successful outcome but no tool call or action "
        "in the session actually succeeded."
    ),
    FailureType.no_progress: (
        "The session shows repeated attempts without effective progress."
    ),
    FailureType.wrong_record: (
        "The agent acted on an entity that does not match the entity "
        "identified in the user's request."
    ),
    FailureType.repeated_question: (
        "The agent repeated the same question to the user without moving forward."
    ),
    FailureType.incomplete_request: (
        "Only part of the user's multi-part request was addressed."
    ),
}


_RECOMMENDATIONS: dict[FailureType, str] = {
    FailureType.unsupported_success: (
        "Tighten the agent's success criteria: require a successful tool "
        "result before emitting a success message."
    ),
    FailureType.no_progress: (
        "Add retry/backoff limits and detect repeated identical tool calls; "
        "escalate after N failed attempts."
    ),
    FailureType.wrong_record: (
        "Validate entity identifiers extracted from the user request against "
        "the identifiers passed to tools."
    ),
    FailureType.repeated_question: (
        "Track the agent's own prior questions and prevent duplicate prompts."
    ),
    FailureType.incomplete_request: (
        "Decompose multi-part user requests into explicit sub-tasks and verify "
        "each was addressed before completion."
    ),
}


async def build_failures(investigation_id: str, session: dict, analysis: dict) -> list[dict]:
    signals = analysis["signals"]
    if not signals:
        return []

    seen_types: set[FailureType] = set()
    failures: list[dict] = []
    now = datetime.now(timezone.utc)

    for signal in signals:
        ftype = SIGNAL_TO_TYPE.get(signal)
        if ftype is None or ftype in seen_types:
            continue
        seen_types.add(ftype)

        evidence_ids = session.get("evidence_event_ids") or []
        if not evidence_ids:
            # fallback: query recent events for the session
            evs = await ev_repo.list_events_for_session(session["session_id"])
            evidence_ids = [e["event_id"] for e in evs[:5]]
        if not evidence_ids:
            # No evidence -> skip; a failure without evidence cannot be cited.
            continue

        failure_id = await format_id("FAIL", "failures", 4)
        severity = severity_for(ftype)

        failures.append({
            "failure_id": failure_id,
            "investigation_id": investigation_id,
            "session_id": session["session_id"],
            "failure_type": ftype.value,
            "severity": severity.value,
            "confidence": 0.75,
            "title": _FAILURE_TITLES[ftype],
            "summary": _FAILURE_SUMMARIES[ftype],
            "evidence_event_ids": evidence_ids[:5],
            "impact": _FAILURE_SUMMARIES[ftype],
            "signals": [signal],
            "recommendation": _RECOMMENDATIONS[ftype],
            "status": FailureStatus.new.value,
            "created_at": now,
        })

    return failures
