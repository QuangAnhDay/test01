# ==========================================
# PHOTOBOOTH - FREE MODE (Không cần thanh toán)
# ==========================================
"""
File chạy ứng dụng Photobooth ở chế độ MIỄN PHÍ.
Bỏ qua hoàn toàn bước chọn giá và thanh toán QR.

CÁCH CHẠY:
    python -m src.app_free     (từ thư mục gốc)
    hoặc: python src/app_free.py
"""

import os
import sys
import cv2
import datetime
import traceback

# === PATH FIX: Cho phép chạy trực tiếp bằng `python src/app_free.py` ===
_PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if _PROJECT_ROOT not in sys.path:
    sys.path.insert(0, _PROJECT_ROOT)

from PyQt5.QtWidgets import (QApplication, QMessageBox, QPushButton, QWidget,
                             QLabel, QVBoxLayout, QHBoxLayout, QFrame, QGridLayout)
from PyQt5.QtCore import Qt, QTimer
from PyQt5.QtGui import QPixmap, QImage, QFont

from src.shared.types.models import load_config, FIRST_PHOTO_DELAY, PHOTOS_TO_TAKE
from src.shared.utils.helpers import ensure_directories, convert_cv_qt, load_sample_photos, get_rounded_pixmap
from src.modules.image_processing.processor import crop_to_aspect_wh
from src.modules.camera.camera_thread import CameraThread
from src.photobooth.components.dialogs import DownloadSingleQRDialog
from src.app import PhotoboothApp
from src.ui.screens.home_screen import HomeScreen


