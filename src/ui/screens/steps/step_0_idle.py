import os
import sys

# === PATH FIX: Cho phép chạy trực tiếp ===
_PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
if _PROJECT_ROOT not in sys.path:
    sys.path.insert(0, _PROJECT_ROOT)

# ==========================================
# STEP 0 - IDLE (Màn hình chờ / Welcome)
# ==========================================
"""
Màn hình chờ: Hiển thị carousel ảnh và nút bắt đầu.
"""

from PyQt5.QtWidgets import QWidget, QLabel, QPushButton, QVBoxLayout, QHBoxLayout
from PyQt5.QtCore import Qt
from src.ui.widgets.carousel import CarouselPhotoWidget
from src.utils import load_sample_photos


def create_idle_screen(app):
    """Tạo màn hình Idle/Welcome với carousel ảnh."""
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

    gallery_title = QLabel("📸 MEMORABLE MOMENTS")
    gallery_title.setObjectName("TitleLabel")
    gallery_title.setAlignment(Qt.AlignCenter)
    gallery_layout.addWidget(gallery_title)

    subtitle = QLabel("Beautiful photos from Photobooth")
    subtitle.setObjectName("InfoLabel")
    subtitle.setAlignment(Qt.AlignCenter)
    # Mau chu thong tin huong dan (Xanh nhat)
    subtitle.setStyleSheet("color: #a8dadc; font-size: 16px;")
    gallery_layout.addWidget(subtitle)

    # Carousel hàng 1
    app.carousel1 = CarouselPhotoWidget()
    app.carousel1.scroll_speed = 2
    gallery_layout.addWidget(app.carousel1)

    # Carousel hàng 2 (ngược chiều)
    app.carousel2 = CarouselPhotoWidget()
    app.carousel2.scroll_speed = -2
    gallery_layout.addWidget(app.carousel2)

    info_text = QLabel("✨ Create wonderful memories with us! ✨")
    # Mau chu nhan manh (Vang kim)
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

    logo_label = QLabel("📷")
    logo_label.setStyleSheet("font-size: 80px;")
    logo_label.setAlignment(Qt.AlignCenter)
    start_layout.addWidget(logo_label)

    title = QLabel("PHOTOBOOTH")
    title.setObjectName("TitleLabel")
    title.setAlignment(Qt.AlignCenter)
    start_layout.addWidget(title)

    welcome_text = QLabel("Welcome!\nPress the button below to start")
    welcome_text.setObjectName("InfoLabel")
    welcome_text.setAlignment(Qt.AlignCenter)
    welcome_text.setWordWrap(True)
    # Mau chu chao mung (Xanh nhat)
    welcome_text.setStyleSheet("color: #a8dadc; font-size: 18px;")
    start_layout.addWidget(welcome_text)

    start_layout.addStretch()

    app.btn_start_welcome = QPushButton("🎬 START CAPTURING")
    app.btn_start_welcome.setObjectName("GreenBtn")
    app.btn_start_welcome.setFixedSize(280, 90)
    app.btn_start_welcome.setStyleSheet("""
        QPushButton {
            /* Mau nen nut Bat dau (Gradient Xanh la) */
            background: qlineargradient(x1:0, y1:0, x2:1, y2:1,
                stop:0 #06d6a0, stop:1 #00f5d4);
            /* Mau chu (Xanh den) */
            color: #1a1a2e; border: none; border-radius: 20px;
            padding: 20px 40px; font-size: 24px; font-weight: bold;
        }
        QPushButton:hover {
            /* Mau khi di chuot qua */
            background: qlineargradient(x1:0, y1:0, x2:1, y2:1,
                stop:0 #00f5d4, stop:1 #06d6a0);
        }
        QPushButton:pressed { background-color: #04a777; }
    """)
    app.btn_start_welcome.clicked.connect(app.go_to_price_select)
    start_layout.addWidget(app.btn_start_welcome, alignment=Qt.AlignCenter)

    start_layout.addStretch()

    info_label = QLabel("💡 Take up to 10 photos\n🖼️ Select beautiful frames\n🖨️ Print instantly")
    info_label.setAlignment(Qt.AlignCenter)
    info_label.setStyleSheet("color: #a8dadc; font-size: 14px;")
    start_layout.addWidget(info_label)

    main_layout.addWidget(start_panel, stretch=1)

    # Load ảnh cho carousel
    gallery_photos = load_sample_photos()
    if gallery_photos:
        half = len(gallery_photos) // 2
        app.carousel1.set_photos(gallery_photos[:max(half, 4)])
        app.carousel2.set_photos(gallery_photos[half:] if half > 0 else gallery_photos[:4])

    return screen
# ==========================================
# KHỐI TEST STANDALONE
# ==========================================
if __name__ == "__main__":
    from PyQt5.QtWidgets import QApplication

    # Giả lập đối tượng app
    class MockApp:
        def __init__(self):
            self.carousel1 = None
            self.carousel2 = None
            self.btn_start_welcome = None

        def go_to_price_select(self):
            print("Chuyển đến màn hình chọn gói!")

    app_qt = QApplication(sys.argv)
    
    # Áp dụng STYLE cho app test
    from src.ui.styles import GLOBAL_STYLESHEET
    app_qt.setStyleSheet(GLOBAL_STYLESHEET)

    mock_app = MockApp()
    window = create_idle_screen(mock_app)
    window.showFullScreen()
    sys.exit(app_qt.exec_())
