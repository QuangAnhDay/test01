import sys
import os
import cv2
import time
import json
import random
import string
import subprocess
import numpy as np
import qrcode
import requests
from io import BytesIO
from PIL import Image
from PyQt5.QtWidgets import (QApplication, QMainWindow, QWidget, QLabel, 
                             QPushButton, QVBoxLayout, QHBoxLayout, QScrollArea, 
                             QMessageBox, QFrame, QGridLayout, QStackedWidget,
                             QGraphicsOpacityEffect, QDialog, QSlider, QGroupBox)
from PyQt5.QtCore import Qt, QTimer, QSize, QPropertyAnimation, QPoint, QEasingCurve, QSequentialAnimationGroup, QParallelAnimationGroup, QThread, pyqtSignal
from PyQt5.QtGui import QImage, QPixmap, QFont, QIcon

# Cloudinary upload
import cloudinary
import cloudinary.uploader

# ==========================================
# CẤU HÌNH (CONFIGURATION)
# ==========================================
CONFIG_FILE = "config.json"
WINDOW_TITLE = "Photobooth Cảm Ứng"
WINDOW_WIDTH = 1200
WINDOW_HEIGHT = 800
CAMERA_INDEX = 0
FIRST_PHOTO_DELAY = 10  # Giây cho ảnh đầu tiên
BETWEEN_PHOTO_DELAY = 1  # Giây giữa các ảnh
PHOTOS_TO_TAKE = 10
TEMPLATE_DIR = "templates"
OUTPUT_DIR = "output"
SAMPLE_PHOTOS_DIR = "sample_photos"

# ==========================================
# BIẾN TOÀN CỤC CHO CẤU HÌNH
# ==========================================
APP_CONFIG = {}

def load_config():
    """Tải cấu hình từ file config.json."""
    global APP_CONFIG
    if not os.path.exists(CONFIG_FILE):
        return False
    try:
        with open(CONFIG_FILE, 'r', encoding='utf-8') as f:
            APP_CONFIG = json.load(f)
        
        # Cấu hình Cloudinary từ config
        cloud_config = APP_CONFIG.get('cloudinary', {})
        if all([cloud_config.get('cloud_name'), cloud_config.get('api_key'), cloud_config.get('api_secret')]):
            import cloudinary
            cloudinary.config(
                cloud_name=cloud_config.get('cloud_name'),
                api_key=cloud_config.get('api_key'),
                api_secret=cloud_config.get('api_secret'),
                secure=True
            )
        return True
    except Exception as e:
        print(f"Lỗi đọc config: {e}")
        return False

def get_price_2():
    """Lấy giá gói 2 ảnh từ config."""
    return APP_CONFIG.get('price_2_photos', 20000)

def get_price_4():
    """Lấy giá gói 4 ảnh từ config."""
    return APP_CONFIG.get('price_4_photos', 35000)

def format_price(amount):
    """Format số tiền thành chuỗi VNĐ."""
    return f"{amount:,}".replace(",", ".") + " VNĐ"

def generate_unique_code():
    """Tạo mã giao dịch duy nhất: PB + 4 ký tự ngẫu nhiên."""
    chars = string.ascii_uppercase + string.digits
    return "PB" + ''.join(random.choices(chars, k=4))

def generate_vietqr_url(amount, description):
    """Tạo URL VietQR động từ config."""
    bank_bin = APP_CONFIG.get('bank_bin', '')
    account = APP_CONFIG.get('bank_account', '')
    name = APP_CONFIG.get('account_name', '')
    
    # Format: https://img.vietqr.io/image/{bank_bin}-{account}-compact2.png?amount={amount}&addInfo={description}&accountName={name}
    url = f"https://img.vietqr.io/image/{bank_bin}-{account}-compact2.png"
    url += f"?amount={amount}&addInfo={description}&accountName={name}"
    return url

# ==========================================
# HÀM HỖ TRỢ (HELPER FUNCTIONS)
# ==========================================

def ensure_directories():
    """Tạo các thư mục cần thiết."""
    if not os.path.exists(TEMPLATE_DIR):
        os.makedirs(TEMPLATE_DIR)
        create_sample_templates()
    if not os.path.exists(OUTPUT_DIR):
        os.makedirs(OUTPUT_DIR)
    if not os.path.exists(SAMPLE_PHOTOS_DIR):
        os.makedirs(SAMPLE_PHOTOS_DIR)
        create_sample_photos()


