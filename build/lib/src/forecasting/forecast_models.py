from src.forecasting.statistical.moving_average import MovingAverageForecaster
from src.forecasting.statistical.regression_forecast import LinearRegressionForecaster


def build_forecaster(mode):
    if mode == "Moving Average":
        return MovingAverageForecaster()
    if mode == "Linear Regression":
        return LinearRegressionForecaster()
    raise ValueError(f"Unsupported Phase 1 forecast mode: {mode}")
