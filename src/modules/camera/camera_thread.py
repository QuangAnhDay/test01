import cv2
import time
import numpy as np
import requests
from PyQt5.QtCore import QThread, pyqtSignal

class CameraThread(QThread):
    """
    Luồng phụ chuyên đọc frame từ Camera để tránh làm treo UI.
    Hỗ trợ Web Camera (webcam) và DSLR (qua MJPEG URL).
    """
    frame_ready = pyqtSignal(object)
    error_occurred = pyqtSignal(str)

    def __init__(self, camera_index=0, width=1280, height=720, use_dshow=True, use_compat=False):
        super().__init__()
        self.camera_index = camera_index
        self.width = width
        self.height = height
        self.use_dshow = use_dshow
        self.use_compat = use_compat
        self.running = False
        self.cap = None

    def run(self):
        self.running = True
        self._open_camera()

        while self.running:
            if self.cap is None or not self.cap.isOpened():
                # Thử mở lại sau một khoảng thời gian nếu mất kết nối
                time.sleep(1)
                self._open_camera()
                continue

            ret, frame = self.cap.read()
            if ret and frame is not None:
                self.frame_ready.emit(frame)
                # Điều tiết FPS (khoảng 30fps)
                self.msleep(30)
            else:
                # Lỗi đọc frame
                self.msleep(10)

    def _open_camera(self):
        """Khởi tạo kết nối camera."""
        if self.cap is not None:
            self.cap.release()
            self.cap = None

        try:
            # MJPEG Stream (thường từ digiCamControl hoặc Web Server MJPEG)
            if isinstance(self.camera_index, str) and self.camera_index.startswith("http"):
                self.cap = cv2.VideoCapture(self.camera_index)
            else:
                # OpenCV Camera Index
                idx = int(self.camera_index)
                if self.use_dshow:
                    self.cap = cv2.VideoCapture(idx, cv2.CAP_DSHOW)
                else:
                    self.cap = cv2.VideoCapture(idx)
                
                if not self.cap.isOpened() and self.use_dshow:
                    self.cap = cv2.VideoCapture(idx)

            if self.cap and self.cap.isOpened():
                if not (isinstance(self.camera_index, str) and self.camera_index.startswith("http")):
                    if self.use_compat:
                        self.cap.set(cv2.CAP_PROP_FOURCC, cv2.VideoWriter_fourcc(*'MJPG'))
                        self.cap.set(cv2.CAP_PROP_FRAME_WIDTH, 640)
                        self.cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)
                    else:
                        self.cap.set(cv2.CAP_PROP_FRAME_WIDTH, self.width)
                        self.cap.set(cv2.CAP_PROP_FRAME_HEIGHT, self.height)
                return True
            else:
                self.error_occurred.emit(f"Không thể mở camera {self.camera_index}")
                return False
        except Exception as e:
            self.error_occurred.emit(str(e))
            return False

    def change_camera(self, index, width=1280, height=720, use_dshow=True, use_compat=False):
        """Đổi camera index một cách an toàn."""
        self.camera_index = index
        self.width = width
        self.height = height
        self.use_dshow = use_dshow
        self.use_compat = use_compat
        # Việc mở lại sẽ được thread chính xử lý trong loop run() hoặc gọi thủ công
        self._open_camera()

    def stop(self):
        self.running = False
        self.wait(1000)
        if self.cap:
            self.cap.release()
            self.cap = None
