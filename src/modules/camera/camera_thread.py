import cv2
import time
import datetime
import os
import numpy as np
from PyQt5.QtCore import QThread, pyqtSignal, QMutex, QMutexLocker
from PyQt5.QtGui import QImage

class CameraThread(QThread):
    """
    Luồng phụ chuyên đọc frame từ Camera để tránh làm treo UI.
    Hỗ trợ Web Camera (webcam) và DSLR (qua MJPEG URL).
    Hỗ trợ quay video ở luồng phụ.
    """
    frame_ready = pyqtSignal(QImage)
    error_occurred = pyqtSignal(str)

    def __init__(self, camera_index=0, width=1280, height=720, use_dshow=True, use_compat=False):
        super().__init__()
        self.camera_index = camera_index
        self.width = width
        self.height = height
        self.use_dshow = use_dshow
        self.use_compat = use_compat
        self.rotation = 0
        self.last_cv_frame = None
        
        self.running = False
        self.cap = None
        self.mutex = QMutex()
        
        # Cấu hình quay video
        self.is_recording = False
        self.video_writer = None
        self.record_width = 1280
        self.record_height = 720

    def run(self):
        self.running = True
        try:
            self._open_camera()
            while self.running:
                if self.cap is None or not self.cap.isOpened():
                    # Thử mở lại sau một khoảng thời gian nếu mất kết nối
                    time.sleep(1)
                    if self.running:
                        self._open_camera()
                    continue

                ret, frame = self.cap.read()
                if ret and frame is not None:
                    # Pre-processing (Xoay, Lật)
                    if getattr(self, 'rotation', 0) == 90:
                        frame = cv2.rotate(frame, cv2.ROTATE_90_CLOCKWISE)
                    elif getattr(self, 'rotation', 0) == 180:
                        frame = cv2.rotate(frame, cv2.ROTATE_180)
                    elif getattr(self, 'rotation', 0) == 270:
                        frame = cv2.rotate(frame, cv2.ROTATE_90_COUNTERCLOCKWISE)

                    # Mirror
                    frame = cv2.flip(frame, 1)

                    # Lưu frame copy cho chụp ảnh (OpenCV format)
                    self.last_cv_frame = frame.copy()

                    # Ghi video nếu đang quay
                    with QMutexLocker(self.mutex):
                        if self.is_recording and self.video_writer:
                            try:
                                v_frame = cv2.resize(frame, (self.record_width, self.record_height))
                                self.video_writer.write(v_frame)
                            except Exception as ve:
                                print(f"[THREAD CAMERA] Loi ghi video: {ve}")

                    # Chuyển đổi sang QImage ngay tại đây để UI dùng luôn
                    rgb_image = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
                    h, w, ch = rgb_image.shape
                    bytes_per_line = ch * w
                    qt_image = QImage(rgb_image.data, w, h, bytes_per_line, QImage.Format_RGB888)

                    # Phát tín hiệu báo có frame mới (copy cho chắc chắn lặp lại được ở các recipient khác nhau)
                    self.frame_ready.emit(qt_image.copy())
                    
                    # Điều tiết FPS (khoảng 30fps)
                    self.msleep(30)
                else:
                    # Lỗi đọc frame
                    self.msleep(10)
        finally:
            # Luôn giải phóng camera khi thoát loop (vì bất cứ lý do gì)
            self._close_all()

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
                print(f"[THREAD CAMERA] Opened index {self.camera_index} SUCCESSFULLY.")
                if not (isinstance(self.camera_index, str) and self.camera_index.startswith("http")):
                    # Đợi một chút để driver ổn định
                    time.sleep(0.3)
                    try:
                        if self.use_compat:
                            # MJPG mode
                            self.cap.set(cv2.CAP_PROP_FOURCC, cv2.VideoWriter_fourcc('M', 'J', 'P', 'G'))
                            self.cap.set(cv2.CAP_PROP_FRAME_WIDTH, 640)
                            self.cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)
                            print(f"[THREAD CAMERA] Mode: COMPAT (MJPG 640x480)")
                        else:
                            print(f"[THREAD CAMERA] Setting resolution to {self.width}x{self.height}")
                            self.cap.set(cv2.CAP_PROP_FRAME_WIDTH, self.width)
                            self.cap.set(cv2.CAP_PROP_FRAME_HEIGHT, self.height)
                    except Exception as se:
                        print(f"[THREAD CAMERA] WARNING: Could not set camera properties: {se}")
                return True
            else:
                print(f"[THREAD CAMERA] FAILED to open index {self.camera_index}")
                self.error_occurred.emit(f"Không thể mở camera {self.camera_index}")
                return False
        except Exception as e:
            self.error_occurred.emit(str(e))
            return False

    def start_recording(self, output_path, width=1280, height=720, fps=20.0):
        """Bắt đầu ghi video ở luồng phụ."""
        with QMutexLocker(self.mutex):
            try:
                self.record_width = width
                self.record_height = height
                fourcc = cv2.VideoWriter_fourcc(*'mp4v')
                self.video_writer = cv2.VideoWriter(output_path, fourcc, fps, (width, height))
                self.is_recording = True
                print(f"[THREAD CAMERA] Bat dau ghi video tai: {output_path}")
            except Exception as e:
                print(f"[THREAD CAMERA] Loi khoi tao VideoWriter: {e}")
                self.is_recording = False

    def stop_recording(self):
        """Dừng ghi video."""
        with QMutexLocker(self.mutex):
            self.is_recording = False
            if self.video_writer:
                self.video_writer.release()
                self.video_writer = None
                print("[THREAD CAMERA] Da dung va luu video.")

    def change_camera(self, index, width=1280, height=720, use_dshow=True, use_compat=False):
        """Đổi camera index một cách an toàn."""
        self.camera_index = index
        self.width = width
        self.height = height
        self.use_dshow = use_dshow
        self.use_compat = use_compat
        self._open_camera()

    def _close_all(self):
        """Giải phóng tài nguyên."""
        self.stop_recording()
        if self.cap:
            self.cap.release()
            self.cap = None

    def stop(self):
        """Dừng thread một cách an toàn."""
        self.running = False
        # Chờ tối đa 2 giây để thread tự thoát vòng lặp
        if not self.wait(2000):
            print("[THREAD CAMERA] Thread khong thoat dung han, dang cuong che dung...")
            self.terminate()
            self.wait(1000)
            self._close_all() # Buộc dọn dẹp nếu terminate
