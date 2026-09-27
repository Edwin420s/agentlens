from fastapi import APIRouter

from app.db.repositories import datasets as ds_repo
from app.schemas.common import APIResponse
from app.schemas.datasets import DatasetImport
from app.services.ingestion import import_dataset

router = APIRouter()


@router.post("/datasets/import")
async def import_dataset_route(payload: DatasetImport):
    result = await import_dataset(payload)
    return APIResponse(success=True, data=result)


@router.get("/datasets")
async def list_datasets():
    docs = await ds_repo.list_datasets()
    return APIResponse(success=True, data=[
        {k: v for k, v in d.items() if k != "_id"} for d in docs
    ])
