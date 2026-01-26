"""
================================================================================
SETUP ADMIN - Chương trình cài đặt cấu hình cho Photobooth
================================================================================
Mô tả: Ứng dụng PyQt5 cho phép chủ máy cấu hình thông tin thanh toán và giá tiền.
Phiên bản: 1.1 - Tối ưu cho màn hình 15.6 inch
================================================================================
"""

import sys
import os
import json
import requests
from PyQt5.QtWidgets import (
    QApplication, QMainWindow, QWidget, QLabel, QPushButton,
    QVBoxLayout, QHBoxLayout, QLineEdit, QComboBox, QMessageBox,
    QGroupBox, QGridLayout, QSpinBox, QScrollArea
)
from PyQt5.QtCore import Qt, QThread, pyqtSignal
from PyQt5.QtGui import QFont

# ==========================================
# CẤU HÌNH
# ==========================================
CONFIG_FILE = "config.json"

# ==========================================
# THREAD TẢI DANH SÁCH NGÂN HÀNG
# ==========================================
class BankLoaderThread(QThread):
    """Thread tải danh sách ngân hàng từ VietQR API."""
    banks_loaded = pyqtSignal(list)
    load_error = pyqtSignal(str)
    
    def run(self):
        try:
            response = requests.get("https://api.vietqr.io/v2/banks", timeout=10)
            response.raise_for_status()
            data = response.json()
            if data.get("code") == "00" and "data" in data:
                self.banks_loaded.emit(data["data"])
            else:
                self.load_error.emit("Không thể lấy danh sách ngân hàng")
        except requests.exceptions.Timeout:
            self.load_error.emit("Timeout - thử lại sau")
        except requests.exceptions.ConnectionError:
            self.load_error.emit("Lỗi kết nối mạng")
        except Exception as e:
            self.load_error.emit(str(e))


