#!/usr/bin/env python3
import sys
import os

# --- CẤU HÌNH TỐI ƯU CHO WINDOWS (Sửa lỗi lag) ---
# 1. Ép PyQt dùng ANGLE (Chạy OpenGL trên nền DirectX) -> Fix lỗi GLES3 Context
os.environ["QT_OPENGL"] = "angle"
os.environ["QT_ANGLE_PLATFORM"] = "d3d11" # Hoặc "warp" nếu máy cực yếu

# 2. Xóa các dòng --disable cũ đi. Chỉ giữ lại disable-gpu-compositing nếu thực sự cần thiết.
# Nếu máy bạn vẫn crash, hãy thử bỏ comment dòng dưới đây, nhưng ĐỪNG dùng disable-software-rasterizer
# os.environ["QTWEBENGINE_CHROMIUM_FLAGS"] = "--disable-gpu-compositing"
# -----------------------------------------------------------------------

from PyQt6.QtWidgets import QApplication, QMainWindow
from PyQt6.QtCore import QSize
from analyze import ProvinceAnalysisWindow, CoordinateAnalysisWindow
from map_view import MapView

class WeatherForecastApp(QMainWindow):
    """Main application window"""

    def __init__(self):
        super().__init__()
        self.setup_ui()
        self.setup_connections()

    def setup_ui(self):
        self.setWindowTitle("Vietnam Weather Forecast")
        self.setGeometry(100, 100, 1200, 700)
        self.setMinimumSize(QSize(800, 600))
        self.map_view = MapView(self)
        self.setCentralWidget(self.map_view)
        # Bỏ style sheet phức tạp nếu không cần thiết để load nhanh hơn
        self.setStyleSheet("QMainWindow { background-color: #f5f5f5; }")

    def setup_connections(self):
        bridge = self.map_view.get_bridge()
        bridge.map_clicked.connect(self.on_map_clicked)

    def on_map_clicked(self, lat: float, lon: float):
        # In ít log hơn để đỡ lag console
        print(f"Clicked: {lat}, {lon}") 
        self.statusBar().showMessage(f"Selected: {lat}, {lon}")
        if hasattr(self, "coord_window") and self.coord_window is not None:
            try:
                self.coord_window.close()
            except Exception:
                pass
        self.coord_window = CoordinateAnalysisWindow(lat, lon, self)

def main():
    # Thêm cấu hình Attribute HighDpi cho màn hình nét
    QApplication.setHighDpiScaleFactorRoundingPolicy(
        Qt.HighDpiScaleFactorRoundingPolicy.PassThrough)
    
    app = QApplication(sys.argv)
    app.setApplicationName("Vietnam Weather Forecast")
    
    window = WeatherForecastApp()
    window.show()

    sys.exit(app.exec())

# Cần import thêm Qt để chỉnh HighDpi (tùy chọn)
from PyQt6.QtCore import Qt 

if __name__ == "__main__":
    main()