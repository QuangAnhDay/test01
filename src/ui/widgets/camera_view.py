import os
import cv2
from PyQt5.QtWidgets import QFrame, QLabel, QVBoxLayout
from PyQt5.QtCore import Qt, pyqtSignal, QRectF
from PyQt5.QtGui import QImage, QPixmap, QRegion, QPainterPath, QPainter
import logging

logger = logging.getLogger(__name__)


class CameraView(QFrame):
    """
    Widget hiển thị camera feed với bo góc.
    Dữ liệu (frame) được đẩy vào từ CameraHandler trung tâm thông qua hàm set_frame().
    """

    camera_changed = pyqtSignal(int)

    def __init__(self, initial_camera_index=0, parent=None):
        super().__init__(parent)

        # Cấu hình container chính (Khung trắng bo góc)
        self.setFixedSize(730, 470)
        self.setObjectName("cameraViewFrame")
        self.setStyleSheet("""
            #cameraViewFrame {
                background-color: white;
                border-radius: 24px;
            }
        """)

        # Áp dụng mask cho container ngoài để chắc chắn viền trắng bo tròn
        self._apply_outer_mask()

        # Khung đen bên trong để chứa camera feed (Lọt lòng 5px)
        self.inner_frame = QFrame(self)
        self.inner_frame.setFixedSize(720, 460)
        self.inner_frame.move(5, 5)
        self.inner_frame.setObjectName("cameraInner")
        self.inner_frame.setStyleSheet("""
            #cameraInner {
                background-color: black;
                border-radius: 19px;
            }
        """)
        
        # Áp dụng mask cho khung đen để bo cả feed camera bên trong
        inner_path = QPainterPath()
        inner_path.addRoundedRect(QRectF(0, 0, 720, 460), 19, 19)
        self.inner_frame.setMask(QRegion(inner_path.toFillPolygon().toPolygon()))

        # Layout trong khung đen
        inner_layout = QVBoxLayout(self.inner_frame)
        inner_layout.setContentsMargins(0, 0, 0, 0)

        # Label hiển thị camera feed
        self.image_label = QLabel("Khởi tạo Camera...", self.inner_frame)
        self.image_label.setAlignment(Qt.AlignCenter)
        self.image_label.setStyleSheet("color: white; background: transparent;")
        self.image_label.setFixedSize(720, 460)
        inner_layout.addWidget(self.image_label)

        self.current_camera_index = initial_camera_index
        self._is_running = False

    def set_frame(self, qt_img):
        """Nhận và hiển thị frame từ CameraHandler tập trung."""
        self.display_frame(qt_img)

    def start(self):
        """Bật hiển thị (Thực tế chỉ là trạng thái vì handler điều khiển luồng)."""
        self._is_running = True
        logger.info("CameraView started (Passive mode)")

    def stop(self):
        """Dừng hiển thị và xóa màn hình."""
        self._is_running = False
        self.image_label.clear()
        self.image_label.setText("Camera Offline")
        logger.info("CameraView stopped")

    def display_frame(self, qt_image):
        """Vẽ frame lên label với bo góc."""
        if not self._is_running or qt_image is None:
            return
            
        if isinstance(qt_image, QImage):
             if qt_image.isNull(): return
             pixmap = QPixmap.fromImage(qt_image)
        elif isinstance(qt_image, QPixmap):
             if qt_image.isNull(): return
             pixmap = qt_image
        else:
            return

        # Scale để lấp đầy label
        lbl_size = self.image_label.size()
        if not lbl_size.isEmpty():
            scaled = pixmap.scaled(lbl_size, Qt.KeepAspectRatioByExpanding, Qt.SmoothTransformation)
            from src.utils import get_rounded_pixmap
            rounded = get_rounded_pixmap(scaled, radius=24)
            self.image_label.setPixmap(rounded)
        else:
            self.image_label.setPixmap(pixmap)

    def _apply_outer_mask(self):
        """Tạo mask bo góc cho toàn bộ khung trắng ngoài cùng"""
        path = QPainterPath()
        path.addRoundedRect(QRectF(0, 0, 730, 470), 24, 24)
        region = QRegion(path.toFillPolygon().toPolygon())
        self.setMask(region)

    def handle_camera_error(self, error_message):
        """Hiển thị thông báo lỗi lên màn hình camera."""
        logger.error(f"Camera View Error: {error_message}")
        self.image_label.setText(error_message)

    def closeEvent(self, event):
        self.stop()
        super().closeEvent(event)
