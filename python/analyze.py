import datetime
from typing import List, Tuple

import requests
from matplotlib.backends.backend_qtagg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure
from PyQt6.QtCore import Qt
from PyQt6.QtWidgets import QDialog, QVBoxLayout, QLabel, QSizePolicy


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
        start = end - datetime.timedelta(days=90)
        return start.isoformat(), end.isoformat()

    def _fetch_three_months_data(self) -> Tuple[List[str], List[float], List[float]]:
        """
        Call Open‑Meteo archive API and return (dates, tmax, tmin).

        Docs: https://archive-api.open-meteo.com/
        """
        start_date, end_date = self._get_date_range()

        params = {
            "latitude": self.lat,
            "longitude": self.lon,
            "start_date": start_date,
            "end_date": end_date,
            "daily": "temperature_2m_max,temperature_2m_min",
            "timezone": "auto",
        }

        url = "https://archive-api.open-meteo.com/v1/archive"

        try:
            resp = requests.get(url, params=params, timeout=15)
            resp.raise_for_status()
            data = resp.json()

            daily = data.get("daily", {})
            dates = daily.get("time", [])
            tmax = daily.get("temperature_2m_max", [])
            tmin = daily.get("temperature_2m_min", [])

            if not dates or not tmax or not tmin:
                raise ValueError("Missing daily temperature data")

            return dates, tmax, tmin
        except Exception as exc:  # noqa: BLE001
            # Bubble up a simple error message; plotting layer will handle it.
            raise RuntimeError(f"Failed to fetch data from Open‑Meteo: {exc}") from exc

    def _load_and_plot(self) -> None:
        """Fetch data and draw the matplotlib chart in the Qt dialog."""
        ax = self.figure.add_subplot(111)
        ax.clear()

        try:
            dates, tmax, tmin = self._fetch_three_months_data()
        except Exception as exc:  # noqa: BLE001
            self.info_label.setText(str(exc))
            self.canvas.draw()
            return

        # Use index on x‑axis; show first/last dates in title for context.
        x = list(range(len(dates)))
        ax.plot(x, tmax, label="Max temp (°C)", color="red", linewidth=1.2)
        ax.plot(x, tmin, label="Min temp (°C)", color="blue", linewidth=1.2)

        ax.set_xlabel("Day (last 3 months)")
        ax.set_ylabel("Temperature (°C)")
        ax.set_title(f"Daily max/min temperature\n{dates[0]} → {dates[-1]}")
        ax.grid(True, linestyle="--", alpha=0.3)
        ax.legend()

        self.info_label.setText(
            f"3‑month daily temperature history for {self.lat:.3f}, {self.lon:.3f}"
        )
        self.figure.tight_layout()
        self.canvas.draw()
