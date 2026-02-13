from prophet import Prophet


def run_forecast(df, periods=30):

    data = df.reset_index()

    data = data[["index", "4. close"]]
    data.columns = ["ds", "y"]

    model = Prophet(
        weekly_seasonality=True,
        yearly_seasonality=True
    )

    model.fit(data)

    future = model.make_future_dataframe(
        periods=periods,
        freq="D"
    )

    forecast = model.predict(future)

    return forecast[
        ["ds", "yhat", "yhat_upper", "yhat_lower"]
    ]
