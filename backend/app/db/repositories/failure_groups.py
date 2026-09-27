from app.db import mongo
from app.db.repositories.base import serialize


async def insert_group(doc: dict) -> None:
    await mongo.col_failure_groups().insert_one(doc)


async def get_group(group_id: str) -> dict | None:
    doc = await mongo.col_failure_groups().find_one({"group_id": group_id})
    return serialize(doc) if doc else None


async def list_groups(investigation_id: str) -> list[dict]:
    cursor = mongo.col_failure_groups().find(
        {"investigation_id": investigation_id}
    ).sort("occurrence_count", -1)
    return [serialize(d) async for d in cursor]


async def delete_groups_for_investigation(investigation_id: str) -> None:
    await mongo.col_failure_groups().delete_many(
        {"investigation_id": investigation_id}
    )
