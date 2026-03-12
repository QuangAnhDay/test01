# ==========================================
# ADMIN DASHBOARD - Trang quản trị chính
# ==========================================
"""
Trang quản trị: cấu hình giá, ngân hàng, API keys, 
mở Frame Editor, quản lý layouts.

CÁCH CHẠY:
    python -m src.admin.pages.dashboard
"""

import sys
import os
import json
import importlib

from PyQt5.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout,
                             QHBoxLayout, QLabel, QLineEdit, QPushButton,
                             QGroupBox, QMessageBox, QFrame, QComboBox, QScrollArea)
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QFont, QIcon

from src.shared.types.models import get_all_layouts, load_config, TEMPLATE_DIR
import shutil
from PyQt5.QtWidgets import QFileDialog

from src.config import APP_CONFIG_PATH
CONFIG_FILE = APP_CONFIG_PATH

# Danh sách ngân hàng phổ biến tại Việt Nam
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
    """Bảng điều khiển quản trị Photobooth."""

    def __init__(self):
        super().__init__()
        self.setWindowTitle("🛠️ Photobooth - Admin System")
        self.resize(1100, 950) # Tăng kích thước cửa sổ cho dễ nhìn
        self.editor_window = None # Để lưu cửa sổ Frame Editor
        self.setStyleSheet("""
            /* Mau nen cua cua so Admin (Xam nhat) */
            QMainWindow { background-color: #f0f2f5; }
            QLabel { color: #333; font-size: 14px; font-weight: bold; }
            QLineEdit, QComboBox, QListWidget { 
                background-color: white; 
                color: #333; 
                border: 1px solid #ccc; 
                border-radius: 5px; 
                padding: 8px;
                font-size: 14px;
            }
            /* Mau vien khi o nhap lieu duoc chon (Xanh duong) */
            QLineEdit:focus, QComboBox:focus { border-color: #4361ee; }
            QGroupBox { 
                color: #2c3e50; 
                font-weight: bold; 
                border: 1px solid #ccc; 
                border-radius: 10px; 
                margin-top: 20px;
                padding-top: 15px;
                background-color: white;
            }
            /* Mau nen mac dinh cua cac nut bam Admin (Xanh duong) */
            QPushButton {
                background-color: #4361ee;
                color: white;
                border: none;
                border-radius: 10px;
                padding: 12px;
                font-size: 14px;
                font-weight: bold;
            }
            /* Mau nut khi di chuot qua (Xanh nhat) */
            QPushButton:hover { background-color: #4cc9f0; }
            /* Mau nut SAVE (Xanh la cay) */
            QPushButton#SaveBtn { background-color: #28a745; color: white; font-size: 18px; }
            QPushButton#SaveBtn:hover { background-color: #218838; }
            /* Mau nut Editor (Cam) */
            QPushButton#EditorBtn { background-color: #f39c12; }
            QPushButton#EditorBtn:hover { background-color: #e67e22; }
        """)

        self.editor_window = None

        self.init_ui()
        load_config()
        self.refresh_layout_list() # Tự động load danh sách layout và giá

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

        title = QLabel("PHOTOBOOTH SYSTEM CONFIGURATION")
        title.setAlignment(Qt.AlignCenter)
        title.setStyleSheet("font-size: 22px; color: #333; margin-bottom: 10px;")
        layout.addWidget(title)

        # --- Quản lý Giá tiền ---
        pricing_group = QGroupBox("PRICING CONFIGURATION")
        pricing_layout = QVBoxLayout(pricing_group)
        
        self.price_vertical = self.create_input(pricing_layout, "Vertical Price (4x1):", "Enter price in USD/VND")
        self.price_custom = self.create_input(pricing_layout, "Custom Price:", "Enter price in USD/VND")
        
        layout.addWidget(pricing_group)

        # --- Quản lý Template (Hình ảnh) ---
        template_group = QGroupBox("TEMPLATE MANAGEMENT (IMAGES)")
        template_layout = QVBoxLayout(template_group)
        
        h_sel_layout = QHBoxLayout()
        h_sel_layout.addWidget(QLabel("Select Layout:"))
        self.temp_layout_combo = QComboBox()
        self.temp_layout_combo.currentTextChanged.connect(self.load_template_files)
        h_sel_layout.addWidget(self.temp_layout_combo)
        template_layout.addLayout(h_sel_layout)

        from PyQt5.QtWidgets import QListWidget
        self.template_list = QListWidget()
        self.template_list.setMinimumHeight(350) # Tăng chiều cao danh sách ảnh
        self.template_list.setStyleSheet("background-color: #ffffff; color: #333; border: 1px solid #ccc;")
        template_layout.addWidget(self.template_list)

        h_btns = QHBoxLayout()
        self.btn_add_temp = QPushButton("➕ ADD IMAGE FILE")
        self.btn_add_temp.setStyleSheet("background-color: #06d6a0; color: #1a1a2e;")
        self.btn_add_temp.clicked.connect(self.upload_template_file)
        
        self.btn_del_temp = QPushButton("🗑️ DELETE FILE")
        self.btn_del_temp.setStyleSheet("background-color: #e94560;")
        self.btn_del_temp.clicked.connect(self.delete_template_file)
        
        h_btns.addWidget(self.btn_add_temp)
        h_btns.addWidget(self.btn_del_temp)
        template_layout.addLayout(h_btns)

        layout.addWidget(template_group)


        # --- Ngân hàng ---
        bank_group = QGroupBox("PAYMENT CONFIGURATION (VIETQR)")
        bank_layout = QVBoxLayout(bank_group)

        h_bank_layout = QHBoxLayout()
        lbl_bank = QLabel("Bank:")
        lbl_bank.setFixedWidth(180)
        self.bank_combo = QComboBox()
        for bank in VIETNAM_BANKS:
            self.bank_combo.addItem(bank["name"], bank["bin"])
        h_bank_layout.addWidget(lbl_bank)
        h_bank_layout.addWidget(self.bank_combo)
        bank_layout.addLayout(h_bank_layout)

        self.bank_acc = self.create_input(bank_layout, "Account Number:", "Enter receiving account number")
        self.bank_name = self.create_input(bank_layout, "Account Holder Name:", "Enter name without accents (UPPERCASE)")
        layout.addWidget(bank_group)

        # --- API Keys ---
        api_group = QGroupBox("API KEYS & CLOUD")
        api_layout = QVBoxLayout(api_group)

        self.casso_key = self.create_input(api_layout, "Casso API Key:", "Used to verify payments")
        self.cloud_name = self.create_input(api_layout, "Cloudinary Name:", "Cloud name")
        self.cloud_api_key = self.create_input(api_layout, "Cloudinary API Key:", "API Key")
        self.cloud_api_secret = self.create_input(api_layout, "Cloudinary API Secret:", "API Secret")
        layout.addWidget(api_group)

        # --- Nút Mở Frame Editor (Nút vàng cam) ---
        self.btn_editor = QPushButton("🎨 OPEN FRAME EDITOR (DESIGN LAYOUT)")
        self.btn_editor.setObjectName("EditorBtn")
        self.btn_editor.setFixedHeight(60)
        self.btn_editor.clicked.connect(self.open_frame_editor)
        layout.addWidget(self.btn_editor)
        
        layout.addSpacing(10)

        self.btn_save = QPushButton("💾 SAVE ALL CONFIGURATIONS")
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
        """Cập nhật lại danh sách nhóm template."""
        from src.shared.types import models as frame_config
        importlib.reload(frame_config)

        self.temp_layout_combo.blockSignals(True)
        self.temp_layout_combo.clear()
        # Hiển thị nhóm template (vertical, custom) thay vì tên layout
        template_groups = []
        for group_name in ["vertical", "custom"]:
            group_dir = os.path.join(TEMPLATE_DIR, group_name)
            if os.path.exists(group_dir):
                template_groups.append(group_name)

        self.temp_layout_combo.addItems(template_groups)
        self.temp_layout_combo.blockSignals(False)
        self.load_template_files() # Load file cho nhóm đầu tiên

        self.load_current_config()

    def clear_layout(self, layout):
        if layout is not None:
            while layout.count():
                item = layout.takeAt(0)
                widget = item.widget()
                if widget is not None:
                    widget.deleteLater()
                else:
                    self.clear_layout(item.layout())

    def handle_delete_layout(self, name):
        """Xử lý yêu cầu xóa layout từ admin."""
        reply = QMessageBox.question(self, "Confirm", f"Are you sure you want to delete Layout '{name}'?",
                                   QMessageBox.Yes | QMessageBox.No)
        if reply == QMessageBox.Yes:
            from src.shared.types.models import delete_custom_layout
            if delete_custom_layout(name):
                QMessageBox.information(self, "Success", f"Deleted layout {name}")
                self.refresh_layout_list()
            else:
                QMessageBox.warning(self, "Error", "Could not delete this layout.")


    def load_template_files(self):
        """Liệt kê các file trong thư mục template của nhóm đang chọn."""
        group_name = self.temp_layout_combo.currentText()
        if not group_name: return
        
        self.template_list.clear()
        
        # Lấy danh sách layout hợp lệ cho nhóm custom để lọc template mồ côi
        valid_layout_names = None
        if group_name == "custom":
            from src.services.image.template import detect_layout_from_template
            all_layouts = get_all_layouts()
            valid_layout_names = set()
            for lname, lcfg in all_layouts.items():
                lgroup = lcfg.get("group", "vertical" if lname == "4x1" else "custom")
                if lgroup == "custom":
                    valid_layout_names.add(lname)
        
        # Quét thư mục nhóm (vertical, custom)
        search_dirs = []
        if group_name == "vertical":
            search_dirs.append(os.path.join(TEMPLATE_DIR, "vertical"))
        else:
            search_dirs.append(os.path.join(TEMPLATE_DIR, group_name))
        
        for search_dir in search_dirs:
            if os.path.exists(search_dir):
                files = [f for f in sorted(os.listdir(search_dir)) if f.lower().endswith(('.png', '.jpg', '.jpeg'))]
                for f in files:
                    # Với nhóm custom: chỉ hiển thị template có layout config tồn tại
                    if valid_layout_names is not None:
                        fpath = os.path.join(search_dir, f)
                        detected = detect_layout_from_template(fpath)
                        if detected and detected not in valid_layout_names:
                            continue  # Bỏ qua template mồ côi
                    
                    # Hiển thị tên file kèm thư mục để phân biệt
                    dir_name = os.path.basename(search_dir)
                    self.template_list.addItem(f"{dir_name}/{f}")

    def upload_template_file(self):
        """Mở hộp thoại chọn file và copy vào thư mục template tương ứng."""
        group_name = self.temp_layout_combo.currentText()
        if not group_name: return
        
        # Xác định thư mục đích
        dest_dir = os.path.join(TEMPLATE_DIR, group_name)
        
        files, _ = QFileDialog.getOpenFileNames(self, "Select Template Image Files", "", "Images (*.png *.jpg *.jpeg)")
        if files:
            os.makedirs(dest_dir, exist_ok=True)
            for f in files:
                shutil.copy(f, dest_dir)
            self.load_template_files()
            QMessageBox.information(self, "Success", f"Added {len(files)} files to {group_name}")

    def delete_template_file(self):
        """Xóa file template đang chọn."""
        item = self.template_list.currentItem()
        # Item có format: "dir_name/filename"
        item_text = item.text()
        if "/" in item_text:
            dir_name, filename = item_text.split("/", 1)
        else:
            dir_name = self.temp_layout_combo.currentText()
            filename = item_text
            
        reply = QMessageBox.question(self, "Confirm", f"Are you sure you want to delete file '{filename}'?",
                                   QMessageBox.Yes | QMessageBox.No)
        if reply == QMessageBox.Yes:
            file_path = os.path.join(TEMPLATE_DIR, dir_name, filename)
            try:
                os.remove(file_path)
                self.load_template_files()
                QMessageBox.information(self, "Success", f"Deleted file {filename}")
            except Exception as e:
                QMessageBox.critical(self, "Error", f"Could not delete file: {e}")

    def load_current_config(self):
        if not os.path.exists(CONFIG_FILE):
            return

        try:
            with open(CONFIG_FILE, 'r', encoding='utf-8') as f:
                data = json.load(f)

            self.price_vertical.setText(str(data.get("price_vertical", data.get("price_4_photos", ""))))
            self.price_custom.setText(str(data.get("price_custom", data.get("price_2_photos", ""))))

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

    def open_frame_editor(self):
        """Mở công cụ thiết kế khung ảnh."""
        from src.admin.components.frame_editor import FrameEditor
        self.editor_window = FrameEditor()
        self.editor_window.show()
        
    def save_config(self):
        try:
            pv = int(self.price_vertical.text().strip() or 0)
            pc = int(self.price_custom.text().strip() or 0)
        except ValueError:
            QMessageBox.critical(self, "Error", "Price must be an integer!")
            return

        config_data = {
            "price_vertical": pv,
            "price_custom": pc,
            "price_2_photos": pc, # Giữ cho tương thích code cũ
            "price_4_photos": pv, # Giữ cho tương thích code cũ
            "layout_prices": {}, # Clear layout_prices để App dùng fallback
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
            QMessageBox.information(self, "Success", "Configuration saved to config.json!")
            load_config()
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Could not save file: {e}")


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = AdminSetup()
    window.show()
    sys.exit(app.exec_())
