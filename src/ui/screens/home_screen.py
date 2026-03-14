import os
import sys

# === PATH FIX: Cho phép chạy trực tiếp ===
_PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))) or '.')
if _PROJECT_ROOT not in sys.path:
    sys.path.insert(0, _PROJECT_ROOT)

from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout,
    QPushButton, QLabel, QFrame
)
from PyQt5.QtCore import Qt, QSize, pyqtSignal
from PyQt5.QtGui import QPixmap, QFont

from src.ui.widgets.infinite_image_column import InfiniteImageColumnWidget
from src.ui.widgets.camera_view import CameraView


class HomeScreen(QWidget):
    """Màn hình chính của ứng dụng PhotoBooth"""

    start_clicked = pyqtSignal()
    open_admin = pyqtSignal()  # Tín hiệu mở giao diện admin (F2)

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("PhotoBooth - Home")
        self.camera_view = None
        self.setup_ui()
        self.apply_styles()

    def setup_ui(self):
        """Thiết lập bố cục giao diện chính"""
        root_layout = QVBoxLayout(self)
        root_layout.setContentsMargins(0, 0, 0, 0)
        root_layout.setSpacing(0)

        content_frame = QFrame()
        content_frame.setObjectName("contentFrame")
        root_layout.addWidget(content_frame)

        # Khung chính
        main_layout = QHBoxLayout(content_frame)
        main_layout.setContentsMargins(22, 18, 22, 18)
        main_layout.setSpacing(26)

        # Panel trái - Lưới ảnh mẫu masonry
        left_panel = self.create_left_panel()
        main_layout.addWidget(left_panel, 11)

        # Panel phải - Logo, khung xem trước camera, nút Start
        right_panel = self.create_right_panel()
        main_layout.addWidget(right_panel, 8)

    def create_left_panel(self):
        """Tạo panel trái chứa lưới ảnh mẫu masonry"""
        left_widget = QFrame()
        left_widget.setMinimumWidth(820)
        left_widget.setStyleSheet("""
            QFrame {
                /* Mau nen cua khung Masonry ben trai (Mau trang) */
                background-color: #FFFFFF;
                border-radius: 24px;
            }
        """)

        left_layout = QVBoxLayout(left_widget)
        left_layout.setContentsMargins(0, 0, 0, 0)
        left_layout.setSpacing(0)
        left_layout.addWidget(InfiniteImageColumnWidget(left_widget))

        return left_widget

    def create_right_panel(self):
        """Tạo panel bên phải chứa logo, khung camera và nút bắt đầu"""
        right_widget = QWidget()
        right_layout = QVBoxLayout(right_widget)
        right_layout.setContentsMargins(0, 10, 0, 26)
        right_layout.setSpacing(0)

        right_content = QWidget()
        right_content.setFixedWidth(760)
        content_layout = QVBoxLayout(right_content)
        content_layout.setContentsMargins(0, 0, 0, 0)
        content_layout.setSpacing(0)

        logo_layout = self.create_logo_section()
        content_layout.addLayout(logo_layout)
        content_layout.addSpacing(26)

        # Khung xem trước camera
        self.camera_view = CameraView(initial_camera_index=0)
        content_layout.addWidget(self.camera_view)
        content_layout.addSpacing(76)

        # Nút bắt đầu
        start_button = QPushButton("START")
        start_button.setFixedSize(730, 130)
        start_button.setFont(self.get_button_font())
        start_button.setCursor(Qt.PointingHandCursor)
        start_button.clicked.connect(self.on_start_clicked)
        start_button.setStyleSheet("""
            QPushButton {
                /* Mau nen nut START (Hong nhat) */
                background-color: #F1C4C5;
                /* Mau chu nut START (Do dam) */
                color: #D33E42;
                border: none;
                border-radius: 24px;
                font-weight: bold;
                font-size: 64px;
            }
            QPushButton:hover {
                /* Mau nut khi di chuot qua */
                background-color: #F3CFD1;
            }
            QPushButton:pressed {
                /* Mau nut khi nhan xuong */
                background-color: #EAB9BC;
            }
        """)
        content_layout.addWidget(start_button)

        right_layout.addWidget(right_content, 0, Qt.AlignHCenter | Qt.AlignTop)
        right_layout.addStretch(1)

        return right_widget

    def create_logo_section(self):
        """Tạo phần logo và tiêu đề, căn giữa"""
        logo_layout = QVBoxLayout()
        logo_layout.setAlignment(Qt.AlignHCenter)
        logo_layout.setContentsMargins(0, 0, 0, 0)
        logo_layout.setSpacing(0)

        # Ảnh logo
        logo_label = QLabel()
        logo_label.setFixedSize(430, 210)

        # Tìm logo ở nhiều vị trí
        logo_paths = [
            os.path.join(os.path.dirname(__file__), '../../../assets/images/logo.png'),
            os.path.join(os.path.dirname(__file__), '../../../public/logo.png'),
            r"D:\photobooth2\public\logo\logo.png",
            r"D:\photobooth2\assets\images\logo.png",
        ]

        found = False
        for logo_path in logo_paths:
            if os.path.exists(logo_path):
                pixmap = QPixmap(logo_path)
                scaled_pixmap = pixmap.scaled(
                    QSize(430, 210), Qt.KeepAspectRatio, Qt.SmoothTransformation
                )
                logo_label.setPixmap(scaled_pixmap)
                logo_label.setAlignment(Qt.AlignCenter)
                found = True
                break

        if not found:
            logo_label.setText("PHOTOBOOTH")
            logo_label.setStyleSheet("color: #D33E42; font-size: 48px; font-weight: bold;")
            logo_label.setAlignment(Qt.AlignCenter)

        logo_layout.addWidget(logo_label, alignment=Qt.AlignHCenter)

        return logo_layout

    def get_button_font(self):
        """Lấy font chữ cho các nút"""
        font = QFont()
        font.setFamilies(["Cooper Black", "Arial Black", "Segoe UI"])
        font.setPointSize(40)
        font.setBold(True)
        return font

    def start_camera_preview(self):
        """Bật camera preview cho người dùng xem trước"""
        if self.camera_view:
            self.camera_view.start()

    def stop_camera_preview(self):
        """Tắt camera preview nếu đang chạy"""
        if self.camera_view:
            self.camera_view.stop()

    def on_start_clicked(self):
        """Xử lý khi người dùng nhấn nút Start"""
        self.start_clicked.emit()

    def keyPressEvent(self, event):
        """Bắt phím F2 để mở admin"""
        if event.key() == Qt.Key_F2:
            self.open_admin.emit()
        else:
            super().keyPressEvent(event)

    def apply_styles(self):
        """Áp dụng style toàn cục cho màn hình"""
        self.setStyleSheet("""
            HomeScreen {
                /* Mau nen tong the cua Man hinh chinh (Hong tim nhat) */
                background-color: #E9E1E3;
            }
            QLabel {
                font-family: 'Cooper Black', 'Segoe UI', Arial;
            }
            QFrame#contentFrame {
                /* Mau nen cua khung noi dung chinh */
                background-color: #E9E1E3;
                border-radius: 24px;
            }
        """)

    def closeEvent(self, event):
        """Dừng camera khi đóng giao diện"""
        self.stop_camera_preview()
        super().closeEvent(event)

    def showEvent(self, event):
        """Bật camera khi màn hình hiển thị"""
        super().showEvent(event)
        self.start_camera_preview()

    def hideEvent(self, event):
        """Dừng camera khi màn hình bị ẩn"""
        self.stop_camera_preview()
        super().hideEvent(event)

    def cleanup_before_exit(self):
        """Hook để bảo đảm camera được dừng khi app thoát"""
        self.stop_camera_preview()


if __name__ == "__main__":
    from PyQt5.QtWidgets import QApplication
    from PyQt5.QtCore import QSharedMemory

    # Project root đã được thiết lập ở đầu file

    instance_lock = QSharedMemory("photobooth_v3_single_instance_home")
    if instance_lock.attach() or not instance_lock.create(1):
        print("PhotoBooth is already running.")

    app = QApplication(sys.argv)
    w = HomeScreen()
    app.aboutToQuit.connect(w.cleanup_before_exit)
    w.showFullScreen()
    sys.exit(app.exec_())
