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
                             QHBoxLayout, QFrame, QGridLayout, QSizePolicy, QStackedWidget)
from PyQt5.QtCore import Qt, QTimer, QSize
from PyQt5.QtGui import QImage, QPixmap, QFont
from src.shared.utils.helpers import convert_cv_qt, overlay_images
from src.modules.image_processing.processor import apply_template_overlay, crop_to_aspect_wh

def create_interactive_capture_screen(app):
    """
    Tạo màn hình chụp tương tác mới với Workflow 2 bước:
    - Page 0: Màn hình chính (Sidebar + Preview dải ảnh lớn ở giữa).
    - Page 1: Màn hình chụp (Camera toàn màn hình).
    """
    screen = QWidget()
    main_layout = QVBoxLayout(screen)
    main_layout.setContentsMargins(0, 0, 0, 0)

    app.interactive_stack = QStackedWidget()
    main_layout.addWidget(app.interactive_stack)

    # --- PAGE 0: GIAO DIỆN CHÍNH (PREVIEW & CONTROL) ---
    app.page_main = QWidget()
    page_main_layout = QHBoxLayout(app.page_main)
    page_main_layout.setContentsMargins(30, 30, 30, 30)
    page_main_layout.setSpacing(30)

    # Bên trái: Chứa Preview dải ảnh (Căn giữa)
    preview_container = QWidget()
    preview_layout = QVBoxLayout(preview_container)
    preview_layout.setContentsMargins(0, 0, 0, 0)
    
    msg_label = QLabel("✨ DẢI ẢNH CỦA BẠN ✨")
    msg_label.setStyleSheet("font-size: 24px; font-weight: bold; color: #FF7E7E; font-style: italic;")
    msg_label.setAlignment(Qt.AlignCenter)
    preview_layout.addWidget(msg_label)

    app.interactive_template_label = QLabel()
    app.interactive_template_label.setAlignment(Qt.AlignCenter)
    # Ignored giúp label co giãn linh hoạt theo ảnh
    app.interactive_template_label.setSizePolicy(QSizePolicy.Ignored, QSizePolicy.Ignored)
    app.interactive_template_label.setStyleSheet("background-color: transparent; border: 2px dashed #FFB6FF; border-radius: 15px;")
    preview_layout.addWidget(app.interactive_template_label, stretch=1)

    page_main_layout.addWidget(preview_container, stretch=1)

    # Bên phải: Sidebar chứa nút bấm
    right_sidebar = QFrame()
    right_sidebar.setFixedWidth(280)
    right_sidebar.setStyleSheet("background-color: #FFDBDB; border-radius: 20px; border: 3px solid #FFB6FF;")
    right_layout = QVBoxLayout(right_sidebar)
    right_layout.setContentsMargins(20, 40, 20, 40)
    right_layout.setSpacing(20)

    btn_style_pink = """
        QPushButton {
            background-color: #FF7E7E; color: white; border-radius: 10px;
            font-size: 22px; font-weight: bold; font-style: italic;
            height: 60px; border: none;
        }
        QPushButton:hover { background-color: #FF9494; }
        QPushButton:disabled { background-color: #DDD; color: #AAA; }
    """
    
    btn_style_purple = """
        QPushButton {
            background-color: #FFB6FF; color: white; border-radius: 10px;
            font-size: 28px; font-weight: bold; font-style: italic;
            height: 80px; border: none;
        }
        QPushButton:hover { background-color: #FFCEFF; }
    """

    app.btn_capture_step = QPushButton("chụp tiếp")
    app.btn_capture_step.setStyleSheet(btn_style_pink)
    app.btn_capture_step.setCursor(Qt.PointingHandCursor)
    app.btn_capture_step.clicked.connect(app.start_interactive_shot)
    right_layout.addWidget(app.btn_capture_step)

    app.btn_retake_last = QPushButton("chụp lại")
    app.btn_retake_last.setStyleSheet(btn_style_pink)
    app.btn_retake_last.setCursor(Qt.PointingHandCursor)
    app.btn_retake_last.clicked.connect(app.retake_last_shot)
    right_layout.addWidget(app.btn_retake_last)
    
    right_layout.addStretch(1)

    app.btn_finish_interactive = QPushButton("lấy ảnh")
    app.btn_finish_interactive.setStyleSheet(btn_style_purple)
    app.btn_finish_interactive.setCursor(Qt.PointingHandCursor)
    app.btn_finish_interactive.clicked.connect(app.accept_and_print)
    right_layout.addWidget(app.btn_finish_interactive)

    page_main_layout.addWidget(right_sidebar)
    app.interactive_stack.addWidget(app.page_main)

    # --- PAGE 1: GIAO DIỆN CHỤP (FULL CAMERA) ---
    app.page_capture = QWidget()
    page_cap_layout = QVBoxLayout(app.page_capture)
    page_cap_layout.setContentsMargins(0, 0, 0, 0)

    app.interactive_camera_label = QLabel()
    app.interactive_camera_label.setAlignment(Qt.AlignCenter)
    app.interactive_camera_label.setSizePolicy(QSizePolicy.Ignored, QSizePolicy.Ignored)
    app.interactive_camera_label.setStyleSheet("background-color: #000;")
    page_cap_layout.addWidget(app.interactive_camera_label)

    # Lớp phủ đếm ngược đè lên camera
    app.interactive_countdown_label = QLabel(app.interactive_camera_label)
    app.interactive_countdown_label.setAlignment(Qt.AlignCenter)
    app.interactive_countdown_label.setStyleSheet("font-size: 300px; font-weight: bold; color: white; background-color: rgba(0, 0, 0, 100);")
    app.interactive_countdown_label.hide()

    # Lớp phủ nháy Flash
    app.interactive_flash_overlay = QLabel(app.interactive_camera_label)
    app.interactive_flash_overlay.setStyleSheet("background-color: white;")
    app.interactive_flash_overlay.hide()

    app.interactive_stack.addWidget(app.page_capture)

    # Khởi đầu ở Page 0
    app.interactive_stack.setCurrentIndex(0)

    return screen
