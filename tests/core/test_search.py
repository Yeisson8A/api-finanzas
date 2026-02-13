import pytest
from unittest.mock import patch, Mock

from app.core.search import search_symbol


# ============================
# Mock helpers
# ============================

def mock_response(json_data):
    """
    Crea mock de requests response
    """
    mock = Mock()
    mock.json.return_value = json_data
    return mock


# ============================
# Tests
# ============================

@patch("app.core.search.requests.get")
def test_search_symbol_success(mock_get):
    """
    Debe parsear resultados correctamente
    """

    alpha_response = {
        "bestMatches": [
            {
                "1. symbol": "AAPL",
                "2. name": "Apple Inc",
                "4. region": "United States",
                "8. currency": "USD",
            },
            {
                "1. symbol": "AAP",
                "2. name": "Advance Auto Parts",
                "4. region": "United States",
                "8. currency": "USD",
            },
        ]
    }

    mock_get.return_value = mock_response(alpha_response)

    result = search_symbol("app")

    assert result == [
        {
            "symbol": "AAPL",
            "name": "Apple Inc",
            "region": "United States",
            "currency": "USD",
        },
        {
            "symbol": "AAP",
            "name": "Advance Auto Parts",
            "region": "United States",
            "currency": "USD",
        },
    ]

    mock_get.assert_called_once()


@patch("app.core.search.requests.get")
def test_search_symbol_empty_results(mock_get):
    """
    Debe retornar lista vacía si no hay matches
    """

    mock_get.return_value = mock_response({
        "bestMatches": []
    })

    result = search_symbol("zzz")

    assert result == []


@patch("app.core.search.requests.get")
def test_search_symbol_no_bestmatches_key(mock_get):
    """
    Debe manejar respuesta sin bestMatches
    """

    mock_get.return_value = mock_response({
        "Note": "API limit"
    })

    result = search_symbol("test")

    assert result == []


@patch("app.core.search.requests.get")
def test_search_symbol_incomplete_data(mock_get):
    """
    Si faltan campos debe lanzar KeyError
    (documenta comportamiento actual)
    """

    mock_get.return_value = mock_response({
        "bestMatches": [
            {
                "1. symbol": "AAPL"
                # faltan campos
            }
        ]
    })

    with pytest.raises(KeyError):
        search_symbol("apple")


@patch("app.core.search.requests.get")
def test_search_symbol_request_called_correctly(mock_get):
    """
    Verifica URL y params
    """

    mock_get.return_value = mock_response({
        "bestMatches": []
    })

    keyword = "tesla"

    search_symbol(keyword)

    args, kwargs = mock_get.call_args

    assert args[0] == "https://www.alphavantage.co/query"

    assert kwargs["params"]["function"] == "SYMBOL_SEARCH"
    assert kwargs["params"]["keywords"] == keyword
    assert "apikey" in kwargs["params"]

    assert kwargs["timeout"] == 15
