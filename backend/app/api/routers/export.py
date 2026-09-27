from fastapi import APIRouter, Query, Response

from app.schemas.common import APIResponse
from app.services.export_service import export_investigation, export_investigation_csv

router = APIRouter()


@router.get("/investigations/{investigation_id}/export")
async def export_route(
    investigation_id: str,
    format: str = Query(default="json"),
):
    if format.lower() == "csv":
        csv_text = await export_investigation_csv(investigation_id)
        return Response(
            content=csv_text,
            media_type="text/csv",
            headers={"Content-Disposition": f'attachment; filename="{investigation_id}_export.csv"'},
        )

    result = await export_investigation(investigation_id, format)
    return APIResponse(success=True, data=result)
