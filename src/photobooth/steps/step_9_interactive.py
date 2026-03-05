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
                             QHBoxLayout, QFrame, QGridLayout, QSizePolicy)
from PyQt5.QtCore import Qt, QTimer, QSize
from PyQt5.QtGui import QImage, QPixmap, QFont
from src.shared.utils.helpers import convert_cv_qt, overlay_images
from src.modules.image_processing.processor import apply_template_overlay, crop_to_aspect_wh

def create_interactive_capture_screen(app):
    """Tạo màn hình chụp tương tác: Trái Camera - Phải Sidebar thiết kế mới (Bo góc & Tối ưu diện tích)."""
    screen = QWidget()
    
    master_layout = QHBoxLayout(screen)
    master_layout.setContentsMargins(10, 10, 10, 10)
    master_layout.setSpacing(10)

    # ===== CỘT TRÁI: CAMERA (BO GÓC) =====
    left_side = QWidget()
    left_layout = QVBoxLayout(left_side)
    left_layout.setContentsMargins(0, 0, 0, 0)
    
    app.interactive_camera_label = QLabel()
    app.interactive_camera_label.setAlignment(Qt.AlignCenter)
    # Quan trọng: Dùng Ignored để tránh vòng lặp tự phình to khi setPixmap liên tục
    app.interactive_camera_label.setSizePolicy(QSizePolicy.Ignored, QSizePolicy.Ignored)
    app.interactive_camera_label.setStyleSheet("""
        background-color: #000; 
        border-radius: 20px; 
        border: 2px solid #E9CBD1;
    """)
    left_layout.addWidget(app.interactive_camera_label)

    # Lớp phủ đếm ngược đè lên camera
    app.interactive_countdown_label = QLabel(app.interactive_camera_label)
    app.interactive_countdown_label.setAlignment(Qt.AlignCenter)
    app.interactive_countdown_label.setStyleSheet("""
        font-size: 200px; font-weight: bold; color: white;
        background-color: rgba(0, 0, 0, 80); 
        border-radius: 20px;
    """)
    app.interactive_countdown_label.hide()

    # Lớp phủ nháy Flash
    app.interactive_flash_overlay = QLabel(app.interactive_camera_label)
    app.interactive_flash_overlay.setStyleSheet("background-color: white; border-radius: 20px;")
    app.interactive_flash_overlay.hide()

    # ===== CỘT PHẢI: SIDEBAR CONTAINER (BỎ VIỀN XANH) =====
    right_sidebar = QFrame()
    right_sidebar.setFixedWidth(280)
    right_sidebar.setStyleSheet("""
        QFrame {
            background-color: #FFDBDB; 
            border-radius: 12px; 
            border: none;
        }
    """)
    right_layout = QVBoxLayout(right_sidebar)
    # Tăng lề ngang lên 15px để thu nhỏ chiều rộng nút bấm, lề dưới 50px để kéo nút lên
    right_layout.setContentsMargins(15, 10, 15, 50) 
    right_layout.setSpacing(8) 

    # Style nút mỏng tuyệt đối
    btn_style_pink = """
        QPushButton {
            background-color: #FF7E7E; color: white; border-radius: 5px;
            font-size: 13px; font-weight: bold; font-style: italic;
            border: none; padding: 0px; margin: 0px;
        }
        QPushButton:hover { background-color: #FF9494; }
        QPushButton:disabled { background-color: #EEE; color: #AAA; }
    """
    
    btn_style_purple = """
        QPushButton {
            background-color: #FFB6FF; color: white; border-radius: 5px;
            font-size: 15px; font-weight: bold; font-style: italic;
            border: none; padding: 0px; margin: 0px;
        }
    """

    app.btn_capture_step = QPushButton("chụp tiếp")
    app.btn_capture_step.setStyleSheet(btn_style_pink)
    app.btn_capture_step.setFixedHeight(22) # Ép chiều cao phần nền mỏng dính
    app.btn_capture_step.setCursor(Qt.PointingHandCursor)
    app.btn_capture_step.clicked.connect(app.start_interactive_shot)
    right_layout.addWidget(app.btn_capture_step)

    app.btn_retake_last = QPushButton("chụp lại")
    app.btn_retake_last.setStyleSheet(btn_style_pink)
    app.btn_retake_last.setFixedHeight(22) # Ép chiều cao phần nền mỏng dính
    app.btn_retake_last.setCursor(Qt.PointingHandCursor)
    app.btn_retake_last.clicked.connect(app.retake_last_shot)
    right_layout.addWidget(app.btn_retake_last)

    # Preview dải ảnh ở giữa (Sẽ chiếm trọn bề ngang sidebar mới)
    app.interactive_template_label = QLabel()
    app.interactive_template_label.setAlignment(Qt.AlignCenter)
    app.interactive_template_label.setSizePolicy(QSizePolicy.Ignored, QSizePolicy.Ignored)
    app.interactive_template_label.setStyleSheet("background-color: transparent; border: none;")
    right_layout.addWidget(app.interactive_template_label, stretch=1)

    # Nút lấy ảnh ở dưới cùng
    app.btn_finish_interactive = QPushButton("lấy ảnh")
    app.btn_finish_interactive.setStyleSheet(btn_style_purple)
    app.btn_finish_interactive.setFixedHeight(28) # Mỏng đúng ý bạn
    app.btn_finish_interactive.setCursor(Qt.PointingHandCursor)
    app.btn_finish_interactive.clicked.connect(app.accept_and_print)
    right_layout.addWidget(app.btn_finish_interactive)

    master_layout.addWidget(left_side, stretch=1)
    master_layout.addWidget(right_sidebar)

    return screen
