# ============================
# Tests básicos
# ============================

def test_app_starts(client_main):

    test_client, _ = client_main

    res = test_client.get("/openapi.json")

    assert res.status_code == 200


def test_docs_available(client_main):

    test_client, _ = client_main

    res = test_client.get("/docs")

    assert res.status_code == 200


# ============================
# Test rutas
# ============================

def test_market_route_exists(client_main):

    test_client, mock = client_main

    res = test_client.get("/finance/market")

    assert res.status_code == 200

    mock.market_data.assert_called_once()


def test_forecast_route_exists(client_main):

    test_client, mock = client_main

    res = test_client.get("/finance/forecast")

    assert res.status_code == 200

    mock.get_forecast.assert_called_once()


def test_kpis_route_exists(client_main):

    test_client, mock = client_main

    res = test_client.get("/finance/kpis")

    assert res.status_code == 200

    mock.get_kpis.assert_called_once()


# ============================
# Test CORS
# ============================

def test_cors_headers(client_main):

    test_client, _ = client_main

    headers = {
        "Origin": "http://localhost:3000",
        "Access-Control-Request-Method": "GET"
    }

    res = test_client.options(
        "/finance/market",
        headers=headers
    )

    assert res.status_code in (200, 204)

    assert "access-control-allow-origin" in res.headers


# ============================
# Robustez
# ============================

def test_unknown_route(client_main):

    test_client, _ = client_main

    res = test_client.get("/no-existe")

    assert res.status_code == 404