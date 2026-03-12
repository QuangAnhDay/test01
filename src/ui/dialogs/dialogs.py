# ==========================================
# DIALOG COMPONENTS (MEMORY UPLOAD VERSION)
# ==========================================
"""
Các dialog popup: QR tải ảnh, QR tải ảnh + video.
Đã cập nhật để nhận dữ liệu ảnh trực tiếp từ bộ nhớ (RAM).
"""

import qrcode
from io import BytesIO
from PyQt5.QtWidgets import QDialog, QWidget, QLabel, QPushButton, QVBoxLayout, QHBoxLayout, QFrame
from PyQt5.QtCore import Qt, QTimer
from PyQt5.QtGui import QPixmap
from src.services.cloud.cloud_upload import CloudinaryUploadThread, CloudinaryLandingPageThread


class DownloadQRDialog(QDialog):
    """Dialog hiển thị QR code để khách tải ảnh (Dùng cho bản trả phí)."""

    def __init__(self, image_data, parent=None):
        super().__init__(parent)
        self.image_data = image_data
        self.upload_thread = None

        self.setWindowTitle("📱 Download photos to phone")
        self.setFixedSize(500, 600)
        self.setStyleSheet("""
            QDialog { background-color: #1a1a2e; border-radius: 20px; }
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

        # --- AUTO RESET TIMER (60s) ---
        self.auto_close_timer = QTimer(self)
        self.auto_close_timer.setSingleShot(True)
        self.auto_close_timer.timeout.connect(self.accept)
        self.auto_close_timer.start(60000)

    def setup_ui(self):
        layout = QVBoxLayout(self)
        layout.setAlignment(Qt.AlignCenter)
        layout.setSpacing(20)
        layout.setContentsMargins(30, 30, 30, 30)

        self.title_label = QLabel("☁️ UPLOADING TO CLOUD...")
        self.title_label.setStyleSheet("font-size: 24px; font-weight: bold; color: #ffd700;")
        self.title_label.setAlignment(Qt.AlignCenter)
        layout.addWidget(self.title_label)

        self.status_label = QLabel("Please wait a moment...")
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

        self.btn_close = QPushButton("✅ CLOSE")
        self.btn_close.setFixedSize(200, 60)
        self.btn_close.clicked.connect(self.accept)
        self.btn_close.hide()
        layout.addWidget(self.btn_close, alignment=Qt.AlignCenter)

    def start_upload(self):
        """Bắt đầu upload ảnh lên Cloudinary từ RAM."""
        self.upload_thread = CloudinaryUploadThread(self.image_data)
        self.upload_thread.upload_success.connect(self.on_upload_success)
        self.upload_thread.upload_error.connect(self.on_upload_error)
        self.upload_thread.start()

    def on_upload_success(self, url):
        self.title_label.setText("📱 SCAN TO DOWNLOAD")
        self.title_label.setStyleSheet("font-size: 24px; font-weight: bold; color: #06d6a0;")
        self.status_label.setText("Photo uploaded successfully!")

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

        self.instruction_label.setText("📲 Open your phone camera to scan!")
        self.instruction_label.setStyleSheet("font-size: 16px; color: #ffd700;")
        self.btn_close.show()

    def on_upload_error(self, error_msg):
        self.title_label.setText("❌ UPLOAD ERROR")
        self.status_label.setText(f"Could not upload. Error: {error_msg}")
        self.qr_label.setText("❌")
        self.btn_close.show()


class DownloadSingleQRDialog(QDialog):
    """Dialog hiển thị QR code dẫn tới Landing Page (Dùng cho bản Free/Interactive)."""

    def __init__(self, image_data, video_path=None, parent=None):
        super().__init__(parent)
        self.image_data = image_data
        self.video_path = video_path

        self.setWindowTitle("📱 Download your memories")
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

        # --- AUTO RESET TIMER (60s) ---
        self.auto_close_timer = QTimer(self)
        self.auto_close_timer.setSingleShot(True)
        self.auto_close_timer.timeout.connect(self.accept)
        self.auto_close_timer.start(60000)

    def setup_ui(self):
        layout = QVBoxLayout(self)
        layout.setSpacing(20)
        layout.setContentsMargins(40, 40, 40, 40)

        self.title_label = QLabel("☁️ CREATING DOWNLOAD PAGE...")
        self.title_label.setStyleSheet("font-size: 22px; font-weight: bold; color: #ffd700;")
        self.title_label.setAlignment(Qt.AlignCenter)
        layout.addWidget(self.title_label)

        self.qr_label = QLabel("⌛")
        self.qr_label.setFixedSize(300, 300)
        self.qr_label.setAlignment(Qt.AlignCenter)
        self.qr_label.setStyleSheet("background-color: white; border-radius: 20px; font-size: 60px; color: #333;")
        layout.addWidget(self.qr_label, alignment=Qt.AlignCenter)

        msg = "Processing photos, please wait..."
        if self.video_path:
            msg = "Processing photos and video, please wait..."
            
        self.status_label = QLabel(msg)
        self.status_label.setWordWrap(True)
        self.status_label.setAlignment(Qt.AlignCenter)
        self.status_label.setStyleSheet("color: #aaa; font-size: 14px;")
        layout.addWidget(self.status_label)

        self.btn_close = QPushButton("✅ DONE")
        self.btn_close.setFixedSize(200, 50)
        self.btn_close.clicked.connect(self.accept)
        self.btn_close.hide()
        layout.addWidget(self.btn_close, alignment=Qt.AlignCenter)

    def start_combined_upload(self):
        """Bắt đầu upload từ RAM + Video (nếu có)."""
        self.thread = CloudinaryLandingPageThread(self.image_data, self.video_path)
        self.thread.upload_success.connect(self.on_upload_success)
        self.thread.upload_error.connect(self.on_upload_error)
        self.thread.start()

    def on_upload_success(self, url):
        self.title_label.setText("📱 SCAN TO DOWNLOAD")
        self.title_label.setStyleSheet("font-size: 24px; font-weight: bold; color: #06d6a0;")
        
        if self.video_path:
            self.status_label.setText("Memories ready! Includes photos & video.")
        else:
            self.status_label.setText("Memories ready! Scan to get photos.")

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
        self.title_label.setText("❌ ERROR")
        self.status_label.setText(f"An error occurred: {error_msg}")
        self.btn_close.show()


class FinishDialog(QDialog):
    """
    Dialog xác nhận cuối cùng: 
    - QR Code tải ảnh & video
    - Chọn số lượng bản in (Chẵn cho dọc, tự nhiên cho custom)
    """

    def __init__(self, image_data, video_path=None, layout_type="4x1", parent=None):
        super().__init__(parent)
        self.image_data = image_data
        self.video_path = video_path
        self.layout_type = layout_type
        
        # Tự động phát hiện group của layout để áp dụng quy tắc in
        from src.shared.types.models import get_layout_config
        cfg = get_layout_config(layout_type)
        self.is_vertical_group = cfg.get("group") == "vertical"
        print(f"[DEBUG] FinishDialog: layout={layout_type}, group={cfg.get('group')}, is_vertical={self.is_vertical_group}")
        
        # Mặc định: 2 cho dọc, 1 cho custom
        # Cường chế số chẵn ngay từ đầu nếu là nhóm dọc
        self.print_count = 2 if self.is_vertical_group else 1

        self.setWindowFlags(Qt.FramelessWindowHint | Qt.Dialog)
        self.setAttribute(Qt.WA_TranslucentBackground)
        self.setFixedSize(700, 850)

        self.setup_ui()
        self.start_upload()

    def setup_ui(self):
        # Container chính với bo góc và viền trắng
        self.container = QFrame(self)
        self.container.setGeometry(10, 10, 680, 830)
        self.container.setStyleSheet("""
            QFrame {
                background-color: #F2E3E5;
                border-radius: 40px;
                border: 5px solid white;
            }
        """)

        layout = QVBoxLayout(self.container)
        layout.setContentsMargins(40, 40, 40, 40)
        layout.setSpacing(25)

        # Tiêu đề
        self.title_label = QLabel("FINISHED!")
        self.title_label.setAlignment(Qt.AlignCenter)
        self.title_label.setStyleSheet("""
            color: #FF7E7E; font-family: 'Cooper Black', 'Arial';
            font-size: 36px; font-weight: bold; border: none;
        """)
        layout.addWidget(self.title_label)

        # Vùng QR
        self.qr_box = QFrame()
        self.qr_box.setFixedSize(350, 350)
        self.qr_box.setStyleSheet("background-color: white; border-radius: 25px; border: 3px solid #FADBDC;")
        qr_layout = QVBoxLayout(self.qr_box)
        
        self.qr_label = QLabel("⏳")
        self.qr_label.setAlignment(Qt.AlignCenter)
        self.qr_label.setStyleSheet("font-size: 60px; color: #FADBDC; border: none;")
        qr_layout.addWidget(self.qr_label)
        
        layout.addWidget(self.qr_box, alignment=Qt.AlignCenter)

        self.status_label = QLabel("Creating download QR code...")
        self.status_label.setAlignment(Qt.AlignCenter)
        self.status_label.setStyleSheet("color: #FF7E7E; font-family: 'Arial'; font-size: 18px; border: none;")
        layout.addWidget(self.status_label)

        # Ngăn cách
        line = QFrame()
        line.setFrameShape(QFrame.HLine)
        line.setStyleSheet("background-color: white; min-height: 2px; border: none;")
        layout.addWidget(line)

        # Phần chọn số lượng in
        print_layout = QHBoxLayout()
        
        print_label = QLabel("QUANTITY:")
        print_label.setStyleSheet("color: #FF7E7E; font-family: 'Cooper Black'; font-size: 24px; border: none;")
        print_layout.addWidget(print_label)
        
        counter_layout = QHBoxLayout()
        counter_layout.setSpacing(10)
        
        btn_minus = QPushButton("-")
        btn_plus = QPushButton("+")
        self.lbl_count = QLabel(str(self.print_count))
        
        btn_style = """
            QPushButton {
                background-color: white; color: #FF7E7E;
                font-size: 30px; font-weight: bold;
                border-radius: 15px; border: 3px solid #FF7E7E;
                min-width: 50px; min-height: 50px;
            }
            QPushButton:hover { background-color: #FFF0F0; }
        """
        btn_minus.setStyleSheet(btn_style)
        btn_plus.setStyleSheet(btn_style)
        self.lbl_count.setStyleSheet("color: #FF7E7E; font-size: 32px; font-weight: bold; min-width: 40px; border: none;")
        self.lbl_count.setAlignment(Qt.AlignCenter)
        
        btn_minus.clicked.connect(self.decrease_count)
        btn_plus.clicked.connect(self.increase_count)
        
        counter_layout.addWidget(btn_minus)
        counter_layout.addWidget(self.lbl_count)
        counter_layout.addWidget(btn_plus)
        
        print_layout.addLayout(counter_layout)
        layout.addLayout(print_layout)

        # Nút xác nhận cuối cùng
        self.btn_finish = QPushButton("CONFIRM & PRINT !")
        self.btn_finish.setStyleSheet("""
            QPushButton {
                background-color: #FF7E7E; color: white;
                font-family: 'Cooper Black'; font-size: 28px;
                border-radius: 20px; border: 5px solid white;
                min-height: 80px;
            }
            QPushButton:hover { background-color: #FF9494; }
        """)
        self.btn_finish.clicked.connect(self.accept)
        layout.addWidget(self.btn_finish)

    def decrease_count(self):
        step = 2 if self.is_vertical_group else 1
        self.print_count -= step
        # Đảm bảo tối thiểu là 2 cho group dọc, 0 cho custom
        min_val = 2 if self.is_vertical_group else 0
        self.print_count = max(min_val, self.print_count)
        # Đảm bảo luôn chẵn nếu là dọc (phòng hờ)
        if self.is_vertical_group and self.print_count % 2 != 0:
            self.print_count += 1
        self.lbl_count.setText(str(self.print_count))

    def increase_count(self):
        step = 2 if self.is_vertical_group else 1
        self.print_count = min(10, self.print_count + step)
        # Đảm bảo luôn chẵn nếu là dọc
        if self.is_vertical_group and self.print_count % 2 != 0:
            self.print_count = min(10, self.print_count + 1)
        self.lbl_count.setText(str(self.print_count))

    def start_upload(self):
        self.thread = CloudinaryLandingPageThread(self.image_data, self.video_path)
        self.thread.upload_success.connect(self.on_upload_success)
        self.thread.upload_error.connect(self.on_upload_error)
        self.thread.start()

    def on_upload_success(self, url):
        self.status_label.setText("✅ SCAN TO DOWNLOAD")
        qr = qrcode.QRCode(version=1, box_size=10, border=1)
        qr.add_data(url)
        qr.make(fit=True)
        img = qr.make_image(fill_color="black", back_color="white")
        buf = BytesIO()
        img.save(buf, format='PNG')
        pix = QPixmap()
        pix.loadFromData(buf.getvalue())
        self.qr_label.setPixmap(pix.scaled(300, 300, Qt.KeepAspectRatio, Qt.SmoothTransformation))

    def on_upload_error(self, error):
        self.status_label.setText(f"❌ Error: {error[:30]}")
