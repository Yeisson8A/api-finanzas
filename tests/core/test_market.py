import time
from unittest.mock import Mock
from app.core.market import (
    _fetch_from_alpha,
    get_market_data,
    _cache,
    CACHE_SECONDS
)
import pandas as pd
import pytest

# ============================
# Tests _fetch_from_alpha
# ============================

def test_fetch_from_alpha_ok(monkeypatch, alpha_response_ok):
    """Debe devolver DataFrame válido"""

    mock_response = Mock()
    mock_response.json.return_value = alpha_response_ok

    def mock_get(*args, **kwargs):
        return mock_response

    monkeypatch.setattr("requests.get", mock_get)

    df = _fetch_from_alpha("AAPL")

    assert isinstance(df, pd.DataFrame)
    assert len(df) == 2

    # Índice debe ser datetime
    assert isinstance(df.index[0], pd.Timestamp)

    # Valores float
    assert df["4. close"].dtype == float


def test_fetch_from_alpha_error(monkeypatch):
    """Debe lanzar excepción si Alpha responde mal"""

    mock_response = Mock()
    mock_response.json.return_value = {
        "Error Message": "Invalid API call"
    }

    monkeypatch.setattr("requests.get", lambda *a, **k: mock_response)

    with pytest.raises(Exception):
        _fetch_from_alpha("BAD")


# ============================
# Tests get_market_data
# ============================

def test_get_market_data_calls_fetch(monkeypatch, alpha_response_ok):
    """Debe llamar a _fetch_from_alpha si no hay cache"""

    mock_df = pd.DataFrame(
        {"4. close": [100.0, 105.0]},
        index=pd.to_datetime(["2024-01-01", "2024-01-02"])
    )

    mock_fetch = Mock(return_value=mock_df)

    monkeypatch.setattr(
        "app.core.market._fetch_from_alpha",
        mock_fetch
    )

    result = get_market_data("AAPL")

    assert result.equals(mock_df)
    mock_fetch.assert_called_once_with("AAPL")


def test_get_market_data_uses_cache(monkeypatch):
    """Debe usar cache si está vigente"""

    mock_df = pd.DataFrame(
        {"4. close": [200.0]},
        index=pd.to_datetime(["2024-01-01"])
    )

    fake_time = 1000

    # Mock time.time()
    monkeypatch.setattr(time, "time", lambda: fake_time)

    _cache["AAPL"] = {
        "data": mock_df,
        "time": fake_time
    }

    result = get_market_data("AAPL")

    assert result.equals(mock_df)


def test_get_market_data_cache_expired(monkeypatch):
    """Debe refrescar cache si expiró"""

    old_time = 1000
    new_time = old_time + CACHE_SECONDS + 10

    old_df = pd.DataFrame(
        {"4. close": [100.0]},
        index=pd.to_datetime(["2024-01-01"])
    )

    new_df = pd.DataFrame(
        {"4. close": [150.0]},
        index=pd.to_datetime(["2024-01-02"])
    )

    _cache["AAPL"] = {
        "data": old_df,
        "time": old_time
    }

    monkeypatch.setattr(time, "time", lambda: new_time)

    mock_fetch = Mock(return_value=new_df)

    monkeypatch.setattr(
        "app.core.market._fetch_from_alpha",
        mock_fetch
    )

    result = get_market_data("AAPL")

    assert result.equals(new_df)
    mock_fetch.assert_called_once()


def test_get_market_data_default_symbol(monkeypatch):
    """Debe usar DEFAULT_SYMBOL si no viene symbol"""

    mock_df = pd.DataFrame(
        {"4. close": [300.0]},
        index=pd.to_datetime(["2024-01-01"])
    )

    mock_fetch = Mock(return_value=mock_df)

    monkeypatch.setattr(
        "app.core.market._fetch_from_alpha",
        mock_fetch
    )

    result = get_market_data()

    assert result.equals(mock_df)

    # Se llamó con DEFAULT_SYMBOL
    args = mock_fetch.call_args[0]
    assert len(args) == 1