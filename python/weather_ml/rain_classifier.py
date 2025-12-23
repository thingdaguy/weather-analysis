import numpy as np
import pandas as pd
from sklearn.linear_model import LogisticRegression
from sklearn.preprocessing import StandardScaler

class RainClassifier:
    def __init__(self):
        self.scaler = StandardScaler()
        self.model = LogisticRegression(
            multi_class="multinomial",
            max_iter=1000
        )

    def _label_rule(self, rain: float) -> int:
        if rain < 1:
            return 0   # Khô
        elif rain < 10:
            return 1   # Bình thường
        return 2       # Ẩm

    def train(self, df: pd.DataFrame):
        X = df[["tmean", "wind_max", "rain"]].values
        y = df["rain"].apply(self._label_rule).values

        X_scaled = self.scaler.fit_transform(X)
        self.model.fit(X_scaled, y)

    def predict(self, tmean, wind, rain) -> str:
        X = np.array([[tmean, wind, rain]])
        X_scaled = self.scaler.transform(X)
        pred = self.model.predict(X_scaled)[0]

        return ["Khô", "Bình thường", "Ẩm"][pred]
