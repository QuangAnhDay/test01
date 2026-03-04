# ==========================================
# STEP 5 - FILTER (Placeholder)
# ==========================================
"""
Placeholder cho tính năng filter/sticker trong tương lai.
Hiện tại bước này được bỏ qua trong flow.
"""

from PyQt5.QtWidgets import QWidget, QLabel, QVBoxLayout
from PyQt5.QtCore import Qt


def create_filter_screen(app):
    """Placeholder - Màn hình chọn filter/sticker (Chưa triển khai)."""
    screen = QWidget()
    layout = QVBoxLayout(screen)
    layout.setAlignment(Qt.AlignCenter)

    label = QLabel("🎨 Tính năng Filter/Sticker\n(Sẽ được phát triển trong phiên bản sau)")
    label.setAlignment(Qt.AlignCenter)
    label.setStyleSheet("color: #a8dadc; font-size: 24px;")
    layout.addWidget(label)

    return screen
