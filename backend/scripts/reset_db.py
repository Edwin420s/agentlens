import asyncio
from app.db.mongo import connect_to_mongo, close_mongo_connection, get_database


async def main():
    await connect_to_mongo()
    db = get_database()
    for name in [
        "investigations", "datasets", "sessions", "events",
        "failures", "failure_groups", "ai_analysis", "counters",
        "evaluation_labels",
    ]:
        await db[name].delete_many({})
        print(f"cleared {name}")
    await close_mongo_connection()


if __name__ == "__main__":
    asyncio.run(main())
