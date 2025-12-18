import datetime
import matplotlib.dates as mdates
from typing import List, Tuple
import pandas as pd
import requests
import matplotlib.pyplot as plt 
from matplotlib.backends.backend_qtagg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure
from PyQt6.QtCore import Qt
from PyQt6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QLabel, 
    QSizePolicy, QWidget, QFrame, QScrollArea, QApplication
)
from PyQt6.QtGui import QScreen
from cycler import cycler
import numpy as np
import mplcyberpunk

plt.style.use("cyberpunk")

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
    Shows a 30-day weather history for a lat/lng point
    using Open-Meteo archive API and matplotlib embedded in PyQt.
    Displays:
    - Summary cards: Avg Wind, Avg Temp, Total Rain
    - Temperature chart over 30 days
    - Rain and Snow precipitation chart
    """

    def __init__(self, lat: float, lon: float, parent=None):
        super().__init__(parent)
        self.lat = lat
        self.lon = lon

        self.setWindowTitle(f"30-day Weather Analysis @ {lat:.3f}, {lon:.3f}")
        
        # Get screen geometry and position window on right half
        screen = QApplication.primaryScreen()
        screen_geometry = screen.geometry()
        screen_width = screen_geometry.width()
        screen_height = screen_geometry.height()
        
        # Calculate right half position and size
        window_width = screen_width // 2
        window_height = screen_height
        window_x = screen_width // 2
        window_y = 0
        
        # Set window geometry to right half of screen
        self.setGeometry(window_x, window_y, window_width, window_height)
        self.setMinimumSize(window_width, 600)
        
        # Make window non-modal so it doesn't block the main window
        self.setWindowFlags(Qt.WindowType.Window)

        # Apply dark theme to the dialog
        self.setStyleSheet("""
            QDialog {
                background-color: #1e1e1e;
            }
        """)

        # Create scroll area
        scroll_area = QScrollArea()
        scroll_area.setWidgetResizable(True)
        scroll_area.setStyleSheet("""
            QScrollArea {
                background-color: #1e1e1e;
                border: none;
            }
            QScrollBar:vertical {
                background-color: #2d2d2d;
                width: 12px;
                border-radius: 6px;
            }
            QScrollBar::handle:vertical {
                background-color: #4a4a4a;
                border-radius: 6px;
                min-height: 20px;
            }
            QScrollBar::handle:vertical:hover {
                background-color: #5a5a5a;
            }
        """)

        # Content widget for scroll area
        content_widget = QWidget()
        main_layout = QVBoxLayout()
        main_layout.setSpacing(20)
        main_layout.setContentsMargins(20, 20, 20, 20)

        # Info label
        self.info_label = QLabel("Loading 30-day weather data...")
        self.info_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.info_label.setStyleSheet("""
            QLabel {
                font-size: 14px;
                font-weight: bold;
                color: #e0e0e0;
                padding: 12px;
                background-color: #2d2d2d;
                border-radius: 8px;
                border: 1px solid #3d3d3d;
            }
        """)
        main_layout.addWidget(self.info_label)

        # Summary cards container
        self.summary_container = QWidget()
        self.summary_layout = QHBoxLayout()
        self.summary_layout.setSpacing(15)
        self.summary_container.setLayout(self.summary_layout)
        main_layout.addWidget(self.summary_container)

        # Temperature chart (first chart) - increased height
        self.temp_figure = Figure(figsize=(12, 6), dpi=100)
        self.temp_figure.patch.set_facecolor('#1e1e1e')
        self.temp_canvas = FigureCanvas(self.temp_figure)
        self.temp_canvas.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Fixed)
        self.temp_canvas.setMinimumHeight(400)
        main_layout.addWidget(self.temp_canvas)

        # Precipitation chart (second chart) - increased height
        self.precip_figure = Figure(figsize=(12, 6), dpi=100)
        self.precip_figure.patch.set_facecolor('#1e1e1e')
        self.precip_canvas = FigureCanvas(self.precip_figure)
        self.precip_canvas.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Fixed)
        self.precip_canvas.setMinimumHeight(400)
        main_layout.addWidget(self.precip_canvas)

        # Wind chart (third chart) - increased height
        self.wind_figure = Figure(figsize=(12, 6), dpi=100)
        self.wind_figure.patch.set_facecolor('#1e1e1e')
        self.wind_canvas = FigureCanvas(self.wind_figure)
        self.wind_canvas.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Fixed)
        self.wind_canvas.setMinimumHeight(400)
        main_layout.addWidget(self.wind_canvas)

        content_widget.setLayout(main_layout)
        content_widget.setStyleSheet("background-color: #1e1e1e;")
        scroll_area.setWidget(content_widget)

        # Set scroll area as main layout
        dialog_layout = QVBoxLayout()
        dialog_layout.setContentsMargins(0, 0, 0, 0)
        dialog_layout.addWidget(scroll_area)
        self.setLayout(dialog_layout)

        # Fetch data and draw charts synchronously
        self._load_and_plot()
        self.show()

    def _get_date_range(self) -> Tuple[str, str]:
        """Return (start_date, end_date) strings for the last 30 days."""
        end = datetime.date.today() - datetime.timedelta(days=1)
        start = end - datetime.timedelta(days=29)  # 30 days total (inclusive)
        return start.isoformat(), end.isoformat()

    def _fetch_weather_df(self) -> pd.DataFrame:
        """
        Fetch 30 days of daily weather data from Open-Meteo
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
                "temperature_2m_mean,"
                "rain_sum,"
                "snowfall_sum,"
                "windspeed_10m_max"
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
                "tmean": daily.get("temperature_2m_mean", []),
                "rain": daily["rain_sum"],
                "snow": daily["snowfall_sum"],
                "wind_max": daily.get("windspeed_10m_max", []),
            })

            # Calculate mean temperature if not available
            if len(df["tmean"]) == 0 or all(pd.isna(df["tmean"])):
                df["tmean"] = (df["tmax"] + df["tmin"]) / 2

            # Safety: replace None → 0 for precipitation and wind
            df[["rain", "snow"]] = df[["rain", "snow"]].fillna(0.0)
            df["wind_max"] = df["wind_max"].fillna(0.0)

            return df

        except Exception as exc:  # noqa: BLE001
            raise RuntimeError(f"Failed to fetch data from Open-Meteo: {exc}") from exc

    def _create_summary_card(self, icon: str, value_with_unit: str, label: str, icon_color: str) -> QFrame:
        """Create a summary card widget with icon, value, and label."""
        card = QFrame()
        card.setFrameShape(QFrame.Shape.StyledPanel)
        card.setStyleSheet("""
            QFrame {
                background-color: #2d2d2d;
                border-radius: 12px;
                border: 1px solid #3d3d3d;
                padding: 25px;
            }
        """)
        
        card_layout = QVBoxLayout()
        card_layout.setSpacing(10)
        card_layout.setAlignment(Qt.AlignmentFlag.AlignCenter)
        
        # Icon label
        icon_label = QLabel(icon)
        icon_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        icon_label.setStyleSheet(f"""
            QLabel {{
                font-size: 52px;
                background: transparent;
            }}
        """)
        card_layout.addWidget(icon_label)
        
        # Value with unit label
        value_label = QLabel(value_with_unit)
        value_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        value_label.setStyleSheet("""
            QLabel {
                font-size: 32px;
                font-weight: bold;
                color: #ffffff;
                background: transparent;
            }
        """)
        card_layout.addWidget(value_label)
        
        # Label text
        label_widget = QLabel(label)
        label_widget.setAlignment(Qt.AlignmentFlag.AlignCenter)
        label_widget.setStyleSheet("""
            QLabel {
                font-size: 14px;
                color: #b0b0b0;
                background: transparent;
            }
        """)
        card_layout.addWidget(label_widget)
        
        card.setLayout(card_layout)
        return card

    def _load_and_plot(self) -> None:
        """Load data and create all visualizations."""
        try:
            df = self._fetch_weather_df()
        except Exception as exc:  # noqa: BLE001
            print(exc)
            self.info_label.setText(f"Error: {str(exc)}")
            self.info_label.setStyleSheet("""
                QLabel {
                    font-size: 14px;
                    font-weight: bold;
                    color: #ff6b6b;
                    padding: 12px;
                    background-color: #3d2d2d;
                    border-radius: 8px;
                    border: 1px solid #4d3d3d;
                }
            """)
            return

        # Calculate summary statistics
        avg_wind = df["wind_max"].mean()
        avg_temp = df["tmean"].mean()
        avg_rain = df["rain"].mean()

        # Clear existing summary cards
        for i in reversed(range(self.summary_layout.count())):
            self.summary_layout.itemAt(i).widget().setParent(None)

        # Create and add summary cards
        wind_card = self._create_summary_card(
            "🌬️",
            f"{avg_wind:.1f} km/h",
            "Avg Wind",
            "#3498db"
        )
        temp_card = self._create_summary_card(
            "🌡️",
            f"{avg_temp:.1f} °C",
            "Avg Temp",
            "#e74c3c"
        )
        rain_card = self._create_summary_card(
            "🌧️",
            f"{avg_rain:.1f} mm",
            "Avg Rain",
            "#2ecc71"
        )

        self.summary_layout.addWidget(wind_card)
        self.summary_layout.addWidget(temp_card)
        self.summary_layout.addWidget(rain_card)

        # Plot temperature chart
        self._plot_temperature_chart(df)

        # Plot precipitation chart
        self._plot_precipitation_chart(df)

        # Plot wind chart
        self._plot_wind_chart(df)

        # Update info label
        self.info_label.setText(
            f"30-day weather analysis for {self.lat:.3f}°N, {self.lon:.3f}°E"
        )
        self.info_label.setStyleSheet("""
            QLabel {
                font-size: 14px;
                font-weight: bold;
                color: #51cf66;
                padding: 12px;
                background-color: #2d3d2d;
                border-radius: 8px;
                border: 1px solid #3d4d3d;
            }
        """)

    def _plot_temperature_chart(self, df: pd.DataFrame) -> None:
        """Plot temperature chart over 30 days."""
        ax = self.temp_figure.add_subplot(111)
        ax.clear()
        ax.set_facecolor('#1e1e1e')

        x = np.arange(len(df))
        tick_step = max(1, len(df) // 6)
        ticks = x[::tick_step]
        labels = df["date"].dt.strftime("%d %b")[::tick_step]

        ax.set_xticks(ticks)
        ax.set_xticklabels(labels, rotation=45, ha="right", color='#e0e0e0')

        # Plot max, min, and mean temperatures
        ax.plot(x, df["tmax"], label="Max Temp", linewidth=2.5, marker='o', markersize=5, color="#ff6b6b")
        ax.plot(x, df["tmin"], label="Min Temp", linewidth=2.5, marker='o', markersize=5, color="#4dabf7")
        ax.plot(x, df["tmean"], label="Avg Temp", linewidth=2.5, marker='s', markersize=4, color="#51cf66", linestyle='--')

        # Fill area between max and min
        ax.fill_between(x, df["tmin"], df["tmax"], alpha=0.15, color="#4dabf7")

        ax.set_ylabel("Temperature (°C)", fontsize=12, fontweight='bold', color='#e0e0e0')
        ax.set_xlabel("Date", fontsize=12, fontweight='bold', color='#e0e0e0')
        ax.set_title("Temperature Over 30 Days", fontsize=14, fontweight='bold', pad=20, color='#ffffff')
        ax.legend(loc='best', framealpha=0.9, facecolor='#2d2d2d', edgecolor='#3d3d3d', labelcolor='#e0e0e0')
        ax.grid(True, alpha=0.2, linestyle='--', color='#4a4a4a')
        ax.tick_params(colors='#b0b0b0')
        ax.spines['bottom'].set_color('#4a4a4a')
        ax.spines['top'].set_color('#4a4a4a')
        ax.spines['right'].set_color('#4a4a4a')
        ax.spines['left'].set_color('#4a4a4a')

        self.temp_figure.subplots_adjust(
            top=0.88,     # more space for title
            bottom=0.01,
            left=0.08,
            right=0.97
        )
        self.temp_canvas.draw()

    def _plot_precipitation_chart(self, df: pd.DataFrame) -> None:
        """Plot rain and snow precipitation chart."""
        ax = self.precip_figure.add_subplot(111)
        ax.clear()
        ax.set_facecolor('#1e1e1e')

        x = np.arange(len(df))
        tick_step = max(1, len(df) // 6)
        ticks = x[::tick_step]
        labels = df["date"].dt.strftime("%d %b")[::tick_step]

        ax.set_xticks(ticks)
        ax.set_xticklabels(labels, rotation=45, ha="right", color='#e0e0e0')

        # Plot rain bars
        rain_bar = ax.bar(
            x,
            df["rain"],
            label="Rain (mm)",
            color="#4dabf7",
            alpha=0.85,
            edgecolor="#339af0",
            linewidth=1.2
        )

        # Plot snow bars on top
        ax.bar(
            x,
            df["snow"],
            bottom=df["rain"],
            label="Snow (mm)",
            color="#adb5bd",
            alpha=0.9,
            edgecolor="#868e96",
            linewidth=1.2
        )

        ax.set_ylim(bottom=0)
        ax.set_ylabel("Precipitation (mm)", fontsize=12, fontweight='bold', color='#e0e0e0')
        ax.set_xlabel("Date", fontsize=12, fontweight='bold', color='#e0e0e0')
        ax.set_title("Daily Precipitation (Rain + Snow)", fontsize=14, fontweight='bold', pad=20, color='#ffffff')
        ax.legend(loc='best', framealpha=0.9, facecolor='#2d2d2d', edgecolor='#3d3d3d', labelcolor='#e0e0e0')
        ax.grid(True, alpha=0.2, linestyle='--', axis='y', color='#4a4a4a')
        ax.tick_params(colors='#b0b0b0')
        ax.spines['bottom'].set_color('#4a4a4a')
        ax.spines['top'].set_color('#4a4a4a')
        ax.spines['right'].set_color('#4a4a4a')
        ax.spines['left'].set_color('#4a4a4a')

        self.precip_figure.subplots_adjust(
            top=0.88,     # more space for title
            bottom=0.01,
            left=0.08,
            right=0.97
        )
        self.precip_canvas.draw()

    def _plot_wind_chart(self, df: pd.DataFrame) -> None:
        """Plot wind speed chart over 30 days."""
        ax = self.wind_figure.add_subplot(111)
        ax.clear()
        ax.set_facecolor('#1e1e1e')

        x = np.arange(len(df))
        tick_step = max(1, len(df) // 6)
        ticks = x[::tick_step]
        labels = df["date"].dt.strftime("%d %b")[::tick_step]

        ax.set_xticks(ticks)
        ax.set_xticklabels(labels, rotation=45, ha="right", color='#e0e0e0')

        # Plot wind speed as bars
        ax.bar(
            x,
            df["wind_max"],
            label="Max Wind Speed",
            color="#4dabf7",
            alpha=0.85,
            edgecolor="#339af0",
            linewidth=1.2
        )

        ax.set_ylim(bottom=0)
        ax.set_ylabel("Wind Speed (km/h)", fontsize=12, fontweight='bold', color='#e0e0e0')
        ax.set_xlabel("Date", fontsize=12, fontweight='bold', color='#e0e0e0')
        ax.set_title("Wind Speed Over 30 Days", fontsize=14, fontweight='bold', pad=20, color='#ffffff')
        ax.legend(loc='best', framealpha=0.9, facecolor='#2d2d2d', edgecolor='#3d3d3d', labelcolor='#e0e0e0')
        ax.grid(True, alpha=0.2, linestyle='--', axis='y', color='#4a4a4a')
        ax.tick_params(colors='#b0b0b0')
        ax.spines['bottom'].set_color('#4a4a4a')
        ax.spines['top'].set_color('#4a4a4a')
        ax.spines['right'].set_color('#4a4a4a')
        ax.spines['left'].set_color('#4a4a4a')

        self.wind_figure.subplots_adjust(
            top=0.88,     # more space for title
            bottom=0.01,
            left=0.08,
            right=0.97
        )
        self.wind_canvas.draw()
