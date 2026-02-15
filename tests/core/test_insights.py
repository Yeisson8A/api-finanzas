from unittest.mock import MagicMock, patch
from app.core.insights import _make_key, generate_kpi_insight, _ai_cache, CACHE_TTL, model

# ============================
# TEST _make_key
# ============================


def test_make_key():

    key = _make_key(
        "AAPL",
        "RSI",
        "55.2"
    )

    assert key == "AAPL:RSI:55.2"


# ============================
# TEST generate_kpi_insight (SIN CACHE)
# ============================


def test_generate_kpi_insight_calls_gemini(
    mock_gemini,
    mock_time
):
    """
    Debe llamar a Gemini si no hay cache
    """

    mock_time.return_value = 1000.0

    result = generate_kpi_insight(
        "RSI",
        "55.2",
        "AAPL"
    )

    assert result == "This KPI indicates low risk."

    mock_gemini.assert_called_once()

    # Verifica cache
    key = "AAPL:RSI:55.2"

    assert key in _ai_cache


# ============================
# TEST CACHE HIT
# ============================


def test_generate_kpi_insight_uses_cache(
    mock_gemini,
    mock_time
):
    """
    Debe usar cache si no expira
    """

    # Primera llamada
    mock_time.return_value = 1000.0

    first = generate_kpi_insight(
        "RSI",
        "55.2",
        "AAPL"
    )

    # Segunda llamada dentro TTL
    mock_time.return_value = 1000.0 + 10

    second = generate_kpi_insight(
        "RSI",
        "55.2",
        "AAPL"
    )

    assert first == second

    # Gemini solo 1 vez
    mock_gemini.assert_called_once()


# ============================
# TEST CACHE EXPIRED
# ============================


def test_generate_kpi_insight_cache_expired(
    mock_gemini,
    mock_time
):
    """
    Debe llamar Gemini si cache expiró
    """

    # Primera llamada
    mock_time.return_value = 1000.0

    generate_kpi_insight(
        "RSI",
        "55.2",
        "AAPL"
    )

    # Simular expiración
    mock_time.return_value = (
        1000.0 + CACHE_TTL + 1
    )

    generate_kpi_insight(
        "RSI",
        "55.2",
        "AAPL"
    )

    # Gemini llamado 2 veces
    assert mock_gemini.call_count == 2


# ============================
# TEST CACHE MULTIPLE KEYS
# ============================


def test_generate_kpi_insight_multiple_keys(
    mock_gemini,
    mock_time
):
    """
    Cache independiente por símbolo/KPI
    """

    mock_time.return_value = 1000.0

    generate_kpi_insight(
        "RSI",
        "55.2",
        "AAPL"
    )

    generate_kpi_insight(
        "RSI",
        "60.1",
        "AAPL"
    )

    generate_kpi_insight(
        "RSI",
        "55.2",
        "TSLA"
    )

    # 3 keys distintas
    assert len(_ai_cache) == 3

    assert mock_gemini.call_count == 3


# ============================
# TEST STRIP TEXT
# ============================


def test_generate_kpi_insight_strips_text(
    mock_time
):
    """
    Debe limpiar espacios del texto
    """

    dirty_response = MagicMock()
    dirty_response.text = "  Hello Investor  \n"

    with patch.object(
        model,
        "generate_content",
        return_value=dirty_response
    ):

        mock_time.return_value = 1000

        result = generate_kpi_insight(
            "RSI",
            "55",
            "AAPL"
        )

        assert result == "Hello Investor"