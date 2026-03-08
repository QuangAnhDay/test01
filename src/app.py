# ==========================================
# PHOTOBOOTH APP - MAIN APPLICATION (Chế độ có thanh toán)
# ==========================================
"""
File chính điều khiển toàn bộ ứng dụng Photobooth.
Sử dụng QStackedWidget để chuyển đổi giữa các bước (steps).

CÁCH CHẠY:
    python -m src.app          (từ thư mục gốc)
    hoặc: python src/app.py
"""

import sys
import os
import cv2
import time
import traceback
import numpy as np

# === PATH FIX: Cho phép chạy trực tiếp bằng `python src/app.py` ===
_PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if _PROJECT_ROOT not in sys.path:
    sys.path.insert(0, _PROJECT_ROOT)

from PyQt5.QtWidgets import (QApplication, QMainWindow, QWidget, QLabel,
                             QPushButton, QVBoxLayout, QHBoxLayout, QScrollArea,
                             QMessageBox, QFrame, QGridLayout, QStackedWidget,
                             QGroupBox)
from PyQt5.QtCore import Qt, QTimer, QSize
from PyQt5.QtGui import QImage, QPixmap, QFont, QIcon

# Import shared
from src.shared.types.models import (
    WINDOW_TITLE, WINDOW_WIDTH, WINDOW_HEIGHT, CAMERA_INDEX,
    FIRST_PHOTO_DELAY, BETWEEN_PHOTO_DELAY, PHOTOS_TO_TAKE,
    TEMPLATE_DIR, OUTPUT_DIR, APP_CONFIG,
    get_price_2, get_price_4, format_price,
    generate_unique_code, generate_vietqr_url,
    load_config, get_price_by_layout, get_layout_config
)
from src.shared.utils.helpers import (
    ensure_directories, convert_cv_qt, overlay_images,
    load_sample_photos, get_rounded_pixmap
)
from src.shared.utils.qr_utils import generate_qr_code

# Import modules
from src.modules.payment.payment_service import QRImageLoaderThread, CassoCheckThread
from src.modules.image_processing.processor import (
    generate_frame_templates, create_collage, crop_to_aspect_wh,
    load_templates_for_layout, apply_template_overlay,
    load_all_templates_for_group, detect_layout_from_template
)

# Import UI components
from src.photobooth.components.dialogs import DownloadQRDialog

# Import step screens
#from src.photobooth.steps.step_0_idle import create_idle_screen
from src.photobooth.steps.step_1_package import create_package_screen
from src.photobooth.steps.step_2_payment import create_payment_screen
from src.photobooth.steps.step_3_liveview import create_liveview_screen
from src.photobooth.steps.step_4_capture import create_photo_select_screen
from src.photobooth.steps.step_6_template import create_template_screen
from src.photobooth.steps.step_8_finish import create_finish_screen
from src.photobooth.steps.step_1_custom_editor import create_custom_editor_screen
from src.photobooth.steps.step_9_interactive import create_interactive_capture_screen
from src.ui.screens.home_screen import HomeScreen

# Import flow controller
from src.photobooth.hooks.flow_controller import FlowController


# ==========================================
# STYLESHEET TOÀN CỤC
# ==========================================
GLOBAL_STYLESHEET = """
    QMainWindow { background-color: #F2E3E5; }
    QLabel { 
        color: white; 
        font-family: 'Arial', 'Tahoma', 'Segoe UI', sans-serif;
        font-size: 18px;
    }
    QLabel#TitleLabel {
        font-size: 32px; font-weight: bold; color: #eaf0f6;
        font-family: 'Arial', 'Tahoma', sans-serif;
    }
    QLabel#SubTitleLabel {
        font-size: 24px; font-weight: bold; color: #ffd700;
        font-family: 'Arial', 'Tahoma', sans-serif;
    }
    QLabel#CountdownLabel {
        font-size: 120px; font-weight: bold; color: #ffd700;
    }
    QLabel#InfoLabel {
        font-size: 24px; color: #a8dadc;
        font-family: 'Arial', 'Tahoma', sans-serif;
    }
    QLabel#PriceLabel {
        font-size: 28px; font-weight: bold; color: #06d6a0;
        font-family: 'Arial', 'Tahoma', sans-serif;
    }
    QPushButton {
        background-color: #e94560; color: white; border: none;
        border-radius: 15px; padding: 20px 40px; font-size: 22px;
        font-weight: bold; font-family: 'Arial', 'Tahoma', sans-serif;
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
    QScrollArea { border: none; background-color: transparent; }
    QWidget#PhotoCard {
        background-color: #16213e; border-radius: 10px;
        border: 2px solid #E9E1E3;
    }
    QWidget#PhotoCard:hover { border-color: #e94560; }
    QWidget#GalleryPanel { background-color: #0f0f23; }
    QWidget#StartPanel {
        background-color: #1a1a2e; border-left: 2px solid #4361ee;
    }
"""


