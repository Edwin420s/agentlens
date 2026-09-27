from app.db import mongo
from app.db.repositories.base import serialize


async def bulk_insert_events(docs: list[dict]) -> None:
    if docs:
        await mongo.col_events().insert_many(docs, ordered=False)


async def list_events_for_session(session_id: str) -> list[dict]:
    cursor = mongo.col_events().find(
        {"session_id": session_id}
    ).sort("sequence", 1)
    return [serialize(d) async for d in cursor]


async def get_events_by_ids(event_ids: list[str]) -> list[dict]:
    cursor = mongo.col_events().find({"event_id": {"$in": event_ids}})
    return [serialize(d) async for d in cursor]
