import asyncio
import os
import pytest

os.environ.setdefault("MONGO_DB_NAME", "agentlens_test")


@pytest.fixture(autouse=True, scope="function")
def clean_test_db():
    from pymongo import MongoClient
    client = MongoClient("mongodb://localhost:27017")
    db = client[os.environ["MONGO_DB_NAME"]]
    for name in [
        "investigations", "datasets", "sessions", "events",
        "failures", "failure_groups", "ai_analysis", "counters",
        "evaluation_labels",
    ]:
        db[name].delete_many({})
    client.close()
    yield
