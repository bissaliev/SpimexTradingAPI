import operator
from datetime import date
from typing import Any

import pytest
from httpx import AsyncClient


@pytest.mark.usefixtures("test_redis_cache", "test_database_engine", "populate_test_database")
class TestAPI:
    """Тесты для API торговой системы."""

    async def test_get_last_trading_dates(self, async_client: AsyncClient):
        """Тестирует эндпоинт получения последних торговых дат"""
        response = await async_client.get("/trading/last_trading_dates")
        assert response.status_code == 200
        assert len(response.json()["dates"]) == 3

    async def test_get_trading_results(self, async_client: AsyncClient):
        """Тестирует эндпоинт получения последних торгов"""
        response = await async_client.get("/trading/trading_results")
        assert response.status_code == 200
        assert len(response.json()) == 3

    async def test_dynamics(self, async_client: AsyncClient):
        """Тестирует эндпоинт получения последних торгов"""
        response = await async_client.get("/trading/dynamics")
        assert response.status_code == 200
        assert len(response.json()) == 3

    @pytest.mark.parametrize(
        "field",
        ("oil_id", "delivery_type_id", "delivery_basis_id"),
    )
    async def test_trading_results_filter(
        self, async_client: AsyncClient, trading_data: list[dict[str, Any]], field: str
    ):
        """Тестирует эндпоинт получения последних торгов с фильтрацией по определенным полям"""
        filter_value = trading_data[0][field]
        response = await async_client.get(f"/trading/trading_results?{field}={filter_value}")
        assert response.status_code == 200
        assert len(response.json()) == 1
        assert response.json()[0][field] == filter_value

    @pytest.mark.parametrize(
        "field",
        ("oil_id", "delivery_type_id", "delivery_basis_id"),
    )
    async def test_dynamics_filters(self, async_client: AsyncClient, field: str, trading_data: list[dict[str, Any]]):
        """Тестирует эндпоинт получения последних торгов с фильтрацией по определенным полям"""
        obj = trading_data[0]
        value = obj[field]
        response = await async_client.get(f"trading/dynamics?{field}={value}")
        assert response.status_code == 200
        assert len(response.json()) == 1
        response_obj = response.json()[0]
        response_value = response_obj[field]
        assert response_value == value

    @pytest.mark.parametrize(
        "field, operator",
        (
            ("start_date", operator.ge),
            ("end_date", operator.le),
        ),
    )
    async def test_filter_by_date(
        self, async_client: AsyncClient, field: str, operator, trading_data: list[dict[str, Any]]
    ):
        """Тестирует эндпоинт получения последних торгов с фильтрацией по дате торгов"""
        obj = trading_data[0]
        expected = sorted(
            [i for i in trading_data if operator(i["date"], obj["date"])], key=lambda x: x["date"], reverse=True
        )
        response = await async_client.get(f"trading/dynamics?{field}={obj['date']}")
        assert response.status_code == 200
        assert len(response.json()) == len(expected)
        assert operator(date.fromisoformat(response.json()[0]["date"]), obj["date"])

    @pytest.mark.parametrize(
        "field",
        ("oil_id", "delivery_type_id", "delivery_basis_id"),
    )
    async def test_trading_results_filter_with_invalid_params(self, async_client: AsyncClient, field: str):
        """Тестирует эндпоинт получения последних торгов с фильтрацией по не валидными значениями"""
        filter_value = ""
        response = await async_client.get(f"/trading/trading_results?{field}={filter_value}")
        assert response.status_code == 422

    @pytest.mark.parametrize(
        "field, non_existent_data",
        (("oil_id", "X101"), ("delivery_type_id", "X"), ("delivery_basis_id", "NOT")),
    )
    async def test_trading_results_filter_with_non_existent_data(
        self, async_client: AsyncClient, field: str, non_existent_data: str
    ):
        """
        Тестирует эндпоинт получения последних торгов с фильтрацией по несуществующим данным возвращает пустой список
        """
        response = await async_client.get(f"/trading/trading_results?{field}={non_existent_data}")
        assert response.status_code == 200
        assert len(response.json()) == 0
