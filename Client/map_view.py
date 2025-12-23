# map_view.py
from PyQt6.QtWidgets import QWidget, QVBoxLayout
from PyQt6.QtWebEngineWidgets import QWebEngineView
from PyQt6.QtWebChannel import QWebChannel
from PyQt6.QtCore import QUrl, pyqtSignal, QObject, pyqtSlot
from PyQt6.QtWebEngineCore import QWebEngineSettings
from pathlib import Path
import json

class MapBridge(QObject):
    """Cầu nối giao tiếp giữa Python và JavaScript"""

    # Signal gửi ra: lat, lon, và dictionary dữ liệu thời tiết
    map_clicked = pyqtSignal(float, float, dict)

    def __init__(self):
        super().__init__()

    @pyqtSlot(float, float, str)
    def on_map_click(self, lat: float, lon: float, data_json: str):
        # print(f"Bridge received click: {lat}, {lon}")
        
        try:
            # Parse chuỗi JSON thành Dictionary Python
            data = json.loads(data_json)
            print(data)
        except json.JSONDecodeError:
            print("Lỗi: Không thể đọc dữ liệu JSON từ JS")
            data = {}

        # Phát tín hiệu kèm dữ liệu đã parse
        self.map_clicked.emit(lat, lon, data)


class MapView(QWidget):
    """
    Wrapper hiển thị bản đồ Leaflet
    """
    def __init__(self, parent=None):
        super().__init__(parent)
        self.bridge = MapBridge() # Khởi tạo bridge trước
        self.setup_ui()

    def setup_ui(self):
        layout = QVBoxLayout()
        layout.setContentsMargins(0, 0, 0, 0)

        self.web_view = QWebEngineView()
        
        # Cấu hình WebEngine
        settings = self.web_view.settings()
        settings.setAttribute(QWebEngineSettings.WebAttribute.LocalContentCanAccessRemoteUrls, True)
        settings.setAttribute(QWebEngineSettings.WebAttribute.LocalContentCanAccessFileUrls, True)
        settings.setAttribute(QWebEngineSettings.WebAttribute.JavascriptEnabled, True)

        # Cấu hình WebChannel
        self.channel = QWebChannel()
        # Đăng ký object tên "pywebview" để khớp với code JS bên dưới (hoặc trong file HTML cũ)
        self.channel.registerObject("pywebview", self.bridge)
        self.web_view.page().setWebChannel(self.channel)

        # Load file map.html
        map_path = Path(__file__).parent / "map.html"
        self.web_view.setUrl(QUrl.fromLocalFile(str(map_path.absolute())))

        layout.addWidget(self.web_view)
        self.setLayout(layout)

    def get_bridge(self) -> MapBridge:
        return self.bridge