class FreePhotobooth(PhotoboothApp):
    """
    Photobooth miễn phí - Bỏ qua thanh toán.
    Kế thừa từ PhotoboothApp và override workflow.
    """

    def __init__(self):
        # Đặt flag TRƯỚC khi gọi super().__init__()
        self.is_free_mode = True
        self.is_recording_video = False
        self.current_video_path = None

        # Đọc cấu hình camera
        self.camera_config = self._load_camera_config_file()
        self.current_camera_index = self.camera_config.get("camera_index", 0)

        # 1. Khởi tạo và chạy 'Server' Camera ngay lập tức
        self.cam_thread = CameraThread(
            camera_index=self.current_camera_index,
            width=self.camera_config.get("width", 1280),
            height=self.camera_config.get("height", 720),
            use_dshow=self.camera_config.get("use_dshow", True),
            use_compat=self.camera_config.get("use_compat", False)
        )
        self.cam_thread.start()

        # 2. Gọi constructor cha (Sẽ tạo HomeScreen, LiveView...)
        super().__init__()
        
        # 3. Kết nối 'Server' vào màn hình hiện tại
        self.switch_camera_recipient("START")
        
        # Giải phóng camera mặc định (nếu app.py lỡ mở)
        if hasattr(self, 'cap') and self.cap:
             self.cap.release()
             self.cap = None
        
        # Dừng timer camera của bản app.py vì ta dùng Thread
        if hasattr(self, 'camera_timer'):
            self.camera_timer.stop()

        self.setWindowTitle("🎉 Photobooth - MIỄN PHÍ")
        self.selected_price_type = 4
        self.selected_frame_count = 4
        self.payment_confirmed = True

        # Cache cho layout và rotation (để tối ưu update_camera_frame)
        self._cached_layout_type = None
        self._cached_rotation = 0

        print("\n" + "=" * 60)
        print("FREE MODE ACTIVATED")
        print("=" * 60)

    def create_welcome_screen(self):
        """Sử dụng thiết kế HomeScreen mới."""
        self.home_screen = HomeScreen(self)
        
        # Disable CameraView's internal reader thread to avoid resource fighting
        # Cần set TRƯỚC khi Home_Screen start camera ở showEvent
        if hasattr(self.home_screen, 'camera_view') and self.home_screen.camera_view:
            self.home_screen.camera_view.camera_worker.external_cap = True

        # Sử dụng capture có sẵn nếu có
        if hasattr(self, 'cap') and self.cap:
            self.home_screen.camera_view.set_capture(self.cap)
        
        # Kết nối các tín hiệu
        self.home_screen.start_clicked.connect(self.go_to_price_select)
        self.home_screen.open_admin.connect(lambda: self.stacked.setCurrentIndex(8))
        
        # Thêm vào stacked widget
        self.stacked.addWidget(self.home_screen)
        self.state = "START"
        self.switch_camera_recipient("START")

    def _load_camera_config_file(self):
        """Đọc file camera_settings.json."""
        from src.config import CAMERA_SETTINGS_PATH
        config_path = CAMERA_SETTINGS_PATH
        if os.path.exists(config_path):
            try:
                import json
                with open(config_path, 'r') as f:
                    return json.load(f)
            except:
                pass
        return {}

    def auto_select_camera(self):
        """Hàm này hiện không dùng nữa vì dùng CameraThread trực tiếp."""
        pass

    def try_next_camera(self):
        """Chuyển camera tiếp theo (Sử dụng CameraThread)."""
        # Nếu đang dùng URL, thì next sẽ là Webcam 0
        if isinstance(self.current_camera_index, str):
            self.current_camera_index = 0
        else:
            self.current_camera_index = (self.current_camera_index + 1) % 4
            
        self.cam_thread.change_camera(self.current_camera_index)

    def go_to_capture_screen(self):
        """Override - Chuyển sang interactive capture step 9."""
        print("[FREE] Di chuyen den STEP 9 (Interactive)")
        self.state = "INTERACTIVE_CAPTURE"
        self.stacked.setCurrentIndex(9)
        self.switch_camera_recipient("INTERACTIVE_CAPTURE")

    def go_to_price_select(self):
        """Override - Chuyển sang chọn gói (Step 1)."""
        print("[FREE] Di chuyen den STEP 1 (Packages)")
        self.state = "PACKAGE_SELECT"
        if hasattr(self, 'stacked'):
            self.stacked.setCurrentIndex(1)
        self.switch_camera_recipient("NONE")

    def handle_template_confirmation(self):
        """Override - Dành cho bản Free để chuyển recipient camera."""
        super().handle_template_confirmation()
        if self.state == "INTERACTIVE_CAPTURE":
            self.switch_camera_recipient("INTERACTIVE_CAPTURE")

    def start_interactive_shot(self):
        """Override - Bắt đầu Countdown và đảm bảo feed camera Full được bật."""
        self.switch_camera_recipient("INTERACTIVE_CAPTURE")
        super().start_interactive_shot()

    def take_one_photo(self):
        """Override - Chụp ảnh từ Thread thay vì self.cap."""
        if self.cam_thread and self.cam_thread.last_cv_frame is not None:
            frame = self.cam_thread.last_cv_frame.copy()
            # Xử lý tương tự app.py nhưng dùng frame từ thread
            self.interactive_photos.append(frame)
            self.current_slot_index += 1
            self.update_interactive_template_preview()
            self.update_interactive_button_text()
            
            if hasattr(self, 'interactive_stack'):
                self.interactive_stack.setCurrentIndex(0)
            self.interactive_countdown_label.setText("")
        else:
            print("[ERROR] take_one_photo: Khong co frame tu thread!")

    def create_qr_payment_screen(self):
        """Override - Không tạo màn hình QR payment."""
        screen = QWidget()
        layout = QVBoxLayout(screen)
        label = QLabel("Free Mode - Đang chuyển sang chụp ảnh...")
        label.setAlignment(Qt.AlignCenter)
        label.setStyleSheet("font-family: 'Cooper Black'; color: #00f5d4; font-size: 24px;")
        layout.addWidget(label)
        self.stacked.addWidget(screen)

    # select_layout_and_price ĐÃ ĐƯỢC DÙNG CHUNG TỪ app.py

    def start_capture_session(self):
        """Override - Bắt đầu quay video ở luồng phụ."""
        super().start_capture_session()
        self.state = "CAPTURING"
        self.stacked.setCurrentIndex(3)
        self.switch_camera_recipient("CAPTURING") # Chuyển frame feed sang LiveView

        try:
            timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
            output_folder = r"D:\picture"
            if not os.path.exists("D:"):
                output_folder = os.path.join(os.path.expanduser("~"), "Pictures", "Photobooth")
            
            os.makedirs(output_folder, exist_ok=True)
            self.current_video_path = os.path.join(output_folder, f"video_{timestamp}.mp4")

            # Ra lệnh cho thread bắt đầu ghi (Non-blocking)
            self.cam_thread.start_recording(self.current_video_path)
            self.is_recording_video = True
        except Exception as e:
            print(f"[ERROR] Loi khoi tao ghi video: {e}")

    def go_to_photo_select(self):
        """Override - Dừng ghi video ở luồng phụ."""
        self.switch_camera_recipient("NONE") # Ngắt feed camera
        if self.is_recording_video:
            self.cam_thread.stop_recording()
            self.is_recording_video = False
        super().go_to_photo_select()

    def update_camera_frame(self):
        """Hàm này không dùng nữa vì đã dùng signal-based on_frame_received."""
        pass
    
    def switch_camera_recipient(self, state):
        """
        Đăng ký/Hủy đăng ký nhận frame tùy theo state của ứng dụng.
        Đây là 'Server' pattern giúp tối ưu tài nguyên và tránh crash.
        """
        print(f"[CAM_SERVER_DEBUG] Yeu cau chuyen sang: {state}")
        try:
            # 1. Đồng bộ cấu hình Rotation cho CameraThread
            rot = 0
            try:
                curr_layout = getattr(self, 'layout_type', '4x1')
                from src.shared.types.models import get_layout_config
                l_cfg = get_layout_config(curr_layout)
                rot = l_cfg.get("rotation", 0)
                self.cam_thread.rotation = rot
            except:
                pass

            # 2. Ngắt kết nối tất cả trước (An toàn)
            try:
                self.cam_thread.frame_ready.disconnect()
            except:
                pass 
                
            # 3. Đăng ký lại dựa trên state mới
            if state == "START":
                self.cam_thread.frame_ready.connect(self.on_frame_home)
            elif state in ["CAPTURING", "WAITING_CAPTURE"]:
                self.cam_thread.frame_ready.connect(self.on_frame_liveview)
            elif state == "INTERACTIVE_CAPTURE":
                self.cam_thread.frame_ready.connect(self.on_frame_interactive)
            
            print(f"[CAMERA SERVER] Success: Recipient for {state} connected. (Rotation: {rot})")
        except Exception as e:
            print(f"[ERROR] switch_camera_recipient error: {e}")

    def on_frame_home(self, qt_img):
        """Feed cho màn hình HomeScreen - Khôi phục bo góc."""
        if hasattr(self, 'home_screen') and self.home_screen.camera_view:
            lbl = self.home_screen.camera_view.image_label
            if lbl and not lbl.size().isEmpty():
                # Scale ảnh để lấp đầy label (label hiện tại là 720x460 nằm trong khung trắng)
                scaled = qt_img.scaled(lbl.size(), Qt.KeepAspectRatioByExpanding, Qt.SmoothTransformation)
                
                # Chuyển sang pixmap và áp dụng bo góc (radius=19 cho khung đen lọt lòng)
                pixmap = QPixmap.fromImage(scaled)
                rounded_pixmap = get_rounded_pixmap(pixmap, radius=19)
                
                lbl.setPixmap(rounded_pixmap)
                lbl.setVisible(True)

    def on_frame_liveview(self, qt_img):
        """Feed cho màn hình LiveView (Step 3)."""
        if hasattr(self, 'camera_label'):
            scaled = qt_img.scaled(self.camera_label.size(), Qt.KeepAspectRatio, Qt.SmoothTransformation)
            self.camera_label.setPixmap(QPixmap.fromImage(scaled))

    def on_frame_interactive(self, qt_img):
        """Feed cho màn hình Interactive (Step 9) - Đã có Crop để khớp slot."""
        # Update Full Preview (Page 1)
        if hasattr(self, 'interactive_camera_label'):
            lbl_size = self.interactive_camera_label.size()
            if not lbl_size.isEmpty():
                # Lấy tỷ lệ slot hiện tại
                curr_layout = getattr(self, 'layout_type', '4x1')
                from src.shared.types.models import get_layout_config
                cfg = get_layout_config(curr_layout)
                slots = cfg.get("SLOTS", [])
                
                qt_img_display = qt_img
                if slots:
                    sw, sh = slots[0][2], slots[0][3]
                    target_ratio = sw / sh
                    iw, ih = qt_img.width(), qt_img.height()
                    current_ratio = iw / ih
                    if current_ratio > target_ratio:
                        new_w = int(ih * target_ratio)
                        offset = (iw - new_w) // 2
                        qt_img_display = qt_img.copy(offset, 0, new_w, ih)
                    elif current_ratio < target_ratio:
                        new_h = int(iw / target_ratio)
                        offset = (ih - new_h) // 2
                        qt_img_display = qt_img.copy(0, offset, iw, new_h)

                scaled_full = qt_img_display.scaled(lbl_size, Qt.KeepAspectRatioByExpanding, Qt.SmoothTransformation)
                self.interactive_camera_label.setPixmap(QPixmap.fromImage(scaled_full))
                
                # Update Mini Sidebar (Page 0)
                if hasattr(self, 'interactive_camera_mini'):
                    mini_w = self.interactive_camera_mini.width() - 12
                    mini_h = self.interactive_camera_mini.height() - 12
                    if mini_w > 0 and mini_h > 0:
                        mini_scaled_img = qt_img_display.scaled(mini_w, mini_h, Qt.IgnoreAspectRatio, Qt.FastTransformation)
                        mini_pixmap = QPixmap.fromImage(mini_scaled_img)
                        mini_rounded = get_rounded_pixmap(mini_pixmap, radius=20)
                        self.interactive_camera_mini.setPixmap(mini_rounded)

    def on_frame_received(self, qt_img):
        """Legacy handler - Hiện tại switch_camera_recipient sẽ điều hướng luồng này."""
        pass

    def capture_photo(self):
        """Sử dụng frame cuối cùng từ CameraThread để chụp."""
        if self.cam_thread and self.cam_thread.last_cv_frame is not None:
             self.current_frame = self.cam_thread.last_cv_frame.copy()
             super(FreePhotobooth, self).capture_photo()
        else:
             print("[ERROR] Khong co frame de chup!")

    def accept_and_print(self):
        """Override - Hiển thị QR cho cả ảnh và video."""
        self.template_timer.stop()
        
        # ƯU TIÊN collage_image (vì ở Step 9, đây là ảnh đã có cả ảnh chụp & template)
        # Nếu không có (lỗi gì đó) thì mới dùng merged_image
        final_image = self.collage_image if self.collage_image is not None else self.merged_image
        
        if final_image is None:
            QMessageBox.warning(self, "Lỗi", "Không tìm thấy ảnh để lưu!")
            return
            
        self.merged_image = final_image

        output_folder = r"D:\picture"
        os.makedirs(output_folder, exist_ok=True)
        timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
        filepath = os.path.join(output_folder, f"photo_{timestamp}.jpg")

        try:
            cv2.imwrite(filepath, self.merged_image)
            dialog = DownloadSingleQRDialog(filepath, self.current_video_path, self)
            dialog.exec_()
            self.reset_all()
        except Exception as e:
            QMessageBox.critical(self, "Lỗi", f"Không thể lưu kết quả: {e}")

    def reset_all(self):
        super().reset_all()
        self.current_video_path = None
        self.switch_camera_recipient("START")

    def keyPressEvent(self, event):
        """Xử lý phím tắt - Chế độ Admin."""
        # F1: Mở cài đặt camera (Safe version cho Free Mode)
        if event.key() == Qt.Key_F1:
            self.open_camera_setup()
        
        # F5: Reset ứng dụng khẩn cấp
        elif event.key() == Qt.Key_F5:
            print("[ADMIN] Manual Reset requested via F5")
            self.reset_all()

        # Các phím khác (F2: Layout Designer, F3: Admin Dashboard) để super() xử lý
        else:
            super().keyPressEvent(event)

    def open_camera_setup(self):
        """Dừng thread camera chính trước khi mở cửa sổ cài đặt."""
        print("[FREE] Settings requested: Stopping main camera thread...")
        if hasattr(self, 'cam_thread') and self.cam_thread:
            self.switch_camera_recipient("NONE")
            self.cam_thread.stop()
            self.cam_thread = None
        
        from src.admin.pages.settings import CameraSetupApp
        self.camera_setup_window = CameraSetupApp()
        self.camera_setup_window.closeEvent = self._on_setup_closed
        self.camera_setup_window.show()

    def _on_setup_closed(self, event):
        """Khởi động lại camera sau khi đóng cài đặt."""
        print("[FREE] Settings closed. Restarting camera...")
        self.camera_config = self._load_camera_config_file()
        self.current_camera_index = self.camera_config.get("camera_index", 0)

        self.cam_thread = CameraThread(
            camera_index=self.current_camera_index,
            width=self.camera_config.get("width", 1280),
            height=self.camera_config.get("height", 720),
            use_dshow=self.camera_config.get("use_dshow", True),
            use_compat=self.camera_config.get("use_compat", False)
        )
        self.cam_thread.start()
        self.state = "START"
        self.switch_camera_recipient("START")
        event.accept()


