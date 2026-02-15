# ============================
# Tests /market
# ============================

from unittest.mock import patch

import pytest


def test_market_default_symbol(client):

    test_client, mock_service = client

    res = test_client.get("/finance/market")

    assert res.status_code == 200
    assert res.json()["symbol"] == "AAPL"

    mock_service.market_data.assert_called_once_with(None)


def test_market_with_symbol(client):

    test_client, mock_service = client

    res = test_client.get("/finance/market?symbol=TSLA")

    assert res.status_code == 200

    mock_service.market_data.assert_called_once_with("TSLA")


# ============================
# Tests /forecast
# ============================

def test_forecast_default(client):

    test_client, mock_service = client

    res = test_client.get("/finance/forecast")

    assert res.status_code == 200

    mock_service.get_forecast.assert_called_once_with(
        None,
        30
    )


def test_forecast_with_params(client):

    test_client, mock_service = client

    res = test_client.get(
        "/finance/forecast?symbol=MSFT&periods=60"
    )

    assert res.status_code == 200

    mock_service.get_forecast.assert_called_once_with(
        "MSFT",
        60
    )


# ============================
# Tests /kpis
# ============================

def test_kpis_default(client):

    test_client, mock_service = client

    res = test_client.get("/finance/kpis")

    assert res.status_code == 200

    mock_service.get_kpis.assert_called_once_with(None)


def test_kpis_with_symbol(client):

    test_client, mock_service = client

    res = test_client.get("/finance/kpis?symbol=GOOG")

    assert res.status_code == 200

    mock_service.get_kpis.assert_called_once_with("GOOG")


# ============================
# Validación básica
# ============================

def test_market_returns_json(client):

    test_client, _ = client

    res = test_client.get("/finance/market")

    assert res.headers["content-type"] == "application/json"


# ============================
# Tests /search
# ============================

@patch("app.routes.finanzas_routes.finanzas_service.search_symbols")
def test_search_route_success(mock_search, client_search):
    """
    Debe devolver resultados correctamente
    """

    fake_data = {
        "results": [
            {
                "symbol": "AAPL",
                "name": "Apple Inc",
                "region": "United States",
                "currency": "USD",
            },
            {
                "symbol": "MSFT",
                "name": "Microsoft Corp",
                "region": "United States",
                "currency": "USD",
            },
        ]
    }

    mock_search.return_value = fake_data

    response = client_search.get("/finance/search?q=app")

    assert response.status_code == 200

    assert response.json() == fake_data

    mock_search.assert_called_once_with("app")


@patch("app.routes.finanzas_routes.finanzas_service.search_symbols")
def test_search_route_empty(mock_search, client_search):
    """
    Debe manejar resultados vacíos
    """

    mock_search.return_value = {
        "results": []
    }

    response = client_search.get("/finance/search?q=zzz")

    assert response.status_code == 200

    assert response.json() == {
        "results": []
    }

    mock_search.assert_called_once_with("zzz")


def test_search_route_missing_query(client_search):
    """
    Debe fallar si no se envía q
    """

    response = client_search.get("/finance/search")

    assert response.status_code == 422


@patch("app.routes.finanzas_routes.finanzas_service.search_symbols")
def test_search_route_propagates_exception(mock_search, client_search):
    """
    Debe devolver 500 si el service falla
    """

    mock_search.side_effect = Exception("Service error")

    with pytest.raises(Exception) as exc:
        client_search.get("/finance/search?q=fail")

    assert str(exc.value) == "Service error"

    mock_search.assert_called_once_with("fail")


def test_kpi_insight_ok(
    client_insights,
    mock_service_ok,
    mock_kpi_response
):
    """Debe responder correctamente con symbol"""

    response = client_insights.get(
        "/finance/kpi-insight",
        params={
            "kpi": "RSI",
            "value": "55.2",
            "symbol": "AAPL"
        }
    )

    assert response.status_code == 200
    assert response.json() == mock_kpi_response

    mock_service_ok.assert_called_once_with(
        "RSI",
        "55.2",
        "AAPL"
    )


def test_kpi_insight_without_symbol(
    client_insights,
    mock_service_ok,
    mock_kpi_response
):
    """Debe funcionar sin symbol"""

    response = client_insights.get(
        "/finance/kpi-insight",
        params={
            "kpi": "RSI",
            "value": "55.2"
        }
    )

    assert response.status_code == 200
    assert response.json() == mock_kpi_response

    mock_service_ok.assert_called_once_with(
        "RSI",
        "55.2",
        None
    )


def test_kpi_insight_propagates_exception(
    client_insights,
    mock_service_error
):
    """Debe retornar 500 si el servicio falla"""

    response = client_insights.get(
        "/finance/kpi-insight",
        params={
            "kpi": "RSI",
            "value": "70",
            "symbol": "TSLA"
        }
    )

    assert response.status_code == 500