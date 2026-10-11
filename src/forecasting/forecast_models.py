from src.forecasting.deep_learning.lstm_forecast import LSTMForecaster
from src.forecasting.statistical.moving_average import MovingAverageForecaster
from src.forecasting.statistical.regression_forecast import LinearRegressionForecaster


def build_forecaster(mode):
    if mode == "Moving Average":
        return MovingAverageForecaster()
    if mode == "Linear Regression":
        return LinearRegressionForecaster()
    if mode == "LSTM":
        return LSTMForecaster()
    raise ValueError(f"Unsupported forecast mode: {mode}")
