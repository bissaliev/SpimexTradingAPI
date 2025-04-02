import operator
from datetime import date
from typing import Any

import pytest
from services.tradings import TradingService
from sqlalchemy import func, insert, select
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.ext.asyncio import AsyncSession

from database.models import SpimexTradingResults


@pytest.mark.usefixtures("populate_test_database", "test_redis_cache")
class TestTradingServiceRead:
    """Тестирование чтения данных из БД сервисов TradingService"""

    async def test_get_last_dates(self, session: AsyncSession, trading_data: list[dict[str, Any]]):
        """Тест получения самых последних торговых дат из базы данных"""
        service = TradingService(session)
        response = await service.get_last_dates()
        assert len(response) == len(trading_data)
        assert response == sorted([obj["date"] for obj in trading_data], reverse=True)

    async def test_fetch_all_trading_results(self, session: AsyncSession, trading_data):
        """Тест получения всех торговых результатов без фильтров"""
        service = TradingService(session)
        response = await service.filter()
        assert len(response) == len(trading_data)

    async def test_filter_with_limit_and_offset(self, session: AsyncSession, trading_data: list[dict[str, Any]]):
        """Тест фильтрации торговых результатов с параметрами limit и offset"""
        limit = 1
        offset = len(trading_data) - limit
        service = TradingService(session)
        response = await service.filter(limit=limit, offset=offset)
        assert len(response) == 1
        assert len(trading_data) > limit

    @pytest.mark.parametrize(
        "field",
        ("oil_id", "delivery_basis_id", "delivery_type_id"),
    )
    async def test_method_filter_with_params(
        self, session: AsyncSession, field: str, trading_data: list[dict[str, Any]]
    ):
        """Тест фильтрации торговых результатов по определенным полям (например, oil_id)"""
        obj = trading_data[0]
        query = obj[field]
        service = TradingService(session)
        response = await service.filter(**{field: query})
        assert len(response) == 1

    @pytest.mark.parametrize(
        "field, operator",
        (
            ("start_date", operator.ge),
            ("end_date", operator.le),
        ),
    )
    async def test_filter_by_date(
        self, session: AsyncSession, field: str, operator, trading_data: list[dict[str, Any]]
    ):
        """Тест фильтрации торговых результатов по полям даты (start_date или end_date)"""
        obj = trading_data[0]
        query_param = obj["date"]
        service = TradingService(session)
        response = await service.filter(**{field: query_param})
        assert len(response) == len([i for i in trading_data if operator(i["date"], query_param)])
        assert operator(response[0].date, query_param)

    @pytest.mark.parametrize(
        "field, value, exception",
        (
            ("oil_id", 1111, SQLAlchemyError),
            ("delivery_basis_id", 1111, SQLAlchemyError),
            ("delivery_type_id", 1111, SQLAlchemyError),
            ("start_date", "2000-12-12", SQLAlchemyError),
            ("end_date", "2000-12-12", SQLAlchemyError),
            ("limit", "non number", ValueError),
            ("offset", "non number", ValueError),
        ),
    )
    async def test_filter_with_invalid_params(
        self, session: AsyncSession, field: str, value: Any, exception: type[Exception]
    ):
        """Тест невалидные данные вызывают определенное исключение"""
        with pytest.raises(exception):
            service = TradingService(session)
            await service.filter(**{field: value})

    async def test_cache_functionality(self, session: AsyncSession):
        """Тест функциональности кеша: данные должны возвращаться из кеша после первого запроса"""
        new_data = [
            {
                "exchange_product_id": "B111NVL060D",
                "exchange_product_name": "Бензин (АИ-100-К5)",
                "oil_id": "B111",
                "delivery_basis_id": "NVL",
                "delivery_basis_name": "ст. Новоярославская",
                "delivery_type_id": "H",
                "volume": 61,
                "total": 5997121.00,
                "count": 2,
                "date": date(2024, 8, 7),
            },
        ]
        service = TradingService(session)
        result_1 = await service.get_last_dates()
        await session.execute(insert(SpimexTradingResults), new_data)
        await session.commit()
        result_2 = await service.get_last_dates()
        assert len(result_1) == len(result_2)
        count_in_db = await session.scalar(select(func.count()).select_from(SpimexTradingResults))
        assert count_in_db == len(result_2) + 1


class TestTradingServiceWrite:
    """Тестирование сохранения данных в БД сервисов TradingService"""

    async def test_method_mass_create_trading(self, session: AsyncSession, trading_data: list[dict[str, Any]]):
        count = await session.scalar(select(func.count()).select_from(SpimexTradingResults))
        assert count == 0
        service = TradingService(session)
        await service.mass_create_trading(trading_data)
        await session.commit()
        update_count = await session.scalar(select(func.count()).select_from(SpimexTradingResults))
        assert update_count == len(trading_data)

    @pytest.mark.parametrize(
        "field",
        (
            "exchange_product_id",
            "exchange_product_name",
            "oil_id",
            "delivery_basis_id",
            "delivery_basis_name",
            "delivery_type_id",
            "volume",
            "total",
            "count",
            "date",
        ),
    )
    async def test_method_mass_create_trading_with_invalid_data(
        self, session: AsyncSession, trading_data: list[dict[str, Any]], field: str
    ):
        service = TradingService(session)
        invalid_data = trading_data[0].copy()
        invalid_data[field] = 11111 if isinstance(invalid_data[field], str) else "invalid"
        with pytest.raises(SQLAlchemyError):
            await service.mass_create_trading(invalid_data)
            await session.commit()
