# ==========================================
# STEP 6 - TEMPLATE (Chọn khung hình)
# ==========================================
"""
Màn hình chọn khung viền/template cho ảnh.
"""

from PyQt5.QtWidgets import (QWidget, QLabel, QPushButton, QVBoxLayout,
                             QHBoxLayout, QScrollArea, QGridLayout, QGroupBox)
from PyQt5.QtCore import Qt


def create_template_screen(app):
    """Tạo màn hình chọn template/khung viền."""
    screen = QWidget()
    main_layout = QHBoxLayout(screen)
    main_layout.setContentsMargins(20, 20, 20, 20)
    main_layout.setSpacing(20)

    # ===== LEFT COLUMN (2/3) - ẢNH THÀNH QUẢ =====
    left_container = QWidget()
    left_container.setStyleSheet("background-color: #0f0f23; border-radius: 15px;")
    left_layout = QVBoxLayout(left_container)
    left_layout.setContentsMargins(15, 15, 15, 15)
    left_layout.setSpacing(10)

    preview_title = QLabel("📸 ẢNH THÀNH QUẢ")
    preview_title.setAlignment(Qt.AlignCenter)
    preview_title.setStyleSheet("font-size: 24px; font-weight: bold; color: #ffd700;")
    left_layout.addWidget(preview_title)

    app.template_preview_label = QLabel()
    app.template_preview_label.setAlignment(Qt.AlignCenter)
    app.template_preview_label.setStyleSheet("""
        background-color: #000;
        border: 4px solid #4361ee;
        border-radius: 15px;
    """)
    left_layout.addWidget(app.template_preview_label, stretch=1)

    main_layout.addWidget(left_container, stretch=2)

    # ===== RIGHT COLUMN (1/3) - KHUNG + NÚT =====
    right_container = QWidget()
    right_container.setStyleSheet("background-color: #1a1a2e; border-radius: 15px;")
    right_layout = QVBoxLayout(right_container)
    right_layout.setContentsMargins(15, 15, 15, 15)
    right_layout.setSpacing(15)

    title = QLabel("🖼️ CHỌN KHUNG VIỀN")
    title.setObjectName("TitleLabel")
    title.setAlignment(Qt.AlignCenter)
    title.setWordWrap(True)
    right_layout.addWidget(title)

    app.lbl_template_timer = QLabel("Thời gian còn lại: 00:00")
    app.lbl_template_timer.setAlignment(Qt.AlignCenter)
    app.lbl_template_timer.setStyleSheet("font-size: 20px; color: #ffd700; font-weight: bold;")
    right_layout.addWidget(app.lbl_template_timer)

    template_group = QGroupBox("CÁC MẪU KHUNG")
    template_group.setStyleSheet("""
        QGroupBox { 
            color: #a8dadc; font-weight: bold; 
            border: 2px solid #4361ee; border-radius: 10px; 
            margin-top: 15px; padding-top: 10px;
        } 
        QGroupBox::title { 
            subcontrol-origin: margin; 
            left: 10px; padding: 0 10px; 
        }
    """)
    group_layout = QVBoxLayout(template_group)

    template_scroll = QScrollArea()
    template_scroll.setWidgetResizable(True)
    template_scroll.setVerticalScrollBarPolicy(Qt.ScrollBarAsNeeded)
    template_scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
    template_scroll.setStyleSheet("background-color: transparent; border: none;")
    template_scroll.setMinimumHeight(250)

    app.template_btn_widget = QWidget()
    app.template_btn_layout = QGridLayout(app.template_btn_widget)
    app.template_btn_layout.setSpacing(10)
    template_scroll.setWidget(app.template_btn_widget)

    group_layout.addWidget(template_scroll)
    right_layout.addWidget(template_group, stretch=1)

    app.btn_no_template = QPushButton("KHÔNG DÙNG KHUNG")
    app.btn_no_template.setObjectName("OrangeBtn")
    app.btn_no_template.setFixedSize(280, 50)
    app.btn_no_template.clicked.connect(app.use_no_template)
    right_layout.addWidget(app.btn_no_template, alignment=Qt.AlignCenter)

    app.btn_confirm_template = QPushButton("✅ XÁC NHẬN")
    app.btn_confirm_template.setObjectName("GreenBtn")
    app.btn_confirm_template.setFixedSize(280, 80)
    app.btn_confirm_template.setStyleSheet("""
        QPushButton#GreenBtn {
            font-size: 24px; font-weight: bold;
        }
    """)
    app.btn_confirm_template.clicked.connect(app.handle_template_confirmation)
    right_layout.addWidget(app.btn_confirm_template, alignment=Qt.AlignCenter)

    main_layout.addWidget(right_container, stretch=1)

    return screen
