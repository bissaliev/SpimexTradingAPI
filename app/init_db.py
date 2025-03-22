import asyncio

from configs.logging_config import logger

from database.database import BaseModel, engine
from database.models import SpimexTradingResults  # noqa: F401

logger.info(f"Инициализация БД с таблицами: {BaseModel.metadata.tables.keys()}")


async def init_db():
    async with engine.begin() as conn:
        await conn.run_sync(BaseModel.metadata.create_all)


if __name__ == "__main__":
    asyncio.run(init_db())
