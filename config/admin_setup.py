import sys
import json
import os

# Thêm thư mục gốc của project vào path để import đúng
PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)

from PyQt5.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout, 
                             QHBoxLayout, QLabel, QLineEdit, QPushButton, 
                             QGroupBox, QMessageBox, QFrame, QComboBox, QScrollArea)
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QFont, QIcon

# Import FrameEditor and config helpers
from modules.frame_editor import FrameEditor
from config.frame_config import get_all_layouts
from config import settings

CONFIG_FILE = "config.json"

# Danh sách một số ngân hàng phổ biến tại Việt Nam
VIETNAM_BANKS = [
    {"name": "MB Bank (Ngân hàng Quân đội)", "bin": "970422"},
    {"name": "Vietcombank (VCB)", "bin": "970436"},
    {"name": "Vietinbank", "bin": "970415"},
    {"name": "BIDV", "bin": "970418"},
    {"name": "Agribank", "bin": "970405"},
    {"name": "Techcombank (TCB)", "bin": "970407"},
    {"name": "ACB (Á Châu)", "bin": "970416"},
    {"name": "TPBank", "bin": "970423"},
    {"name": "VPBank", "bin": "970432"},
    {"name": "Sacombank", "bin": "970403"},
    {"name": "HDBank", "bin": "970437"},
    {"name": "VIB", "bin": "970441"},
    {"name": "SHB", "bin": "970443"},
    {"name": "MSB (Hàng Hải)", "bin": "970426"},
    {"name": "SeABank", "bin": "970440"},
    {"name": "Nam A Bank", "bin": "970428"},
    {"name": "LienVietPostBank", "bin": "970449"},
    {"name": "OCB (Phương Đông)", "bin": "970448"},
]

