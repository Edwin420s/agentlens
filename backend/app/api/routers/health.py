from fastapi import APIRouter
from app.db.mongo import get_database
from app.schemas.common import APIResponse

router = APIRouter()


@router.get("/health")
async def health():
    db = get_database()
    await db.command("ping")
    return APIResponse(success=True, data={"status": "ok"})
