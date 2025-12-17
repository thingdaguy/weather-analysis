"""
Map view component using QWebEngineView with Leaflet.js
Handles communication between Python and JavaScript via QWebChannel
"""

from PyQt6.QtWidgets import QWidget, QVBoxLayout
from PyQt6.QtWebEngineWidgets import QWebEngineView
from PyQt6.QtWebChannel import QWebChannel
# --- SỬA 1: Import thêm pyqtSlot ---
from PyQt6.QtCore import QUrl, pyqtSignal, QObject, pyqtSlot
from pathlib import Path
from PyQt6.QtWebEngineCore import QWebEngineSettings

class MapBridge(QObject):
    """Bridge object for communication between Python and JavaScript"""

    map_clicked = pyqtSignal(float, float)

    def __init__(self):
        super().__init__()

    # --- SỬA 2: Thêm decorator @pyqtSlot để JS có thể gọi hàm này ---
    # Phải khai báo rõ kiểu dữ liệu (float, float)
    @pyqtSlot(float, float)
    def on_map_click(self, lat: float, lon: float):
        """
        Called when user clicks on the map
        Receives latitude and longitude from JavaScript
        """
        print(f"Bridge received click: {lat}, {lon}") # Log để debug
        self.map_clicked.emit(lat, lon)


class MapView(QWidget):
    """
    QWebEngineView wrapper for displaying Leaflet map
    """

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setup_ui()

    def setup_ui(self):
        """Initialize the UI components"""
        layout = QVBoxLayout()
        layout.setContentsMargins(0, 0, 0, 0)

        # Create web view
        
        self.web_view = QWebEngineView()
        
        settings = self.web_view.settings()
        settings.setAttribute(QWebEngineSettings.WebAttribute.LocalContentCanAccessRemoteUrls, True)
        settings.setAttribute(QWebEngineSettings.WebAttribute.LocalContentCanAccessFileUrls, True)
        settings.setAttribute(QWebEngineSettings.WebAttribute.JavascriptEnabled, True)

        # Create web channel
        self.channel = QWebChannel()

        # Create bridge object
        self.bridge = MapBridge()
        
        # --- SỬA 3: Đổi tên đăng ký thành "pywebview" ---
        # Lý do: Trong file HTML cũ của bạn dòng 127 đang gọi: channel.objects.pywebview
        # Nếu muốn dùng tên "mapBridge", bạn phải sửa cả trong file HTML.
        self.channel.registerObject("pywebview", self.bridge)

        # Set web channel
        self.web_view.page().setWebChannel(self.channel)

        # Load map HTML
        # Đảm bảo file map.html nằm cùng thư mục với map_view.py
        map_path = Path(__file__).parent / "map.html"
        self.web_view.setUrl(QUrl.fromLocalFile(str(map_path.absolute())))

        layout.addWidget(self.web_view)
        self.setLayout(layout)

    def get_bridge(self) -> MapBridge:
        """Get the map bridge object for signal connections"""
        return self.bridge