class PhotoboothApp(QMainWindow):
    """Ứng dụng Photobooth chính với đầy đủ chức năng."""

    def __init__(self):
        super().__init__()
        self.setWindowTitle(WINDOW_TITLE)
        self.resize(WINDOW_WIDTH, WINDOW_HEIGHT)
        self.setStyleSheet(GLOBAL_STYLESHEET)

        # --- FLOW CONTROLLER ---
        self.flow = FlowController()

        # Shortcut references
        self.state = self.flow.state
        self.captured_photos = self.flow.captured_photos
        self.selected_frame_count = self.flow.selected_frame_count
        self.selected_photo_indices = self.flow.selected_photo_indices
        self.collage_image = self.flow.collage_image
        self.merged_image = self.flow.merged_image
        self.current_frame = self.flow.current_frame
        self.countdown_val = self.flow.countdown_val
        self.selected_price_type = self.flow.selected_price_type
        self.payment_confirmed = self.flow.payment_confirmed
        self.layout_type = self.flow.layout_type

        # Thread references
        self.casso_thread = None
        self.qr_loader_thread = None
        self.current_transaction_code = ""
        self.current_amount = 0

        # Gallery photos
        self.gallery_photos = load_sample_photos()

        # --- CAMERA (đọc từ camera_settings.json) ---
        import json
        _cam_cfg = {}
        _cam_settings_path = os.path.join(_PROJECT_ROOT, "camera_settings.json")
        if os.path.exists(_cam_settings_path):
            try:
                with open(_cam_settings_path, 'r') as _f:
                    _cam_cfg = json.load(_f)
            except Exception:
                pass
        elif os.path.exists("camera_settings.json"):
            try:
                with open("camera_settings.json", 'r') as _f:
                    _cam_cfg = json.load(_f)
            except Exception:
                pass

        _cam_idx = _cam_cfg.get("camera_index", CAMERA_INDEX)
        _use_dshow = _cam_cfg.get("use_dshow", True)
        _use_compat = _cam_cfg.get("use_compat", False)
        _cam_w = _cam_cfg.get("width", 1280)
        _cam_h = _cam_cfg.get("height", 960)

        print(f"[DEBUG] Camera Config Loaded: {_cam_cfg}")
        print(f"[DEBUG] Final Cam Index: {_cam_idx} (Type: {type(_cam_idx)})")

        if isinstance(_cam_idx, str) and _cam_idx.startswith("http"):
            self.cap = cv2.VideoCapture(_cam_idx)
            print(f"[CAMERA] Kết nối DSLR qua MJPEG: {_cam_idx}")
        elif _use_dshow and os.name == "nt":
            self.cap = cv2.VideoCapture(_cam_idx, cv2.CAP_DSHOW)
            if not self.cap.isOpened():
                self.cap = cv2.VideoCapture(_cam_idx)  # Fallback
        else:
            self.cap = cv2.VideoCapture(_cam_idx)

        # Chế độ tương thích (Chỉ áp dụng cho webcam thật)
        if not (isinstance(_cam_idx, str) and _cam_idx.startswith("http")):
            if _use_compat:
                self.cap.set(cv2.CAP_PROP_FOURCC, cv2.VideoWriter_fourcc(*'MJPG'))
                self.cap.set(cv2.CAP_PROP_FRAME_WIDTH, 640)
                self.cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)
                print(f"[CAMERA] Main App: Compat mode (MJPG 640x480)")
            else:
                self.cap.set(cv2.CAP_PROP_FRAME_WIDTH, _cam_w)
                self.cap.set(cv2.CAP_PROP_FRAME_HEIGHT, _cam_h)

        self.current_camera_index = _cam_idx
        self._cam_read_fail_count = 0

        # Warmup: Đọc bỏ vài frame đầu
        if self.cap.isOpened():
            for _ in range(5):
                self.cap.read()
            print(f"[CAMERA] Đã mở camera index {_cam_idx} (dshow={_use_dshow}, compat={_use_compat})")
        else:
            print(f"[CAMERA ERROR] Không thể mở camera index {_cam_idx}")

        # --- MAIN LAYOUT ---
        self.central_widget = QWidget()
        self.setCentralWidget(self.central_widget)
        self.main_layout = QVBoxLayout(self.central_widget)
        self.main_layout.setContentsMargins(0, 0, 0, 0)
        self.main_layout.setSpacing(0)

        # --- STACKED WIDGET ---
        self.stacked = QStackedWidget()
        self.main_layout.addWidget(self.stacked)

        # Thiết lập các màn hình
        self.home_screen = HomeScreen(self)
        if hasattr(self, 'cap') and self.cap:
            self.home_screen.camera_view.set_capture(self.cap)
            
        self.home_screen.start_clicked.connect(self.go_to_price_select)
        self.home_screen.open_admin.connect(lambda: self.stacked.setCurrentIndex(8))
        
        self.stacked.addWidget(self.home_screen)                   # 0 - Welcome
        self.showFullScreen()
        self.stacked.addWidget(create_package_screen(self))       # 1 - Package
        self.stacked.addWidget(create_payment_screen(self))       # 2 - Payment
        self.stacked.addWidget(create_liveview_screen(self))      # 3 - LiveView
        self._create_layout_select_screen()                       # 4 - Layout Select
        self.stacked.addWidget(create_photo_select_screen(self))  # 5 - Photo Select
        self.stacked.addWidget(create_template_screen(self))      # 6 - Template
        self.stacked.addWidget(create_finish_screen(self))        # 7 - Finish
        self.stacked.addWidget(create_custom_editor_screen(self)) # 8 - Custom Editor
        self.stacked.addWidget(create_interactive_capture_screen(self)) # 9 - Chụp & Ghép trực tiếp

        # Trạng thái lấp đầy slot
        self.current_slot_index = 0
        self.interactive_photos = []

        # --- TIMERS ---
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
        generate_frame_templates()
        self.templates = []

    # ==========================================
    # LAYOUT SELECT SCREEN (giữ trong app vì phức tạp)
    # ==========================================
    def _create_layout_select_screen(self):
        screen = QWidget()
        layout = QVBoxLayout(screen)
        layout.setAlignment(Qt.AlignCenter)
        layout.setSpacing(20)
        layout.setContentsMargins(40, 40, 40, 40)

        self.layout_title = QLabel("🖼️ CHỌN BỐ CỤC ẢNH")
        self.layout_title.setObjectName("TitleLabel")
        self.layout_title.setAlignment(Qt.AlignCenter)
        layout.addWidget(self.layout_title)

        self.layout_subtitle = QLabel("Hãy chọn cách sắp xếp các tấm ảnh của bạn")
        self.layout_subtitle.setObjectName("InfoLabel")
        self.layout_subtitle.setAlignment(Qt.AlignCenter)
        layout.addWidget(self.layout_subtitle)

        # Thêm ScrollArea để chứa nhiều layout
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setStyleSheet("background-color: transparent; border: none;")
        
        self.layout_options_widget = QWidget()
        self.layout_options_layout = QHBoxLayout(self.layout_options_widget)
        self.layout_options_layout.setSpacing(40)
        self.layout_options_layout.setAlignment(Qt.AlignCenter)
        self.layout_options_layout.setContentsMargins(20, 20, 20, 20)
        
        scroll.setWidget(self.layout_options_widget)
        layout.addWidget(scroll)

        # Nút Quay Lại (đặt ở dưới cùng)
        self.btn_layout_back = QPushButton("⬅️ QUAY LẠI")
        self.btn_layout_back.setFixedSize(250, 70)
        self.btn_layout_back.setObjectName("OrangeBtn")
        self.btn_layout_back.clicked.connect(lambda: self.stacked.setCurrentIndex(1))
        layout.addWidget(self.btn_layout_back, alignment=Qt.AlignCenter)

        self.stacked.addWidget(screen)

    def go_to_custom_layout_select(self, group_filter="custom"):
        """Bỏ qua bước chọn layout, hiển thị thẳng tất cả template trong nhóm."""
        # Reset trạng thái
        self.selected_template_path = None
        self.collage_image = None
        self.merged_image = None
        self._current_group_filter = group_filter  # Lưu lại nhóm đang chọn
        
        # Load TẤT CẢ templates trong nhóm (không phân biệt layout)
        self.templates = load_all_templates_for_group(group_filter)
        
        if not self.templates:
            QMessageBox.information(self, "Thông báo", 
                f"Hiện chưa có template nào trong nhóm {group_filter}.")
            return
        
        # Chuyển thẳng sang màn hình chọn template (index 6)
        self.state = "TEMPLATE_SELECT"
        
        # Điều chỉnh UI lọc dựa trên nhóm: Chỉ ẩn ở Custom, hiện ở Vertical
        if group_filter == "custom":
            if hasattr(self, 'filter_container'):
                self.filter_container.hide()
            if hasattr(self, 'list_container'):
                self.list_container.setGeometry(40, 160, 1160, 880) 
        else:
            if hasattr(self, 'filter_container'):
                self.filter_container.show()
            if hasattr(self, 'list_container'):
                self.list_container.setGeometry(40, 300, 1160, 740)
                # Mặc định chọn lọc "Tất cả" khi mới vào Vertical
                if hasattr(self, 'btn_filter_all'):
                    self.btn_filter_all.setChecked(True)
                if hasattr(self, 'btn_filter_3'):
                    self.btn_filter_3.setChecked(False)
                if hasattr(self, 'btn_filter_4'):
                    self.btn_filter_4.setChecked(False)
        
        # Hiển thị preview trống (chưa chọn template)
        self.update_template_preview()
        
        # Populate template buttons
        for i in reversed(range(self.template_btn_layout.count())):
            widget = self.template_btn_layout.itemAt(i).widget()
            if widget:
                widget.deleteLater()

        for idx, path in enumerate(self.templates):
            btn = QPushButton()
            btn.setFixedSize(220, 320)
            pix = QPixmap(path).scaled(200, 300, Qt.KeepAspectRatio, Qt.SmoothTransformation)
            btn.setIcon(QIcon(pix))
            btn.setIconSize(QSize(200, 300))
            btn.setCheckable(True)
            btn.setStyleSheet("""
                QPushButton {
                    background: transparent; border: none;
                }
                QPushButton:checked { border: 5px solid #F8D7D8; border-radius: 15px; }
                QPushButton:hover { border: 2px solid #F1C4C5; border-radius: 15px; }
            """)
            btn.clicked.connect(lambda checked, p=path, b=btn: self.apply_template(p, b))
            self.template_btn_layout.addWidget(btn)

        self.stacked.setCurrentIndex(6)



    def quick_select_group(self, group_filter="vertical"):
        """Tự động chọn layout mặc định cho nhóm và nhảy thẳng tới Template Select."""
        from src.shared.types.models import get_all_layouts
        all_layouts = get_all_layouts()
        
        target_layout = "4x1"
        slot_count = 4

        if group_filter == "vertical":
            target_layout = "4x1"
            slot_count = 4
        else:
            # Tìm layout đầu tiên thuộc nhóm custom
            custom_layouts = [k for k, v in all_layouts.items() if v.get("group", "custom") == "custom" and k != "4x1"]
            if custom_layouts:
                target_layout = custom_layouts[0]
                cfg = all_layouts[target_layout]
                slot_count = len(cfg.get("SLOTS", [1,2,3,4]))
            else:
                target_layout = "2x2" # Fallback
                slot_count = 4

        print(f"[DEBUG] Quick Selecting: {target_layout} ({slot_count} slots)")
        self.select_layout_and_price(slot_count, target_layout)

    def go_to_price_select(self):
        self.state = "PRICE_SELECT"
        self.stacked.setCurrentIndex(1)

    def select_layout_and_price(self, photo_count, layout_type):
        """Xử lý khi chọn gói - Chuyển sang chọn Template trước khi chụp."""
        self.selected_price_type = photo_count
        self.selected_frame_count = photo_count
        self.layout_type = layout_type
        self.selected_template_path = None  # Reset template đã chọn
        self.collage_image = None
        self.merged_image = None
        
        # Chế độ CUSTOM_INTERFACE giờ đây sẽ hoạt động như một layout group 
        # chứa các template đã được Admin định nghĩa sẵn.
        
        # Chuyển sang màn hình chọn Template
        self.go_to_template_select()

    def on_qr_image_loaded(self, pixmap):
        scaled = pixmap.scaled(350, 350, Qt.KeepAspectRatio, Qt.SmoothTransformation)
        self.qr_label.setPixmap(scaled)

    def on_qr_load_error(self, error):
        self.qr_label.setText(f"❌ Lỗi tải QR\n{error[:30]}...")
        content = f"{APP_CONFIG.get('bank_account', '')} - {self.current_amount} - {self.current_transaction_code}"
        pixmap = generate_qr_code(content, 300)
        self.qr_label.setPixmap(pixmap)

    def start_casso_check(self):
        if hasattr(self, 'casso_thread') and self.casso_thread and self.casso_thread.isRunning():
            self.casso_thread.stop()
            self.casso_thread.wait()

        self.casso_thread = CassoCheckThread(self.current_amount, self.current_transaction_code)
        self.casso_thread.payment_received.connect(self.on_payment_received)
        self.casso_thread.check_error.connect(self.on_casso_error)
        self.casso_thread.start()

    def on_payment_received(self):
        self.payment_status_label.setText("✅ ĐÃ NHẬN THANH TOÁN!")
        self.payment_status_label.setStyleSheet("font-size: 24px; color: #06d6a0; font-weight: bold;")
        if self.casso_thread and self.casso_thread.isRunning():
            self.casso_thread.stop()
        QTimer.singleShot(1500, self.go_to_capture_screen)

    def on_casso_error(self, error):
        self.payment_status_label.setText(f"⚠️ Lỗi: {error[:50]}...")
        self.payment_status_label.setStyleSheet("font-size: 16px; color: #ff6b6b;")

    def cancel_payment_and_go_back(self):
        if hasattr(self, 'casso_thread') and self.casso_thread and self.casso_thread.isRunning():
            self.casso_thread.stop()
            self.casso_thread.wait()
        if hasattr(self, 'qr_loader_thread') and self.qr_loader_thread and self.qr_loader_thread.isRunning():
            self.qr_loader_thread.wait()
        self.stacked.setCurrentIndex(1)

    def go_to_capture_screen(self):
        self.state = "WAITING_CAPTURE"
        self.captured_photos = []
        self.selected_photo_indices = []
        self.stacked.setCurrentIndex(3)
        self.photo_count_label.setText(f"Ảnh: 0/{PHOTOS_TO_TAKE}")
        self.status_label.setText("Sẵn sàng?")
        self.countdown_label.setText("")
        self.btn_capture_start.show()

    def update_camera_frame(self):
        """Cập nhật khung hình camera cho mọi trạng thái đang xem."""
        if self.state in ["START", "CAPTURING", "WAITING_CAPTURE", "INTERACTIVE_CAPTURE"]:
            ret, frame = self.cap.read()
            if ret and frame is not None:
                self._cam_read_fail_count = 0
                frame = cv2.flip(frame, 1)
                
                # Cập nhật frame hiện tại cho Flow và Capture
                self.current_frame = frame.copy()
                self.current_frame_cv = frame.copy() # Compatible với code cũ
                
                qt_img = convert_cv_qt(frame)
                
                # 1. Cập nhật Preview cho HomeScreen (nếu đang ở Home)
                if self.state == "START" and hasattr(self, 'home_screen'):
                    # Ta cập nhật trực tiếp vào label của CameraView bên trong HomeScreen
                    # Tránh việc CameraView tự chạy thread riêng gây double-read
                    self.home_screen.camera_view.display_frame(qt_img)
                
                # 2. Vẽ lên Step 3 (LiveView cũ)
                elif self.stacked.currentIndex() == 3:
                     scaled = qt_img.scaled(self.camera_label.size(), Qt.KeepAspectRatio, Qt.SmoothTransformation)
                     self.camera_label.setPixmap(scaled)
                
                # 3. Vẽ lên Step 9 (Interactive MỚI)
                elif self.stacked.currentIndex() == 9 and hasattr(self, 'interactive_camera_label'):
                     scaled_mini = qt_img.scaled(self.interactive_camera_label.size(), Qt.KeepAspectRatio, Qt.SmoothTransformation)
                     rounded = get_rounded_pixmap(scaled_mini, radius=30)
                     self.interactive_camera_label.setPixmap(rounded)
            else:
                self._cam_read_fail_count += 1
                if self._cam_read_fail_count > 60: # ~2 giây mất hình
                    print("[CAMERA WARNING] Mất tín hiệu camera trong App loop, không reset tự động để tránh treo.")
                    self._cam_read_fail_count = 0

    def start_capture_session(self):
        self.state = "CAPTURING"
        self.btn_capture_start.hide()
        self.countdown_val = FIRST_PHOTO_DELAY
        self.photo_count_label.setText(f"Ảnh: 0/{PHOTOS_TO_TAKE}")
        self.status_label.setText("Chuẩn bị tạo dáng!")
        self.countdown_label.setText(str(self.countdown_val))
        self.countdown_timer.start(1000)

    def countdown_tick(self):
        self.countdown_val -= 1
        if self.countdown_val > 0:
            self.countdown_label.setText(str(self.countdown_val))
        else:
            self.countdown_label.setText("📸")
            self.capture_photo()

    def capture_photo(self):
        # Nếu dùng DSLR, ra lệnh chụp trước khi lấy frame
        if isinstance(self.current_camera_index, str) and "127.0.0.1" in self.current_camera_index:
            self.trigger_dslr_capture()
            import time
            time.sleep(0.4) # Chờ màn trập và stream cập nhật

        if self.current_frame is not None:
            self.captured_photos.append(self.current_frame.copy())
            photo_num = len(self.captured_photos)
            self.photo_count_label.setText(f"Ảnh: {photo_num}/{PHOTOS_TO_TAKE}")

            if photo_num < PHOTOS_TO_TAKE:
                self.countdown_val = BETWEEN_PHOTO_DELAY
                self.countdown_label.setText(str(self.countdown_val))
                self.status_label.setText(f"Đã chụp ảnh {photo_num}! Tiếp tục...")
            else:
                self.countdown_timer.stop()
                self.countdown_label.setText("✓")
                self.status_label.setText("Hoàn thành!")
                QTimer.singleShot(1000, self.go_to_photo_select)

    def go_to_photo_select(self):
        self.state = "PHOTO_SELECT"
        self.selected_photo_indices = []

        self.photo_select_title.setText(
            f"CHỌN {self.selected_frame_count} ẢNH CHO KHUNG {self.selected_frame_count} ẢNH")

        if self.selected_frame_count == 2:
            self.selection_time_left = 60
        else:
            self.selection_time_left = 120

        self.update_timer_label()
        self.selection_timer.start(1000)

        # Clear grid cũ
        for i in reversed(range(self.photo_grid_layout.count())):
            widget = self.photo_grid_layout.itemAt(i).widget()
            if widget:
                widget.deleteLater()

        self.photo_buttons = []
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
            btn.setStyleSheet("border: none; border-radius: 5px;")
            btn.clicked.connect(
                lambda checked, i=idx, c=container, b=btn: self.toggle_photo(i, c, b))

            layout.addWidget(btn)

            lbl = QLabel(f"Ảnh {idx + 1}")
            lbl.setAlignment(Qt.AlignCenter)
            lbl.setStyleSheet("font-size: 14px; font-weight: bold;")
            layout.addWidget(lbl)

            row = idx // 5
            col = idx % 5
            self.photo_grid_layout.addWidget(container, row, col)
            self.photo_buttons.append(btn)

        self.btn_confirm_photos.setEnabled(False)
        self.stacked.setCurrentIndex(5)

    def on_selection_timer_tick(self):
        self.selection_time_left -= 1
        self.update_timer_label()
        if self.selection_time_left <= 0:
            self.selection_timer.stop()
            self.auto_confirm_selection()

    def update_timer_label(self):
        minutes = self.selection_time_left // 60
        seconds = self.selection_time_left % 60
        self.lbl_selection_timer.setText(f"Thời gian còn lại: {minutes:02d}:{seconds:02d}")
        if self.selection_time_left < 10:
            self.lbl_selection_timer.setStyleSheet("font-size: 24px; color: #ff6b6b; font-weight: bold;")
        else:
            self.lbl_selection_timer.setStyleSheet("font-size: 24px; color: #ffd700; font-weight: bold;")

    def auto_confirm_selection(self):
        QMessageBox.warning(self, "Hết giờ",
                            "Đã hết thời gian chọn ảnh! Hệ thống sẽ tự động chọn ảnh cho bạn.")
        if len(self.selected_photo_indices) < self.selected_frame_count:
            needed = self.selected_frame_count - len(self.selected_photo_indices)
            for i in range(len(self.captured_photos)):
                if needed <= 0:
                    break
                if i not in self.selected_photo_indices:
                    self.selected_photo_indices.append(i)
                    needed -= 1

        if len(self.selected_photo_indices) > self.selected_frame_count:
            self.selected_photo_indices = self.selected_photo_indices[:self.selected_frame_count]

        self.confirm_photo_selection()

    def toggle_photo(self, index, container, button):
        if index in self.selected_photo_indices:
            self.selected_photo_indices.remove(index)
            container.setStyleSheet("""
                QWidget#PhotoCard {
                    background-color: #16213e; border: 2px solid #0f3460;
                    border-radius: 10px;
                }
            """)
            button.setChecked(False)
        else:
            if len(self.selected_photo_indices) >= self.selected_frame_count:
                button.setChecked(False)
                QMessageBox.information(self, "Thông báo",
                                        f"Bạn chỉ được chọn {self.selected_frame_count} ảnh!")
                return
            self.selected_photo_indices.append(index)
            container.setStyleSheet("""
                QWidget#PhotoCard {
                    background-color: #16213e; border: 5px solid #ffd700;
                    border-radius: 10px;
                }
            """)
            button.setChecked(True)

        self.btn_confirm_photos.setEnabled(
            len(self.selected_photo_indices) == self.selected_frame_count)

    def confirm_photo_selection(self):
        self.selection_timer.stop()
        selected_imgs = [self.captured_photos[i] for i in sorted(self.selected_photo_indices)]
        if not selected_imgs:
            QMessageBox.warning(self, "Lỗi", "Không có ảnh nào được chọn!")
            return

        self.collage_image = create_collage(selected_imgs, self.layout_type)
        self.merged_image = self.collage_image.copy()
        self.go_to_template_select()

    def go_to_template_select(self):
        self.state = "TEMPLATE_SELECT"
        
        # Hiện thanh lọc và đưa dải lấp đầy về vị trí chuẩn (Dành cho bản Dọc/Vertical)
        if hasattr(self, 'filter_container'):
            self.filter_container.show()
        if hasattr(self, 'list_container'):
            self.list_container.setGeometry(40, 300, 1160, 740) 
            
        self.templates = load_templates_for_layout(self.layout_type, self.selected_frame_count)

        self.update_template_preview()

        # Populate template buttons
        for i in reversed(range(self.template_btn_layout.count())):
            widget = self.template_btn_layout.itemAt(i).widget()
            if widget:
                widget.deleteLater()

        for idx, path in enumerate(self.templates):
            btn = QPushButton()
            btn.setFixedSize(220, 320)
            pix = QPixmap(path).scaled(200, 300, Qt.KeepAspectRatio, Qt.SmoothTransformation)
            btn.setIcon(QIcon(pix))
            btn.setIconSize(QSize(200, 300))
            btn.setCheckable(True)
            btn.setStyleSheet("""
                QPushButton {
                    background: transparent; border: none;
                }
                QPushButton:checked { border: 5px solid #F8D7D8; border-radius: 15px; }
                QPushButton:hover { border: 2px solid #F1C4C5; border-radius: 15px; }
            """)
            btn.clicked.connect(lambda checked, p=path, b=btn: self.apply_template(p, b))
            self.template_btn_layout.addWidget(btn)

        self.stacked.setCurrentIndex(6)

        # Cập nhật trạng thái nút lọc
        if hasattr(self, 'btn_filter_3'):
            self.btn_filter_3.setChecked(self.selected_frame_count == 3)
            self.btn_filter_4.setChecked(self.selected_frame_count == 4)

        self.template_time_left = 60
        self.update_template_timer_label()
        self.template_timer.start(1000)

    def on_template_timer_tick(self):
        self.template_time_left -= 1
        self.update_template_timer_label()
        if self.template_time_left <= 0:
            self.template_timer.stop()
            QMessageBox.information(self, "Hết giờ", "Đã hết thời gian! Hệ thống sẽ tự động in ảnh.")
            self.accept_and_print()

    def update_template_timer_label(self):
        minutes = self.template_time_left // 60
        seconds = self.template_time_left % 60
        self.lbl_template_timer.setText(f"Thời gian còn lại: {minutes:02d}:{seconds:02d}")
        if self.template_time_left < 10:
            self.lbl_template_timer.setStyleSheet("font-size: 24px; color: #ff6b6b; font-weight: bold;")
        else:
            self.lbl_template_timer.setStyleSheet("font-size: 24px; color: #ffd700; font-weight: bold;")

    def update_template_preview(self):
        if self.merged_image is not None:
            # Nếu convert_cv_qt của bạn đã trả về QPixmap, dùng trực tiếp luôn
            self.pixmap = convert_cv_qt(self.merged_image) 
        elif self.layout_type:
            cfg = get_layout_config(self.layout_type)
            bw, bh = cfg.get("CANVAS_W", 800), cfg.get("CANVAS_H", 600)
            blank = np.zeros((bh, bw, 3), dtype=np.uint8) + 200
            
            # Chuyển từ numpy array sang QImage
            qt_img = QImage(blank.data, bw, bh, bw * 3, QImage.Format_RGB888)
            # Sau đó mới chuyển QImage sang QPixmap
            self.pixmap = QPixmap.fromImage(qt_img)
        else:
            return

        # Hiển thị lên giao diện
        target_size = self.template_preview_label.size()
        if target_size.width() <= 10 or target_size.height() <= 10:
            target_size = QSize(800, 600) # Fallback size
            
        scaled = self.pixmap.scaled(target_size, Qt.KeepAspectRatio, Qt.SmoothTransformation)
        self.template_preview_label.setPixmap(scaled)

    def filter_templates_by_count(self, count):
        """Lọc danh sách template theo số lượng pô ảnh."""
        self.selected_frame_count = count
        
        # Cập nhật UI nút lọc
        if hasattr(self, 'btn_filter_3'):
            self.btn_filter_3.setChecked(count == 3)
        if hasattr(self, 'btn_filter_4'):
            self.btn_filter_4.setChecked(count == 4)
        if hasattr(self, 'btn_filter_all'):
            self.btn_filter_all.setChecked(count == 0)

        # Lấy lại danh sách full cho group hiện tại
        group = getattr(self, '_current_group_filter', self.layout_type)
        if group == "4x1": group = "vertical"
        
        all_for_group = load_all_templates_for_group("vertical" if "vertical" in str(group).lower() else "custom")
        
        # Lọc những cái có số slot khớp
        filtered = []
        for p in all_for_group:
            lname = detect_layout_from_template(p)
            cfg = get_layout_config(lname)
            slots = cfg.get("SLOTS", [])

            if count == 0: # Lấy TẤT CẢ
                filtered.append(p)
            elif len(slots) == count:
                filtered.append(p)
            elif count == 4 and lname == "4x1": # Trường hợp đặc biệt 4x1 mặc định
                filtered.append(p)

        self.templates = filtered
        
        # Refresh danh sách nút
        for i in reversed(range(self.template_btn_layout.count())):
            widget = self.template_btn_layout.itemAt(i).widget()
            if widget: widget.deleteLater()

        for idx, path in enumerate(self.templates):
            btn = QPushButton()
            btn.setFixedSize(220, 320)
            pix = QPixmap(path).scaled(200, 300, Qt.KeepAspectRatio, Qt.SmoothTransformation)
            btn.setIcon(QIcon(pix))
            btn.setIconSize(QSize(200, 300))
            btn.setCheckable(True)
            btn.setStyleSheet("""
                QPushButton {
                    background: transparent; border: none;
                }
                QPushButton:checked { border: 5px solid #F8BBD0; border-radius: 15px; }
                QPushButton:hover { border: 2px solid #F1C4C5; border-radius: 15px; }
            """)
            btn.clicked.connect(lambda checked, p=path, b=btn: self.apply_template(p, b))
            self.template_btn_layout.addWidget(btn)

    def apply_template(self, template_path, source_btn=None):
        """Áp dụng template lên ảnh, tự phát hiện layout_type từ tên file template."""
        import os
        from src.shared.types.models import get_layout_config
        
        # Highlight nút đã chọn
        if source_btn:
            for i in range(self.template_btn_layout.count()):
                w = self.template_btn_layout.itemAt(i).widget()
                if isinstance(w, QPushButton):
                    w.setChecked(w == source_btn)

        # Phát hiện layout_type từ tên file template
        detected_layout = detect_layout_from_template(template_path)
        if detected_layout:
            self.layout_type = detected_layout
        elif not self.layout_type:
            folder_name = os.path.basename(os.path.dirname(template_path))
            self.layout_type = "4x1" if folder_name == "vertical" else folder_name
        
        cfg = get_layout_config(self.layout_type)
        
        # Cập nhật số lượng ảnh cần chụp (slots)
        if "SLOTS" in cfg:
            self.selected_frame_count = len(cfg["SLOTS"])
        elif self.selected_frame_count == 0:
            self.selected_frame_count = 4  # Mặc định
        
        print(f"[DEBUG] Template Selected: {template_path}")
        print(f"[DEBUG] Layout: {self.layout_type} ({self.selected_frame_count} slots)")

        # 3. Áp dụng template lên ảnh
        self.selected_template_path = template_path
        if self.collage_image is not None:
            self.merged_image = apply_template_overlay(self.collage_image, template_path)
        else:
            # Chưa có ảnh -> Tạo canvas trống theo kích thước Layout mới + đè template lên
            bw, bh = cfg.get("CANVAS_W", 800), cfg.get("CANVAS_H", 600)
            blank = np.zeros((bh, bw, 3), dtype=np.uint8) + 240
            self.merged_image = apply_template_overlay(blank, template_path)
            
        self.update_template_preview()

    def handle_template_confirmation(self):
        """Xác nhận Template -> Chuyển sang Chụp ảnh tương tác (Từng pô lấp đầy)."""
        self.template_timer.stop()
        self.current_slot_index = 0
        self.interactive_photos = []
        
        # Nếu đang ở bước chuẩn bị (chưa chụp ảnh)
        if self.state == "TEMPLATE_SELECT":
            # Điều hướng dựa trên chế độ Free/Paid
            if getattr(self, 'is_free_mode', False):
                # Bản Free: Vào giao diện chụp lấp đầy ngay
                self.state = "INTERACTIVE_CAPTURE"
                self.stacked.setCurrentIndex(9)
                self.update_interactive_template_preview()
                self.update_interactive_button_text()
            else:
                # Bản trả phí: Chuyển sang thanh toán trước
                self.setup_payment_flow()
        else:
            # Nếu đã chụp xong (luồng cũ)
            self.accept_and_print()

    def setup_payment_flow(self):
        """Khởi tạo thông tin thanh toán và chuyển sang màn hình QR."""
        self.current_transaction_code = generate_unique_code()
        self.current_amount = get_price_by_layout(self.layout_type)

        layout_name = {
            "2x1": "2 Hàng x 1 Cột", "1x2": "1 Hàng x 2 Cột",
            "4x1": "4 Hàng x 1 Cột", "2x2": "2 Hàng x 2 Cột"
        }.get(self.layout_type, self.layout_type)

        self.selected_package_label.setText(
            f"📦 {layout_name} - {self.selected_frame_count} ẢNH - {format_price(self.current_amount)}")
        self.transaction_code_label.setText(f"Nội dung CK: {self.current_transaction_code}")
        self.bank_info_label.setText(
            f"{APP_CONFIG.get('bank_name', '')} - {APP_CONFIG.get('bank_account', '')}")
        self.payment_status_label.setText("🔄 Đang chờ thanh toán...")
        self.payment_status_label.setStyleSheet("font-size: 18px; color: #ffd700;")

        # Tải QR Image (async)
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

    # ==========================================
    # LOGIC CHỤP ẢNH TƯƠNG TÁC (STEP 9)
    # ==========================================

    def update_interactive_button_text(self):
        """Cập nhật trạng thái bật/tắt của các nút (Step 9)."""
        idx = self.current_slot_index
        total = self.selected_frame_count
        
        self.btn_capture_step.setEnabled(idx < total)
        self.btn_retake_last.setEnabled(idx > 0)
        self.btn_finish_interactive.setEnabled(idx == total)

    def start_interactive_shot(self):
        """Bắt đầu Countdown 10s để chụp 1 tấm (Chuyển sang Full Camera)."""
        # Chuyển sang Page 1 (Full Camera)
        if hasattr(self, 'interactive_stack'):
            self.interactive_stack.setCurrentIndex(1)
        
        # Đồng bộ kích thước lớp phủ với camera label
        if hasattr(self, 'interactive_camera_label'):
            self.interactive_countdown_label.setGeometry(self.interactive_camera_label.rect())
            self.interactive_flash_overlay.setGeometry(self.interactive_camera_label.rect())

        self.countdown_val = 10
        self.interactive_countdown_label.setText(str(self.countdown_val))
        self.interactive_countdown_label.show()
        
        # Sử dụng QTimer để đếm ngược
        if not hasattr(self, 'timer_shot'):
            self.timer_shot = QTimer()
            self.timer_shot.timeout.connect(self.interactive_countdown_tick)
        
        self.timer_shot.start(1000)
        self.btn_capture_step.setEnabled(False)

    def interactive_countdown_tick(self):
        self.countdown_val -= 1
        if self.countdown_val > 0:
            self.interactive_countdown_label.setText(str(self.countdown_val))
        else:
            self.timer_shot.stop()
            self.interactive_countdown_label.hide()
            
            if hasattr(self, 'interactive_flash_overlay'):
                self.interactive_flash_overlay.show()
                # Kéo dài Flash lên 400ms cho "đã"
                QTimer.singleShot(400, self.interactive_flash_overlay.hide)
            
            # Chụp ảnh sau khi Flash sáng được một nửa (250ms) để lấy đúng khoảnh khắc
            QTimer.singleShot(250, self.take_one_photo)

    def take_one_photo(self):
        """Chụp 1 pô ảnh và lấp vào slot, sau đó quay về màn hình chính."""
        # Nếu dùng DSLR qua digiCamControl
        if isinstance(self.current_camera_index, str) and "127.0.0.1" in self.current_camera_index:
            self.trigger_dslr_capture()
            import time
            time.sleep(0.5) # Wait for DSLR shutter and MJPEG update

        ret, frame = self.cap.read()
        if ret:
            frame = cv2.flip(frame, 1)
            self.interactive_photos.append(frame.copy())
            self.current_slot_index += 1
            self.update_interactive_template_preview()
            self.update_interactive_button_text()
            
        # Quay về Page 0 (Preview)
        if hasattr(self, 'interactive_stack'):
            self.interactive_stack.setCurrentIndex(0)
            
        self.interactive_countdown_label.setText("")

    def retake_last_shot(self):
        """Xóa tấm ảnh gần nhất để chụp lại."""
        if self.interactive_photos:
            self.interactive_photos.pop()
            self.current_slot_index -= 1
            self.update_interactive_template_preview()
            self.update_interactive_button_text()

    def update_interactive_template_preview(self):
        """Vẽ Preview Template với những ảnh đã chụp lấp vào slot."""
        from src.shared.types.models import get_layout_config
        from src.modules.image_processing.processor import apply_template_overlay, crop_to_aspect_wh
        
        cfg = get_layout_config(self.layout_type)
        bw, bh = cfg.get("CANVAS_W", 800), cfg.get("CANVAS_H", 1200)
        
        # Canvas xám nhạt
        canvas = np.zeros((bh, bw, 3), dtype=np.uint8) + 240
        
        # Lấy Slots (Nếu 4x1 thì tự tính nếu cfg trống)
        slots = cfg.get("SLOTS", [])
        if not slots and self.layout_type == "4x1":
             slots = [(53, 48 + i*(312+32), 445, 312) for i in range(4)]
        
        print(f"[DEBUG] update_interactive: Layout={self.layout_type}, Slots={len(slots)}, Image Count={len(self.interactive_photos)}")
        
        # Vẽ các ảnh đã chụp
        for i, (sx, sy, sw, sh) in enumerate(slots):
            if i < len(self.interactive_photos):
                photo = self.interactive_photos[i]
                cropped = crop_to_aspect_wh(photo, sw, sh)
                resized = cv2.resize(cropped, (sw, sh))
                canvas[sy:sy+sh, sx:sx+sw] = resized
            else:
                # Vẽ ô trống màu hồng nhạt như mockup (#FFDBDB -> BGR: 219, 219, 255)
                cv2.rectangle(canvas, (sx, sy), (sx+sw, sy+sh), (219, 219, 255), -1)
        
        # Vẽ viền bao quanh toàn bộ canvas để thấy rõ biên
        cv2.rectangle(canvas, (0, 0), (bw-1, bh-1), (0, 0, 0), 5)

        # Lồng khung Template (nếu có)
        if hasattr(self, 'selected_template_path') and self.selected_template_path and os.path.exists(self.selected_template_path):
            canvas = apply_template_overlay(canvas, self.selected_template_path)
        
        self.collage_image = canvas  # Lưu lại kết quả cuối
        pixmap = convert_cv_qt(canvas)  # Returns QPixmap
        scaled = pixmap.scaled(self.interactive_template_label.size(), Qt.KeepAspectRatio, Qt.SmoothTransformation)
        self.interactive_template_label.setPixmap(scaled)

    def use_no_template(self):
        self.merged_image = self.collage_image.copy() if self.collage_image is not None else None
        self.handle_template_confirmation()

    def accept_and_print(self):
        self.template_timer.stop()
        # Dùng merged_image nếu có, nếu không dùng collage_image (từ interactive capture)
        final_image = self.merged_image if self.merged_image is not None else self.collage_image
        if final_image is None:
            return
        self.merged_image = final_image

        output_folder = r"D:\picture"
        os.makedirs(output_folder, exist_ok=True)

        timestamp = time.strftime("%Y%m%d-%H%M%S")
        filename = f"photo_{timestamp}.jpg"
        filepath = os.path.join(output_folder, filename)

        try:
            cv2.imwrite(filepath, self.merged_image)

            self.gallery_photos = load_sample_photos()
            if hasattr(self, 'carousel1'):
                half = len(self.gallery_photos) // 2
                self.carousel1.set_photos(self.gallery_photos[:max(half, 4)])
                self.carousel2.set_photos(
                    self.gallery_photos[half:] if half > 0 else self.gallery_photos[:4])

            dialog = DownloadQRDialog(filepath, self)
            dialog.exec_()
            self.reset_all()

        except Exception as e:
            QMessageBox.critical(self, "❌ LỖI LƯU ẢNH", f"Không thể lưu ảnh: {str(e)}")

    def reset_all(self):
        self.state = "START"
        self.captured_photos = []
        self.selected_photo_indices = []
        self.selected_frame_count = 0
        self.collage_image = None
        self.merged_image = None
        self.payment_confirmed = False
        self.selected_price_type = 0
        self.layout_type = ""
        self.stacked.setCurrentIndex(0)

    def keyPressEvent(self, event):
        """Xử lý phím tắt - Chế độ Admin."""
        if event.key() == Qt.Key_F2:
            # Mở trình thiết kế layout (chỉ dành cho Admin)
            QMessageBox.information(self, "Admin Mode", "Đang mở trình thiết kế Bố cục (Layout Designer)...")
            self.stacked.setCurrentIndex(8)
            if hasattr(self, 'custom_editor_step'):
                self.custom_editor_step.update_preview()
        super().keyPressEvent(event)

    def closeEvent(self, event):
        """Dừng tất cả các timer khi tắt ứng dụng."""
        for timer_attr in ['camera_timer', 'countdown_timer', 'selection_timer', 'template_timer', 'timer_shot']:
            if hasattr(self, timer_attr):
                timer = getattr(self, timer_attr)
                if timer and timer.isActive():
                    timer.stop()
        
        if hasattr(self, 'carousel1'):
            self.carousel1.scroll_timer.stop()
        if hasattr(self, 'carousel2'):
            self.carousel2.scroll_timer.stop()
        if hasattr(self, 'casso_thread') and self.casso_thread and self.casso_thread.isRunning():
            self.casso_thread.stop()
            self.casso_thread.wait()
        
        if hasattr(self, 'cap') and self.cap:
            self.cap.release()
        event.accept()

    def trigger_dslr_capture(self):
        """Gửi lệnh chụp HTTP tới digiCamControl."""
        import requests
        try:
            # Mặc định digiCamControl chạy Webserver ở port 5513
            requests.get("http://127.0.0.1:5513/remote?code=2001", timeout=1)
            print("[DSLR] Da gui lenh chụp thành công.")
        except Exception as e:
            print(f"[DSLR ERROR] Không thể gửi lệnh chụp: {e}")



