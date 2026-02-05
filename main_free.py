# ==========================================
# MAIN FREE MODE - KHÔNG CẦN THANH TOÁN
# ==========================================
"""
File chạy ứng dụng Photobooth ở chế độ MIỄN PHÍ.
Bỏ qua hoàn toàn bước chọn giá và thanh toán QR.

CÁCH CHẠY:
    python main_free.py

KHÁC BIỆT VỚI main.py:
    - Không có màn hình chọn giá
    - Không có màn hình QR thanh toán
    - Bấm "Bắt đầu" → Chụp ảnh ngay
    - Mặc định: 4 ảnh
"""

import os
import sys
import cv2
import datetime
from PyQt5.QtWidgets import (QApplication, QMessageBox, QPushButton, QWidget, 
                             QLabel, QVBoxLayout, QHBoxLayout, QFrame, QGridLayout)
from PyQt5.QtCore import Qt, QTimer, QRect
from PyQt5.QtGui import QPixmap, QFont, QBrush, QPalette, QImage, QPainter

# Import từ cấu trúc mô-đun mới
from config.settings import load_config, SAMPLE_PHOTOS_DIR, CAMERA_INDEX, OUTPUT_DIR, FIRST_PHOTO_DELAY, PHOTOS_TO_TAKE
from modules.utils import ensure_directories, convert_cv_qt, load_sample_photos
from ui.ui_main import PhotoboothApp
from ui.ui_components import DownloadSingleQRDialog


