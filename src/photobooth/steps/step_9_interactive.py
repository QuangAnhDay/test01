# ==========================================
# STEP 9 - INTERACTIVE CAPTURE (Chụp & Ghép)
# ==========================================
"""
Giao diện đặc biệt: 
- TRÁI: Camera LiveView
- PHẢI: Template Preview (Lấp đầy ảnh lúc chụp)
"""

import cv2
import numpy as np
from PyQt5.QtWidgets import (QWidget, QLabel, QPushButton, QVBoxLayout,
                             QHBoxLayout, QFrame, QGridLayout)
from PyQt5.QtCore import Qt, QTimer, QSize
from PyQt5.QtGui import QImage, QPixmap, QFont
from src.shared.utils.helpers import convert_cv_qt, overlay_images
from src.modules.image_processing.processor import apply_template_overlay, crop_to_aspect_wh

def create_interactive_capture_screen(app):
    """Tạo màn hình chụp tương tác: Trái Camera - Phải Template."""
    screen = QWidget()
    master_layout = QHBoxLayout(screen)
    master_layout.setContentsMargins(10, 10, 10, 10)
    master_layout.setSpacing(20)

    # ===== CỘT TRÁI: CAMERA & CONTROLS =====
    left_panel = QFrame()
    left_panel.setStyleSheet("background-color: #1a1a2e; border-radius: 20px;")
    left_layout = QVBoxLayout(left_panel)
    left_layout.setSpacing(15)

    app.interactive_camera_label = QLabel("CAMERA")
    app.interactive_camera_label.setAlignment(Qt.AlignCenter)
    app.interactive_camera_label.setFixedSize(640, 480)
    app.interactive_camera_label.setStyleSheet("background-color: black; border-radius: 15px; border: 3px solid #e94560;")
    left_layout.addWidget(app.interactive_camera_label, alignment=Qt.AlignCenter)

    app.interactive_countdown_label = QLabel("")
    app.interactive_countdown_label.setAlignment(Qt.AlignCenter)
    app.interactive_countdown_label.setStyleSheet("font-size: 100px; font-weight: bold; color: #ffd700;")
    left_layout.addWidget(app.interactive_countdown_label)

    # Nút bấm tích hợp
    btns_layout = QHBoxLayout()
    app.btn_capture_step = QPushButton("📸 CHỤP ẢNH")
    app.btn_capture_step.setObjectName("GreenBtn")
    app.btn_capture_step.setFixedSize(300, 80)
    app.btn_capture_step.clicked.connect(app.start_interactive_shot)
    btns_layout.addWidget(app.btn_capture_step)

    # Nút chụp lại ảnh cuối
    app.btn_retake_last = QPushButton("⏮️ CHỤP LẠI (XÓA CHỖ NÀY)")
    app.btn_retake_last.setObjectName("OrangeBtn")
    app.btn_retake_last.setFixedSize(250, 60)
    app.btn_retake_last.clicked.connect(app.retake_last_shot)
    app.btn_retake_last.setEnabled(False)
    btns_layout.addWidget(app.btn_retake_last)
    
    left_layout.addLayout(btns_layout)
    left_layout.addStretch()

    # ===== CỘT PHẢI: TEMPLATE PREVIEW =====
    right_panel = QFrame()
    right_panel.setStyleSheet("background-color: #0f172a; border-radius: 20px; padding: 10px;")
    right_layout = QVBoxLayout(right_panel)
    
    lbl_preview = QLabel("🖼️ KẾT QUẢ ĐANG TẠO")
    lbl_preview.setAlignment(Qt.AlignCenter)
    lbl_preview.setStyleSheet("font-size: 20px; font-weight: bold; color: #a8dadc;")
    right_layout.addWidget(lbl_preview)

    app.interactive_template_label = QLabel()
    app.interactive_template_label.setAlignment(Qt.AlignCenter)
    # Tỉ lệ khung hình (ví dụ Strip 4x1 đứng)
    app.interactive_template_label.setMinimumSize(400, 700)
    right_layout.addWidget(app.interactive_template_label, stretch=1)

    # Nút hoàn thành (chỉ bật khi xong hết các slot)
    app.btn_finish_interactive = QPushButton("✅ HOÀN THÀNH & IN")
    app.btn_finish_interactive.setObjectName("BlueBtn")
    app.btn_finish_interactive.setFixedSize(350, 70)
    app.btn_finish_interactive.setEnabled(False)
    app.btn_finish_interactive.clicked.connect(app.accept_and_print)
    right_layout.addWidget(app.btn_finish_interactive, alignment=Qt.AlignCenter)

    master_layout.addWidget(left_panel, stretch=2)
    master_layout.addWidget(right_panel, stretch=1)

    return screen
