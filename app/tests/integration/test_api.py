import operator
from datetime import date

import pytest


@pytest.mark.usefixtures("test_cache", "async_db_engine", "load_data_in_db")
class TestEndpoints:
    async def test_get_last_trading_dates(self, async_client):
        response = await async_client.get("/trading/last_trading_dates")
        assert response.status_code == 200
        assert len(response.json()["dates"]) == 3

    async def test_get_trading_results_endpoint(self, async_client):
        response = await async_client.get("/trading/trading_results")
        assert response.status_code == 200
        assert len(response.json()) == 3

    async def test_dynamics_endpoint(self, async_client):
        response = await async_client.get("/trading/dynamics")
        assert response.status_code == 200
        assert len(response.json()) == 3

    @pytest.mark.parametrize(
        "field",
        ("oil_id", "delivery_type_id", "delivery_basis_id"),
    )
    async def test_trading_results_endpoint_filter(self, async_client, tradings_list, field):
        filter_value = tradings_list[0][field]
        response = await async_client.get(f"/trading/trading_results?{field}={filter_value}")
        assert response.status_code == 200
        assert len(response.json()) == 1
        assert response.json()[0][field] == filter_value

    @pytest.mark.parametrize(
        "field",
        ("oil_id", "delivery_type_id", "delivery_basis_id"),
    )
    async def test_dynamics_endpoints_filters(self, async_client, field, tradings_list):
        obj = tradings_list[0]
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
    async def test_method_filter_by_date(self, async_client, field, operator, tradings_list):
        obj = tradings_list[0]
        expected = sorted(
            [i for i in tradings_list if operator(i["date"], obj["date"])], key=lambda x: x["date"], reverse=True
        )
        response = await async_client.get(f"trading/dynamics?{field}={obj['date']}")
        assert response.status_code == 200
        assert len(response.json()) == len(expected)
        assert operator(date.fromisoformat(response.json()[0]["date"]), obj["date"])

    @pytest.mark.parametrize(
        "field",
        ("oil_id", "delivery_type_id", "delivery_basis_id"),
    )
    async def test_trading_results_endpoint_filter_with_invalid_params(self, async_client, field):
        filter_value = ""
        response = await async_client.get(f"/trading/trading_results?{field}={filter_value}")
        assert response.status_code == 422

    @pytest.mark.parametrize(
        "field, non_existent_data",
        (("oil_id", "X101"), ("delivery_type_id", "X"), ("delivery_basis_id", "NOT")),
    )
    async def test_trading_results_endpoint_filter_with_non_existent_data(
        self, async_client, field, non_existent_data
    ):
        response = await async_client.get(f"/trading/trading_results?{field}={non_existent_data}")
        assert response.status_code == 200
        assert len(response.json()) == 0
