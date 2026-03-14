import os
import sys

# === PATH FIX: Cho phép chạy trực tiếp ===
_PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))))
if _PROJECT_ROOT not in sys.path:
    sys.path.insert(0, _PROJECT_ROOT)

# ==========================================
# STEP 1 - PACKAGE (Chọn gói combo/layout)
# ==========================================
"""
Màn hình chọn kiểu lưới ảnh: Dạng Dọc và Dạng Custom.
"""

from PyQt5.QtWidgets import (QWidget, QLabel, QPushButton, QVBoxLayout,
                             QHBoxLayout, QFrame, QSizePolicy)
from PyQt5.QtCore import Qt, QSize
from PyQt5.QtGui import QPixmap, QIcon
from src.shared.types.models import format_price, get_price_by_layout

def create_package_screen(app):
    """Tạo màn hình chọn kiểu lưới ảnh với layout mới: 2 hình ảnh máy ảnh và giá."""
    screen = QWidget()
    
    # Set nền màu giống hình ảnh (nếu cần thiết, hoặc dùng nền trong suốt để ăn theo QMainWindow)
    screen.setStyleSheet("background-color: transparent;")
    
    layout = QVBoxLayout(screen)
    layout.setAlignment(Qt.AlignCenter)
    layout.setSpacing(0)
    layout.setContentsMargins(50, 50, 50, 50)

    # Thân màn hình chứa 2 lựa chọn lớn
    options_layout = QHBoxLayout()
    options_layout.setSpacing(60)
    options_layout.setAlignment(Qt.AlignCenter)

    # Styles
    price_btn_style = """
        QPushButton {
            /* Mau nen nut gia tien (Giong nut START) */
            background-color: #FDCFCF; 
            /* Mau chu nut gia tien */
            color: #D33E42; 
            border: none;
            border-radius: 24px; 
            font-size: 44px; 
            font-weight: bold;
            padding: 10px 40px;
            min-height: 100px;
            min-width: 400px;
            font-family: 'Cooper Black', 'Segoe UI', Arial, sans-serif;
        }
        QPushButton:hover {
            /* Mau nut khi di chuot qua */
            background-color: #F3CFD1;
        }
        QPushButton:pressed {
            /* Mau nut khi nhan xuong */
            background-color: #EAB9BC;
        }
    """
    
    img_btn_style = """
        QPushButton {
            background-color: transparent;
            border: none;
        }
        QPushButton:hover {
            background-color: rgba(255,255,255, 0.2);
            border-radius: 20px;
        }
    """

    # Helper function để tìm file ảnh
    def get_image_path(filename):
        paths = [
            os.path.join(os.path.dirname(__file__), '../../../assets/images', filename),
            os.path.join(os.path.dirname(__file__), '../../../public/type', filename),
            os.path.join(os.path.dirname(__file__), '../../../public', filename),
            f"D:\\photobooth2\\public\\type\\{filename}",
            f"D:\\photobooth2\\public\\{filename}",
            f"D:\\photobooth2\\assets\\images\\{filename}"
        ]
        for p in paths:
            if os.path.exists(p):
                return p
        return None

    # ==========================================
    # LỰA CHỌN 1: DẠNG DỌC (60.000 VND)
    # ==========================================
    frame_1 = QFrame()
    # Mau nen khung bao phay (Trang trong suot)
    frame_1.setStyleSheet("background-color: rgba(255,255,255, 0.4); border-radius: 20px;")
    layout_1 = QVBoxLayout(frame_1)
    layout_1.setContentsMargins(30, 40, 30, 40)
    layout_1.setSpacing(30)
    layout_1.setAlignment(Qt.AlignBottom | Qt.AlignHCenter)

    # Hình ảnh 1 
    btn_img_1 = QPushButton()
    btn_img_1.setStyleSheet(img_btn_style)
    btn_img_1.setCursor(Qt.PointingHandCursor)
    
    img_path_1 = get_image_path("package_1.png") # Đặt tên file ảnh máy ảnh 1 là package_1.png
    if img_path_1:
        pix_1 = QPixmap(img_path_1)
        btn_img_1.setIcon(QIcon(pix_1))
        btn_img_1.setIconSize(QSize(450, 450)) # Chỉnh kích thước hiển thị ảnh
        btn_img_1.setFixedSize(450, 450)
    else:
        # Placeholder nếu chưa có ảnh
        btn_img_1.setText("No image (package_1.png)")
        btn_img_1.setFixedSize(450, 450)
        btn_img_1.setStyleSheet("background-color: #d1d8e0; border-radius: 20px; color: #D33E42; font-size: 20px;")

    # Nút giá 1
    price_val_1 = get_price_by_layout("4x1")
    btn_price_1 = QPushButton(f"{format_price(price_val_1)}")
    btn_price_1.setStyleSheet(price_btn_style)
    btn_price_1.setCursor(Qt.PointingHandCursor)

    layout_1.addWidget(btn_img_1, alignment=Qt.AlignCenter)
    layout_1.addWidget(btn_price_1, alignment=Qt.AlignCenter)

    # Kết nối sự kiện bấm (bấm vào hình hay nút đều được)
    img1_action = lambda: app.go_to_custom_layout_select("vertical")
    btn_img_1.clicked.connect(img1_action)
    btn_price_1.clicked.connect(img1_action)

    options_layout.addWidget(frame_1)

    # ==========================================
    # LỰA CHỌN 2: DẠNG CUSTOM (90.000 VND)
    # ==========================================
    frame_2 = QFrame()
    # Mau nen khung bao phay Custom (Trang trong suot)
    frame_2.setStyleSheet("background-color: rgba(255,255,255, 0.4); border-radius: 20px;")
    layout_2 = QVBoxLayout(frame_2)
    layout_2.setContentsMargins(30, 40, 30, 40)
    layout_2.setSpacing(30)
    layout_2.setAlignment(Qt.AlignBottom | Qt.AlignHCenter)

    # Hình ảnh 2
    btn_img_2 = QPushButton()
    btn_img_2.setStyleSheet(img_btn_style)
    btn_img_2.setCursor(Qt.PointingHandCursor)
    
    img_path_2 = get_image_path("package_2.png") # Đặt tên file ảnh máy ảnh 2 là package_2.png
    if img_path_2:
        pix_2 = QPixmap(img_path_2)
        btn_img_2.setIcon(QIcon(pix_2))
        btn_img_2.setIconSize(QSize(450, 450))
        btn_img_2.setFixedSize(450, 450)
    else:
        btn_img_2.setText("No image (package_2.png)")
        btn_img_2.setFixedSize(450, 450)
        btn_img_2.setStyleSheet("background-color: #d1d8e0; border-radius: 20px; color: #D33E42; font-size: 20px;")

    # Nút giá 2
    price_val_2 = get_price_by_layout("2x2")
    btn_price_2 = QPushButton(f"{format_price(price_val_2)}")
    btn_price_2.setStyleSheet(price_btn_style)
    btn_price_2.setCursor(Qt.PointingHandCursor)

    layout_2.addWidget(btn_img_2, alignment=Qt.AlignCenter)
    layout_2.addWidget(btn_price_2, alignment=Qt.AlignCenter)

    # Kết nối sự kiện bấm
    img2_action = lambda: app.go_to_custom_layout_select("custom")
    btn_img_2.clicked.connect(img2_action)
    btn_price_2.clicked.connect(img2_action)

    options_layout.addWidget(frame_2)

    # Đưa khối options vào màn hình
    layout.addLayout(options_layout)

    # Ghi nhận các nút vào app để quản lý nếu cần
    app.btn_vert_layout = btn_img_1
    app.btn_cust_layout = btn_img_2

    return screen

# ==========================================
# KHỐI TEST STANDALONE
# ==========================================
if __name__ == "__main__":
    from PyQt5.QtWidgets import QApplication

    # Giả lập đối tượng app
    class MockApp:
        def __init__(self):
            self.btn_vert_layout = None
            self.btn_cust_layout = None
            
        def go_to_custom_layout_select(self, group):
            print(f"Chuyển đến chọn layout cho nhóm: {group}")

    app_qt = QApplication(sys.argv)
    
    # Áp dụng STYLE cho app test
    from src.ui.styles import GLOBAL_STYLESHEET
    app_qt.setStyleSheet(GLOBAL_STYLESHEET)

    mock_app = MockApp()
    window = create_package_screen(mock_app)
    window.showFullScreen()
    sys.exit(app_qt.exec_())
