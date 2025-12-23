import numpy as np
from sklearn.linear_model import LinearRegression

class TempPredictor:
    def __init__(self):
        self.model = LinearRegression()

    def train(self, temps: list[float]):
        X = []
        y = []

        for i in range(len(temps) - 7):
            X.append(temps[i:i+7])
            y.append(temps[i+7])

        X = np.array(X)
        y = np.array(y)

        self.model.fit(X, y)

    def predict_next(self, last_7_days: list[float]) -> float:
        return float(self.model.predict([last_7_days])[0])