def create_sample_templates():
    """Tạo các template mẫu."""
    width, height = 1280, 720
    
    # Template 1: Khung đỏ đơn giản
    img = np.zeros((height, width, 4), dtype=np.uint8)
    cv2.rectangle(img, (0, 0), (width, height), (0, 0, 255, 255), 40)
    cv2.putText(img, "PHOTOBOOTH", (width//2 - 200, 60), cv2.FONT_HERSHEY_SIMPLEX, 2, (255, 255, 255, 255), 4)
    img[80:height-40, 40:width-40] = [0, 0, 0, 0]
    cv2.imwrite(os.path.join(TEMPLATE_DIR, "frame_red.png"), img)
    
    # Template 2: Khung xanh
    img2 = np.zeros((height, width, 4), dtype=np.uint8)
    cv2.rectangle(img2, (0, 0), (width, height), (255, 100, 0, 255), 40)
    cv2.putText(img2, "MEMORIES", (width//2 - 150, 60), cv2.FONT_HERSHEY_SIMPLEX, 2, (255, 255, 255, 255), 4)
    img2[80:height-40, 40:width-40] = [0, 0, 0, 0]
    cv2.imwrite(os.path.join(TEMPLATE_DIR, "frame_blue.png"), img2)

def create_sample_photos():
    """Tạo các ảnh mẫu demo."""
    colors = [
        ((255, 100, 150), "Memory 1"),
        ((100, 200, 255), "Memory 2"),
        ((150, 255, 150), "Memory 3"),
        ((255, 200, 100), "Memory 4"),
        ((200, 150, 255), "Memory 5"),
        ((100, 255, 200), "Memory 6"),
        ((255, 150, 200), "Memory 7"),
        ((150, 200, 255), "Memory 8"),
    ]
    
    for i, (color, text) in enumerate(colors):
        img = np.zeros((400, 300, 3), dtype=np.uint8)
        # Gradient background
        for y in range(400):
            ratio = y / 400
            img[y, :] = (
                int(color[0] * (1 - ratio * 0.5)),
                int(color[1] * (1 - ratio * 0.5)),
                int(color[2] * (1 - ratio * 0.5))
            )
        # Add text
        cv2.putText(img, text, (50, 200), cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 255, 255), 2)
        cv2.putText(img, "Sample", (80, 250), cv2.FONT_HERSHEY_SIMPLEX, 0.8, (255, 255, 255), 2)
        cv2.imwrite(os.path.join(SAMPLE_PHOTOS_DIR, f"sample_{i+1}.jpg"), img)



def generate_qr_code(content, size=300):
    """Tạo mã QR từ nội dung."""
    qr = qrcode.QRCode(
        version=1,
        error_correction=qrcode.constants.ERROR_CORRECT_L,
        box_size=10,
        border=4,
    )
    qr.add_data(content)
    qr.make(fit=True)
    
    qr_img = qr.make_image(fill_color="black", back_color="white")
    qr_img = qr_img.resize((size, size))
    
    # Convert PIL Image to QPixmap
    buffer = BytesIO()
    qr_img.save(buffer, format="PNG")
    buffer.seek(0)
    
    q_img = QImage()
    q_img.loadFromData(buffer.getvalue())
    return QPixmap.fromImage(q_img)

def overlay_images(background, foreground):
    """Ghép ảnh foreground (có alpha) lên background."""
    bg_h, bg_w = background.shape[:2]
    fg_h, fg_w = foreground.shape[:2]

    if (bg_w, bg_h) != (fg_w, fg_h):
        foreground = cv2.resize(foreground, (bg_w, bg_h))

    if foreground.shape[2] < 4:
        return background
    
    alpha = foreground[:, :, 3] / 255.0
    output = np.zeros_like(background)
    
    for c in range(0, 3):
        output[:, :, c] = (foreground[:, :, c] * alpha + 
                           background[:, :, c] * (1.0 - alpha))
    
    return output

def convert_cv_qt(cv_img):
    """Chuyển đổi ảnh OpenCV sang QPixmap."""
    if cv_img is None:
        return QPixmap()
    rgb_image = cv2.cvtColor(cv_img, cv2.COLOR_BGR2RGB)
    h, w, ch = rgb_image.shape
    bytes_per_line = ch * w
    qt_format = QImage(rgb_image.data, w, h, bytes_per_line, QImage.Format_RGB888)
    return QPixmap.fromImage(qt_format)

def check_printer_available():
    """Kiểm tra xem có máy in nào được kết nối không (Windows)."""
    if os.name != 'nt':
        return False, "Chỉ hỗ trợ Windows"
    
    try:
        # Dùng PowerShell để lấy danh sách máy in
        result = subprocess.run(
            ['powershell', '-Command', 'Get-Printer | Select-Object -ExpandProperty Name'],
            capture_output=True, text=True, timeout=5
        )
        printers = result.stdout.strip().split('\n')
        printers = [p.strip() for p in printers if p.strip()]
        
        if printers:
            return True, printers[0]  # Trả về máy in đầu tiên
        else:
            return False, "Không tìm thấy máy in"
    except Exception as e:
        return False, str(e)

def load_sample_photos():
    """Load các ảnh mẫu từ thư mục."""
    photos = []
    if os.path.exists(SAMPLE_PHOTOS_DIR):
        for f in sorted(os.listdir(SAMPLE_PHOTOS_DIR)):
            if f.lower().endswith(('.jpg', '.jpeg', '.png')):
                photos.append(os.path.join(SAMPLE_PHOTOS_DIR, f))
    # Load từ output nếu có
    if os.path.exists(OUTPUT_DIR):
        for f in sorted(os.listdir(OUTPUT_DIR)):
            if f.lower().endswith(('.jpg', '.jpeg', '.png')):
                photos.append(os.path.join(OUTPUT_DIR, f))
    return photos

# ==========================================
# CLOUDINARY UPLOAD THREAD
# ==========================================

class CloudinaryUploadThread(QThread):
    """Thread để upload ảnh lên Cloudinary mà không block UI."""
    
    # Signals
    upload_success = pyqtSignal(str)  # Emit URL khi thành công
    upload_error = pyqtSignal(str)    # Emit thông báo lỗi
    
    def __init__(self, image_path):
        super().__init__()
        self.image_path = image_path
    
    def run(self):
        try:
            # Upload lên Cloudinary
            result = cloudinary.uploader.upload(
                self.image_path,
                folder="photobooth",
                resource_type="image"
            )
            # Emit URL khi thành công
            self.upload_success.emit(result['secure_url'])
        except Exception as e:
            # Emit lỗi
            self.upload_error.emit(str(e))


# ==========================================
# THREAD TẢI ẢNH QR TỪ VIETQR
# ==========================================
class QRImageLoaderThread(QThread):
    """Thread tải ảnh QR từ VietQR API để không block UI."""
    image_loaded = pyqtSignal(QPixmap)
    load_error = pyqtSignal(str)
    
    def __init__(self, url):
        super().__init__()
        self.url = url
    
    def run(self):
        try:
            response = requests.get(self.url, timeout=15)
            response.raise_for_status()
            img_data = response.content
            pixmap = QPixmap()
            pixmap.loadFromData(img_data)
            self.image_loaded.emit(pixmap)
        except Exception as e:
            self.load_error.emit(str(e))


# ==========================================
# THREAD KIỂM TRA GIAO DỊCH CASSO
# ==========================================
class CassoCheckThread(QThread):
    """
    Thread kiểm tra giao dịch từ Casso API mỗi 3 giây.
    Khi tìm thấy giao dịch khớp số tiền và nội dung, phát signal.
    """
    payment_received = pyqtSignal()  # Signal khi nhận được tiền
    check_error = pyqtSignal(str)    # Signal khi có lỗi
    
    def __init__(self, amount, description):
        super().__init__()
        self.amount = amount
        self.description = description.upper()
        self.running = True
    
    def stop(self):
        """Dừng thread."""
        self.running = False
    
    def run(self):
        api_key = APP_CONFIG.get('casso_api_key', '')
        if not api_key:
            self.check_error.emit("Chưa cấu hình Casso API Key")
            return
        
        headers = {
            "Authorization": f"Apikey {api_key}",
            "Content-Type": "application/json"
        }
        
        while self.running:
            try:
                # Gọi API Casso lấy danh sách giao dịch
                response = requests.get(
                    "https://oauth.casso.vn/v2/transactions",
                    headers=headers,
                    params={"pageSize": 20, "sort": "DESC"},
                    timeout=10
                )
                
                if response.status_code == 200:
                    data = response.json()
                    transactions = data.get('data', {}).get('records', [])
                    
                    for trans in transactions:
                        trans_amount = trans.get('amount', 0)
                        trans_desc = trans.get('description', '').upper()
                        
                        # Kiểm tra khớp số tiền và nội dung chuyển khoản
                        if trans_amount >= self.amount and self.description in trans_desc:
                            self.payment_received.emit()
                            return
                
                # Chờ 3 giây trước khi kiểm tra lại
                for _ in range(30):  # 3 giây = 30 x 0.1s
                    if not self.running:
                        return
                    time.sleep(0.1)
                    
            except Exception as e:
                self.check_error.emit(str(e))
                time.sleep(3)


class DownloadQRDialog(QDialog):
    """Dialog hiển thị QR code để khách tải ảnh."""
    
    def __init__(self, image_path, parent=None):
        super().__init__(parent)
        self.image_path = image_path
        self.upload_thread = None
        
        self.setWindowTitle("📱 Tải ảnh về điện thoại")
        self.setFixedSize(500, 600)
        self.setStyleSheet("""
            QDialog {
                background-color: #1a1a2e;
            }
            QLabel {
                color: white;
                font-family: 'Arial', 'Tahoma', sans-serif;
            }
            QPushButton {
                background-color: #e94560;
                color: white;
                border: none;
                border-radius: 10px;
                padding: 15px 30px;
                font-size: 18px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #ff6b6b;
            }
        """)
        
        self.setup_ui()
        self.start_upload()
    
    def setup_ui(self):
        layout = QVBoxLayout(self)
        layout.setAlignment(Qt.AlignCenter)
        layout.setSpacing(20)
        layout.setContentsMargins(30, 30, 30, 30)
        
        # Title
        self.title_label = QLabel("☁️ ĐANG TẢI ẢNH LÊN CLOUD...")
        self.title_label.setStyleSheet("font-size: 24px; font-weight: bold; color: #ffd700;")
        self.title_label.setAlignment(Qt.AlignCenter)
        layout.addWidget(self.title_label)
        
        # Status/Info label
        self.status_label = QLabel("Vui lòng chờ trong giây lát...")
        self.status_label.setStyleSheet("font-size: 16px; color: #a8dadc;")
        self.status_label.setAlignment(Qt.AlignCenter)
        self.status_label.setWordWrap(True)
        layout.addWidget(self.status_label)
        
        # QR Code container
        self.qr_container = QWidget()
        self.qr_container.setFixedSize(350, 350)
        self.qr_container.setStyleSheet("""
            background-color: white;
            border-radius: 20px;
        """)
        qr_layout = QVBoxLayout(self.qr_container)
        qr_layout.setAlignment(Qt.AlignCenter)
        
        self.qr_label = QLabel()
        self.qr_label.setAlignment(Qt.AlignCenter)
        self.qr_label.setFixedSize(300, 300)
        self.qr_label.setStyleSheet("background-color: white;")
        qr_layout.addWidget(self.qr_label)
        
        # Hiển thị loading spinner ban đầu
        self.qr_label.setText("⏳")
        self.qr_label.setStyleSheet("font-size: 80px; background-color: white;")
        
        layout.addWidget(self.qr_container, alignment=Qt.AlignCenter)
        
        # Instruction label
        self.instruction_label = QLabel("")
        self.instruction_label.setStyleSheet("font-size: 14px; color: #a8dadc;")
        self.instruction_label.setAlignment(Qt.AlignCenter)
        self.instruction_label.setWordWrap(True)
        layout.addWidget(self.instruction_label)
        
        # Close button (initially hidden)
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
        
        # Tạo QR code từ URL
        qr = qrcode.QRCode(version=1, box_size=10, border=2)
        qr.add_data(url)
        qr.make(fit=True)
        qr_img = qr.make_image(fill_color="black", back_color="white")
        
        # Convert PIL Image to QPixmap
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
    
    def closeEvent(self, event):
        """Cleanup khi đóng dialog."""
        if self.upload_thread and self.upload_thread.isRunning():
            self.upload_thread.wait()
        event.accept()


# ==========================================
# CAROUSEL PHOTO WIDGET
# ==========================================

class CarouselPhotoWidget(QWidget):
    """Widget hiển thị ảnh carousel trôi từ trái sang phải."""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.photos = []
        self.photo_labels = []
        self.current_offset = 0
        self.photo_width = 220
        self.photo_height = 280
        self.spacing = 20
        self.scroll_speed = 2  # pixels per frame
        
        self.setMinimumHeight(self.photo_height + 40)
        
        # Timer cho animation
        self.scroll_timer = QTimer()
        self.scroll_timer.timeout.connect(self.update_scroll)
        self.scroll_timer.start(30)  # ~33 FPS
        
    def set_photos(self, photo_paths):
        """Đặt danh sách ảnh cho carousel."""
        self.photos = photo_paths
        self.setup_photo_labels()
        
    def setup_photo_labels(self):
        """Tạo các label ảnh cho carousel."""
        # Xóa các label cũ
        for label in self.photo_labels:
            label.deleteLater()
        self.photo_labels = []
        
        if not self.photos:
            return
        
        # Nhân ảnh để tạo hiệu ứng vòng lặp liền mạch
        # Nhân 4 lần để đảm bảo đủ ảnh phủ kín màn hình và vòng lặp
        total_photos = self.photos * 4
        
        for i, photo_path in enumerate(total_photos):
            label = QLabel(self)
            label.setFixedSize(self.photo_width, self.photo_height)
            label.setAlignment(Qt.AlignCenter)
            label.setStyleSheet("""
                QLabel {
                    background: qlineargradient(x1:0, y1:0, x2:1, y2:1,
                        stop:0 #2d2d44, stop:1 #1a1a2e);
                    border: 3px solid #4361ee;
                    border-radius: 15px;
                    padding: 5px;
                }
            """)
            
            # Load và scale ảnh
            img = cv2.imread(photo_path)
            if img is not None:
                qt_img = convert_cv_qt(img)
                scaled = qt_img.scaled(
                    self.photo_width - 16, 
                    self.photo_height - 16, 
                    Qt.KeepAspectRatio, 
                    Qt.SmoothTransformation
                )
                label.setPixmap(scaled)
            
            label.show()
            self.photo_labels.append(label)
        
        self.update_positions()
    
    def update_positions(self):
        """Cập nhật vị trí các ảnh."""
        if not self.photo_labels:
            return
            
        y_pos = 20
        
        for i, label in enumerate(self.photo_labels):
            x_pos = i * (self.photo_width + self.spacing) - self.current_offset
            label.move(int(x_pos), y_pos)
    
    def update_scroll(self):
        """Cập nhật vị trí scroll."""
        if not self.photo_labels or not self.photos:
            return
        
        self.current_offset += self.scroll_speed
        
        # Reset offset khi đã cuộn qua 1 bộ ảnh gốc
        single_set_width = len(self.photos) * (self.photo_width + self.spacing)
        
        # Xử lý vòng lặp cho cả 2 chiều
        if self.current_offset >= single_set_width:
            self.current_offset -= single_set_width
        elif self.current_offset <= 0:
            self.current_offset += single_set_width
        
        self.update_positions()

# ==========================================
# GIAO DIỆN CHÍNH (MAIN GUI)
# ==========================================

class PhotoboothApp(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle(WINDOW_TITLE)
        self.resize(WINDOW_WIDTH, WINDOW_HEIGHT)
        
        # Stylesheet - Sử dụng font hỗ trợ tiếng Việt tốt
        self.setStyleSheet("""
            QMainWindow { background-color: #1a1a2e; }
            QLabel { 
                color: white; 
                font-family: 'Arial', 'Tahoma', 'Segoe UI', sans-serif;
                font-size: 18px;
            }
            QLabel#TitleLabel {
                font-size: 32px;
                font-weight: bold;
                color: #eaf0f6;
                font-family: 'Arial', 'Tahoma', sans-serif;
            }
            QLabel#SubTitleLabel {
                font-size: 24px;
                font-weight: bold;
                color: #ffd700;
                font-family: 'Arial', 'Tahoma', sans-serif;
            }
            QLabel#CountdownLabel {
                font-size: 120px;
                font-weight: bold;
                color: #ffd700;
            }
            QLabel#InfoLabel {
                font-size: 24px;
                color: #a8dadc;
                font-family: 'Arial', 'Tahoma', sans-serif;
            }
            QLabel#PriceLabel {
                font-size: 28px;
                font-weight: bold;
                color: #06d6a0;
                font-family: 'Arial', 'Tahoma', sans-serif;
            }
            QPushButton {
                background-color: #e94560;
                color: white;
                border: none;
                border-radius: 15px;
                padding: 20px 40px;
                font-size: 22px;
                font-weight: bold;
                font-family: 'Arial', 'Tahoma', sans-serif;
                min-height: 60px;
            }
            QPushButton:hover { background-color: #ff6b6b; }
            QPushButton:pressed { background-color: #c73e5a; }
            QPushButton:disabled { background-color: #4a4a6a; color: #8a8a9a; }
            QPushButton#GreenBtn { background-color: #06d6a0; }
            QPushButton#GreenBtn:hover { background-color: #00f5d4; }
            QPushButton#OrangeBtn { background-color: #fb8500; }
            QPushButton#OrangeBtn:hover { background-color: #ffb703; }
            QPushButton#BlueBtn { background-color: #4361ee; }
            QPushButton#BlueBtn:hover { background-color: #4cc9f0; }
            QPushButton#PriceBtn {
                background-color: #16213e;
                border: 4px solid #4361ee;
                border-radius: 25px;
                padding: 30px;
                min-height: 180px;
                min-width: 280px;
            }
            QPushButton#PriceBtn:hover { 
                background-color: #0f3460; 
                border-color: #e94560;
            }
            QPushButton#FrameBtn {
                background-color: #16213e;
                border: 3px solid #0f3460;
                border-radius: 20px;
                padding: 30px;
                min-height: 120px;
            }
            QPushButton#FrameBtn:hover { 
                background-color: #0f3460; 
                border-color: #e94560;
            }
            QPushButton#FrameBtn:checked { 
                background-color: #06d6a0; 
                border-color: #00f5d4;
            }
            QScrollArea { 
                border: none; 
                background-color: transparent; 
            }
            QWidget#PhotoCard {
                background-color: #16213e;
                border-radius: 10px;
                border: 2px solid #0f3460;
            }
            QWidget#PhotoCard:hover {
                border-color: #e94560;
            }
            QWidget#GalleryPanel {
                background-color: #0f0f23;
            }
            QWidget#StartPanel {
                background-color: #1a1a2e;
                border-left: 2px solid #4361ee;
            }
            QWidget#QRPanel {
                background-color: white;
                border-radius: 20px;
                padding: 20px;
            }
        """)

        # --- STATE MANAGEMENT ---
        self.state = "START"  # START, PRICE_SELECT, LAYOUT_SELECT, QR_PAYMENT, CAPTURING, PHOTO_SELECT, TEMPLATE_SELECT, CONFIRM, PRINTING
        self.captured_photos = []
        self.selected_frame_count = 0  # 2 hoặc 4
        self.selected_photo_indices = []
        self.collage_image = None
        self.merged_image = None
        self.current_frame = None
        self.countdown_val = 0
        self.selected_price_type = 0  # 2 hoặc 4
        self.payment_confirmed = False
        self.layout_type = ""  # "1x2", "2x1", "2x2", "4x1"
        
        # Thread references
        self.casso_thread = None
        self.qr_loader_thread = None
        self.current_transaction_code = ""
        self.current_amount = 0

        
        # Ảnh mẫu cho gallery
        self.gallery_photos = load_sample_photos()
        
        # --- CAMERA ---
        self.cap = cv2.VideoCapture(CAMERA_INDEX)
        self.cap.set(cv2.CAP_PROP_FRAME_WIDTH, 1280)
        self.cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 720)

        # --- MAIN LAYOUT ---
        self.central_widget = QWidget()
        self.setCentralWidget(self.central_widget)
        self.main_layout = QVBoxLayout(self.central_widget)
        self.main_layout.setContentsMargins(0, 0, 0, 0)
        self.main_layout.setSpacing(0)

        # --- STACKED WIDGET cho các màn hình ---
        self.stacked = QStackedWidget()
        self.main_layout.addWidget(self.stacked)

        # Tạo các màn hình
        self.create_welcome_screen()        # Index 0 - Màn hình welcome
        self.create_price_select_screen()   # Index 1 - Chọn giá tiền
        self.create_qr_payment_screen()     # Index 2 - Hiển thị QR
        self.create_capture_screen()        # Index 3 - Chụp ảnh
        self.create_layout_select_screen()  # Index 4 - Chọn kiểu bố cục
        self.create_photo_select_screen()   # Index 5 - Chọn ảnh
        self.create_template_select_screen() # Index 6 - Chọn khung
        self.create_confirm_screen()        # Index 7 - Xác nhận

        # --- TIMER ---
        self.camera_timer = QTimer()
        self.camera_timer.timeout.connect(self.update_camera_frame)
        self.camera_timer.start(30)

        self.countdown_timer = QTimer()
        self.countdown_timer.timeout.connect(self.countdown_tick)

        self.selection_timer = QTimer()
        self.selection_timer.timeout.connect(self.on_selection_timer_tick)
        self.selection_time_left = 0

        self.template_timer = QTimer()
        self.template_timer.timeout.connect(self.on_template_timer_tick)
        self.template_time_left = 0

        # Load templates
        self.templates = self.load_templates()

    # ==========================================
    # TẠO CÁC MÀN HÌNH
    # ==========================================

    def create_welcome_screen(self):
        """Màn hình welcome với carousel ảnh bên trái và nút bắt đầu bên phải."""
        screen = QWidget()
        main_layout = QHBoxLayout(screen)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)
        
        # ===== PHẦN TRÁI (2/3) - CAROUSEL ẢNH =====
        gallery_panel = QWidget()
        gallery_panel.setObjectName("GalleryPanel")
        gallery_layout = QVBoxLayout(gallery_panel)
        gallery_layout.setContentsMargins(20, 30, 20, 30)
        gallery_layout.setSpacing(15)
        
        # Title cho gallery
        gallery_title = QLabel("📸 NHỮNG KHOẢNH KHẮC ĐÁNG NHỚ")
        gallery_title.setObjectName("TitleLabel")
        gallery_title.setAlignment(Qt.AlignCenter)
        gallery_layout.addWidget(gallery_title)
        
        # Subtitle
        subtitle = QLabel("Những bức ảnh thành phẩm tuyệt đẹp từ Photobooth")
        subtitle.setObjectName("InfoLabel")
        subtitle.setAlignment(Qt.AlignCenter)
        subtitle.setStyleSheet("color: #a8dadc; font-size: 16px;")
        gallery_layout.addWidget(subtitle)
        
        # Carousel widget - Hàng 1
        self.carousel1 = CarouselPhotoWidget()
        self.carousel1.scroll_speed = 2
        gallery_layout.addWidget(self.carousel1)
        
        # Carousel widget - Hàng 2 (ngược chiều)
        self.carousel2 = CarouselPhotoWidget()
        self.carousel2.scroll_speed = -2  # Ngược chiều
        gallery_layout.addWidget(self.carousel2)
        
        # Thông tin bổ sung
        info_text = QLabel("✨ Tạo kỷ niệm tuyệt vời cùng chúng tôi! ✨")
        info_text.setAlignment(Qt.AlignCenter)
        info_text.setStyleSheet("color: #ffd700; font-size: 20px; font-weight: bold;")
        gallery_layout.addWidget(info_text)
        
        gallery_layout.addStretch()
        
        main_layout.addWidget(gallery_panel, stretch=2)
        
        # ===== PHẦN PHẢI (1/3) - NÚT BẮT ĐẦU =====
        start_panel = QWidget()
        start_panel.setObjectName("StartPanel")
        start_layout = QVBoxLayout(start_panel)
        start_layout.setContentsMargins(40, 60, 40, 60)
        start_layout.setSpacing(25)
        start_layout.setAlignment(Qt.AlignCenter)
        
        # Logo/Icon
        logo_label = QLabel("📷")
        logo_label.setStyleSheet("font-size: 80px;")
        logo_label.setAlignment(Qt.AlignCenter)
        start_layout.addWidget(logo_label)
        
        # Title
        title = QLabel("PHOTOBOOTH")
        title.setObjectName("TitleLabel")
        title.setAlignment(Qt.AlignCenter)
        start_layout.addWidget(title)
        
        # Subtitle
        welcome_text = QLabel("Chào mừng bạn!\nNhấn nút bên dưới để bắt đầu")
        welcome_text.setObjectName("InfoLabel")
        welcome_text.setAlignment(Qt.AlignCenter)
        welcome_text.setWordWrap(True)
        welcome_text.setStyleSheet("color: #a8dadc; font-size: 18px;")
        start_layout.addWidget(welcome_text)
        
        start_layout.addStretch()
        
        # Nút bắt đầu chụp
        self.btn_start_welcome = QPushButton("🎬 BẮT ĐẦU CHỤP")
        self.btn_start_welcome.setObjectName("GreenBtn")
        self.btn_start_welcome.setFixedSize(280, 90)
        self.btn_start_welcome.setStyleSheet("""
            QPushButton {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:1,
                    stop:0 #06d6a0, stop:1 #00f5d4);
                color: #1a1a2e;
                border: none;
                border-radius: 20px;
                padding: 20px 40px;
                font-size: 24px;
                font-weight: bold;
            }
            QPushButton:hover {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:1,
                    stop:0 #00f5d4, stop:1 #06d6a0);
            }
            QPushButton:pressed {
                background-color: #04a777;
            }
        """)
        self.btn_start_welcome.clicked.connect(self.go_to_price_select)
        start_layout.addWidget(self.btn_start_welcome, alignment=Qt.AlignCenter)
        
        start_layout.addStretch()
        
        # Info
        info_label = QLabel("💡 Chụp lên đến 10 ảnh\n🖼️ Chọn khung ảnh đẹp\n🖨️ In ngay tại chỗ")
        info_label.setAlignment(Qt.AlignCenter)
        info_label.setStyleSheet("color: #a8dadc; font-size: 14px;")
        start_layout.addWidget(info_label)
        
        main_layout.addWidget(start_panel, stretch=1)
        
        self.stacked.addWidget(screen)
        
        # Load ảnh cho carousel
        self.load_carousel_photos()

    def load_carousel_photos(self):
        """Load ảnh vào carousel."""
        if self.gallery_photos:
            # Chia ảnh thành 2 hàng
            half = len(self.gallery_photos) // 2
            self.carousel1.set_photos(self.gallery_photos[:max(half, 4)])
            self.carousel2.set_photos(self.gallery_photos[half:] if half > 0 else self.gallery_photos[:4])
        else:
            # Tạo ảnh mẫu nếu không có
            self.carousel1.set_photos([])
            self.carousel2.set_photos([])

    def create_price_select_screen(self):
        """Màn hình chọn kiểu lưới ảnh (4 options)."""
        screen = QWidget()
        layout = QVBoxLayout(screen)
        layout.setAlignment(Qt.AlignCenter)
        layout.setSpacing(30)
        layout.setContentsMargins(50, 30, 50, 30)
        
        # Title
        title = QLabel("�️ CHỌN KIỂU LƯỚI ẢNH")
        title.setObjectName("TitleLabel")
        title.setAlignment(Qt.AlignCenter)
        layout.addWidget(title)
        
        subtitle = QLabel("Chọn kiểu sắp xếp ảnh bạn muốn")
        subtitle.setObjectName("InfoLabel")
        subtitle.setAlignment(Qt.AlignCenter)
        layout.addWidget(subtitle)
        
        # Grid 2x2 for 4 options
        options_grid = QGridLayout()
        options_grid.setSpacing(30)
        options_grid.setAlignment(Qt.AlignCenter)
        
        # Common button style for 2-photo options
        btn_style_2photo = """
            QPushButton {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:1,
                    stop:0 #16213e, stop:1 #0f3460);
                border: 4px solid #4361ee;
                border-radius: 20px;
                padding: 20px;
                min-height: 150px;
                min-width: 250px;
                font-size: 18px;
                font-weight: bold;
                color: white;
            }
            QPushButton:hover { 
                background: qlineargradient(x1:0, y1:0, x2:1, y2:1,
                    stop:0 #0f3460, stop:1 #16213e);
                border-color: #06d6a0;
            }
        """
        
        # Common button style for 4-photo options
        btn_style_4photo = """
            QPushButton {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:1,
                    stop:0 #16213e, stop:1 #0f3460);
                border: 4px solid #e94560;
                border-radius: 20px;
                padding: 20px;
                min-height: 150px;
                min-width: 250px;
                font-size: 18px;
                font-weight: bold;
                color: white;
            }
            QPushButton:hover { 
                background: qlineargradient(x1:0, y1:0, x2:1, y2:1,
                    stop:0 #0f3460, stop:1 #16213e);
                border-color: #06d6a0;
            }
        """
        
        
        # === ROW 1: 2-PHOTO OPTIONS ===
        btn_2x1 = QPushButton(f"📷\n📷\n\n2 HÀNG x 1 CỘT\n(2 Ảnh - Dọc)\n\n{format_price(get_price_2())}")
        btn_2x1.setStyleSheet(btn_style_2photo)
        btn_2x1.clicked.connect(lambda: self.select_layout_and_price(2, "2x1"))
        options_grid.addWidget(btn_2x1, 0, 0)
        
        btn_1x2 = QPushButton(f"📷 📷\n\n1 HÀNG x 2 CỘT\n(2 Ảnh - Ngang)\n\n{format_price(get_price_2())}")
        btn_1x2.setStyleSheet(btn_style_2photo)
        btn_1x2.clicked.connect(lambda: self.select_layout_and_price(2, "1x2"))
        options_grid.addWidget(btn_1x2, 0, 1)
        
        # === ROW 2: 4-PHOTO OPTIONS ===
        btn_4x1 = QPushButton(f"📷\n📷\n📷\n📷\n\n4 HÀNG x 1 CỘT\n(4 Ảnh - Dọc)\n\n{format_price(get_price_4())}")
        btn_4x1.setStyleSheet(btn_style_4photo)
        btn_4x1.clicked.connect(lambda: self.select_layout_and_price(4, "4x1"))
        options_grid.addWidget(btn_4x1, 1, 0)
        
        btn_2x2 = QPushButton(f"📷 📷\n📷 📷\n\n2 HÀNG x 2 CỘT\n(4 Ảnh - Lưới)\n\n{format_price(get_price_4())}")
        btn_2x2.setStyleSheet(btn_style_4photo)
        btn_2x2.clicked.connect(lambda: self.select_layout_and_price(4, "2x2"))
        options_grid.addWidget(btn_2x2, 1, 1)
        
        layout.addLayout(options_grid)
        
        # Back button
        self.btn_back_price = QPushButton("⬅️ QUAY LẠI")
        self.btn_back_price.setObjectName("OrangeBtn")
        self.btn_back_price.setFixedSize(200, 60)
        self.btn_back_price.clicked.connect(self.reset_all)
        layout.addWidget(self.btn_back_price, alignment=Qt.AlignCenter)
        
        self.stacked.addWidget(screen)

    def create_layout_select_screen(self):
        """Màn hình chọn kiểu bố cục ảnh."""
        screen = QWidget()
        layout = QVBoxLayout(screen)
        layout.setAlignment(Qt.AlignCenter)
        layout.setSpacing(40)
        layout.setContentsMargins(50, 50, 50, 50)
        
        # Title
        self.layout_title = QLabel("🖼️ CHỌN KIỂU BỐ CỤC")
        self.layout_title.setObjectName("TitleLabel")
        self.layout_title.setAlignment(Qt.AlignCenter)
        layout.addWidget(self.layout_title)
        
        self.layout_subtitle = QLabel("Đã chụp xong! Hãy chọn cách sắp xếp ảnh của bạn")
        self.layout_subtitle.setObjectName("InfoLabel")
        self.layout_subtitle.setAlignment(Qt.AlignCenter)
        layout.addWidget(self.layout_subtitle)
        
        # Container cho các lựa chọn bố cục
        self.layout_options_widget = QWidget()
        self.layout_options_layout = QHBoxLayout(self.layout_options_widget)
        self.layout_options_layout.setSpacing(60)
        self.layout_options_layout.setAlignment(Qt.AlignCenter)
        layout.addWidget(self.layout_options_widget)
        
        # Không có nút quay lại vì đã chụp ảnh xong
        
        self.stacked.addWidget(screen)

    def create_qr_payment_screen(self):
        """Màn hình hiển thị mã QR thanh toán VietQR với kiểm tra Casso tự động."""
        screen = QWidget()
        layout = QVBoxLayout(screen)
        layout.setAlignment(Qt.AlignCenter)
        layout.setSpacing(20)
        layout.setContentsMargins(50, 30, 50, 30)
        
        # Title
        title = QLabel("📱 QUÉT MÃ ĐỂ THANH TOÁN")
        title.setObjectName("TitleLabel")
        title.setAlignment(Qt.AlignCenter)
        layout.addWidget(title)
        
        # Thông tin gói đã chọn
        self.selected_package_label = QLabel()
        self.selected_package_label.setObjectName("SubTitleLabel")
        self.selected_package_label.setAlignment(Qt.AlignCenter)
        layout.addWidget(self.selected_package_label)
        
        # Mã giao dịch
        self.transaction_code_label = QLabel()
        self.transaction_code_label.setAlignment(Qt.AlignCenter)
        self.transaction_code_label.setStyleSheet("font-size: 20px; color: #ffd700; font-weight: bold;")
        layout.addWidget(self.transaction_code_label)
        
        # QR container
        qr_container = QWidget()
        qr_container.setStyleSheet("background-color: white; border-radius: 25px;")
        qr_container.setFixedSize(380, 380)
        qr_layout = QVBoxLayout(qr_container)
        qr_layout.setAlignment(Qt.AlignCenter)
        
        self.qr_label = QLabel("⏳ Đang tải...")
        self.qr_label.setAlignment(Qt.AlignCenter)
        self.qr_label.setFixedSize(350, 350)
        self.qr_label.setStyleSheet("font-size: 24px; color: #333; background-color: white;")
        qr_layout.addWidget(self.qr_label)
        layout.addWidget(qr_container, alignment=Qt.AlignCenter)
        
        # Thông tin tài khoản
        self.bank_info_label = QLabel()
        self.bank_info_label.setAlignment(Qt.AlignCenter)
        self.bank_info_label.setStyleSheet("font-size: 16px; color: #a8dadc;")
        layout.addWidget(self.bank_info_label)
        
        # Trạng thái kiểm tra Casso
        self.payment_status_label = QLabel("🔄 Đang chờ thanh toán...")
        self.payment_status_label.setAlignment(Qt.AlignCenter)
        self.payment_status_label.setStyleSheet("font-size: 18px; color: #ffd700;")
        layout.addWidget(self.payment_status_label)
        
        # Buttons
        btn_layout = QHBoxLayout()
        btn_layout.setSpacing(30)
        
        self.btn_back_qr = QPushButton("⬅️ HỦY VÀ QUAY LẠI")
        self.btn_back_qr.setObjectName("OrangeBtn")
        self.btn_back_qr.setFixedSize(250, 60)
        self.btn_back_qr.clicked.connect(self.cancel_payment_and_go_back)
        btn_layout.addWidget(self.btn_back_qr)
        
        layout.addLayout(btn_layout)
        
        self.stacked.addWidget(screen)

    def create_capture_screen(self):
        """Màn hình chụp ảnh với camera live."""
        screen = QWidget()
        layout = QVBoxLayout(screen)
        layout.setSpacing(10)
        layout.setContentsMargins(20, 20, 20, 20)

        # Camera view
        self.camera_label = QLabel("Đang khởi động camera...")
        self.camera_label.setAlignment(Qt.AlignCenter)
        self.camera_label.setStyleSheet("""
            background-color: #000; 
            border: 4px solid #e94560; 
            border-radius: 15px;
        """)
        self.camera_label.setMinimumSize(900, 500)
        layout.addWidget(self.camera_label, stretch=4)

        # Info bar
        info_widget = QWidget()
        info_layout = QHBoxLayout(info_widget)
        
        self.photo_count_label = QLabel("Ảnh: 0/10")
        self.photo_count_label.setObjectName("InfoLabel")
        info_layout.addWidget(self.photo_count_label)
        
        self.countdown_label = QLabel("")
        self.countdown_label.setObjectName("CountdownLabel")
        self.countdown_label.setAlignment(Qt.AlignCenter)
        info_layout.addWidget(self.countdown_label, stretch=1)
        
        # Start Capture Button (Hidden initially)
        self.btn_capture_start = QPushButton("📸 BẮT ĐẦU CHỤP")
        self.btn_capture_start.setObjectName("GreenBtn")
        self.btn_capture_start.setFixedSize(200, 60)
        self.btn_capture_start.hide()
        self.btn_capture_start.clicked.connect(self.start_capture_session)
        # Add to layout but we might want it centered or overlay. 
        # Putting it in the info layout for simplicity or above status.
        # Let's put it in the main layout under the camera image for better visibility
        
        self.status_label = QLabel("Chuẩn bị...")
        self.status_label.setObjectName("InfoLabel")
        self.status_label.setAlignment(Qt.AlignRight)
        info_layout.addWidget(self.status_label)
        
        layout.addWidget(self.btn_capture_start, alignment=Qt.AlignCenter)
        layout.addWidget(info_widget)

        self.stacked.addWidget(screen)

    def create_photo_select_screen(self):
        """Màn hình chọn ảnh từ 10 ảnh đã chụp."""
        screen = QWidget()
        layout = QVBoxLayout(screen)
        layout.setSpacing(15)
        layout.setContentsMargins(20, 20, 20, 20)

        self.photo_select_title = QLabel("CHỌN ẢNH")
        self.photo_select_title.setObjectName("TitleLabel")
        self.photo_select_title.setAlignment(Qt.AlignCenter)
        layout.addWidget(self.photo_select_title)

        # Timer Label
        self.lbl_selection_timer = QLabel("Thời gian còn lại: 00:00")
        self.lbl_selection_timer.setAlignment(Qt.AlignCenter)
        self.lbl_selection_timer.setStyleSheet("font-size: 24px; color: #ffd700; font-weight: bold;")
        layout.addWidget(self.lbl_selection_timer)

        # Scroll area for photo grid
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setStyleSheet("background-color: transparent;")
        
        self.photo_grid_widget = QWidget()
        self.photo_grid_layout = QGridLayout(self.photo_grid_widget)
        self.photo_grid_layout.setSpacing(15)
        scroll.setWidget(self.photo_grid_widget)
        layout.addWidget(scroll, stretch=1)

        self.btn_confirm_photos = QPushButton("XÁC NHẬN CHỌN ẢNH")
        self.btn_confirm_photos.setObjectName("GreenBtn")
        self.btn_confirm_photos.setEnabled(False)
        self.btn_confirm_photos.clicked.connect(self.confirm_photo_selection)
        layout.addWidget(self.btn_confirm_photos, alignment=Qt.AlignCenter)

        self.stacked.addWidget(screen)



    def create_template_select_screen(self):
        """Màn hình chọn template/khung viền - 2/3 trái preview, 1/3 phải templates + nút."""
        screen = QWidget()
        main_layout = QHBoxLayout(screen)
        main_layout.setContentsMargins(20, 20, 20, 20)
        main_layout.setSpacing(20)

        # ===== LEFT COLUMN (2/3) - ẢNH THÀNH QUẢ =====
        left_container = QWidget()
        left_container.setStyleSheet("background-color: #0f0f23; border-radius: 15px;")
        left_layout = QVBoxLayout(left_container)
        left_layout.setContentsMargins(15, 15, 15, 15)
        left_layout.setSpacing(10)
        
        # Title for preview
        preview_title = QLabel("📸 ẢNH THÀNH QUẢ")
        preview_title.setAlignment(Qt.AlignCenter)
        preview_title.setStyleSheet("font-size: 24px; font-weight: bold; color: #ffd700;")
        left_layout.addWidget(preview_title)

        # Preview (Large)
        self.template_preview_label = QLabel()
        self.template_preview_label.setAlignment(Qt.AlignCenter)
        self.template_preview_label.setStyleSheet("""
            background-color: #000;
            border: 4px solid #4361ee;
            border-radius: 15px;
        """)
        left_layout.addWidget(self.template_preview_label, stretch=1)

        main_layout.addWidget(left_container, stretch=2)

        # ===== RIGHT COLUMN (1/3) - KHUNG + NÚT =====
        right_container = QWidget()
        right_container.setStyleSheet("background-color: #1a1a2e; border-radius: 15px;")
        right_layout = QVBoxLayout(right_container)
        right_layout.setContentsMargins(15, 15, 15, 15)
        right_layout.setSpacing(15)

        # Title
        title = QLabel("🖼️ CHỌN KHUNG VIỀN")
        title.setObjectName("TitleLabel")
        title.setAlignment(Qt.AlignCenter)
        title.setWordWrap(True)
        right_layout.addWidget(title)

        # Timer
        self.lbl_template_timer = QLabel("Thời gian còn lại: 00:00")
        self.lbl_template_timer.setAlignment(Qt.AlignCenter)
        self.lbl_template_timer.setStyleSheet("font-size: 20px; color: #ffd700; font-weight: bold;")
        right_layout.addWidget(self.lbl_template_timer)
        
        # Template options (Vertical scroll)
        template_group = QGroupBox("CÁC MẪU KHUNG")
        template_group.setStyleSheet("""
            QGroupBox { 
                color: #a8dadc; 
                font-weight: bold; 
                border: 2px solid #4361ee; 
                border-radius: 10px; 
                margin-top: 15px;
                padding-top: 10px;
            } 
            QGroupBox::title { 
                subcontrol-origin: margin; 
                left: 10px; 
                padding: 0 10px; 
            }
        """)
        group_layout = QVBoxLayout(template_group)
        
        template_scroll = QScrollArea()
        template_scroll.setWidgetResizable(True)
        template_scroll.setVerticalScrollBarPolicy(Qt.ScrollBarAsNeeded)
        template_scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        template_scroll.setStyleSheet("background-color: transparent; border: none;")
        template_scroll.setMinimumHeight(250)
        
        self.template_btn_widget = QWidget()
        self.template_btn_layout = QGridLayout(self.template_btn_widget)
        self.template_btn_layout.setSpacing(10)
        template_scroll.setWidget(self.template_btn_widget)
        
        group_layout.addWidget(template_scroll)
        right_layout.addWidget(template_group, stretch=1)

        # Buttons at bottom
        self.btn_no_template = QPushButton("KHÔNG DÙNG KHUNG")
        self.btn_no_template.setObjectName("OrangeBtn")
        self.btn_no_template.setFixedSize(280, 50)
        self.btn_no_template.clicked.connect(self.use_no_template)
        right_layout.addWidget(self.btn_no_template, alignment=Qt.AlignCenter)
        
        self.btn_confirm_template = QPushButton("✅ ĐỒNG Ý - IN ẢNH")
        self.btn_confirm_template.setObjectName("GreenBtn")
        self.btn_confirm_template.setFixedSize(280, 80)
        self.btn_confirm_template.setStyleSheet("""
             QPushButton#GreenBtn {
                font-size: 24px;
                font-weight: bold;
             }
        """)
        self.btn_confirm_template.clicked.connect(self.accept_and_print)
        right_layout.addWidget(self.btn_confirm_template, alignment=Qt.AlignCenter)

        main_layout.addWidget(right_container, stretch=1)

        self.stacked.addWidget(screen)

    def create_confirm_screen(self):
        """Màn hình xác nhận cuối cùng trước khi in."""
        screen = QWidget()
        layout = QVBoxLayout(screen)
        layout.setAlignment(Qt.AlignCenter)
        layout.setSpacing(20)
        layout.setContentsMargins(20, 20, 20, 20)

        title = QLabel("BẠN CÓ ĐỒNG Ý VỚI MẪU NÀY KHÔNG?")
        title.setObjectName("TitleLabel")
        title.setAlignment(Qt.AlignCenter)
        layout.addWidget(title)

        # Final preview
        self.final_preview_label = QLabel()
        self.final_preview_label.setAlignment(Qt.AlignCenter)
        self.final_preview_label.setStyleSheet("""
            background-color: #000;
            border: 4px solid #06d6a0;
            border-radius: 15px;
        """)
        self.final_preview_label.setMinimumSize(800, 450)
        layout.addWidget(self.final_preview_label)

        # Buttons
        btn_layout = QHBoxLayout()
        btn_layout.setSpacing(30)
        
        # Đã bỏ nút "Chụp lại từ đầu" theo yêu cầu
        
        self.btn_accept = QPushButton("ĐỒNG Ý - IN ẢNH")
        self.btn_accept.setObjectName("GreenBtn")
        self.btn_accept.setFixedSize(300, 80)
        self.btn_accept.clicked.connect(self.accept_and_print)
        btn_layout.addWidget(self.btn_accept)
        
        layout.addLayout(btn_layout)

        self.stacked.addWidget(screen)

    # ==========================================
    # LOGIC ĐIỀU KHIỂN
    # ==========================================

    def go_to_price_select(self):
        """Chuyển sang màn hình chọn giá tiền."""
        self.state = "PRICE_SELECT"
        self.stacked.setCurrentIndex(1)

    def select_price(self, photo_count):
        """Xử lý khi chọn gói giá tiền."""
        self.selected_price_type = photo_count
        self.selected_frame_count = photo_count
        
        # Cập nhật thông tin trên màn hình QR
        if photo_count == 2:
            self.selected_package_label.setText(f"📦 GÓI 2 ẢNH - {PRICE_2_PHOTOS}")
            qr_amount = "20000"
        else:
            self.selected_package_label.setText(f"📦 GÓI 4 ẢNH - {PRICE_4_PHOTOS}")
            qr_amount = "35000"
        
        # Tạo QR code
        qr_content = f"https://momosv3.apimienphi.com/api/QRCode?phone=0123456789&amount={qr_amount}&note=Photobooth{photo_count}Anh"
        qr_pixmap = generate_qr_code(qr_content, 300)
        self.qr_label.setPixmap(qr_pixmap)
        
        # Chuyển sang màn hình QR
        self.state = "QR_PAYMENT"
        self.stacked.setCurrentIndex(2)
    
    def select_layout_and_price(self, photo_count, layout_type):
        """Xử lý khi chọn kiểu lưới (kết hợp chọn giá và layout)."""
        self.selected_price_type = photo_count
        self.selected_frame_count = photo_count
        self.layout_type = layout_type
        
        # Cập nhật thông tin trên màn hình QR
        if photo_count == 2:
            layout_name = "2 Hàng x 1 Cột" if layout_type == "2x1" else "1 Hàng x 2 Cột"
            self.selected_package_label.setText(f"📦 {layout_name} - 2 ẢNH - {PRICE_2_PHOTOS}")
            qr_amount = "20000"
        else:
            layout_name = "4 Hàng x 1 Cột" if layout_type == "4x1" else "2 Hàng x 2 Cột"
            self.selected_package_label.setText(f"📦 {layout_name} - 4 ẢNH - {PRICE_4_PHOTOS}")
            qr_amount = "35000"
        
        # Tạo QR code
        qr_content = f"https://momosv3.apimienphi.com/api/QRCode?phone=0123456789&amount={qr_amount}&note=Photobooth{photo_count}Anh"
        qr_pixmap = generate_qr_code(qr_content, 300)
        self.qr_label.setPixmap(qr_pixmap)
        
        # Chuyển sang màn hình QR
        self.state = "QR_PAYMENT"
        self.stacked.setCurrentIndex(2)
    
    def go_to_layout_select(self):
        """Chuyển sang màn hình chọn bố cục."""
        self.state = "LAYOUT_SELECT"
        
        # Xóa các nút cũ
        for i in reversed(range(self.layout_options_layout.count())):
            widget = self.layout_options_layout.itemAt(i).widget()
            if widget:
                widget.deleteLater()
        
        # Tạo các nút bố cục dựa trên số ảnh đã chọn
        if self.selected_frame_count == 2:
            self.layout_title.setText("🖼️ CHỌN KIỂU LƯỚI ẢNH CHO 2 ẢNH")
            
            # Option 1: 2 hàng 1 cột (dọc)
            btn_2x1 = QPushButton("📷\n📷\n\n2 HÀNG x 1 CỘT\n(Dọc)")
            btn_2x1.setStyleSheet("""
                QPushButton {
                    background: qlineargradient(x1:0, y1:0, x2:1, y2:1,
                        stop:0 #16213e, stop:1 #0f3460);
                    border: 4px solid #e94560;
                    border-radius: 25px;
                    padding: 30px;
                    min-height: 200px;
                    min-width: 300px;
                    font-size: 24px;
                    font-weight: bold;
                    color: white;
                }
                QPushButton:hover { 
                    background: qlineargradient(x1:0, y1:0, x2:1, y2:1,
                        stop:0 #0f3460, stop:1 #16213e);
                    border-color: #06d6a0;
                }
            """)
            btn_2x1.clicked.connect(lambda: self.select_layout("2x1"))
            self.layout_options_layout.addWidget(btn_2x1)
            
            # Option 2: 1 hàng 2 cột (ngang)
            btn_1x2 = QPushButton("📷 📷\n\n1 HÀNG x 2 CỘT\n(Ngang)")
            btn_1x2.setStyleSheet("""
                QPushButton {
                    background: qlineargradient(x1:0, y1:0, x2:1, y2:1,
                        stop:0 #16213e, stop:1 #0f3460);
                    border: 4px solid #4361ee;
                    border-radius: 25px;
                    padding: 30px;
                    min-height: 200px;
                    min-width: 300px;
                    font-size: 24px;
                    font-weight: bold;
                    color: white;
                }
                QPushButton:hover { 
                    background: qlineargradient(x1:0, y1:0, x2:1, y2:1,
                        stop:0 #0f3460, stop:1 #16213e);
                    border-color: #06d6a0;
                }
            """)
            btn_1x2.clicked.connect(lambda: self.select_layout("1x2"))
            self.layout_options_layout.addWidget(btn_1x2)
            
        elif self.selected_frame_count == 4:
            self.layout_title.setText("🖼️ CHỌN KIỂU LƯỚI ẢNH CHO 4 ẢNH")
            
            # Option 1: 4 hàng 1 cột (dọc dài)
            btn_4x1 = QPushButton("📷\n📷\n📷\n📷\n\n4 HÀNG x 1 CỘT\n(Dọc dài)")
            btn_4x1.setStyleSheet("""
                QPushButton {
                    background: qlineargradient(x1:0, y1:0, x2:1, y2:1,
                        stop:0 #16213e, stop:1 #0f3460);
                    border: 4px solid #e94560;
                    border-radius: 25px;
                    padding: 30px;
                    min-height: 200px;
                    min-width: 300px;
                    font-size: 24px;
                    font-weight: bold;
                    color: white;
                }
                QPushButton:hover { 
                    background: qlineargradient(x1:0, y1:0, x2:1, y2:1,
                        stop:0 #0f3460, stop:1 #16213e);
                    border-color: #06d6a0;
                }
            """)
            btn_4x1.clicked.connect(lambda: self.select_layout("4x1"))
            self.layout_options_layout.addWidget(btn_4x1)
            
            # Option 2: 2 hàng 2 cột (lưới vuông)
            btn_2x2 = QPushButton("📷 📷\n📷 📷\n\n2 HÀNG x 2 CỘT\n(Lưới vuông)")
            btn_2x2.setStyleSheet("""
                QPushButton {
                    background: qlineargradient(x1:0, y1:0, x2:1, y2:1,
                        stop:0 #16213e, stop:1 #0f3460);
                    border: 4px solid #4361ee;
                    border-radius: 25px;
                    padding: 30px;
                    min-height: 200px;
                    min-width: 300px;
                    font-size: 24px;
                    font-weight: bold;
                    color: white;
                }
                QPushButton:hover { 
                    background: qlineargradient(x1:0, y1:0, x2:1, y2:1,
                        stop:0 #0f3460, stop:1 #16213e);
                    border-color: #06d6a0;
                }
            """)
            btn_2x2.clicked.connect(lambda: self.select_layout("2x2"))
            self.layout_options_layout.addWidget(btn_2x2)
        
        self.stacked.setCurrentIndex(4)
    
    def select_layout(self, layout_type):
        """Xử lý khi chọn kiểu bố cục."""
        self.layout_type = layout_type
        
        # Validate selection
        if not self.selected_photo_indices or len(self.selected_photo_indices) != self.selected_frame_count:
            # Fallback (should not happen normally)
            needed = self.selected_frame_count
            self.selected_photo_indices = list(range(min(needed, len(self.captured_photos))))
            
        # Tạo collage ngay sau khi chọn layout
        selected_imgs = [self.captured_photos[i] for i in sorted(self.selected_photo_indices)]
        
        # Ensure we have images
        if not selected_imgs:
             QMessageBox.warning(self, "Lỗi", "Không có ảnh nào được chọn!")
             return

        self.collage_image = self.create_collage(selected_imgs)
        self.merged_image = self.collage_image.copy()
        
        # Chuyển sang màn hình chọn template
        self.go_to_template_select()

    def confirm_payment(self):
        """Xác nhận đã thanh toán và chuyển sang màn hình chờ chụp."""
        self.payment_confirmed = True
        self.prepare_capture_wait()

    def prepare_capture_wait(self):
        """Chuẩn bị màn hình chờ chụp."""
        self.state = "WAITING_CAPTURE"
        self.captured_photos = []
        self.selected_photo_indices = []
        
        # Chuyển sang màn hình chụp
        self.stacked.setCurrentIndex(3)
        
        # Reset UI
        self.photo_count_label.setText(f"Ảnh: 0/{PHOTOS_TO_TAKE}")
        self.status_label.setText("Sẵn sàng?")
        self.countdown_label.setText("")
        
        # Hiện nút bắt đầu
        self.btn_capture_start.show()

    def load_templates(self):
        """Load danh sách templates dựa trên kiểu bố cục đã chọn."""
        templates = []
        # Xác định thư mục template dựa trên bố cục
        layout_folder = f"{self.selected_frame_count}_{self.layout_type}"
        layout_template_dir = os.path.join(TEMPLATE_DIR, layout_folder)
        
        if os.path.exists(layout_template_dir):
            for f in os.listdir(layout_template_dir):
                if f.lower().endswith('.png'):
                    templates.append(os.path.join(layout_template_dir, f))
        
        # Nếu không có template trong thư mục cụ thể, load từ thư mục chung
        if not templates and os.path.exists(TEMPLATE_DIR):
            for f in os.listdir(TEMPLATE_DIR):
                if f.lower().endswith('.png') and os.path.isfile(os.path.join(TEMPLATE_DIR, f)):
                    templates.append(os.path.join(TEMPLATE_DIR, f))
        
        return templates

    def update_camera_frame(self):
        """Cập nhật frame từ camera."""
        if self.state == "CAPTURING":
            ret, frame = self.cap.read()
            if ret:
                frame = cv2.flip(frame, 1)
                self.current_frame = frame.copy()
                
                # Hiển thị lên camera label
                qt_img = convert_cv_qt(frame)
                scaled = qt_img.scaled(self.camera_label.size(), Qt.KeepAspectRatio, Qt.SmoothTransformation)
                self.camera_label.setPixmap(scaled)
        elif self.state == "WAITING_CAPTURE":
            # Cũng hiển thị camera khi đang chờ
            ret, frame = self.cap.read()
            if ret:
                frame = cv2.flip(frame, 1)
                qt_img = convert_cv_qt(frame)
                scaled = qt_img.scaled(self.camera_label.size(), Qt.KeepAspectRatio, Qt.SmoothTransformation)
                self.camera_label.setPixmap(scaled)

    def start_capture_session(self):
        """Bắt đầu phiên chụp ảnh (đếm ngược)."""
        self.state = "CAPTURING"
        self.btn_capture_start.hide()
        
        # Bắt đầu đếm ngược cho ảnh đầu tiên (10 giây)
        self.countdown_val = FIRST_PHOTO_DELAY
        self.photo_count_label.setText(f"Ảnh: 0/{PHOTOS_TO_TAKE}")
        self.status_label.setText("Chuẩn bị tạo dáng!")
        self.countdown_label.setText(str(self.countdown_val))
        
        self.countdown_timer.start(1000)

    def countdown_tick(self):
        """Xử lý mỗi giây đếm ngược."""
        self.countdown_val -= 1
        
        if self.countdown_val > 0:
            self.countdown_label.setText(str(self.countdown_val))
        else:
            # Chụp ảnh!
            self.countdown_label.setText("📸")
            self.capture_photo()

    def capture_photo(self):
        """Chụp một ảnh."""
        if self.current_frame is not None:
            self.captured_photos.append(self.current_frame.copy())
            photo_num = len(self.captured_photos)
            self.photo_count_label.setText(f"Ảnh: {photo_num}/{PHOTOS_TO_TAKE}")
            
            if photo_num < PHOTOS_TO_TAKE:
                # Còn ảnh cần chụp, đặt countdown 7 giây
                self.countdown_val = BETWEEN_PHOTO_DELAY
                self.countdown_label.setText(str(self.countdown_val))
                self.status_label.setText(f"Đã chụp ảnh {photo_num}! Tiếp tục...")
            else:
                # Đã chụp đủ 10 ảnh
                self.countdown_timer.stop()
                self.countdown_label.setText("✓")
                self.status_label.setText("Hoàn thành!")
                
                # Chuyển sang màn hình chọn ảnh (Flow mới: Chụp -> Chọn ảnh -> Chọn Layout)
                QTimer.singleShot(1000, self.go_to_photo_select)

    def go_to_photo_select(self):
        """Chuyển sang màn hình chọn ảnh."""
        self.state = "PHOTO_SELECT"
        self.selected_photo_indices = []
        
        # Cập nhật title dựa trên gói đã chọn
        self.photo_select_title.setText(f"CHỌN {self.selected_frame_count} ẢNH CHO KHUNG {self.selected_frame_count} ẢNH")
        
        # --- CONFIG TIMER ---
        if self.selected_frame_count == 2:
            self.selection_time_left = 60  # 1 phút
        else:
            self.selection_time_left = 120 # 2 phút
        
        self.update_timer_label()
        self.selection_timer.start(1000)
        
        # Clear grid cũ
        for i in reversed(range(self.photo_grid_layout.count())):
            widget = self.photo_grid_layout.itemAt(i).widget()
            if widget:
                widget.deleteLater()
        
        # Tạo grid ảnh (2 hàng x 5 cột) - Kích thước lớn cho màn hình 15.6"
        self.photo_buttons = []
        
        # Kích thước lớn cho ảnh thumb - tỷ lệ 16:9 để khớp với camera
        # Card: 230x160, Button: 210x118 (16:9)
        card_w, card_h = 230, 160
        btn_w, btn_h = 210, 118
        
        for idx, img in enumerate(self.captured_photos):
            container = QWidget()
            container.setObjectName("PhotoCard")
            container.setFixedSize(card_w, card_h)
            
            layout = QVBoxLayout(container)
            layout.setContentsMargins(8, 8, 8, 8)
            layout.setSpacing(3)
            
            btn = QPushButton()
            btn.setCheckable(True)
            btn.setFixedSize(btn_w, btn_h)
            
            thumb = cv2.resize(img, (btn_w, btn_h))
            btn.setIcon(QIcon(convert_cv_qt(thumb)))
            btn.setIconSize(QSize(btn_w, btn_h))
            # Button style is minimal as container handles border
            btn.setStyleSheet("border: none; border-radius: 5px;")
            # Pass container to be styled
            btn.clicked.connect(lambda checked, i=idx, c=container, b=btn: self.toggle_photo(i, c, b))
            
            layout.addWidget(btn)
            
            lbl = QLabel(f"Ảnh {idx + 1}")
            lbl.setAlignment(Qt.AlignCenter)
            lbl.setStyleSheet("font-size: 14px; font-weight: bold;")
            layout.addWidget(lbl)
            
            # 5 Columns grid (2 rows x 5 cols)
            row = idx // 5
            col = idx % 5
            self.photo_grid_layout.addWidget(container, row, col)
            self.photo_buttons.append(btn)
        
        self.btn_confirm_photos.setEnabled(False)
        self.stacked.setCurrentIndex(5)
    
    def on_selection_timer_tick(self):
        """Xử lý đếm ngược thời gian chọn ảnh."""
        self.selection_time_left -= 1
        self.update_timer_label()
        
        if self.selection_time_left <= 0:
            self.selection_timer.stop()
            # Hết giờ -> Tự động chọn nếu chưa đủ
            self.auto_confirm_selection()

    def update_timer_label(self):
        """Cập nhật label hiển thị thời gian."""
        minutes = self.selection_time_left // 60
        seconds = self.selection_time_left % 60
        self.lbl_selection_timer.setText(f"Thời gian còn lại: {minutes:02d}:{seconds:02d}")
        if self.selection_time_left < 10:
             self.lbl_selection_timer.setStyleSheet("font-size: 24px; color: #ff6b6b; font-weight: bold;")
        else:
             self.lbl_selection_timer.setStyleSheet("font-size: 24px; color: #ffd700; font-weight: bold;")

    def auto_confirm_selection(self):
        """Tự động chọn ảnh khi hết giờ."""
        QMessageBox.warning(self, "Hết giờ", "Đã hết thời gian chọn ảnh! Hệ thống sẽ tự động chọn ảnh cho bạn.")
        
        # Nếu chưa chọn đủ, chọn tự động các ảnh đầu tiên chưa được chọn
        if len(self.selected_photo_indices) < self.selected_frame_count:
            needed = self.selected_frame_count - len(self.selected_photo_indices)
            for i in range(len(self.captured_photos)):
                if needed <= 0:
                    break
                if i not in self.selected_photo_indices:
                    self.selected_photo_indices.append(i)
                    needs -= 1
        
        # Nếu chọn thừa (hiếm khi xảy ra do logic check), cắt bớt
        if len(self.selected_photo_indices) > self.selected_frame_count:
             self.selected_photo_indices = self.selected_photo_indices[:self.selected_frame_count]

        self.confirm_photo_selection()

    def toggle_photo(self, index, container, button):
        """Xử lý chọn/bỏ chọn ảnh."""
        if index in self.selected_photo_indices:
            self.selected_photo_indices.remove(index)
            # Reset container border
            container.setStyleSheet("""
                QWidget#PhotoCard {
                    background-color: #16213e;
                    border: 2px solid #0f3460;
                    border-radius: 10px;
                }
            """)
            button.setChecked(False) # Ensure button state matches
        else:
            if len(self.selected_photo_indices) >= self.selected_frame_count:
                # Đã chọn đủ, bỏ chọn ảnh này
                button.setChecked(False)
                QMessageBox.information(self, "Thông báo", 
                    f"Bạn chỉ được chọn {self.selected_frame_count} ảnh!")
                return
            
            self.selected_photo_indices.append(index)
            # Set Highlight border (Yellow)
            container.setStyleSheet("""
                QWidget#PhotoCard {
                    background-color: #16213e;
                    border: 5px solid #ffd700;
                    border-radius: 10px;
                }
            """)
            button.setChecked(True)
        
        # Enable/disable confirm button
        self.btn_confirm_photos.setEnabled(
            len(self.selected_photo_indices) == self.selected_frame_count
        )

    def confirm_photo_selection(self):
        """Xác nhận chọn ảnh và tạo collage."""
        # Stop timer
        self.selection_timer.stop()
        
        # Tạo collage (layout đã được chọn ở bước chọn giá)
        selected_imgs = [self.captured_photos[i] for i in sorted(self.selected_photo_indices)]
        
        if not selected_imgs:
            QMessageBox.warning(self, "Lỗi", "Không có ảnh nào được chọn!")
            return
        
        self.collage_image = self.create_collage(selected_imgs)
        self.merged_image = self.collage_image.copy()
        
        # Chuyển sang màn hình chọn template
        self.go_to_template_select()

    def create_collage(self, images):
        """Tạo collage từ các ảnh đã chọn dựa trên kiểu bố cục với padding."""
        count = len(images)
        
        # Padding xung quanh các ảnh để khung có thể mở rộng hơn
        PADDING = 40  # pixels padding xung quanh
        GAP = 10      # khoảng cách giữa các ảnh
        
        if count == 0:
            return np.zeros((720, 1280, 3), dtype=np.uint8)

        if count == 2:
            if self.layout_type == "1x2":
                # 2 ảnh: 1 hàng 2 cột (ngang) - canvas 1280x720
                canvas_w, canvas_h = 1280, 720
                canvas = np.zeros((canvas_h, canvas_w, 3), dtype=np.uint8)
                
                # Tính kích thước ảnh sau khi trừ padding
                available_w = canvas_w - 2 * PADDING - GAP
                available_h = canvas_h - 2 * PADDING
                img_w = available_w // 2
                img_h = available_h
                
                for i, img in enumerate(images):
                    cropped = self.crop_to_aspect(img, img_w, img_h)
                    resized = cv2.resize(cropped, (img_w, img_h))
                    x = PADDING + i * (img_w + GAP)
                    y = PADDING
                    canvas[y:y+img_h, x:x+img_w] = resized
                    
            elif self.layout_type == "2x1":
                # 2 ảnh: 2 hàng 1 cột (dọc)
                canvas_w, canvas_h = 640, 900
                canvas = np.zeros((canvas_h, canvas_w, 3), dtype=np.uint8)
                
                available_w = canvas_w - 2 * PADDING
                available_h = canvas_h - 2 * PADDING - GAP
                img_w = available_w
                img_h = available_h // 2
                
                for i, img in enumerate(images):
                    cropped = self.crop_to_aspect(img, img_w, img_h)
                    resized = cv2.resize(cropped, (img_w, img_h))
                    x = PADDING
                    y = PADDING + i * (img_h + GAP)
                    canvas[y:y+img_h, x:x+img_w] = resized
            else:
                # Default 1x2
                canvas_w, canvas_h = 1280, 720
                canvas = np.zeros((canvas_h, canvas_w, 3), dtype=np.uint8)
                available_w = canvas_w - 2 * PADDING - GAP
                available_h = canvas_h - 2 * PADDING
                img_w = available_w // 2
                img_h = available_h
                for i, img in enumerate(images):
                    cropped = self.crop_to_aspect(img, img_w, img_h)
                    resized = cv2.resize(cropped, (img_w, img_h))
                    x = PADDING + i * (img_w + GAP)
                    y = PADDING
                    canvas[y:y+img_h, x:x+img_w] = resized
                    
        elif count == 4:
            if self.layout_type == "2x2":
                # 4 ảnh: 2 hàng 2 cột (lưới vuông) - canvas 1280x720
                canvas_w, canvas_h = 1280, 720
                canvas = np.zeros((canvas_h, canvas_w, 3), dtype=np.uint8)
                
                available_w = canvas_w - 2 * PADDING - GAP
                available_h = canvas_h - 2 * PADDING - GAP
                img_w = available_w // 2
                img_h = available_h // 2
                
                for i, img in enumerate(images):
                    cropped = self.crop_to_aspect(img, img_w, img_h)
                    resized = cv2.resize(cropped, (img_w, img_h))
                    row = i // 2
                    col = i % 2
                    x = PADDING + col * (img_w + GAP)
                    y = PADDING + row * (img_h + GAP)
                    canvas[y:y+img_h, x:x+img_w] = resized
                    
            elif self.layout_type == "4x1":
                # 4 ảnh: 4 hàng 1 cột (dọc dài)
                canvas_w, canvas_h = 640, 1600
                canvas = np.zeros((canvas_h, canvas_w, 3), dtype=np.uint8)
                
                available_w = canvas_w - 2 * PADDING
                available_h = canvas_h - 2 * PADDING - 3 * GAP
                img_w = available_w
                img_h = available_h // 4
                
                for i, img in enumerate(images):
                    cropped = self.crop_to_aspect(img, img_w, img_h)
                    resized = cv2.resize(cropped, (img_w, img_h))
                    x = PADDING
                    y = PADDING + i * (img_h + GAP)
                    canvas[y:y+img_h, x:x+img_w] = resized
            else:
                # Default 2x2
                canvas_w, canvas_h = 1280, 720
                canvas = np.zeros((canvas_h, canvas_w, 3), dtype=np.uint8)
                available_w = canvas_w - 2 * PADDING - GAP
                available_h = canvas_h - 2 * PADDING - GAP
                img_w = available_w // 2
                img_h = available_h // 2
                for i, img in enumerate(images):
                    cropped = self.crop_to_aspect(img, img_w, img_h)
                    resized = cv2.resize(cropped, (img_w, img_h))
                    row = i // 2
                    col = i % 2
                    x = PADDING + col * (img_w + GAP)
                    y = PADDING + row * (img_h + GAP)
                    canvas[y:y+img_h, x:x+img_w] = resized
        
        return canvas

    def crop_to_aspect(self, img, target_w, target_h):
        """Crop ảnh về đúng tỷ lệ trước khi resize để tránh méo."""
        if img is None: return np.zeros((target_h, target_w, 3), np.uint8)
        
        h, w = img.shape[:2]
        target_ratio = target_w / target_h
        current_ratio = w / h
        
        if current_ratio > target_ratio:
            # Ảnh quá rộng -> Crop 2 bên
            new_w = int(h * target_ratio)
            start_x = (w - new_w) // 2
            return img[:, start_x:start_x+new_w]
        else:
            # Ảnh quá cao -> Crop trên dưới
            new_h = int(w / target_ratio)
            start_y = (h - new_h) // 2
            return img[start_y:start_y+new_h, :]



    def go_to_template_select(self):
        """Chuyển sang màn hình chọn template."""
        self.state = "TEMPLATE_SELECT"
        
        # Reload templates dựa trên bố cục đã chọn
        self.templates = self.load_templates()
        
        # Hiển thị preview ban đầu
        self.update_template_preview()
        
        # Populate template buttons in grid (2 columns)
        for i in reversed(range(self.template_btn_layout.count())):
            widget = self.template_btn_layout.itemAt(i).widget()
            if widget:
                widget.deleteLater()
        
        for idx, path in enumerate(self.templates):
            btn = QPushButton()
            btn.setFixedSize(130, 100)
            pix = QPixmap(path).scaled(110, 85, Qt.KeepAspectRatio, Qt.SmoothTransformation)
            btn.setIcon(QIcon(pix))
            btn.setIconSize(QSize(110, 85))
            btn.setStyleSheet("""
                QPushButton {
                    background-color: #16213e; 
                    border: 2px solid #0f3460;
                    border-radius: 8px;
                }
                QPushButton:hover {
                    border-color: #ffd700;
                }
            """)
            btn.clicked.connect(lambda checked, p=path: self.apply_template(p))
            # 2 columns grid
            row = idx // 2
            col = idx % 2
            self.template_btn_layout.addWidget(btn, row, col)
        
        self.stacked.setCurrentIndex(6)
        
        # Start timer 60s
        self.template_time_left = 60
        self.update_template_timer_label()
        self.template_timer.start(1000)

    def on_template_timer_tick(self):
        """Xử lý đếm ngược thời gian chọn template."""
        self.template_time_left -= 1
        self.update_template_timer_label()
        
        if self.template_time_left <= 0:
            self.template_timer.stop()
            # Hết giờ -> Tự động in
            QMessageBox.information(self, "Hết giờ", "Đã hết thời gian! Hệ thống sẽ tự động in ảnh.")
            self.accept_and_print()

    def update_template_timer_label(self):
        """Cập nhật label hiển thị thời gian chọn template."""
        minutes = self.template_time_left // 60
        seconds = self.template_time_left % 60
        self.lbl_template_timer.setText(f"Thời gian còn lại: {minutes:02d}:{seconds:02d}")
        if self.template_time_left < 10:
             self.lbl_template_timer.setStyleSheet("font-size: 24px; color: #ff6b6b; font-weight: bold;")
        else:
             self.lbl_template_timer.setStyleSheet("font-size: 24px; color: #ffd700; font-weight: bold;")

    def update_template_preview(self):
        """Cập nhật preview."""
        if self.merged_image is not None:
            qt_img = convert_cv_qt(self.merged_image)
            # Sử dụng kích thước cố định để tránh preview phóng to dần
            max_w, max_h = 800, 600
            scaled = qt_img.scaled(
                max_w, max_h, 
                Qt.KeepAspectRatio, 
                Qt.SmoothTransformation
            )
            self.template_preview_label.setPixmap(scaled)

    def apply_template(self, template_path):
        """Áp dụng template lên collage."""
        template = cv2.imread(template_path, cv2.IMREAD_UNCHANGED)
        if template is not None and self.collage_image is not None:
            self.merged_image = overlay_images(self.collage_image.copy(), template)
            self.update_template_preview()

    def use_no_template(self):
        """Không sử dụng template."""
        self.merged_image = self.collage_image.copy()
        # In luôn
        self.accept_and_print()

    def go_to_confirm(self):
        """Chuyển sang màn hình xác nhận."""
        self.state = "CONFIRM"
        
        # Hiển thị preview cuối
        if self.merged_image is not None:
            qt_img = convert_cv_qt(self.merged_image)
            scaled = qt_img.scaled(
                self.final_preview_label.size(), 
                Qt.KeepAspectRatio, 
                Qt.SmoothTransformation
            )
            self.final_preview_label.setPixmap(scaled)
        
        self.stacked.setCurrentIndex(7)

    def accept_and_print(self):
        """Đồng ý và lưu ảnh, sau đó hiển thị QR để khách tải về."""
        # Stop timer
        self.template_timer.stop()
        
        if self.merged_image is None:
            return
        
        # Tạo thư mục D:\picture nếu chưa có
        output_folder = r"D:\picture"
        os.makedirs(output_folder, exist_ok=True)
        
        # Lưu file
        timestamp = time.strftime("%Y%m%d-%H%M%S")
        filename = f"photo_{timestamp}.jpg"
        filepath = os.path.join(output_folder, filename)
        
        try:
            cv2.imwrite(filepath, self.merged_image)
            
            # Cập nhật carousel với ảnh mới
            self.gallery_photos = load_sample_photos()
            self.load_carousel_photos()
            
            # Hiển thị Dialog với QR code để khách tải ảnh
            dialog = DownloadQRDialog(filepath, self)
            dialog.exec_()  # Chờ khách đóng dialog
            
            # Sau khi khách đóng dialog, reset về màn hình đầu
            self.reset_all()
            
        except Exception as e:
            QMessageBox.critical(
                self,
                "❌ LỖI LƯU ẢNH",
                f"Không thể lưu ảnh: {str(e)}"
            )

    def reset_all(self):
        """Reset toàn bộ về trạng thái ban đầu."""
        self.state = "START"
        self.captured_photos = []
        self.selected_photo_indices = []
        self.selected_frame_count = 0
        self.collage_image = None
        self.merged_image = None
        self.payment_confirmed = False
        self.selected_price_type = 0
        self.layout_type = ""

        
        # Về màn hình bắt đầu
        self.stacked.setCurrentIndex(0)
    
    # ==========================================
    # LOGIC THANH TOÁN CASSO
    # ==========================================
    
    def select_layout_and_price(self, photo_count, layout_type):
        """Xử lý khi chọn gói (layout + giá) - Hiển thị QR và bắt đầu check Casso."""
        self.selected_price_type = photo_count
        self.selected_frame_count = photo_count
        self.layout_type = layout_type
        
        # Tạo mã giao dịch duy nhất
        self.current_transaction_code = generate_unique_code()
        self.current_amount = get_price_2() if photo_count == 2 else get_price_4()
        
        # Cập nhật UI
        layout_name = {
            "2x1": "2 Hàng x 1 Cột", "1x2": "1 Hàng x 2 Cột",
            "4x1": "4 Hàng x 1 Cột", "2x2": "2 Hàng x 2 Cột"
        }.get(layout_type, layout_type)
        
        self.selected_package_label.setText(f"📦 {layout_name} - {photo_count} ẢNH - {format_price(self.current_amount)}")
        self.transaction_code_label.setText(f"Nội dung CK: {self.current_transaction_code}")
        self.bank_info_label.setText(f"{APP_CONFIG.get('bank_name', '')} - {APP_CONFIG.get('bank_account', '')}")
        self.payment_status_label.setText("🔄 Đang chờ thanh toán...")
        self.payment_status_label.setStyleSheet("font-size: 18px; color: #ffd700;")
        
        # Tải QR Image từ VietQR (async)
        self.qr_label.setText("⏳ Đang tải mã QR...")
        qr_url = generate_vietqr_url(self.current_amount, self.current_transaction_code)
        self.qr_loader_thread = QRImageLoaderThread(qr_url)
        self.qr_loader_thread.image_loaded.connect(self.on_qr_image_loaded)
        self.qr_loader_thread.load_error.connect(self.on_qr_load_error)
        self.qr_loader_thread.start()
        
        # Bắt đầu kiểm tra Casso
        self.start_casso_check()
        
        self.state = "QR_PAYMENT"
        self.stacked.setCurrentIndex(2)
    
    def on_qr_image_loaded(self, pixmap):
        """Khi tải xong ảnh QR từ VietQR."""
        scaled = pixmap.scaled(350, 350, Qt.KeepAspectRatio, Qt.SmoothTransformation)
        self.qr_label.setPixmap(scaled)
    
    def on_qr_load_error(self, error):
        """Khi lỗi tải QR, fallback sang QR tự tạo."""
        self.qr_label.setText(f"❌ Lỗi tải QR\n{error[:30]}...")
        # Fallback: tạo QR từ thông tin
        content = f"{APP_CONFIG.get('bank_account', '')} - {self.current_amount} - {self.current_transaction_code}"
        pixmap = generate_qr_code(content, 300)
        self.qr_label.setPixmap(pixmap)
    
    def start_casso_check(self):
        """Bắt đầu thread kiểm tra thanh toán Casso."""
        if hasattr(self, 'casso_thread') and self.casso_thread and self.casso_thread.isRunning():
            self.casso_thread.stop()
            self.casso_thread.wait()
        
        self.casso_thread = CassoCheckThread(self.current_amount, self.current_transaction_code)
        self.casso_thread.payment_received.connect(self.on_payment_received)
        self.casso_thread.check_error.connect(self.on_casso_error)
        self.casso_thread.start()
    
    def on_payment_received(self):
        """Khi nhận được thanh toán thành công từ Casso."""
        self.payment_status_label.setText("✅ ĐÃ NHẬN THANH TOÁN!")
        self.payment_status_label.setStyleSheet("font-size: 24px; color: #06d6a0; font-weight: bold;")
        
        # Dừng casso thread
        if self.casso_thread and self.casso_thread.isRunning():
            self.casso_thread.stop()
        
        # Chuyển sang màn hình chụp ảnh sau 1.5 giây
        QTimer.singleShot(1500, self.go_to_capture_screen)
    
    def on_casso_error(self, error):
        """Xử lý lỗi Casso."""
        self.payment_status_label.setText(f"⚠️ Lỗi: {error[:50]}...")
        self.payment_status_label.setStyleSheet("font-size: 16px; color: #ff6b6b;")
    
    def cancel_payment_and_go_back(self):
        """Hủy thanh toán và quay lại chọn gói."""
        if hasattr(self, 'casso_thread') and self.casso_thread and self.casso_thread.isRunning():
            self.casso_thread.stop()
            self.casso_thread.wait()
        if hasattr(self, 'qr_loader_thread') and self.qr_loader_thread and self.qr_loader_thread.isRunning():
            self.qr_loader_thread.wait()
        
        self.stacked.setCurrentIndex(1)  # Quay lại price select
    
    def go_to_capture_screen(self):
        """Chuyển sang màn hình chụp ảnh."""
        self.state = "WAITING_CAPTURE"
        self.captured_photos = []
        self.selected_photo_indices = []
        self.stacked.setCurrentIndex(3)
        self.photo_count_label.setText(f"Ảnh: 0/{PHOTOS_TO_TAKE}")
        self.status_label.setText("Sẵn sàng?")
        self.countdown_label.setText("")
        self.btn_capture_start.show()


    def closeEvent(self, event):
        """Cleanup khi đóng app."""
        self.camera_timer.stop()
        self.countdown_timer.stop()
        self.selection_timer.stop()
        self.template_timer.stop()
        if hasattr(self, 'carousel1'):
            self.carousel1.scroll_timer.stop()
        if hasattr(self, 'carousel2'):
            self.carousel2.scroll_timer.stop()
        
        # Dừng Casso thread nếu đang chạy
        if hasattr(self, 'casso_thread') and self.casso_thread and self.casso_thread.isRunning():
            self.casso_thread.stop()
            self.casso_thread.wait()
        
        self.cap.release()
        event.accept()




if __name__ == "__main__":
    # Kiểm tra config.json
    if not load_config():
        app = QApplication(sys.argv)
        QMessageBox.critical(
            None,
            "❌ Thiếu cấu hình",
            "Không tìm thấy file config.json!\n\n"
            "Vui lòng chạy setup_admin.py trước để tạo cấu hình."
        )
        sys.exit(1)
    
    ensure_directories()
    app = QApplication(sys.argv)
    
    # Set font mặc định - sử dụng font hỗ trợ tiếng Việt
    font = QFont("Arial", 12)
    font.setStyleHint(QFont.SansSerif)
    app.setFont(font)
    
    window = PhotoboothApp()
    window.show()
    sys.exit(app.exec_())

