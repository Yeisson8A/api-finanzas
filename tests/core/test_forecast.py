import pandas as pd
from app.core.forecast import run_forecast


def test_run_forecast_basic(sample_forecast_df, mock_prophet):
    """Test principal"""

    mock_class, mock_model = mock_prophet

    result = run_forecast(sample_forecast_df, periods=30)

    # =========================
    # Validaciones resultado
    # =========================

    assert isinstance(result, pd.DataFrame)
    assert len(result) == 30

    expected_cols = ["ds", "yhat", "yhat_upper", "yhat_lower"]

    assert list(result.columns) == expected_cols


def test_prophet_constructor_called(mock_prophet, sample_forecast_df):
    """Verifica parámetros de Prophet"""

    mock_class, _ = mock_prophet

    run_forecast(sample_forecast_df)

    mock_class.assert_called_once_with(
        weekly_seasonality=True,
        yearly_seasonality=True
    )


def test_model_fit_called(mock_prophet, sample_forecast_df):
    """Verifica que fit() se ejecuta"""

    _, mock_model = mock_prophet

    run_forecast(sample_forecast_df)

    assert mock_model.fit.called
    assert mock_model.fit.call_count == 1


def test_future_dataframe_called(mock_prophet, sample_forecast_df):
    """Verifica creación de fechas futuras"""

    _, mock_model = mock_prophet

    run_forecast(sample_forecast_df, periods=45)

    mock_model.make_future_dataframe.assert_called_once_with(
        periods=45,
        freq="D"
    )


def test_predict_called(mock_prophet, sample_forecast_df):
    """Verifica ejecución predict"""

    _, mock_model = mock_prophet

    run_forecast(sample_forecast_df)

    mock_model.predict.assert_called_once()


def test_fit_input_format(mock_prophet, sample_forecast_df):
    """Verifica formato de datos enviados a fit"""

    _, mock_model = mock_prophet

    run_forecast(sample_forecast_df)

    fit_arg = mock_model.fit.call_args[0][0]

    # Columnas correctas
    assert list(fit_arg.columns) == ["ds", "y"]

    # Tipos
    assert pd.api.types.is_datetime64_any_dtype(fit_arg["ds"])
    assert pd.api.types.is_numeric_dtype(fit_arg["y"])


def test_output_values(mock_prophet, sample_forecast_df):
    """Verifica contenido simulado"""

    result = run_forecast(sample_forecast_df)

    assert (result["yhat"] == 110).all()
    assert (result["yhat_upper"] == 115).all()
    assert (result["yhat_lower"] == 105).all()
