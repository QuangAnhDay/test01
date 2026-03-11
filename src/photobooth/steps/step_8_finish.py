import os
import sys

# === PATH FIX: Cho phép chạy trực tiếp bằng `python step_8_finish.py` ===
_PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
if _PROJECT_ROOT not in sys.path:
    sys.path.insert(0, _PROJECT_ROOT)

from PyQt5.QtWidgets import QWidget, QLabel, QPushButton, QVBoxLayout, QHBoxLayout, QFrame, QApplication
from PyQt5.QtCore import Qt


def create_finish_screen(app):
    """
    Màn hình xác nhận cuối cùng (Step 8) - Phong cách Pink Pastel.
    """
    screen = QWidget()
    screen.setObjectName("finishScreen")
    screen.setFixedSize(1920, 1080)
    screen.setStyleSheet("background-color: #F2E3E5;") # Nền hồng đặc trưng

    # --- [1] TIÊU ĐỀ ("XONG RỒI !") ---
    title_box = QLabel("xong rồi !", screen)
    title_box.setAlignment(Qt.AlignCenter)
    title_box.setGeometry(685, 40, 550, 85) 
    title_box.setStyleSheet("""
        background-color: #FADBDC; color: white;
        font-family: 'Cooper Black', 'Arial'; font-size: 36px; font-style: italic; font-weight: bold;
        border-radius: 25px; border: 5px solid white;
    """)

    # --- [2] KHUNG PREVIEW ẢNH ---
    preview_container = QFrame(screen)
    preview_container.setGeometry(460, 160, 1000, 700)
    preview_container.setStyleSheet("""
        background-color: #FADBDC; border-radius: 40px; border: 8px solid white;
    """)
    
    preview_layout = QVBoxLayout(preview_container)
    preview_layout.setContentsMargins(25, 25, 25, 25)

    app.final_preview_label = QLabel()
    app.final_preview_label.setAlignment(Qt.AlignCenter)
    app.final_preview_label.setStyleSheet("background: transparent; border: none;")
    preview_layout.addWidget(app.final_preview_label)

    # --- [3] NÚT XÁC NHẬN / IN ---
    app.btn_accept = QPushButton("IN ẢNH !", screen)
    app.btn_accept.setGeometry(685, 900, 550, 120)
    app.btn_accept.setStyleSheet("""
        QPushButton {
            background-color: #FF7E7E; color: white;
            font-family: 'Cooper Black', 'Arial'; font-size: 38px; font-style: italic; font-weight: bold;
            border-radius: 25px; border: 5px solid white;
        }
        QPushButton:hover { background-color: #FF9494; }
        QPushButton:pressed { background-color: #F8B9BC; }
    """)
    app.btn_accept.clicked.connect(app.accept_and_print)

    return screen

# ==========================================
# KHỐI TEST STANDALONE
# ==========================================
if __name__ == "__main__":
    app_qt = QApplication(sys.argv)
    
    class DummyApp:
        def accept_and_print(self):
            print("Xác nhận in ảnh!")

    dummy = DummyApp()
    window = create_finish_screen(dummy)
    window.showFullScreen()
    sys.exit(app_qt.exec_())
