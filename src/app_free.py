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
from src.shared.utils.helpers import ensure_directories, convert_cv_qt, load_sample_photos
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

        # Cache cho layout và rotation (để tối ưu update_camera_frame)
        self._cached_layout_type = None
        self._cached_rotation = 0

        print("\n" + "=" * 60)
        print("FREE MODE ACTIVATED")
        print("=" * 60)

    def create_welcome_screen(self):
        """Sử dụng thiết kế HomeScreen mới."""
        self.home_screen = HomeScreen(self)
        
        # Sử dụng capture có sẵn nếu có
        if hasattr(self, 'cap') and self.cap:
            self.home_screen.camera_view.set_capture(self.cap)
        
        # Kết nối các tín hiệu
        self.home_screen.start_clicked.connect(self.go_to_price_select)
        self.home_screen.open_admin.connect(lambda: self.stacked.setCurrentIndex(8))
        
        # Thêm vào stacked widget
        self.stacked.addWidget(self.home_screen)
        self.state = "START"

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

        # Kiểm tra nếu config là URL (digiCamControl)
        if isinstance(config_idx, str) and config_idx.startswith("http"):
            self.cap = cv2.VideoCapture(config_idx)
            if self.cap.isOpened():
                print(f"[OK] Free Mode: DSLR URL connected: {config_idx}")
                found = True
                self.current_camera_index = config_idx

        if not found:
            indices = [1, 2, 0, 3]
            if isinstance(config_idx, int) and config_idx in indices:
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

        # Nếu đang dùng URL, thì next sẽ là Webcam 0
        if isinstance(self.current_camera_index, str):
            self.current_camera_index = 0
        else:
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

    def start_capture_session(self):
        """Override - Bắt đầu ghi video."""
        super().start_capture_session()
        self.state = "CAPTURING"
        self.stacked.setCurrentIndex(3)

        try:
            timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
            output_folder = r"D:\picture"
            os.makedirs(output_folder, exist_ok=True)
            self.current_video_path = os.path.join(output_folder, f"video_{timestamp}.mp4")

            fourcc = cv2.VideoWriter_fourcc(*'mp4v')
            self.video_writer = cv2.VideoWriter(self.current_video_path, fourcc, 20.0, (1280, 720))
            self.is_recording_video = True
        except Exception as e:
            print(f"[ERROR] Loi khoi tao video: {e}")

    def go_to_photo_select(self):
        """Override - Dừng ghi video."""
        if self.is_recording_video and self.video_writer:
            self.is_recording_video = False
            self.video_writer.release()
            self.video_writer = None
        super().go_to_photo_select()

    def update_camera_frame(self):
        """Override - Cập nhật frame camera cho Free Mode."""
        try:
            if self.state in ["START", "CAPTURING", "WAITING_CAPTURE", "INTERACTIVE_CAPTURE"]:
                if self.cap is None or not self.cap.isOpened():
                    # Nếu camera chưa mở, thử mở lại dựa trên config
                    return

                ret, frame = self.cap.read()
                if ret and frame is not None:
                    # Chỉ lấy cấu hình nếu layout thay đổi (để tối ưu)
                    curr_layout = getattr(self, 'layout_type', '4x1')
                    if curr_layout != self._cached_layout_type:
                        from src.shared.types.models import get_layout_config
                        l_cfg = get_layout_config(curr_layout)
                        self._cached_rotation = l_cfg.get("rotation", 0)
                        self._cached_layout_type = curr_layout

                    # Áp dụng xoay
                    if self._cached_rotation == 90:
                        frame = cv2.rotate(frame, cv2.ROTATE_90_CLOCKWISE)
                    elif self._cached_rotation == 180:
                        frame = cv2.rotate(frame, cv2.ROTATE_180)
                    elif self._cached_rotation == 270:
                        frame = cv2.rotate(frame, cv2.ROTATE_90_COUNTERCLOCKWISE)

                    frame = cv2.flip(frame, 1)
                    self.current_frame = frame.copy()

                    if self.is_recording_video and self.video_writer:
                        try:
                            # Tự lấy kích thước video từ frame
                            fh, fw = frame.shape[:2]
                            v_frame = cv2.resize(frame, (1280, 720))
                            self.video_writer.write(v_frame)
                        except Exception as ve:
                            print(f"[WARNING] Loi ghi video: {ve}")

                    qt_img = convert_cv_qt(frame)

                    if self.state == "START" and hasattr(self, 'home_screen'):
                        self.home_screen.camera_view.display_frame(qt_img)
                    elif self.state in ["CAPTURING", "WAITING_CAPTURE"] and hasattr(self, 'camera_label'):
                        scaled = qt_img.scaled(self.camera_label.size(),
                                               Qt.KeepAspectRatio, Qt.SmoothTransformation)
                        self.camera_label.setPixmap(scaled)
                    elif self.state == "INTERACTIVE_CAPTURE" and hasattr(self, 'interactive_camera_label'):
                        scaled = qt_img.scaled(self.interactive_camera_label.size(),
                                               Qt.KeepAspectRatio, Qt.SmoothTransformation)
                        self.interactive_camera_label.setPixmap(scaled)

                    self._read_fail_count = 0
                else:
                    if not hasattr(self, '_read_fail_count'):
                        self._read_fail_count = 0
                    self._read_fail_count += 1
                    if self._read_fail_count > 60: # 2 giây mất hình
                        print("[CAMERA] Thu ket noi lai DSLR/Webcam...")
                        # Thử mở lại bằng index hiện tại
                        self.cap.release()
                        self.cap = cv2.VideoCapture(self.current_camera_index)
                        self._read_fail_count = 0
        except Exception as e:
            print(f"[WARNING] Loi trong update_camera_frame: {e}")

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
