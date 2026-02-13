import app.services.finanzas_service as finanzas_service

# ============================
# Tests market_data
# ============================

def test_market_data_with_symbol(mock_dependencies):

    mocks = mock_dependencies

    result = finanzas_service.market_data("TSLA")

    # Llamada correcta
    mocks["market"].assert_called_once_with("TSLA")

    # Formato
    assert result["symbol"] == "TSLA"
    assert isinstance(result["data"], dict)


def test_market_data_default_symbol(mock_dependencies):

    result = finanzas_service.market_data(None)

    assert result["symbol"] == "AAPL"


def test_market_data_limits_rows(mock_dependencies):

    df = mock_dependencies["df"]

    result = finanzas_service.market_data("AAPL")

    # .tail(150) no debe romper
    assert len(result["data"]["4. close"]) <= 150


# ============================
# Tests get_forecast
# ============================

def test_get_forecast_basic(mock_dependencies):

    mocks = mock_dependencies

    result = finanzas_service.get_forecast("MSFT", 3)

    mocks["market"].assert_called_once_with("MSFT")
    mocks["forecast"].assert_called_once_with(
        mocks["df"],
        3
    )

    assert result["symbol"] == "MSFT"
    assert isinstance(result["forecast"], list)


def test_get_forecast_default_symbol(mock_dependencies):

    result = finanzas_service.get_forecast(None, 5)

    assert result["symbol"] == "AAPL"


def test_get_forecast_serialization(mock_dependencies):

    result = finanzas_service.get_forecast("AAPL", 3)

    row = result["forecast"][0]

    assert "ds" in row
    assert "yhat" in row
    assert "yhat_upper" in row
    assert "yhat_lower" in row


# ============================
# Tests get_kpis
# ============================

def test_get_kpis_basic(mock_dependencies):

    mocks = mock_dependencies

    result = finanzas_service.get_kpis("GOOG")

    mocks["market"].assert_called_once_with("GOOG")
    mocks["kpis"].assert_called_once_with(
        mocks["df"]
    )

    assert result["symbol"] == "GOOG"
    assert result["kpis"]["trend"] == "bullish"


def test_get_kpis_default_symbol(mock_dependencies):

    result = finanzas_service.get_kpis(None)

    assert result["symbol"] == "AAPL"


# ============================
# Robustez
# ============================

def test_market_data_returns_dict(mock_dependencies):

    result = finanzas_service.market_data("AAPL")

    assert isinstance(result, dict)


def test_get_forecast_returns_dict(mock_dependencies):

    result = finanzas_service.get_forecast("AAPL")

    assert isinstance(result, dict)


def test_get_kpis_returns_dict(mock_dependencies):

    result = finanzas_service.get_kpis("AAPL")

    assert isinstance(result, dict)