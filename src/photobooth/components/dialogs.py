# ==========================================
# DIALOG COMPONENTS
# ==========================================
"""
Các dialog popup: QR tải ảnh, QR tải ảnh + video.
"""

import qrcode
from io import BytesIO
from PyQt5.QtWidgets import QDialog, QWidget, QLabel, QPushButton, QVBoxLayout, QHBoxLayout
from PyQt5.QtCore import Qt, QTimer
from PyQt5.QtGui import QPixmap
from src.modules.storage.cloud_upload import CloudinaryUploadThread, CloudinaryLandingPageThread
from src.shared.utils.helpers import convert_cv_qt


class DownloadQRDialog(QDialog):
    """Dialog hiển thị QR code để khách tải ảnh."""

    def __init__(self, image_path, parent=None):
        super().__init__(parent)
        self.image_path = image_path
        self.upload_thread = None

        self.setWindowTitle("📱 Tải ảnh về điện thoại")
        self.setFixedSize(500, 600)
        self.setStyleSheet("""
            QDialog { background-color: #1a1a2e; }
            QLabel { color: white; font-family: 'Arial', 'Tahoma', sans-serif; }
            QPushButton {
                background-color: #e94560; color: white; border: none;
                border-radius: 10px; padding: 15px 30px;
                font-size: 18px; font-weight: bold;
            }
            QPushButton:hover { background-color: #ff6b6b; }
        """)

        self.setup_ui()
        self.start_upload()

    def setup_ui(self):
        layout = QVBoxLayout(self)
        layout.setAlignment(Qt.AlignCenter)
        layout.setSpacing(20)
        layout.setContentsMargins(30, 30, 30, 30)

        self.title_label = QLabel("☁️ ĐANG TẢI ẢNH LÊN CLOUD...")
        self.title_label.setStyleSheet("font-size: 24px; font-weight: bold; color: #ffd700;")
        self.title_label.setAlignment(Qt.AlignCenter)
        layout.addWidget(self.title_label)

        self.status_label = QLabel("Vui lòng chờ trong giây lát...")
        self.status_label.setStyleSheet("font-size: 16px; color: #a8dadc;")
        self.status_label.setAlignment(Qt.AlignCenter)
        self.status_label.setWordWrap(True)
        layout.addWidget(self.status_label)

        self.qr_container = QWidget()
        self.qr_container.setFixedSize(350, 350)
        self.qr_container.setStyleSheet("background-color: white; border-radius: 20px;")
        qr_layout = QVBoxLayout(self.qr_container)
        qr_layout.setAlignment(Qt.AlignCenter)

        self.qr_label = QLabel()
        self.qr_label.setAlignment(Qt.AlignCenter)
        self.qr_label.setFixedSize(300, 300)
        self.qr_label.setText("⏳")
        self.qr_label.setStyleSheet("font-size: 80px; background-color: white;")
        qr_layout.addWidget(self.qr_label)

        layout.addWidget(self.qr_container, alignment=Qt.AlignCenter)

        self.instruction_label = QLabel("")
        self.instruction_label.setStyleSheet("font-size: 14px; color: #a8dadc;")
        self.instruction_label.setAlignment(Qt.AlignCenter)
        self.instruction_label.setWordWrap(True)
        layout.addWidget(self.instruction_label)

        self.btn_close = QPushButton("✅ ĐÓNG")
        self.btn_close.setFixedSize(200, 60)
        self.btn_close.clicked.connect(self.accept)
        self.btn_close.hide()
        layout.addWidget(self.btn_close, alignment=Qt.AlignCenter)

    def start_upload(self):
        """Bắt đầu upload ảnh lên Cloudinary."""
        self.upload_thread = CloudinaryUploadThread(self.image_path)
        self.upload_thread.upload_success.connect(self.on_upload_success)
        self.upload_thread.upload_error.connect(self.on_upload_error)
        self.upload_thread.start()

    def on_upload_success(self, url):
        """Xử lý khi upload thành công."""
        self.title_label.setText("📱 QUÉT MÃ ĐỂ TẢI ẢNH")
        self.title_label.setStyleSheet("font-size: 24px; font-weight: bold; color: #06d6a0;")
        self.status_label.setText("Ảnh đã được tải lên thành công!")

        qr = qrcode.QRCode(version=1, box_size=10, border=2)
        qr.add_data(url)
        qr.make(fit=True)
        qr_img = qr.make_image(fill_color="black", back_color="white")

        buffer = BytesIO()
        qr_img.save(buffer, format='PNG')
        buffer.seek(0)

        pixmap = QPixmap()
        pixmap.loadFromData(buffer.getvalue())
        scaled = pixmap.scaled(280, 280, Qt.KeepAspectRatio, Qt.SmoothTransformation)

        self.qr_label.setStyleSheet("background-color: white;")
        self.qr_label.setPixmap(scaled)

        self.instruction_label.setText(
            "📲 Mở camera điện thoại và quét mã QR\n"
            "để tải ảnh về máy của bạn!"
        )
        self.instruction_label.setStyleSheet("font-size: 16px; color: #ffd700;")
        self.btn_close.show()

    def on_upload_error(self, error_msg):
        """Xử lý khi upload thất bại."""
        self.title_label.setText("❌ LỖI TẢI ẢNH")
        self.title_label.setStyleSheet("font-size: 24px; font-weight: bold; color: #e94560;")
        self.status_label.setText(f"Không thể tải ảnh lên Cloud.\n\nLỗi: {error_msg}")
        self.status_label.setStyleSheet("font-size: 14px; color: #ff6b6b;")

        self.qr_label.setText("❌")
        self.qr_label.setStyleSheet("font-size: 80px; background-color: white; color: #e94560;")

        self.instruction_label.setText(
            "Ảnh vẫn được lưu tại thư mục D:\\picture\n"
            "Vui lòng liên hệ nhân viên để được hỗ trợ."
        )
        self.btn_close.setText("ĐÓNG")
        self.btn_close.show()


