# ==========================================
# PHOTOBOOTH - FREE MODE (REFACTORED)
# ==========================================
"""
Chế độ MIỄN PHÍ - Đã refactor theo Clean Architecture.
Kế thừa toàn bộ Handler từ PhotoboothApp.
"""

import sys
import os
import datetime
from PyQt5.QtWidgets import QApplication, QMessageBox
from PyQt5.QtCore import Qt

# === PATH FIX ===
_PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if _PROJECT_ROOT not in sys.path:
    sys.path.insert(0, _PROJECT_ROOT)

from src.app import PhotoboothApp
from src.shared.types.models import load_config
from src.utils import ensure_directories
from src.ui.dialogs.dialogs import DownloadSingleQRDialog


class FreePhotobooth(PhotoboothApp):
    """Bản Photobooth miễn phí - Ứng dụng Handler Pattern."""

    def __init__(self):
        self.is_free_mode = True
        super().__init__()
        
        # Override settings cho bản Free
        self.setWindowTitle("🎉 Photobooth - MIỄN PHÍ")
        self.selected_price_type = 4
        self.selected_frame_count = 4
        self.payment_confirmed = True
        
        print("\n" + "=" * 60)
        print("FREE MODE REFACTORED - READY")
        print("=" * 60)
        
        # Bắt đầu camera ngay cho bản Free
        self.camera_handler.start()
        self.camera_handler.set_callback(self.on_frame_home)

    def go_to_price_select(self):
        """Chuyển thẳng đến chọn gói (Step 1)."""
        print("[FREE] Skipping payment...")
        self.state = "PACKAGE_SELECT"
        if hasattr(self, 'stacked'):
            self.stacked.setCurrentIndex(1)
        self.camera_handler.set_callback(None)

    def start_capture_session(self):
        """Bắt đầu chụp - Bật LiveView feed."""
        super().start_capture_session()
        self.camera_handler.set_callback(self.on_frame_liveview, self.layout_type)

    def go_to_capture_screen(self):
        """Màn hình chụp Interactive."""
        self.state = "INTERACTIVE_CAPTURE"
        self.stacked.setCurrentIndex(9)
        self.camera_handler.set_callback(self.on_frame_interactive, self.layout_type)
        self.update_interactive_template_preview()
        self.update_interactive_button_text()
        self.start_video_recording()

    def accept_and_print(self):
        """Hoàn tất - Dừng video và bắt đầu xử lý ảnh cuối."""
        print("[FREE] Ending session and processing image...")
        self.stop_video_recording()
        
        if hasattr(self, 'template_timer'):
            self.template_timer.stop()
        
        # Chọn danh sách ảnh (ưu tiên ảnh chụp tương tác)
        interactive = getattr(self, 'interactive_photos', [])
        captured = getattr(self, 'captured_photos', [])
        photos_to_use = interactive if interactive else captured
        
        # Chỉ cần gọi workflow. Signal processing_finished sẽ kích hoạt on_processing_finished trong app.py
        self.image_workflow.process_final_image(
            photos_to_use, 
            getattr(self, 'layout_type', "4x1"), 
            getattr(self, 'selected_template_path', None)
        )

    def reset_all(self):
        super().reset_all()
        # Restart camera cho màn hình Home
        self.camera_handler.start()
        self.camera_handler.set_callback(self.on_frame_home)

    def open_camera_setup(self):
        """Mở cửa sổ thiết lập Camera."""
        from src.admin.pages.settings import CameraSetupApp
        self.camera_setup_window = CameraSetupApp(self.camera_handler)
        self.camera_setup_window.closeEvent = self._on_setup_closed
        self.camera_setup_window.show()

    def _on_setup_closed(self, event):
        """Callback khi đóng setup - Trả lại luồng cho màn hình Home."""
        self.camera_handler.set_callback(self.on_frame_home)
        event.accept()


def main():
    app = QApplication(sys.argv)
    app.is_free_mode = True
    ensure_directories()
    load_config()
    
    window = FreePhotobooth()
    window.showFullScreen()
    return app.exec_()


if __name__ == "__main__":
    sys.exit(main())