class AdminSetup(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("🛠️ Photobooth - Hệ thống Quản trị")
        self.resize(700, 900)
        self.setStyleSheet("""
            QMainWindow { background-color: #1a1a2e; }
            QLabel { color: #a8dadc; font-size: 14px; font-weight: bold; }
            QLineEdit, QComboBox { 
                background-color: #16213e; 
                color: white; 
                border: 1px solid #4361ee; 
                border-radius: 5px; 
                padding: 8px;
                font-size: 14px;
            }
            QLineEdit:focus, QComboBox:focus { border-color: #06d6a0; }
            QGroupBox { 
                color: #06d6a0; 
                font-weight: bold; 
                border: 2px solid #4361ee; 
                border-radius: 10px; 
                margin-top: 20px;
                padding-top: 15px;
            }
            QPushButton {
                background-color: #4361ee;
                color: white;
                border: none;
                border-radius: 10px;
                padding: 12px;
                font-size: 14px;
                font-weight: bold;
            }
            QPushButton:hover { background-color: #4cc9f0; }
            QPushButton#SaveBtn { background-color: #06d6a0; color: #1a1a2e; font-size: 18px; }
            QPushButton#SaveBtn:hover { background-color: #00f5d4; }
            QPushButton#EditorBtn { background-color: #f39c12; }
            QPushButton#EditorBtn:hover { background-color: #e67e22; }
        """)

        # Lưu trữ các QLineEdit của giá tiền layout
        self.layout_price_inputs = {}
        self.editor_window = None

        self.init_ui()
        settings.load_config()
        self.load_current_config()

    def init_ui(self):
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        main_layout = QVBoxLayout(central_widget)
        
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setStyleSheet("background-color: transparent; border: none;")
        
        content_widget = QWidget()
        layout = QVBoxLayout(content_widget)
        layout.setContentsMargins(30, 20, 30, 30)

        title = QLabel("CẤU HÌNH HỆ THỐNG PHOTOBOOTH")
        title.setAlignment(Qt.AlignCenter)
        title.setStyleSheet("font-size: 22px; color: #eaf0f6; margin-bottom: 10px;")
        layout.addWidget(title)
        
        # --- Frame Editor Shortcut ---
        editor_group = QGroupBox("QUẢN LÝ KHUNG ẢNH (EDITOR)")
        editor_layout = QVBoxLayout(editor_group)
        lbl_info = QLabel("Sử dụng công cụ thiết kế để tạo/chỉnh sửa các kiểu layout:")
        lbl_info.setStyleSheet("color: #a8dadc; font-weight: normal; margin-bottom: 5px;")
        editor_layout.addWidget(lbl_info)
        
        self.btn_open_editor = QPushButton("🎨 MỞ BỘ THIẾT KẾ KHUNG (FRAME EDITOR)")
        self.btn_open_editor.setObjectName("EditorBtn")
        self.btn_open_editor.clicked.connect(self.open_frame_editor)
        editor_layout.addWidget(self.btn_open_editor)

        self.btn_refresh_layouts = QPushButton("🔄 CẬP NHẬT DANH SÁCH LAYOUT MỚI")
        self.btn_refresh_layouts.setStyleSheet("background-color: #4361ee; margin-top: 5px;")
        self.btn_refresh_layouts.clicked.connect(self.refresh_layout_list)
        editor_layout.addWidget(self.btn_refresh_layouts)
        
        layout.addWidget(editor_group)

        # --- Gói Giá Chi Tiết ---
        price_group = QGroupBox("GIÁ TIỀN TỪNG KIỂU KHUNG (VNĐ)")
        self.price_container_layout = QVBoxLayout(price_group)
        
        # Lấy danh sách layouts hiện có
        all_layouts = get_all_layouts()
        for name in all_layouts.keys():
            self.layout_price_inputs[name] = self.create_input(self.price_container_layout, f"Giá {name}:", "Ví dụ: 30000")
            
        layout.addWidget(price_group)

        # --- Ngân hàng ---
        bank_group = QGroupBox("CẤU HÌNH THANH TOÁN (VIETQR)")
        bank_layout = QVBoxLayout(bank_group)
        
        h_bank_layout = QHBoxLayout()
        lbl_bank = QLabel("Ngân hàng:")
        lbl_bank.setFixedWidth(180)
        self.bank_combo = QComboBox()
        for bank in VIETNAM_BANKS:
            self.bank_combo.addItem(bank["name"], bank["bin"])
        h_bank_layout.addWidget(lbl_bank)
        h_bank_layout.addWidget(self.bank_combo)
        bank_layout.addLayout(h_bank_layout)

        self.bank_acc = self.create_input(bank_layout, "Số tài khoản:", "Nhập số tài khoản nhận tiền")
        self.bank_name = self.create_input(bank_layout, "Tên chủ tài khoản:", "Nhập tên không dấu (VIET HOA)")
        layout.addWidget(bank_group)

        # --- API Keys ---
        api_group = QGroupBox("API KEYS & CLOUD")
        api_layout = QVBoxLayout(api_group)
        
        self.casso_key = self.create_input(api_layout, "Casso API Key:", "Dùng để kiểm tra thanh toán")
        self.cloud_name = self.create_input(api_layout, "Cloudinary Name:", "Tên cloud")
        self.cloud_api_key = self.create_input(api_layout, "Cloudinary API Key:", "API Key")
        self.cloud_api_secret = self.create_input(api_layout, "Cloudinary API Secret:", "API Secret")
        layout.addWidget(api_group)

        # --- Nút Lưu ---
        self.btn_save = QPushButton("💾 LƯU TẤT CẢ CẤU HÌNH")
        self.btn_save.setObjectName("SaveBtn")
        self.btn_save.setFixedHeight(60)
        self.btn_save.clicked.connect(self.save_config)
        layout.addWidget(self.btn_save)
        
        scroll.setWidget(content_widget)
        main_layout.addWidget(scroll)

    def create_input(self, parent_layout, label_text, placeholder):
        h_layout = QHBoxLayout()
        lbl = QLabel(label_text)
        lbl.setFixedWidth(180)
        edit = QLineEdit()
        edit.setPlaceholderText(placeholder)
        h_layout.addWidget(lbl)
        h_layout.addWidget(edit)
        parent_layout.addLayout(h_layout)
        return edit

    def refresh_layout_list(self):
        """Cập nhật lại danh sách các ô nhập giá tiền (sau khi thêm layout mới)."""
        import importlib
        from config import frame_config
        importlib.reload(frame_config) # Buộc Python load lại file đã thay đổi
        
        # Xóa các widget cũ trong price_container_layout
        while self.price_container_layout.count():
            item = self.price_container_layout.takeAt(0)
            widget = item.widget()
            if widget:
                widget.deleteLater()
            else:
                # Nếu là layout (QHBoxLayout), xóa các con của nó
                sub_layout = item.layout()
                if sub_layout:
                    while sub_layout.count():
                        sub_item = sub_layout.takeAt(0)
                        if sub_item.widget(): sub_item.widget().deleteLater()

        # Re-populate
        self.layout_price_inputs = {}
        all_layouts = frame_config.get_all_layouts()
        for name in all_layouts.keys():
            self.layout_price_inputs[name] = self.create_input(self.price_container_layout, f"Giá {name}:", "Ví dụ: 30000")
        
        # Load lại giá trị từ config.json
        self.load_current_config()
        QMessageBox.information(self, "Thành công", "Đã cập nhật danh sách layouts mới từ cấu hình!")

    def open_frame_editor(self):
        """Mở cửa sổ Frame Editor."""
        if self.editor_window is None:
            self.editor_window = FrameEditor()
        self.editor_window.show()
        self.editor_window.raise_()
        self.editor_window.activateWindow()

    def load_current_config(self):
        if not os.path.exists(CONFIG_FILE):
            return

        try:
            with open(CONFIG_FILE, 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            # Load giá cho từng layout
            layout_prices = data.get("layout_prices", {})
            for name, input_field in self.layout_price_inputs.items():
                if name in layout_prices:
                    input_field.setText(str(layout_prices[name]))
                else:
                    # Fallback to general price if specific not found
                    if name in ["1x2", "2x1"]:
                         input_field.setText(str(data.get("price_2_photos", "")))
                    else:
                         input_field.setText(str(data.get("price_4_photos", "")))
            
            # Chọn ngân hàng
            saved_bin = data.get("bank_bin", "")
            index = self.bank_combo.findData(saved_bin)
            if index != -1:
                self.bank_combo.setCurrentIndex(index)
                
            self.bank_acc.setText(data.get("bank_account", ""))
            self.bank_name.setText(data.get("account_name", ""))
            self.casso_key.setText(data.get("casso_api_key", ""))
            
            cloud = data.get("cloudinary", {})
            self.cloud_name.setText(cloud.get("cloud_name", ""))
            self.cloud_api_key.setText(cloud.get("api_key", ""))
            self.cloud_api_secret.setText(cloud.get("api_secret", ""))
            
        except Exception as e:
            print(f"Lỗi load config: {e}")

    def save_config(self):
        # Thu thập giá tiền các layout
        layout_prices = {}
        try:
            for name, input_field in self.layout_price_inputs.items():
                val = input_field.text().strip()
                if val:
                    layout_prices[name] = int(val)
        except ValueError:
            QMessageBox.critical(self, "Lỗi", "Giá tiền các layout phải là số nguyên!")
            return

        # Lấy giá trị chung để tương thích ngược (nếu cần)
        p2 = layout_prices.get("2x1", layout_prices.get("1x2", 20000))
        p4 = layout_prices.get("2x2", layout_prices.get("4x1", 35000))

        config_data = {
            "price_2_photos": p2,
            "price_4_photos": p4,
            "layout_prices": layout_prices,
            "bank_bin": self.bank_combo.currentData(),
            "bank_account": self.bank_acc.text(),
            "account_name": self.bank_name.text(),
            "casso_api_key": self.casso_key.text(),
            "cloudinary": {
                "cloud_name": self.cloud_name.text(),
                "api_key": self.cloud_api_key.text(),
                "api_secret": self.cloud_api_secret.text()
            }
        }

        try:
            with open(CONFIG_FILE, 'w', encoding='utf-8') as f:
                json.dump(config_data, f, indent=4, ensure_ascii=False)
            QMessageBox.information(self, "Thành công", "Đã lưu cấu hình vào config.json!")
            settings.load_config() # Refresh global config
        except Exception as e:
            QMessageBox.critical(self, "Lỗi", f"Không thể lưu file: {e}")

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = AdminSetup()
    window.show()
    sys.exit(app.exec_())
