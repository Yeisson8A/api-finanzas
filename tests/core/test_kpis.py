import numpy as np
import pandas as pd
import pytest
from app.core.kpis import calculate_kpis


def test_calculate_kpis_returns_dict(bullish_df):
    """Debe devolver diccionario"""

    result = calculate_kpis(bullish_df)

    assert isinstance(result, dict)


def test_kpis_contains_all_keys(bullish_df):
    """Debe incluir todas las métricas"""

    result = calculate_kpis(bullish_df)

    expected_keys = {
        "last_price",
        "daily_return_pct",
        "volatility_pct",
        "ma_20",
        "ma_50",
        "rsi_14",
        "max_drawdown_pct",
        "trend"
    }

    assert set(result.keys()) == expected_keys


def test_last_price_correct(bullish_df):
    """Último precio correcto"""

    result = calculate_kpis(bullish_df)

    assert result["last_price"] == round(bullish_df["4. close"].iloc[-1], 2)


def test_bullish_trend(bullish_df):
    """Detecta tendencia alcista"""

    result = calculate_kpis(bullish_df)

    assert result["trend"] == "bullish"


def test_bearish_trend(bearish_df):
    """Detecta tendencia bajista"""

    result = calculate_kpis(bearish_df)

    assert result["trend"] == "bearish"


def test_volatility_zero_on_flat(flat_df):
    """Volatilidad debe ser ~0 si no hay cambios"""

    result = calculate_kpis(flat_df)

    assert abs(result["volatility_pct"]) < 0.0001


def test_daily_return_positive_on_bullish(bullish_df):
    """Retorno debe ser positivo"""

    result = calculate_kpis(bullish_df)

    assert result["daily_return_pct"] > 0


def test_daily_return_negative_on_bearish(bearish_df):
    """Retorno debe ser negativo"""

    result = calculate_kpis(bearish_df)

    assert result["daily_return_pct"] < 0


def test_rsi_range(bullish_df):
    """RSI siempre entre 0 y 100"""

    result = calculate_kpis(bullish_df)

    rsi = result["rsi_14"]

    assert 0 <= rsi <= 100


def test_drawdown_negative_or_zero(bullish_df):
    """Drawdown nunca positivo"""

    result = calculate_kpis(bullish_df)

    assert result["max_drawdown_pct"] <= 0


def test_moving_averages_exist(bullish_df):
    """MA20 y MA50 deben existir"""

    result = calculate_kpis(bullish_df)

    assert isinstance(result["ma_20"], float)
    assert isinstance(result["ma_50"], float)


def test_minimum_required_data():
    """
    Menos de 50 datos → MAs serán NaN
    Debe manejar sin crash
    """

    prices = [100, 102, 101, 103, 104]

    dates = pd.date_range(
        "2024-01-01",
        periods=5
    )

    df = pd.DataFrame(
        {"4. close": prices},
        index=dates
    )

    result = calculate_kpis(df)

    assert "ma_50" in result
    assert result["last_price"] == 104


def test_missing_column_raises():
    """Debe fallar si no existe '4. close'"""

    df = pd.DataFrame(
        {"close": [100, 101, 102]}
    )

    with pytest.raises(KeyError):
        calculate_kpis(df)


def test_nan_values_handling():
    """Debe manejar NaN sin romper"""

    prices = [100, 101, np.nan, 103, 104, 105, 106, 107, 108, 109,
              110, 111, 112, 113, 114, 115, 116, 117, 118, 119,
              120, 121, 122, 123, 124, 125, 126, 127, 128, 129,
              130, 131, 132, 133, 134, 135, 136, 137, 138, 139,
              140, 141, 142, 143, 144, 145, 146, 147, 148, 149,
              150, 151, 152, 153, 154, 155, 156, 157, 158, 159]

    dates = pd.date_range(
        "2024-01-01",
        periods=60
    )

    df = pd.DataFrame(
        {"4. close": prices},
        index=dates
    )

    result = calculate_kpis(df)

    # No debe ser None
    assert result["last_price"] is not None


def test_rounding_precision(bullish_df):
    """Todos los floats deben venir redondeados a 2 decimales"""

    result = calculate_kpis(bullish_df)

    for key, value in result.items():

        if isinstance(value, float):

            text = f"{value:.2f}"
            assert float(text) == value