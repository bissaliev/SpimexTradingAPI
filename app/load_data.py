import asyncio
import json
from datetime import datetime
from pathlib import Path

from sqlalchemy import insert

from database.database import AsyncSessionLocal
from database.models import SpimexTradingResults

filepath = Path(__file__).parent / "fixtures.json"


async def load_fixtures(filepath):
    async with AsyncSessionLocal() as session:
        with open(filepath, encoding="utf-8") as file:
            json_file = json.load(file)
            for row in json_file:
                date = row.pop("date")
                date = datetime.strptime(date, "%Y-%m-%d").date()
                query = insert(SpimexTradingResults).values(**row, date=date)
                await session.execute(query)
            await session.commit()


if __name__ == "__main__":
    asyncio.run(load_fixtures(filepath))
