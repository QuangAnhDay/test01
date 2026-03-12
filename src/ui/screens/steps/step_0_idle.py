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

    gallery_title = QLabel("📸 NHỮNG KHOẢNH KHẮC ĐÁNG NHỚ")
    gallery_title.setObjectName("TitleLabel")
    gallery_title.setAlignment(Qt.AlignCenter)
    gallery_layout.addWidget(gallery_title)

    subtitle = QLabel("Những bức ảnh thành phẩm tuyệt đẹp từ Photobooth")
    subtitle.setObjectName("InfoLabel")
    subtitle.setAlignment(Qt.AlignCenter)
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

    logo_label = QLabel("📷")
    logo_label.setStyleSheet("font-size: 80px;")
    logo_label.setAlignment(Qt.AlignCenter)
    start_layout.addWidget(logo_label)

    title = QLabel("PHOTOBOOTH")
    title.setObjectName("TitleLabel")
    title.setAlignment(Qt.AlignCenter)
    start_layout.addWidget(title)

    welcome_text = QLabel("Chào mừng bạn!\nNhấn nút bên dưới để bắt đầu")
    welcome_text.setObjectName("InfoLabel")
    welcome_text.setAlignment(Qt.AlignCenter)
    welcome_text.setWordWrap(True)
    welcome_text.setStyleSheet("color: #a8dadc; font-size: 18px;")
    start_layout.addWidget(welcome_text)

    start_layout.addStretch()

    app.btn_start_welcome = QPushButton("🎬 BẮT ĐẦU CHỤP")
    app.btn_start_welcome.setObjectName("GreenBtn")
    app.btn_start_welcome.setFixedSize(280, 90)
    app.btn_start_welcome.setStyleSheet("""
        QPushButton {
            background: qlineargradient(x1:0, y1:0, x2:1, y2:1,
                stop:0 #06d6a0, stop:1 #00f5d4);
            color: #1a1a2e; border: none; border-radius: 20px;
            padding: 20px 40px; font-size: 24px; font-weight: bold;
        }
        QPushButton:hover {
            background: qlineargradient(x1:0, y1:0, x2:1, y2:1,
                stop:0 #00f5d4, stop:1 #06d6a0);
        }
        QPushButton:pressed { background-color: #04a777; }
    """)
    app.btn_start_welcome.clicked.connect(app.go_to_price_select)
    start_layout.addWidget(app.btn_start_welcome, alignment=Qt.AlignCenter)

    start_layout.addStretch()

    info_label = QLabel("💡 Chụp lên đến 10 ảnh\n🖼️ Chọn khung ảnh đẹp\n🖨️ In ngay tại chỗ")
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
