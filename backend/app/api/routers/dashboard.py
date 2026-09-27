from fastapi import APIRouter

from app.exceptions import NotFoundError
from app.schemas.common import APIResponse
from app.services.dashboard_service import build_dashboard

router = APIRouter()


@router.get("/investigations/{investigation_id}/dashboard")
async def get_dashboard(investigation_id: str):
    result = await build_dashboard(investigation_id)
    if not result:
        raise NotFoundError(f"Investigation {investigation_id} not found.")
    return APIResponse(success=True, data=result)
