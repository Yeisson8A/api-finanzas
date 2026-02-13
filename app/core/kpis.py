import pandas as pd


def calculate_kpis(df: pd.DataFrame):

    close = df["4. close"]

    # ==========================
    # Rendimientos
    # ==========================

    returns = close.pct_change().dropna()

    daily_return = returns.mean() * 100
    volatility = returns.std() * 100

    # ==========================
    # Moving Averages
    # ==========================

    ma_20 = close.rolling(20).mean().iloc[-1]
    ma_50 = close.rolling(50).mean().iloc[-1]

    # ==========================
    # RSI (14)
    # ==========================

    delta = close.diff()

    gain = delta.where(delta > 0, 0)
    loss = -delta.where(delta < 0, 0)

    avg_gain = gain.rolling(14).mean()
    avg_loss = loss.rolling(14).mean()

    rs = avg_gain / avg_loss
    rsi = 100 - (100 / (1 + rs))

    rsi_value = rsi.iloc[-1]

    # ==========================
    # Drawdown
    # ==========================

    rolling_max = close.cummax()
    drawdown = (close - rolling_max) / rolling_max

    max_drawdown = drawdown.min() * 100

    # ==========================
    # Trend
    # ==========================

    trend = "bullish" if close.iloc[-1] > ma_50 else "bearish"

    # ==========================
    # Resultado
    # ==========================

    return {
        "last_price": round(close.iloc[-1], 2),

        "daily_return_pct": round(daily_return, 2),
        "volatility_pct": round(volatility, 2),

        "ma_20": round(ma_20, 2),
        "ma_50": round(ma_50, 2),

        "rsi_14": round(rsi_value, 2),

        "max_drawdown_pct": round(max_drawdown, 2),

        "trend": trend
    }
