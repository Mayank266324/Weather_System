import numpy as np


class LSTMForecaster:
    """Small CPU-friendly LSTM for univariate lag-window forecasting."""

    name = "LSTM"

    def __init__(self, hidden_size=16, epochs=120, learning_rate=0.01):
        self.hidden_size = hidden_size
        self.epochs = epochs
        self.learning_rate = learning_rate
        self.model = None
        self._torch = None

    def _load_backend(self):
        if self._torch is not None:
            return self._torch
        try:
            import torch
            from torch import nn
        except (ImportError, OSError) as error:
            raise RuntimeError(
                "LSTM requires a working PyTorch installation. "
                "The current Python environment could not load PyTorch; "
                "use a supported Python version such as 3.12 and reinstall torch."
            ) from error

        class LSTMRegressor(nn.Module):
            def __init__(self, hidden_size):
                super().__init__()
                self.lstm = nn.LSTM(input_size=1, hidden_size=hidden_size, batch_first=True)
                self.output = nn.Linear(hidden_size, 1)

            def forward(self, values):
                sequence, _ = self.lstm(values)
                return self.output(sequence[:, -1, :])

        self._torch = (torch, nn, LSTMRegressor)
        return self._torch

    def fit(self, X, y):
        X = np.asarray(X, dtype=np.float32)
        y = np.asarray(y, dtype=np.float32)
        if len(X) == 0:
            return self

        torch, nn, lstm_regressor = self._load_backend()
        torch.manual_seed(42)
        self.model = lstm_regressor(self.hidden_size)
        inputs = torch.from_numpy(X).unsqueeze(-1)
        targets = torch.from_numpy(y).reshape(-1, 1)
        optimizer = torch.optim.Adam(self.model.parameters(), lr=self.learning_rate)
        loss_function = nn.MSELoss()

        self.model.train()
        for _ in range(self.epochs):
            optimizer.zero_grad()
            loss = loss_function(self.model(inputs), targets)
            loss.backward()
            optimizer.step()
        return self

    def predict(self, X):
        X = np.asarray(X, dtype=np.float32)
        if len(X) == 0:
            return np.asarray([])
        if self.model is None:
            raise RuntimeError("LSTM forecaster must be fitted before prediction.")

        torch = self._torch[0]
        self.model.eval()
        with torch.no_grad():
            inputs = torch.from_numpy(X).unsqueeze(-1)
            return self.model(inputs).squeeze(-1).numpy().astype(float)

    def forecast_next(self, history, steps=1, window_size=3):
        values = list(np.asarray(history, dtype=float))
        predictions = []
        for _ in range(steps):
            window = values[-window_size:]
            if len(window) < window_size:
                prediction = float(np.mean(window))
            else:
                prediction = float(self.predict(np.asarray([window]))[0])
            predictions.append(prediction)
            values.append(prediction)
        return np.asarray(predictions, dtype=float)
