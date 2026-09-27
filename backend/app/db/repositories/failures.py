from app.db import mongo
from app.db.repositories.base import serialize


async def bulk_insert_failures(docs: list[dict]) -> None:
    if docs:
        await mongo.col_failures().insert_many(docs, ordered=False)


async def get_failure(failure_id: str) -> dict | None:
    doc = await mongo.col_failures().find_one({"failure_id": failure_id})
    return serialize(doc) if doc else None


async def list_failures(investigation_id: str, failure_type: str | None = None,
                        severity: str | None = None, status: str | None = None,
                        limit: int = 50, offset: int = 0) -> list[dict]:
    q: dict = {"investigation_id": investigation_id}
    if failure_type: q["failure_type"] = failure_type
    if severity: q["severity"] = severity
    if status: q["status"] = status
    cursor = (mongo.col_failures().find(q)
              .sort("created_at", -1).skip(offset).limit(limit))
    return [serialize(d) async for d in cursor]


async def list_failures_for_session(session_id: str) -> list[dict]:
    cursor = mongo.col_failures().find({"session_id": session_id})
    return [serialize(d) async for d in cursor]


async def list_all_failures(investigation_id: str) -> list[dict]:
    cursor = mongo.col_failures().find({"investigation_id": investigation_id})
    return [serialize(d) async for d in cursor]


async def update_failure(failure_id: str, updates: dict) -> None:
    await mongo.col_failures().update_one(
        {"failure_id": failure_id}, {"$set": updates}
    )
