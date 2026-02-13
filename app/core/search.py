import requests
from app.config.config import ALPHA_API_KEY


def search_symbol(keyword: str):

    url = "https://www.alphavantage.co/query"

    params = {
        "function": "SYMBOL_SEARCH",
        "keywords": keyword,
        "apikey": ALPHA_API_KEY,
    }

    r = requests.get(url, params=params, timeout=15)

    data = r.json()

    matches = data.get("bestMatches", [])

    results = []

    for item in matches:
        results.append({
            "symbol": item["1. symbol"],
            "name": item["2. name"],
            "region": item["4. region"],
            "currency": item["8. currency"],
        })

    return results
