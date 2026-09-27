from fastapi import APIRouter, Depends

from app.db.repositories import investigations as inv_repo
from app.exceptions import NotFoundError
from app.schemas.common import APIResponse
from app.schemas.datasets import DatasetImport
from app.schemas.investigations import CreateInvestigationRequest, InvestigationResponse
from app.services.ingestion import import_dataset
from app.api.deps import Pagination, pagination

router = APIRouter()


@router.post("/investigations")
async def create_investigation_route(payload: CreateInvestigationRequest):
    doc = await inv_repo.create_investigation(
        name=payload.name,
        description=payload.description,
        dataset_name=payload.dataset_name,
        dataset_version="1.0",
    )
    return APIResponse(
        success=True,
        data=InvestigationResponse.model_validate({k: v for k, v in doc.items() if k != "_id"}),
    )


@router.get("/investigations")
async def list_investigations(p: Pagination = Depends(pagination)):
    docs = await inv_repo.list_investigations(p.limit, p.offset)
    data = [
        InvestigationResponse.model_validate({k: v for k, v in d.items() if k != "_id"})
        for d in docs
    ]
    return APIResponse(success=True, data=data)


@router.get("/investigations/{investigation_id}")
async def get_investigation(investigation_id: str):
    doc = await inv_repo.get_investigation(investigation_id)
    if not doc:
        raise NotFoundError(f"Investigation {investigation_id} not found.")
    return APIResponse(
        success=True,
        data=InvestigationResponse.model_validate({k: v for k, v in doc.items() if k != "_id"}),
    )


@router.get("/investigations/{investigation_id}/evaluation")
async def get_evaluation(investigation_id: str):
    from app.services.evaluation import evaluate_investigation
    result = await evaluate_investigation(investigation_id)
    return APIResponse(success=True, data=result)


@router.post("/investigations/{investigation_id}/dataset")
async def attach_dataset_to_investigation(investigation_id: str, payload: DatasetImport):
    inv = await inv_repo.get_investigation(investigation_id)
    if not inv:
        raise NotFoundError(f"Investigation {investigation_id} not found.")
    result = await import_dataset(payload, target_investigation_id=investigation_id)
    return APIResponse(success=True, data=result)


@router.post("/investigations/{investigation_id}/analyze")
async def analyze_investigation(investigation_id: str):
    inv = await inv_repo.get_investigation(investigation_id)
    if not inv:
        raise NotFoundError(f"Investigation {investigation_id} not found.")
    return APIResponse(success=True, data={"investigation_id": investigation_id, "status": "completed"})
