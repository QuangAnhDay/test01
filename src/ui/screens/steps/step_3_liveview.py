import os
import sys

# === PATH FIX: Cho phép chạy trực tiếp ===
_PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
if _PROJECT_ROOT not in sys.path:
    sys.path.insert(0, _PROJECT_ROOT)

# ==========================================
# STEP 3 - LIVEVIEW (Camera & Đếm ngược)
# ==========================================
"""
Màn hình live camera + đếm ngược + chụp ảnh.
"""

from PyQt5.QtWidgets import QWidget, QLabel, QPushButton, QVBoxLayout, QHBoxLayout
from PyQt5.QtCore import Qt


def create_liveview_screen(app):
    """Tạo màn hình camera live với đếm ngược."""
    screen = QWidget()
    layout = QVBoxLayout(screen)
    layout.setSpacing(10)
    layout.setContentsMargins(20, 20, 20, 20)

    # Camera view
    app.camera_label = QLabel("Starting camera...")
    app.camera_label.setAlignment(Qt.AlignCenter)
    app.camera_label.setStyleSheet("""
        background-color: #000; 
        border: 4px solid #e94560; 
        border-radius: 15px;
    """)
    app.camera_label.setMinimumSize(900, 500)
    layout.addWidget(app.camera_label, stretch=4)

    # Info bar
    info_widget = QWidget()
    info_layout = QHBoxLayout(info_widget)

    app.photo_count_label = QLabel("Photos: 0/10")
    app.photo_count_label.setObjectName("InfoLabel")
    info_layout.addWidget(app.photo_count_label)

    app.countdown_label = QLabel("")
    app.countdown_label.setObjectName("CountdownLabel")
    app.countdown_label.setAlignment(Qt.AlignCenter)
    info_layout.addWidget(app.countdown_label, stretch=1)

    app.btn_capture_start = QPushButton("📸 START CAPTURING")
    app.btn_capture_start.setObjectName("GreenBtn")
    app.btn_capture_start.setFixedSize(200, 60)
    app.btn_capture_start.hide()
    app.btn_capture_start.clicked.connect(app.start_capture_session)

    app.status_label = QLabel("Preparing...")
    app.status_label.setObjectName("InfoLabel")
    app.status_label.setAlignment(Qt.AlignRight)
    info_layout.addWidget(app.status_label)

    layout.addWidget(app.btn_capture_start, alignment=Qt.AlignCenter)
    layout.addWidget(info_widget)

    return screen

# ==========================================
# KHỐI TEST STANDALONE
# ==========================================
if __name__ == "__main__":
    from PyQt5.QtWidgets import QApplication

    # Giả lập đối tượng app
    class MockApp:
        def __init__(self):
            self.camera_label = None
            self.photo_count_label = None
            self.countdown_label = None
            self.btn_capture_start = None
            self.status_label = None

        def start_capture_session(self):
            print("Bắt đầu phiên chụp ảnh!")

    app_qt = QApplication(sys.argv)
    
    # Áp dụng STYLE cho app test
    from src.ui.styles import GLOBAL_STYLESHEET
    app_qt.setStyleSheet(GLOBAL_STYLESHEET)

    mock_app = MockApp()
    window = create_liveview_screen(mock_app)
    window.showFullScreen()
    sys.exit(app_qt.exec_())
