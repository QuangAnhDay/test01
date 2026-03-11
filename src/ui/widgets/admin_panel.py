import os
import json
import cv2
from PyQt5.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel, 
                             QPushButton, QFrame, QTabWidget, QLineEdit, 
                             QSpinBox, QCheckBox, QGridLayout, QMessageBox)
from PyQt5.QtCore import Qt, pyqtSignal
from PyQt5.QtGui import QImage, QPixmap

# Lấy code Layout Designer hiện có để tích hợp vào Tab
from src.photobooth.steps.step_1_custom_editor import create_custom_editor_screen

class AdminPanel(QWidget):
    """
    Bảng điều khiển Admin hợp nhất: Setup Camera + Thiết kế Layout (F2).
    """
    def __init__(self, app):
        super().__init__()
        self.app = app
        self.setWindowTitle("⚙️ PHOTOBOOTH ADMIN CENTER")
        self.setFixedSize(1200, 800)
        self.setStyleSheet("background-color: #1a1a2e; color: white;")
        
        self.layout = QVBoxLayout(self)
        self.tabs = QTabWidget()
        self.tabs.setStyleSheet("""
            QTabWidget::pane { border: 1px solid #4361ee; background-color: #16213e; }
            QTabBar::tab { background: #0f3460; color: #aaa; padding: 15px 30px; font-weight: bold; }
            QTabBar::tab:selected { background: #4361ee; color: white; }
        """)
        
        # --- TAB 1: THIẾT KẾ LAYOUT (ORIGINAL) ---
        self.layout_design_tab = create_custom_editor_screen(app)
        self.tabs.addTab(self.layout_design_tab, "🖼️ THIẾT KẾ BỐ CỤC (LAYOUT)")
        
        # --- TAB 2: SETUP CAMERA (NEW) ---
        self.camera_setup_tab = self.create_camera_tab()
        self.tabs.addTab(self.camera_setup_tab, "📸 CÀI ĐẶT CAMERA")
        
        self.layout.addWidget(self.tabs)
        
        # Nút Thoát Admin
        self.btn_exit = QPushButton("❌ THOÁT ADMIN")
        self.btn_exit.setFixedSize(200, 50)
        self.btn_exit.setObjectName("OrangeBtn") # Dùng style chung nếu có
        self.btn_exit.clicked.connect(lambda: self.app.stacked.setCurrentIndex(0))
        self.layout.addWidget(self.btn_exit, alignment=Qt.AlignRight)

    def create_camera_tab(self):
        tab = QWidget()
        layout = QHBoxLayout(tab)
        layout.setContentsMargins(30,30,30,30)
        layout.setSpacing(40)
        
        # -- Bên trái: Form Settings --
        form_widget = QFrame()
        form_widget.setFixedWidth(400)
        form_widget.setStyleSheet("background-color: #16213e; border-radius: 15px; padding: 20px;")
        form_layout = QVBoxLayout(form_widget)
        
        title = QLabel("CÀI ĐẶT CAMERA")
        title.setStyleSheet("font-size: 20px; font-weight: bold; color: #06d6a0;")
        form_layout.addWidget(title)
        form_layout.addSpacing(20)
        
        # Camera Index / URL
        form_layout.addWidget(QLabel("Index (0,1,...) hoặc DSLR URL (MJPEG):"))
        self.edit_cam_idx = QLineEdit()
        self.edit_cam_idx.setStyleSheet("background: #000; color: #fff; border: 1px solid #4361ee;")
        form_layout.addWidget(self.edit_cam_idx)
        
        # Resolution
        res_layout = QGridLayout()
        res_layout.addWidget(QLabel("Chiều rộng (W):"), 0, 0)
        self.spin_w = QSpinBox()
        self.spin_w.setRange(320, 3840)
        res_layout.addWidget(self.spin_w, 0, 1)
        
        res_layout.addWidget(QLabel("Chiều cao (H):"), 1, 0)
        self.spin_h = QSpinBox()
        self.spin_h.setRange(240, 2160)
        res_layout.addWidget(self.spin_h, 1, 1)
        form_layout.addLayout(res_layout)
        
        # Flags
        self.check_dshow = QCheckBox("Bật DirectShow (Nhanh hơn trên Windows)")
        self.check_compat = QCheckBox("Chế độ tương thích (Cố định 640x480 MJPG)")
        form_layout.addWidget(self.check_dshow)
        form_layout.addWidget(self.check_compat)
        
        form_layout.addStretch()
        
        # Nút Action
        btn_apply = QPushButton("🚀 ÁP DỤNG & LƯU")
        btn_apply.setStyleSheet("background-color: #06d6a0; color: #000; height: 50px; font-weight: bold; border-radius: 10px;")
        btn_apply.clicked.connect(self.save_and_apply_camera)
        form_layout.addWidget(btn_apply)
        
        layout.addWidget(form_widget)
        
        # -- Bên phải: Preview --
        preview_container = QVBoxLayout()
        preview_container.addWidget(QLabel("LIVE PREVIEW (ADMIN VIEW)"))
        self.admin_cam_label = QLabel("Đang chờ khởi động...")
        self.admin_cam_label.setAlignment(Qt.AlignCenter)
        self.admin_cam_label.setFixedSize(640, 480)
        self.admin_cam_label.setStyleSheet("background-color: #000; border: 2px solid #4361ee; border-radius: 10px;")
        preview_container.addWidget(self.admin_cam_label)
        preview_container.addStretch()
        
        layout.addLayout(preview_container)
        
        # Load values from file
        self.load_camera_settings()
        
        return tab

    def load_camera_settings(self):
        try:
            from src.config import CAMERA_SETTINGS_PATH
            if os.path.exists(CAMERA_SETTINGS_PATH):
                with open(CAMERA_SETTINGS_PATH, "r") as f:
                    cfg = json.load(f)
                    self.edit_cam_idx.setText(str(cfg.get("camera_index", 0)))
                    self.spin_w.setValue(cfg.get("width", 1280))
                    self.spin_h.setValue(cfg.get("height", 960))
                    self.check_dshow.setChecked(cfg.get("use_dshow", True))
                    self.check_compat.setChecked(cfg.get("use_compat", False))
        except: pass

    def save_and_apply_camera(self):
        idx_str = self.edit_cam_idx.text()
        try:
            idx = int(idx_str)
        except:
            idx = idx_str # If string, maybe it's URL
            
        cfg = {
            "camera_index": idx,
            "width": self.spin_w.value(),
            "height": self.spin_h.value(),
            "use_dshow": self.check_dshow.isChecked(),
            "use_compat": self.check_compat.isChecked()
        }
        
        from src.config import CAMERA_SETTINGS_PATH
        with open(CAMERA_SETTINGS_PATH, "w") as f:
            json.dump(cfg, f, indent=4)
            
        # Gọi app.py để cập nhật nóng luồng camera
        if hasattr(self.app, 'switch_camera_live'):
            self.app.switch_camera_live(idx, cfg["width"], cfg["height"], self.check_dshow.isChecked(), cfg["use_compat"])
            QMessageBox.information(self, "Thành công", "Đã lưu và cập nhật camera mới!")
        else:
            QMessageBox.warning(self, "Lưu ý", "Đã lưu cài đặt nhưng không thể cập nhật nóng camera. Hãy khởi động lại ứng dụng.")
            
    def update_admin_preview(self, frame):
        """Hàm nhận frame từ CameraThread và hiển thị lên tab Admin."""
        if self.isVisible() and self.tabs.currentIndex() == 1:
            h, w, ch = frame.shape
            bytes_per_line = ch * w
            qt_img = QImage(frame.data, w, h, bytes_per_line, QImage.Format_BGR888)
            pixmap = QPixmap.fromImage(qt_img).scaled(640, 480, Qt.KeepAspectRatio, Qt.SmoothTransformation)
            self.admin_cam_label.setPixmap(pixmap)
