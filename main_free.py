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
from configs import load_config, SAMPLE_PHOTOS_DIR, CAMERA_INDEX, OUTPUT_DIR, FIRST_PHOTO_DELAY, PHOTOS_TO_TAKE
from utils import ensure_directories, convert_cv_qt, load_sample_photos
from main_app import PhotoboothApp
from ui_components import DownloadSingleQRDialog


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
        
        # Mặc định thử index 0, sau đó 1, 2 để tìm camera vật lý
        self.current_camera_index = 0
        
        # Gọi constructor của class cha
        super().__init__()
        
        # Thử tìm camera vật lý (thường laptop camera là 0 hoặc 1, Iriun thường chiếm 0)
        # Chúng ta sẽ thử khởi tạo lại nếu thấy Iriun, nhưng đơn giản nhất là cho phép đổi
        self.try_next_camera()
        
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
        """Redesign welcome screen: Samples on Left (Scrolling), UI on Right."""
        screen = QWidget()
        
        # Set Topographic Background for the UI side
        if os.path.exists("topo_bg.png"):
            bg_pixmap = QPixmap("topo_bg.png")
            palette = QPalette()
            palette.setBrush(QPalette.Window, QBrush(bg_pixmap.scaled(1200, 800, Qt.IgnoreAspectRatio, Qt.SmoothTransformation)))
            screen.setPalette(palette)
            screen.setAutoFillBackground(True)
        else:
            screen.setStyleSheet("background-color: #f4f7f6;")

        main_layout = QHBoxLayout(screen)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)
        
        # SAGE GREEN COLOR: #709a8a
        SAGE_STYLE = "background-color: #709a8a; color: white; border-radius: 40px;"

        # ===== LEFT SIDE (PHOTO SAMPLES) - Vertical Scrolling =====
        collage_container = QFrame()
        collage_container.setStyleSheet("background-color: #709a8a;")
        collage_layout = QHBoxLayout(collage_container)
        collage_layout.setSpacing(15)
        collage_layout.setContentsMargins(40, 0, 40, 0)
        
        # Get photos
        photos = load_sample_photos()
        if not photos:
            photos = [] 
            
        # We'll use a timer to move these labels
        self.scrolling_photos = []
        
        # Create 3 scrolling columns
        for col_idx in range(3):
            col_container = QWidget()
            col_container.setFixedWidth(160)
            
            # Sub-list of photos for this column
            col_photos = [photos[i] for i in range(len(photos)) if i % 3 == col_idx]
            # Triple the list to ensure smooth looping
            col_photos = col_photos * 3
            
            y_offset = (col_idx * 150) % 600 # Stagger start
            direction = 1 if col_idx != 1 else -1 # Middle column goes down, others up
            
            for p_path in col_photos:
                photo_lbl = QLabel(col_container)
                pix = QPixmap(p_path)
                if not pix.isNull():
                    photo_lbl.setPixmap(pix.scaled(160, 240, Qt.KeepAspectRatioByExpanding, Qt.SmoothTransformation))
                photo_lbl.setFixedSize(160, 240)
                photo_lbl.setStyleSheet("border-radius: 20px; background-color: #ddd;")
                
                # Store scrolling info
                self.scrolling_photos.append({
                    'label': photo_lbl,
                    'y': y_offset,
                    'x': 0,
                    'dir': direction,
                    'col': col_idx
                })
                y_offset += 265 # 240 height + 25 spacing
            
            collage_layout.addWidget(col_container)

        # Timer for vertical scrolling
        self.scroll_timer = QTimer(self)
        self.scroll_timer.timeout.connect(self.update_vertical_scroll)
        self.scroll_timer.start(30)
        
        main_layout.addWidget(collage_container, stretch=1)

        # ===== RIGHT SIDE (CAMERA & UI) =====
        right_ui_panel = QWidget()
        right_ui_layout = QVBoxLayout(right_ui_panel)
        right_ui_layout.setSpacing(25)
        right_ui_layout.setContentsMargins(50, 50, 50, 50)
        right_ui_layout.setAlignment(Qt.AlignCenter)
        
        # 1. Title Box
        title_box = QLabel("QuangAnhDay's Photobooth")
        title_box.setAlignment(Qt.AlignCenter)
        title_box.setFixedHeight(80)
        title_box.setFixedWidth(500)
        title_box.setStyleSheet(SAGE_STYLE + "font-size: 28px; font-weight: bold; border-radius: 40px;")
        right_ui_layout.addWidget(title_box)
        
        # 2. Camera Preview (Large)
        self.welcome_camera_label = QLabel("Đang tải camera...")
        self.welcome_camera_label.setAlignment(Qt.AlignCenter)
        self.welcome_camera_label.setFixedSize(540, 420)
        self.welcome_camera_label.setStyleSheet("""
            background-color: #709a8a; 
            border-radius: 40px; 
            border: 8px solid #709a8a;
        """)
        # Cho phép click vào camera để đổi index (tính năng ẩn)
        self.welcome_camera_label.mousePressEvent = lambda e: self.try_next_camera()
        right_ui_layout.addWidget(self.welcome_camera_label)
        
        # 3. Start Button
        self.btn_start_welcome = QPushButton("Bấm để bắt đầu chụp")
        self.btn_start_welcome.setFixedSize(450, 110)
        self.btn_start_welcome.setStyleSheet("""
            QPushButton {
                background-color: #709a8a; 
                color: white;
                border-radius: 55px; 
                font-size: 30px; 
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #84af9f;
            }
            QPushButton:pressed {
                background-color: #5d8476;
            }
        """)
        self.btn_start_welcome.clicked.connect(self.go_to_price_select)
        right_ui_layout.addWidget(self.btn_start_welcome)
        
        # 4. Login Link
        login_label = QLabel("Don't have an account? <span style='color: #709a8a; font-weight: bold;'>Log in</span>")
        login_label.setAlignment(Qt.AlignCenter)
        login_label.setStyleSheet("color: #999; font-size: 18px;")
        right_ui_layout.addWidget(login_label)
        
        main_layout.addWidget(right_ui_panel, stretch=1)
        
        self.stacked.addWidget(screen)
        self.state = "START"

    def try_next_camera(self):
        """Thử camera index tiếp theo (0 -> 1 -> 2 -> 0)."""
        print(f"Switching from camera {self.current_camera_index}...")
        if self.cap:
            self.cap.release()
            
        self.current_camera_index = (self.current_camera_index + 1) % 3
        self.cap = cv2.VideoCapture(self.current_camera_index)
        self.cap.set(cv2.CAP_PROP_FRAME_WIDTH, 1280)
        self.cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 720)
        
        if not self.cap.isOpened():
            # Nếu 1 hoặc 2 không được, về 0
            self.current_camera_index = 0
            self.cap = cv2.VideoCapture(0)
        
        print(f"Now using camera index: {self.current_camera_index}")

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
            print(f"🎬 Bắt đầu ghi video: {self.current_video_path}")
        except Exception as e:
            print(f"❌ Lỗi khởi tạo video: {e}")

    def go_to_photo_select(self):
        """Override - Dừng ghi video khi chụp xong."""
        if self.is_recording_video and self.video_writer:
            self.is_recording_video = False
            self.video_writer.release()
            self.video_writer = None
            print("🎬 Đã dừng ghi video.")
        super().go_to_photo_select()

    def update_camera_frame(self):
        """Override - Ghi frame vào video nếu đang ghi."""
        # Luôn đọc frame nếu đang ở các state cần camera
        if self.state in ["START", "CAPTURING", "WAITING_CAPTURE"]:
            ret, frame = self.cap.read()
            if ret:
                frame = cv2.flip(frame, 1)
                self.current_frame = frame.copy()
                
                # Ghi vào video nếu đang trong phiên chụp
                if self.is_recording_video and self.video_writer:
                    # Resize để đảm bảo đúng kích thước video
                    v_frame = cv2.resize(frame, (1280, 720))
                    self.video_writer.write(v_frame)

                qt_img = convert_cv_qt(frame)
                
                # Cập nhật cho màn hình welcome (START)
                if self.state == "START" and hasattr(self, 'welcome_camera_label'):
                    scaled = qt_img.scaled(self.welcome_camera_label.size(), Qt.KeepAspectRatioByExpanding, Qt.SmoothTransformation)
                    self.welcome_camera_label.setPixmap(scaled)
                
                # Cập nhật cho màn hình capture (CAPTURING/WAITING_CAPTURE)
                elif self.state in ["CAPTURING", "WAITING_CAPTURE"] and hasattr(self, 'camera_label'):
                    scaled = qt_img.scaled(self.camera_label.size(), Qt.KeepAspectRatio, Qt.SmoothTransformation)
                    self.camera_label.setPixmap(scaled)

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


if __name__ == "__main__":
    sys.exit(main())
