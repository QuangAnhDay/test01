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

    app.photo_select_title = QLabel("CHỌN ẢNH")
    app.photo_select_title.setObjectName("TitleLabel")
    app.photo_select_title.setAlignment(Qt.AlignCenter)
    layout.addWidget(app.photo_select_title)

    # Timer Label
    app.lbl_selection_timer = QLabel("Thời gian còn lại: 00:00")
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

    app.btn_confirm_photos = QPushButton("XÁC NHẬN CHỌN ẢNH")
    app.btn_confirm_photos.setObjectName("GreenBtn")
    app.btn_confirm_photos.setEnabled(False)
    app.btn_confirm_photos.clicked.connect(app.confirm_photo_selection)
    layout.addWidget(app.btn_confirm_photos, alignment=Qt.AlignCenter)

    return screen
