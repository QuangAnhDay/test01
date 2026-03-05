# ==========================================
# STEP 9 - INTERACTIVE CAPTURE (BỐ CỤC MỚI)
# ==========================================
"""
Giao diện được thiết kế lại theo yêu cầu:
- TRÁI: Camera lớn (Chiếm phần lớn không gian).
- PHẢI: Sidebar (Chụp, Chụp lại, Preview, Lấy ảnh).
- ĐẾM NGƯỢC: Hiển thị ở giữa khung Camera với độ mờ.
"""

from PyQt5.QtWidgets import (QWidget, QLabel, QPushButton, QVBoxLayout,
                             QHBoxLayout, QFrame, QSizePolicy, QGridLayout)
from PyQt5.QtCore import Qt

def create_interactive_capture_screen(app):
    """Tạo màn hình chụp tương tác với camera bên trái và countdown ở giữa."""
    screen = QWidget()
    screen.setObjectName("InteractiveScreen")
    screen.setStyleSheet("QWidget#InteractiveScreen { background-color: #D9D9D9; }")
    
    master_layout = QHBoxLayout(screen)
    master_layout.setContentsMargins(15, 15, 15, 15)
    master_layout.setSpacing(15)

    # ===== CỘT 1: VÙNG CAMERA (BÊN TRÁI) =====
    camera_container = QWidget()
    camera_layout = QGridLayout(camera_container)
    camera_layout.setContentsMargins(0, 0, 0, 0)
    
    # Label hiển thị Camera
    app.interactive_camera_label = QLabel()
    app.interactive_camera_label.setAlignment(Qt.AlignCenter)
    # Tỉ lệ 4:3 cực đại
    app.interactive_camera_label.setFixedSize(1400, 1050) 
    app.interactive_camera_label.setStyleSheet("""
        background-color: black; 
        border-radius: 30px; 
    """)
    camera_layout.addWidget(app.interactive_camera_label, 0, 0)
    
    # Label Đếm ngược (Nằm đè lên giữa Camera)
    app.interactive_countdown_label = QLabel("")
    app.interactive_countdown_label.setAlignment(Qt.AlignCenter)
    # Kích thước khung tròn đếm ngược
    app.interactive_countdown_label.setFixedSize(300, 300)
    app.interactive_countdown_label.setStyleSheet("""
        QLabel {
            font-size: 160px;
            font-weight: bold;
            color: white;
            background-color: rgba(0, 0, 0, 100); /* Độ mờ vừa phải */
            border-radius: 150px;
        }
    """)
    # Thêm vào cùng cell (0,0) để nằm đè lên nhau
    camera_layout.addWidget(app.interactive_countdown_label, 0, 0, Qt.AlignCenter)
    
    master_layout.addWidget(camera_container, stretch=1)

    # ===== CỘT 2: SIDEBAR (BÊN PHẢI) =====
    right_sidebar = QWidget()
    right_sidebar.setFixedWidth(280)
    right_layout = QVBoxLayout(right_sidebar)
    right_layout.setContentsMargins(0, 0, 0, 0)
    right_layout.setSpacing(12)

    # 1. Nút CHỤP
    app.btn_capture_step = QPushButton("CHỤP")
    app.btn_capture_step.setFixedHeight(120)
    app.btn_capture_step.setStyleSheet("""
        QPushButton {
            background-color: #EB5757;
            color: black;
            font-size: 32px;
            font-weight: bold;
            border-radius: 12px;
            border: none;
        }
        QPushButton:hover { background-color: #f27474; }
    """)
    app.btn_capture_step.clicked.connect(app.start_interactive_shot)
    right_layout.addWidget(app.btn_capture_step)

    # 2. Nút CHỤP LẠI
    app.btn_retake_last = QPushButton("CHỤP LẠI")
    app.btn_retake_last.setFixedHeight(90)
    app.btn_retake_last.setStyleSheet("""
        QPushButton {
            background-color: #EB5757;
            color: black;
            font-size: 26px;
            font-weight: bold;
            border-radius: 12px;
            border: none;
        }
    """)
    app.btn_retake_last.clicked.connect(app.retake_last_shot)
    right_layout.addWidget(app.btn_retake_last)

    # 3. Preview ảnh thành phẩm (Label màu trắng bao quanh)
    preview_container = QFrame()
    preview_container.setStyleSheet("background-color: white; border-radius: 10px;")
    preview_layout = QVBoxLayout(preview_container)
    preview_layout.setContentsMargins(10, 10, 10, 10)
    
    app.interactive_template_label = QLabel()
    app.interactive_template_label.setAlignment(Qt.AlignCenter)
    app.interactive_template_label.setStyleSheet("background: transparent;")
    preview_layout.addWidget(app.interactive_template_label)
    
    right_layout.addWidget(preview_container, stretch=1)

    # 4. Nút LẤY ẢNH
    app.btn_finish_interactive = QPushButton("LẤY ẢNH")
    app.btn_finish_interactive.setFixedHeight(140)
    app.btn_finish_interactive.setStyleSheet("""
        QPushButton {
            background-color: #8DED58;
            color: black;
            font-size: 36px;
            font-weight: bold;
            border-radius: 12px;
            border: none;
        }
        QPushButton:hover { background-color: #a6f27e; }
    """)
    app.btn_finish_interactive.clicked.connect(app.accept_and_print)
    right_layout.addWidget(app.btn_finish_interactive)

    master_layout.addWidget(right_sidebar)

    return screen
