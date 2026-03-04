# ==========================================
# STEP 2 - PAYMENT (QR Thanh toán)
# ==========================================
"""
Màn hình hiển thị mã QR thanh toán VietQR + kiểm tra Casso.
"""

from PyQt5.QtWidgets import QWidget, QLabel, QPushButton, QVBoxLayout, QHBoxLayout
from PyQt5.QtCore import Qt


def create_payment_screen(app):
    """Tạo màn hình QR thanh toán."""
    screen = QWidget()
    layout = QVBoxLayout(screen)
    layout.setAlignment(Qt.AlignCenter)
    layout.setSpacing(20)
    layout.setContentsMargins(50, 30, 50, 30)

    title = QLabel("📱 QUÉT MÃ ĐỂ THANH TOÁN")
    title.setObjectName("TitleLabel")
    title.setAlignment(Qt.AlignCenter)
    layout.addWidget(title)

    app.selected_package_label = QLabel()
    app.selected_package_label.setObjectName("SubTitleLabel")
    app.selected_package_label.setAlignment(Qt.AlignCenter)
    layout.addWidget(app.selected_package_label)

    app.transaction_code_label = QLabel()
    app.transaction_code_label.setAlignment(Qt.AlignCenter)
    app.transaction_code_label.setStyleSheet("font-size: 20px; color: #ffd700; font-weight: bold;")
    layout.addWidget(app.transaction_code_label)

    # QR container
    qr_container = QWidget()
    qr_container.setStyleSheet("background-color: white; border-radius: 25px;")
    qr_container.setFixedSize(380, 380)
    qr_layout = QVBoxLayout(qr_container)
    qr_layout.setAlignment(Qt.AlignCenter)

    app.qr_label = QLabel("⏳ Đang tải...")
    app.qr_label.setAlignment(Qt.AlignCenter)
    app.qr_label.setFixedSize(350, 350)
    app.qr_label.setStyleSheet("font-size: 24px; color: #333; background-color: white;")
    qr_layout.addWidget(app.qr_label)
    layout.addWidget(qr_container, alignment=Qt.AlignCenter)

    app.bank_info_label = QLabel()
    app.bank_info_label.setAlignment(Qt.AlignCenter)
    app.bank_info_label.setStyleSheet("font-size: 16px; color: #a8dadc;")
    layout.addWidget(app.bank_info_label)

    app.payment_status_label = QLabel("🔄 Đang chờ thanh toán...")
    app.payment_status_label.setAlignment(Qt.AlignCenter)
    app.payment_status_label.setStyleSheet("font-size: 18px; color: #ffd700;")
    layout.addWidget(app.payment_status_label)

    btn_layout = QHBoxLayout()
    btn_layout.setSpacing(30)

    app.btn_back_qr = QPushButton("⬅️ HỦY VÀ QUAY LẠI")
    app.btn_back_qr.setObjectName("OrangeBtn")
    app.btn_back_qr.setFixedSize(250, 60)
    app.btn_back_qr.clicked.connect(app.cancel_payment_and_go_back)
    btn_layout.addWidget(app.btn_back_qr)

    layout.addLayout(btn_layout)

    return screen