# ==========================================
# GIAO DIỆN CHÍNH
# ==========================================
class SetupAdminApp(QMainWindow):
    """Ứng dụng cài đặt cấu hình Photobooth."""
    
    def __init__(self):
        super().__init__()
        self.setWindowTitle("⚙️ Photobooth - Cài đặt cấu hình")
        self.setMinimumSize(800, 700)
        self.resize(900, 750)
        
        self.banks_list = []
        self._saved_bank_bin = ""
        
        self.apply_stylesheet()
        self.setup_ui()
        self.load_existing_config()
        self.start_loading_banks()
    
    def apply_stylesheet(self):
        """Áp dụng style cho giao diện."""
        self.setStyleSheet("""
            QMainWindow {
                background-color: #1a1a2e;
            }
            QScrollArea {
                background-color: #1a1a2e;
                border: none;
            }
            QWidget#ScrollContent {
                background-color: #1a1a2e;
            }
            QLabel {
                color: white;
                font-family: 'Segoe UI', 'Arial', sans-serif;
                font-size: 13px;
                background: transparent;
            }
            QLabel#TitleLabel {
                font-size: 26px;
                font-weight: bold;
                color: #ffd700;
                padding: 10px;
            }
            QLabel#SubTitleLabel {
                font-size: 14px;
                color: #a8dadc;
                padding-bottom: 10px;
            }
            QLabel#FieldLabel {
                font-size: 13px;
                color: #a8dadc;
                min-width: 120px;
                padding-right: 10px;
            }
            QGroupBox {
                color: #ffd700;
                font-weight: bold;
                font-size: 14px;
                border: 2px solid #4361ee;
                border-radius: 10px;
                margin-top: 20px;
                padding: 15px;
                padding-top: 25px;
                background-color: #16213e;
            }
            QGroupBox::title {
                subcontrol-origin: margin;
                subcontrol-position: top left;
                left: 15px;
                top: 5px;
                padding: 0 8px;
                background-color: #16213e;
            }
            QLineEdit, QComboBox, QSpinBox {
                background-color: #0f0f23;
                color: white;
                border: 2px solid #4361ee;
                border-radius: 6px;
                padding: 8px 12px;
                font-size: 13px;
                min-height: 18px;
            }
            QLineEdit:focus, QComboBox:focus, QSpinBox:focus {
                border-color: #06d6a0;
            }
            QComboBox::drop-down {
                border: none;
                width: 30px;
            }
            QComboBox::down-arrow {
                border-left: 5px solid transparent;
                border-right: 5px solid transparent;
                border-top: 8px solid #ffd700;
                margin-right: 10px;
            }
            QComboBox QAbstractItemView {
                background-color: #16213e;
                color: white;
                selection-background-color: #4361ee;
            }
            QPushButton {
                background-color: #4361ee;
                color: white;
                border: none;
                border-radius: 8px;
                padding: 10px 20px;
                font-size: 13px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #5a7eff;
            }
            QPushButton#SaveBtn {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:1,
                    stop:0 #06d6a0, stop:1 #00f5d4);
                color: #1a1a2e;
                font-size: 18px;
                min-height: 50px;
                border-radius: 10px;
            }
            QPushButton#SaveBtn:hover {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:1,
                    stop:0 #00f5d4, stop:1 #06d6a0);
            }
            QSpinBox::up-button, QSpinBox::down-button {
                width: 20px;
                background-color: #4361ee;
            }
            QSpinBox::up-button:hover, QSpinBox::down-button:hover {
                background-color: #06d6a0;
            }
        """)
    
    def setup_ui(self):
        """Thiết lập giao diện."""
        # Scroll Area để hỗ trợ màn hình nhỏ
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.setCentralWidget(scroll)
        
        # Container chính
        container = QWidget()
        container.setObjectName("ScrollContent")
        scroll.setWidget(container)
        
        main_layout = QVBoxLayout(container)
        main_layout.setContentsMargins(40, 20, 40, 20)
        main_layout.setSpacing(15)
        
        # === TIÊU ĐỀ ===
        title = QLabel("⚙️ CÀI ĐẶT CẤU HÌNH PHOTOBOOTH")
        title.setObjectName("TitleLabel")
        title.setAlignment(Qt.AlignCenter)
        main_layout.addWidget(title)
        
        subtitle = QLabel("Nhập thông tin thanh toán và giá tiền cho hệ thống")
        subtitle.setObjectName("SubTitleLabel")
        subtitle.setAlignment(Qt.AlignCenter)
        main_layout.addWidget(subtitle)
        
        # === NHÓM: THÔNG TIN NGÂN HÀNG ===
        bank_group = QGroupBox("🏦 Thông tin tài khoản ngân hàng")
        bank_grid = QGridLayout(bank_group)
        bank_grid.setSpacing(12)
        bank_grid.setColumnStretch(1, 1)
        
        # Row 0: Ngân hàng
        lbl_bank = QLabel("Ngân hàng:")
        lbl_bank.setObjectName("FieldLabel")
        bank_grid.addWidget(lbl_bank, 0, 0, Qt.AlignRight)
        self.combo_bank = QComboBox()
        self.combo_bank.addItem("⏳ Đang tải danh sách ngân hàng...")
        self.combo_bank.setEnabled(False)
        bank_grid.addWidget(self.combo_bank, 0, 1)
        
        # Row 1: Số tài khoản
        lbl_acc = QLabel("Số tài khoản:")
        lbl_acc.setObjectName("FieldLabel")
        bank_grid.addWidget(lbl_acc, 1, 0, Qt.AlignRight)
        self.input_account_number = QLineEdit()
        self.input_account_number.setPlaceholderText("Nhập số tài khoản ngân hàng")
        bank_grid.addWidget(self.input_account_number, 1, 1)
        
        # Row 2: Tên chủ TK
        lbl_name = QLabel("Tên chủ TK:")
        lbl_name.setObjectName("FieldLabel")
        bank_grid.addWidget(lbl_name, 2, 0, Qt.AlignRight)
        self.input_account_name = QLineEdit()
        self.input_account_name.setPlaceholderText("Nhập tên chủ tài khoản (không dấu)")
        bank_grid.addWidget(self.input_account_name, 2, 1)
        
        main_layout.addWidget(bank_group)
        
        # === NHÓM: CASSO API ===
        casso_group = QGroupBox("🔐 Casso API (Xác nhận thanh toán tự động)")
        casso_grid = QGridLayout(casso_group)
        casso_grid.setSpacing(12)
        casso_grid.setColumnStretch(1, 1)
        
        lbl_casso = QLabel("Casso API Key:")
        lbl_casso.setObjectName("FieldLabel")
        casso_grid.addWidget(lbl_casso, 0, 0, Qt.AlignRight)
        
        casso_input_layout = QHBoxLayout()
        self.input_casso_api = QLineEdit()
        self.input_casso_api.setPlaceholderText("Nhập API Key từ Casso.vn")
        self.input_casso_api.setEchoMode(QLineEdit.Password)
        casso_input_layout.addWidget(self.input_casso_api)
        
        self.btn_toggle_api = QPushButton("👁️ Hiện")
        self.btn_toggle_api.setFixedWidth(80)
        self.btn_toggle_api.clicked.connect(self.toggle_api_visibility)
        casso_input_layout.addWidget(self.btn_toggle_api)
        casso_grid.addLayout(casso_input_layout, 0, 1)
        
        # Hướng dẫn
        api_note = QLabel("💡 Để lấy API Key: Đăng ký tại casso.vn → Cài đặt → API Keys")
        api_note.setStyleSheet("color: #a8dadc; font-size: 11px; font-style: italic;")
        casso_grid.addWidget(api_note, 1, 1)
        
        main_layout.addWidget(casso_group)
        
        # === NHÓM: GIÁ TIỀN ===
        price_group = QGroupBox("💰 Thiết lập giá tiền")
        price_grid = QGridLayout(price_group)
        price_grid.setSpacing(12)
        price_grid.setColumnStretch(1, 1)
        
        lbl_p2 = QLabel("Gói 2 ảnh:")
        lbl_p2.setObjectName("FieldLabel")
        price_grid.addWidget(lbl_p2, 0, 0, Qt.AlignRight)
        self.input_price_2 = QSpinBox()
        self.input_price_2.setRange(1000, 1000000)
        self.input_price_2.setSingleStep(1000)
        self.input_price_2.setValue(20000)
        self.input_price_2.setSuffix(" VNĐ")
        price_grid.addWidget(self.input_price_2, 0, 1)
        
        lbl_p4 = QLabel("Gói 4 ảnh:")
        lbl_p4.setObjectName("FieldLabel")
        price_grid.addWidget(lbl_p4, 1, 0, Qt.AlignRight)
        self.input_price_4 = QSpinBox()
        self.input_price_4.setRange(1000, 1000000)
        self.input_price_4.setSingleStep(1000)
        self.input_price_4.setValue(35000)
        self.input_price_4.setSuffix(" VNĐ")
        price_grid.addWidget(self.input_price_4, 1, 1)
        
        main_layout.addWidget(price_group)
        
        # === NHÓM: CLOUDINARY ===
        cloud_group = QGroupBox("☁️ Cloudinary (Tải ảnh lên Cloud - Tùy chọn)")
        cloud_grid = QGridLayout(cloud_group)
        cloud_grid.setSpacing(12)
        cloud_grid.setColumnStretch(1, 1)
        
        lbl_cn = QLabel("Cloud Name:")
        lbl_cn.setObjectName("FieldLabel")
        cloud_grid.addWidget(lbl_cn, 0, 0, Qt.AlignRight)
        self.input_cloud_name = QLineEdit()
        self.input_cloud_name.setPlaceholderText("Cloud name từ Cloudinary")
        cloud_grid.addWidget(self.input_cloud_name, 0, 1)
        
        lbl_ck = QLabel("API Key:")
        lbl_ck.setObjectName("FieldLabel")
        cloud_grid.addWidget(lbl_ck, 1, 0, Qt.AlignRight)
        self.input_cloud_api_key = QLineEdit()
        self.input_cloud_api_key.setPlaceholderText("API Key từ Cloudinary")
        cloud_grid.addWidget(self.input_cloud_api_key, 1, 1)
        
        lbl_cs = QLabel("API Secret:")
        lbl_cs.setObjectName("FieldLabel")
        cloud_grid.addWidget(lbl_cs, 2, 0, Qt.AlignRight)
        self.input_cloud_api_secret = QLineEdit()
        self.input_cloud_api_secret.setPlaceholderText("API Secret từ Cloudinary")
        self.input_cloud_api_secret.setEchoMode(QLineEdit.Password)
        cloud_grid.addWidget(self.input_cloud_api_secret, 2, 1)
        
        main_layout.addWidget(cloud_group)
        
        # === NÚT LƯU ===
        main_layout.addSpacing(10)
        
        self.btn_save = QPushButton("💾 LƯU CẤU HÌNH")
        self.btn_save.setObjectName("SaveBtn")
        self.btn_save.setFixedHeight(60)
        self.btn_save.clicked.connect(self.save_config)
        main_layout.addWidget(self.btn_save)
        
        # Trạng thái
        self.status_label = QLabel("")
        self.status_label.setAlignment(Qt.AlignCenter)
        self.status_label.setStyleSheet("color: #a8dadc; font-size: 12px;")
        main_layout.addWidget(self.status_label)
        
        main_layout.addStretch()
    
    def start_loading_banks(self):
        """Tải danh sách ngân hàng."""
        self.bank_loader = BankLoaderThread()
        self.bank_loader.banks_loaded.connect(self.on_banks_loaded)
        self.bank_loader.load_error.connect(self.on_banks_load_error)
        self.bank_loader.start()
    
    def on_banks_loaded(self, banks):
        """Xử lý khi tải xong danh sách ngân hàng."""
        self.banks_list = banks
        self.combo_bank.clear()
        self.combo_bank.setEnabled(True)
        self.combo_bank.addItem("-- Chọn ngân hàng --", "")
        
        for bank in banks:
            display_name = f"{bank.get('shortName', '')} - {bank.get('name', '')}"
            self.combo_bank.addItem(display_name, bank.get('bin', ''))
        
        # Khôi phục lựa chọn nếu có
        if self._saved_bank_bin:
            for i in range(self.combo_bank.count()):
                if self.combo_bank.itemData(i) == self._saved_bank_bin:
                    self.combo_bank.setCurrentIndex(i)
                    break
        
        self.status_label.setText(f"✅ Đã tải {len(banks)} ngân hàng từ VietQR")
        self.status_label.setStyleSheet("color: #06d6a0; font-size: 12px;")
    
    def on_banks_load_error(self, error_msg):
        """Xử lý khi lỗi tải ngân hàng."""
        self.combo_bank.clear()
        self.combo_bank.addItem("❌ Lỗi - Thử lại sau", "")
        self.combo_bank.setEnabled(False)
        self.status_label.setText(f"❌ {error_msg}")
        self.status_label.setStyleSheet("color: #e94560; font-size: 12px;")
    
    def toggle_api_visibility(self):
        """Ẩn/hiện API key."""
        if self.input_casso_api.echoMode() == QLineEdit.Password:
            self.input_casso_api.setEchoMode(QLineEdit.Normal)
            self.btn_toggle_api.setText("🙈 Ẩn")
        else:
            self.input_casso_api.setEchoMode(QLineEdit.Password)
            self.btn_toggle_api.setText("👁️ Hiện")
    
    def load_existing_config(self):
        """Tải cấu hình đã lưu."""
        if os.path.exists(CONFIG_FILE):
            try:
                with open(CONFIG_FILE, 'r', encoding='utf-8') as f:
                    config = json.load(f)
                
                self.input_account_number.setText(config.get('bank_account', ''))
                self.input_account_name.setText(config.get('account_name', ''))
                self.input_casso_api.setText(config.get('casso_api_key', ''))
                self.input_price_2.setValue(config.get('price_2_photos', 20000))
                self.input_price_4.setValue(config.get('price_4_photos', 35000))
                
                cloudinary = config.get('cloudinary', {})
                self.input_cloud_name.setText(cloudinary.get('cloud_name', ''))
                self.input_cloud_api_key.setText(cloudinary.get('api_key', ''))
                self.input_cloud_api_secret.setText(cloudinary.get('api_secret', ''))
                
                self._saved_bank_bin = config.get('bank_bin', '')
                
                self.status_label.setText("📂 Đã tải cấu hình từ config.json")
                self.status_label.setStyleSheet("color: #ffd700; font-size: 12px;")
            except Exception as e:
                self.status_label.setText(f"⚠️ Lỗi đọc config: {e}")
    
    def save_config(self):
        """Lưu cấu hình."""
        bank_bin = self.combo_bank.currentData()
        account_number = self.input_account_number.text().strip()
        account_name = self.input_account_name.text().strip()
        casso_api = self.input_casso_api.text().strip()
        
        errors = []
        if not bank_bin:
            errors.append("• Chưa chọn ngân hàng")
        if not account_number:
            errors.append("• Chưa nhập số tài khoản")
        if not account_name:
            errors.append("• Chưa nhập tên chủ tài khoản")
        if not casso_api:
            errors.append("• Chưa nhập Casso API Key")
        
        if errors:
            QMessageBox.warning(self, "⚠️ Thiếu thông tin",
                "Vui lòng điền đầy đủ:\n\n" + "\n".join(errors))
            return
        
        config = {
            "bank_bin": bank_bin,
            "bank_name": self.combo_bank.currentText(),
            "bank_account": account_number,
            "account_name": account_name,
            "casso_api_key": casso_api,
            "price_2_photos": self.input_price_2.value(),
            "price_4_photos": self.input_price_4.value(),
            "cloudinary": {
                "cloud_name": self.input_cloud_name.text().strip(),
                "api_key": self.input_cloud_api_key.text().strip(),
                "api_secret": self.input_cloud_api_secret.text().strip()
            }
        }
        
        try:
            with open(CONFIG_FILE, 'w', encoding='utf-8') as f:
                json.dump(config, f, ensure_ascii=False, indent=4)
            
            QMessageBox.information(self, "✅ Thành công",
                f"Đã lưu cấu hình!\n\nFile: {os.path.abspath(CONFIG_FILE)}\n\n"
                "Bạn có thể đóng và chạy main_app.py")
            
            self.status_label.setText("✅ Đã lưu thành công!")
            self.status_label.setStyleSheet("color: #06d6a0; font-size: 14px; font-weight: bold;")
        except Exception as e:
            QMessageBox.critical(self, "❌ Lỗi", f"Không thể lưu:\n{e}")


# ==========================================
# KHỞI CHẠY
# ==========================================
if __name__ == "__main__":
    app = QApplication(sys.argv)
    
    font = QFont("Segoe UI", 10)
    font.setStyleHint(QFont.SansSerif)
    app.setFont(font)
    
    window = SetupAdminApp()
    window.show()
    
    sys.exit(app.exec_())
