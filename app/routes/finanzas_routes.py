from fastapi import APIRouter, Query
from app.services import finanzas_service

router = APIRouter(prefix="/finance", tags=["Finance"])

@router.get("/market")
def market_data(
    symbol: str = Query(
        default=None,
        description="Símbolo bursátil (ej: AAPL, TSLA)"
    )
):
    return finanzas_service.market_data(symbol)


@router.get("/forecast")
def forecast(
    symbol: str = Query(
        default=None,
        description="Símbolo bursátil (ej: AAPL, TSLA)"
    ),
    periods: int = 30
):
    return finanzas_service.get_forecast(symbol, periods)

@router.get("/kpis")
def kpis(symbol: str = Query(default=None, description="Símbolo bursátil (ej: AAPL, TSLA)")):
    return finanzas_service.get_kpis(symbol)


@router.get("/search")
def search(q: str):

    return finanzas_service.search_symbols(q)