# analyze.py
import datetime
import pandas as pd
import requests  # Cần import thư viện này để gọi API
import numpy as np
import matplotlib.pyplot as plt
import mplcyberpunk
from typing import Tuple, Optional

from matplotlib.backends.backend_qtagg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure
from PyQt6.QtCore import Qt
from PyQt6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QLabel, 
    QSizePolicy, QWidget, QFrame, QScrollArea, QApplication
)

plt.style.use("cyberpunk")

class ProvinceAnalysisWindow(QDialog):
    """Placeholder window for province click."""
    def __init__(self, province_name: str, parent=None):
        super().__init__(parent)
        self.setWindowTitle(f"Analysis - {province_name}")
        self.setMinimumSize(400, 300)
        layout = QVBoxLayout()
        layout.addWidget(QLabel(f"Analysis for {province_name} (not implemented)"))
        self.setLayout(layout)
        self.show()

class CoordinateAnalysisWindow(QDialog):
    def __init__(self, lat: float, lon: float, weather_data: Optional[dict] = None, parent=None):
        super().__init__(parent)
        self.lat = lat
        self.lon = lon
        self.weather_data = weather_data 

        location_text = f"{lat:.3f}, {lon:.3f}"
        if self.weather_data and 'location' in self.weather_data:
            loc = self.weather_data['location']
            location_text = loc.get('full', location_text)

        self.setWindowTitle(f"Weather Analysis: {location_text}")
        
        self._setup_window_geometry()
        self._setup_styles()
        
        # --- UI LAYOUT ---
        scroll_area = QScrollArea()
        scroll_area.setWidgetResizable(True)
        content_widget = QWidget()
        self.main_layout = QVBoxLayout()
        self.main_layout.setSpacing(20)
        self.main_layout.setContentsMargins(20, 20, 20, 20)

        # 1. Info Label
        self.info_label = QLabel(f"Địa chỉ: {location_text}")
        self.info_label.setWordWrap(True) 
        self.info_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.info_label.setStyleSheet("""
            QLabel { font-size: 16px; font-weight: bold; color: #51cf66; padding: 12px; 
            background-color: #2d3d2d; border-radius: 8px; border: 1px solid #3d4d3d; }
        """)
        self.main_layout.addWidget(self.info_label)

        # 2. Summary Cards Container (Nhiệt độ, Mưa, Gió)
        self.summary_container = QWidget()
        self.summary_layout = QHBoxLayout()
        self.summary_layout.setSpacing(15)
        self.summary_container.setLayout(self.summary_layout)
        self.main_layout.addWidget(self.summary_container)

        # --- [NEW] PHẦN HIỂN THỊ DỰ ĐOÁN AI ---
        self.prediction_frame = QFrame()
        self.prediction_frame.setStyleSheet("""
            QFrame { background-color: #2d2d3d; border-radius: 12px; border: 1px dashed #6c5ce7; padding: 15px; }
        """)
        self.prediction_frame.setVisible(False) # Ẩn đi cho đến khi có kết quả
        pred_layout = QVBoxLayout()
        
        self.lbl_pred_title = QLabel("Phân loại thời tiết")
        self.lbl_pred_title.setStyleSheet("color: #a29bfe; font-weight: bold; font-size: 14px;")
        self.lbl_pred_title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        
        self.lbl_pred_result = QLabel("Analyzing...")
        self.lbl_pred_result.setStyleSheet("color: white; font-size: 18px; font-weight: bold;")
        self.lbl_pred_result.setAlignment(Qt.AlignmentFlag.AlignCenter)
        
        pred_layout.addWidget(self.lbl_pred_title)
        pred_layout.addWidget(self.lbl_pred_result)
        self.prediction_frame.setLayout(pred_layout)
        self.main_layout.addWidget(self.prediction_frame)
        # ---------------------------------------

        # 3. Charts
        self.temp_canvas = self._add_chart_widget()
        self.precip_canvas = self._add_chart_widget()
        self.wind_canvas = self._add_chart_widget()

        content_widget.setLayout(self.main_layout)
        scroll_area.setWidget(content_widget)

        dialog_layout = QVBoxLayout()
        dialog_layout.setContentsMargins(0, 0, 0, 0)
        dialog_layout.addWidget(scroll_area)
        self.setLayout(dialog_layout)

        self._display_data()
        self.show()

    def _setup_window_geometry(self):
        screen = QApplication.primaryScreen()
        geo = screen.geometry()
        w, h = geo.width(), geo.height()
        self.setGeometry(w // 2, 0, w // 2, h)
        self.setMinimumSize(w // 2, 600)
        self.setWindowFlags(Qt.WindowType.Window)

    def _setup_styles(self):
        self.setStyleSheet("""
            QDialog, QWidget { background-color: #1e1e1e; }
            QScrollArea { border: none; }
            QScrollBar:vertical { background-color: #2d2d2d; width: 12px; border-radius: 6px; }
            QScrollBar::handle:vertical { background-color: #4a4a4a; border-radius: 6px; min-height: 20px; }
        """)

    def _add_chart_widget(self):
        fig = Figure(figsize=(12, 6), dpi=100)
        fig.patch.set_facecolor('#1e1e1e')
        canvas = FigureCanvas(fig)
        canvas.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Fixed)
        canvas.setMinimumHeight(350)
        self.main_layout.addWidget(canvas)
        return canvas

    def _display_data(self):
        # --- Update Cards from Snapshot ---
        current_temp = "N/A"
        current_wind = "N/A"
        current_rain = "N/A"

        if self.weather_data and 'weather' in self.weather_data:
            w = self.weather_data['weather']
            current_temp = f"{w.get('temp', 0)} °C"
            current_wind = f"{w.get('wind', 0)} km/h"
            current_rain = f"{w.get('precipitation', 0)} mm"
        
        self._update_summary_cards(current_wind, current_temp, current_rain)

        # --- Fetch History & Predict ---
        try:
            df = self._fetch_weather_history()
            
            self._plot_temperature_chart(df)
            self._plot_precipitation_chart(df)
            self._plot_wind_chart(df)

            # [NEW] Tính toán dữ liệu trung bình để gửi cho AI
            # Chúng ta dùng trung bình của 30 ngày qua để phân loại khí hậu vùng này
            avg_data = {
                "t_max": df["tmax"].mean(),
                "t_min": df["tmin"].mean(),
                "wind_speed": df["wind_max"].mean(),
                "rain": df["rain"].mean()
            }
            
            # Gọi API
            self._call_ml_api(avg_data)

            if not self.weather_data:
                 self._update_summary_cards(
                     f"{avg_data['wind_speed']:.1f} km/h (Avg)",
                     f"{df['tmean'].mean():.1f} °C (Avg)",
                     f"{avg_data['rain']:.1f} mm (Avg)"
                 )

        except Exception as exc:
            print(f"Chart/API Error: {exc}")

    # --- [NEW] HÀM GỌI API ---
    def _call_ml_api(self, data):
        """Gửi dữ liệu sang Python Backend (Flask) để dự đoán"""
        try:
            url = "http://127.0.0.1:5000/predict"
            # Gửi request POST
            response = requests.post(url, json=data, timeout=2)
            
            if response.status_code == 200:
                result = response.json()
                if result.get("status") == "success":
                    self.prediction_frame.setVisible(True)
                    condition = result.get("condition", "Unknown")
                    icon = result.get("icon", "")
                    color = result.get("color", "#ffffff")
                    
                    self.lbl_pred_result.setText(f"{icon} {condition}")
                    self.lbl_pred_result.setStyleSheet(f"color: {color}; font-size: 22px; font-weight: bold;")
            else:
                print("API Error:", response.text)
                
        except Exception as e:
            print(f"Cannot connect to ML API: {e}")
            # Có thể ẩn frame nếu lỗi hoặc hiện thông báo
            self.prediction_frame.setVisible(False)

    def _update_summary_cards(self, wind, temp, rain):
        for i in reversed(range(self.summary_layout.count())):
            self.summary_layout.itemAt(i).widget().setParent(None)

        self.summary_layout.addWidget(self._create_card("🌬️", wind, "Wind", "#3498db"))
        self.summary_layout.addWidget(self._create_card("🌡️", temp, "Temp", "#e74c3c"))
        self.summary_layout.addWidget(self._create_card("🌧️", rain, "Rain", "#2ecc71"))

    def _create_card(self, icon, value, label, color):
        card = QFrame()
        card.setStyleSheet("QFrame { background-color: #2d2d2d; border-radius: 12px; border: 1px solid #3d3d3d; padding: 20px; }")
        l = QVBoxLayout()
        l.setAlignment(Qt.AlignmentFlag.AlignCenter)
        
        lb_icon = QLabel(icon)
        lb_icon.setStyleSheet("font-size: 40px; background: transparent;")
        lb_icon.setAlignment(Qt.AlignmentFlag.AlignCenter)
        
        lb_val = QLabel(value)
        lb_val.setStyleSheet("font-size: 24px; font-weight: bold; color: #ffffff; background: transparent;")
        lb_val.setAlignment(Qt.AlignmentFlag.AlignCenter)
        
        lb_lbl = QLabel(label)
        lb_lbl.setStyleSheet(f"font-size: 14px; color: {color}; background: transparent;")
        lb_lbl.setAlignment(Qt.AlignmentFlag.AlignCenter)

        l.addWidget(lb_icon)
        l.addWidget(lb_val)
        l.addWidget(lb_lbl)
        card.setLayout(l)
        return card

    # ... (Giữ nguyên các hàm _fetch_weather_history, _plot... bên dưới) ...
    def _fetch_weather_history(self) -> pd.DataFrame:
        end = datetime.date.today() - datetime.timedelta(days=1)
        start = end - datetime.timedelta(days=29)
        
        url = "https://archive-api.open-meteo.com/v1/archive"
        params = {
            "latitude": self.lat, "longitude": self.lon,
            "start_date": start.isoformat(), "end_date": end.isoformat(),
            "daily": "temperature_2m_max,temperature_2m_min,temperature_2m_mean,rain_sum,snowfall_sum,windspeed_10m_max",
            "timezone": "auto"
        }
        
        resp = requests.get(url, params=params, timeout=10)
        resp.raise_for_status()
        daily = resp.json().get("daily", {})
        
        df = pd.DataFrame({
            "date": pd.to_datetime(daily["time"]),
            "tmax": daily["temperature_2m_max"],
            "tmin": daily["temperature_2m_min"],
            "tmean": daily.get("temperature_2m_mean", []),
            "rain": daily["rain_sum"],
            "snow": daily["snowfall_sum"],
            "wind_max": daily.get("windspeed_10m_max", []),
        })
        
        if df["tmean"].isnull().all(): df["tmean"] = (df["tmax"] + df["tmin"]) / 2
        df = df.fillna(0)
        return df

    def _plot_temperature_chart(self, df):
        fig = self.temp_canvas.figure
        ax = fig.add_subplot(111)
        ax.clear()
        
        x = np.arange(len(df))
        labels = df["date"].dt.strftime("%d/%m")
        
        ax.plot(x, df["tmax"], label="Max", color="#ff6b6b", marker='o')
        ax.plot(x, df["tmin"], label="Min", color="#4dabf7", marker='o')
        ax.fill_between(x, df["tmin"], df["tmax"], alpha=0.1, color="#4dabf7")
        
        self._style_chart(ax, "Temperature History (°C)", x, labels)
        self.temp_canvas.draw()

    def _plot_precipitation_chart(self, df):
        fig = self.precip_canvas.figure
        ax = fig.add_subplot(111)
        ax.clear()
        
        x = np.arange(len(df))
        ax.bar(x, df["rain"], label="Rain", color="#4dabf7")
        ax.bar(x, df["snow"], bottom=df["rain"], label="Snow", color="#adb5bd")
        
        self._style_chart(ax, "Precipitation (mm)", x, df["date"].dt.strftime("%d/%m"))
        self.precip_canvas.draw()

    def _plot_wind_chart(self, df):
        fig = self.wind_canvas.figure
        ax = fig.add_subplot(111)
        ax.clear()
        
        x = np.arange(len(df))
        ax.bar(x, df["wind_max"], label="Wind Max", color="#3498db")
        
        self._style_chart(ax, "Wind Speed (km/h)", x, df["date"].dt.strftime("%d/%m"))
        self.wind_canvas.draw()

    def _style_chart(self, ax, title, x, labels):
        ax.set_title(title, color='white', pad=20)
        ax.set_facecolor('#1e1e1e')
        ax.grid(True, alpha=0.2, linestyle='--')
        
        tick_step = max(1, len(x) // 6)
        ax.set_xticks(x[::tick_step])
        ax.set_xticklabels(labels[::tick_step], rotation=45, color='#b0b0b0')
        ax.tick_params(colors='#b0b0b0')
        for spine in ax.spines.values(): spine.set_color('#4a4a4a')
        ax.legend(facecolor='#2d2d2d', labelcolor='#e0e0e0')