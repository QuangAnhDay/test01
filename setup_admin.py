import sys
import json
import os
from PyQt5.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout, 
                             QHBoxLayout, QLabel, QLineEdit, QPushButton, 
                             QGroupBox, QMessageBox, QFrame, QComboBox)
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QFont, QIcon

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
        self.resize(600, 800)
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
                padding: 15px;
                font-size: 16px;
                font-weight: bold;
            }
            QPushButton:hover { background-color: #4cc9f0; }
            QPushButton#SaveBtn { background-color: #06d6a0; color: #1a1a2e; }
            QPushButton#SaveBtn:hover { background-color: #00f5d4; }
        """)

        self.init_ui()
        self.load_current_config()

    def init_ui(self):
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        layout = QVBoxLayout(central_widget)
        layout.setContentsMargins(30, 20, 30, 30)

        title = QLabel("CẤU HÌNH HỆ THỐNG PHOTOBOOTH")
        title.setAlignment(Qt.AlignCenter)
        title.setStyleSheet("font-size: 22px; color: #eaf0f6; margin-bottom: 10px;")
        layout.addWidget(title)

        # --- Gói Giá ---
        price_group = QGroupBox("GÓI GIÁ (VNĐ)")
        price_layout = QVBoxLayout(price_group)
        
        self.price_2 = self.create_input(price_layout, "Giá gói 2 ảnh:", "Ví dụ: 20000")
        self.price_4 = self.create_input(price_layout, "Giá gói 4 ảnh:", "Ví dụ: 35000")
        layout.addWidget(price_group)

        # --- Ngân hàng ---
        bank_group = QGroupBox("CẤU HÌNH VIETQR")
        bank_layout = QVBoxLayout(bank_group)
        
        # Combo box cho Ngân hàng
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

        # --- Casso & Cloudinary ---
        api_group = QGroupBox("API KEYS")
        api_layout = QVBoxLayout(api_group)
        
        self.casso_key = self.create_input(api_layout, "Casso API Key:", "Dùng để kiểm tra thanh toán")
        self.cloud_name = self.create_input(api_layout, "Cloudinary Name:", "Tên cloud")
        self.cloud_api_key = self.create_input(api_layout, "Cloudinary API Key:", "API Key")
        self.cloud_api_secret = self.create_input(api_layout, "Cloudinary API Secret:", "API Secret")
        layout.addWidget(api_group)

        layout.addStretch()

        # --- Nút Lưu ---
        self.btn_save = QPushButton("💾 LƯU CẤU HÌNH")
        self.btn_save.setObjectName("SaveBtn")
        self.btn_save.clicked.connect(self.save_config)
        layout.addWidget(self.btn_save)

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

    def load_current_config(self):
        if not os.path.exists(CONFIG_FILE):
            return

        try:
            with open(CONFIG_FILE, 'r', encoding='utf-8') as f:
                data = json.load(f)
                
            # Điền dữ liệu vào form
            self.price_2.setText(str(data.get("price_2_photos", "")))
            self.price_4.setText(str(data.get("price_4_photos", "")))
            
            # Chọn ngân hàng trong combo box dựa trên BIN
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
        # Validate data
        try:
            p2 = int(self.price_2.text() or 0)
            p4 = int(self.price_4.text() or 0)
        except ValueError:
            QMessageBox.critical(self, "Lỗi", "Giá tiền phải là số nguyên!")
            return

        # Lấy BIN từ combo box
        selected_bin = self.bank_combo.currentData()

        config_data = {
            "price_2_photos": p2,
            "price_4_photos": p4,
            "bank_bin": selected_bin,
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
        except Exception as e:
            QMessageBox.critical(self, "Lỗi", f"Không thể lưu file: {e}")

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = AdminSetup()
    window.show()
    sys.exit(app.exec_())
