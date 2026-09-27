from fastapi import APIRouter, Depends, Query

from app.db.repositories import (
    ai_analysis as ai_repo,
    events as ev_repo,
    failures as fail_repo,
    sessions as sess_repo,
)
from app.exceptions import NotFoundError
from app.schemas.common import APIResponse
from app.schemas.sessions import SessionDetailResponse, SessionDocument
from app.api.deps import Pagination, pagination

router = APIRouter()


@router.get("/investigations/{investigation_id}/sessions")
async def list_sessions(
    investigation_id: str,
    status: str | None = Query(default=None),
    p: Pagination = Depends(pagination),
):
    docs = await sess_repo.list_sessions(investigation_id, status, p.limit, p.offset)
    return APIResponse(success=True, data=[
        SessionDocument.model_validate({k: v for k, v in d.items() if k != "_id"})
        for d in docs
    ])


@router.get("/sessions/{session_id}")
async def get_session(session_id: str, investigation_id: str | None = Query(default=None)):
    s = await sess_repo.get_session(session_id, investigation_id)
    if not s:
        raise NotFoundError(f"Session {session_id} not found.")

    inv_id = s.get("investigation_id")
    events = await ev_repo.list_events_for_session(session_id, inv_id)
    failures = await fail_repo.list_failures_for_session(session_id)
    if inv_id:
        failures = [f for f in failures if f.get("investigation_id") == inv_id]
    ai = await ai_repo.get_analysis_for_session(session_id)

    payload = {
        "session": {k: v for k, v in s.items() if k != "_id"},
        "events": [{k: v for k, v in e.items() if k != "_id"} for e in events],
        "failures": [{k: v for k, v in f.items() if k != "_id"} for f in failures],
        "ai_analyses": [{k: v for k, v in ai.items() if k != "_id"}] if ai else [],
    }
    return APIResponse(success=True, data=SessionDetailResponse.model_validate(payload))
