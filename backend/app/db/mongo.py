import logging
from motor.motor_asyncio import AsyncIOMotorClient, AsyncIOMotorDatabase

from app.config import get_settings

logger = logging.getLogger(__name__)

_client: AsyncIOMotorClient | None = None
_db: AsyncIOMotorDatabase | None = None


async def connect_to_mongo() -> None:
    global _client, _db
    settings = get_settings()
    _client = AsyncIOMotorClient(
        settings.mongo_uri,
        uuidRepresentation="standard",
        tz_aware=True,
    )
    _db = _client[settings.mongo_db_name]
    await _client.admin.command("ping")
    logger.info("Connected to MongoDB: %s", settings.mongo_db_name)


async def close_mongo_connection() -> None:
    global _client
    if _client is not None:
        _client.close()
        logger.info("Closed MongoDB connection.")


def get_database() -> AsyncIOMotorDatabase:
    if _db is None:
        raise RuntimeError("Database not initialized. Call connect_to_mongo().")
    return _db


# collections
def col_investigations(): return get_database()["investigations"]
def col_datasets(): return get_database()["datasets"]
def col_sessions(): return get_database()["sessions"]
def col_events(): return get_database()["events"]
def col_failures(): return get_database()["failures"]
def col_failure_groups(): return get_database()["failure_groups"]
def col_ai_analysis(): return get_database()["ai_analysis"]
def col_counters(): return get_database()["counters"]
def col_evaluation_labels(): return get_database()["evaluation_labels"]
