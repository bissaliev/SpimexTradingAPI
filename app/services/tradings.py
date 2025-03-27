from datetime import date
from typing import Any

from fastapi_cache.decorator import cache
from sqlalchemy import insert, select
from sqlalchemy.ext.asyncio import AsyncSession

from database.models import SpimexTradingResults
from utils.redis_client import get_expiries


class TradingService:
    """
    Сервис для работы с торговыми результатами.
    """

    def __init__(self, session: AsyncSession):
        """
        Инициализирует сервис с асинхронной сессией базы данных.

        :param session: Асинхронная сессия SQLAlchemy.
        """
        self.session = session
        self.model = SpimexTradingResults

    @cache(expire=get_expiries())
    async def get_last_dates(self, offset: int = 0, limit: int = 10) -> list[date]:
        """
        Получает последние доступные даты торгов.

        :param offset: Смещение в выборке (по умолчанию 0).
        :param limit: Количество записей в выборке (по умолчанию 10).
        :return: Список последних дат торгов.
        """
        async with self.session as session:
            stmt = select(self.model.date).distinct().order_by(self.model.date.desc()).offset(offset).limit(limit)
            results = await session.scalars(stmt)
            return results.all()

    @cache(expire=get_expiries())
    async def filter(self, **filters: dict[str, Any]) -> list[SpimexTradingResults]:
        """
        Фильтрует торговые результаты на основе переданных параметров.

        :param filters: Словарь с фильтрами (
            oil_id, delivery_type_id, delivery_basis_id, start_date, end_date, limit, offset
        ).
        :return: Список отфильтрованных записей.
        """
        async with self.session as session:
            stmt = select(self.model)

            if oil_id := filters.get("oil_id"):
                stmt = stmt.where(self.model.oil_id == oil_id)
            if delivery_type_id := filters.get("delivery_type_id"):
                stmt = stmt.where(self.model.delivery_type_id == delivery_type_id)
            if delivery_basis_id := filters.get("delivery_basis_id"):
                stmt = stmt.where(self.model.delivery_basis_id == delivery_basis_id)
            if start_date := filters.get("start_date"):
                stmt = stmt.where(self.model.date >= start_date)
            if end_date := filters.get("end_date"):
                stmt = stmt.where(self.model.date <= end_date)

            limit = filters.get("limit", 10)
            offset = filters.get("offset", 0)
            results = await session.scalars(stmt.limit(limit).offset(offset))
            return results.all()

    async def mass_create_trading(self, data: list[dict]) -> None:
        """
        Массово создает записи в таблице торговых результатов.

        :param data: Список словарей с данными для вставки.
        """
        async with self.session as session:
            await session.execute(insert(SpimexTradingResults), data)
