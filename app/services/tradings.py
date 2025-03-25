from fastapi_cache.decorator import cache
from sqlalchemy import insert, select
from sqlalchemy.ext.asyncio import AsyncSession

from database.models import SpimexTradingResults
from utils.redis_client import get_expiries


class TradingService:
    def __init__(self, session: AsyncSession):
        self.session = session
        self.model = SpimexTradingResults

    @cache(expire=get_expiries())
    async def get_last_dates(self, offset: int = 0, limit: int = 10):
        async with self.session as session:
            stmt = select(self.model.date).distinct().order_by(self.model.date.desc()).offset(offset).limit(limit)
            results = await session.scalars(stmt)
            return results.all()

    @cache(expire=get_expiries())
    async def filter(self, **filters: dict):
        async with self.session as session:
            limit = filters.get("limit", 10)
            offset = filters.get("offset", 0)
            stmt = select(self.model)
            oil_id = filters.get("oil_id")
            delivery_type_id = filters.get("delivery_type_id")
            delivery_basis_id = filters.get("delivery_basis_id")
            start_date = filters.get("start_date")
            end_date = filters.get("end_date")
            if oil_id:
                stmt = stmt.where(self.model.oil_id == oil_id)
            if delivery_type_id:
                stmt = stmt.where(self.model.delivery_type_id == delivery_type_id)
            if delivery_basis_id:
                stmt = stmt.where(self.model.delivery_basis_id == delivery_basis_id)
            if start_date:
                stmt = stmt.where(self.model.date >= start_date)
            if end_date:
                stmt = stmt.where(self.model.date <= end_date)
            results = await session.scalars(stmt.limit(limit).offset(offset))
            return results.all()

    async def mass_create_trading(self, data: list[dict]):
        async with self.session as session:
            await session.execute(insert(SpimexTradingResults), data)
