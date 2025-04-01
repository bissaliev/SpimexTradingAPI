import operator

import pytest
from tests.dependencies import data


class TestEndpoints:
    def test_get_last_trading_dates(self, client):
        sorted_data = sorted([i["date"] for i in data], reverse=True)
        response = client.get("/trading/last_trading_dates")
        assert response.status_code == 200
        assert "dates" in response.json()
        assert response.json()["dates"] == sorted_data

    def test_get_trading_results_endpoint(self, client):
        response = client.get("/trading/trading_results")
        assert response.status_code == 200
        assert len(response.json()) == len(data)

    def test_dynamics_endpoint(self, client):
        response = client.get("/trading/dynamics")
        assert response.status_code == 200
        assert len(response.json()) == len(data)

    @pytest.mark.parametrize(
        "field, value",
        (
            ("oil_id", data[0]["oil_id"]),
            ("delivery_type_id", data[0]["delivery_type_id"]),
            ("delivery_basis_id", data[0]["delivery_basis_id"]),
        ),
    )
    def test_trading_results_endpoint_filter(self, client, field, value):
        limit = 10
        offset = 0
        response = client.get(f"/trading/trading_results?{field}={value}&limit={limit}&offset={offset}")
        assert response.status_code == 200
        assert len(response.json()) == 1
        assert response.json()[0][field] == value

    @pytest.mark.parametrize(
        "field, operator, value",
        (
            ("oil_id", operator.eq, data[0]["oil_id"]),
            ("delivery_type_id", operator.eq, data[0]["delivery_type_id"]),
            ("delivery_basis_id", operator.eq, data[0]["delivery_basis_id"]),
            ("start_date", operator.ge, sorted(data, key=lambda x: x["date"], reverse=True)[0]["date"]),
            ("end_date", operator.le, sorted(data, key=lambda x: x["date"])[0]["date"]),
        ),
    )
    def test_dynamics_endpoints_filters(self, client, field, operator, value):
        response = client.get(f"trading/dynamics?{field}={value}")
        assert response.status_code == 200
        assert len(response.json()) == 1
        obj = response.json()[0]
        current_date = obj["date"] if "date" in field else obj[field]
        assert operator(current_date, value)

    @pytest.mark.parametrize(
        "field, value",
        (("oil_id", "AAAA"), ("delivery_type_id", "L"), ("delivery_basis_id", "NNN")),
    )
    def test_dynamics_endpoints_filter_with_non_existent_params(self, client, field, value):
        response = client.get(f"trading/dynamics?{field}={value}")
        assert response.status_code == 200
        assert len(response.json()) == 0

    @pytest.mark.parametrize(
        "field, value",
        (
            ("oil_id", "AAAA"),
            ("delivery_type_id", "L"),
            ("delivery_basis_id", "NNN"),
        ),
    )
    def test_trading_results_endpoint_filter_with_non_existent_params(self, client, field, value):
        limit = 10
        offset = 0
        response = client.get(f"/trading/trading_results?{field}={value}&limit={limit}&offset={offset}")
        assert response.status_code == 200
        assert len(response.json()) == 0
