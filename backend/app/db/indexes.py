import logging
from pymongo import ASCENDING, DESCENDING, IndexModel

from app.db import mongo

logger = logging.getLogger(__name__)


async def ensure_indexes() -> None:
    await mongo.col_investigations().create_indexes([
        IndexModel([("investigation_id", ASCENDING)], unique=True),
        IndexModel([("status", ASCENDING)]),
        IndexModel([("created_at", DESCENDING)]),
    ])
    await mongo.col_datasets().create_indexes([
        IndexModel([("dataset_name", ASCENDING), ("dataset_version", ASCENDING)], unique=True),
    ])
    await mongo.col_sessions().create_indexes([
        IndexModel([("session_id", ASCENDING)], unique=True),
        IndexModel([("investigation_id", ASCENDING)]),
        IndexModel([("session_status", ASCENDING)]),
        IndexModel([("investigation_id", ASCENDING), ("session_status", ASCENDING)]),
    ])
    await mongo.col_events().create_indexes([
        IndexModel([("event_id", ASCENDING)], unique=True),
        IndexModel([("session_id", ASCENDING), ("sequence", ASCENDING)], unique=True),
    ])
    await mongo.col_failures().create_indexes([
        IndexModel([("failure_id", ASCENDING)], unique=True),
        IndexModel([("investigation_id", ASCENDING)]),
        IndexModel([("session_id", ASCENDING)]),
        IndexModel([("failure_type", ASCENDING)]),
        IndexModel([("severity", ASCENDING)]),
        IndexModel([("status", ASCENDING)]),
    ])
    await mongo.col_failure_groups().create_indexes([
        IndexModel([("group_id", ASCENDING)], unique=True),
        IndexModel([("investigation_id", ASCENDING)]),
        IndexModel([("failure_type", ASCENDING)]),
    ])
    await mongo.col_ai_analysis().create_indexes([
        IndexModel([("analysis_id", ASCENDING)], unique=True),
        IndexModel([("investigation_id", ASCENDING)]),
        IndexModel([("session_id", ASCENDING)]),
        IndexModel([("group_id", ASCENDING)]),
    ])
    await mongo.col_evaluation_labels().create_indexes([
        IndexModel([("session_id", ASCENDING)], unique=True),
        IndexModel([("investigation_id", ASCENDING)]),
    ])
    logger.info("Indexes ensured.")
