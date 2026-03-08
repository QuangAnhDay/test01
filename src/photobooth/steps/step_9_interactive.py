import os
import sys

# === PATH FIX: Cho phép chạy trực tiếp bằng `python step_9_interactive.py` ===
_PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
if _PROJECT_ROOT not in sys.path:
    sys.path.insert(0, _PROJECT_ROOT)

import cv2
import numpy as np
from PyQt5.QtWidgets import (QWidget, QLabel, QPushButton, QVBoxLayout,
                             QHBoxLayout, QFrame, QGridLayout, QSizePolicy, QStackedWidget, QApplication)
from PyQt5.QtCore import Qt, QTimer, QSize
from PyQt5.QtGui import QImage, QPixmap, QFont
from src.shared.utils.helpers import convert_cv_qt, overlay_images
from src.modules.image_processing.processor import apply_template_overlay, crop_to_aspect_wh

def create_interactive_capture_screen(app):
    """
    Màn hình chụp tương tác (Step 9) - Bố cục y hệt Step 6 để dễ tinh chỉnh.
    """
    screen = QWidget()
    screen.setObjectName("interactiveScreen")
    screen.setFixedSize(1920, 1080)
    screen.setStyleSheet("background-color: #F2E3E5;") # Nền hồng pastel

    # Sử dụng StackedWidget để chuyển giữa Preview và Full Camera
    app.interactive_stack = QStackedWidget(screen)
    app.interactive_stack.setGeometry(0, 0, 1920, 1080)

    # ---------------------------------------------------------
    # --- PAGE 0: GIAO DIỆN CHÍNH (GIỐNG STEP 6) ---
    # ---------------------------------------------------------
    app.page_main = QWidget()
    


    # --- [4] KHUNG TRÁI LỚN (Chứa Dải ảnh - Tương ứng với List Template của Step 6) ---
    list_container = QFrame(app.page_main)
    list_container.setGeometry(40, 40, 1160, 1000) 
    list_container.setStyleSheet("background-color: #FADBDC; border-radius: 35px; border: 5px solid white;")
    
    list_layout = QVBoxLayout(list_container)
    list_layout.setContentsMargins(30, 30, 30, 30)

    app.interactive_template_label = QLabel()
    app.interactive_template_label.setAlignment(Qt.AlignCenter)
    app.interactive_template_label.setStyleSheet("background: transparent; border: none;")
    list_layout.addWidget(app.interactive_template_label)

    # --- [5] KHUNG PHẢI (Chứa nút bấm & Camera mini - Tương ứng Preview Box của Step 6) ---
    control_container = QFrame(app.page_main)
    control_container.setGeometry(1440, 40, 440, 1000) 
    control_container.setStyleSheet("background-color: #FADBDC; border-radius: 40px; border: 5px solid white;")
    
    control_layout = QVBoxLayout(control_container)
    control_layout.setContentsMargins(40, 60, 40, 60)
    control_layout.setSpacing(30)

    btn_style_white = """
        QPushButton {
            background-color: white; color: #FF7E7E;
            font-family: 'Arial'; font-size: 28px; font-style: italic; font-weight: bold;
            border-radius: 20px; border: none; height: 100px;
        }
        QPushButton:hover { background-color: #FFF0F0; }
        QPushButton:disabled { background-color: #EEE; color: #BBB; }
    """

    app.btn_capture_step = QPushButton("CHỤP ẢNH !")
    app.btn_capture_step.setStyleSheet(btn_style_white)
    app.btn_capture_step.clicked.connect(app.start_interactive_shot)

    app.btn_retake_last = QPushButton("CHỤP LẠI")
    app.btn_retake_last.setStyleSheet(btn_style_white)
    app.btn_retake_last.clicked.connect(app.retake_last_shot)

    # Nút Hoàn thành (Lấy ảnh)
    app.btn_finish_interactive = QPushButton("LẤY ẢNH !")
    app.btn_finish_interactive.setStyleSheet("""
        QPushButton {
            background-color: #FF7E7E; color: white;
            font-family: 'Arial'; font-size: 34px; font-style: italic; font-weight: bold;
            border-radius: 25px; border: 5px solid white; height: 140px;
        }
        QPushButton:hover { background-color: #FF9494; }
    """)
    app.btn_finish_interactive.clicked.connect(app.accept_and_print)

    control_layout.addWidget(app.btn_capture_step)
    control_layout.addWidget(app.btn_retake_last)
    control_layout.addStretch()
    control_layout.addWidget(app.btn_finish_interactive)

    app.interactive_stack.addWidget(app.page_main)

    # ---------------------------------------------------------
    # --- PAGE 1: GIAO DIỆN CHỤP (FULL CAMERA) ---
    # ---------------------------------------------------------
    app.page_capture = QWidget()
    page_cap_layout = QVBoxLayout(app.page_capture)
    page_cap_layout.setContentsMargins(0, 0, 0, 0)

    app.interactive_camera_label = QLabel()
    app.interactive_camera_label.setAlignment(Qt.AlignCenter)
    app.interactive_camera_label.setStyleSheet("background-color: #000;")
    page_cap_layout.addWidget(app.interactive_camera_label)

    app.interactive_countdown_label = QLabel(app.interactive_camera_label)
    app.interactive_countdown_label.setAlignment(Qt.AlignCenter)
    app.interactive_countdown_label.setStyleSheet("""
        font-family: 'Arial'; font-size: 250px; font-weight: bold; 
        color: rgba(255, 255, 255, 120); background-color: rgba(0, 0, 0, 30);
    """)
    app.interactive_countdown_label.hide()

    app.interactive_flash_overlay = QLabel(app.interactive_camera_label)
    app.interactive_flash_overlay.setStyleSheet("background-color: white;")
    app.interactive_flash_overlay.hide()

    app.interactive_stack.addWidget(app.page_capture)

    app.interactive_stack.setCurrentIndex(0)
    return screen

# ==========================================
# KHỐI TEST STANDALONE
# ==========================================
if __name__ == "__main__":
    app_qt = QApplication(sys.argv)
    
    class DummyApp:
        def __init__(self):
            # Tạo stack ảo để chuyển trang
            class MockStack:
                def setCurrentIndex(self, idx):
                    print(f"Interactive Stack chuyển sang Page {idx}")
            self.interactive_stack = MockStack()
            self.selected_frame_count = 4
            self.layout_type = "4x1"
            self.current_slot_index = 0
            self.interactive_photos = []
        def start_interactive_shot(self): print("Bắt đầu chụp!")
        def retake_last_shot(self): print("Chụp lại pô cuối!")
        def accept_and_print(self): print("Xác nhận in ảnh!")

    dummy = DummyApp()
    window = create_interactive_capture_screen(dummy)
    window.showFullScreen()
    sys.exit(app_qt.exec_())
