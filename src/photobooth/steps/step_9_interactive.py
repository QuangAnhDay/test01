# ==========================================
# STEP 9 - INTERACTIVE CAPTURE (BỐ CỤC ĐỒNG BỘ STEP 6)
# ==========================================
"""
Màn hình chụp tương tác (Step 9) - Đã đồng bộ cấu trúc y hệt Step 6:
- Khung trái (Collage Preview): (40, 40, 1160, 1000)
- Khung phải (Dashboard Box): (1240, 40, 640, 840)
- Nút "LẤY ẢNH !" (Nằm ngoài khung): (1335, 920, 450, 110)
"""

import os
import sys

# === PATH FIX ===
_PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
if _PROJECT_ROOT not in sys.path:
    sys.path.insert(0, _PROJECT_ROOT)

from PyQt5.QtWidgets import (QWidget, QLabel, QPushButton, QVBoxLayout,
                             QHBoxLayout, QFrame, QGridLayout, QSizePolicy, QStackedWidget, QApplication)
from PyQt5.QtCore import Qt, QTimer, QSize
from PyQt5.QtGui import QImage, QPixmap, QFont
from src.shared.utils.helpers import convert_cv_qt, overlay_images, get_rounded_pixmap
from src.modules.image_processing.processor import apply_template_overlay, crop_to_aspect_wh

def create_interactive_capture_screen(app):
    """
    Tạo giao diện Step 9 với bố cục đồng bộ tuyệt đối với Step 6.
    """
    screen = QWidget()
    screen.setObjectName("interactiveScreen")
    screen.setFixedSize(1920, 1080)
    screen.setStyleSheet("background-color: #F2E3E5;") # Nền hồng pastel chuẩn

    # Sử dụng StackedWidget để chuyển giữa Preview và Full Camera
    app.interactive_stack = QStackedWidget(screen)
    app.interactive_stack.setGeometry(0, 0, 1920, 1080)

    # ---------------------------------------------------------
    # --- PAGE 0: DASHBOARD (GIỐNG STEP 6) ---
    # ---------------------------------------------------------
    app.page_main = QWidget()
    
    # --- [1] KHUNG TRÁI (Hiển thị Tiến trình ảnh ghép) ---
    list_container = QFrame(app.page_main)
    list_container.setGeometry(40, 40, 1160, 1000) 
    list_container.setStyleSheet("background-color: #FADBDC; border-radius: 35px; border: 5px solid white;")
    
    list_layout = QVBoxLayout(list_container)
    list_layout.setContentsMargins(30, 30, 30, 30)

    app.interactive_template_label = QLabel()
    app.interactive_template_label.setAlignment(Qt.AlignCenter)
    app.interactive_template_label.setStyleSheet("background: transparent; border: none;")
    list_layout.addWidget(app.interactive_template_label)

    # --- [2] KHUNG PHẢI (Camera Mini & Các nút điều khiển phụ) ---
    # Tọa độ và kích thước khớp 100% với Preview Box của Step 6
    control_container = QFrame(app.page_main)
    control_container.setGeometry(1240, 40, 640, 840) 
    control_container.setStyleSheet("background-color: #FADBDC; border-radius: 40px; border: 5px solid white;")
    
    control_layout = QVBoxLayout(control_container)
    control_layout.setContentsMargins(40, 40, 40, 40)
    control_layout.setSpacing(35)

    # Label Camera Mini (Tỷ lệ 4:3, bo góc)
    app.interactive_camera_mini = QLabel()
    app.interactive_camera_mini.setFixedSize(560, 420) 
    app.interactive_camera_mini.setAlignment(Qt.AlignCenter)
    app.interactive_camera_mini.setStyleSheet("""
        background-color: white; 
        border-radius: 35px; 
        border: 5px solid white; 
        padding: 0px;
    """)
    control_layout.addWidget(app.interactive_camera_mini)

    btn_style_white = """
        QPushButton {
            background-color: white; color: #FF7E7E;
            font-family: 'Arial'; font-size: 28px; font-style: italic; font-weight: bold;
            border-radius: 20px; border: none; min-height: 90px;
        }
        QPushButton:hover { background-color: #FFF0F0; }
        QPushButton:disabled { background-color: #EEE; color: #BBB; }
    """

    app.btn_capture_step = QPushButton("CHỤP ẢNH !")
    app.btn_capture_step.setStyleSheet(btn_style_white)
    app.btn_capture_step.clicked.connect(app.start_interactive_shot)
    control_layout.addWidget(app.btn_capture_step)

    app.btn_retake_last = QPushButton("CHỤP LẠI")
    app.btn_retake_last.setStyleSheet(btn_style_white)
    app.btn_retake_last.clicked.connect(app.retake_last_shot)
    control_layout.addWidget(app.btn_retake_last)

    control_layout.addStretch()

    # --- [3] NÚT "LẤY ẢNH !" (Nằm ngoài khung, đồng bộ với nút Confirm của Step 6) ---
    app.btn_finish_interactive = QPushButton("LẤY ẢNH !", app.page_main)
    app.btn_finish_interactive.setGeometry(1335, 920, 450, 110)
    app.btn_finish_interactive.setStyleSheet("""
        QPushButton {
            background-color: #FF7E7E; color: white;
            font-family: 'Arial'; font-size: 38px; font-style: italic; font-weight: bold;
            border-radius: 25px; border: 5px solid white;
        }
        QPushButton:hover { background-color: #FF9494; }
        QPushButton:disabled { background-color: #EEE; color: #BBB; }
    """)
    app.btn_finish_interactive.clicked.connect(app.accept_and_print)

    app.interactive_stack.addWidget(app.page_main)

    # ---------------------------------------------------------
    # --- PAGE 1: FULL CAMERA CAPTURE ---
    # ---------------------------------------------------------
    app.page_capture = QWidget()
    page_cap_layout = QVBoxLayout(app.page_capture)
    page_cap_layout.setContentsMargins(0, 0, 0, 0)

    app.interactive_camera_label = QLabel()
    app.interactive_camera_label.setAlignment(Qt.AlignCenter)
    app.interactive_camera_label.setStyleSheet("background-color: #000;")
    page_cap_layout.addWidget(app.interactive_camera_label)

    # Countdown Overlay
    app.interactive_countdown_label = QLabel(app.interactive_camera_label)
    app.interactive_countdown_label.setAlignment(Qt.AlignCenter)
    app.interactive_countdown_label.setStyleSheet("""
        font-family: 'Arial'; font-size: 250px; font-weight: bold; 
        color: rgba(255, 255, 255, 120); background-color: rgba(0, 0, 0, 30);
    """)
    app.interactive_countdown_label.hide()

    # Flash Overlay
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
