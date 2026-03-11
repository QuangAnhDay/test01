import os
import json
import cv2
from PyQt5.QtWidgets import QFrame, QLabel, QVBoxLayout
from PyQt5.QtCore import Qt, pyqtSignal, QThread, QRectF
from PyQt5.QtGui import QImage, QPixmap, QRegion, QPainterPath, QPainter
from PyQt5.QtCore import QMutex, QMutexLocker
import logging

logger = logging.getLogger(__name__)


def _load_camera_settings():
    """Đọc cấu hình camera từ camera_settings.json."""
    from src.config import CAMERA_SETTINGS_PATH
    for path in [CAMERA_SETTINGS_PATH, "camera_settings.json"]:
        if os.path.exists(path):
            try:
                with open(path, 'r') as f:
                    return json.load(f)
            except Exception:
                pass
    return {}


class CameraWorkerThread(QThread):
    """Thread riêng để xử lý việc capture frame từ camera"""
    frame_ready = pyqtSignal(QImage)
    camera_error = pyqtSignal(str)

    def __init__(self):
        super().__init__()
        self.is_running = False
        self.camera_index = 0
        self.cap = None
        
        # Tự động phát hiện chế độ FREE để tránh tranh chấp Camera
        from PyQt5.QtWidgets import QApplication
        app = QApplication.instance()
        self.external_cap = getattr(app, 'is_free_mode', False)
        
        self.mutex = QMutex()
        self._pending_index = None
        self._consecutive_failures = 0  # Counter for failed reads

    def run(self):
        """Loop chính để capture frame"""
        try:
            while self.is_running:
                should_open_camera = False

                # Kiểm tra xem có yêu cầu đổi camera hay không
                with QMutexLocker(self.mutex):
                    if self._pending_index is not None:
                        self.camera_index = self._pending_index
                        self._pending_index = None
                        # Nếu đang dùng external cap mà đổi index -> tự mở camera mới
                        if self.external_cap:
                            self.external_cap = False
                        should_open_camera = True
                    elif self.cap is None:
                        should_open_camera = True

                if should_open_camera and not self.external_cap:
                    self._open_camera()
                    if self.cap is None:
                        self.msleep(250)
                        continue

                # Nếu camera chưa mở, bỏ qua
                if self.cap is None:
                    self.msleep(100)
                    continue

                # Capture frame
                if self.external_cap:
                    # Nếu dùng external_cap, thread này TRÁNH gọi read() 
                    # để không tranh giành luồng dữ liệu (tránh double-read).
                    # Frame sẽ được push thông qua hàm display_frame ngoài main app.
                    self.msleep(100)
                    continue

                ret, frame = self.cap.read()
                if not ret:
                    self._consecutive_failures += 1
                    # Chỉ reset camera sau ~30 lần lỗi liên tục (~1 giây)
                    if self._consecutive_failures > 30:
                        logger.warning(f"Lỗi đọc frame liên tục ({self._consecutive_failures}), đang reset camera...")
                        if not self.external_cap:
                            self.camera_error.emit(f"Mất kết nối camera {self.camera_index}")
                            self._open_camera()
                        self._consecutive_failures = 0
                    
                    self.msleep(33) # Giảm msleep để check nhanh hơn nhưng không block
                    continue
                
                # Reset counter if read is successful
                self._consecutive_failures = 0

                # Lật ngang (mirror effect)
                frame = cv2.flip(frame, 1)

                # Resize và convert sang RGB (Trừ đi 10px mỗi chiều cho viền trắng 5px)
                frame = cv2.resize(frame, (720, 460))
                frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)

                # Convert sang QImage
                h, w, ch = frame_rgb.shape
                bytes_per_line = 3 * w
                qt_image = QImage(frame_rgb.data, w, h, bytes_per_line, QImage.Format_RGB888).copy()

                self.frame_ready.emit(qt_image)
                self.msleep(33)  # ~30 FPS
        finally:
            # Đảm bảo camera luôn được release dù thoát thread vì lý do nào.
            # Chỉ release nếu KHÔNG dùng external cap (tránh release cap của app)
            if self.cap is not None and not self.external_cap:
                self.cap.release()
                self.cap = None

    def _open_camera(self):
        """Mở camera theo index hiện tại, đọc cấu hình từ camera_settings.json"""
        # Release camera cũ nếu có (chỉ khi tự quản lý)
        if self.cap is not None and not self.external_cap:
            self.cap.release()
            self.cap = None

        try:
            cam_cfg = _load_camera_settings()
            use_dshow = cam_cfg.get("use_dshow", True)
            use_compat = cam_cfg.get("use_compat", False)

            # Trên Windows, ưu tiên DirectShow để giảm lỗi treo với backend MSMF.
            if use_dshow and os.name == "nt":
                self.cap = cv2.VideoCapture(self.camera_index, cv2.CAP_DSHOW)
                if not self.cap.isOpened():
                    self.cap = cv2.VideoCapture(self.camera_index)  # Fallback
            else:
                self.cap = cv2.VideoCapture(self.camera_index)

            if not self.cap.isOpened():
                self.camera_error.emit(f"Không thể mở camera index {self.camera_index}")
                self.cap = None
                return False

            # Chế độ tương thích: MJPG codec (sửa lỗi cam laptop bị đen)
            if use_compat:
                self.cap.set(cv2.CAP_PROP_FOURCC, cv2.VideoWriter_fourcc(*'MJPG'))
                self.cap.set(cv2.CAP_PROP_FRAME_WIDTH, 640)
                self.cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)
                logger.info(f"Camera compat mode: MJPG 640x480")
            else:
                cam_w = cam_cfg.get("width", 1280)
                cam_h = cam_cfg.get("height", 960) # Mặc định 960p (4:3)
                self.cap.set(cv2.CAP_PROP_FRAME_WIDTH, cam_w)
                self.cap.set(cv2.CAP_PROP_FRAME_HEIGHT, cam_h)

            self.cap.set(cv2.CAP_PROP_FPS, 30)

            # Warmup: Đọc bỏ vài frame đầu (nhiều webcam cần khởi động)
            for _ in range(8):
                self.cap.read()

            logger.info(f"✓ Mở camera index {self.camera_index} thành công (compat={use_compat})")
            return True

        except Exception as e:
            self.camera_error.emit(f"Lỗi khi mở camera: {str(e)}")
            self.cap = None
            return False

    def set_camera_index(self, index):
        """Đặt index camera để đổi (thread-safe)"""
        with QMutexLocker(self.mutex):
            self._pending_index = index

    def set_external_capture(self, cap):
        """Sử dụng đối tượng capture có sẵn từ bên ngoài (thread-safe)."""
        with QMutexLocker(self.mutex):
            # Release camera cũ nếu tự quản lý
            if self.cap is not None and not self.external_cap:
                self.cap.release()
            self.cap = cap
            self.external_cap = True
            self._pending_index = None  # Hủy pending index nếu có

    def stop(self):
        """Dừng worker thread một cách sạch sẽ"""
        self.is_running = False
        if not self.wait(1500):  # Tránh treo vô hạn khi backend camera bị block
            logger.warning("Camera worker không dừng kịp, buộc terminate thread")
            self.terminate()
            self.wait(500)
            # Chỉ release nếu tự quản lý
            if self.cap is not None and not self.external_cap:
                self.cap.release()
                self.cap = None


