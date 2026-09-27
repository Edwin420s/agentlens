from app.db import mongo
from app.db.repositories.base import serialize


async def insert_session(doc: dict) -> None:
    await mongo.col_sessions().insert_one(doc)


async def bulk_insert_sessions(docs: list[dict]) -> None:
    if docs:
        await mongo.col_sessions().insert_many(docs, ordered=False)


async def get_session(session_id: str, investigation_id: str | None = None) -> dict | None:
    q: dict = {"session_id": session_id}
    if investigation_id:
        q["investigation_id"] = investigation_id
    doc = await mongo.col_sessions().find_one(q, sort=[("_id", -1)])
    return serialize(doc) if doc else None


async def list_sessions(investigation_id: str, status: str | None = None,
                        limit: int = 50, offset: int = 0) -> list[dict]:
    q: dict = {"investigation_id": investigation_id}
    if status:
        q["session_status"] = status
    cursor = (mongo.col_sessions().find(q)
              .sort("started_at", 1).skip(offset).limit(limit))
    return [serialize(d) async for d in cursor]


async def count_sessions(investigation_id: str) -> int:
    return await mongo.col_sessions().count_documents(
        {"investigation_id": investigation_id}
    )


async def update_session(session_id: str, updates: dict, investigation_id: str | None = None) -> None:
    q: dict = {"session_id": session_id}
    if investigation_id:
        q["investigation_id"] = investigation_id
    await mongo.col_sessions().update_many(q, {"$set": updates})


async def iter_sessions(investigation_id: str):
    cursor = mongo.col_sessions().find(
        {"investigation_id": investigation_id}
    ).sort("started_at", 1)
    async for d in cursor:
        yield serialize(d)
