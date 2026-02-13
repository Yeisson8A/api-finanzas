import time
import requests
import pandas as pd
from app.config.config import ALPHA_API_KEY, DEFAULT_SYMBOL


# Cache por símbolo
_cache = {}
CACHE_SECONDS = 300


def _fetch_from_alpha(symbol: str):

    url = "https://www.alphavantage.co/query"

    params = {
        "function": "TIME_SERIES_DAILY",
        "symbol": symbol,
        "apikey": ALPHA_API_KEY,
        "outputsize": "compact"
    }

    r = requests.get(url, params=params, timeout=15)
    data = r.json()

    series = data.get("Time Series (Daily)")

    if not series:
        raise Exception(f"Alpha error: {data}")

    df = pd.DataFrame.from_dict(series, orient="index")

    df = df.astype(float)
    df.index = pd.to_datetime(df.index)

    return df.sort_index()


def get_market_data(symbol: str | None = None):

    global _cache_data, _cache_time

    # Usar default si no viene
    symbol = symbol or DEFAULT_SYMBOL

    now = time.time()

    # Cache independiente por símbolo
    if symbol in _cache:

        cached = _cache[symbol]

        if now - cached["time"] < CACHE_SECONDS:
            return cached["data"]

    # Llamada real
    df = _fetch_from_alpha(symbol)

    _cache[symbol] = {
        "data": df,
        "time": now
    }

    return df
