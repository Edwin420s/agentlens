from fastapi import APIRouter

from app.schemas.ai_analysis import InvestigationAssistantRequest
from app.schemas.common import APIResponse
from app.services.investigation_assistant import ask

router = APIRouter()


@router.post("/investigations/{investigation_id}/assistant")
async def assistant_route(investigation_id: str, payload: InvestigationAssistantRequest):
    result = await ask(investigation_id, payload.question)
    return APIResponse(success=True, data=result)
