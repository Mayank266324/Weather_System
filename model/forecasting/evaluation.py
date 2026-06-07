import numpy as np


class ForecastEvaluator:
    """Evaluate forecast outputs with baseline regression metrics."""

    def evaluate(self, actual, predicted):
        actual = np.asarray(actual, dtype=float)
        predicted = np.asarray(predicted, dtype=float)
        if actual.size == 0 or predicted.size == 0:
            return {"mse": "N/A", "rmse": "N/A", "mae": "N/A"}
        error = predicted - actual
        mse = float(np.mean(error**2))
        rmse = float(np.sqrt(mse))
        mae = float(np.mean(np.abs(error)))
        return {"mse": f"{mse:.4f}", "rmse": f"{rmse:.4f}", "mae": f"{mae:.4f}"}
