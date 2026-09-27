import json
import logging

from app.ai.prompts import ASSISTANT_SYSTEM
from app.ai.analyzer import _get_provider, provider_available

logger = logging.getLogger(__name__)


def _deterministic_assistant_response(question: str, failures: list[dict]) -> dict:
    from collections import Counter

    type_counts = Counter(f.get("failure_type", "unknown") for f in failures)
    sev_counts = Counter(f.get("severity", "medium") for f in failures)
    critical_failures = [f for f in failures if f.get("severity") == "critical"]
    unsupported = [f for f in failures if f.get("failure_type") == "unsupported_success"]
    wrong_records = [f for f in failures if f.get("failure_type") == "wrong_record"]

    top_type = type_counts.most_common(1)[0][0] if type_counts else "unsupported_success"
    q_lower = question.lower()

    if "first" in q_lower or "investigate" in q_lower or "priority" in q_lower:
        answer = (
            f"Engineers should investigate **unsupported_success** and **critical** failures first. "
            f"There are {len(unsupported)} instances of unsupported success and {len(critical_failures)} critical severity "
            f"events in this dataset. In these sessions, the agent hallucinated successful task completion despite tool failures, "
            f"causing silent workflow corruption that end-users cannot detect without log inspection."
        )
    elif "quiet" in q_lower or "success" in q_lower or "claim" in q_lower:
        answer = (
            f"Silent workflow failures are concentrated in the **unsupported_success** category ({len(unsupported)} instances). "
            f"In these traces, the agent's final message informed the customer that their request was complete, "
            f"even though the preceding API tool response returned an error code or negative status."
        )
    elif "wrong" in q_lower or "record" in q_lower:
        answer = (
            f"There are {len(wrong_records)} observed **wrong_record** failures. In these execution traces, "
            f"the agent retrieved, operated on, or displayed data corresponding to an incorrect customer, order, "
            f"or item identifier, leading to data confidentiality and integrity violations."
        )
    else:
        answer = (
            f"AgentLens observed {len(failures)} failures across {len(type_counts)} distinct patterns: "
            + ", ".join(f"{k} ({v})" for k, v in type_counts.most_common())
            + f". Most severe issues stem from {top_type} with {len(critical_failures)} critical-level breakages."
        )

    observed_facts = [
        f"Failure distribution: " + ", ".join(f"{k.replace('_', ' ')}: {v}" for k, v in type_counts.items()),
        f"Severity levels recorded: " + ", ".join(f"{k}: {v}" for k, v in sev_counts.items()),
        f"{len(unsupported)} sessions exhibited terminal success claims without successful tool backing.",
    ]
    if wrong_records:
        observed_facts.append(f"{len(wrong_records)} sessions exhibited cross-entity ID discrepancies in tool payloads.")

    recommendations = [
        "Enforce strict tool-result schema contract validation before the agent generates its final answer.",
        "Add deterministic entity-matching verification to block cross-record leakage.",
        "Implement circuit breakers that halt the workflow upon unhandled 4xx/5xx API responses.",
    ]

    evidence = [
        {"failure_id": f["failure_id"], "event_ids": f.get("evidence_event_ids", [])}
        for f in failures[:5]
    ]

    return {
        "answer": answer,
        "evidence": evidence,
        "uncertainty": "Synthesized deterministically from stored session traces. Configure GROQ_API_KEY or GEMINI_API_KEY for dynamic open-ended reasoning.",
        "recommendations": recommendations,
        "observed_facts": observed_facts,
    }


async def answer_question(question: str, failures: list[dict]) -> dict:
    if not provider_available():
        return _deterministic_assistant_response(question, failures)

    try:
        provider = _get_provider()
    except Exception as exc:
        logger.warning("Assistant provider unavailable: %s", exc)
        return _deterministic_assistant_response(question, failures)

    valid_failure_ids = {f["failure_id"] for f in failures}
    valid_event_ids: set[str] = set()
    for f in failures:
        for eid in f.get("evidence_event_ids", []):
            valid_event_ids.add(eid)

    payload = {
        "question": question,
        "failures": [
            {
                "failure_id": f["failure_id"],
                "failure_type": f["failure_type"],
                "severity": f["severity"],
                "title": f["title"],
                "summary": f["summary"],
                "signals": f.get("signals", []),
                "evidence_event_ids": f.get("evidence_event_ids", []),
                "session_id": f["session_id"],
            }
            for f in failures[:100]
        ],
    }

    try:
        raw = await provider.complete_json(ASSISTANT_SYSTEM, json.dumps(payload, default=str))
    except Exception as exc:
        logger.error("Assistant call failed: %s", exc)
        return {
            "answer": "Assistant failed to produce an answer.",
            "evidence": [],
            "uncertainty": str(exc),
            "recommendations": [],
        }

    validated_evidence = []
    for item in raw.get("evidence", []):
        fid = item.get("failure_id")
        eids = item.get("event_ids", [])
        if fid in valid_failure_ids:
            validated_evidence.append({
                "failure_id": fid,
                "event_ids": [e for e in eids if e in valid_event_ids],
            })

    return {
        "answer": str(raw.get("answer", ""))[:5000] or "No answer produced.",
        "evidence": validated_evidence,
        "uncertainty": str(raw.get("uncertainty", ""))[:2000] or "None stated.",
        "recommendations": [str(r)[:500] for r in raw.get("recommendations", [])[:20]],
    }
