import time
import google.generativeai as genai
from app.config.config import GEMINI_API_KEY


genai.configure(api_key=GEMINI_API_KEY)

model = genai.GenerativeModel("gemini-2.5-flash")

_ai_cache = {}

CACHE_TTL = 60 * 60  # 1 hora


def _make_key(symbol: str, kpi: str, value: str):

    return f"{symbol}:{kpi}:{value}"


def generate_kpi_insight(kpi_name: str, value: str, symbol: str):

    now = time.time()

    key = _make_key(symbol, kpi_name, value)

    if key in _ai_cache:

        cached = _ai_cache[key]

        if now - cached["time"] < CACHE_TTL:
            return cached["text"]

    prompt = f"""
    You are a professional financial analyst.

    Stock: {symbol}
    KPI: {kpi_name}
    Value: {value}

    Explain clearly for an investor:
    - What this means
    - Risk level
    - Recommendation

    Use max 3 short sentences.
    """

    response = model.generate_content(prompt)

    text = response.text.strip()

    _ai_cache[key] = {
        "text": text,
        "time": now
    }

    return text