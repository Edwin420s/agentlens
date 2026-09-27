from app.db import mongo
from app.db.repositories.base import serialize


async def bulk_insert_events(docs: list[dict]) -> None:
    if docs:
        await mongo.col_events().insert_many(docs, ordered=False)


async def list_events_for_session(session_id: str, investigation_id: str | None = None) -> list[dict]:
    q: dict = {"session_id": session_id}
    if investigation_id:
        q["investigation_id"] = investigation_id
    cursor = mongo.col_events().find(q).sort("sequence", 1)
    return [serialize(d) async for d in cursor]


async def get_events_by_ids(event_ids: list[str], investigation_id: str | None = None) -> list[dict]:
    q: dict = {"event_id": {"$in": event_ids}}
    if investigation_id:
        q["investigation_id"] = investigation_id
    cursor = mongo.col_events().find(q)
    return [serialize(d) async for d in cursor]
