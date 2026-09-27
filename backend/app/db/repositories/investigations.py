from datetime import datetime, timezone

from app.db import mongo
from app.db.repositories.base import serialize
from app.db.repositories.counters import format_id


async def create_investigation(name: str, description: str | None,
                               dataset_name: str, dataset_version: str) -> dict:
    inv_id = await format_id("INV", "investigations", 4)
    doc = {
        "investigation_id": inv_id,
        "name": name,
        "description": description,
        "dataset_name": dataset_name,
        "dataset_version": dataset_version,
        "status": "pending",
        "total_sessions": 0,
        "successful_sessions": 0,
        "failed_sessions": 0,
        "ambiguous_sessions": 0,
        "failure_count": 0,
        "failure_group_count": 0,
        "created_at": datetime.now(timezone.utc),
        "completed_at": None,
    }
    await mongo.col_investigations().insert_one(doc)
    return serialize(doc)


async def get_investigation(inv_id: str) -> dict | None:
    doc = await mongo.col_investigations().find_one({"investigation_id": inv_id})
    return serialize(doc) if doc else None


async def list_investigations(limit: int = 50, offset: int = 0) -> list[dict]:
    cursor = (mongo.col_investigations()
              .find()
              .sort("created_at", -1)
              .skip(offset)
              .limit(limit))
    return [serialize(d) async for d in cursor]


async def update_investigation(inv_id: str, updates: dict) -> None:
    await mongo.col_investigations().update_one(
        {"investigation_id": inv_id}, {"$set": updates}
    )


async def bump_counters(inv_id: str, delta: dict) -> None:
    inc = {k: v for k, v in delta.items() if v}
    if inc:
        await mongo.col_investigations().update_one(
            {"investigation_id": inv_id}, {"$inc": inc}
        )
