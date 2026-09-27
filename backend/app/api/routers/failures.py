from fastapi import APIRouter, Depends, Query

from app.db.repositories import (
    ai_analysis as ai_repo,
    events as ev_repo,
    failures as fail_repo,
    sessions as sess_repo,
)
from app.exceptions import NotFoundError
from app.schemas.common import APIResponse
from app.schemas.failures import FailureDocument, FailureDetailResponse, UpdateFailureStatusRequest
from app.api.deps import Pagination, pagination

router = APIRouter()


@router.get("/investigations/{investigation_id}/failures")
async def list_failures(
    investigation_id: str,
    failure_type: str | None = Query(default=None),
    severity: str | None = Query(default=None),
    status: str | None = Query(default=None),
    p: Pagination = Depends(pagination),
):
    docs = await fail_repo.list_failures(
        investigation_id, failure_type, severity, status, p.limit, p.offset
    )
    return APIResponse(success=True, data=[
        FailureDocument.model_validate({k: v for k, v in d.items() if k != "_id"})
        for d in docs
    ])


@router.get("/failures/{failure_id}")
async def get_failure(failure_id: str):
    f = await fail_repo.get_failure(failure_id)
    if not f:
        raise NotFoundError(f"Failure {failure_id} not found.")

    session = await sess_repo.get_session(f["session_id"])
    if not session:
        raise NotFoundError(f"Session {f['session_id']} not found.")

    evidence_ids = f.get("evidence_event_ids", [])
    evidence_events = await ev_repo.get_events_by_ids(evidence_ids)

    ai = await ai_repo.get_analysis_for_session(f["session_id"])

    related = await fail_repo.list_failures_for_session(f["session_id"])
    related = [r for r in related if r["failure_id"] != f["failure_id"]]

    payload = {
        "failure": {k: v for k, v in f.items() if k != "_id"},
        "session_summary": {k: v for k, v in session.items() if k != "_id"},
        "evidence_events": [
            {k: v for k, v in e.items() if k != "_id"} for e in evidence_events
        ],
        "ai_analysis": {k: v for k, v in ai.items() if k != "_id"} if ai else None,
        "related_failures": [
            {k: v for k, v in r.items() if k != "_id"} for r in related
        ],
    }
    return APIResponse(success=True, data=FailureDetailResponse.model_validate(payload))


@router.patch("/failures/{failure_id}/status")
async def update_failure_status(failure_id: str, payload: UpdateFailureStatusRequest):
    f = await fail_repo.get_failure(failure_id)
    if not f:
        raise NotFoundError(f"Failure {failure_id} not found.")
    await fail_repo.update_failure(failure_id, {"status": payload.status.value})
    return APIResponse(success=True, data={"failure_id": failure_id, "status": payload.status.value})
