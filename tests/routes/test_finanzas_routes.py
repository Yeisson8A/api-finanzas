# ============================
# Tests /market
# ============================

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