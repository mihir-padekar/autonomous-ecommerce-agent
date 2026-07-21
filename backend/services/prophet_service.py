from joblib import load
import pandas as pd

# Load once
model = load("prophet_model/delay_forecast.pkl")

history = pd.read_csv("prophet_model/delay_history.csv")

history.rename(
    columns={
        "order_date": "ds",
        "delayed_orders": "y"
    },
    inplace=True
)

history["ds"] = pd.to_datetime(history["ds"])
# Remove the last (incomplete) month
history = history.iloc[:-1]

def get_delay_forecast():

    future = model.make_future_dataframe(
        periods=6,
        freq="MS"
    )

    forecast = model.predict(future)

    # Keep only forecast part
    forecast = forecast.tail(6)[
        [
            "ds",
            "yhat",
            "yhat_lower",
            "yhat_upper"
        ]
    ].copy()

    forecast["yhat"] = forecast["yhat"].round().astype(int)
    forecast["yhat_lower"] = forecast["yhat_lower"].round().astype(int)
    forecast["yhat_upper"] = forecast["yhat_upper"].round().astype(int)

    history_json = history.copy()
    forecast_json = forecast.copy()

    history_json["ds"] = history_json["ds"].dt.strftime("%Y-%m-%d")
    forecast_json["ds"] = forecast_json["ds"].dt.strftime("%Y-%m-%d")

    return {
        "history": history_json.to_dict(orient="records"),
        "forecast": forecast_json.to_dict(orient="records")
    }