from app.ai.assistant import answer_question
from app.db.repositories import failures as fail_repo
from app.schemas.ai_analysis import (
    AssistantEvidence,
    InvestigationAssistantResponse,
)


async def ask(investigation_id: str, question: str) -> InvestigationAssistantResponse:
    failures = await fail_repo.list_all_failures(investigation_id)
    result = await answer_question(question, failures)

    observed = []
    if failures:
        counts: dict[str, int] = {}
        for f in failures:
            counts[f["failure_type"]] = counts.get(f["failure_type"], 0) + 1
        top = sorted(counts.items(), key=lambda x: -x[1])[:3]
        observed.append("Observed failure types: " + ", ".join(f"{k} ({v})" for k, v in top) + ".")

    recs = result.get("recommendations", [])

    return InvestigationAssistantResponse(
        answer=result["answer"],
        evidence=[AssistantEvidence(**e) for e in result["evidence"]],
        uncertainty=result["uncertainty"],
        recommendations=recs,
        recommendation=recs,
        observed_facts=observed,
    )