class CameraView(QFrame):
    """Widget hiển thị camera feed với bo góc"""

    camera_changed = pyqtSignal(int)  # Phát tín hiệu khi camera thay đổi

    def __init__(self, initial_camera_index=0, parent=None):
        super().__init__(parent)

        # Cấu hình container chính (Khung trắng bo góc)
        self.setFixedSize(730, 470)
        self.setObjectName("cameraViewFrame")
        self.setStyleSheet("""
            #cameraViewFrame {
                background-color: white;
                border-radius: 24px;
            }
        """)

        # Áp dụng mask cho container ngoài để chắc chắn viền trắng bo tròn
        self._apply_outer_mask()

        # Khung đen bên trong để chứa camera feed (Lọt lòng 5px)
        self.inner_frame = QFrame(self)
        self.inner_frame.setFixedSize(720, 460)
        self.inner_frame.move(5, 5)
        self.inner_frame.setObjectName("cameraInner")
        self.inner_frame.setStyleSheet("""
            #cameraInner {
                background-color: black;
                border-radius: 19px;
            }
        """)
        
        # Áp dụng mask cho khung đen để bo cả feed camera bên trong
        inner_path = QPainterPath()
        inner_path.addRoundedRect(QRectF(0, 0, 720, 460), 19, 19)
        self.inner_frame.setMask(QRegion(inner_path.toFillPolygon().toPolygon()))

        # Layout trong khung đen
        inner_layout = QVBoxLayout(self.inner_frame)
        inner_layout.setContentsMargins(0, 0, 0, 0)

        # Label hiển thị camera feed
        self.image_label = QLabel("Camera Offline", self.inner_frame)
        self.image_label.setAlignment(Qt.AlignCenter)
        self.image_label.setStyleSheet("color: white; background: transparent;")
        self.image_label.setFixedSize(720, 460)
        inner_layout.addWidget(self.image_label)

        # Camera worker thread
        self.camera_worker = CameraWorkerThread()
        self.camera_worker.frame_ready.connect(self.display_frame)
        self.camera_worker.camera_error.connect(self.handle_camera_error)

        # Khai báo biến theo dõi
        self.current_camera_index = initial_camera_index
        self._is_running = False

        # Đặt camera ban đầu
        self.camera_worker.camera_index = initial_camera_index

    def set_frame(self, q_img):
        """Đẩy frame từ bên ngoài vào (dùng cho kiến trúc tập trung CameraHandler)."""
        if q_img and not q_img.isNull():
            # Áp dụng bo góc nếu cần
            if self.image_label:
                self.image_label.setPixmap(QPixmap.fromImage(q_img).scaled(
                    self.image_label.size(), Qt.KeepAspectRatio, Qt.SmoothTransformation
                ))

    def set_capture(self, cap):
        """Hỗ trợ backward compatibility."""
        if cap:
            self.camera_worker.set_external_capture(cap)
            # If an external capture is provided, and the worker is not running,
            # we might need to start it to process frames if it's in a mode
            # where it expects to be started but not read from.
            # However, the CameraView.start() method already handles the external_cap logic.
            # So, just setting the external capture is sufficient.
            # The worker's run loop will then respect the external_cap flag.

    def start(self):
        """Khởi động camera"""
        if self._is_running:
            logger.warning("Camera đã đang chạy")
            return

        logger.info(f"Bắt đầu camera index {self.current_camera_index}")
        if self.camera_worker.external_cap:
            logger.info("Camera đang ở chế độ External Capture, không chạy worker thread riêng.")
            self._is_running = True
            return

        self.camera_worker.is_running = True
        if not self.camera_worker.external_cap:
            self.camera_worker.set_camera_index(self.current_camera_index)
        self.camera_worker.start()
        self._is_running = True

    def stop(self):
        """Dừng camera một cách sạch sẽ"""
        if not self._is_running:
            return

        logger.info("Dừng camera")
        self._is_running = False
        self.camera_worker.stop()

        # Clear display
        self.image_label.clear()
        self.image_label.setText("Camera Offline")

    def set_camera(self, camera_index):
        """Đổi camera sang index khác (thread-safe)"""
        if camera_index == self.current_camera_index:
            logger.info(f"Camera index {camera_index} đã được chọn")
            return

        logger.info(f"Đổi camera từ {self.current_camera_index} sang {camera_index}")
        self.current_camera_index = camera_index
        self.camera_worker.set_camera_index(camera_index)
        self.camera_changed.emit(camera_index)

    def display_frame(self, qt_image):
        """Hiển thị frame lên giao diện"""
        if isinstance(qt_image, QImage):
            pixmap = QPixmap.fromImage(qt_image)
        elif isinstance(qt_image, QPixmap):
            pixmap = qt_image
        else:
            return

        self.image_label.setPixmap(pixmap)

    def _create_rounded_pixmap(self, pixmap, radius=24):
        """Tạo pixmap với các góc bo tròn"""
        size = pixmap.size()

        # Tạo QImage mới với alpha channel
        image = QImage(size.width(), size.height(), QImage.Format_ARGB32_Premultiplied)
        image.fill(Qt.transparent)

        # Vẽ pixmap lên image với mask bo góc
        painter = QPainter(image)
        painter.setRenderHint(QPainter.Antialiasing, True)

        # Tạo path bo góc
        path = QPainterPath()
        path.addRoundedRect(0, 0, size.width(), size.height(), radius, radius)
        painter.setClipPath(path)

        # Vẽ pixmap vào image
        painter.drawPixmap(0, 0, pixmap)
        painter.end()

        return QPixmap.fromImage(image)

    def _apply_outer_mask(self):
        """Tạo mask bo góc cho toàn bộ khung trắng ngoài cùng"""
        path = QPainterPath()
        path.addRoundedRect(QRectF(0, 0, 730, 470), 24, 24)
        region = QRegion(path.toFillPolygon().toPolygon())
        self.setMask(region)

    def handle_camera_error(self, error_message):
        """Xử lý lỗi camera"""
        logger.error(f"❌ {error_message}")
        self.image_label.setText(error_message)

    def get_available_cameras(self):
        """Quét tất cả camera khả dụng trên hệ thống"""
        available_cameras = []

        for index in range(10):  # Quét từ 0 đến 9
            cap = cv2.VideoCapture(index)
            if cap.isOpened():
                available_cameras.append(index)
                cap.release()

        logger.info(f"Tìm thấy {len(available_cameras)} camera: {available_cameras}")
        return available_cameras

    def closeEvent(self, event):
        """Đảm bảo camera được dừng khi widget bị đóng"""
        self.stop()
        super().closeEvent(event)
