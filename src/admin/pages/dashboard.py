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

CONFIG_FILE = "config.json"

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

        self.layout_price_inputs = {}
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

        title = QLabel("CẤU HÌNH HỆ THỐNG PHOTOBOOTH")
        title.setAlignment(Qt.AlignCenter)
        title.setStyleSheet("font-size: 22px; color: #eaf0f6; margin-bottom: 10px;")
        layout.addWidget(title)

        # --- Quản lý danh sách Layout & Giá tiền ---
        layout_management_group = QGroupBox("QUẢN LÝ GIÁ TIỀN & LAYOUT")
        layout_mgmt_vbox = QVBoxLayout(layout_management_group)
        
        lbl_layout_info = QLabel("Sau khi tạo Layout mới ở App (F2), nhấn nút dưới đây để cập nhật danh sách và cấu hình giá:")
        lbl_layout_info.setWordWrap(True)
        lbl_layout_info.setStyleSheet("color: #a8dadc; font-weight: normal; margin-bottom: 5px;")
        layout_mgmt_vbox.addWidget(lbl_layout_info)

        self.btn_refresh_layouts = QPushButton("🔄 CẬP NHẬT DANH SÁCH LAYOUT & GIÁ")
        self.btn_refresh_layouts.setStyleSheet("background-color: #4361ee; padding: 15px; font-size: 15px;")
        self.btn_refresh_layouts.clicked.connect(self.refresh_layout_list)
        layout_mgmt_vbox.addWidget(self.btn_refresh_layouts)

        # Container để hiển thị các input giá tiền (sẽ được cập nhật khi nhấn refresh)
        self.price_scroll = QScrollArea()
        self.price_scroll.setWidgetResizable(True)
        self.price_scroll.setFixedHeight(250)
        self.price_scroll.setStyleSheet("background-color: #0f172a; border-radius: 5px;")
        
        self.price_widget = QWidget()
        self.price_container_layout = QVBoxLayout(self.price_widget)
        self.price_scroll.setWidget(self.price_widget)
        layout_mgmt_vbox.addWidget(self.price_scroll)

        layout.addWidget(layout_management_group)

        # --- Quản lý Template (Hình ảnh) ---
        template_group = QGroupBox("QUẢN LÝ TEMPLATE (HÌNH ẢNH)")
        template_layout = QVBoxLayout(template_group)
        
        h_sel_layout = QHBoxLayout()
        h_sel_layout.addWidget(QLabel("Chọn Layout:"))
        self.temp_layout_combo = QComboBox()
        self.temp_layout_combo.currentTextChanged.connect(self.load_template_files)
        h_sel_layout.addWidget(self.temp_layout_combo)
        template_layout.addLayout(h_sel_layout)

        from PyQt5.QtWidgets import QListWidget
        self.template_list = QListWidget()
        self.template_list.setFixedHeight(200)
        self.template_list.setStyleSheet("background-color: #0f172a; color: white; border: 1px solid #4361ee;")
        template_layout.addWidget(self.template_list)

        h_btns = QHBoxLayout()
        self.btn_add_temp = QPushButton("➕ THÊM FILE ẢNH")
        self.btn_add_temp.setStyleSheet("background-color: #06d6a0; color: #1a1a2e;")
        self.btn_add_temp.clicked.connect(self.upload_template_file)
        
        self.btn_del_temp = QPushButton("🗑️ XÓA FILE")
        self.btn_del_temp.setStyleSheet("background-color: #e94560;")
        self.btn_del_temp.clicked.connect(self.delete_template_file)
        
        h_btns.addWidget(self.btn_add_temp)
        h_btns.addWidget(self.btn_del_temp)
        template_layout.addLayout(h_btns)

        layout.addWidget(template_group)


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
        """Cập nhật lại danh sách layout sau khi thêm mới, hỗ trợ Xóa."""
        from src.shared.types import models as frame_config
        importlib.reload(frame_config)

        # Xóa sạch các widget cũ trong price_container_layout
        while self.price_container_layout.count():
            item = self.price_container_layout.takeAt(0)
            if item.widget():
                item.widget().deleteLater()
            elif item.layout():
                self.clear_layout(item.layout())

        self.layout_price_inputs = {}
        all_layouts = frame_config.get_all_layouts()
        
        for name, cfg in all_layouts.items():
            h_layout = QHBoxLayout()
            
            # Label tên và nhóm
            group_tag = f"[{cfg.get('group', 'Default').upper()}]"
            lbl_name = QLabel(f"{group_tag} {name}:")
            lbl_name.setFixedWidth(200)
            lbl_name.setStyleSheet("color: #06d6a0;")
            
            # Input giá
            edit_price = QLineEdit()
            edit_price.setPlaceholderText("Giá VNĐ")
            edit_price.setFixedWidth(120)
            self.layout_price_inputs[name] = edit_price
            
            h_layout.addWidget(lbl_name)
            h_layout.addWidget(edit_price)
            h_layout.addStretch()

            # Nút Xóa (chỉ cho layout custom và trừ cái Custom_Layout mặc định nếu muốn)
            if name.startswith("Custom_") or name not in ["1x2", "2x1", "2x2", "4x1"]:
                btn_del = QPushButton("🗑️")
                btn_del.setFixedSize(40, 40)
                btn_del.setStyleSheet("background-color: #e94560; border-radius: 5px;")
                btn_del.clicked.connect(lambda checked, n=name: self.handle_delete_layout(n))
                h_layout.addWidget(btn_del)

            self.price_container_layout.addLayout(h_layout)

        self.temp_layout_combo.blockSignals(True)
        self.temp_layout_combo.clear()
        # Hiển thị nhóm template (vertical, custom) thay vì tên layout
        template_groups = []
        for group_name in ["vertical", "custom"]:
            group_dir = os.path.join(TEMPLATE_DIR, group_name)
            if os.path.exists(group_dir):
                template_groups.append(group_name)
        # Thêm thư mục 4x1 nếu tồn tại (backward compatibility)
        fourx1_dir = os.path.join(TEMPLATE_DIR, "4x1")
        if os.path.exists(fourx1_dir) and "4x1" not in template_groups:
            template_groups.append("4x1")
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
        reply = QMessageBox.question(self, "Xác nhận", f"Bạn có chắc muốn xóa Layout '{name}' không?",
                                   QMessageBox.Yes | QMessageBox.No)
        if reply == QMessageBox.Yes:
            from src.shared.types.models import delete_custom_layout
            if delete_custom_layout(name):
                QMessageBox.information(self, "Thành công", f"Đã xóa layout {name}")
                self.refresh_layout_list()
            else:
                QMessageBox.warning(self, "Lỗi", "Không thể xóa layout này.")


    def load_template_files(self):
        """Liệt kê các file trong thư mục template của nhóm đang chọn."""
        group_name = self.temp_layout_combo.currentText()
        if not group_name: return
        
        self.template_list.clear()
        
        # Lấy danh sách layout hợp lệ cho nhóm custom để lọc template mồ côi
        valid_layout_names = None
        if group_name == "custom":
            from src.modules.image_processing.processor import detect_layout_from_template
            all_layouts = get_all_layouts()
            valid_layout_names = set()
            for lname, lcfg in all_layouts.items():
                lgroup = lcfg.get("group", "vertical" if lname == "4x1" else "custom")
                if lgroup == "custom":
                    valid_layout_names.add(lname)
        
        # Quét thư mục nhóm (vertical, custom, hoặc 4x1)
        search_dirs = []
        if group_name == "vertical":
            search_dirs.append(os.path.join(TEMPLATE_DIR, "vertical"))
            search_dirs.append(os.path.join(TEMPLATE_DIR, "4x1"))
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
        
        files, _ = QFileDialog.getOpenFileNames(self, "Chọn file ảnh Template", "", "Ảnh (*.png *.jpg *.jpeg)")
        if files:
            os.makedirs(dest_dir, exist_ok=True)
            for f in files:
                shutil.copy(f, dest_dir)
            self.load_template_files()
            QMessageBox.information(self, "Thành công", f"Đã thêm {len(files)} file vào {group_name}")

    def delete_template_file(self):
        """Xóa file template đang chọn."""
        item = self.template_list.currentItem()
        if not item: 
            QMessageBox.warning(self, "Thông báo", "Vui lòng chọn một file để xóa.")
            return
        
        # Item có format: "dir_name/filename"
        item_text = item.text()
        if "/" in item_text:
            dir_name, filename = item_text.split("/", 1)
        else:
            dir_name = self.temp_layout_combo.currentText()
            filename = item_text
            
        reply = QMessageBox.question(self, "Xác nhận", f"Bạn có chắc muốn xóa file '{filename}' không?",
                                   QMessageBox.Yes | QMessageBox.No)
        if reply == QMessageBox.Yes:
            file_path = os.path.join(TEMPLATE_DIR, dir_name, filename)
            try:
                os.remove(file_path)
                self.load_template_files()
                QMessageBox.information(self, "Thành công", f"Đã xóa file {filename}")
            except Exception as e:
                QMessageBox.critical(self, "Lỗi", f"Không thể xóa file: {e}")

    def load_current_config(self):
        if not os.path.exists(CONFIG_FILE):
            return

        try:
            with open(CONFIG_FILE, 'r', encoding='utf-8') as f:
                data = json.load(f)

            layout_prices = data.get("layout_prices", {})
            for name, input_field in self.layout_price_inputs.items():
                if name in layout_prices:
                    input_field.setText(str(layout_prices[name]))
                else:
                    if name in ["1x2", "2x1"]:
                        input_field.setText(str(data.get("price_2_photos", "")))
                    else:
                        input_field.setText(str(data.get("price_4_photos", "")))

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
        layout_prices = {}
        try:
            for name, input_field in self.layout_price_inputs.items():
                val = input_field.text().strip()
                if val:
                    layout_prices[name] = int(val)
        except ValueError:
            QMessageBox.critical(self, "Lỗi", "Giá tiền các layout phải là số nguyên!")
            return

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
            load_config()
        except Exception as e:
            QMessageBox.critical(self, "Lỗi", f"Không thể lưu file: {e}")


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = AdminSetup()
    window.show()
    sys.exit(app.exec_())
