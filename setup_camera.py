import sys
import os
import cv2
import json
from PyQt5.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout, 
                             QHBoxLayout, QLabel, QComboBox, QPushButton, 
                             QMessageBox, QGroupBox, QCheckBox, QSlider)
from PyQt5.QtCore import Qt, QTimer, pyqtSignal
from PyQt5.QtGui import QImage, QPixmap

CONFIG_FILE = "camera_settings.json"

def load_camera_config():
    if os.path.exists(CONFIG_FILE):
        try:
            with open(CONFIG_FILE, 'r') as f:
                return json.load(f)
        except:
            pass
    return {"camera_index": 0, "use_dshow": True, "width": 1280, "height": 720}

def save_camera_config(config):
    with open(CONFIG_FILE, 'w') as f:
        json.dump(config, f, indent=4)

class CameraSetupApp(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Thiết lập Camera - Photobooth")
        self.setFixedSize(900, 700)
        self.setStyleSheet("""
            QMainWindow { background-color: #f0f2f5; }
            QGroupBox { font-weight: bold; border: 1px solid #ccc; border-radius: 8px; margin-top: 10px; }
            QPushButton { padding: 10px; border-radius: 5px; font-weight: bold; }
        """)
        
        self.config = load_camera_config()
        self.cap = None
        
        self.init_ui()
        self.start_preview()
        
    def init_ui(self):
        main_widget = QWidget()
        self.setCentralWidget(main_widget)
        layout = QHBoxLayout(main_widget)
        
        # --- Cột trái: Điều khiển ---
        controls_layout = QVBoxLayout()
        layout.addLayout(controls_layout, 1)
        
        group_select = QGroupBox("1. Chọn Camera")
        select_layout = QVBoxLayout(group_select)
        
        self.combo_cam = QComboBox()
        self.refresh_cameras()
        self.combo_cam.currentIndexChanged.connect(self.start_preview)
        
        hint_label = QLabel("💡 Gợi ý:\nIndex 0: Thường là Cam Laptop\nIndex 1: Thường là Iriun/HDMI")
        hint_label.setStyleSheet("color: #666; font-size: 13px;")
        
        select_layout.addWidget(QLabel("Thiết bị nhận diện được:"))
        select_layout.addWidget(self.combo_cam)
        select_layout.addWidget(hint_label)
        
        btn_refresh = QPushButton("Làm mới danh sách")
        btn_refresh.clicked.connect(self.refresh_cameras)
        select_layout.addWidget(btn_refresh)
        
        controls_layout.addWidget(group_select)
        
        group_settings = QGroupBox("2. Cấu hình & Sửa lỗi")
        settings_layout = QVBoxLayout(group_settings)
        
        self.check_dshow = QCheckBox("Sử dụng DirectShow (Khuyên dùng)")
        self.check_dshow.setChecked(self.config.get("use_dshow", True))
        self.check_dshow.stateChanged.connect(self.start_preview)
        settings_layout.addWidget(self.check_dshow)

        self.check_compat = QCheckBox("Chế độ Tương thích (Sửa lỗi Cam Laptop bị đen)")
        self.check_compat.setStyleSheet("color: #d9534f; font-weight: bold;")
        self.check_compat.stateChanged.connect(self.start_preview)
        settings_layout.addWidget(self.check_compat)
        
        self.combo_res = QComboBox()
        self.combo_res.addItems(["1280x720 (HD)", "1920x1080 (FullHD)", "640x480 (SD)"])
        settings_layout.addWidget(QLabel("Độ phân giải mong muốn:"))
        settings_layout.addWidget(self.combo_res)
        
        controls_layout.addWidget(group_settings)
        
        btn_save = QPushButton("LƯU CẤU HÌNH & KẾT THÚC")
        btn_save.setStyleSheet("background-color: #28a745; color: white; height: 50px;")
        btn_save.clicked.connect(self.save_and_exit)
        controls_layout.addWidget(btn_save)
        
        controls_layout.addStretch()
        
        # --- Cột phải: Preview ---
        preview_layout = QVBoxLayout()
        layout.addLayout(preview_layout, 2)
        
        self.preview_label = QLabel("Vui chọn camera để xem trước")
        self.preview_label.setAlignment(Qt.AlignCenter)
        self.preview_label.setStyleSheet("background-color: black; color: white; border-radius: 10px; font-size: 16px;")
        self.preview_label.setFixedSize(560, 420)
        preview_layout.addWidget(self.preview_label)
        
        self.status_label = QLabel("Status: Chào mừng")
        preview_layout.addWidget(self.status_label)
        
        self.timer = QTimer()
        self.timer.timeout.connect(self.update_frame)
        
    def refresh_cameras(self):
        old_idx = self.combo_cam.currentIndex()
        self.combo_cam.blockSignals(True)
        self.combo_cam.clear()
        
        # Thử dùng pygrabber để lấy tên thật
        cam_names = []
        try:
            from pygrabber.dshow_graph import FilterGraph
            graph = FilterGraph()
            cam_names = graph.get_input_devices()
        except:
            print("Pygrabber not available, using indices")

        found_any = False
        for i in range(5):
            cap = cv2.VideoCapture(i, cv2.CAP_DSHOW)
            if cap.isOpened():
                name = cam_names[i] if i < len(cam_names) else f"Camera {i}"
                self.combo_cam.addItem(f"{name} (Index {i})", i)
                cap.release()
                found_any = True
            else:
                cap.release()
                
        if not found_any:
            self.combo_cam.addItem("Không tìm thấy camera hoạt động", -1)
            for i in range(3):
                name = cam_names[i] if i < len(cam_names) else f"Index {i}"
                self.combo_cam.addItem(f"Thử {name}", i)

        self.combo_cam.blockSignals(False)
        if old_idx >= 0: self.combo_cam.setCurrentIndex(old_idx)
        else: self.combo_cam.setCurrentIndex(0)

    def start_preview(self):
        if self.timer.isActive():
            self.timer.stop()
            
        if self.cap:
            self.cap.release()
            self.cap = None
        
        index = self.combo_cam.currentData()
        if index is None or index < 0:
            return
            
        use_dshow = self.check_dshow.isChecked()
        use_compat = self.check_compat.isChecked()
        print(f"DEBUG: Starting preview for index {index} (DSHOW={use_dshow}, COMPAT={use_compat})")
        
        self.consecutive_fails = 0
        
        if use_dshow:
            self.cap = cv2.VideoCapture(index, cv2.CAP_DSHOW)
        else:
            self.cap = cv2.VideoCapture(index)
            
        if self.cap.isOpened():
            import time
            time.sleep(0.5) 
            
            if use_compat:
                # Chế độ tương thích cao cho laptop cam
                self.cap.set(cv2.CAP_PROP_FOURCC, cv2.VideoWriter_fourcc(*'MJPG'))
                self.cap.set(cv2.CAP_PROP_FRAME_WIDTH, 640)
                self.cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)
            else:
                self.cap.set(cv2.CAP_PROP_FRAME_WIDTH, 1280)
                self.cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 720)
            
            for _ in range(5):
                self.cap.read()
                time.sleep(0.05)
            
            self.status_label.setText(f"Status: Đang chạy Camera {index}")
            self.timer.start(50)
        else:
            self.status_label.setText(f"Status: KHÔNG THỂ KẾT NỐI")
            self.preview_label.setText(f"LỖI: Không thể mở Camera {index}\nHãy thử bật 'Chế độ tương thích' hoặc đổi Index")

    def update_frame(self):
        if self.cap and self.cap.isOpened():
            ret, frame = self.cap.read()
            if ret and frame is not None:
                self.consecutive_fails = 0
                frame = cv2.flip(frame, 1)
                rgb_image = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
                h, w, ch = rgb_image.shape
                bytes_per_line = ch * w
                convert_to_Qt_format = QImage(rgb_image.data, w, h, bytes_per_line, QImage.Format_RGB888)
                p = convert_to_Qt_format.scaled(560, 420, Qt.KeepAspectRatio, Qt.SmoothTransformation)
                self.preview_label.setPixmap(QPixmap.fromImage(p))
            else:
                self.consecutive_fails += 1
                if self.consecutive_fails > 10:
                    self.timer.stop()
                    self.preview_label.setText("MẤT TÍN HIỆU\nĐang khởi động lại...")
                    QTimer.singleShot(1500, self.start_preview)
        else:
            self.timer.stop()

    def save_and_exit(self):
        res_text = self.combo_res.currentText()
        w, h = (1280, 720)
        if "1920" in res_text: w, h = (1920, 1080)
        elif "640" in res_text: w, h = (640, 480)
        
        new_config = {
            "camera_index": self.combo_cam.currentData(),
            "use_dshow": self.check_dshow.isChecked(),
            "use_compat": self.check_compat.isChecked(),
            "width": w,
            "height": h
        }
        save_camera_config(new_config)
        QMessageBox.information(self, "Thành công", "Đã lưu cấu hình camera!\nBây giờ bạn có thể mở main_free.py")
        self.close()

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = CameraSetupApp()
    window.show()
    sys.exit(app.exec_())
