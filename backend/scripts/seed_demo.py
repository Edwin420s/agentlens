import asyncio
import json
from pathlib import Path

from app.schemas.datasets import DatasetImport
from app.services.ingestion import import_dataset
from app.db.mongo import connect_to_mongo, close_mongo_connection


async def main():
    await connect_to_mongo()
    data_dir = Path(__file__).parent.parent / "data"
    path = data_dir / "agentlens_demo.json"
    if not path.exists():
        path = data_dir / "demo_dataset.json"

    payload = json.loads(path.read_text(encoding="utf-8"))
    dataset = DatasetImport.model_validate(payload)
    result = await import_dataset(dataset)
    print("Seeded:", result)
    await close_mongo_connection()


if __name__ == "__main__":
    asyncio.run(main())
