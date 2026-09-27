from pymongo import ReturnDocument

from app.db import mongo


async def next_sequence(name: str, start: int = 1) -> int:
    doc = await mongo.col_counters().find_one_and_update(
        {"_id": name},
        {"$inc": {"value": 1}, "$setOnInsert": {"start": start}},
        upsert=True,
        return_document=ReturnDocument.AFTER,
    )
    return doc["value"]


async def format_id(prefix: str, name: str, width: int) -> str:
    n = await next_sequence(name)
    return f"{prefix}-{n:0{width}d}"
