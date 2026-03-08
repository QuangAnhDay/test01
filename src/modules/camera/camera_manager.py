# ==========================================
# CAMERA MANAGER - Xử lý kết nối, chụp ảnh
# ==========================================
"""
Module quản lý camera: kết nối, chuyển camera, 
đọc frame, đếm ngược, chụp ảnh.
"""

import os
import json
import cv2
import datetime
from PyQt5.QtCore import QTimer

CAMERA_SETTINGS_FILE = "camera_settings.json"


class CameraManager:
    """Quản lý kết nối và điều khiển camera."""

    def __init__(self, default_index=0):
        self.cap = None
        self.current_camera_index = default_index
        self.camera_config = self._load_camera_config()
        self.current_frame = None
        self.is_recording_video = False
        self.video_writer = None
        self.current_video_path = None
        self._read_fail_count = 0
        self._last_camera_retry = 0

    def _load_camera_config(self):
        """Đọc file camera_settings.json."""
        if os.path.exists(CAMERA_SETTINGS_FILE):
            try:
                with open(CAMERA_SETTINGS_FILE, 'r') as f:
                    return json.load(f)
            except:
                pass
        return {"camera_index": 0, "use_dshow": True, "width": 1280, "height": 720}

    def init_camera(self, index=None):
        """Khởi tạo camera với index chỉ định."""
        if index is None:
            index = self.camera_config.get("camera_index", 0)
        
        if self.cap:
            self.cap.release()

        if isinstance(index, str) and index.startswith("http"):
            self.cap = cv2.VideoCapture(index)
            print(f"[CAMERA] Kết nối DSLR qua MJPEG: {index}")
        elif use_dshow and os.name == "nt":
            self.cap = cv2.VideoCapture(index, cv2.CAP_DSHOW)
            if not self.cap.isOpened():
                self.cap = cv2.VideoCapture(index)  # Fallback
        else:
            self.cap = cv2.VideoCapture(index)

        # Chế độ tương thích (Chỉ cho Webcam, không áp dụng cho DSLR URL)
        if not (isinstance(index, str) and index.startswith("http")):
            if use_compat:
                self.cap.set(cv2.CAP_PROP_FOURCC, cv2.VideoWriter_fourcc(*'MJPG'))
                self.cap.set(cv2.CAP_PROP_FRAME_WIDTH, 640)
                self.cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)
            else:
                self.cap.set(cv2.CAP_PROP_FRAME_WIDTH, self.camera_config.get("width", 1280))
                self.cap.set(cv2.CAP_PROP_FRAME_HEIGHT, self.camera_config.get("height", 720))

        self.current_camera_index = index

        # Warmup: Đọc bỏ vài frame đầu
        for _ in range(8):
            self.cap.read()

    def auto_select_camera(self):
        """Tự động tìm camera, ưu tiên cấu hình trong file settings."""
        found = False
        config_idx = self.camera_config.get("camera_index")
        use_dshow = self.camera_config.get("use_dshow", True)

        indices = [1, 2, 0, 3]
        if config_idx is not None:
            if config_idx in indices:
                indices.remove(config_idx)
            indices.insert(0, config_idx)

        print(f"[CAMERA] Dang tim camera (Thu thu tu: {indices})...")

        # Kiểm tra nếu config là URL (digiCamControl)
        if isinstance(config_idx, str) and config_idx.startswith("http"):
            self.cap = cv2.VideoCapture(config_idx)
            if self.cap.isOpened():
                print(f"[OK] Da ket noi DSLR URL: {config_idx}")
                found = True
                self.current_camera_index = config_idx

        if not found:
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

                            print(f"[OK] Da chon camera index: {idx} ({w}x{h})")
                            found = True
                            break
                    temp_cap.release()
                except:
                    pass

        if not found:
            print("[WARNING] Khong tim thay camera nao hoat dong!")
            if not self.cap or not self.cap.isOpened():
                self.current_camera_index = 0
                self.cap = cv2.VideoCapture(0)

    def try_next_camera(self):
        """Chuyển sang camera index tiếp theo (thủ công)."""
        print(f"[SWITCH] Dang doi camera tu index {self.current_camera_index}...")

        if self.cap:
            self.cap.release()

        self.current_camera_index = (self.current_camera_index + 1) % 4
        self.cap = cv2.VideoCapture(self.current_camera_index, cv2.CAP_DSHOW)
        if not self.cap.isOpened():
            self.cap = cv2.VideoCapture(self.current_camera_index)

        self.cap.set(cv2.CAP_PROP_FRAME_WIDTH, 1280)
        self.cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 720)
        print(f"Now using camera index: {self.current_camera_index}")

    def read_frame(self):
        """Đọc một frame từ camera. Trả về (success, frame)."""
        if self.cap is None or not self.cap.isOpened():
            return False, None

        ret, frame = self.cap.read()
        if ret and frame is not None:
            frame = cv2.flip(frame, 1)
            self.current_frame = frame.copy()
            self._read_fail_count = 0
            return True, frame
        else:
            self._read_fail_count += 1
            if self._read_fail_count > 60: # Chờ ~2 giây
                print("[WARNING] Camera mất tín hiệu quá lâu, đang thử tự động chọn lại...")
                self.auto_select_camera()
                self._read_fail_count = 0
            return False, None

    def start_video_recording(self, output_folder=r"D:\picture"):
        """Bắt đầu ghi video."""
        try:
            os.makedirs(output_folder, exist_ok=True)
            timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
            self.current_video_path = os.path.join(output_folder, f"video_{timestamp}.mp4")

            fourcc = cv2.VideoWriter_fourcc(*'mp4v')
            self.video_writer = cv2.VideoWriter(self.current_video_path, fourcc, 20.0, (1280, 720))
            self.is_recording_video = True
            print(f"[VIDEO] Bat dau ghi video: {self.current_video_path}")
        except Exception as e:
            print(f"[ERROR] Loi khoi tao video: {e}")

    def write_video_frame(self, frame):
        """Ghi một frame vào video."""
        if self.is_recording_video and self.video_writer:
            try:
                v_frame = cv2.resize(frame, (1280, 720))
                self.video_writer.write(v_frame)
            except Exception as ve:
                print(f"[WARNING] Loi ghi video: {ve}")

    def stop_video_recording(self):
        """Dừng ghi video."""
        if self.is_recording_video and self.video_writer:
            self.is_recording_video = False
            self.video_writer.release()
            self.video_writer = None
            print("[VIDEO] Da dung ghi video.")

    def remote_capture(self, port=5513):
        """Gửi lệnh chụp cho digiCamControl qua HTTP API."""
        import requests
        try:
            url = f"http://127.0.0.1:{port}/remote?code=2001"
            print(f"[DSLR] Dang ra lenh chup: {url}")
            requests.get(url, timeout=2)
            return True
        except Exception as e:
            print(f"[ERROR] DSLR Capture fail: {e}")
            return False

    def release(self):
        """Giải phóng camera và video writer."""
        self.stop_video_recording()
        if self.cap:
            self.cap.release()
            self.cap = None
