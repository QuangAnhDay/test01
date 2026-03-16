# ==========================================
# SETTINGS PAGE - Thiết lập Camera
# ==========================================
"""
Trang thiết lập camera: chọn camera, cấu hình độ phân giải,
chế độ DirectShow, preview trực tiếp.

CÁCH CHẠY:
    python -m src.admin.pages.settings
"""

import sys
import os
import cv2
import json
import time
from PyQt5.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout,
                             QHBoxLayout, QLabel, QComboBox, QPushButton,
                             QMessageBox, QGroupBox, QCheckBox, QSlider, QLineEdit)
from PyQt5.QtCore import Qt, QTimer
from PyQt5.QtGui import QImage, QPixmap

from src.config import CAMERA_SETTINGS_PATH
CAMERA_SETTINGS_FILE = CAMERA_SETTINGS_PATH


def load_camera_config():
    if os.path.exists(CAMERA_SETTINGS_FILE):
        try:
            with open(CAMERA_SETTINGS_FILE, 'r') as f:
                return json.load(f)
        except:
            pass
    return {"camera_index": 0, "use_dshow": True, "use_compat": False, "width": 1280, "height": 960}


def save_camera_config(config):
    with open(CAMERA_SETTINGS_FILE, 'w') as f:
        json.dump(config, f, indent=4)


