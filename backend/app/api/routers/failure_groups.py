from fastapi import APIRouter

from app.db.repositories import failure_groups as fg_repo, failures as fail_repo
from app.exceptions import NotFoundError
from app.schemas.common import APIResponse
from app.schemas.failure_groups import FailureGroupDocument, FailureGroupDetailResponse

router = APIRouter()


@router.get("/investigations/{investigation_id}/groups")
@router.get("/investigations/{investigation_id}/failure-groups")
async def list_groups(investigation_id: str):
    docs = await fg_repo.list_groups(investigation_id)
    return APIResponse(success=True, data=[
        FailureGroupDocument.model_validate({k: v for k, v in d.items() if k != "_id"})
        for d in docs
    ])


@router.get("/groups/{group_id}")
@router.get("/failure-groups/{group_id}")
async def get_group(group_id: str):
    g = await fg_repo.get_group(group_id)
    if not g:
        raise NotFoundError(f"Group {group_id} not found.")

    failures = await fail_repo.list_failures(
        investigation_id=g["investigation_id"],
        failure_type=g["failure_type"],
    )

    payload = {
        "group": {k: v for k, v in g.items() if k != "_id"},
        "failures": [{k: v for k, v in f.items() if k != "_id"} for f in failures],
    }
    return APIResponse(
        success=True,
        data=FailureGroupDetailResponse.model_validate(payload),
    )
