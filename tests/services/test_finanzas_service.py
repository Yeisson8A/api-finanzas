from unittest.mock import patch

import pytest
from app.config.config import DEFAULT_SYMBOL
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


@patch("app.services.finanzas_service.search_symbol")
def test_search_symbols_success(mock_search):
    """
    Debe envolver correctamente el resultado
    """

    fake_results = [
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

    mock_search.return_value = fake_results

    result = finanzas_service.search_symbols("app")

    assert result == {
        "results": fake_results
    }

    mock_search.assert_called_once_with("app")


@patch("app.services.finanzas_service.search_symbol")
def test_search_symbols_empty(mock_search):
    """
    Debe manejar lista vacía
    """

    mock_search.return_value = []

    result = finanzas_service.search_symbols("zzz")

    assert result == {
        "results": []
    }

    mock_search.assert_called_once_with("zzz")


@patch("app.services.finanzas_service.search_symbol")
def test_search_symbols_propagates_exception(mock_search):
    """
    Debe propagar errores del core
    """

    mock_search.side_effect = Exception("API error")

    try:
        finanzas_service.search_symbols("fail")
        assert False, "Exception not raised"

    except Exception as e:
        assert str(e) == "API error"

    mock_search.assert_called_once_with("fail")


def test_get_kpi_insight_ok(
    kpi_data,
    mock_generate_ok,
    mock_insight_text
):
    """Debe retornar insight con symbol"""

    result = finanzas_service.get_kpi_insight(
        kpi_data["kpi"],
        kpi_data["value"],
        kpi_data["symbol"]
    )

    assert result == {
        "kpi": "RSI",
        "insight": mock_insight_text
    }

    mock_generate_ok.assert_called_once_with(
        "RSI",
        "55.2",
        "AAPL"
    )


def test_get_kpi_insight_uses_default_symbol(
    kpi_data,
    mock_generate_ok,
    mock_insight_text
):
    """Debe usar DEFAULT_SYMBOL si symbol es None"""

    result = finanzas_service.get_kpi_insight(
        kpi_data["kpi"],
        kpi_data["value"],
        None
    )

    assert result == {
        "kpi": "RSI",
        "insight": mock_insight_text
    }

    mock_generate_ok.assert_called_once_with(
        "RSI",
        "55.2",
        DEFAULT_SYMBOL
    )


def test_get_kpi_insight_propagates_exception(
    kpi_data,
    mock_generate_error
):
    """Debe propagar error del generador IA"""

    with pytest.raises(Exception) as exc:

        finanzas_service.get_kpi_insight(
            kpi_data["kpi"],
            kpi_data["value"],
            kpi_data["symbol"]
        )

    assert "Gemini error" in str(exc.value)