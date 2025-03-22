from sqlalchemy import insert
from sqlalchemy.ext.asyncio import AsyncSession

from database.database import async_context_session
from database.models import SpimexTradingResults


@async_context_session
async def mass_create_trade(session: AsyncSession, lst_data: list[dict]) -> None:
    """Выполняет массовую вставку данных в таблицу `SpimexTradingResults`"""
    await session.execute(insert(SpimexTradingResults), lst_data)
