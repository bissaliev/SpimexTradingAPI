import operator
from datetime import date
from unittest.mock import Mock

import pytest
from services.tradings import TradingService
from sqlalchemy import insert, select
from sqlalchemy.exc import SQLAlchemyError
from tests.test_data import tradings

from database.models import SpimexTradingResults


@pytest.mark.usefixtures("test_cache")
class TestTradingServiceRead:
    async def test_get_last_dates2(self, mock_session):
        trading_service = TradingService(mock_session)
        mock_result = Mock()
        mock_result.all.return_value = [date(2025, 3, 31), date(2025, 3, 30), date(2025, 3, 29)]
        mock_session.scalars.return_value = mock_result
        test_dates = [date(2025, 3, 31), date(2025, 3, 30), date(2025, 3, 29)]
        # Настраиваем поведение scalars
        result = await trading_service.get_last_dates()
        # Проверяем результат
        assert result == test_dates
        assert mock_session.scalars.call_count == 1
        assert mock_result.all.call_count == 1
        expected_stmt = (
            select(SpimexTradingResults.date).distinct().order_by(SpimexTradingResults.date.desc()).offset(0).limit(10)
        )
        actual_call = mock_session.scalars.call_args[0][0]
        assert str(actual_call) == str(expected_stmt)

    async def test_filter(self, fixtures, mock_session):
        """Проверка метода get_last_dates"""
        mock_result = Mock()
        mock_result.all.return_value = fixtures
        mock_session.scalars.return_value = mock_result
        trading_service = TradingService(mock_session)
        response = await trading_service.filter()
        assert len(response) == len(fixtures)
        assert mock_session.scalars.call_count == 1
        assert mock_result.all.call_count == 1
        expected_stmt = select(SpimexTradingResults).limit(10).offset(0)
        actual_stmt = mock_session.scalars.call_args[0][0]
        assert str(expected_stmt) == str(actual_stmt)

    @pytest.mark.parametrize(
        "field, value, expected",
        (
            ("oil_id", tradings[0]["oil_id"], [tradings[0]]),
            ("delivery_basis_id", tradings[0]["delivery_basis_id"], [tradings[0]]),
            ("delivery_type_id", tradings[0]["delivery_type_id"], [tradings[0]]),
        ),
    )
    async def test_method_filter_with_params(self, mock_session, field, value, expected):
        mock_result = Mock()
        mock_result.all.return_value = expected
        mock_session.scalars.return_value = mock_result
        service = TradingService(mock_session)
        response = await service.filter(**{field: value})
        assert len(response) == 1
        assert mock_session.scalars.call_count == 1
        assert mock_result.all.call_count == 1
        expected_stmt = (
            select(SpimexTradingResults).where(getattr(SpimexTradingResults, field) == value).limit(10).offset(0)
        )
        actual_stmt = mock_session.scalars.call_args[0][0]
        assert str(expected_stmt) == str(actual_stmt)

    @pytest.mark.parametrize(
        "field, operator, index",
        (
            ("start_date", operator.ge, 0),
            ("end_date", operator.le, 0),
        ),
    )
    async def test_method_filter_by_date(self, mock_session, field, operator, index, fixtures):
        mock_result = Mock()
        obj = fixtures[index]
        expected = sorted([i for i in fixtures if operator(obj["date"], i["date"])], key=lambda x: x["date"])
        print(fixtures)
        mock_result.all.return_value = expected
        mock_session.scalars.return_value = mock_result
        service = TradingService(mock_session)
        response = await service.filter(**{field: obj["date"]})
        assert len(response) == len(expected)
        assert mock_session.scalars.call_count == 1
        assert mock_result.all.call_count == 1
        expected_stmt = (
            select(SpimexTradingResults).where(operator(SpimexTradingResults.date, obj["date"])).limit(10).offset(0)
        )
        actual_stmt = mock_session.scalars.call_args[0][0]
        assert str(expected_stmt) == str(actual_stmt)

    @pytest.mark.parametrize(
        "field, value",
        (
            ("oil_id", 1111),
            ("delivery_basis_id", 1111),
            ("delivery_type_id", 1111),
            ("start_date", "2000-12-12"),
            ("end_date", "2000-12-12"),
        ),
    )
    async def test_method_filter_with_invalid_params(self, mock_session, field, value):
        # mock_result.all.return_value = expected
        mock_session.scalars.side_effect = SQLAlchemyError()
        service = TradingService(mock_session)
        with pytest.raises(SQLAlchemyError):
            await service.filter(**{field: value})
        assert mock_session.scalars.call_count == 1


class TestTradingServiceWrite:
    """Тестирование сохранения данных в БД сервисов TradingService"""

    async def test_method_mass_create_trading(self, mock_session, fixtures):
        trading_service = TradingService(mock_session)
        await trading_service.mass_create_trading(fixtures)

        # Проверяем, что execute был вызван один раз с правильными аргументами
        assert mock_session.execute.call_count == 1
        expected_call = insert(SpimexTradingResults)
        actual_call_args = mock_session.execute.call_args

        # Проверяем, что первый аргумент — это insert(SpimexTradingResults)
        assert str(actual_call_args[0][0]) == str(expected_call)
