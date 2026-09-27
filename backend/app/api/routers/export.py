from fastapi import APIRouter, Query

from app.schemas.common import APIResponse
from app.services.export_service import export_investigation

router = APIRouter()


@router.get("/investigations/{investigation_id}/export")
async def export_route(
    investigation_id: str,
    format: str = Query(default="json"),
):
    result = await export_investigation(investigation_id, format)
    return APIResponse(success=True, data=result)
