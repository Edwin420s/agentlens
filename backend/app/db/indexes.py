import logging
from pymongo import ASCENDING, DESCENDING, IndexModel

from app.db import mongo

logger = logging.getLogger(__name__)


async def _cleanup_legacy_indexes() -> None:
    """Drop legacy indexes whose uniqueness specs conflict with multi-tenant compound indexes."""
    legacy_specs = [
        (mongo.col_sessions(), ["session_id_1"]),
        (mongo.col_events(), ["event_id_1", "session_id_1_sequence_1"]),
        (mongo.col_evaluation_labels(), ["session_id_1"]),
    ]
    for col, index_names in legacy_specs:
        try:
            info = await col.index_information()
            for idx_name in index_names:
                if idx_name in info and info[idx_name].get("unique"):
                    logger.info("Dropping legacy unique index '%s' on '%s'", idx_name, col.name)
                    await col.drop_index(idx_name)
        except Exception as e:
            logger.debug("Legacy index cleanup check skipped for %s: %s", col.name, e)


async def ensure_indexes() -> None:
    await _cleanup_legacy_indexes()
    await mongo.col_investigations().create_indexes([
        IndexModel([("investigation_id", ASCENDING)], unique=True),
        IndexModel([("status", ASCENDING)]),
        IndexModel([("created_at", DESCENDING)]),
    ])
    await mongo.col_datasets().create_indexes([
        IndexModel([("dataset_name", ASCENDING), ("dataset_version", ASCENDING)], unique=True),
    ])
    await mongo.col_sessions().create_indexes([
        IndexModel([("investigation_id", ASCENDING), ("session_id", ASCENDING)], unique=True),
        IndexModel([("session_id", ASCENDING)]),
        IndexModel([("investigation_id", ASCENDING)]),
        IndexModel([("session_status", ASCENDING)]),
        IndexModel([("investigation_id", ASCENDING), ("session_status", ASCENDING)]),
    ])
    await mongo.col_events().create_indexes([
        IndexModel([("investigation_id", ASCENDING), ("event_id", ASCENDING)], unique=True),
        IndexModel([("investigation_id", ASCENDING), ("session_id", ASCENDING), ("sequence", ASCENDING)], unique=True),
        IndexModel([("session_id", ASCENDING)]),
        IndexModel([("event_id", ASCENDING)]),
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
        IndexModel([("investigation_id", ASCENDING), ("session_id", ASCENDING)], unique=True),
        IndexModel([("investigation_id", ASCENDING)]),
    ])
    logger.info("Indexes ensured.")
