import datetime
import matplotlib.dates as mdates
from typing import List, Tuple
import pandas as pd
import requests
import matplotlib.pyplot as plt 
from matplotlib.backends.backend_qtagg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure
from PyQt6.QtCore import Qt
from PyQt6.QtWidgets import QDialog, QVBoxLayout, QLabel, QSizePolicy
from cycler import cycler
import numpy as np
import mplcyberpunk

plt.style.use("cyberpunk")

''''
plt.style.use('https://github.com/dhaitz/matplotlib-stylesheets/raw/master/pitayasmoothie-dark.mplstyle')
plt.rcParams["axes.prop_cycle"] = cycler(
    color=[
        "#e03131",  # red – max temp
        "#1c7ed6",  # blue – min temp
        "#2f9e44",  # green – avg / rain
        "#f08c00",  # orange – wind
        "#7048e8",  # purple – extra
    ]
)
'''

class ProvinceAnalysisWindow(QDialog):
    """Placeholder window for province click (kept for compatibility)."""

    def __init__(self, province_name: str, parent=None):
        super().__init__(parent)
        self.setWindowTitle(f"Analysis - {province_name}")
        self.setMinimumSize(400, 300)

        layout = QVBoxLayout()
        layout.addWidget(QLabel(f"Analysis for {province_name} (not implemented)"))
        self.setLayout(layout)
        self.show()


class CoordinateAnalysisWindow(QDialog):
    """
    Shows a 3‑month temperature history for a lat/lng point
    using Open‑Meteo archive API and matplotlib embedded in PyQt.
    """

    def __init__(self, lat: float, lon: float, parent=None):
        super().__init__(parent)
        self.lat = lat
        self.lon = lon

        self.setWindowTitle(f"3‑month history @ {lat:.3f}, {lon:.3f}")
        self.setMinimumSize(700, 500)

        self.figure = Figure(figsize=(6, 4), dpi=100)
        self.canvas = FigureCanvas(self.figure)
        self.canvas.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)
        self.canvas.updateGeometry()

        self.info_label = QLabel("Loading 3‑month temperature history...")
        self.info_label.setAlignment(Qt.AlignmentFlag.AlignCenter)

        layout = QVBoxLayout()
        layout.addWidget(self.info_label)
        layout.addWidget(self.canvas)
        self.setLayout(layout)

        # Fetch data and draw chart synchronously
        self._load_and_plot()
        self.show()

    def _get_date_range(self) -> Tuple[str, str]:
        """Return (start_date, end_date) strings for the last ~3 months."""
        end = datetime.date.today() - datetime.timedelta(days=1)
        start = end - datetime.timedelta(days=30)
        return start.isoformat(), end.isoformat()

    def _fetch_three_months_df(self) -> pd.DataFrame:
        """
        Fetch 3 months of daily weather data from Open-Meteo
        and return a pandas DataFrame.
        """
        start_date, end_date = self._get_date_range()

        params = {
            "latitude": self.lat,
            "longitude": self.lon,
            "start_date": start_date,
            "end_date": end_date,
            "daily": (
                "temperature_2m_max,"
                "temperature_2m_min,"
                "rain_sum,"
                "snowfall_sum"
            ),
            "timezone": "auto",
        }

        url = "https://archive-api.open-meteo.com/v1/archive"

        try:
            resp = requests.get(url, params=params, timeout=15)
            resp.raise_for_status()
            data = resp.json()

            daily = data.get("daily", {})
            if not daily:
                raise ValueError("Missing daily data")

            df = pd.DataFrame({
                "date": pd.to_datetime(daily["time"]),
                "tmax": daily["temperature_2m_max"],
                "tmin": daily["temperature_2m_min"],
                "rain": daily["rain_sum"],
                "snow": daily["snowfall_sum"],
            })

            # Safety: replace None → 0 for precipitation
            df[["rain", "snow"]] = df[["rain", "snow"]].fillna(0.0)

            return df

        except Exception as exc:  # noqa: BLE001
            raise RuntimeError(f"Failed to fetch data from Open-Meteo: {exc}") from exc

   



    def _load_and_plot(self) -> None:
        ax = self.figure.add_subplot(111)
        ax.clear()

        try:
            df = self._fetch_three_months_df()
        except Exception as exc:  # noqa: BLE001
            print(exc)
            self.info_label.setText(str(exc))
            self.canvas.draw()
            return

        x = np.arange(len(df))

        tick_step = 7
        ticks = x[::tick_step]
        labels = df["date"].dt.strftime("%d %b")[::tick_step]

        ax.set_xticks(ticks)
        ax.set_xticklabels(labels, rotation=45, ha="right")

        rain_bar = ax.bar(
            x,
            df["rain"],
            label="Rain (mm)",
        )

        ax.bar(
            x,
            df["snow"],
            bottom=df["rain"],
            label="Snow (mm)",
            color="#e7f5ff"
        )

        # Always start at zero for precipitation
        ax.set_ylim(bottom=0)

        # Title with real date range
        ax.set_title(
            f"Daily precipitation (rain + snow)\n"
        )


        ax.legend()

        self.info_label.setText(
            f"3-month daily precipitation for {self.lat:.3f}, {self.lon:.3f}"
        )

        self.figure.tight_layout()
        self.canvas.draw()

    