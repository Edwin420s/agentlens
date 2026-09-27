from app.db import mongo
from app.db.repositories.base import serialize


async def insert_analysis(doc: dict) -> None:
    await mongo.col_ai_analysis().insert_one(doc)


async def get_analysis(analysis_id: str) -> dict | None:
    doc = await mongo.col_ai_analysis().find_one({"analysis_id": analysis_id})
    return serialize(doc) if doc else None


async def get_analysis_for_session(session_id: str) -> dict | None:
    doc = await mongo.col_ai_analysis().find_one({"session_id": session_id})
    return serialize(doc) if doc else None


async def get_analysis_for_group(group_id: str) -> dict | None:
    doc = await mongo.col_ai_analysis().find_one({"group_id": group_id})
    return serialize(doc) if doc else None


async def list_analyses_for_investigation(investigation_id: str) -> list[dict]:
    cursor = mongo.col_ai_analysis().find({"investigation_id": investigation_id})
    return [serialize(d) async for d in cursor]
