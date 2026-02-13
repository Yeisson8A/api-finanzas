from unittest.mock import Mock
from fastapi import FastAPI
from fastapi.testclient import TestClient
import numpy as np
import pandas as pd
import pytest
from app.core.market import _cache
from app.routes.finanzas_routes import router
import app.services.finanzas_service as finanzas_service
import app.main as main_app

@pytest.fixture
def alpha_response_ok():
    """Respuesta mock válida de Alpha"""

    return {
        "Time Series (Daily)": {
            "2024-01-01": {
                "1. open": "100",
                "2. high": "105",
                "3. low": "98",
                "4. close": "102",
                "5. volume": "1000000"
            },
            "2024-01-02": {
                "1. open": "102",
                "2. high": "108",
                "3. low": "101",
                "4. close": "107",
                "5. volume": "1200000"
            }
        }
    }


@pytest.fixture(autouse=True)
def clear_cache():
    """Limpia cache antes de cada test"""

    _cache.clear()


@pytest.fixture
def sample_forecast_df():
    """DataFrame simulado de mercado"""

    return pd.DataFrame(
        {
            "4. close": [100, 102, 101, 105, 107]
        },
        index=pd.to_datetime([
            "2024-01-01",
            "2024-01-02",
            "2024-01-03",
            "2024-01-04",
            "2024-01-05"
        ])
    )


@pytest.fixture
def mock_prophet(monkeypatch):
    """Mock completo de Prophet"""

    mock_model = Mock()

    # DataFrame futuro
    future_df = pd.DataFrame({
        "ds": pd.date_range("2024-01-06", periods=30)
    })

    # Forecast simulado
    forecast_df = pd.DataFrame({
        "ds": future_df["ds"],
        "yhat": [110] * 30,
        "yhat_upper": [115] * 30,
        "yhat_lower": [105] * 30,
    })

    # Comportamiento del mock
    mock_model.make_future_dataframe.return_value = future_df
    mock_model.predict.return_value = forecast_df

    mock_class = Mock(return_value=mock_model)

    monkeypatch.setattr(
        "app.core.forecast.Prophet",
        mock_class
    )

    return mock_class, mock_model


@pytest.fixture
def bullish_df():
    """
    DataFrame con tendencia alcista clara
    60 días para cubrir MA50
    """

    prices = np.linspace(100, 160, 60)

    dates = pd.date_range(
        start="2024-01-01",
        periods=60,
        freq="D"
    )

    return pd.DataFrame(
        {
            "4. close": prices
        },
        index=dates
    )


@pytest.fixture
def bearish_df():
    """DataFrame con tendencia bajista"""

    prices = np.linspace(160, 100, 60)

    dates = pd.date_range(
        start="2024-01-01",
        periods=60,
        freq="D"
    )

    return pd.DataFrame(
        {
            "4. close": prices
        },
        index=dates
    )


@pytest.fixture
def flat_df():
    """Precio constante (sin volatilidad)"""

    prices = np.full(60, 120.0)

    dates = pd.date_range(
        start="2024-01-01",
        periods=60,
        freq="D"
    )

    return pd.DataFrame(
        {
            "4. close": prices
        },
        index=dates
    )


@pytest.fixture
def client(monkeypatch):
    """
    Crea una app FastAPI aislada
    con services mockeados
    """

    app = FastAPI()
    app.include_router(router)

    # =========================
    # Mock del service
    # =========================

    mock_service = Mock()

    mock_service.market_data.return_value = {
        "symbol": "AAPL",
        "data": []
    }

    mock_service.get_forecast.return_value = {
        "symbol": "AAPL",
        "forecast": []
    }

    mock_service.get_kpis.return_value = {
        "symbol": "AAPL",
        "kpis": {}
    }

    monkeypatch.setattr(
        "app.routes.finanzas_routes.finanzas_service",
        mock_service
    )

    return TestClient(app), mock_service


@pytest.fixture
def sample_service_df():
    """DataFrame simulado"""

    return pd.DataFrame(
        {
            "4. close": [100.0, 102.0, 105.0]
        },
        index=pd.to_datetime([
            "2024-01-01",
            "2024-01-02",
            "2024-01-03"
        ])
    )


@pytest.fixture
def mock_dependencies(monkeypatch, sample_service_df):
    """
    Mockea todas las dependencias externas
    """

    # Mock get_market_data
    mock_market = Mock(return_value=sample_service_df)

    monkeypatch.setattr(
        finanzas_service,
        "get_market_data",
        mock_market
    )

    # Mock run_forecast
    forecast_df = pd.DataFrame({
        "ds": pd.date_range("2024-01-04", periods=3),
        "yhat": [110, 111, 112],
        "yhat_upper": [115, 116, 117],
        "yhat_lower": [105, 106, 107],
    })

    mock_forecast = Mock(return_value=forecast_df)

    monkeypatch.setattr(
        finanzas_service,
        "run_forecast",
        mock_forecast
    )

    # Mock calculate_kpis
    mock_kpis_data = {
        "last_price": 105,
        "trend": "bullish"
    }

    mock_kpis = Mock(return_value=mock_kpis_data)

    monkeypatch.setattr(
        finanzas_service,
        "calculate_kpis",
        mock_kpis
    )

    # Mock DEFAULT_SYMBOL
    monkeypatch.setattr(
        finanzas_service,
        "DEFAULT_SYMBOL",
        "AAPL"
    )

    return {
        "market": mock_market,
        "forecast": mock_forecast,
        "kpis": mock_kpis,
        "df": sample_service_df,
        "forecast_df": forecast_df,
        "kpis_data": mock_kpis_data
    }


@pytest.fixture
def client_main(monkeypatch):
    """
    Cliente con services mockeados
    (evita llamadas a Alpha)
    """

    # Mock del service
    mock_service = Mock()

    mock_service.market_data.return_value = {
        "symbol": "AAPL",
        "data": []
    }

    mock_service.get_forecast.return_value = {
        "symbol": "AAPL",
        "forecast": []
    }

    mock_service.get_kpis.return_value = {
        "symbol": "AAPL",
        "kpis": {}
    }

    # Patch del service dentro del router
    monkeypatch.setattr(
        "app.routes.finanzas_routes.finanzas_service",
        mock_service
    )

    app = main_app.app

    return TestClient(app), mock_service


@pytest.fixture
def client_search():
    app = main_app.app
    return TestClient(app)