import sys
import os
import cv2
import time
import subprocess
import numpy as np
import qrcode
from io import BytesIO
from PIL import Image
from PyQt5.QtWidgets import (QApplication, QMainWindow, QWidget, QLabel, 
                             QPushButton, QVBoxLayout, QHBoxLayout, QScrollArea, 
                             QMessageBox, QFrame, QGridLayout, QStackedWidget,
                             QGraphicsOpacityEffect)
from PyQt5.QtCore import Qt, QTimer, QSize, QPropertyAnimation, QPoint, QEasingCurve, QSequentialAnimationGroup, QParallelAnimationGroup
from PyQt5.QtGui import QImage, QPixmap, QFont, QIcon

# ==========================================
# CẤU HÌNH (CONFIGURATION)
# ==========================================
WINDOW_TITLE = "Photobooth Cảm Ứng"
WINDOW_WIDTH = 1200
WINDOW_HEIGHT = 800
CAMERA_INDEX = 0
FIRST_PHOTO_DELAY = 10  # Giây cho ảnh đầu tiên
BETWEEN_PHOTO_DELAY = 7  # Giây giữa các ảnh
PHOTOS_TO_TAKE = 10
TEMPLATE_DIR = "templates"
OUTPUT_DIR = "output"
SAMPLE_PHOTOS_DIR = "sample_photos"

# Cấu hình giá tiền
PRICE_2_PHOTOS = "20.000 VNĐ"
PRICE_4_PHOTOS = "35.000 VNĐ"