class FreePhotobooth(PhotoboothApp):
    """
    Photobooth miễn phí - Bỏ qua thanh toán.
    Kế thừa từ PhotoboothApp và override workflow.
    """
    
    def __init__(self):
        # Đặt flag TRƯỚC khi gọi super().__init__()
        self.is_free_mode = True
        
        # Khởi tạo biến video recording TRƯỚC khi gọi super()
        self.is_recording_video = False
        self.video_writer = None
        self.current_video_path = None
        
        # Đọc cấu hình camera từ setup_camera (nếu có)
        self.camera_config = self.load_camera_config_file()
        self.current_camera_index = self.camera_config.get("camera_index", 0)

        # Gọi constructor của class cha (Khởi tạo UI, camera mặc định)
        super().__init__()
        
        # Tự động chọn camera (ưu tiên Iriun/HDMI hoặc theo config đã chọn)
        self.auto_select_camera()
        
        # Đặt title khác để phân biệt
        self.setWindowTitle("🎉 Photobooth - MIỄN PHÍ")
        
        # Đặt mặc định cho chế độ free
        self.selected_price_type = 4  # Mặc định 4 ảnh
        self.selected_frame_count = 4
        self.payment_confirmed = True  # Luôn True vì không cần thanh toán
        
        print("\n" + "="*60)
        print("FREE MODE ACTIVATED")
        print("="*60)
        print("- Skipped price selection")
        print("- Skipped QR payment")
        print("- Default: 4 photos")
        print("="*60 + "\n")
    
    def create_welcome_screen(self):
        """Redesign welcome screen: Bloom Photobooth Style (Pink Theme)."""
        screen = QWidget()
        
        # Main Theme Colors
        BG_PINK = "#fdeef4"
        ACCENT_PINK = "#d87093" # PaleVioletRed
        BUTTON_PINK = "#f06292"
        
        screen.setStyleSheet(f"background-color: {BG_PINK};")

        main_layout = QHBoxLayout(screen)
        main_layout.setContentsMargins(40, 40, 40, 40)
        main_layout.setSpacing(40)
        
        # ===== LEFT SIDE: PHOTO COLLAGE =====
        # We'll use a widget with absolute positioning to simulate the scattered look
        left_side = QWidget()
        left_layout = QGridLayout(left_side)
        left_layout.setSpacing(15)
        
        photos = load_sample_photos()
        if not photos: photos = []
        
        # Style for individual photo cards
        card_style = """
            border: 8px solid white;
            background-color: white;
            border-radius: 5px;
        """
        
        # Adding some photos to the grid to create a collage feel
        # (Using a grid is more stable than absolute positioning for different resolutions)
        if len(photos) >= 6:
            # Column 1
            lbl1 = QLabel(); lbl1.setPixmap(QPixmap(photos[0]).scaled(140, 350, Qt.KeepAspectRatioByExpanding, Qt.SmoothTransformation))
            lbl1.setStyleSheet(card_style); left_layout.addWidget(lbl1, 0, 0, 3, 1)
            
            lbl2 = QLabel(); lbl2.setPixmap(QPixmap(photos[1]).scaled(140, 200, Qt.KeepAspectRatioByExpanding, Qt.SmoothTransformation))
            lbl2.setStyleSheet(card_style); left_layout.addWidget(lbl2, 3, 0, 2, 1)
            
            # Column 2
            lbl3 = QLabel(); lbl3.setPixmap(QPixmap(photos[2]).scaled(250, 250, Qt.KeepAspectRatioByExpanding, Qt.SmoothTransformation))
            lbl3.setStyleSheet(card_style); left_layout.addWidget(lbl3, 0, 1, 2, 2)
            
            lbl4 = QLabel(); lbl4.setPixmap(QPixmap(photos[3]).scaled(250, 250, Qt.KeepAspectRatioByExpanding, Qt.SmoothTransformation))
            lbl4.setStyleSheet(card_style); left_layout.addWidget(lbl4, 2, 1, 2, 2)
            
            # Column 3
            lbl5 = QLabel(); lbl5.setPixmap(QPixmap(photos[4]).scaled(140, 350, Qt.KeepAspectRatioByExpanding, Qt.SmoothTransformation))
            lbl5.setStyleSheet(card_style); left_layout.addWidget(lbl5, 0, 3, 3, 1)
            
            lbl6 = QLabel(); lbl6.setPixmap(QPixmap(photos[5]).scaled(140, 200, Qt.KeepAspectRatioByExpanding, Qt.SmoothTransformation))
            lbl6.setStyleSheet(card_style); left_layout.addWidget(lbl6, 3, 3, 2, 1)

        main_layout.addWidget(left_side, stretch=2)

        # ===== RIGHT SIDE: THE CONTROL CARD =====
        right_card = QFrame()
        right_card.setFixedWidth(450)
        right_card.setStyleSheet("""
            QFrame {
                background-color: white;
                border-radius: 40px;
            }
        """)
        card_layout = QVBoxLayout(right_card)
        card_layout.setContentsMargins(40, 60, 40, 60)
        card_layout.setSpacing(20)
        card_layout.setAlignment(Qt.AlignCenter)
        
        # 1. Title "BLOOM"
        bloom_title = QLabel("Bloom")
        bloom_title.setStyleSheet(f"color: {ACCENT_PINK}; font-family: 'Georgia', serif; font-size: 60px; font-style: italic;")
        bloom_title.setAlignment(Qt.AlignCenter)
        card_layout.addWidget(bloom_title)
        
        # 2. Title "PHOTOBOOTH"
        pb_title = QLabel("PHOTOBOOTH")
        pb_title.setStyleSheet(f"color: {ACCENT_PINK}; font-family: 'Verdana'; font-size: 24px; letter-spacing: 5px; font-weight: bold;")
        pb_title.setAlignment(Qt.AlignCenter)
        card_layout.addWidget(pb_title)
        
        card_layout.addSpacing(20)
        
        # 3. Camera Preview Area
        self.welcome_camera_label = QLabel("Loading Camera...")
        self.welcome_camera_label.setFixedSize(350, 280)
        self.welcome_camera_label.setAlignment(Qt.AlignCenter)
        self.welcome_camera_label.setStyleSheet("""
            background-color: #eee; 
            border-radius: 20px;
            border: 2px solid #fce4ec;
        """)
        self.welcome_camera_label.mousePressEvent = lambda e: self.try_next_camera()
        card_layout.addWidget(self.welcome_camera_label, alignment=Qt.AlignCenter)
        
        card_layout.addStretch()
        
        # 4. Start Button
        self.btn_start_welcome = QPushButton("BẮT ĐẦU CHỤP")
        self.btn_start_welcome.setFixedSize(320, 90)
        self.btn_start_welcome.setStyleSheet(f"""
            QPushButton {{
                background-color: {BUTTON_PINK}; 
                color: white;
                border-radius: 45px; 
                font-size: 24px; 
                font-weight: bold;
            }}
            QPushButton:hover {{
                background-color: #f48fb1;
            }}
            QPushButton:pressed {{
                background-color: #c2185b;
            }}
        """)
        self.btn_start_welcome.clicked.connect(self.go_to_price_select)
        card_layout.addWidget(self.btn_start_welcome, alignment=Qt.AlignCenter)
        
        main_layout.addWidget(right_card)
        
        self.stacked.addWidget(screen)
        self.state = "START"

    def load_camera_config_file(self):
        """Đọc file camera_settings.json."""
        config_path = "camera_settings.json"
        if os.path.exists(config_path):
            try:
                import json
                with open(config_path, 'r') as f:
                    return json.load(f)
            except: pass
        return {}

    def auto_select_camera(self):
        """Tự động tìm camera, ưu tiên cấu hình trong file settings."""
        if hasattr(self, 'camera_timer'): self.camera_timer.stop()
        
        found = False
        config_idx = self.camera_config.get("camera_index")
        use_dshow = self.camera_config.get("use_dshow", True)
        
        # Danh sách index cần thử: ưu tiên index từ config trước
        indices = [1, 2, 0, 3]
        if config_idx is not None:
            if config_idx in indices: indices.remove(config_idx)
            indices.insert(0, config_idx)

        print(f"[CAMERA] Dang tim camera (Thu thu tu: {indices})...")
        
        for idx in indices:
            try:
                # Thử với DSHOW (ưu tiên Windows/Iriun)
                cap_flag = cv2.CAP_DSHOW if use_dshow else 0
                temp_cap = cv2.VideoCapture(idx, cap_flag)
                if not temp_cap.isOpened() and use_dshow:
                    temp_cap = cv2.VideoCapture(idx) # Fallback
                
                if temp_cap.isOpened():
                    temp_cap.read()
                    ret, frame = temp_cap.read()
                    if ret and frame is not None:
                        if self.cap: self.cap.release()
                        self.cap = temp_cap
                        self.current_camera_index = idx
                        
                        # Set resolution from config
                        w = self.camera_config.get("width", 1280)
                        h = self.camera_config.get("height", 720)
                        self.cap.set(cv2.CAP_PROP_FRAME_WIDTH, w)
                        self.cap.set(cv2.CAP_PROP_FRAME_HEIGHT, h)
                        
                        print(f"[OK] Da chon camera index: {idx} ({w}x{h})")
                        found = True
                        break
                temp_cap.release()
            except: pass
        
        if not found:
            print("[WARNING] Khong tim thay camera nao hoat dong!")
            if not self.cap or not self.cap.isOpened():
                self.current_camera_index = 0
                self.cap = cv2.VideoCapture(0)
        
        if hasattr(self, 'camera_timer'): self.camera_timer.start(30)

    def try_next_camera(self):
        """Chuyển sang camera index tiếp theo (thủ công khi chọn)."""
        if hasattr(self, 'camera_timer'): self.camera_timer.stop()
        print(f"[SWITCH] Dang doi camera tu index {self.current_camera_index}...")
        
        if self.cap:
            self.cap.release()
            
        self.current_camera_index = (self.current_camera_index + 1) % 4
        # Thử với CAP_DSHOW trước
        self.cap = cv2.VideoCapture(self.current_camera_index, cv2.CAP_DSHOW)
        if not self.cap.isOpened():
            self.cap = cv2.VideoCapture(self.current_camera_index)
            
        self.cap.set(cv2.CAP_PROP_FRAME_WIDTH, 1280)
        self.cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 720)
        
        print(f"Now using camera index: {self.current_camera_index}")
        if hasattr(self, 'camera_timer'): self.camera_timer.start(30)

    def update_vertical_scroll(self):
        """Move photo labels vertically to create a looping efekt."""
        spacing = 265
        total_height = 0
        
        # Calculate single set height for each column
        # Simplified: assume all cols have same photo count
        count_per_col = len(self.scrolling_photos) // 3
        col_height = (count_per_col // 3) * spacing # Height of one set
        
        for item in self.scrolling_photos:
            lbl = item['label']
            speed = 1.5 * item['dir']
            item['y'] += speed
            
            # Loop logic
            if item['dir'] > 0: # Moving Down
                if item['y'] > 850: 
                    item['y'] -= (count_per_col * spacing) / 3 * 3 # This is complex because of 3x list
                    # Simpler: just loop within a large range
                    # Let's use a constant based on observed height
                    pass
            
            # Refreshing the logic:
            # If we have N photos tripled (3N total), the set is N * spacing.
            # We want to loop when we pass 1 set.
            N = count_per_col // 3
            set_unit = N * spacing
            
            if item['y'] > 850:
                item['y'] -= set_unit
            elif item['y'] < -300:
                item['y'] += set_unit
                
            lbl.move(0, int(item['y']))
    
    def create_price_select_screen(self):
        """Giữ nguyên màn hình chọn lưới - Không override."""
        # Gọi hàm gốc để tạo màn hình chọn lưới bình thường
        super().create_price_select_screen()
    
    def create_qr_payment_screen(self):
        """Override - Không tạo màn hình QR payment trong free mode."""
        # Tạo màn hình trống để giữ index
        from PyQt5.QtWidgets import QWidget, QLabel, QVBoxLayout
        screen = QWidget()
        layout = QVBoxLayout(screen)
        label = QLabel("Free Mode - Đang chuyển sang chụp ảnh...")
        label.setAlignment(Qt.AlignCenter)
        label.setStyleSheet("color: #00f5d4; font-size: 24px;")
        layout.addWidget(label)
        self.stacked.addWidget(screen)
    
    def select_layout_and_price(self, photo_count, layout_type):
        """Override - Bỏ qua QR payment, chuyển thẳng sang chụp ảnh."""
        print(f"\nFREE MODE - Selected: {photo_count} photos, Layout: {layout_type}")
        
        # Lưu thông tin đã chọn
        self.selected_price_type = photo_count
        self.selected_frame_count = photo_count
        self.layout_type = layout_type
        self.payment_confirmed = True  # Luôn True trong free mode
        
        print(f"Skipping payment - Go to capture screen (Index 3)")
        
        # Chuyển THẲNG sang màn hình chụp ảnh (bỏ qua QR payment)
        self.stacked.setCurrentIndex(3)
        self.start_capture_session()
    
    def start_capture_session(self):
        """Override - Bắt đầu ghi video cùng với việc chụp ảnh."""
        super().start_capture_session()
        self.state = "CAPTURING"
        self.stacked.setCurrentIndex(3) # Cố định index màn hình chụp
        
        # Khởi tạo VideoWriter
        try:
            timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
            output_folder = r"D:\picture"
            os.makedirs(output_folder, exist_ok=True)
            self.current_video_path = os.path.join(output_folder, f"video_{timestamp}.mp4")
            
            # FPS khoảng 20, độ phân giải HD
            fourcc = cv2.VideoWriter_fourcc(*'mp4v')
            self.video_writer = cv2.VideoWriter(self.current_video_path, fourcc, 20.0, (1280, 720))
            self.is_recording_video = True
            print(f"[VIDEO] Bat dau ghi video: {self.current_video_path}")
        except Exception as e:
            print(f"[ERROR] Loi khoi tao video: {e}")

    def go_to_photo_select(self):
        """Override - Dừng ghi video khi chụp xong."""
        if self.is_recording_video and self.video_writer:
            self.is_recording_video = False
            self.video_writer.release()
            self.video_writer = None
            print("[VIDEO] Da dung ghi video.")
        super().go_to_photo_select()

    def update_camera_frame(self):
        """Override - Ghi frame vào video nếu đang ghi."""
        try:
            # Luôn đọc frame nếu đang ở các state cần camera
            if self.state in ["START", "CAPTURING", "WAITING_CAPTURE"]:
                if self.cap is None or not self.cap.isOpened():
                    # Thử khởi tạo lại camera sau mỗi 3 giây nếu mất kết nối
                    if not hasattr(self, '_last_camera_retry'): self._last_camera_retry = 0
                    if datetime.datetime.now().timestamp() - self._last_camera_retry > 3:
                        print("[CAMERA] Dang thu ket noi lai camera...")
                        self.auto_select_camera()
                        self._last_camera_retry = datetime.datetime.now().timestamp()
                    return

                ret, frame = self.cap.read()
                if ret and frame is not None:
                    frame = cv2.flip(frame, 1)
                    self.current_frame = frame.copy()
                    
                    # Ghi vào video nếu đang trong phiên chụp
                    if self.is_recording_video and self.video_writer:
                        try:
                            # Resize để đảm bảo đúng kích thước video
                            v_frame = cv2.resize(frame, (1280, 720))
                            self.video_writer.write(v_frame)
                        except Exception as ve:
                            print(f"[WARNING] Loi ghi video: {ve}")

                    qt_img = convert_cv_qt(frame)
                    
                    # Cập nhật cho màn hình welcome (START)
                    if self.state == "START" and hasattr(self, 'welcome_camera_label'):
                        scaled = qt_img.scaled(self.welcome_camera_label.size(), Qt.KeepAspectRatioByExpanding, Qt.SmoothTransformation)
                        self.welcome_camera_label.setPixmap(scaled)
                    
                    # Cập nhật cho màn hình capture (CAPTURING/WAITING_CAPTURE)
                    elif self.state in ["CAPTURING", "WAITING_CAPTURE"] and hasattr(self, 'camera_label'):
                        scaled = qt_img.scaled(self.camera_label.size(), Qt.KeepAspectRatio, Qt.SmoothTransformation)
                        self.camera_label.setPixmap(scaled)
                    
                    # Reset fail count if successful
                    self._read_fail_count = 0
                else:
                    # Nếu read() thất bại dù cap.isOpened() là True
                    if not hasattr(self, '_read_fail_count'): self._read_fail_count = 0
                    self._read_fail_count += 1
                    if self._read_fail_count > 30: # ~1 giây liên tục lỗi
                        print("[WARNING] Camera bi treo hoac mat tin hieu, dang khoi dong lai...")
                        self.auto_select_camera()
                        self._read_fail_count = 0
        except Exception as e:
            print(f"[WARNING] Loi trong update_camera_frame: {e}")

    def accept_and_print(self):
        """Override - Hiển thị QR cho cả ảnh và video."""
        self.template_timer.stop()
        if self.merged_image is None: return

        output_folder = r"D:\picture"
        os.makedirs(output_folder, exist_ok=True)
        
        timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
        filepath = os.path.join(output_folder, f"photo_{timestamp}.jpg")
        
        try:
            cv2.imwrite(filepath, self.merged_image)
            
            # Sử dụng Dialog DUY NHẤT 1 mã QR
            dialog = DownloadSingleQRDialog(filepath, self.current_video_path, self)
            dialog.exec_()
            
            self.reset_all()
        except Exception as e:
            QMessageBox.critical(self, "Lỗi", f"Không thể lưu kết quả: {e}")

    def on_price_2_clicked(self):
        """Override - Không dùng trong free mode."""
        pass
    
    def on_price_4_clicked(self):
        """Override - Không dùng trong free mode."""
        pass
    
    def show_qr_payment(self):
        """Override - Bỏ qua QR payment, chuyển thẳng sang chụp."""
        self.start_capture_session()
    
    def on_payment_received(self):
        """Override - Không cần kiểm tra thanh toán."""
        pass

    def on_payment_error(self, error_msg):
        """Override - Không có lỗi thanh toán trong free mode."""
        pass

    def reset_all(self):
        """Override - Xóa thông tin video cũ."""
        super().reset_all()
        self.current_video_path = None


def main():
    """Entry point cho chế độ FREE."""
    
    # Banner
    print("\n" + "="*60)
    print("PHOTOBOOTH - FREE MODE")
    print("="*60)
    print("- No payment required")
    print("- Click 'Start' to capture")
    print("- Default: 4 photos")
    print("="*60 + "\n")
    
    # Tạo QApplication
    app = QApplication(sys.argv)
    
    # Đảm bảo thư mục tồn tại
    ensure_directories()
    
    # Load config (vẫn cần cho Cloudinary, camera, etc.)
    if not load_config():
        msg = QMessageBox()
        msg.setIcon(QMessageBox.Warning)
        msg.setWindowTitle("Thiếu cấu hình")
        msg.setText("Không tìm thấy file config.json")
        msg.setInformativeText(
            "Vui lòng tạo file config.json theo mẫu config.example.json\n\n"
            "Lưu ý: Chế độ FREE vẫn cần config cho:\n"
            "- Cloudinary upload\n"
            "- Camera settings\n"
            "- Các cấu hình khác"
        )
        msg.setStandardButtons(QMessageBox.Ok)
        msg.exec_()
        return 1
    
    # Tạo và hiển thị cửa sổ FREE MODE
    window = FreePhotobooth()
    window.show()
    
    # Chạy app
    return app.exec_()


def handle_exception(exc_type, exc_value, exc_traceback):
    """Bắt các lỗi chưa được xử lý để tránh app tự tắt đột ngột."""
    if issubclass(exc_type, KeyboardInterrupt):
        sys.__excepthook__(exc_type, exc_value, exc_traceback)
        return
    
    error_msg = "".join(traceback.format_exception(exc_type, exc_value, exc_traceback))
    print(f"[CRITICAL ERROR]\n{error_msg}")
    
    # Hiển thị thông báo lỗi cho người dùng
    msg = QMessageBox()
    msg.setIcon(QMessageBox.Critical)
    msg.setWindowTitle("Lỗi Hệ Thống")
    msg.setText("Ứng dụng gặp lỗi và cần khởi động lại.")
    msg.setInformativeText(str(exc_value))
    msg.setDetailedText(error_msg)
    msg.setStandardButtons(QMessageBox.Ok)
    msg.exec_()
    sys.exit(1)

import traceback
sys.excepthook = handle_exception

if __name__ == "__main__":
    sys.exit(main())
