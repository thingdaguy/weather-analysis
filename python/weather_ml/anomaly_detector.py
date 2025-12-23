import numpy as np
import pandas as pd
from sklearn.ensemble import IsolationForest

class WeatherAnomalyDetector:
    def __init__(self):
        self.model = IsolationForest(
            contamination=0.1,
            random_state=42
        )

    def fit_predict(self, df: pd.DataFrame) -> pd.DataFrame:
        X = df[["tmean", "rain", "wind_max"]].values
        preds = self.model.fit_predict(X)

        df = df.copy()
        df["anomaly"] = preds
        df["anomaly_label"] = df["anomaly"].apply(
            lambda x: "Bất thường" if x == -1 else "Bình thường"
        )
        return df
