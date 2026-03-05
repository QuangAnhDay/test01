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
from PyQt5.QtGui import QPixmap, QFont

from src.shared.types.models import load_config, FIRST_PHOTO_DELAY, PHOTOS_TO_TAKE
from src.shared.utils.helpers import ensure_directories, convert_cv_qt, load_sample_photos, get_rounded_pixmap
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
        self.video_writer = None
        self.current_video_path = None

        # Đọc cấu hình camera
        self.camera_config = self._load_camera_config_file()
        self.current_camera_index = self.camera_config.get("camera_index", 0)

        # Gọi constructor cha
        super().__init__()

        # Tự động chọn camera (sẽ được HomeScreen sử dụng hoặc ghi đè)
        # self.auto_select_camera()

        self.setWindowTitle("🎉 Photobooth - MIỄN PHÍ")
        self.selected_price_type = 4
        self.selected_frame_count = 4
        self.payment_confirmed = True

        # Ghi đè kết nối nút START của HomeScreen để bỏ qua các bước chọn gói/mẫu
        if hasattr(self, 'home_screen'):
            try:
                self.home_screen.start_clicked.disconnect()
            except:
                pass
            self.home_screen.start_clicked.connect(self.go_to_capture_fast)

        print("\n" + "=" * 60)
        print("FREE MODE ACTIVATED")
        print("=" * 60)

    def _load_camera_config_file(self):
        """Đọc file camera_settings.json."""
        config_path = "camera_settings.json"
        if os.path.exists(config_path):
            try:
                import json
                with open(config_path, 'r') as f:
                    return json.load(f)
            except:
                pass
        return {}

    def auto_select_camera(self):
        """Tự động tìm camera."""
        if hasattr(self, 'camera_timer'):
            self.camera_timer.stop()

        found = False
        config_idx = self.camera_config.get("camera_index")
        use_dshow = self.camera_config.get("use_dshow", True)

        indices = [1, 2, 0, 3]
        if config_idx is not None:
            if config_idx in indices:
                indices.remove(config_idx)
            indices.insert(0, config_idx)

        for idx in indices:
            try:
                cap_flag = cv2.CAP_DSHOW if use_dshow else 0
                temp_cap = cv2.VideoCapture(idx, cap_flag)
                if not temp_cap.isOpened() and use_dshow:
                    temp_cap = cv2.VideoCapture(idx)

                if temp_cap.isOpened():
                    temp_cap.read()
                    ret, frame = temp_cap.read()
                    if ret and frame is not None:
                        if self.cap:
                            self.cap.release()
                        self.cap = temp_cap
                        self.current_camera_index = idx
                        w = self.camera_config.get("width", 1280)
                        h = self.camera_config.get("height", 720)
                        self.cap.set(cv2.CAP_PROP_FRAME_WIDTH, w)
                        self.cap.set(cv2.CAP_PROP_FRAME_HEIGHT, h)
                        found = True
                        break
                temp_cap.release()
            except:
                pass

        if not found:
            if not self.cap or not self.cap.isOpened():
                self.cap = cv2.VideoCapture(0)

        if hasattr(self, 'camera_timer'):
            self.camera_timer.start(30)

    def try_next_camera(self):
        """Chuyển camera tiếp theo."""
        if hasattr(self, 'camera_timer'):
            self.camera_timer.stop()
        if self.cap:
            self.cap.release()
        self.current_camera_index = (self.current_camera_index + 1) % 4
        self.cap = cv2.VideoCapture(self.current_camera_index, cv2.CAP_DSHOW)
        if not self.cap.isOpened():
            self.cap = cv2.VideoCapture(self.current_camera_index)
        self.cap.set(cv2.CAP_PROP_FRAME_WIDTH, 1280)
        self.cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 720)
        if hasattr(self, 'camera_timer'):
            self.camera_timer.start(30)

    def create_qr_payment_screen(self):
        """Override - Không tạo màn hình QR payment."""
        screen = QWidget()
        layout = QVBoxLayout(screen)
        label = QLabel("Free Mode - Đang chuyển sang chụp ảnh...")
        label.setAlignment(Qt.AlignCenter)
        label.setStyleSheet("color: #00f5d4; font-size: 24px;")
        layout.addWidget(label)
        self.stacked.addWidget(screen)

    # select_layout_and_price ĐÃ ĐƯỢC DÙNG CHUNG TỪ app.py

    def go_to_capture_fast(self):
        """Bỏ qua chọn layout/template, dùng mặc định và chụp luôn (Step 9)."""
        from src.shared.types.models import get_all_layouts, get_layout_config
        from src.modules.image_processing.processor import load_templates_for_layout
        
        # 1. Tìm layout group 'vertical'
        all_layouts = get_all_layouts()
        target_layout = "4x1" # Mặc định
        
        # Thử tìm các layout Custom đã được gán group 'vertical'
        vertical_layouts = [k for k, v in all_layouts.items() if v.get("group") == "vertical"]
        if vertical_layouts:
            target_layout = vertical_layouts[0]
            
        cfg = get_layout_config(target_layout)
        
        # 2. Xác định slot count
        if "SLOTS" in cfg:
            slot_count = len(cfg["SLOTS"])
        else:
            slot_count = 4 
            
        # 3. Tìm template đầu tiên trong folder tương ứng
        templates = load_templates_for_layout(target_layout, slot_count)
        
        # 4. Gán thông số
        self.layout_type = target_layout
        self.selected_frame_count = slot_count
        self.selected_price_type = slot_count
        self.selected_template_path = templates[0] if templates else None
        
        print(f"[FREE MODE] Fast Start: Layout={target_layout}, Slots={slot_count}, Template={self.selected_template_path}")
        
        # 5. Khởi tạo trạng thái chụp tương tác (Từng pô - Step 9)
        self.current_slot_index = 0
        self.interactive_photos = []
        self.state = "INTERACTIVE_CAPTURE"
        self.stacked.setCurrentIndex(9)
        
        # 6. BẮT ĐẦU GHI VIDEO từ lúc nhấn START
        self._start_video_recording()
        
        # Cập nhật UI cho Step 9
        if hasattr(self, 'update_interactive_template_preview'):
            self.update_interactive_template_preview()
        if hasattr(self, 'update_interactive_button_text'):
            self.update_interactive_button_text()
            # Cập nhật text nút bấm để người dùng biết cần bấm để bắt đầu
            if hasattr(self, 'btn_capture_step'):
                self.btn_capture_step.setText(f"📸 BẤM ĐỂ CHỤP [1/{slot_count}]")

    def start_interactive_shot(self):
        """Bắt đầu Countdown để chụp 1 tấm (Tăng lên 10 giây)."""
        self.countdown_val = 3
        self.interactive_countdown_label.setText(str(self.countdown_val))
        self.timer_shot = QTimer()
        self.timer_shot.timeout.connect(self.interactive_countdown_tick)
        self.timer_shot.start(1000)
        if hasattr(self, 'btn_capture_step'):
            self.btn_capture_step.setEnabled(False)

    def _start_video_recording(self):
        """Khởi tạo VideoWriter để ghi video quá trình chụp."""
        try:
            # Dừng ghi video cũ (nếu có)
            self._stop_video_recording()

            timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
            output_folder = r"D:\picture"
            os.makedirs(output_folder, exist_ok=True)
            self.current_video_path = os.path.join(output_folder, f"video_{timestamp}.mp4")

            fourcc = cv2.VideoWriter_fourcc(*'mp4v')
            self.video_writer = cv2.VideoWriter(self.current_video_path, fourcc, 20.0, (1280, 720))
            self.is_recording_video = True
            print(f"[VIDEO] Bắt đầu ghi video: {self.current_video_path}")
        except Exception as e:
            print(f"[ERROR] Lỗi khởi tạo video: {e}")
            self.is_recording_video = False

    def _stop_video_recording(self):
        """Dừng ghi video và giải phóng VideoWriter."""
        if self.is_recording_video and self.video_writer:
            self.is_recording_video = False
            self.video_writer.release()
            self.video_writer = None
            print(f"[VIDEO] Đã dừng ghi video: {self.current_video_path}")

    def start_capture_session(self):
        """Override - Bắt đầu ghi video (luồng cũ, giữ tương thích)."""
        super().start_capture_session()
        self.state = "CAPTURING"
        self.stacked.setCurrentIndex(3)
        self._start_video_recording()

    def go_to_photo_select(self):
        """Override - Dừng ghi video."""
        self._stop_video_recording()
        super().go_to_photo_select()

    def update_camera_frame(self):
        """Override - Ghi frame vào video nếu đang ghi."""
        try:
            if self.state in ["START", "CAPTURING", "WAITING_CAPTURE", "INTERACTIVE_CAPTURE"]:
                if self.cap is None or not self.cap.isOpened():
                    if not hasattr(self, '_last_camera_retry'):
                        self._last_camera_retry = 0
                    if datetime.datetime.now().timestamp() - self._last_camera_retry > 3:
                        self.auto_select_camera()
                        self._last_camera_retry = datetime.datetime.now().timestamp()
                    return

                ret, frame = self.cap.read()
                if ret and frame is not None:
                    frame = cv2.flip(frame, 1)
                    self.current_frame = frame.copy()

                    if self.is_recording_video and self.video_writer:
                        try:
                            v_frame = cv2.resize(frame, (1280, 720))
                            self.video_writer.write(v_frame)
                        except Exception as ve:
                            print(f"[WARNING] Loi ghi video: {ve}")

                    qt_img = convert_cv_qt(frame)

                    if self.state == "START" and hasattr(self, 'home_screen'):
                        # Nếu đang ở Home, để HomeScreen tự cập nhật qua CameraView của nó
                        # hoặc ta có thể chủ động cập nhật label của HomeScreen nếu muốn dùng chung cap
                        pass
                    elif self.state in ["CAPTURING", "WAITING_CAPTURE"] and hasattr(self, 'camera_label'):
                        scaled = qt_img.scaled(self.camera_label.size(),
                                               Qt.KeepAspectRatio, Qt.SmoothTransformation)
                        self.camera_label.setPixmap(scaled)
                    elif self.state == "INTERACTIVE_CAPTURE" and hasattr(self, 'interactive_camera_label'):
                        scaled = qt_img.scaled(self.interactive_camera_label.size(),
                                               Qt.KeepAspectRatio, Qt.SmoothTransformation)
                        rounded = get_rounded_pixmap(scaled, radius=30)
                        self.interactive_camera_label.setPixmap(rounded)

                    self._read_fail_count = 0
                else:
                    if not hasattr(self, '_read_fail_count'):
                        self._read_fail_count = 0
                    self._read_fail_count += 1
                    if self._read_fail_count > 30:
                        self.auto_select_camera()
                        self._read_fail_count = 0
        except Exception as e:
            print(f"[WARNING] Loi trong update_camera_frame: {e}")

    def accept_and_print(self):
        """Override - Dừng ghi video, lưu ảnh, hiển thị QR cho cả ảnh và video."""
        self.template_timer.stop()
        
        # DỪNG GHI VIDEO khi nhấn "LẤY ẢNH"
        self._stop_video_recording()
        
        # Dùng merged_image nếu có, nếu không dùng collage_image (từ interactive capture)
        final_image = self.merged_image if self.merged_image is not None else self.collage_image
        if final_image is None:
            return
        self.merged_image = final_image

        output_folder = r"D:\picture"
        os.makedirs(output_folder, exist_ok=True)
        timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
        filepath = os.path.join(output_folder, f"photo_{timestamp}.jpg")

        try:
            cv2.imwrite(filepath, self.merged_image)
            print(f"[FREE MODE] Ảnh đã lưu: {filepath}")
            print(f"[FREE MODE] Video đã lưu: {self.current_video_path}")
            dialog = DownloadSingleQRDialog(filepath, self.current_video_path, self)
            dialog.exec_()
            self.reset_all()
        except Exception as e:
            QMessageBox.critical(self, "Lỗi", f"Không thể lưu kết quả: {e}")

    def reset_all(self):
        # Đảm bảo video đã dừng trước khi reset
        self._stop_video_recording()
        super().reset_all()
        self.current_video_path = None
        self.is_recording_video = False
        self.video_writer = None


# ==========================================
# ENTRY POINT
# ==========================================

def main():
    """Entry point cho chế độ FREE."""
    print("\n" + "=" * 60)
    print("PHOTOBOOTH - FREE MODE")
    print("=" * 60)

    app = QApplication(sys.argv)
    ensure_directories()

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

    window = FreePhotobooth()
    window.showFullScreen()
    return app.exec_()


def handle_exception(exc_type, exc_value, exc_traceback):
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