class DownloadSingleQRDialog(QDialog):
    """Dialog hiển thị DUY NHẤT 1 QR code dẫn tới trang web chứa cả ảnh và video."""

    def __init__(self, image_path, video_path=None, parent=None):
        super().__init__(parent)
        self.image_path = image_path
        self.video_path = video_path

        self.setWindowTitle("📱 Tải ảnh và Video")
        self.setFixedSize(500, 600)
        self.setStyleSheet("""
            QDialog { background-color: #1a1a2e; border-radius: 20px; }
            QLabel { color: white; font-family: 'Arial', sans-serif; }
            QPushButton {
                background-color: #709a8a; color: white;
                border-radius: 15px; padding: 15px;
                font-size: 18px; font-weight: bold;
            }
            QPushButton:hover { background-color: #84af9f; }
        """)

        self.setup_ui()
        self.start_combined_upload()

    def setup_ui(self):
        layout = QVBoxLayout(self)
        layout.setSpacing(20)
        layout.setContentsMargins(40, 40, 40, 40)

        self.title_label = QLabel("☁️ ĐANG TẠO TRANG TẢI...")
        self.title_label.setStyleSheet("font-size: 22px; font-weight: bold; color: #ffd700;")
        self.title_label.setAlignment(Qt.AlignCenter)
        layout.addWidget(self.title_label)

        self.qr_label = QLabel("⌛")
        self.qr_label.setFixedSize(300, 300)
        self.qr_label.setAlignment(Qt.AlignCenter)
        self.qr_label.setStyleSheet("background-color: white; border-radius: 20px; font-size: 60px; color: #333;")
        layout.addWidget(self.qr_label, alignment=Qt.AlignCenter)

        self.status_label = QLabel("Đang xử lý ảnh và video, vui lòng đợi giây lát...")
        self.status_label.setWordWrap(True)
        self.status_label.setAlignment(Qt.AlignCenter)
        self.status_label.setStyleSheet("color: #aaa; font-size: 14px;")
        layout.addWidget(self.status_label)

        self.btn_close = QPushButton("✅ HOÀN TẤT")
        self.btn_close.setFixedSize(200, 50)
        self.btn_close.clicked.connect(self.accept)
        self.btn_close.hide()
        layout.addWidget(self.btn_close, alignment=Qt.AlignCenter)

    def start_combined_upload(self):
        """Bắt đầu tiến trình upload và tạo trang Landing Page."""
        self.thread = CloudinaryLandingPageThread(self.image_path, self.video_path)
        self.thread.upload_success.connect(self.on_upload_success)
        self.thread.upload_error.connect(self.on_upload_error)
        self.thread.start()

    def on_upload_success(self, url):
        """Khi đã có link Landing Page, tạo QR."""
        self.title_label.setText("📱 QUÉT MÃ ĐỂ TẢI")
        self.title_label.setStyleSheet("font-size: 24px; font-weight: bold; color: #06d6a0;")
        self.status_label.setText("Trang kỷ niệm của bạn đã sẵn sàng! Quét mã để xem và tải cả ảnh & video.")

        qr = qrcode.QRCode(version=1, box_size=10, border=1)
        qr.add_data(url)
        qr.make(fit=True)
        img = qr.make_image(fill_color="black", back_color="white")

        buf = BytesIO()
        img.save(buf, format='PNG')
        pix = QPixmap()
        pix.loadFromData(buf.getvalue())
        scaled = pix.scaled(280, 280, Qt.KeepAspectRatio, Qt.SmoothTransformation)

        self.qr_label.setPixmap(scaled)
        self.btn_close.show()

    def on_upload_error(self, error_msg):
        self.title_label.setText("❌ LỖI XỬ LÝ")
        self.status_label.setText(f"Có lỗi xảy ra: {error_msg}")
        self.btn_close.show()
