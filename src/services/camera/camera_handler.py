# ==========================================
# CAMERA HANDLER - Điều phối luồng camera
# ==========================================
"""
Quản lý việc chuyển đổi recipient (người nhận frame) tùy theo state của ứng dụng.
Sử dụng một CameraThread duy nhất để tối ưu hiệu năng.
"""

from PyQt5.QtCore import QObject, pyqtSignal
from src.services.camera.camera_thread import CameraThread
from src.shared.types.models import get_layout_config


class CameraHandler(QObject):
    """Quản lý thread camera và phân phối frame."""
    frame_received = pyqtSignal(object) # Chuyển tiếp frame đến UI hiện tại

    def __init__(self, camera_index=0, width=1280, height=960, use_dshow=True, use_compat=False):
        super().__init__()
        self.camera_index = camera_index
        self._width = width
        self._height = height
        self._use_dshow = use_dshow
        self._use_compat = use_compat
        
        self.thread = None
        self._current_callback = None

    def start(self):
        """Khởi động thread camera."""
        if self.thread and self.thread.isRunning():
            return
            
        self.thread = CameraThread(
            self.camera_index, 
            width=self._width, 
            height=self._height,
            use_dshow=self._use_dshow, 
            use_compat=self._use_compat
        )
        self.thread.frame_ready.connect(self._on_frame)
        self.thread.start()
        print(f"[CAMERA HANDLER] Initialized index {self.camera_index}")

    def stop(self):
        """Dừng thread camera."""
        if self.thread:
            self.thread.stop()
            self.thread.wait()
            self.thread = None

    def set_callback(self, callback, layout_type=None):
        """Đổi hàm nhận frame và cập nhật rotation theo layout."""
        if layout_type:
            try:
                cfg = get_layout_config(layout_type)
                rot = cfg.get("rotation", 0)
                if self.thread:
                    self.thread.rotation = rot
                    print(f"[CAMERA HANDLER] Rotation set to {rot} for {layout_type}")
            except Exception as e:
                print(f"[CAMERA HANDLER] Error setting rotation: {e}")
        else:
            if self.thread:
                self.thread.rotation = 0
                print(f"[CAMERA HANDLER] Rotation reset to 0")

        self._current_callback = callback
        print(f"[CAMERA HANDLER] Callback changed to {callback.__name__ if callback else 'None'}")

    def _on_frame(self, frame):
        """Nhận frame từ thread và chuyển cho callback đang hoạt động."""
        if self._current_callback:
            self._current_callback(frame)
        self.frame_received.emit(frame)

    def restart_with_config(self, index, w, h, dshow, compat):
        """Cập nhật cấu hình camera nóng."""
        self.stop()
        self.camera_index = index
        self._width = w
        self._height = h
        self._use_dshow = dshow
        self._use_compat = compat
        self.start()

    def start_recording(self, output_path, w=1280, h=720, fps=20.0):
        """Proxy bắt đầu ghi video."""
        if self.thread:
            self.thread.start_recording(output_path, w, h, fps)

    def stop_recording(self):
        """Proxy dừng ghi video."""
        if self.thread:
            self.thread.stop_recording()