class CameraSetupApp(QMainWindow):
    """Trang thiết lập và kiểm tra camera."""

    def __init__(self, camera_handler=None):
        super().__init__()
        self.setWindowTitle("Camera Setup - Photobooth")
        self.setFixedSize(900, 700)
        self.setStyleSheet("""
            QMainWindow { background-color: #f0f2f5; }
            QGroupBox { font-weight: bold; border: 1px solid #ccc; border-radius: 8px; margin-top: 10px; }
            QPushButton { padding: 10px; border-radius: 5px; font-weight: bold; }
        """)

        self.config = load_camera_config()
        self.camera_handler = camera_handler # Sử dụng handler từ app chính
        self.cap = None
        self.consecutive_fails = 0

        self.init_ui()
        self.start_preview()

    def init_ui(self):
        main_widget = QWidget()
        self.setCentralWidget(main_widget)
        layout = QHBoxLayout(main_widget)

        # --- Cột trái: Điều khiển ---
        controls_layout = QVBoxLayout()
        layout.addLayout(controls_layout, 1)

        group_select = QGroupBox("1. Select Camera")
        select_layout = QVBoxLayout(group_select)

        self.combo_cam = QComboBox()
        self.refresh_cameras()
        self.combo_cam.currentIndexChanged.connect(self.start_preview)

        hint_label = QLabel("💡 Hint:\nIndex 0: Usually Laptop Cam\nIndex 1: Usually Iriun/HDMI")
        hint_label.setStyleSheet("color: #666; font-size: 13px;")

        select_layout.addWidget(QLabel("Detected devices:"))
        select_layout.addWidget(self.combo_cam)
        select_layout.addWidget(hint_label)

        btn_refresh = QPushButton("Refresh list")
        btn_refresh.clicked.connect(self.refresh_cameras)
        select_layout.addWidget(btn_refresh)

        controls_layout.addWidget(group_select)

        group_settings = QGroupBox("2. Config & Troubleshooting")
        settings_layout = QVBoxLayout(group_settings)

        self.check_dshow = QCheckBox("Use DirectShow (Recommended)")
        self.check_dshow.setChecked(self.config.get("use_dshow", True))
        self.check_dshow.stateChanged.connect(self.start_preview)
        settings_layout.addWidget(self.check_dshow)

        self.check_compat = QCheckBox("Compatibility Mode (Fix black Laptop Cam)")
        self.check_compat.setStyleSheet("color: #d9534f; font-weight: bold;")
        self.check_compat.stateChanged.connect(self.start_preview)
        settings_layout.addWidget(self.check_compat)

        self.combo_res = QComboBox()
        self.combo_res.addItems(["1280x960 (4:3)", "1280x720 (16:9)", "1920x1080 (FullHD)", "640x480 (SD)"])
        settings_layout.addWidget(QLabel("Desired resolution:"))
        settings_layout.addWidget(self.combo_res)

        controls_layout.addWidget(group_settings)
        
        group_dslr = QGroupBox("3. DSLR Mode (digiCamControl)")
        dslr_layout = QVBoxLayout(group_dslr)
        
        self.edit_mjpeg = QLineEdit()
        self.edit_mjpeg.setPlaceholderText("http://127.0.0.1:8080/mjpg/video.mjpg")
        current_idx = str(self.config.get("camera_index", ""))
        if current_idx.startswith("http"):
            self.edit_mjpeg.setText(current_idx)
            
        dslr_layout.addWidget(QLabel("MJPEG Stream Address:"))
        dslr_layout.addWidget(self.edit_mjpeg)
        
        self.btn_use_dslr = QPushButton("USE DSLR")
        self.btn_use_dslr.clicked.connect(self.use_dslr_mjpeg)
        dslr_layout.addWidget(self.btn_use_dslr)
        
        controls_layout.addWidget(group_dslr)

        btn_save = QPushButton("SAVE CONFIG & EXIT")
        btn_save.setStyleSheet("background-color: #28a745; color: white; height: 50px;")
        btn_save.clicked.connect(self.save_and_exit)
        controls_layout.addWidget(btn_save)

        controls_layout.addStretch()

        # --- Cột phải: Preview ---
        preview_layout = QVBoxLayout()
        layout.addLayout(preview_layout, 2)

        self.preview_label = QLabel("Camera Preview")
        self.preview_label.setAlignment(Qt.AlignCenter)
        self.preview_label.setStyleSheet("background-color: black; color: white; border: 2px solid white;")
        self.preview_label.setFixedSize(560, 420)
        preview_layout.addWidget(self.preview_label)

        self.status_label = QLabel("Status: Welcome")
        self.status_label.setStyleSheet("color: #333; font-weight: bold;")
        preview_layout.addWidget(self.status_label)

        self.timer = QTimer()
        self.timer.timeout.connect(self.update_frame)

        # Thread-safe camera opener
        self.cam_thread = None

    def refresh_cameras(self):
        """Lấy danh sách camera nhanh chóng mà không gây treo app."""
        self.combo_cam.blockSignals(True)
        self.combo_cam.clear()

        cam_names = []
        try:
            from pygrabber.dshow_graph import FilterGraph
            graph = FilterGraph()
            cam_names = graph.get_input_devices()
        except Exception as e:
            print(f"Pygrabber error: {e}")

        if cam_names:
            for i, name in enumerate(cam_names):
                # KHÔNG tự ý mở camera ở đây vì gây treo UI (nhất là khi có nhiều camera)
                self.combo_cam.addItem(f"📷 {name} (Index {i})", i)
        else:
            # Fallback nếu pygrabber lỗi
            for i in range(5):
                self.combo_cam.addItem(f"Camera {i} (Index {i})", i)

        self.combo_cam.blockSignals(False)
        
        # Thử chọn lại index trong config nếu có
        config_idx = self.config.get("camera_index", 0)
        if isinstance(config_idx, int):
            for i in range(self.combo_cam.count()):
                if self.combo_cam.itemData(i) == config_idx:
                    self.combo_cam.setCurrentIndex(i)
                    break

    def start_preview(self):
        """Khởi động camera ở luồng phụ để tránh treo UI."""
        if self.timer.isActive():
            self.timer.stop()

        if self.cap:
            self.cap.release()
            self.cap = None

        # Lấy camera index
        url_input = self.edit_mjpeg.text().strip()
        index = url_input if url_input.startswith("http") else self.combo_cam.currentData()

        if index is None or (isinstance(index, int) and index < 0):
            self.preview_label.setText("No camera selected")
            return

        use_dshow = self.check_dshow.isChecked()
        use_compat = self.check_compat.isChecked()

        # Cho phép người dùng chọn lại nếu lỗi, không block UI
        if self.camera_handler:
            # Ra lệnh cho handler trung tâm khởi động lại với cấu hình mới
            # và đặt callback nhận ảnh duy nhất cho màn hình Setup này
            self.camera_handler.set_callback(self.on_frame_from_thread)
            self.camera_handler.restart_with_config(index, 1280, 720, use_dshow, use_compat)
            # Kết nối sự kiện báo lỗi nếu có
            if self.camera_handler.thread:
                self.camera_handler.thread.error_occurred.connect(self.on_camera_error)
        else:
            # Fallback nếu chạy độc lập
            from src.services.camera.camera_thread import CameraThread
            if hasattr(self, 'cam_thread') and self.cam_thread:
                self.cam_thread.stop()
            
            self.cam_thread = CameraThread(index, width=1280, height=720, use_dshow=use_dshow, use_compat=use_compat)
            self.cam_thread.frame_ready.connect(self.on_frame_from_thread)
            self.cam_thread.error_occurred.connect(self.on_camera_error)
            self.cam_thread.start()

    def on_frame_from_thread(self, q_img):
        """Callback khi có frame từ thread camera (Loại QImage)."""
        # Cập nhật UI nếu đây là frame đầu tiên (chuyển trạng thái)
        if "active" not in self.status_label.text():
            self.status_label.setText("Status: ✅ Camera active")

        # Hiển thị lên UI (Signal đã là QImage và đã được lật/xoay sẵn trong thread)
        pixmap = QPixmap.fromImage(q_img).scaled(560, 420, Qt.KeepAspectRatio, Qt.SmoothTransformation)
        self.preview_label.setPixmap(pixmap)

    def on_camera_error(self, message):
        """Callback khi camera gặp lỗi."""
        self.combo_cam.setEnabled(True)
        self.btn_use_dslr.setEnabled(True)
        self.status_label.setText(f"Status: ⚠️ Error - {message}")
        self.preview_label.setText(f"❌ CONNECTION ERROR\n{message}")

    def update_frame(self):
        # Hàm này không còn dùng nữa vì đã dùng CameraThread
        pass

    def use_dslr_mjpeg(self):
        url = self.edit_mjpeg.text().strip()
        if not url.startswith("http"):
             QMessageBox.warning(self, "Error", "MJPEG address must start with http://")
             return
             
        self.config["camera_index"] = url
        self.config["use_dshow"] = False
        save_camera_config(self.config)
        self.start_preview()
        QMessageBox.information(self, "Success", f"Switched to DSLR:\n{url}")

    def save_and_exit(self):
        res_text = self.combo_res.currentText()
        w, h = (1280, 720) # Default for DSLR
        if "960" in res_text:
            w, h = (1280, 960)
        elif "1080" in res_text:
            w, h = (1920, 1080)
        elif "480" in res_text:
            w, h = (640, 480)

        # Nếu đang dùng MJPEG, giữ nguyên index là chuỗi URL
        current_cam_idx = self.edit_mjpeg.text().strip()
        if not current_cam_idx.startswith("http"):
            current_cam_idx = self.combo_cam.currentData()

        new_config = {
            "camera_index": current_cam_idx,
            "use_dshow": self.check_dshow.isChecked() if not isinstance(current_cam_idx, str) else False,
            "use_compat": self.check_compat.isChecked(),
            "width": w,
            "height": h
        }
        save_camera_config(new_config)
        
        # Dọn dẹp trước khi thoát
        if self.camera_handler:
            try:
                self.camera_handler.frame_received.disconnect(self.on_frame_from_thread)
            except:
                pass
        elif hasattr(self, 'cam_thread') and self.cam_thread:
            self.cam_thread.stop()
            
        QMessageBox.information(self, "Success",
                                "Camera configuration saved!\nYou can now run the application.")
        self.close()


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = CameraSetupApp()
    window.show()
    sys.exit(app.exec_())
