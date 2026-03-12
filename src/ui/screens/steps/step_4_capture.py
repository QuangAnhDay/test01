import os
import sys

# === PATH FIX: Cho phép chạy trực tiếp ===
_PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
if _PROJECT_ROOT not in sys.path:
    sys.path.insert(0, _PROJECT_ROOT)

# ==========================================
# STEP 4 - CAPTURE (Hiển thị/Chọn ảnh vừa chụp)
# ==========================================
"""
Màn hình chọn ảnh từ các ảnh đã chụp.
"""

from PyQt5.QtWidgets import (QWidget, QLabel, QPushButton, QVBoxLayout,
                             QScrollArea, QGridLayout)
from PyQt5.QtCore import Qt


def create_photo_select_screen(app):
    """Tạo màn hình chọn ảnh từ các ảnh đã chụp."""
    screen = QWidget()
    layout = QVBoxLayout(screen)
    layout.setSpacing(15)
    layout.setContentsMargins(20, 20, 20, 20)

    app.photo_select_title = QLabel("SELECT PHOTOS")
    app.photo_select_title.setObjectName("TitleLabel")
    app.photo_select_title.setAlignment(Qt.AlignCenter)
    layout.addWidget(app.photo_select_title)

    # Timer Label
    app.lbl_selection_timer = QLabel("Time remaining: 00:00")
    app.lbl_selection_timer.setAlignment(Qt.AlignCenter)
    app.lbl_selection_timer.setStyleSheet("font-family: 'Cooper Black'; font-size: 24px; color: #ffd700; font-weight: bold;")
    layout.addWidget(app.lbl_selection_timer)

    # Scroll area for photo grid
    scroll = QScrollArea()
    scroll.setWidgetResizable(True)
    scroll.setStyleSheet("background-color: transparent;")

    app.photo_grid_widget = QWidget()
    app.photo_grid_layout = QGridLayout(app.photo_grid_widget)
    app.photo_grid_layout.setSpacing(15)
    scroll.setWidget(app.photo_grid_widget)
    layout.addWidget(scroll, stretch=1)

    app.btn_confirm_photos = QPushButton("CONFIRM SELECTION")
    app.btn_confirm_photos.setObjectName("GreenBtn")
    app.btn_confirm_photos.setEnabled(False)
    app.btn_confirm_photos.clicked.connect(app.confirm_photo_selection)
    layout.addWidget(app.btn_confirm_photos, alignment=Qt.AlignCenter)

    return screen

# ==========================================
# KHỐI TEST STANDALONE
# ==========================================
if __name__ == "__main__":
    from PyQt5.QtWidgets import QApplication

    # Giả lập đối tượng app
    class MockApp:
        def __init__(self):
            self.photo_select_title = None
            self.lbl_selection_timer = None
            self.photo_grid_layout = None
            self.btn_confirm_photos = None

        def confirm_photo_selection(self):
            print("Xác nhận chọn ảnh!")

    app_qt = QApplication(sys.argv)
    
    # Áp dụng STYLE cho app test
    from src.ui.styles import GLOBAL_STYLESHEET
    app_qt.setStyleSheet(GLOBAL_STYLESHEET)

    mock_app = MockApp()
    window = create_photo_select_screen(mock_app)
    window.showFullScreen()
    sys.exit(app_qt.exec_())