# ==========================================
# ENTRY POINT
# ==========================================

def is_cloudinary_valid():
    """Kiểm tra xem thông số Cloudinary đã đầy đủ chưa."""
    from src.shared.types.models import APP_CONFIG
    cloud = APP_CONFIG.get('cloudinary', {})
    return all([cloud.get('cloud_name'), cloud.get('api_key'), cloud.get('api_secret')])


def main():
    """Entry point cho chế độ FREE."""
    print("\n" + "=" * 60)
    print("PHOTOBOOTH - FREE MODE")
    print("=" * 60)

    app = QApplication(sys.argv)
    app.is_free_mode = True
    ensure_directories()

    # 1. Tải cấu hình
    config_loaded = load_config()
    
    # 2. Kiểm tra tính hợp lệ của Cloudinary (Cần thiết cho cả Free/Paid)
    if not config_loaded or not is_cloudinary_valid():
        from src.admin.pages.dashboard import AdminSetup
        
        # Thông báo cho người dùng
        msg = QMessageBox()
        msg.setIcon(QMessageBox.Information)
        msg.setWindowTitle("Cấu hình hệ thống")
        msg.setText("Chào mừng! Hệ thống phát hiện bạn chưa cấu hình thông số Cloudinary.")
        msg.setInformativeText(
            "Vui lòng nhập 'Cloud Name', 'API Key' và 'API Secret' trong mục 'API KEYS & CLOUD' "
            "để ứng dụng có thể upload và trả ảnh qua QR Code.\n\n"
            "Sau khi LƯU, hãy đóng cửa sổ cấu hình để bắt đầu ứng dụng."
        )
        msg.setStandardButtons(QMessageBox.Ok)
        msg.exec_()

        # Hiển thị trang Admin Setup
        admin_win = AdminSetup()
        admin_win.show()
        
        # Chờ người dùng cấu hình xong và đóng cửa sổ
        app.exec_()
        
        # Sau khi đóng, kiểm tra lại
        load_config()
        if not is_cloudinary_valid():
            print("[INFO] Cấu hình vẫn chưa hoàn thiện. Thoát ứng dụng.")
            return 0
        
        # Nếu đã hợp lệ, có thể tiếp tục khởi động FreePhotobooth
        print("[INFO] Cấu hình hợp lệ. Đang khởi động Photobooth...")

    # 3. Khởi động ứng dụng chính
    window = FreePhotobooth()
    window.showFullScreen()
    return app.exec_()


def handle_exception(exc_type, exc_value, exc_traceback):
    if issubclass(exc_type, KeyboardInterrupt):
        sys.__excepthook__(exc_type, exc_value, exc_traceback)
        return
    error_msg = "".join(traceback.format_exception(exc_type, exc_value, exc_traceback))
    print(f"[CRITICAL ERROR]\n{error_msg}")
    
    # Ghi ra file để debug
    try:
        with open("crash_log.txt", "w", encoding="utf-8") as f:
            f.write(error_msg)
    except:
        pass

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
