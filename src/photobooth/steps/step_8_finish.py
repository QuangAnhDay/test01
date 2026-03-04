# ==========================================
# STEP 8 - FINISH (Xác nhận & In ảnh)
# ==========================================
"""
Màn hình xác nhận cuối cùng trước khi in và hiển thị QR tải file.
"""

from PyQt5.QtWidgets import QWidget, QLabel, QPushButton, QVBoxLayout, QHBoxLayout
from PyQt5.QtCore import Qt


def create_finish_screen(app):
    """Tạo màn hình xác nhận cuối cùng."""
    screen = QWidget()
    layout = QVBoxLayout(screen)
    layout.setAlignment(Qt.AlignCenter)
    layout.setSpacing(20)
    layout.setContentsMargins(20, 20, 20, 20)

    title = QLabel("BẠN CÓ ĐỒNG Ý VỚI MẪU NÀY KHÔNG?")
    title.setObjectName("TitleLabel")
    title.setAlignment(Qt.AlignCenter)
    layout.addWidget(title)

    app.final_preview_label = QLabel()
    app.final_preview_label.setAlignment(Qt.AlignCenter)
    app.final_preview_label.setStyleSheet("""
        background-color: #000;
        border: 4px solid #06d6a0;
        border-radius: 15px;
    """)
    app.final_preview_label.setMinimumSize(800, 450)
    layout.addWidget(app.final_preview_label)

    btn_layout = QHBoxLayout()
    btn_layout.setSpacing(30)

    app.btn_accept = QPushButton("ĐỒNG Ý - IN ẢNH")
    app.btn_accept.setObjectName("GreenBtn")
    app.btn_accept.setFixedSize(300, 80)
    app.btn_accept.clicked.connect(app.accept_and_print)
    btn_layout.addWidget(app.btn_accept)

    layout.addLayout(btn_layout)

    return screen
