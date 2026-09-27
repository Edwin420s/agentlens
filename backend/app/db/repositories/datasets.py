from datetime import datetime, timezone

from app.db import mongo
from app.db.repositories.base import serialize


async def save_dataset_record(dataset_name: str, dataset_version: str,
                              description: str | None, session_count: int) -> dict:
    doc = {
        "dataset_name": dataset_name,
        "dataset_version": dataset_version,
        "description": description,
        "session_count": session_count,
        "imported_at": datetime.now(timezone.utc),
    }
    await mongo.col_datasets().update_one(
        {"dataset_name": dataset_name, "dataset_version": dataset_version},
        {"$set": doc},
        upsert=True,
    )
    return serialize(doc)


async def get_dataset(dataset_name: str, dataset_version: str) -> dict | None:
    doc = await mongo.col_datasets().find_one(
        {"dataset_name": dataset_name, "dataset_version": dataset_version}
    )
    return serialize(doc) if doc else None


async def list_datasets() -> list[dict]:
    cursor = mongo.col_datasets().find().sort("imported_at", -1)
    return [serialize(d) async for d in cursor]
