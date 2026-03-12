import os
import sys

# === PATH FIX: Cho phép chạy trực tiếp ===
_PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
if _PROJECT_ROOT not in sys.path:
    sys.path.insert(0, _PROJECT_ROOT)

# ==========================================
# STEP 7 - PROCESSING (Placeholder)
# ==========================================
"""
Màn hình chờ render ảnh (nếu cần xử lý nặng).
Hiện tại việc render diễn ra nhanh nên bước này được bỏ qua.
"""

from PyQt5.QtWidgets import QWidget, QLabel, QVBoxLayout
from PyQt5.QtCore import Qt


def create_processing_screen(app):
    """Placeholder - Màn hình chờ render."""
    screen = QWidget()
    layout = QVBoxLayout(screen)
    layout.setAlignment(Qt.AlignCenter)

    label = QLabel("⏳ Processing photos...\nPlease wait a moment")
    label.setAlignment(Qt.AlignCenter)
    label.setStyleSheet("color: #ffd700; font-size: 28px; font-weight: bold;")
    layout.addWidget(label)

    return screen

# ==========================================
# KHỐI TEST STANDALONE
# ==========================================
if __name__ == "__main__":
    from PyQt5.QtWidgets import QApplication

    # Giả lập đối tượng app
    class MockApp:
        pass

    app_qt = QApplication(sys.argv)
    
    # Áp dụng STYLE cho app test
    from src.ui.styles import GLOBAL_STYLESHEET
    app_qt.setStyleSheet(GLOBAL_STYLESHEET)

    mock_app = MockApp()
    window = create_processing_screen(mock_app)
    window.showFullScreen()
    sys.exit(app_qt.exec_())
