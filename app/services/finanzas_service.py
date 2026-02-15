from app.config.config import DEFAULT_SYMBOL
from app.core.forecast import run_forecast
from app.core.insights import generate_kpi_insight
from app.core.kpis import calculate_kpis
from app.core.market import get_market_data
from app.core.search import search_symbol


def market_data(symbol: str):

    df = get_market_data(symbol)

    return {
        "symbol": symbol or DEFAULT_SYMBOL,
        "data": df.tail(150).to_dict()
    }

def get_forecast(symbol: str, periods: int = 30):

    df = get_market_data(symbol)

    result = run_forecast(df, periods)

    return {
        "symbol": symbol or DEFAULT_SYMBOL,
        "forecast": result.to_dict(orient="records")
    }

def get_kpis(symbol: str):
    df = get_market_data(symbol)
    kpis = calculate_kpis(df)

    return {
        "symbol": symbol or DEFAULT_SYMBOL,
        "kpis": kpis
    }


def search_symbols(keyword: str):

    return {
        "results": search_symbol(keyword)
    }


def get_kpi_insight(kpi: str, value: str, symbol: str):
    insight = generate_kpi_insight(kpi, value, symbol or DEFAULT_SYMBOL)

    return {
        "kpi": kpi,
        "insight": insight
    }