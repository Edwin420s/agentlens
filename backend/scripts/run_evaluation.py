import asyncio
import sys

from app.db.mongo import connect_to_mongo, close_mongo_connection
from app.services.evaluation import evaluate_investigation


async def main():
    if len(sys.argv) < 2:
        print("Usage: python -m scripts.run_evaluation <INVESTIGATION_ID>")
        return
    await connect_to_mongo()
    result = await evaluate_investigation(sys.argv[1])
    print(result)
    await close_mongo_connection()


if __name__ == "__main__":
    asyncio.run(main())
