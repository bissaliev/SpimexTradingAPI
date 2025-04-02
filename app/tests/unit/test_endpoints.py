import operator

import pytest


class TestEndpoints:
    def test_get_last_trading_dates(self, client, override_trading_service, tradings_list):
        override_trading_service.get_last_dates.return_value = [obj["date"] for obj in tradings_list]
        response = client.get("/trading/last_trading_dates")
        assert response.status_code == 200
        assert "dates" in response.json()
        assert override_trading_service.get_last_dates.call_count == 1

    def test_get_trading_results_endpoint(self, client, override_trading_service, tradings_list):
        override_trading_service.filter.return_value = tradings_list
        response = client.get("/trading/trading_results")
        assert response.status_code == 200
        assert override_trading_service.filter.call_count == 1

    def test_dynamics_endpoint(self, client, override_trading_service, tradings_list):
        override_trading_service.filter.return_value = tradings_list
        response = client.get("/trading/dynamics")
        assert response.status_code == 200
        assert override_trading_service.filter.call_count == 1

    @pytest.mark.parametrize(
        "field",
        ("oil_id", "delivery_type_id", "delivery_basis_id"),
    )
    def test_trading_results_endpoint_filter(self, client, field, override_trading_service, tradings_list):
        limit = 10
        offset = 0
        filter_value = tradings_list[0][field]
        override_trading_service.filter.return_value = [tradings_list[0]]
        response = client.get(f"/trading/trading_results?{field}={filter_value}&limit={limit}&offset={offset}")
        assert override_trading_service.filter.call_count == 1
        assert response.status_code == 200
        assert len(response.json()) == 1
        assert response.json()[0][field] == filter_value

    @pytest.mark.parametrize(
        "field",
        ("oil_id", "delivery_type_id", "delivery_basis_id"),
    )
    def test_dynamics_endpoints_filters(self, client, override_trading_service, field, tradings_list):
        obj = tradings_list[0]
        value = obj[field]
        override_trading_service.filter.return_value = [obj]
        response = client.get(f"trading/dynamics?{field}={value}")
        assert override_trading_service.filter.call_count == 1
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
    def test_method_filter_by_date(self, client, override_trading_service, field, operator, tradings_list):
        obj = tradings_list[0]
        expected = sorted([i for i in tradings_list if operator(obj["date"], i["date"])], key=lambda x: x["date"])
        override_trading_service.filter.return_value = expected
        response = client.get(f"trading/dynamics?{field}={obj['date']}")
        assert override_trading_service.filter.call_count == 1
        assert response.status_code == 200
        assert len(response.json()) == len(expected)
