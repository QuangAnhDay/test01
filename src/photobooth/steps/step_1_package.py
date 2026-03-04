# ==========================================
# STEP 1 - PACKAGE (Chọn gói combo/layout)
# ==========================================
"""
Màn hình chọn kiểu lưới ảnh: Dạng Dọc và Dạng Custom.
"""

from PyQt5.QtWidgets import (QWidget, QLabel, QPushButton, QVBoxLayout,
                             QHBoxLayout, QFrame)
from PyQt5.QtCore import Qt
from src.shared.types.models import format_price, get_price_by_layout


def create_package_screen(app):
    """Tạo màn hình chọn kiểu lưới ảnh với 2 lựa chọn chính."""
    screen = QWidget()
    layout = QVBoxLayout(screen)
    layout.setAlignment(Qt.AlignCenter)
    layout.setSpacing(40)
    layout.setContentsMargins(50, 50, 50, 50)

    title = QLabel("🖼️ CHỌN KIỂU KHUNG ẢNH")
    title.setObjectName("TitleLabel")
    title.setAlignment(Qt.AlignCenter)
    layout.addWidget(title)

    subtitle = QLabel("Hãy chọn định dạng ảnh bạn muốn chụp")
    subtitle.setObjectName("InfoLabel")
    subtitle.setAlignment(Qt.AlignCenter)
    layout.addWidget(subtitle)

    # Thân màn hình chứa 2 nút lớn
    options_layout = QHBoxLayout()
    options_layout.setSpacing(50)
    options_layout.setAlignment(Qt.AlignCenter)

    btn_style = """
        QPushButton {
            background: qlineargradient(x1:0, y1:0, x2:1, y2:1,
                stop:0 #1a1a2e, stop:1 #16213e);
            border: 5px solid #4361ee; border-radius: 30px;
            color: white; padding: 40px; min-width: 400px; min-height: 500px;
        }
        QPushButton:hover {
            border-color: #06d6a0;
            background: qlineargradient(x1:0, y1:0, x2:1, y2:1,
                stop:0 #16213e, stop:1 #1a1a2e);
        }
        QLabel { background: transparent; }
    """

    # --- NÚT DẠNG DỌC (STRIP) ---
    btn_vertical = QPushButton()
    btn_vertical.setStyleSheet(btn_style)
    v_vbox = QVBoxLayout(btn_vertical)
    
    icon_vert = QLabel("🎞️")
    icon_vert.setAlignment(Qt.AlignCenter)
    icon_vert.setStyleSheet("font-size: 80px;")
    
    name_vert = QLabel("DẠNG DỌC")
    name_vert.setAlignment(Qt.AlignCenter)
    name_vert.setStyleSheet("font-size: 32px; font-weight: bold; color: #4361ee;")
    
    desc_vert = QLabel("4 Ảnh (1 dải dọc)\nPhổ biến nhất")
    desc_vert.setAlignment(Qt.AlignCenter)
    desc_vert.setStyleSheet("font-size: 18px; color: #a8dadc;")

    price_val = get_price_by_layout("4x1")
    price_vert = QLabel(format_price(price_val))
    price_vert.setAlignment(Qt.AlignCenter)
    price_vert.setStyleSheet("font-size: 24px; font-weight: bold; color: #06d6a0;")

    v_vbox.addWidget(icon_vert)
    v_vbox.addWidget(name_vert)
    v_vbox.addWidget(desc_vert)
    v_vbox.addWidget(price_vert)
    
    # Khi bấm vào DẠNG DỌC -> Hiển thị danh sách Layout (4x1, Custom_3, ...)
    btn_vertical.clicked.connect(lambda: app.go_to_custom_layout_select("vertical"))
    options_layout.addWidget(btn_vertical)

    # --- NÚT DẠNG CUSTOM ---
    btn_custom = QPushButton()
    btn_custom.setStyleSheet(btn_style.replace("#4361ee", "#e94560")) # Màu đỏ
    c_vbox = QVBoxLayout(btn_custom)
    
    icon_cust = QLabel("🎨")
    icon_cust.setAlignment(Qt.AlignCenter)
    icon_cust.setStyleSheet("font-size: 80px;")
    
    name_cust = QLabel("KHUNG TÙY BIẾN")
    name_cust.setAlignment(Qt.AlignCenter)
    name_cust.setStyleSheet("font-size: 32px; font-weight: bold; color: #e94560;")
    
    desc_cust = QLabel("Chọn từ bộ sưu tập\nLayout đặc biệt")
    desc_cust.setAlignment(Qt.AlignCenter)
    desc_cust.setStyleSheet("font-size: 18px; color: #a8dadc;")

    price_cust_val = get_price_by_layout("2x2") # Lấy giá mặc định
    price_cust = QLabel(format_price(price_cust_val))
    price_cust.setAlignment(Qt.AlignCenter)
    price_cust.setStyleSheet("font-size: 24px; font-weight: bold; color: #06d6a0;")

    c_vbox.addWidget(icon_cust)
    c_vbox.addWidget(name_cust)
    c_vbox.addWidget(desc_cust)
    c_vbox.addWidget(price_cust)
    
    # Khi bấm vào KHUNG TÙY BIẾN -> Hiển thị danh sách Layout để chọn
    btn_custom.clicked.connect(lambda: app.go_to_custom_layout_select("custom"))
    options_layout.addWidget(btn_custom)


    layout.addLayout(options_layout)

    # Ghi nhận các nút vào app để quản lý nếu cần
    app.btn_vert_layout = btn_vertical
    app.btn_cust_layout = btn_custom

    # Nút quay lại
    btn_back = QPushButton("⬅️ QUAY LẠI")
    btn_back.setObjectName("OrangeBtn")
    btn_back.setFixedSize(250, 70)
    btn_back.clicked.connect(app.reset_all)
    layout.addWidget(btn_back, alignment=Qt.AlignCenter)

    return screen