# ==========================================
# ENTRY POINT
# ==========================================

def main():
    """Entry point cho chế độ có thanh toán."""
    if not load_config():
        app = QApplication(sys.argv)
        QMessageBox.critical(
            None, "❌ Thiếu cấu hình",
            "Không tìm thấy file config.json!\n\n"
            "Vui lòng chạy setup_admin.py trước để tạo cấu hình."
        )
        sys.exit(1)

    ensure_directories()

    app = QApplication(sys.argv)
    font = QFont("Arial", 12)
    font.setStyleHint(QFont.SansSerif)
    app.setFont(font)

    window = PhotoboothApp()
    window.show()
    return app.exec_()


def handle_exception(exc_type, exc_value, exc_traceback):
    """Bắt các lỗi chưa được xử lý."""
    if issubclass(exc_type, KeyboardInterrupt):
        sys.__excepthook__(exc_type, exc_value, exc_traceback)
        return

    error_msg = "".join(traceback.format_exception(exc_type, exc_value, exc_traceback))
    print(f"[CRITICAL ERROR]\n{error_msg}")

    msg = QMessageBox()
    msg.setIcon(QMessageBox.Critical)
    msg.setWindowTitle("Lỗi Hệ Thống")
    msg.setText("Ứng dụng gặp lỗi và cần khởi động lại.")
    msg.setInformativeText(str(exc_value))
    msg.setDetailedText(error_msg)
    msg.setStandardButtons(QMessageBox.Ok)
    msg.exec_()
    sys.exit(1)


sys.excepthook = handle_exception

if __name__ == "__main__":
    sys.exit(main())
