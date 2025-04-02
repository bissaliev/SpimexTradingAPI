import operator
from typing import Any
from unittest.mock import AsyncMock

import pytest
from fastapi.testclient import TestClient


class TestEndpoints:
    """Тесты для API эндпоинтов, связанных с торговыми операциями."""

    def test_get_last_trading_dates(
        self, client: TestClient, mock_trading_service: AsyncMock, trading_data_with_id: list[dict[str, Any]]
    ):
        """Проверяет, что эндпоинт `/trading/last_trading_dates` корректно возвращает последние торговые даты."""
        mock_trading_service.get_last_dates.return_value = [obj["date"] for obj in trading_data_with_id]
        response = client.get("/trading/last_trading_dates")

        assert response.status_code == 200
        assert "dates" in response.json()
        assert mock_trading_service.get_last_dates.call_count == 1

    def test_get_trading_results(
        self, client: TestClient, mock_trading_service: AsyncMock, trading_data_with_id: list[dict[str, Any]]
    ):
        """Проверяет, что эндпоинт `/trading/trading_results` возвращает результаты торгов."""
        mock_trading_service.filter.return_value = trading_data_with_id
        response = client.get("/trading/trading_results")
        assert response.status_code == 200
        assert mock_trading_service.filter.call_count == 1

    def test_get_trading_dynamics(
        self, client: TestClient, mock_trading_service: AsyncMock, trading_data_with_id: list[dict[str, Any]]
    ):
        """Проверяет, что эндпоинт `/trading/dynamics` возвращает динамику торгов."""
        mock_trading_service.filter.return_value = trading_data_with_id
        response = client.get("/trading/dynamics")
        assert response.status_code == 200
        assert mock_trading_service.filter.call_count == 1

    @pytest.mark.parametrize(
        "field",
        ("oil_id", "delivery_type_id", "delivery_basis_id"),
    )
    def test_trading_results_filtering(
        self,
        client: TestClient,
        field: str,
        mock_trading_service: AsyncMock,
        trading_data_with_id: list[dict[str, Any]],
    ):
        """Проверяет, что эндпоинт `/trading/trading_results` корректно фильтрует данные по заданному полю."""
        limit = 10
        offset = 0
        filter_value = trading_data_with_id[0][field]
        mock_trading_service.filter.return_value = [trading_data_with_id[0]]
        response = client.get(f"/trading/trading_results?{field}={filter_value}&limit={limit}&offset={offset}")
        assert mock_trading_service.filter.call_count == 1
        assert response.status_code == 200
        assert len(response.json()) == 1
        assert response.json()[0][field] == filter_value

    @pytest.mark.parametrize(
        "field",
        ("oil_id", "delivery_type_id", "delivery_basis_id"),
    )
    def test_trading_dynamics_filtering(
        self,
        client: TestClient,
        mock_trading_service: AsyncMock,
        field: str,
        trading_data_with_id: list[dict[str, Any]],
    ):
        """Проверяет, что эндпоинт `/trading/dynamics` корректно фильтрует данные по заданному полю."""
        obj = trading_data_with_id[0]
        value = obj[field]
        mock_trading_service.filter.return_value = [obj]
        response = client.get(f"trading/dynamics?{field}={value}")
        assert mock_trading_service.filter.call_count == 1
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
    def test_filter_by_date_range(
        self,
        client: TestClient,
        mock_trading_service: AsyncMock,
        field: str,
        operator,
        trading_data_with_id: list[dict[str, Any]],
    ):
        """Проверяет, что эндпоинт `/trading/dynamics` корректно фильтрует данные по диапазону дат."""
        obj = trading_data_with_id[0]
        expected = sorted(
            [i for i in trading_data_with_id if operator(obj["date"], i["date"])], key=lambda x: x["date"]
        )
        mock_trading_service.filter.return_value = expected
        response = client.get(f"trading/dynamics?{field}={obj['date']}")
        assert mock_trading_service.filter.call_count == 1
        assert response.status_code == 200
        assert len(response.json()) == len(expected)
