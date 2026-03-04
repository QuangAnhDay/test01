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

    label = QLabel("⏳ Đang xử lý ảnh...\nVui lòng chờ trong giây lát")
    label.setAlignment(Qt.AlignCenter)
    label.setStyleSheet("color: #ffd700; font-size: 28px; font-weight: bold;")
    layout.addWidget(label)

    return screen
