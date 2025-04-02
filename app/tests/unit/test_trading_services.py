import operator
from unittest.mock import Mock

import pytest
from services.tradings import TradingService
from sqlalchemy import insert, select
from sqlalchemy.exc import SQLAlchemyError

from database.models import SpimexTradingResults


@pytest.mark.usefixtures("test_cache")
class TestTradingServiceRead:
    trading_service = TradingService

    async def test_get_last_dates(self, mock_session, tradings_list):
        dates_list = [obj["date"] for obj in tradings_list]
        trading_service = self.trading_service(mock_session)
        mock_result = Mock()
        mock_result.all.return_value = dates_list
        # Настраиваем поведение scalars
        mock_session.scalars.return_value = mock_result
        result = await trading_service.get_last_dates()
        assert result == dates_list
        assert mock_session.scalars.call_count == 1
        assert mock_result.all.call_count == 1
        expected_stmt = (
            select(SpimexTradingResults.date).distinct().order_by(SpimexTradingResults.date.desc()).offset(0).limit(10)
        )
        actual_call = mock_session.scalars.call_args[0][0]
        assert str(actual_call) == str(expected_stmt)

    async def test_filter(self, tradings_list, mock_session):
        """Проверка метода get_last_dates"""
        mock_result = Mock()
        mock_result.all.return_value = tradings_list
        mock_session.scalars.return_value = mock_result
        trading_service = self.trading_service(mock_session)
        response = await trading_service.filter()
        assert len(response) == len(tradings_list)
        assert mock_session.scalars.call_count == 1
        assert mock_result.all.call_count == 1
        expected_stmt = select(SpimexTradingResults).limit(10).offset(0)
        actual_stmt = mock_session.scalars.call_args[0][0]
        assert str(expected_stmt) == str(actual_stmt)

    @pytest.mark.parametrize(
        "field",
        ("oil_id", "delivery_basis_id", "delivery_type_id"),
    )
    async def test_method_filter_with_params(self, mock_session, field, tradings_list):
        obj = tradings_list[0]
        query_data = obj[field]
        mock_result = Mock()
        mock_result.all.return_value = [obj]
        mock_session.scalars.return_value = mock_result
        service = self.trading_service(mock_session)
        response = await service.filter(**{field: query_data})
        assert len(response) == 1
        assert mock_session.scalars.call_count == 1
        assert mock_result.all.call_count == 1
        expected_stmt = (
            select(SpimexTradingResults).where(getattr(SpimexTradingResults, field) == query_data).limit(10).offset(0)
        )
        actual_stmt = mock_session.scalars.call_args[0][0]
        assert str(expected_stmt) == str(actual_stmt)

    @pytest.mark.parametrize(
        "field, operator",
        (
            ("start_date", operator.ge),
            ("end_date", operator.le),
        ),
    )
    async def test_method_filter_by_date(self, mock_session, field, operator, tradings_list):
        mock_result = Mock()
        obj = tradings_list[0]
        expected = sorted([i for i in tradings_list if operator(i["date"], obj["date"])], key=lambda x: x["date"])
        mock_result.all.return_value = expected
        mock_session.scalars.return_value = mock_result
        service = self.trading_service(mock_session)
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
        mock_session.scalars.side_effect = SQLAlchemyError()
        service = self.trading_service(mock_session)
        with pytest.raises(SQLAlchemyError):
            await service.filter(**{field: value})
        assert mock_session.scalars.call_count == 1


class TestTradingServiceWrite:
    """Тестирование сохранения данных в БД сервисов TradingService"""

    trading_service = TradingService

    async def test_method_mass_create_trading(self, mock_session, tradings_list):
        trading_service = self.trading_service(mock_session)
        await trading_service.mass_create_trading(tradings_list)

        # Проверяем, что execute был вызван один раз с правильными аргументами
        assert mock_session.execute.call_count == 1
        expected_call = insert(SpimexTradingResults)
        actual_call_args = mock_session.execute.call_args

        # Проверяем, что первый аргумент — это insert(SpimexTradingResults)
        assert str(actual_call_args[0][0]) == str(expected_call)
