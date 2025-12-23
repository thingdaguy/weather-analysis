#!/usr/bin/env python3
import sys
import os

# --- CẤU HÌNH TỐI ƯU CHO WINDOWS ---
os.environ["QT_OPENGL"] = "angle"
os.environ["QT_ANGLE_PLATFORM"] = "d3d11"
# os.environ["QTWEBENGINE_CHROMIUM_FLAGS"] = "--disable-gpu-compositing"

from PyQt6.QtWidgets import QApplication, QMainWindow
from PyQt6.QtCore import Qt
from analyze import CoordinateAnalysisWindow
from map_view import MapView

class WeatherForecastApp(QMainWindow):
    """Main application window"""

    def __init__(self):
        super().__init__()
        self.setup_ui()
        self.setup_connections()

    def setup_ui(self):
        self.setWindowTitle("Vietnam Weather Forecast")
        self.map_view = MapView(self)
        self.setCentralWidget(self.map_view)
        self.setStyleSheet("QMainWindow { background-color: #f5f5f5; }")

    def setup_connections(self):
        bridge = self.map_view.get_bridge()
        bridge.map_clicked.connect(self.on_map_clicked)

    def on_map_clicked(self, lat: float, lon: float, data: dict):
        """
        Nhận tín hiệu click từ bản đồ.
        data: Là dictionary chứa thông tin location và weather từ JS.
        """
        # Đóng cửa sổ cũ nếu đang mở
        if hasattr(self, "coord_window") and self.coord_window is not None:
            try:
                self.coord_window.close()
            except Exception:
                pass
        
        # Truyền data vào cửa sổ phân tích
        self.coord_window = CoordinateAnalysisWindow(lat, lon, weather_data=data, parent=self)

def main():
    QApplication.setHighDpiScaleFactorRoundingPolicy(
        Qt.HighDpiScaleFactorRoundingPolicy.PassThrough)
    
    app = QApplication(sys.argv)
    app.setApplicationName("Vietnam Weather Forecast")
    
    window = WeatherForecastApp()
    window.showFullScreen()

    sys.exit(app.exec())

if __name__ == "__main__":
    main()