# Thông tin thanh toán (ví dụ: số tài khoản, momo, etc.)
PAYMENT_INFO = "MOMO: 0123456789 - NGUYEN VAN A"
QR_CONTENT = "https://momosv3.apimienphi.com/api/QRCode?phone=0123456789&amount=20000&note=ThanhToanPhotobooth"

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
        
        # Nhân đôi ảnh để tạo hiệu ứng vòng lặp liền mạch
        total_photos = self.photos * 3  # Nhân 3 lần để có đủ ảnh cho vòng lặp
        
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
        total_width = len(self.photo_labels) * (self.photo_width + self.spacing)
        
        for i, label in enumerate(self.photo_labels):
            x_pos = i * (self.photo_width + self.spacing) - self.current_offset
            label.move(int(x_pos), y_pos)
    
    def update_scroll(self):
        """Cập nhật vị trí scroll."""
        if not self.photo_labels or not self.photos:
            return
        
        self.current_offset += self.scroll_speed
        
        # Reset offset khi đã cuộn qua 1 bộ ảnh
        single_set_width = len(self.photos) * (self.photo_width + self.spacing)
        if self.current_offset >= single_set_width:
            self.current_offset = 0
        
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
        self.state = "START"  # START, PRICE_SELECT, QR_PAYMENT, CAPTURING, PHOTO_SELECT, TEMPLATE_SELECT, CONFIRM, PRINTING
        self.captured_photos = []
        self.selected_frame_count = 0  # 2 hoặc 4
        self.selected_photo_indices = []
        self.collage_image = None
        self.merged_image = None
        self.current_frame = None
        self.countdown_val = 0
        self.selected_price_type = 0  # 2 hoặc 4
        self.payment_confirmed = False
        
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

        # Tạo các màn hình (bỏ màn hình chọn kiểu khung)
        self.create_welcome_screen()      # Index 0 - Màn hình welcome mới
        self.create_price_select_screen() # Index 1 - Chọn giá tiền
        self.create_qr_payment_screen()   # Index 2 - Hiển thị QR
        self.create_capture_screen()      # Index 3
        self.create_photo_select_screen() # Index 4
        self.create_template_select_screen() # Index 5
        self.create_confirm_screen()      # Index 6

        # --- TIMER ---
        self.camera_timer = QTimer()
        self.camera_timer.timeout.connect(self.update_camera_frame)
        self.camera_timer.start(30)

        self.countdown_timer = QTimer()
        self.countdown_timer.timeout.connect(self.countdown_tick)

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
        """Màn hình chọn giá tiền (2 ảnh hoặc 4 ảnh)."""
        screen = QWidget()
        layout = QVBoxLayout(screen)
        layout.setAlignment(Qt.AlignCenter)
        layout.setSpacing(40)
        layout.setContentsMargins(50, 50, 50, 50)
        
        # Title
        title = QLabel("💳 CHỌN GÓI CHỤP ẢNH")
        title.setObjectName("TitleLabel")
        title.setAlignment(Qt.AlignCenter)
        layout.addWidget(title)
        
        subtitle = QLabel("Hãy chọn gói phù hợp với bạn")
        subtitle.setObjectName("InfoLabel")
        subtitle.setAlignment(Qt.AlignCenter)
        layout.addWidget(subtitle)
        
        # Price options
        options_layout = QHBoxLayout()
        options_layout.setSpacing(60)
        options_layout.setAlignment(Qt.AlignCenter)
        
        # Option 1: 2 ảnh
        self.btn_price_2 = QPushButton(f"🖼️🖼️\n\n2 ẢNH\n\n{PRICE_2_PHOTOS}")
        self.btn_price_2.setStyleSheet("""
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
        self.btn_price_2.clicked.connect(lambda: self.select_price(2))
        options_layout.addWidget(self.btn_price_2)
        
        # Option 2: 4 ảnh
        self.btn_price_4 = QPushButton(f"🖼️🖼️\n🖼️🖼️\n\n4 ẢNH\n\n{PRICE_4_PHOTOS}")
        self.btn_price_4.setStyleSheet("""
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
        self.btn_price_4.clicked.connect(lambda: self.select_price(4))
        options_layout.addWidget(self.btn_price_4)
        
        layout.addLayout(options_layout)
        
        # Back button
        self.btn_back_price = QPushButton("⬅️ QUAY LẠI")
        self.btn_back_price.setObjectName("OrangeBtn")
        self.btn_back_price.setFixedSize(200, 60)
        self.btn_back_price.clicked.connect(self.reset_all)
        layout.addWidget(self.btn_back_price, alignment=Qt.AlignCenter)
        
        self.stacked.addWidget(screen)

    def create_qr_payment_screen(self):
        """Màn hình hiển thị mã QR để thanh toán."""
        screen = QWidget()
        layout = QVBoxLayout(screen)
        layout.setAlignment(Qt.AlignCenter)
        layout.setSpacing(30)
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
        
        # QR Code container
        qr_container = QWidget()
        qr_container.setStyleSheet("""
            background-color: white;
            border-radius: 25px;
            padding: 30px;
        """)
        qr_container.setFixedSize(400, 400)
        qr_layout = QVBoxLayout(qr_container)
        qr_layout.setAlignment(Qt.AlignCenter)
        
        self.qr_label = QLabel()
        self.qr_label.setAlignment(Qt.AlignCenter)
        self.qr_label.setFixedSize(320, 320)
        qr_layout.addWidget(self.qr_label)
        
        layout.addWidget(qr_container, alignment=Qt.AlignCenter)
        
        # Payment info
        payment_info_label = QLabel(PAYMENT_INFO)
        payment_info_label.setObjectName("InfoLabel")
        payment_info_label.setAlignment(Qt.AlignCenter)
        payment_info_label.setStyleSheet("color: #ffd700; font-size: 20px;")
        layout.addWidget(payment_info_label)
        
        # Hướng dẫn
        instruction = QLabel("Sau khi thanh toán, nhấn nút bên dưới để tiếp tục")
        instruction.setAlignment(Qt.AlignCenter)
        instruction.setStyleSheet("color: #a8dadc; font-size: 18px;")
        layout.addWidget(instruction)
        
        # Buttons
        btn_layout = QHBoxLayout()
        btn_layout.setSpacing(30)
        
        self.btn_back_qr = QPushButton("⬅️ QUAY LẠI")
        self.btn_back_qr.setObjectName("OrangeBtn")
        self.btn_back_qr.setFixedSize(200, 70)
        self.btn_back_qr.clicked.connect(self.go_to_price_select)
        btn_layout.addWidget(self.btn_back_qr)
        
        self.btn_payment_done = QPushButton("✅ ĐÃ THANH TOÁN")
        self.btn_payment_done.setObjectName("GreenBtn")
        self.btn_payment_done.setFixedSize(300, 70)
        self.btn_payment_done.setStyleSheet("""
            QPushButton {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:1,
                    stop:0 #06d6a0, stop:1 #00f5d4);
                color: #1a1a2e;
                border: none;
                border-radius: 15px;
                padding: 20px 40px;
                font-size: 24px;
                font-weight: bold;
            }
            QPushButton:hover {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:1,
                    stop:0 #00f5d4, stop:1 #06d6a0);
            }
        """)
        self.btn_payment_done.clicked.connect(self.confirm_payment)
        btn_layout.addWidget(self.btn_payment_done)
        
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
        
        self.status_label = QLabel("Chuẩn bị...")
        self.status_label.setObjectName("InfoLabel")
        self.status_label.setAlignment(Qt.AlignRight)
        info_layout.addWidget(self.status_label)
        
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

        # Scroll area for photo grid
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setStyleSheet("background-color: transparent;")
        
        self.photo_grid_widget = QWidget()
        self.photo_grid_layout = QGridLayout(self.photo_grid_widget)
        self.photo_grid_layout.setSpacing(15)
        scroll.setWidget(self.photo_grid_widget)
        layout.addWidget(scroll, stretch=1)

        # Confirm button
        self.btn_confirm_photos = QPushButton("XÁC NHẬN CHỌN ẢNH")
        self.btn_confirm_photos.setObjectName("GreenBtn")
        self.btn_confirm_photos.setEnabled(False)
        self.btn_confirm_photos.clicked.connect(self.confirm_photo_selection)
        layout.addWidget(self.btn_confirm_photos, alignment=Qt.AlignCenter)

        self.stacked.addWidget(screen)

    def create_template_select_screen(self):
        """Màn hình chọn template/khung viền."""
        screen = QWidget()
        layout = QVBoxLayout(screen)
        layout.setSpacing(15)
        layout.setContentsMargins(20, 20, 20, 20)

        title = QLabel("CHỌN KHUNG VIỀN")
        title.setObjectName("TitleLabel")
        title.setAlignment(Qt.AlignCenter)
        layout.addWidget(title)

        # Preview
        self.template_preview_label = QLabel()
        self.template_preview_label.setAlignment(Qt.AlignCenter)
        self.template_preview_label.setStyleSheet("""
            background-color: #000;
            border: 3px solid #4361ee;
            border-radius: 10px;
        """)
        self.template_preview_label.setMinimumSize(700, 400)
        layout.addWidget(self.template_preview_label, stretch=1)

        # Template options (horizontal scroll)
        template_scroll = QScrollArea()
        template_scroll.setWidgetResizable(True)
        template_scroll.setFixedHeight(150)
        template_scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOn)
        
        self.template_btn_widget = QWidget()
        self.template_btn_layout = QHBoxLayout(self.template_btn_widget)
        template_scroll.setWidget(self.template_btn_widget)
        layout.addWidget(template_scroll)

        # Buttons
        btn_layout = QHBoxLayout()
        
        self.btn_no_template = QPushButton("KHÔNG DÙNG KHUNG")
        self.btn_no_template.setObjectName("OrangeBtn")
        self.btn_no_template.clicked.connect(self.use_no_template)
        btn_layout.addWidget(self.btn_no_template)
        
        self.btn_confirm_template = QPushButton("XÁC NHẬN")
        self.btn_confirm_template.setObjectName("GreenBtn")
        self.btn_confirm_template.clicked.connect(self.go_to_confirm)
        btn_layout.addWidget(self.btn_confirm_template)
        
        layout.addLayout(btn_layout)

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
        
        self.btn_reject = QPushButton("CHỤP LẠI TỪ ĐẦU")
        self.btn_reject.setObjectName("OrangeBtn")
        self.btn_reject.setFixedSize(300, 80)
        self.btn_reject.clicked.connect(self.reset_all)
        btn_layout.addWidget(self.btn_reject)
        
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

    def confirm_payment(self):
        """Xác nhận đã thanh toán và bắt đầu chụp ảnh."""
        self.payment_confirmed = True
        self.start_capture_session()

    def load_templates(self):
        """Load danh sách templates."""
        templates = []
        if os.path.exists(TEMPLATE_DIR):
            for f in os.listdir(TEMPLATE_DIR):
                if f.lower().endswith('.png'):
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

    def start_capture_session(self):
        """Bắt đầu phiên chụp ảnh."""
        self.state = "CAPTURING"
        self.captured_photos = []
        self.selected_photo_indices = []
        
        # Chuyển sang màn hình chụp
        self.stacked.setCurrentIndex(3)
        
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
                
                # Chuyển thẳng sang chọn ảnh (bỏ qua chọn kiểu khung vì đã chọn trước)
                QTimer.singleShot(1000, self.go_to_photo_select)

    def go_to_photo_select(self):
        """Chuyển sang màn hình chọn ảnh."""
        self.state = "PHOTO_SELECT"
        self.selected_photo_indices = []
        
        # Cập nhật title dựa trên gói đã chọn
        self.photo_select_title.setText(f"CHỌN {self.selected_frame_count} ẢNH CHO KHUNG {self.selected_frame_count} ẢNH")
        
        # Clear grid cũ
        for i in reversed(range(self.photo_grid_layout.count())):
            self.photo_grid_layout.itemAt(i).widget().deleteLater()
        
        # Tạo grid ảnh (2 hàng x 5 cột)
        self.photo_buttons = []
        for idx, img in enumerate(self.captured_photos):
            container = QWidget()
            container.setObjectName("PhotoCard")
            container.setFixedSize(200, 150)
            
            layout = QVBoxLayout(container)
            layout.setContentsMargins(5, 5, 5, 5)
            layout.setSpacing(5)
            
            btn = QPushButton()
            btn.setCheckable(True)
            btn.setFixedSize(180, 100)
            
            thumb = cv2.resize(img, (180, 100))
            btn.setIcon(QIcon(convert_cv_qt(thumb)))
            btn.setIconSize(QSize(180, 100))
            btn.setStyleSheet("border: 2px solid transparent; border-radius: 5px;")
            btn.clicked.connect(lambda checked, i=idx, b=btn: self.toggle_photo(i, b))
            
            layout.addWidget(btn)
            
            lbl = QLabel(f"Ảnh {idx + 1}")
            lbl.setAlignment(Qt.AlignCenter)
            lbl.setStyleSheet("font-size: 14px;")
            layout.addWidget(lbl)
            
            row = idx // 5
            col = idx % 5
            self.photo_grid_layout.addWidget(container, row, col)
            self.photo_buttons.append(btn)
        
        self.btn_confirm_photos.setEnabled(False)
        self.stacked.setCurrentIndex(4)

    def toggle_photo(self, index, button):
        """Xử lý chọn/bỏ chọn ảnh."""
        if index in self.selected_photo_indices:
            self.selected_photo_indices.remove(index)
            button.setStyleSheet("border: 2px solid transparent; border-radius: 5px;")
        else:
            if len(self.selected_photo_indices) >= self.selected_frame_count:
                # Đã chọn đủ, bỏ chọn ảnh này
                button.setChecked(False)
                QMessageBox.information(self, "Thông báo", 
                    f"Bạn chỉ được chọn {self.selected_frame_count} ảnh!")
                return
            
            self.selected_photo_indices.append(index)
            button.setStyleSheet("border: 4px solid #06d6a0; border-radius: 5px;")
        
        # Enable/disable confirm button
        self.btn_confirm_photos.setEnabled(
            len(self.selected_photo_indices) == self.selected_frame_count
        )

    def confirm_photo_selection(self):
        """Xác nhận chọn ảnh và tạo collage."""
        selected_imgs = [self.captured_photos[i] for i in sorted(self.selected_photo_indices)]
        self.collage_image = self.create_collage(selected_imgs)
        self.merged_image = self.collage_image.copy()
        
        self.go_to_template_select()

    def create_collage(self, images):
        """Tạo collage từ các ảnh đã chọn (chỉ 2 hoặc 4 ảnh)."""
        canvas = np.zeros((720, 1280, 3), dtype=np.uint8)
        count = len(images)
        
        if count == 2:
            # 2 ảnh: đặt cạnh nhau
            for i, img in enumerate(images):
                h, w = img.shape[:2]
                center_x = w // 2
                start_x = max(0, center_x - 320)
                end_x = min(w, start_x + 640)
                cropped = img[0:min(h, 720), start_x:end_x]
                cropped = cv2.resize(cropped, (640, 720))
                canvas[0:720, i*640:(i+1)*640] = cropped
        elif count == 4:
            # 4 ảnh: 2x2 grid
            for i, img in enumerate(images):
                resized = cv2.resize(img, (640, 360))
                row = i // 2
                col = i % 2
                canvas[row*360:(row+1)*360, col*640:(col+1)*640] = resized
        
        return canvas

    def go_to_template_select(self):
        """Chuyển sang màn hình chọn template."""
        self.state = "TEMPLATE_SELECT"
        
        # Hiển thị preview ban đầu
        self.update_template_preview()
        
        # Populate template buttons
        for i in reversed(range(self.template_btn_layout.count())):
            self.template_btn_layout.itemAt(i).widget().deleteLater()
        
        for path in self.templates:
            btn = QPushButton()
            btn.setFixedSize(120, 100)
            pix = QPixmap(path).scaled(100, 80, Qt.KeepAspectRatio, Qt.SmoothTransformation)
            btn.setIcon(QIcon(pix))
            btn.setIconSize(QSize(100, 80))
            btn.setStyleSheet("""
                background-color: #16213e; 
                border: 2px solid #0f3460;
                border-radius: 10px;
            """)
            btn.clicked.connect(lambda checked, p=path: self.apply_template(p))
            self.template_btn_layout.addWidget(btn)
        
        self.stacked.setCurrentIndex(5)

    def update_template_preview(self):
        """Cập nhật preview."""
        if self.merged_image is not None:
            qt_img = convert_cv_qt(self.merged_image)
            scaled = qt_img.scaled(
                self.template_preview_label.size(), 
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
        self.go_to_confirm()

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
        
        self.stacked.setCurrentIndex(6)

    def accept_and_print(self):
        """Đồng ý và tiến hành in ảnh."""
        if self.merged_image is None:
            return
        
        # Kiểm tra máy in
        printer_ok, printer_info = check_printer_available()
        
        if not printer_ok:
            QMessageBox.warning(
                self, 
                "⚠️ MÁY IN CHƯA ĐƯỢC KẾT NỐI",
                f"Không thể in ảnh!\n\nLý do: {printer_info}\n\n"
                "Vui lòng kiểm tra kết nối máy in và thử lại."
            )
            return
        
        # Lưu file
        timestamp = time.strftime("%Y%m%d-%H%M%S")
        filename = f"photo_{timestamp}.jpg"
        filepath = os.path.join(OUTPUT_DIR, filename)
        
        cv2.imwrite(filepath, self.merged_image)
        
        # Cập nhật carousel với ảnh mới
        self.gallery_photos = load_sample_photos()
        self.load_carousel_photos()
        
        # In ảnh
        try:
            os.startfile(filepath, "print")
            QMessageBox.information(
                self,
                "✅ ĐANG IN ẢNH",
                f"Ảnh đã được gửi đến máy in: {printer_info}\n\n"
                f"File đã lưu: {filename}\n\n"
                "Vui lòng chờ trong giây lát..."
            )
            
            # Reset về màn hình bắt đầu sau khi in
            QTimer.singleShot(3000, self.reset_all)
            
        except Exception as e:
            QMessageBox.critical(
                self,
                "❌ LỖI IN ẢNH",
                f"Không thể in ảnh: {str(e)}"
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
        
        # Về màn hình bắt đầu
        self.stacked.setCurrentIndex(0)

    def closeEvent(self, event):
        """Cleanup khi đóng app."""
        self.camera_timer.stop()
        self.countdown_timer.stop()
        if hasattr(self, 'carousel1'):
            self.carousel1.scroll_timer.stop()
        if hasattr(self, 'carousel2'):
            self.carousel2.scroll_timer.stop()
        self.cap.release()
        event.accept()


if __name__ == "__main__":
    ensure_directories()
    app = QApplication(sys.argv)
    
    # Set font mặc định - sử dụng font hỗ trợ tiếng Việt
    font = QFont("Arial", 12)
    font.setStyleHint(QFont.SansSerif)
    app.setFont(font)
    
    window = PhotoboothApp()
    window.show()
    sys.exit(app.exec_())
